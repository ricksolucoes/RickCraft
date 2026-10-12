<div align="center">

# RickCraft (Skill) — Governança Técnica & Arquitetura Delphi

[![Delphi](https://img.shields.io/badge/Delphi-Object%20Pascal-red?logo=delphi)](https://www.embarcadero.com/products/delphi)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%26%20SOLID-blue)](#pilares-tecnicos)
[![Design Patterns](https://img.shields.io/badge/Design%20Patterns-GoF-purple)](#1-design-patterns)
[![AI Skill](https://img.shields.io/badge/AI-Skill-green)](#sobre-o-rickcraft)
[![License](https://img.shields.io/badge/License-MIT%20LICENSE-lightgrey)](LICENSE)

</div>

Idioma: Português | [English](README.md)
<div align="right">

[Ver Sumário](#sumário)

</div>

## Sobre o RickCraft

**RickCraft** é uma skill especializada em **governança técnica, arquitetura de software, qualidade de código e engenharia Delphi/Object Pascal**.

Seu objetivo é atuar como uma camada de governança para desenvolvimento assistido por Inteligência Artificial, estabelecendo critérios técnicos que devem ser considerados durante:

- análise de código;
- implementação;
- refatoração;
- revisão arquitetural;
- criação de novas classes e interfaces;
- aplicação de padrões de projeto;
- avaliação de acoplamento e responsabilidades;
- identificação de **Code Smells**;
- manutenção e evolução de sistemas Delphi.

O RickCraft não deve simplesmente gerar código que compile.

O código produzido ou revisado deve buscar **clareza, baixo acoplamento, alta coesão, testabilidade, extensibilidade e manutenção sustentável ao longo do tempo**.

Este repositório funciona como uma **fonte técnica de referência** para as regras e princípios utilizados pela skill.

---

## Objetivos

O RickCraft foi projetado para auxiliar na manutenção de um padrão arquitetural consistente em projetos Delphi.

Seus principais objetivos são:

- **Garantir consistência arquitetural:** manter padrões técnicos previsíveis independentemente de quem escreveu ou gerou o código.
- **Promover baixo acoplamento:** reduzir dependências desnecessárias entre classes, módulos e camadas.
- **Aumentar a coesão:** manter cada unidade de código concentrada em responsabilidades bem definidas.
- **Melhorar a testabilidade:** favorecer abstrações e estruturas que permitam testes unitários e isolamento de dependências.
- **Reduzir débito técnico:** identificar decisões estruturais que podem comprometer manutenção, evolução ou estabilidade futura.
- **Identificar Code Smells:** detectar sinais de problemas arquiteturais ou estruturais antes que se tornem falhas difíceis de corrigir.
- **Favorecer código sustentável:** produzir código compreensível, previsível e preparado para evolução.

---

## Pilares Técnicos

O RickCraft analisa e produz código considerando quatro pilares principais:

1. **Design Patterns**
2. **Princípios SOLID**
3. **Programação Orientada a Interfaces**
4. **Clean Code**

Esses conceitos não devem ser aplicados mecanicamente.

Um padrão, abstração ou camada adicional deve existir quando resolver um problema concreto de arquitetura, manutenção, extensibilidade, testabilidade ou desacoplamento.

> [!IMPORTANT]
> **Regra fundamental:** arquitetura deve reduzir complexidade, não criá-la.

---

## 1. Design Patterns

O RickCraft utiliza como referência os **23 padrões clássicos do catálogo Gang of Four — GoF**.

Os padrões são divididos em três grupos:

- Criacionais;
- Estruturais;
- Comportamentais.

Eles devem ser utilizados quando houver justificativa arquitetural para sua aplicação.

### Padrões Criacionais

Tratam da criação e instanciação de objetos.

#### Factory Method
Define uma abstração para criação de objetos, permitindo que implementações específicas determinem qual classe concreta será instanciada.

#### Abstract Factory
Permite criar famílias de objetos relacionados sem acoplar o código cliente às classes concretas.

#### Builder
Separa o processo de construção de um objeto complexo de sua representação final. É especialmente útil quando um objeto possui muitas configurações ou etapas de inicialização.

#### Prototype
Permite criar novos objetos a partir da cópia de uma instância existente.

#### Singleton
Garante uma única instância de determinada classe e fornece um ponto controlado de acesso a ela.

No RickCraft, quando o Singleton for realmente necessário, a criação e a liberação da instância devem permanecer centralizadas na própria classe.

```pascal
interface

type
  TSessionPadrao = class
  private
    constructor Create;
  public
    destructor Destroy; override;
    class function GetInstance: TSessionPadrao;
    class procedure ReleaseInstance;
  end;

implementation

var
  FInstance: TSessionPadrao;

constructor TSessionPadrao.Create;
begin
  inherited Create;
end;

destructor TSessionPadrao.Destroy;
begin
  inherited;
end;

class function TSessionPadrao.GetInstance: TSessionPadrao;
begin
  if not Assigned(FInstance) then
    FInstance := TSessionPadrao.Create;
  Result := FInstance;
end;

class procedure TSessionPadrao.ReleaseInstance;
begin
  if Assigned(FInstance) then
  begin
    FInstance.Free;
    FInstance := nil;
  end;
end;

end.
```

O construtor permanece privado para impedir que o consumidor crie instâncias fora do ponto de acesso controlado.

> [!WARNING]
> O uso de Singleton deve ser avaliado criteriosamente devido ao risco de introdução de estado global e aumento de acoplamento. O exemplo acima também não implementa sincronização para acesso concorrente; em cenários multithread, a criação e a liberação da instância exigem proteção apropriada.

### Padrões Estruturais

Tratam da composição e organização entre classes e objetos.

#### Adapter
Permite integrar componentes com interfaces incompatíveis através de uma camada de adaptação.

#### Bridge
Separa uma abstração de sua implementação, permitindo que ambas evoluam independentemente.

#### Composite
Permite representar hierarquias de objetos através de estruturas em árvore e tratar objetos individuais e composições de maneira uniforme.

#### Decorator
Adiciona responsabilidades dinamicamente a um objeto sem modificar sua implementação original.

#### Facade
Fornece uma interface simplificada para um conjunto complexo de classes ou subsistemas.

#### Flyweight
Reduz consumo de memória através do compartilhamento de estados comuns entre múltiplos objetos.

#### Proxy
Cria um objeto intermediário responsável por controlar o acesso a outro objeto.

### Padrões Comportamentais

Tratam da comunicação, colaboração e distribuição de responsabilidades entre objetos.

#### Chain of Responsibility
Encaminha uma solicitação através de uma cadeia de manipuladores até que algum deles seja responsável por processá-la.

#### Command
Encapsula uma operação ou solicitação em um objeto independente.

#### Interpreter
Define uma representação para uma linguagem ou expressão e fornece mecanismos para interpretá-la.

#### Iterator
Permite percorrer uma coleção sem expor sua estrutura interna.

#### Mediator
Centraliza a comunicação entre diferentes objetos, reduzindo dependências diretas entre eles.

#### Memento
Permite armazenar e restaurar o estado interno de um objeto preservando seu encapsulamento.

#### Observer
Define um mecanismo de notificação onde múltiplos objetos podem reagir às mudanças de estado de outro objeto.

#### State
Permite alterar o comportamento de um objeto conforme seu estado interno.

#### Strategy
Encapsula diferentes algoritmos ou comportamentos atrás de uma mesma abstração, permitindo que sejam substituídos sem alterar o código consumidor.

#### Template Method
Define a estrutura geral de um algoritmo enquanto permite que determinadas etapas sejam especializadas.

#### Visitor
Permite adicionar operações sobre uma estrutura de objetos sem modificar diretamente as classes que compõem essa estrutura.

---

## 2. Princípios SOLID

Os princípios SOLID são utilizados como referência para avaliação da qualidade estrutural e das responsabilidades do código.

### S — Single Responsibility Principle (SRP)

Uma classe, módulo ou método deve possuir uma responsabilidade claramente definida.

#### Exemplo
Uma `TForm` não deve concentrar simultaneamente:
- regras de negócio;
- persistência;
- validação;
- comunicação HTTP;
- geração de relatórios;
- apresentação visual.

Cada responsabilidade deve permanecer na camada adequada.

### O — Open/Closed Principle (OCP)

O código deve estar **aberto para extensão e fechado para modificação**.

Novos comportamentos devem, sempre que possível, ser adicionados sem exigir alterações constantes em código estável. Polimorfismo, Strategy, Factory e outras abstrações podem ser utilizados quando apropriados.

### L — Liskov Substitution Principle (LSP)

Implementações derivadas devem poder substituir suas abstrações sem alterar o comportamento esperado do sistema. Uma implementação não deve quebrar contratos definidos por sua classe base ou interface.

### I — Interface Segregation Principle (ISP)

Interfaces devem ser específicas e coesas. Evite interfaces excessivamente grandes que obriguem implementações a depender de métodos que não utilizam. Prefira contratos pequenos e direcionados a responsabilidades específicas.

### D — Dependency Inversion Principle (DIP)

Módulos de alto nível não devem depender diretamente de implementações concretas. Ambos devem depender de abstrações.

Sempre que apropriado:

```text
Regra de negócio
      ↓
  Interface
      ↓
Implementação
```

em vez de:

```text
Regra de negócio
      ↓
Classe concreta
```

Isso reduz acoplamento e facilita substituição, testes e evolução.

---

## 3. Programação Orientada a Interfaces

Interfaces são utilizadas como contratos entre componentes sempre que o desacoplamento arquitetural justificar sua existência.

No padrão adotado pelo RickCraft:

- interfaces expõem operações através de `function`, evitando `procedure` nos contratos;
- métodos que implementam uma interface ficam em `protected`;
- o bloco `private` deve existir mesmo quando não houver campos privados;
- o `constructor Create` da implementação fica em `protected`;
- o `destructor Destroy; override;` fica em `public`;
- a criação pública da implementação ocorre através de `class function New`;
- `New` retorna a interface correspondente, e não a classe concreta;
- campos internos da classe utilizam prefixo `F`;
- argumentos utilizam prefixo `A`;
- variáveis locais utilizam prefixo `L`;
- interfaces devem possuir GUID válido e único.

### Contrato e Implementação Básicos

```pascal
interface

type
  IClienteRepository = interface
    ['{7B0C03EC-A12F-4C36-9478-0EF0CD56C7F4}']
    function BuscarPorID(const AID: Integer): IClienteRepository;
  end;

  TClienteRepository = class(TInterfacedObject, IClienteRepository)
  private
  protected
    { Metodos da Interface }
    function BuscarPorID(const AID: Integer): IClienteRepository;
    constructor Create;
  public
    destructor Destroy; override;
    class function New: IClienteRepository;
  end;

implementation

constructor TClienteRepository.Create;
begin
  inherited Create;
end;

destructor TClienteRepository.Destroy;
begin
  inherited;
end;

class function TClienteRepository.New: IClienteRepository;
begin
  Result := Self.Create;
end;

function TClienteRepository.BuscarPorID(const AID: Integer): IClienteRepository;
begin
  { Executa a busca }
  Result := Self;
end;

end.
```

Nesse modelo, o consumidor trabalha com `IClienteRepository` e não precisa conhecer `TClienteRepository`.

### Dependência Entre Interfaces e Retorno ao Contexto Anterior

Quando uma operação precisa disponibilizar um resultado especializado sem quebrar o encadeamento por interfaces, o contrato pode separar a operação principal do resultado.

O fluxo estrutural funciona da seguinte forma:

```text
IClienteRepository
        │
        │ Result
        ▼
  IClienteResult
        │
        │ ToBack
        ▼
IClienteRepository
```

Os contratos permanecem baseados em interfaces:

```pascal
interface

type
  IClienteRepository = interface;
  IClienteResult = interface;

  IClienteRepository = interface
    ['{3CC9581B-48FC-41B0-B2D6-D476E5FE3137}']
    function BuscarPorID(const AID: Integer): IClienteRepository;
    function Result: IClienteResult;
  end;

  IClienteResult = interface
    ['{8CC4E9C2-D5CC-49D1-ADE5-6EF855F04F2E}']
    function Cliente(out AClient: TClient): IClienteResult;
    function ToBack: IClienteRepository;
  end;
```

A implementação do repositório mantém o resultado internamente e o disponibiliza somente através do contrato `IClienteResult`:

```pascal
type
  TClienteRepository = class(TInterfacedObject, IClienteRepository)
  private
    FResult: IClienteResult;
  protected
    { Metodos da Interface }
    function BuscarPorID(const AID: Integer): IClienteRepository;
    function Result: IClienteResult;
    constructor Create;
  public
    destructor Destroy; override;
    class function New: IClienteRepository;
  end;

implementation

constructor TClienteRepository.Create;
begin
  inherited Create;
end;

destructor TClienteRepository.Destroy;
begin
  FResult := nil;
  inherited;
end;

class function TClienteRepository.New: IClienteRepository;
begin
  Result := Self.Create;
end;

function TClienteRepository.BuscarPorID(const AID: Integer): IClienteRepository;
begin
  { Executa a busca }
  Result := Self;
end;

function TClienteRepository.Result: IClienteResult;
begin
  if not Assigned(FResult) then
    FResult := TClienteResult.New(Self);
  Result := FResult;
end;
```

O objeto de resultado recebe a abstração do objeto pai e mantém uma referência fraca para evitar que o relacionamento bidirecional forme um ciclo de contagem de referências:

```pascal
interface

uses
  System.SysUtils;

type
  IClienteRepository = interface;
  IClienteResult = interface;

  IClienteResult = interface
    ['{D35BA7CF-08A6-4A47-9656-70E30E9869DA}']
    function Cliente(out AClient: TClient): IClienteResult;
    function ToBack: IClienteRepository;
  end;

  TClienteResult = class(TInterfacedObject, IClienteResult)
  private
    [weak]
    FParent: IClienteRepository;
    procedure SetupStart;
  protected
    { Metodos da Interface }
    function Cliente(out AClient: TClient): IClienteResult;
    function ToBack: IClienteRepository;
    constructor Create; overload;
    constructor Create(const AValue: IClienteRepository); overload;
  public
    destructor Destroy; override;
    class function New: IClienteResult; overload;
    class function New(const AValue: IClienteRepository): IClienteResult; overload;
  end;

implementation

constructor TClienteResult.Create;
begin
  inherited Create;
  SetupStart;
end;

constructor TClienteResult.Create(const AValue: IClienteRepository);
begin
  inherited Create;
  FParent := AValue;
  SetupStart;
end;

destructor TClienteResult.Destroy;
begin
  FParent := nil;
  inherited;
end;

class function TClienteResult.New: IClienteResult;
begin
  Result := Self.Create;
end;

class function TClienteResult.New(const AValue: IClienteRepository): IClienteResult;
begin
  Result := Self.Create(AValue);
end;

procedure TClienteResult.SetupStart;
begin
end;

function TClienteResult.Cliente(out AClient: TClient): IClienteResult;
begin
  { Preenche AClient }
  Result := Self;
end;

function TClienteResult.ToBack: IClienteRepository;
begin
  if not Assigned(FParent) then
    raise Exception.Create('O Parent da interface não foi informado para retornar.');
  Result := FParent;
end;

end.
```

Esse desenho permite navegar entre contratos sem expor as classes concretas ao consumidor:

```text
IClienteRepository
  .BuscarPorID(...)
  .Result
    .Cliente(...)
  .ToBack
```

#### Relação com Inversão de Dependência

Na fronteira pública, a dependência está orientada às abstrações:

```text
Consumidor
    ↓
IClienteRepository
    ↓
IClienteResult
```

O consumidor não depende de `TClienteRepository` nem de `TClienteResult`.

Entretanto, no exemplo acima, `TClienteRepository.Result` ainda conhece `TClienteResult` no momento da criação:

```pascal
FResult := TClienteResult.New(Self);
```

Portanto, esse ponto específico é uma dependência concreta de construção. Quando houver necessidade real de inversão também nesse nível, a criação deve ser delegada a uma fábrica ou recebida por injeção de dependência.

O RickCraft não deve adicionar essa abstração automaticamente. Ela deve ser introduzida somente quando houver justificativa arquitetural, preservando o princípio de evitar **overengineering**.

Essa abordagem favorece:

- contratos explícitos;
- baixo acoplamento para o consumidor;
- encadeamento fluente entre interfaces;
- substituição de implementações;
- testes unitários;
- isolamento de responsabilidades;
- evolução independente entre componentes.

---

## 4. Clean Code

O código deve priorizar legibilidade, previsibilidade e manutenção.

### Convenção de Nomenclatura Delphi

O RickCraft adota as seguintes convenções:

| Elemento | Convenção | Exemplo |
|---|---|---|
| Classe | Prefixo `T` | `TClienteService` |
| Interface | Prefixo `I` | `IClienteService` |
| Campo privado | Prefixo `F` | `FClienteRepository` |
| Argumento/parâmetro | Prefixo `A` | `AClienteID` |
| Variável local | Prefixo `L` | `LValorTotal` |
| Constante | CAIXA ALTA, iniciando e terminando com `_` | `_NOME_` |
| Constante composta | Palavras separadas por `_` | `_NOME_COMPLETO_` |

### Declaração de Variáveis

Variáveis devem:

- possuir o menor escopo possível;
- ser declaradas próximas ao seu uso;
- possuir nomes descritivos;
- evitar abreviações sem significado claro;
- representar claramente sua responsabilidade;
- utilizar o prefixo `L` quando forem locais.

Evite:

```pascal
var
  x: Integer;
  v: Double;
  aux: string;
```

Prefira:

```pascal
var
  LIndiceProduto: Integer;
  LValorTotal: Double;
  LDescricaoCliente: string;
```

### Regra para Constantes

Constantes Delphi devem obrigatoriamente:

1. ser escritas em **CAIXA ALTA**;
2. começar com `_`;
3. terminar com `_`;
4. utilizar `_` para separar palavras em nomes compostos.

Correto:

```pascal
const
  _NOME_ = 'RickCraft';
  _NOME_COMPLETO_ = 'RickCraft Delphi Skill';
  _TEMPO_LIMITE_CONEXAO_ = 30;
```

Evitar:

```pascal
const
  Nome = 'RickCraft';
  NOME_COMPLETO = 'RickCraft Delphi Skill';
  TempoLimiteConexao = 30;
```

### Enumerados com Escopo

Quando um enumerado precisar de escopo explícito, utilizar `{$SCOPEDENUMS ON}` na região da declaração.

Exemplo:

```pascal
{$SCOPEDENUMS ON}

type
  TMyEnum = (One, Two);
{$SCOPEDENUMS OFF}
```

Com `SCOPEDENUMS` ativo, os valores devem ser acessados através do tipo:

```pascal
LValue := TMyEnum.One;
```
>[!NOTE]
>O `{$SCOPEDENUMS OFF}` pode ser utilizado após a declaração quando a diretiva não deve afetar o restante da unit.

### Criação de Classes por New

Quando uma classe concreta adotar o método de criação `New`, o método deve concentrar a criação e retornar o tipo declarado pela própria API.

Exemplo:

```pascal
interface

type
  TMyClass = class
  public
    class function New: TMyClass;
  end;

implementation

class function TMyClass.New: TMyClass;
begin
  Result := Self.Create;
end;

end.
```

Para classes que implementam interfaces, prevalece a regra da seção **Programação Orientada a Interfaces**: `New` deve retornar a interface correspondente e o `constructor Create` deve permanecer em `protected`.

### Métodos Curtos e Coesos

Métodos devem possuir responsabilidade claramente identificável.

Quando um método realiza muitas operações diferentes, deve ser analisado para verificar se há:

- múltiplas responsabilidades;
- baixa coesão;
- excesso de condicionais;
- níveis excessivos de indentação;
- duplicação;
- regras de negócio misturadas com infraestrutura;
- necessidade de extração de métodos ou componentes.

O objetivo não é reduzir métodos arbitrariamente, mas manter cada método compreensível e responsável por uma operação coerente.

### Method Toxicity Metrics

Além dos critérios qualitativos de Clean Code, o RickCraft utiliza as **Toxicity Metrics configuradas no Delphi** como limites objetivos para identificar métodos que exigem análise estrutural.

Essas métricas não substituem a avaliação arquitetural. Elas funcionam como **limiares de alerta**: quando um método ultrapassa um dos valores configurados, o RickCraft deve tratá-lo como um ponto que precisa ser revisado antes de ser considerado adequado.

A configuração adotada pelo projeto é:

| Métrica | Limite |
|---|---:|
| Function Length | `20` |
| Parameter Count | `6` |
| If Depth | `5` |
| Cyclomatic Complexity | `6` |

#### Function Length — 20
Métodos com mais de `20` linhas devem ser analisados quanto a:
- excesso de responsabilidades;
- possibilidade de extração de comportamento;
- mistura entre regra de negócio, infraestrutura e apresentação;
- dificuldade de leitura e manutenção.

O limite não significa que todo método acima de `20` linhas deva ser dividido automaticamente. A revisão deve considerar coesão, clareza e responsabilidade antes de qualquer alteração.

#### Parameter Count — 6
Métodos com mais de `6` parâmetros devem ser analisados quanto a:
- excesso de dependências;
- responsabilidade ampla demais;
- necessidade de agrupar dados relacionados em uma estrutura apropriada;
- dificuldade de leitura, chamada e teste.

A criação de novos objetos ou abstrações apenas para reduzir a quantidade de parâmetros não deve ocorrer sem justificativa arquitetural.

#### If Depth — 5
Estruturas condicionais com profundidade superior a `5` níveis devem ser analisadas quanto a:
- excesso de aninhamento;
- dificuldade de compreensão do fluxo;
- possibilidade de uso de cláusulas de guarda;
- separação de responsabilidades;
- aplicação de polimorfismo ou padrões comportamentais quando houver justificativa.

O objetivo é reduzir complexidade acidental sem substituir estruturas simples por abstrações desnecessárias.

#### Cyclomatic Complexity — 6
Métodos com complexidade ciclomática superior a `6` devem ser analisados quanto a:
- quantidade excessiva de caminhos de execução;
- concentração de regras de negócio;
- condicionais ou ramificações em excesso;
- dificuldade de teste;
- possibilidade de decomposição em operações menores e coesas.

A redução da complexidade deve preservar o comportamento existente e respeitar os princípios de simplicidade e de evitar overengineering.

#### Aplicação pelo RickCraft
Durante a análise de código, o RickCraft deve:

1. considerar os quatro limites configurados;
2. identificar qual métrica foi ultrapassada;
3. avaliar a causa estrutural antes de propor mudanças;
4. explicar tecnicamente a violação encontrada;
5. propor refatoração somente quando ela melhorar clareza, coesão, testabilidade ou manutenção;
6. não alterar os limites definidos pelo projeto por conveniência.

> [!NOTE]
> Ultrapassar um limite de Toxicity Metrics exige análise; não autoriza refatoração automática.

---

## Base Técnica de Referência

O repositório mantém fontes técnicas locais e um índice controlado de referências externas. Consulte o [Registry de referências técnicas](registries/technical-references.md), a [referência de Padrões de Projeto](<docs/Referencia Padrões de Projeto.pdf>), a [referência para Refatoração de Projetos](<docs/Referencia para Refatoração de Porjetos.pdf>) e o [índice de sites de referência](docs/Site_REF.MD).

Essas fontes complementam o conhecimento do RickCraft e devem ser consultadas quando forem materialmente aplicáveis. Conceitos podem ser considerados independentemente da linguagem do exemplo; código de outra linguagem não deve ser copiado mecanicamente para Delphi/Object Pascal. Policies e contratos normativos aprovados do RickCraft possuem precedência. Detalhes de consulta e rastreabilidade estão na [POL-0000000004](policies/POL-0000000004-fontes-tecnicas-referencia.md).

---

## Postura de Revisão do RickCraft

RickCraft não deve simplesmente aceitar código porque ele:

- compila;
- executa;
- produz o resultado esperado.

Código funcional ainda pode possuir problemas arquiteturais.

Durante uma revisão, devem ser considerados aspectos como:

- acoplamento;
- coesão;
- responsabilidades;
- dependências;
- testabilidade;
- extensibilidade;
- nomenclatura;
- encapsulamento;
- duplicação;
- complexidade;
- legibilidade;
- limites configurados de Method Toxicity Metrics;
- aplicação inadequada de padrões;
- abstrações desnecessárias;
- **Code Smells**.

---

## Protocolo de Resposta

Quando solicitado a revisar ou melhorar código, o RickCraft deve estruturar sua análise em três etapas principais:

### 1. Análise Crítica
Identificar objetivamente:
- problemas encontrados;
- regras violadas;
- riscos arquiteturais;
- **Code Smells**;
- responsabilidades inadequada;
- acoplamentos desnecessários;
- impacto potencial das decisões existentes.

### 2. Refatoração RickCraft
Quando a solicitação permitir alterações no código, apresentar uma implementação compatível com as regras estabelecidas pela skill.

A solução deve buscar:
- clareza;
- baixo acoplamento;
- alta coesão;
- responsabilidades bem definidas;
- testabilidade;
- manutenção sustentável.

### 3. Justificativa Arquitetural
Cada alteração relevante deve possuir justificativa técnica.

> [!NOTE]
> **Exemplo:** Foi aplicado o padrão Strategy para remover a seleção de comportamento baseada em um grande bloco `case`, permitindo que novas estratégias sejam adicionadas sem modificar o código consumidor.

A justificativa deve explicar **qual problema está sendo resolvido**, e não apenas citar o nome de um padrão.

---

## Evitar Overengineering

RickCraft não deve introduzir padrões, interfaces, classes ou camadas sem necessidade técnica.

Um Design Pattern não deve ser utilizado simplesmente porque existe.

Antes de adicionar uma abstração, deve existir uma justificativa baseada em pelo menos um dos seguintes fatores:

- redução de acoplamento;
- aumento de coesão;
- extensibilidade;
- substituição de implementações;
- testabilidade;
- isolamento de infraestrutura;
- eliminação de duplicação;
- redução comprovável de complexidade.

> [!IMPORTANT]
> Simplicidade também é uma decisão arquitetural.

---

## Uso com Inteligência Artificial

RickCraft foi projetado para atuar como referência de governança durante processos de desenvolvimento assistidos por IA.

Uma solicitação pode ser simples, por exemplo:

```text
RickCraft, revise esta classe Delphi.
```

ou:

```text
RickCraft, analise esta implementação e identifique violações de SOLID,
Clean Code, Design Patterns e convenções Delphi.
```

A skill deve compreender que sua função é realizar uma avaliação técnica do código antes de propor alterações.

---

## Resultado Esperado

O objetivo final do RickCraft não é produzir código sofisticado.

É produzir código que seja:

- previsível;
- legível;
- testável;
- desacoplado;
- coeso;
- extensível quando necessário;
- simples quando possível;
- consistente com o restante do projeto;
- sustentável ao longo do tempo.

---

## Sumário

- [Sobre o RickCraft](#sobre-o-rickcraft)
- [Objetivos](#objetivos)
- [Pilares Técnicos](#pilares-técnicos)
- [1. Design Patterns](#1-design-patterns)
  - [Padrões Criacionais](#padrões-criacionais)
    - [Factory Method](#factory-method)
    - [Abstract Factory](#abstract-factory)
    - [Builder](#builder)
    - [Prototype](#prototype)
    - [Singleton](#singleton)
  - [Padrões Estruturais](#padrões-estruturais)
    - [Adapter](#adapter)
    - [Bridge](#bridge)
    - [Composite](#composite)
    - [Decorator](#decorator)
    - [Facade](#facade)
    - [Flyweight](#flyweight)
    - [Proxy](#proxy)
  - [Padrões Comportamentais](#padrões-comportamentais)
    - [Chain of Responsibility](#chain-of-responsibility)
    - [Command](#command)
    - [Interpreter](#interpreter)
    - [Iterator](#iterator)
    - [Mediator](#mediator)
    - [Memento](#memento)
    - [Observer](#observer)
    - [State](#state)
    - [Strategy](#strategy)
    - [Template Method](#template-method)
    - [Visitor](#visitor)
- [2. Princípios SOLID](#2-princípios-solid)
  - [S — Single Responsibility Principle (SRP)](#s--single-responsibility-principle-srp)
  - [O — Open/Closed Principle (OCP)](#o--openclosed-principle-ocp)
  - [L — Liskov Substitution Principle (LSP)](#l--liskov-substitution-principle-lsp)
  - [I — Interface Segregation Principle (ISP)](#i--interface-segregation-principle-isp)
  - [D — Dependency Inversion Principle (DIP)](#d--dependency-inversion-principle-dip)
- [3. Programação Orientada a Interfaces](#3-programação-orientada-a-interfaces)
  - [Contrato e Implementação Básicos](#contrato-e-implementação-básicos)
  - [Dependência Entre Interfaces e Retorno ao Contexto Anterior](#dependência-entre-interfaces-e-retorno-ao-contexto-anterior)
    - [Relação com Inversão de Dependência](#relação-com-inversão-de-dependência)
- [4. Clean Code](#4-clean-code)
  - [Convenção de Nomenclatura Delphi](#convenção-de-nomenclatura-delphi)
  - [Declaração de Variáveis](#declaração-de-variáveis)
  - [Regra para Constantes](#regra-para-constantes)
  - [Enumerados com Escopo](#enumerados-com-escopo)
  - [Criação de Classes por New](#criação-de-classes-por-new)
  - [Métodos Curtos e Coesos](#métodos-curtos-e-coesos)
  - [Method Toxicity Metrics](#method-toxicity-metrics)
    - [Function Length — 20](#function-length--20)
    - [Parameter Count — 6](#parameter-count--6)
    - [If Depth — 5](#if-depth--5)
    - [Cyclomatic Complexity — 6](#cyclomatic-complexity--6)
    - [Aplicação pelo RickCraft](#aplicação-pelo-rickcraft)
- [Base Técnica de Referência](#base-técnica-de-referência)
- [Postura de Revisão do RickCraft](#postura-de-revisão-do-rickcraft)
- [Protocolo de Resposta](#protocolo-de-resposta)
  - [1. Análise Crítica](#1-análise-crítica)
  - [2. Refatoração RickCraft](#2-refatoração-rickcraft)
  - [3. Justificativa Arquitetural](#3-justificativa-arquitetural)
- [Evitar Overengineering](#evitar-overengineering)
- [Uso com Inteligência Artificial](#uso-com-inteligência-artificial)
- [Resultado Esperado](#resultado-esperado)
- [Licença](#licença)
- [Idiomas](#idiomas)
- [RickCraft](#rickcraft)

---

## Licença

Este projeto é distribuído de acordo com os termos definidos no arquivo [`LICENSE`](LICENSE) deste repositório.

Antes de utilizar, modificar, redistribuir ou incorporar o RickCraft em outro projeto, consulte o conteúdo integral da licença para conhecer os direitos, limitações e condições aplicáveis.

> [!NOTE]
> O arquivo `LICENSE` é a referência oficial para os termos de licenciamento deste projeto.

---

## Idiomas

Este projeto possui documentação em dois idiomas:

- [English — README.md](README.md)
- **Português — README_PTBr.md**

---

## RickCraft

**Governança técnica, arquitetura e qualidade de código para Delphi/Object Pascal.**

> Código que funciona é o início.
>
> Código que pode evoluir com segurança é o objetivo.

