"""
Módulo de rotas de Autenticação.
Aqui definimos:
1. A rota para registrar (criar) um novo usuário.
2. A rota para fazer login e obter o token JWT.
3. A dependência (função) para extrair e validar o usuário a partir do token nas requisições.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import select

from database import SessionDep
from models import Token, TokenData, User, UserCreate, UserLogin, UserRead
from security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)

# Criamos um router específico para autenticação
auth_router = APIRouter(tags=["Autenticação"])

# Usando HTTPBearer para receber o token via cabeçalho (sem formulários complexos do OAuth2)
security_bearer = HTTPBearer()


@auth_router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, session: SessionDep):
    """
    Rota para que os alunos possam criar seus próprios usuários.
    Recebe username e password. A senha é imediatamente "hasheada" antes de salvar no banco.
    """
    # Verifica se o usuário já existe
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já registrado",
        )

    # Cria a entidade de banco, substituindo a senha pura pelo hash
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@auth_router.post("/login", response_model=Token)
def login_for_access_token(session: SessionDep, user_login: UserLogin):
    """
    Rota de Login Simplificada.
    Recebe as credenciais em formato JSON (username e password) e retorna o Token JWT.
    """
    # 1. Busca o usuário no banco
    statement = select(User).where(User.username == user_login.username)
    user = session.exec(statement).first()

    # 2. Verifica se o usuário existe e se a senha bate com o hash
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Gera o Token JWT com o 'username' no payload (o subject 'sub' é o padrão JWT)
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),  # noqa: B008
):
    """
    Dependência central de segurança.
    Essa função é injetada nas rotas que exigem login.
    Ela pega o token do cabeçalho da requisição, decodifica, valida e retorna o usuário logado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Pega a string do token
        token = credentials.credentials
        # Decodifica o token usando a chave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        # Se o token for inválido, expirado ou forjado, vai cair aqui
        raise credentials_exception

    # Busca o usuário no banco de dados
    user = session.exec(
        select(User).where(User.username == token_data.username)
    ).first()
    if user is None:
        raise credentials_exception

    return user
