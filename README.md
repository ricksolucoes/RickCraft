# 🛠️ RickCraft (Skill) - Governança Técnica & Arquitetura Delphi

O **RickCraft** é uma skill especializada em governança de software, arquitetura de sistemas e revisão automatizada de código para o ecossistema **Delphi (Object Pascal)**. 

Este repositório serve como a "fonte única da verdade" técnica, documentando as diretrizes rígidas de design que a Inteligência Artificial deve exigir e que os desenvolvedores devem seguir para garantir a saúde a longo prazo do software.

## 🎯 Objetivos Principais
*   **Garantir a Consistência Arquitetural:** Manter o mesmo padrão de excelência em todo o ecossistema de código, independentemente de quem o escreveu.
*   **Promover o Baixo Acoplamento:** Eliminar dependências rígidas entre classes, facilitando a manutenção e a criação de testes unitários.
*   **Eliminar o Débito Técnico:** Agir como um revisor estrito (*Linter* inteligente), identificando *Code Smells* (maus cheiros no código) antes que eles virem problemas em produção.
*   **Assegurar Código Manutenível:** Garantir que o código seja limpo, legível e fácil de evoluir por qualquer membro da equipe.

## 🧠 Pilares Técnicos de Validação

O RickCraft analisa e gera códigos baseando-se estritamente em quatro pilares fundamentais:

### 1. Design Patterns (Padrões de Projeto)
Uso mandatório do catálogo clássico de 22 padrões para resolver problemas de criação, estruturação e comportamento de objetos, garantindo que o sistema seja modular e que a equipe fale uma linguagem técnica comum:

*   **Padrões Criacionais (Como os objetos são instanciados):**
    *   **Factory Method:** Cria uma interface para criar objetos em uma superclasse, mas permite que as subclasses alterem o tipo dos objetos que serão criados.
    *   **Abstract Factory:** Permite produzir famílias de objetos relacionados sem especificar suas classes concretas.
    *   **Builder:** Permite a construção de objetos complexos passo a passo, separando a construção da representação.
    *   **Prototype:** Permite copiar objetos existentes sem fazer seu código depender de suas classes.
    *   **Singleton:** Garante que uma classe tenha apenas uma instância, fornecendo um ponto global de acesso a ela.

*   **Padrões Estruturais (Como classes e objetos se compõem para formar estruturas maiores):**
    *   **Adapter:** Permite que objetos com interfaces incompatíveis colaborem entre si.
    *   **Bridge:** Divide uma classe grande ou um conjunto de classes intimamente ligadas em duas hierarquias separadas (abstração e implementação).
    *   **Composite:** Permite compor objetos em estruturas de árvores e trabalhar com essas estruturas como se fossem objetos individuais.
    *   **Decorator:** Permite acoplar novos comportamentos a objetos dinamicamente, colocando-os dentro de objetos invólucros (*wrappers*).
    *   **Facade:** Fornece uma interface simplificada para uma biblioteca, um framework ou qualquer outro sistema complexo de classes.
    *   **Flyweight:** Permite encaixar mais objetos na quantidade disponível de memória RAM compartilhando estados comuns entre múltiplos objetos.
    *   **Proxy:** Fornece um substituto ou marcador de posição para outro objeto para controlar o acesso a ele.

*   **Padrões Comportamentais (Como os objetos se comunicam e dividem responsabilidades):**
    *   **Chain of Responsibility:** Permite passar solicitações ao longo de uma cadeia de manipuladores até que um deles a processe.
    *   **Command:** Transforma uma solicitação em um objeto independente que contém todas as informações sobre a solicitação.
    *   **Iterator:** Permite navegar por elementos de uma coleção sem expor sua representação subjacente.
    *   **Mediator:** Restringe comunicações diretas entre objetos e os força a cooperar apenas através de um objeto mediador.
    *   **Memento:** Permite salvar e restaurar o estado anterior de um objeto sem violar o encapsulamento.
    *   **Observer:** Define um mecanismo de assinatura para notificar múltiplos objetos sobre quaisquer eventos que aconteçam com o objeto que eles estão observando.
    *   **State:** Permite que um objeto altere seu comportamento quando seu estado interno muda, parecendo que mudou de classe.
    *   **Strategy:** Define uma família de algoritmos, coloca cada um deles em uma classe separada e torna seus objetos intercambiáveis.
    *   **Template Method:** Define o esqueleto de um algoritmo na superclasse, mas deixa as subclasses sobrescreverem etapas específicas sem mudar a estrutura.
    *   **Visitor:** Permite separar algoritmos dos objetos nos quais eles operam.


### 2. Princípios SOLID
*   **S (SRP):** Responsabilidade Única. Classes focadas em apenas uma tarefa (regras de negócio separadas da interface visual/Forms).
*   **O (OCP):** Aberto/Fechado. Código aberto para extensão e fechado para modificação (uso de polimorfismo no lugar de longos blocos `case..of`).
*   **L (LSP):** Substituição de Liskov. Classes derivadas devem poder substituir suas classes base sem quebrar o sistema.
*   **I (ISP):** Segregação de Interfaces. Criação de interfaces específicas e pequenas em vez de uma única interface genérica "mãe".
*   **D (DIP):** Inversão de Dependência. O sistema deve depender de abstrações (interfaces) e nunca de classes concretas, aplicando Injeção de Dependência.

### 3. Programação Orientada a Interfaces (Interface-based Design)
*   Toda comunicação entre camadas do sistema deve ser feita através de contratos (Interfaces).
*   Gerenciamento seguro de memória utilizando a contagem de referência nativa do Delphi para evitar *memory leaks* (vazamentos de memória).

### 4. Clean Code (Código Limpo)
*   **Declaração de Variáveis:** Escopo o mais restrito possível, declaradas próximas ao seu uso e com nomes altamente descritivos.
*   Convenção de Nomenclatura Delphi: Prefixo T para classes, I para interfaces, F para campos privados da classe e A para argumentos/parâmetros de métodos. Constantes devem ser declaradas sempre em CAIXA ALTA, começar com _ e terminar com _. Quando o nome for composto, as palavras devem ser separadas por _. Exemplos: `_NOME_`, `_NOME_COMPLETO_`.
*   **Métodos Curtos:** Procedures e funções focadas, pequenas e fáceis de ler.01

## 🚀 Como a IA Deve Agir (Protocolo de Resposta)
O RickCraft **nunca deve apenas ler e concordar** com o código enviado. Ele foi programado para ser crítico. Para cada interação, a resposta da IA deve seguir esta estrutura:

1.  **🔍 Análise Crítica:** Apontar detalhadamente quais regras de governança ou padrões o código atual está violando.
2.  **🛠️ Refatoração RickCraft:** Apresentar a solução em Delphi totalmente corrigida, limpa e aderente aos pilares acima.
3.  **💡 Justificativa Arquitetural:** Explicar o porquê das mudanças com base nos conceitos técnicos (ex: *"Apliquei o padrão Strategy para eliminar o acoplamento do bloco case..."*).
