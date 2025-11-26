# 🏛️ Projeto de Banco de Dados: Sistema de Gerenciamento de Acervo e Eventos

## 📄 Sobre o Projeto

Este repositório contém o projeto de modelagem e implementação de um Banco de Dados Relacional para um **Sistema de Gerenciamento de Acervo, Empréstimos, Reservas e Eventos** (tipicamente aplicável a bibliotecas, centros culturais ou instituições com acervo e infraestrutura para eventos).

O projeto foi desenvolvido a partir de um **Modelo Entidade-Relacionamento (MER)** e transformado em um **Modelo Relacional (MR)** completo, culminando na criação do script SQL (Data Definition Language - DDL) para a criação das tabelas.

### 🎯 Objetivos

* **Modelagem de Dados:** Criar um diagrama E-R que represente as regras de negócio de um sistema complexo.
* **Normalização:** Converter o modelo conceitual em um modelo relacional.
* **Implementação SQL:** Gerar o script SQL para construção do esquema do banco de dados.

---

## 📐 Estrutura do Modelo de Dados

O modelo relacional é composto por **10 tabelas**, que gerenciam quatro domínios principais:

1.  **Acervo:** Itens físicos e digitais (livros, e-books, mídias, etc.).
2.  **Usuários:** Cadastro de pessoas que utilizam os serviços (leitores, participantes).
3.  **Transações:** Empréstimos, acessos digitais e reservas de infraestrutura.
4.  **Infraestrutura e Eventos:** Gestão de locais físicos e dos eventos que neles ocorrem.

### 🔑 Chaves Primárias e Relacionamentos Chave

| Tabela | Chave Primária (PK) | Relacionamentos Notáveis |
| :--- | :--- | :--- |
| **ITEM\_ACERVO** | `ID_Item` | Genérica para itens físicos e digitais. |
| **USUÁRIO** | `CPF` | Centraliza as interações de empréstimo/reserva/participação. |
| **Exemplar** | `(ID_Item, Num)` | Entidade fraca que representa cópias do `ITEM_FISICO`. |
| **EMPRESTIMO** | Chave Composta | Liga `Exemplar` e `USUÁRIO`. |
| **EVENTOS** | `ID_Evento` | Contém FK para `INFRAESTRUTURA` (N:1). |

---

## 🛠️ Como Utilizar

Para configurar o esquema do banco de dados, você precisará de um Sistema Gerenciador de Banco de Dados (SGBD) que suporte SQL padrão (como MySQL, PostgreSQL, SQL Server, Oracle, SQLite, etc.).

### Pré-requisitos

* Um SGBD instalado e configurado (ex: PostgreSQL).
* Uma ferramenta de cliente SQL (ex: DBeaver, pgAdmin, VS Code com extensão SQL).

### 🚀 Instalação e Execução

1.  **Crie um novo Banco de Dados** com o nome de sua preferência (ex: `DB_ACERVO_CULTURAL`).

    ```sql
    CREATE DATABASE DB_ACERVO_CULTURAL;
    ```

2.  **Acesse o Banco de Dados** recém-criado.

    ```sql
    USE DB_ACERVO_CULTURAL; 
    -- Ou conecte-se via seu cliente SQL.
    ```

3.  **Execute o Script DDL:** Copie e cole o conteúdo do arquivo `DDL` no seu cliente SQL e execute-o.

    > **Nota:** Certifique-se de executar as tabelas na ordem correta, pois as Chaves Estrangeiras (FKs) dependem que as tabelas "pai" já existam.

### Exemplo de Consulta (SQL)

Para listar os usuários que reservaram alguma infraestrutura:

```sql
SELECT 
    U.Nome, 
    I.Local, 
    R.Data_Reserva_Inicio 
FROM 
    USUARIO U
JOIN 
    RESERVA_INFRA R ON U.CPF = R.CPF_Usuario
JOIN
    INFRAESTRUTURA I ON R.ID_Infra = I.ID_Infra
ORDER BY 
    R.Data_Reserva_Inicio;
