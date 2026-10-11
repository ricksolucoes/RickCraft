"""Sonda concreta de capacidades do workspace e classificação D-02/D-03."""

from __future__ import annotations

import errno
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from workspace_resolver import ResultadoCapacidade


_BYTES_SONDA = b"RickCraft D-02 probe v1\n"
_BYTES_SENTINELA = b"sentinela preexistente; nao substituir\n"
_TENTATIVAS_NOME = 8


@dataclass(frozen=True)
class EvidenciaSonda:
    """Diagnóstico observável de uma avaliação de raiz."""

    raiz: Path
    resultado: ResultadoCapacidade
    capacidades: tuple[str, ...] = ()
    operacao_falha: str | None = None
    causa: str | None = None
    errno: int | None = None
    winerror: int | None = None
    residuos: tuple[Path, ...] = ()
    avisos: tuple[str, ...] = ()


@dataclass
class AvaliadorWorkspace:
    """Callback concreto compatível com ``resolver_workspace``.

    A classe não escolhe raiz nem aciona fallback. O resolvedor da TASK-002
    mantém a precedência e consome apenas ``ResultadoCapacidade``.
    """

    evidencias: list[EvidenciaSonda] = field(default_factory=list)

    def __call__(self, raiz: Path) -> ResultadoCapacidade:
        resultado, evidencia = _sondar_raiz(Path(raiz))
        self.evidencias.append(evidencia)
        return resultado


def classificar_falha(exc: OSError, operacao: str) -> ResultadoCapacidade:
    """Classifica somente causas filesystem reconhecidas pelo contrato."""
    codigo = exc.errno
    winerror = getattr(exc, "winerror", None)

    if (codigo is not None and codigo in _codigos_errno("EACCES", "EPERM")) or winerror == 5:
        return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
    if (codigo is not None and codigo in _codigos_errno("EROFS")) or winerror == 19:
        return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
    if (codigo is not None and codigo in _codigos_errno("ENOTDIR")) or winerror == 267:
        return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
    if (
        codigo is not None
        and codigo in _codigos_errno("ENOTSUP", "EOPNOTSUPP", "ENOSYS")
    ) or winerror in {1, 50, 120}:
        return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
    if (
        codigo is not None
        and codigo in _codigos_errno("ENOSPC", "EDQUOT", "EFBIG")
    ) or winerror in {39, 112, 1816}:
        return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
    if (codigo is not None and codigo in _codigos_errno("ENAMETOOLONG")) or winerror == 206:
        return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA

    # EEXIST continua desconhecido nesta classificação e não habilita fallback.
    return ResultadoCapacidade.ERRO_DESCONHECIDO


def _codigos_errno(*simbolos: str) -> set[int]:
    """Retorna somente códigos errno inteiros realmente disponíveis."""
    return {
        codigo
        for simbolo in simbolos
        if (codigo := getattr(errno, simbolo, None)) is not None
    }


def _evidencia_falha(
    raiz: Path,
    exc: Exception,
    operacao: str,
    capacidades: list[str],
    residuos: tuple[Path, ...] = (),
) -> EvidenciaSonda:
    if isinstance(exc, OSError):
        resultado = classificar_falha(exc, operacao)
        return EvidenciaSonda(
            raiz=raiz,
            resultado=resultado,
            capacidades=tuple(capacidades),
            operacao_falha=operacao,
            causa=f"{type(exc).__name__}: {exc}",
            errno=exc.errno,
            winerror=getattr(exc, "winerror", None),
            residuos=residuos,
        )
    return EvidenciaSonda(
        raiz=raiz,
        resultado=ResultadoCapacidade.ERRO_DESCONHECIDO,
        capacidades=tuple(capacidades),
        operacao_falha=operacao,
        causa=f"{type(exc).__name__}: {exc}",
        residuos=residuos,
    )


def _nome_exclusivo(diretorio: Path, prefixo: str, extensao: str = ".tmp") -> Path:
    """Escolhe nome aleatório ainda ausente; criação exclusiva segue separada."""
    for _ in range(_TENTATIVAS_NOME):
        candidato = diretorio / f"{prefixo}-{uuid.uuid4().hex}{extensao}"
        if not candidato.exists():
            return candidato
    raise FileExistsError(errno.EEXIST, "Não foi possível reservar nome aleatório", str(diretorio))


def _criar_arquivo_exclusivo(
    diretorio: Path,
    prefixo: str,
    dados: bytes,
    proprios: list[Path],
) -> Path:
    for _ in range(_TENTATIVAS_NOME):
        caminho = _nome_exclusivo(diretorio, prefixo)
        try:
            with caminho.open("xb") as arquivo:
                proprios.append(caminho)
                arquivo.write(dados)
                arquivo.flush()
                if callable(getattr(os, "fsync", None)):
                    os.fsync(arquivo.fileno())
            return caminho
        except FileExistsError:
            # Colisão de nome aleatório: selecionar outro nome, sem classificar
            # a raiz como indisponível.
            continue
    raise FileExistsError(errno.EEXIST, "Colisões exclusivas excederam o limite", str(diretorio))


