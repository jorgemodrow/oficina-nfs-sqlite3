# Sistema de Oficina & Performance

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Interface](https://img.shields.io/badge/Interface-CLI-1E1E1E?style=for-the-badge&logo=gnometerminal&logoColor=white)
![Dependências](https://img.shields.io/badge/Dependências-Nenhuma-2EA44F?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Concluído-2EA44F?style=for-the-badge)

Aplicação de linha de comando (CLI) desenvolvida em **Python 3** com persistência de dados em **SQLite** para gerenciamento de uma garagem de veículos e instalação de peças de performance.

O sistema permite consultar veículos, visualizar peças disponíveis em estoque, instalar e desinstalar componentes e acompanhar automaticamente a potência total de cada carro a partir dos upgrades instalados.

## Funcionalidades

* **Listagem da garagem:** exibe todos os veículos com potência de fábrica, bônus acumulado e potência total.
* **Ficha técnica:** consulta individualmente um veículo e apresenta suas peças instaladas.
* **Controle de estoque:** lista as peças que estão disponíveis para instalação.
* **Instalação de peças:** associa uma peça disponível a um veículo após validar o carro e a disponibilidade do componente.
* **Desinstalação de peças:** remove uma peça do veículo e devolve o componente ao estoque.
* **Cálculo dinâmico de potência:** a potência total é calculada a partir da potência base e da soma dos bônus das peças instaladas.
* **Validação de entradas:** trata valores numéricos inválidos e cancelamentos durante a entrada de dados.
* **Persistência local:** os dados são armazenados no arquivo `garagem_nfs.db`.

## Arquitetura

O projeto organiza suas responsabilidades em três módulos principais:

```text
                         ┌──────────────┐
                         │   main.py    │
                         │   Controle   │
                         │    da CLI    │
                         └──────┬───────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
        ┌────────────────┐            ┌────────────────┐
        │  interface.py  │            │  database.py   │
        │  Apresentação  │            │  Persistência  │
        └────────────────┘            └───────┬────────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │garagem_nfs.db│
                                      │    SQLite    │
                                      └──────────────┘
```

### `main.py`

Ponto de entrada e controle do fluxo da aplicação.

Responsável por:

* apresentar o menu;
* coordenar as operações;
* solicitar dados ao usuário;
* validar fluxos de alto nível;
* utilizar uma **Dispatch Table** para direcionar as opções do menu.

### `interface.py`

Concentra os recursos de apresentação do terminal.

Responsável por:

* cabeçalhos e divisórias;
* mensagens de sucesso, erro e alerta;
* cores ANSI;
* leitura de números inteiros;
* tratamento de `ValueError` e `KeyboardInterrupt`.

### `database.py`

Concentra a persistência e as operações relacionadas ao banco de dados.

Responsável por:

* criar e inicializar as tabelas;
* inserir os dados iniciais;
* configurar as chaves estrangeiras;
* consultar veículos e peças;
* instalar e desinstalar componentes;
* calcular a potência dos veículos;
* executar consultas parametrizadas.

## Banco de Dados

O sistema utiliza **SQLite**, através do módulo nativo `sqlite3` do Python. Não são necessárias bibliotecas externas.

O banco possui duas tabelas principais:

```text
┌──────────────────────┐
│       carros         │
├──────────────────────┤
│ id (PK)              │
│ modelo (UNIQUE)      │
│ potencia_base        │
└──────────┬───────────┘
           │
           │ 1 : N
           │
           ▼
┌──────────────────────┐
│        pecas         │
├──────────────────────┤
│ id (PK)              │
│ nome                 │
│ bonus_potencia       │
│ carro_id (FK)        │
└──────────────────────┘
```

### Tabela `carros`

| Campo           | Descrição                      |
| --------------- | ------------------------------ |
| `id`            | Identificador único do veículo |
| `modelo`        | Nome do veículo                |
| `potencia_base` | Potência original em cavalos   |

### Tabela `pecas`

| Campo            | Descrição                             |
| ---------------- | ------------------------------------- |
| `id`             | Identificador único da peça           |
| `nome`           | Nome do componente                    |
| `bonus_potencia` | Potência adicionada pela peça         |
| `carro_id`       | Veículo ao qual a peça está associada |

---

## Regras de Negócio

### Estoque

O campo `carro_id` determina o estado da peça:

```text
carro_id = NULL
        ↓
Peça disponível no estoque
```

Quando uma peça é instalada:

```text
carro_id = ID do carro
        ↓
Peça instalada naquele veículo
```

Cada registro da tabela `pecas` representa uma unidade de componente que pode estar livre ou instalada em **um único veículo**.

### Integridade referencial

A conexão com o banco ativa explicitamente as chaves estrangeiras:

```sql
PRAGMA foreign_keys = ON;
```

A relação entre as tabelas utiliza:

```sql
FOREIGN KEY (carro_id)
REFERENCES carros(id)
ON DELETE SET NULL
```

Assim, caso um veículo seja removido, as peças associadas a ele têm seu `carro_id` definido como `NULL`, retornando ao estado de estoque.

## Cálculo da Potência

A potência final não é armazenada como uma coluna independente no banco.

Ela é derivada através de:

```text
Potência Final = Potência Base + Soma dos Bônus das Peças
```

A consulta utilizada pelo sistema é:

```sql
SELECT
    c.id,
    c.modelo,
    c.potencia_base,
    COALESCE(SUM(p.bonus_potencia), 0) AS total_bonus,
    c.potencia_base + COALESCE(SUM(p.bonus_potencia), 0) AS potencia_final
FROM carros c
LEFT JOIN pecas p ON c.id = p.carro_id
GROUP BY c.id, c.modelo, c.potencia_base
ORDER BY potencia_final DESC;
```

### Principais recursos utilizados

* **`LEFT JOIN`** mantém na consulta os veículos que não possuem peças instaladas.
* **`SUM()`** soma os bônus de todas as peças instaladas em cada veículo.
* **`COALESCE(..., 0)`** transforma a ausência de peças em bônus `0`.
* **`GROUP BY`** consolida os registros referentes a cada veículo.
* **`ORDER BY`** organiza a garagem pela potência final, da maior para a menor.

Como a potência é calculada a partir dos dados atuais das peças, não é necessário manter manualmente uma coluna de potência final.

## Validações e Integridade

O sistema realiza validações antes de modificar os dados:

### Instalação

Antes de instalar uma peça, o sistema verifica:

1. se o veículo informado existe;
2. se a peça existe;
3. se a peça ainda está disponível no estoque.

A atualização só ocorre depois dessas verificações.

### Desinstalação

Para remover uma peça, o sistema verifica:

1. se o veículo existe;
2. se a peça existe;
3. se a peça está realmente instalada naquele veículo.

Após a remoção, `carro_id` recebe `NULL` e a peça volta ao estoque.

### Entrada de dados

A função `leia_int()` trata:

* valores que não podem ser convertidos para inteiro;
* interrupções por `Ctrl+C`.

### SQL parametrizado

Os valores fornecidos pelo usuário são enviados às consultas através de parâmetros:

```python
conn.execute(
    "SELECT modelo, potencia_base FROM carros WHERE id = ?;",
    (carro_id,)
)
```

Esse padrão evita a concatenação direta de dados externos nas consultas SQL.

## Dados Iniciais

Na inicialização, o programa cria o banco e as tabelas caso ainda não existam.

Os veículos padrão são inseridos utilizando `INSERT OR IGNORE`, evitando duplicação de modelos.

As peças padrão são carregadas quando a tabela `pecas` está vazia.

Entre os veículos disponíveis estão:

* Honda Civic
* Mazda RX-7
* Nissan 350Z
* Mitsubishi Lancer Evo IX
* Subaru Impreza WRX STI
* Toyota Supra MK4
* Nissan Skyline GT-R R34
* BMW M3 E46
* Audi R8
* Porsche 911 Turbo
* Ford Mustang GT
* Chevrolet Corvette Z06
* Ford Mustang Shelby GT500
* Lamborghini Huracán
* Chevrolet Opala
* Volkswagen Gol GTI

O estoque inicial também contém componentes como:

* Kits Turbo;
* Supercharger;
* Intercooler;
* Bicos injetores;
* Comando de válvulas;
* Pistões forjados;
* Downpipe;
* Escapamento;
* Remap de ECU;
* FuelTech;
* Kits Nitro;
* Injeção água/metanol.

## Exemplo de Uso

### Garagem

```text
=======================================================
                  GARAGEM DE VEÍCULOS
=======================================================
ID   MODELO                     BASE     BÔNUS    TOTAL
-------------------------------------------------------
18   Ford Mustang Shelby GT500  760      +150     910 cv
6    Toyota Supra MK4           320      +120     440 cv
10   Audi R8                    420      +0       420 cv
9    BMW M3 E46                 343      +65      408 cv
1    Honda Civic                160      +72      232 cv
-------------------------------------------------------
```

### Instalação de peça

```text
=======================================================
              ESTOQUE DE PEÇAS DISPONÍVEIS
=======================================================
ID   PEÇA                                BÔNUS
-------------------------------------------------------
3    Turbo Estágio 3 Roletado            +140 cv
5    Intercooler Frontal em Alumínio     +35 cv
-------------------------------------------------------

ID da peça a instalar: 3

Peça 'Turbo Estágio 3 Roletado' instalada com sucesso no Toyota Supra MK4.
Bônus: +140 cv | Nova potência total: 580 cv
```

O fluxo demonstra o recálculo da potência:

```text
Toyota Supra MK4
320 cv
  +
Turbo Estágio 3
+140 cv
  =
460 cv
```

> **Observação:** o exemplo acima deve refletir o estado real do banco no momento em que a demonstração for executada. Caso o Supra já possua outros upgrades, a potência anterior e a potência final poderão ser diferentes.

## Estrutura do Projeto

```text
garagem-tuning/
├── database.py
├── interface.py
├── main.py
├── .gitignore
├── README.md
└── garagem_nfs.db        # criado durante a execução
```

O banco de dados local pode ser incluído no `.gitignore` para evitar versionar dados gerados durante a execução.

## Modelo Lógico do Banco de Dados

![modelo lógico.png](modelo%20l%C3%B3gico.png)

## Requisitos e Execução

### Requisitos

* **Python 3.8 ou superior**
* SQLite através do módulo padrão `sqlite3`
* Nenhuma biblioteca externa

### Executar

No diretório do projeto:

```bash
python main.py
```

Na primeira execução, o programa cria o arquivo:

```text
garagem_nfs.db
```

e inicializa o esquema e os dados padrão.

## 🎮 Menu da Aplicação

```text
1 - Listar Garagem (Potência Total)
2 - Ver Detalhes do Carro
3 - Listar Estoque de Peças
4 - Instalar Peça
5 - Desinstalar Peça
6 - Sair
```

A navegação é realizada diretamente pelo terminal, sem necessidade de interface gráfica ou dependências adicionais.

## Motivação

Este projeto une o aprendizado de arquitetura de software e modelagem relacional com uma paixão minha de infância por carros e jogos de corrida.

A inspiração para o sistema e a seleção de veículos e peças veio da minha vivência com simuladores e clássicos dos videogames — que começou em *Need for Speed: ProStreet* no Nintendo Wii, passando pelo *Shift 2: Unleashed* e *Most Wanted (2012)* no PS3, até a progressão na franquia *Forza Horizon* (do 2 ao 5).

## Autor

Desenvolvido por **Jorge Gabriel Modrow**, estudante de **Análise e Desenvolvimento de Sistemas** na **UFPR**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jorgemodrow)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jorgemodrow)