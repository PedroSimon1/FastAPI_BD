# Criando uma API Completa com FastAPI e SQLModel

Este projeto é um exemplo prático de como criar uma API com FastAPI, utilizando **Pydantic** para validação de dados, **SQLModel** (que por baixo dos panos usa SQLAlchemy) para comunicação com o banco de dados e integração com **PostgreSQL**.

O projeto conta com um **CRUD Completo** (Create, Read, Update, Delete) de uma entidade chamada `Item`.

## 🛠 Pré-requisitos
- **Python 3.9+** instalado na sua máquina.
- **PostgreSQL** instalado e rodando.
- (Opcional) Ferramentas como o **Insomnia**, **Postman** ou simplesmente o navegador para testar a API via Swagger (embutido no FastAPI).

---

## 📝 Passo a Passo da Configuração

### Passo 1: Preparar o Banco de Dados (PostgreSQL)
1. Abra o seu servidor do PostgreSQL (por exemplo via DBeaver, pgAdmin ou terminal).
2. Crie um banco de dados novo. Por exemplo, vamos chamar de `fastapi_db`.
3. Verifique qual o usuário e a senha para conectar ao seu servidor local (geralmente usuário é `postgres`).

### Passo 2: Criar e Ativar um Ambiente Virtual (Venv)
No terminal do seu projeto, rode os seguintes comandos para criar o ambiente isolado do projeto:

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar as Dependências
O projeto possui um arquivo `requirements.txt`. Instale as bibliotecas rodando:
```bash
pip install -r requirements.txt
```

> **O que estamos instalando?**
> - **fastapi**: O framework web.
> - **uvicorn[standard]**: O servidor ASGI para rodar a aplicação.
> - **sqlmodel**: Biblioteca moderna para interagir com o banco de dados usando Pydantic e SQLAlchemy.
> - **psycopg2-binary**: O "driver" que faz o Python conseguir falar com o PostgreSQL.
> - **python-dotenv**: Para ler nossas configurações do arquivo `.env`.

### Passo 4: Configurar as Variáveis de Ambiente (.env)
1. Neste projeto existe um arquivo chamado `.env`.
2. Abra ele e você verá a linha:
   `DATABASE_URL=postgresql://postgres:suasenha@localhost:5432/fastapi_db`
3. Troque `postgres` pelo seu usuário do banco.
4. Troque `suasenha` pela sua senha.
5. Confirme se a porta (`5432`) e o nome do banco (`fastapi_db`) estão corretos.

### Passo 5: Entendendo a Estrutura de Arquivos
Nós dividimos a aplicação de forma organizada:

- `database.py`: Onde criamos o *"motor"* de conexão com o banco de dados usando as configurações do nosso arquivo `.env`. Também onde disponibilizamos as conexões ativas (`Session`) para as rotas.
- `models.py`: Onde definimos nossos esquemas do **Pydantic** e as tabelas do **SQLModel**. Repare que usamos as classes tanto para definir o formato do Banco de Dados quanto o formato dos JSON que recebemos/enviamos (evita duplicação de código!).
- `main.py`: O ponto de entrada da nossa API. Aqui nós criamos o aplicativo FastAPI e declaramos as **rotas** (nossos Endpoints para o CRUD).

### Passo 6: Rodando a Aplicação
Com o ambiente ativado e as dependências instaladas, rode o servidor usando o Uvicorn:

```bash
uvicorn main:app --reload
```
- `main`: Nome do arquivo (main.py).
- `app`: Nome da variável dentro do main.py que guarda a instância do FastAPI.
- `--reload`: Faz o servidor reiniciar sozinho sempre que você salvar um arquivo (ótimo para desenvolvimento!).

---

## 🚀 Testando a API (Documentação Automática)

A melhor parte do FastAPI é que ele cria uma documentação interativa para você automaticamente usando o Swagger UI.

1. Acesse pelo navegador: http://127.0.0.1:8000/docs
2. Você verá toda a lista do nosso CRUD.
3. Você pode clicar no botão **"Try it out"** em qualquer rota para fazer requisições sem precisar usar o Postman!

### Roteiro de Testes:
1. **POST `/items/`**: Tente criar um item novo passando Nome e Preço no body.
2. **GET `/items/`**: Liste todos os itens do banco.
3. **GET `/items/{item_id}`**: Coloque o ID do item recém-criado para consultá-lo.
4. **PATCH `/items/{item_id}`**: Atualize o preço ou o nome do item.
5. **DELETE `/items/{item_id}`**: Apague o item do banco e liste novamente para ver se sumiu.

Parabéns! Você acabou de criar e configurar uma API completa e profissional em Python usando FastAPI, Pydantic, SQLModel e PostgreSQL. 🎉
