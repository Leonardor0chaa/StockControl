# StockControl — Sistema de Controle de Estoque

## Sobre o projeto

O StockControl é um sistema web de controle de estoque desenvolvido como projeto acadêmico, utilizando Python, Flask e MySQL.

O sistema permite cadastrar produtos e registrar movimentações de entrada e saída, mantendo as quantidades atualizadas no banco de dados.

## Tecnologias utilizadas

- Python 3.11
- Flask
- MySQL
- HTML5
- CSS3
- Git e GitHub

## Funcionalidades implementadas

### 1. Cadastro de Produtos
- Cadastro de produtos com nome, descrição, categoria e preço.
- Definição da quantidade inicial e do estoque mínimo.
- Validação dos campos obrigatórios.
- Armazenamento das informações no MySQL.
- Listagem dos produtos cadastrados e situação do estoque.

### 2. Movimentação de Estoque
- Registro de entradas e saídas de produtos.
- Atualização automática da quantidade disponível.
- Bloqueio de saídas superiores ao estoque disponível.
- Registro do histórico de movimentações.
- Identificação de um administrador de teste como responsável pelas operações.

## Banco de dados

O banco de dados `stockcontrol` possui quatro tabelas:

- `USUARIO`
- `CATEGORIA`
- `PRODUTO`
- `MOVIMENTACAO_ESTOQUE`

## Como executar

1. Instale Python e MySQL.
2. Crie o banco de dados e suas tabelas conforme o modelo do projeto.
3. Crie um ambiente virtual Python.
4. Instale as dependências com `pip install -r requirements.txt`.
5. Configure o arquivo `.env` com as credenciais do banco.
6. Execute `python app.py`.
7. Acesse `http://127.0.0.1:5000/produtos`.

**Observação:** o banco e os dados iniciais precisam estar configurados antes da execução. O login e o gerenciamento completo de usuários ainda não foram implementados.

## Projeto acadêmico

Projeto desenvolvido para demonstrar a implementação de funcionalidades de um sistema de controle de estoque, integrando interface web, regras de negócio e banco de dados relacional.
