<div align="center">

<h1>🛠️ RickCraft (Skill) — Governança Técnica & Arquitetura Delphi</h1>

[![Delphi](https://img.shields.io/badge/Delphi-Object%20Pascal-red?logo=delphi)](https://www.embarcadero.com/products/delphi)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%26%20SOLID-blue)](#-pilares-técnicos)
[![Design Patterns](https://img.shields.io/badge/Design%20Patterns-GoF-purple)](#1-design-patterns)
[![AI Skill](https://img.shields.io/badge/AI-Skill-green)](#-sobre-o-rickcraft)
[![License](https://img.shields.io/badge/License-MIT%20LICENSE-lightgrey)](LICENSE)

</div>

🌐 **Idioma:** 🇧🇷 Português | [🇺🇸 English](README.md)

## 📖 Sobre o RickCraft

**RickCraft** é uma skill especializada em **governança técnica, arquitetura de software, qualidade de código e engenharia Delphi/Object Pascal**.

Seu objetivo é atuar como uma camada de governança para desenvolvimento assistido por Inteligência Artificial, estabelecendo critérios técnicos que devem ser considerados durante:

- análise de código;
- implementação;
- refatoração;
- revisão arquitetural;
- criação de novas classes e interfaces;
- aplicação de padrões de projeto;
- avaliação de acoplamento e responsabilidades;
- identificação de *Code Smells*;
- manutenção e evolução de sistemas Delphi.

O RickCraft não deve simplesmente gerar código que compile.

O código produzido ou revisado deve buscar **clareza, baixo acoplamento, alta coesão, testabilidade, extensibilidade e manutenção sustentável ao longo do tempo**.

Este repositório funciona como uma **fonte técnica de referência** para as regras e princípios utilizados pela skill.

---

## 🎯 Objetivos

O RickCraft foi projetado para auxiliar na manutenção de um padrão arquitetural consistente em projetos Delphi.

Seus principais objetivos são:

- **Garantir consistência arquitetural**  
  Manter padrões técnicos previsíveis independentemente de quem escreveu ou gerou o código.

- **Promover baixo acoplamento**  
  Reduzir dependências desnecessárias entre classes, módulos e camadas.

- **Aumentar a coesão**  
  Manter cada unidade de código concentrada em responsabilidades bem definidas.

- **Melhorar a testabilidade**  
  Favorecer abstrações e estruturas que permitam testes unitários e isolamento de dependências.

- **Reduzir débito técnico**  
  Identificar decisões estruturais que podem comprometer manutenção, evolução ou estabilidade futura.

- **Identificar Code Smells**  
  Detectar sinais de problemas arquiteturais ou estruturais antes que se tornem falhas difíceis de corrigir.

- **Favorecer código sustentável**  
  Produzir código compreensível, previsível e preparado para evolução.

---

# 🧠 Pilares Técnicos

O RickCraft analisa e produz código considerando quatro pilares principais:

1. **Design Patterns**
2. **Princípios SOLID**
3. **Programação Orientada a Interfaces**
4. **Clean Code**

Esses conceitos não devem ser aplicados mecanicamente.

Um padrão, abstração ou camada adicional deve existir quando resolver um problema concreto de arquitetura, manutenção, extensibilidade, testabilidade ou desacoplamento.

> **Regra fundamental:** arquitetura deve reduzir complexidade, não criá-la.

---

# 1. Design Patterns

O RickCraft utiliza como referência os **23 padrões clássicos do catálogo Gang of Four — GoF**.

Os padrões são divididos em três grupos:

- Criacionais;
- Estruturais;
- Comportamentais.

Eles devem ser utilizados quando houver justificativa arquitetural para sua aplicação.

## 🏗️ Padrões Criacionais

Tratam da criação e instanciação de objetos.

### Factory Method

Define uma abstração para criação de objetos, permitindo que implementações específicas determinem qual classe concreta será instanciada.

### Abstract Factory

Permite criar famílias de objetos relacionados sem acoplar o código cliente às classes concretas.

### Builder

Separa o processo de construção de um objeto complexo de sua representação final.

É especialmente útil quando um objeto possui muitas configurações ou etapas de inicialização.

### Prototype

Permite criar novos objetos a partir da cópia de uma instância existente.

### Singleton

Garante uma única instância de determinada classe e fornece um ponto controlado de acesso a ela.

> O uso de Singleton deve ser avaliado criteriosamente devido ao risco de introdução de estado global e aumento de acoplamento.

---

## 🧱 Padrões Estruturais

Tratam da composição e organização entre classes e objetos.

### Adapter

Permite integrar componentes com interfaces incompatíveis através de uma camada de adaptação.

### Bridge

Separa uma abstração de sua implementação, permitindo que ambas evoluam independentemente.

### Composite

Permite representar hierarquias de objetos através de estruturas em árvore e tratar objetos individuais e composições de maneira uniforme.

### Decorator

Adiciona responsabilidades dinamicamente a um objeto sem modificar sua implementação original.

### Facade

Fornece uma interface simplificada para um conjunto complexo de classes ou subsistemas.

### Flyweight

Reduz consumo de memória através do compartilhamento de estados comuns entre múltiplos objetos.

### Proxy

Cria um objeto intermediário responsável por controlar o acesso a outro objeto.

---

## 🔄 Padrões Comportamentais

Tratam da comunicação, colaboração e distribuição de responsabilidades entre objetos.

### Chain of Responsibility

Encaminha uma solicitação através de uma cadeia de manipuladores até que algum deles seja responsável por processá-la.

### Command

Encapsula uma operação ou solicitação em um objeto independente.

### Interpreter

Define uma representação para uma linguagem ou expressão e fornece mecanismos para interpretá-la.

### Iterator

Permite percorrer uma coleção sem expor sua estrutura interna.

### Mediator

Centraliza a comunicação entre diferentes objetos, reduzindo dependências diretas entre eles.

### Memento

Permite armazenar e restaurar o estado interno de um objeto preservando seu encapsulamento.

### Observer

Define um mecanismo de notificação onde múltiplos objetos podem reagir às mudanças de estado de outro objeto.

### State

Permite alterar o comportamento de um objeto conforme seu estado interno.

### Strategy

Encapsula diferentes algoritmos ou comportamentos atrás de uma mesma abstração, permitindo que sejam substituídos sem alterar o código consumidor.

### Template Method

Define a estrutura geral de um algoritmo enquanto permite que determinadas etapas sejam especializadas.

### Visitor

Permite adicionar operações sobre uma estrutura de objetos sem modificar diretamente as classes que compõem essa estrutura.

---

# 2. Princípios SOLID

Os princípios SOLID são utilizados como referência para avaliação da qualidade estrutural e das responsabilidades do código.

## S — Single Responsibility Principle — SRP

Uma classe, módulo ou método deve possuir uma responsabilidade claramente definida.

### Exemplo

Uma `TForm` não deve concentrar simultaneamente:

- regras de negócio;
- persistência;
- validação;
- comunicação HTTP;
- geração de relatórios;
- apresentação visual.

Cada responsabilidade deve permanecer na camada adequada.

---

## O — Open/Closed Principle — OCP

O código deve estar:

> **aberto para extensão e fechado para modificação.**

Novos comportamentos devem, sempre que possível, ser adicionados sem exigir alterações constantes em código estável.

Polimorfismo, Strategy, Factory e outras abstrações podem ser utilizados quando apropriados.

---

## L — Liskov Substitution Principle — LSP

Implementações derivadas devem poder substituir suas abstrações sem alterar o comportamento esperado do sistema.

Uma implementação não deve quebrar contratos definidos por sua classe base ou interface.

---

## I — Interface Segregation Principle — ISP

Interfaces devem ser específicas e coesas.

Evite interfaces excessivamente grandes que obriguem implementações a depender de métodos que não utilizam.

Prefira contratos pequenos e direcionados a responsabilidades específicas.

---

## D — Dependency Inversion Principle — DIP

Módulos de alto nível não devem depender diretamente de implementações concretas.

Ambos devem depender de abstrações.

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

# 3. Programação Orientada a Interfaces

Interfaces são utilizadas como contratos entre componentes sempre que o desacoplamento arquitetural justificar sua existência.

Exemplo:

```pascal
type
  IClienteRepository = interface
    ['{A34DB395-BE16-444E-934D-BB09A626BA20}']
    function BuscarPorId(const AId: Integer): TCliente;
  end;
```

Implementação:

```pascal
type
  TClienteRepository = class(TInterfacedObject, IClienteRepository)
  private
  protected
    {Metodos da Interfaces}
    function BuscarPorId(const AId: Integer): TCliente;

    constructor Create;
  public
    destructor Destroy; override;

    class function New: IClienteRepository;
  end;
```

O consumidor depende da abstração:

```pascal
IClienteRepository
```

e não diretamente da implementação:

```pascal
TClienteRepository
```

Essa abordagem favorece:

- baixo acoplamento;
- substituição de implementações;
- testes unitários;
- isolamento de infraestrutura;
- evolução independente entre componentes.

---

# 4. Clean Code

O código deve priorizar legibilidade, previsibilidade e manutenção.

## 🏷️ Convenção de Nomenclatura Delphi

O RickCraft adota as seguintes convenções:

| Elemento | Convenção |
|---|---|
| Classe | Prefixo `T` |
| Interface | Prefixo `I` |
| Campo privado | Prefixo `F` |
| Argumento/parâmetro | Prefixo `A` |
| Variável local | Prefixo `L` |
| Constante | `_NOME_` |
| Constante composta | `_NOME_COMPLETO_` |

### Classes

```pascal
TClienteService
```

### Interfaces

```pascal
IClienteService
```

### Campos privados

```pascal
FClienteRepository
```

### Argumentos e parâmetros

```pascal
procedure BuscarCliente(const AClienteId: Integer);
```

### Variável local

```pascal
LValorTotal
```

### Constante

```pascal
_NOME_
```

### Constante composta

```pascal
_NOME_COMPLETO_
```

## 📍 Declaração de Variáveis

Variáveis devem:

- possuir o menor escopo possível;
- ser declaradas próximas ao seu uso;
- possuir nomes descritivos;
- evitar abreviações sem significado claro;
- representar claramente sua responsabilidade.

Evite:

```pascal
var
  x: Integer;
  v: Double;
  aux: string;
```

Prefira nomes que expressem intenção:

```pascal
var
  LIndiceProduto: Integer;
  LValorTotal: Double;
  LDescricaoCliente: string;
```


## 🔒 Regra para Constantes

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

---

## ✂️ Métodos Curtos e Coesos

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

---

# 🔍 Postura de Revisão do RickCraft

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
- aplicação inadequada de padrões;
- abstrações desnecessárias;
- *Code Smells*.

---

# 🚀 Protocolo de Resposta

Quando solicitado a revisar ou melhorar código, o RickCraft deve estruturar sua análise em três etapas principais.

## 1. 🔍 Análise Crítica

Identificar objetivamente:

- problemas encontrados;
- regras violadas;
- riscos arquiteturais;
- *Code Smells*;
- responsabilidades inadequadas;
- acoplamentos desnecessários;
- impacto potencial das decisões existentes.

---

## 2. 🛠️ Refatoração RickCraft

Quando a solicitação permitir alterações no código, apresentar uma implementação compatível com as regras estabelecidas pela skill.

A solução deve buscar:

- clareza;
- baixo acoplamento;
- alta coesão;
- responsabilidades bem definidas;
- testabilidade;
- manutenção sustentável.

---

## 3. 💡 Justificativa Arquitetural

Cada alteração relevante deve possuir justificativa técnica.

Exemplo:

> Foi aplicado o padrão Strategy para remover a seleção de comportamento baseada em um grande bloco `case`, permitindo que novas estratégias sejam adicionadas sem modificar o código consumidor.

A justificativa deve explicar **qual problema está sendo resolvido**, e não apenas citar o nome de um padrão.

---

# ⚠️ Evitar Overengineering

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

> **Simplicidade também é uma decisão arquitetural.**

---

# 🤖 Uso com Inteligência Artificial

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

# ✅ Resultado Esperado

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

# 📄 Licença

Este projeto é distribuído de acordo com os termos definidos no arquivo [`LICENSE`](LICENSE) deste repositório.

Antes de utilizar, modificar, redistribuir ou incorporar o RickCraft em outro projeto, consulte o conteúdo integral da licença para conhecer os direitos, limitações e condições aplicáveis.

> O arquivo `LICENSE` é a referência oficial para os termos de licenciamento deste projeto.

---

## 🌐 Idiomas

Este projeto possui documentação em dois idiomas:

- 🇺🇸 [English — README.md](README.md)
- 🇧🇷 **Português — README_PTBr.md**

---

## 📌 RickCraft

**Governança técnica, arquitetura e qualidade de código para Delphi/Object Pascal.**

> Código que funciona é o início.  
> Código que pode evoluir com segurança é o objetivo.
