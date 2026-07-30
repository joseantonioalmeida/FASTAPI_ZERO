# Lista de Tarefas com usuários autenticados

API REST desenvolvida com FastAPI para gerenciamento de usuários e tarefas, com autenticação JWT, criptografia de senhas, banco de dados assíncrono e uma arquitetura preparada para produção.

## Sobre o projeto

Este projeto é uma aplicação backend completa para controle de tarefas, seguindo boas práticas de desenvolvimento com FastAPI, SQLAlchemy Async, Pydantic e PostgreSQL. A API oferece um fluxo seguro de autenticação, organização de dados por usuário e endpoints bem estruturados para criar, listar, atualizar e remover tarefas.

A proposta do projeto é demonstrar, de forma prática, como construir uma API REST profissional com:

- autenticação e autorização via JWT
- proteção de rotas autenticadas
- separação clara de responsabilidades por módulos
- validação de dados com Pydantic
- persistência assíncrona com SQLAlchemy
- migrações de banco com Alembic
- automação de testes e deploy contínuo

## Stack tecnológica

- FastAPI
- Pydantic
- SQLAlchemy Async
- PostgreSQL
- Alembic
- PyJWT
- pwdlib para hashing de senhas
- Docker Compose
- pytest
- GitHub Actions
- Fly.io

## Arquitetura do projeto

```text
fastapi_zero/
├── app.py                  # aplicação FastAPI e inclusão dos routers
├── database.py            # configuração da engine assíncrona
├── models.py              # modelos SQLAlchemy
├── schemas.py             # modelos Pydantic para validação e resposta
├── security.py            # autenticação JWT e hash de senhas
├── settings.py            # configuração via Settings
├── routers/
│   ├── auth.py            # login, refresh token e autenticação
│   ├── users.py           # cadastro e gerenciamento de usuários
│   └── todos.py           # CRUD de tarefas
migrations/                # migrações do banco
tests/                     # testes automatizados
.github/workflows/         # pipeline CI/CD
fly.toml                   # configuração de deploy no Fly.io
```

## Principais funcionalidades

### Autenticação e segurança

- login com email e senha
- emissão de access token JWT
- refresh token para renovação de sessão
- validação de token em rotas protegidas
- hash seguro de senhas

### Gestão de usuários

- criação de conta
- leitura e atualização de dados do próprio usuário
- exclusão da conta
- proteção por autenticação

### Gestão de tarefas

- criação de tarefas vinculadas ao usuário autenticado
- listagem com filtros por título, descrição e estado
- atualização parcial de tarefas
- remoção de tarefas

## Requisitos

- Python 3.13+
- Poetry
- Docker e Docker Compose
- PostgreSQL

## Instalação

```bash
poetry install
```

## Execução local

### 0. Substituir o .env-example para .env
 - Colocar as variáveis de ambiente certas.
 
### 1. Subir o banco de dados

```bash
docker compose up -d
```

### 2. Aplicar as migrações

```bash
poetry run alembic upgrade head
```

### 3. Iniciar a aplicação

```bash
poetry run task run
```

A API estará disponível em:

- http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Endpoints principais

### Autenticação

- POST /auth/token/ — autenticação e emissão de token JWT
- POST /auth/refresh-token/ — renovação do token

### Usuários

- POST /users/ — cadastro de usuário
- GET /users/ — listagem paginada de usuários
- GET /users/{user_id}/ — detalhes do usuário autenticado
- PUT /users/{user_id}/ — atualização de dados
- DELETE /users/{user_id}/ — remoção da conta

### Tarefas

- POST /todos/ — criação de tarefa
- GET /todos/ — listagem de tarefas do usuário autenticado
- PATCH /todos/{todo_id} — atualização parcial da tarefa
- DELETE /todos/{todo_id} — remoção da tarefa

## Exemplos de uso

### Login

```bash
curl -X POST "http://localhost:8000/auth/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=seu@email.com&password=sua-senha"
```

### Criar usuário

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jose",
    "email": "jose@email.com",
    "password": "123456"
  }'
```

### Listar tarefas com autenticação

```bash
curl -X GET "http://localhost:8000/todos/" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Testes

```bash
poetry shell task test
```

## CI/CD com GitHub Actions e Fly.io

O projeto conta com uma pipeline de integração e entrega contínua configurada no GitHub Actions.

### Fluxo da pipeline

- toda alteração enviada para a branch main dispara a execução da pipeline
- o workflow roda lint e testes automaticamente
- se tudo passar, o processo realiza o deploy da aplicação no Fly.io

### Arquivos envolvidos

- [.github/workflows/main.yml](.github/workflows/main.yml) — configuração da pipeline CI/CD
- [fly.toml](fly.toml) — configuração do deploy na plataforma Fly.io

Esse fluxo garante maior confiabilidade no desenvolvimento, pois qualquer mudança passa por validação automática antes de ser publicada.

## Observações importantes

- as rotas de usuários e tarefas são protegidas por autenticação, com exceção do cadastro e login
- as senhas são armazenadas de forma segura com hash
- a API utiliza o padrão OAuth2 com formulário para autenticação no endpoint de token