def _publicar_sem_substituir(origem: Path, diretorio: Path, prefixo: str) -> Path:
    for _ in range(_TENTATIVAS_NOME):
        destino = _nome_exclusivo(diretorio, prefixo)
        try:
            os.link(origem, destino)
            return destino
        except FileExistsError:
            # Outro processo ocupou o nome entre a verificação e o link.
            continue
    raise FileExistsError(errno.EEXIST, "Colisões do destino excederam o limite", str(diretorio))


def _limpar_proprios(caminhos: list[Path], diretorio: Path | None) -> tuple[Path, ...]:
    residuos: list[Path] = []
    for caminho in reversed(caminhos):
        try:
            caminho.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            residuos.append(caminho)
    if diretorio is not None:
        try:
            diretorio.rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            residuos.append(diretorio)
    return tuple(residuos)


def _sondar_raiz(raiz: Path) -> tuple[ResultadoCapacidade, EvidenciaSonda]:
    capacidades: list[str] = []
    diretorio_sonda: Path | None = None
    proprios: list[Path] = []
    operacao = "validar raiz candidata"

    try:
        operacao = "criar raiz candidata"
        if raiz.exists() and not raiz.is_dir():
            raise NotADirectoryError(errno.ENOTDIR, "Componente da raiz não é diretório", str(raiz))
        raiz.mkdir(parents=True, exist_ok=True)
        if not raiz.is_dir():
            raise NotADirectoryError(errno.ENOTDIR, "Componente da raiz não é diretório", str(raiz))
        capacidades.append("raiz criada ou já existente como diretório")

        operacao = "criar diretório exclusivo da sonda"
        for _ in range(_TENTATIVAS_NOME):
            diretorio_sonda = raiz / f".rickcraft-probe-{uuid.uuid4().hex}.tmp"
            try:
                diretorio_sonda.mkdir()
                break
            except FileExistsError:
                diretorio_sonda = None
        if diretorio_sonda is None:
            raise FileExistsError(errno.EEXIST, "Colisões do diretório de sonda excederam o limite", str(raiz))
        capacidades.append("diretório isolado e exclusivo criado")

        operacao = "criar, escrever e sincronizar arquivo exclusivo"
        origem = _criar_arquivo_exclusivo(diretorio_sonda, "origem", _BYTES_SONDA, proprios)
        capacidades.extend(("open xb exclusivo", "escrita", "flush"))
        if callable(getattr(os, "fsync", None)):
            capacidades.append("fsync executado")
        else:
            capacidades.append("fsync não disponível no runtime")

        operacao = "reler arquivo de sonda"
        if origem.read_bytes() != _BYTES_SONDA:
            raise OSError(errno.EIO, "Bytes relidos diferem dos bytes escritos", str(origem))
        capacidades.append("releitura da origem conferida byte a byte")

        operacao = "publicar por os.link para destino ausente"
        destino = _publicar_sem_substituir(origem, diretorio_sonda, "publicado")
        proprios.append(destino)
        capacidades.append("os.link para destino ausente")

        operacao = "verificar destino publicado"
        if destino.read_bytes() != _BYTES_SONDA:
            raise OSError(errno.EIO, "Bytes do destino publicado diferem", str(destino))
        capacidades.append("releitura do destino publicada conferida")

        operacao = "preparar destino sentinela preexistente"
        sentinela = _criar_arquivo_exclusivo(
            diretorio_sonda, "sentinela", _BYTES_SENTINELA, proprios
        )
        capacidades.append("destino preexistente com bytes sentinela criado")

        operacao = "comprovar os.link sem substituição"
        destino_existente = sentinela
        rejeitou_destino = False
        try:
            os.link(origem, destino_existente)
        except FileExistsError:
            rejeitou_destino = True
        except OSError as exc:
            # Só o erro de destino existente comprova a semântica esperada;
            # outras falhas seguem classificação D-03.
            if not (
                exc.errno == errno.EEXIST
                or getattr(exc, "winerror", None) in {80, 183}
            ):
                raise
            rejeitou_destino = True
        if sentinela.read_bytes() != _BYTES_SENTINELA:
            raise RuntimeError("Bytes sentinela foram alterados pela tentativa de publicação")
        if not rejeitou_destino:
            raise RuntimeError("os.link aceitou destino já existente")
        capacidades.append("destino existente rejeitado sem substituir bytes sentinela")

        residuos = _limpar_proprios(proprios, diretorio_sonda)
        avisos = ("PROBE_CLEANUP_PENDING",) if residuos else ()
        evidencia = EvidenciaSonda(
            raiz=raiz,
            resultado=ResultadoCapacidade.UTILIZAVEL,
            capacidades=tuple(capacidades),
            residuos=residuos,
            avisos=avisos,
        )
        return ResultadoCapacidade.UTILIZAVEL, evidencia
    except Exception as exc:
        residuos = _limpar_proprios(proprios, diretorio_sonda)
        evidencia = _evidencia_falha(raiz, exc, operacao, capacidades, residuos)
        return evidencia.resultado, evidencia

