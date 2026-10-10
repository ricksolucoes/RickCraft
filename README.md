<div align="center">

# RickCraft (Skill) — Technical Governance & Delphi Architecture

[![Delphi](https://img.shields.io/badge/Delphi-Object%20Pascal-red?logo=delphi)](https://www.embarcadero.com/products/delphi)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%26%20SOLID-blue)](#pilares-tecnicos)
[![Design Patterns](https://img.shields.io/badge/Design%20Patterns-GoF-purple)](#1-design-patterns)
[![AI Skill](https://img.shields.io/badge/AI-Skill-green)](#sobre-o-rickcraft)
[![License](https://img.shields.io/badge/License-MIT%20LICENSE-lightgrey)](LICENSE)

</div>

🌐 Language: English | [Portuguese](README_PTBr.md)

---

## About RickCraft

**RickCraft** is a skill specialized in **technical governance, software architecture, code quality, and Delphi/Object Pascal engineering**.

Its purpose is to serve as a governance layer for AI-assisted development, establishing technical criteria that should be considered during:

- code analysis;
- implementation;
- refactoring;
- architectural reviews;
- creation of new classes and interfaces;
- application of design patterns;
- evaluation of coupling and responsibilities;
- identification of **Code Smells**;
- maintenance and evolution of Delphi systems.

RickCraft should not simply generate code that compiles.

Code produced or reviewed should aim for **clarity, low coupling, high cohesion, testability, extensibility, and long-term maintainability**.

This repository serves as a **technical reference source** for the rules and principles used by the skill.

---

## Objectives

RickCraft was designed to help maintain a consistent architectural standard across Delphi projects.

Its main objectives are:

- **Ensure architectural consistency:** maintain predictable technical standards regardless of who wrote or generated the code.
- **Promote low coupling:** reduce unnecessary dependencies between classes, modules, and layers.
- **Increase cohesion:** keep each unit of code focused on well-defined responsibilities.
- **Improve testability:** favor abstractions and structures that support unit testing and dependency isolation.
- **Reduce technical debt:** identify structural decisions that may compromise future maintenance, evolution, or stability.
- **Identify Code Smells:** detect signs of architectural or structural problems before they become difficult-to-fix issues.
- **Promote sustainable code:** produce code that is understandable, predictable, and ready to evolve.

---

## Technical Pillars

RickCraft analyzes and produces code based on four main pillars:

1. **Design Patterns**
2. **SOLID Principles**
3. **Interface-Oriented Programming**
4. **Clean Code**

These concepts should not be applied mechanically.

A pattern, abstraction, or additional layer should exist only when it solves a concrete problem related to architecture, maintenance, extensibility, testability, or decoupling.

> [!IMPORTANT]
> **Fundamental rule:** architecture should reduce complexity, not create it.

---

## 1. Design Patterns

RickCraft uses the **23 classic patterns from the Gang of Four — GoF catalog** as a reference.

The patterns are divided into three groups:

- Creational;
- Structural;
- Behavioral.

They should be used when there is an architectural justification for applying them.

### Creational Patterns

These patterns deal with object creation and instantiation.

#### Factory Method
Defines an abstraction for object creation, allowing specific implementations to determine which concrete class is instantiated.

#### Abstract Factory
Allows families of related objects to be created without coupling client code to concrete classes.

#### Builder
Separates the process of constructing a complex object from its final representation. It is especially useful when an object has many configuration options or initialization steps.

#### Prototype
Allows new objects to be created by copying an existing instance.

#### Singleton
Ensures that a given class has only one instance and provides a controlled access point to it.

In RickCraft, when a Singleton is truly necessary, creation and release of the instance should remain centralized within the class itself.

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

The constructor remains private to prevent consumers from creating instances outside the controlled access point.

> [!WARNING]
> The use of Singleton should be carefully evaluated due to the risk of introducing global state and increasing coupling. The example above also does not implement synchronization for concurrent access; in multithreaded scenarios, instance creation and release require appropriate protection.

### Structural Patterns

These patterns deal with composition and organization among classes and objects.

#### Adapter
Allows components with incompatible interfaces to be integrated through an adaptation layer.

#### Bridge
Separates an abstraction from its implementation, allowing both to evolve independently.

#### Composite
Allows object hierarchies to be represented as tree structures and individual objects and compositions to be treated uniformly.

#### Decorator
Dynamically adds responsibilities to an object without modifying its original implementation.

#### Facade
Provides a simplified interface to a complex set of classes or subsystems.

#### Flyweight
Reduces memory usage by sharing common state among multiple objects.

#### Proxy
Creates an intermediary object responsible for controlling access to another object.

### Behavioral Patterns

These patterns deal with communication, collaboration, and the distribution of responsibilities among objects.

#### Chain of Responsibility
Passes a request through a chain of handlers until one of them is responsible for processing it.

#### Command
Encapsulates an operation or request in an independent object.

#### Interpreter
Defines a representation for a language or expression and provides mechanisms for interpreting it.

#### Iterator
Allows a collection to be traversed without exposing its internal structure.

#### Mediator
Centralizes communication among different objects, reducing direct dependencies between them.

#### Memento
Allows an object's internal state to be stored and restored while preserving encapsulation.

#### Observer
Defines a notification mechanism in which multiple objects can react to changes in another object's state.

#### State
Allows an object's behavior to change according to its internal state.

#### Strategy
Encapsulates different algorithms or behaviors behind the same abstraction, allowing them to be replaced without changing the consuming code.

#### Template Method
Defines the general structure of an algorithm while allowing specific steps to be specialized.

#### Visitor
Allows operations to be added to an object structure without directly modifying the classes that make up that structure.

---

## 2. SOLID Principles

The SOLID principles are used as a reference for evaluating the structural quality of code and the distribution of responsibilities.

### S — Single Responsibility Principle (SRP)

A class, module, or method should have one clearly defined responsibility.

#### Example
A `TForm` should not simultaneously contain:
- business rules;
- persistence;
- validation;
- HTTP communication;
- report generation;
- visual presentation.

Each responsibility should remain in the appropriate layer.

### O — Open/Closed Principle (OCP)

Code should be **open for extension and closed for modification**.

Whenever possible, new behaviors should be added without requiring constant changes to stable code. Polymorphism, Strategy, Factory, and other abstractions may be used when appropriate.

### L — Liskov Substitution Principle (LSP)

Derived implementations should be able to replace their abstractions without changing the expected behavior of the system. An implementation must not violate contracts defined by its base class or interface.

### I — Interface Segregation Principle (ISP)

Interfaces should be specific and cohesive. Avoid excessively large interfaces that force implementations to depend on methods they do not use. Prefer small contracts focused on specific responsibilities.

### D — Dependency Inversion Principle (DIP)

High-level modules should not depend directly on concrete implementations. Both should depend on abstractions.

Whenever appropriate:

```text
Business rule
      ↓
  Interface
      ↓
Implementation
```

instead of:

```text
Business rule
      ↓
Concrete class
```

This reduces coupling and makes substitution, testing, and evolution easier.

---

## 3. Interface-Oriented Programming

Interfaces are used as contracts between components whenever architectural decoupling justifies their existence.

Under the standard adopted by RickCraft:

- interfaces expose operations through `function`, avoiding `procedure` in contracts;
- methods that implement an interface are placed in `protected`;
- the `private` block must exist even when there are no private fields;
- the implementation's `constructor Create` is placed in `protected`;
- `destructor Destroy; override;` is placed in `public`;
- public creation of the implementation is performed through `class function New`;
- `New` returns the corresponding interface rather than the concrete class;
- internal class fields use the `F` prefix;
- arguments use the `A` prefix;
- local variables use the `L` prefix;
- interfaces must have a valid, unique GUID.

### Basic Contract and Implementation

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

In this model, the consumer works with `IClienteRepository` and does not need to know about `TClienteRepository`.

### Dependencies Between Interfaces and Returning to the Previous Context

When an operation needs to expose a specialized result without breaking interface chaining, the contract can separate the main operation from the result.

The structural flow works as follows:

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

The contracts remain interface-based:

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

The repository implementation keeps the result internally and exposes it only through the `IClienteResult` contract:

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

The result object receives the parent object's abstraction and keeps a weak reference to prevent the bidirectional relationship from creating a reference-counting cycle:

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

This design allows navigation between contracts without exposing concrete classes to the consumer:

```text
IClienteRepository
  .BuscarPorID(...)
  .Result
    .Cliente(...)
  .ToBack
```

#### Relationship to Dependency Inversion

At the public boundary, dependencies point toward abstractions:

```text
Consumer
    ↓
IClienteRepository
    ↓
IClienteResult
```

The consumer does not depend on either `TClienteRepository` or `TClienteResult`.

However, in the example above, `TClienteRepository.Result` still knows about `TClienteResult` when creating it:

```pascal
FResult := TClienteResult.New(Self);
```

Therefore, this specific point is a concrete construction dependency. When there is a genuine need to apply inversion at this level as well, creation should be delegated to a factory or supplied through dependency injection.

RickCraft should not add this abstraction automatically. It should be introduced only when there is an architectural justification, preserving the principle of avoiding **overengineering**.

This approach promotes:

- explicit contracts;
- low coupling for the consumer;
- fluent interface chaining;
- implementation substitution;
- unit testing;
- separation of responsibilities;
- independent evolution of components.

---

## 4. Clean Code

Code should prioritize readability, predictability, and maintainability.

### Delphi Naming Conventions

RickCraft adopts the following conventions:

| Element | Convention | Example |
|---|---|---|
| Class | `T` prefix | `TClienteService` |
| Interface | `I` prefix | `IClienteService` |
| Private field | `F` prefix | `FClienteRepository` |
| Argument/parameter | `A` prefix | `AClienteID` |
| Local variable | `L` prefix | `LValorTotal` |
| Constant | UPPERCASE, starting and ending with `_` | `_NOME_` |
| Multiword constant | Words separated by `_` | `_NOME_COMPLETO_` |

### Variable Declarations

Variables should:

- have the smallest possible scope;
- be declared close to where they are used;
- have descriptive names;
- avoid abbreviations without clear meaning;
- clearly represent their responsibility;
- use the `L` prefix when local.

Avoid:

```pascal
var
  x: Integer;
  v: Double;
  aux: string;
```

Prefer:

```pascal
var
  LIndiceProduto: Integer;
  LValorTotal: Double;
  LDescricaoCliente: string;
```

### Rules for Constants

Delphi constants must:

1. be written in **UPPERCASE**;
2. start with `_`;
3. end with `_`;
4. use `_` to separate words in multiword names.

Correct:

```pascal
const
  _NOME_ = 'RickCraft';
  _NOME_COMPLETO_ = 'RickCraft Delphi Skill';
  _TEMPO_LIMITE_CONEXAO_ = 30;
```

Avoid:

```pascal
const
  Nome = 'RickCraft';
  NOME_COMPLETO = 'RickCraft Delphi Skill';
  TempoLimiteConexao = 30;
```

### Scoped Enumerations

When an enumeration requires explicit scoping, use `{$SCOPEDENUMS ON}` in the declaration region.

Example:

```pascal
{$SCOPEDENUMS ON}

type
  TMyEnum = (One, Two);
{$SCOPEDENUMS OFF}
```

With `SCOPEDENUMS` enabled, values must be accessed through the type:

```pascal
LValue := TMyEnum.One;
```
>[!NOTE]
>`{$SCOPEDENUMS OFF}` can be used after the declaration when the directive should not affect the rest of the unit.

### Class Creation via New

When a concrete class adopts the `New` creation method, the method should centralize object creation and return the type declared by its own API.

Example:

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

For classes that implement interfaces, the rule from the **Interface-Oriented Programming** section takes precedence: `New` must return the corresponding interface, and `constructor Create` must remain `protected`.

### Short, Cohesive Methods

Methods should have a clearly identifiable responsibility.

When a method performs many different operations, it should be analyzed for:

- multiple responsibilities;
- low cohesion;
- excessive conditionals;
- excessive nesting levels;
- duplication;
- business rules mixed with infrastructure;
- the need to extract methods or components.

The goal is not to shorten methods arbitrarily, but to keep each method understandable and responsible for one cohesive operation.

### Method Toxicity Metrics

In addition to qualitative Clean Code criteria, RickCraft uses the **Toxicity Metrics configured in Delphi** as objective thresholds for identifying methods that require structural analysis.

These metrics do not replace architectural evaluation. They serve as **warning thresholds**: when a method exceeds one of the configured values, RickCraft should treat it as an area that requires review before it can be considered acceptable.

The project uses the following configuration:

| Metric | Limit |
|---|---:|
| Function Length | `20` |
| Parameter Count | `6` |
| If Depth | `5` |
| Cyclomatic Complexity | `6` |

#### Function Length — 20
Methods longer than `20` lines should be analyzed for:
- excessive responsibilities;
- opportunities to extract behavior;
- mixing of business rules, infrastructure, and presentation;
- difficulty in reading and maintenance.

The limit does not mean that every method longer than `20` lines should automatically be split. The review should consider cohesion, clarity, and responsibility before any changes are made.

#### Parameter Count — 6
Methods with more than `6` parameters should be analyzed for:
- excessive dependencies;
- overly broad responsibility;
- the need to group related data into an appropriate structure;
- difficulty in reading, calling, and testing.

New objects or abstractions should not be created solely to reduce the number of parameters without an architectural justification.

#### If Depth — 5
Conditional structures nested more than `5` levels deep should be analyzed for:
- excessive nesting;
- difficulty understanding the flow;
- opportunities to use guard clauses;
- separation of responsibilities;
- use of polymorphism or behavioral patterns when justified.

The goal is to reduce accidental complexity without replacing simple structures with unnecessary abstractions.

#### Cyclomatic Complexity — 6
Methods with cyclomatic complexity greater than `6` should be analyzed for:
- too many execution paths;
- concentration of business rules;
- excessive conditionals or branching;
- difficulty in testing;
- opportunities to decompose the method into smaller, cohesive operations.

Reducing complexity should preserve existing behavior and respect the principles of simplicity and avoiding overengineering.

#### Application by RickCraft
During code analysis, RickCraft should:

1. consider all four configured limits;
2. identify which metric has been exceeded;
3. evaluate the structural cause before proposing changes;
4. provide a technical explanation of the violation found;
5. propose refactoring only when it improves clarity, cohesion, testability, or maintainability;
6. never change the limits defined by the project for convenience.

> [!NOTE]
> Exceeding a Toxicity Metrics threshold requires analysis; it does not authorize automatic refactoring.

---

## RickCraft Review Approach

RickCraft should not simply accept code because it:

- compiles;
- runs;
- produces the expected result.

Working code can still have architectural problems.

During a review, aspects such as the following should be considered:

- coupling;
- cohesion;
- responsibilities;
- dependencies;
- testability;
- extensibility;
- naming;
- encapsulation;
- duplication;
- complexity;
- readability;
- configured Method Toxicity Metrics limits;
- inappropriate use of patterns;
- unnecessary abstractions;
- **Code Smells**.

---

## Response Protocol

When asked to review or improve code, RickCraft should structure its analysis into three main stages:

### 1. Critical Analysis
Objectively identify:
- problems found;
- violated rules;
- architectural risks;
- **Code Smells**;
- inappropriate responsibilities;
- unnecessary coupling;
- the potential impact of existing decisions.

### 2. RickCraft Refactoring
When the request allows changes to the code, provide an implementation that complies with the rules established by the skill.

The solution should aim for:
- clarity;
- low coupling;
- high cohesion;
- well-defined responsibilities;
- testability;
- sustainable maintainability.

### 3. Architectural Rationale
Every relevant change should have a technical rationale.

> [!NOTE]
> **Example:** The Strategy pattern was applied to remove behavior selection based on a large `case` block, allowing new strategies to be added without modifying the consuming code.

The rationale should explain **what problem is being solved**, not merely name a pattern.

---

## Avoiding Overengineering

RickCraft should not introduce patterns, interfaces, classes, or layers without a technical need.

A Design Pattern should not be used simply because it exists.

Before adding an abstraction, there should be a justification based on at least one of the following factors:

- reduced coupling;
- increased cohesion;
- extensibility;
- implementation substitution;
- testability;
- infrastructure isolation;
- elimination of duplication;
- demonstrable reduction in complexity.

> [!IMPORTANT]
> Simplicity is also an architectural decision.

---

## Use with Artificial Intelligence

RickCraft was designed to serve as a governance reference during AI-assisted development processes.

A request may be simple, for example:

```text
RickCraft, review this Delphi class.
```

or:

```text
RickCraft, analyze this implementation and identify violations of SOLID,
Clean Code, Design Patterns, and Delphi conventions.
```

The skill should understand that its role is to perform a technical evaluation of the code before proposing changes.

---

## Expected Outcome

RickCraft's ultimate goal is not to produce sophisticated code.

It is to produce code that is:

- predictable;
- readable;
- testable;
- decoupled;
- cohesive;
- extensible when necessary;
- simple when possible;
- consistent with the rest of the project;
- sustainable over time.

---

## License

This project is distributed under the terms defined in the [`LICENSE`](LICENSE) file in this repository.

Before using, modifying, redistributing, or incorporating RickCraft into another project, consult the full license text to understand the applicable rights, limitations, and conditions.

> [!NOTE]
> The `LICENSE` file is the official reference for the licensing terms of this project.

---

## Languages

This project provides documentation in two languages:

- [Portuguese — README_PTBr.md](README_PTBr.md)
- **English — README.md**

---

## RickCraft

**Technical governance, architecture, and code quality for Delphi/Object Pascal.**

> Working code is the starting point.
>
> Code that can evolve safely is the goal.
