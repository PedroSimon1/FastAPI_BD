"""
Módulo de Segurança.
Responsável por:
1. Criar hash das senhas para salvá-las de forma segura no banco.
2. Verificar se uma senha digitada bate com o hash salvo.
3. Gerar tokens JWT (JSON Web Tokens) para autenticação.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from jose import jwt

load_dotenv()

# ==========================================
# Configurações do JWT
# ==========================================
# SECRET_KEY: É como a "senha mestre" da sua aplicação.
# Usada para assinar digitalmente os tokens e garantir que não foram forjados.
# Em produção, ISSO DEVE FICAR EM VARIÁVEIS DE AMBIENTE (.env) e NUNCA no código!
# (Lendo agora a partir do arquivo .env)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-inseguro-para-desenvolvimento")

# Algoritmo de criptografia usado para assinar o token
ALGORITHM = "HS256"

# Tempo de vida do token (ex: o usuário será deslogado após 30 minutos se não renovar)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto puro informada bate com o hash armazenado no banco.
    """
    # bcrypt exige que as strings sejam bytes
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """
    Recebe uma senha em texto puro e retorna a versão hasheada para ser salva no banco.
    """
    # Gera um salt e faz o hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    # Retorna como string (decodificada) para salvar no banco de dados
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Cria um Token JWT.

    Parâmetros:
        data (dict): Os dados que queremos "embutir" dentro do token (o payload).
        expires_delta (timedelta): Opcional. Tempo extra de expiração personalizado.

    Retorno:
        str: A string do JWT codificada.
    """
    # Fazemos uma cópia para não alterar o dicionário original
    to_encode = data.copy()

    # Define o momento da expiração
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Adiciona a "data de validade" (exp) no dicionário
    to_encode.update({"exp": expire})

    # Gera e retorna o JWT codificado com nossa chave secreta e algoritmo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
