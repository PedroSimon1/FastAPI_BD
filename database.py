"""
Módulo de configuração do banco de dados utilizando SQLModel e SQLAlchemy.
Lida com a conexão, criação das tabelas e injeção de dependência da sessão.
"""
import os
from contextlib import asynccontextmanager
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine

# Carrega as variáveis de ambiente definidas no arquivo .env (como DATABASE_URL)
load_dotenv()

# Obtém a URL de conexão com o banco de dados armazenada nas variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o "engine" (motor) de conexão com o banco de dados.
# O parâmetro echo=True faz com que todos os comandos SQL gerados sejam impressos no terminal (ótimo para aprendizado e debug).
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """
    Função responsável por criar todas as tabelas no banco de dados.
    Ela lê os modelos (classes que herdam de SQLModel) e gera as tabelas correspondentes.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Função geradora para injeção de dependência da sessão do banco de dados.
    A cada nova requisição, esta função abre uma nova sessão (conexão) e a retorna (yield).
    O FastAPI garante que a sessão será fechada corretamente ao final da requisição, mesmo se ocorrer um erro.
    """
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de contexto para o ciclo de vida (lifespan) da aplicação FastAPI.
    
    Parâmetros:
        app (FastAPI): A instância da aplicação FastAPI.
        
    Comportamento:
        Tudo que está antes do 'yield' é executado quando a aplicação é iniciada (ex: criar tabelas).
        O 'yield' pausa a execução e permite que a aplicação rode e receba requisições.
        Tudo que estiver após o 'yield' (não há nada neste caso) executará quando a aplicação for desligada.
    """
    print("Criando tabelas no banco de dados...")
    create_db_and_tables()
    yield


# Atalho de tipo para facilitar a injeção de dependência nas rotas.
# Em vez de escrever `session: Session = Depends(get_session)` nas rotas, usamos `session: SessionDep`.
SessionDep = Annotated[Session, Depends(get_session)]
