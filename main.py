"""
Arquivo principal (entry point) da aplicação FastAPI.
Aqui nós configuramos a instância principal do app, middlewares (como CORS) 
e incluímos as rotas (routers) definidas em outros arquivos.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.item import app_router
from database import lifespan

# Criação da instância principal da aplicação FastAPI
# O parâmetro 'lifespan' permite executar código antes da API começar a receber requisições (ex: criar tabelas).
app = FastAPI(
    title="API de Exemplo com FastAPI e SQLModel",
    description="Uma API simples com CRUD completo para uma turma de desenvolvimento web.",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração do Middleware de CORS (Cross-Origin Resource Sharing)
# Essencial para que o frontend (ex: React, Vue, HTML/JS puro) em outro domínio ou porta consiga fazer requisições para esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite requisições de qualquer origem (cuidado em produção!)
    allow_credentials=True, # Permite o envio de cookies e credenciais de autenticação
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos nas requisições
)

# Inclui as rotas (endpoints) definidas no router 'app_router' (arquivo api/item.py)
app.include_router(app_router)
