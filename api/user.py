"""
Módulo que define as rotas (endpoints) da API para o recurso 'User'.
Aqui implementamos o CRUD completo (Create, Read, Update, Delete) de usuários.

A rota de criação (POST /users/) é aberta, seguindo o mesmo raciocínio de
"/register" em api/auth.py: não faria sentido exigir um token de autenticação
para criar o primeiro usuário do sistema. As demais rotas (listar, buscar,
atualizar e deletar) exigem um usuário autenticado, assim como o CRUD de Item.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from api.auth import get_current_user

# Importações dos nossos módulos
from database import SessionDep
from models import User, UserCreate, UserRead, UserUpdate
from security import get_password_hash

# Criação do router, que agrupa as rotas relacionadas a 'User'
user_router = APIRouter(prefix="/users", tags=["Usuários"])


@user_router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(*, session: SessionDep, user: UserCreate):
    """
    Rota para Criar um novo usuário no banco de dados (Operação C - Create).

    Parâmetros:
        session (SessionDep): A sessão do banco de dados injetada automaticamente pelo FastAPI.
        user (UserCreate): Os dados do usuário a ser criado, validados pelo Pydantic.

    Retorno:
        Retorna o usuário recém-criado (sem a senha em texto puro nem o hash), incluindo o 'id' gerado pelo banco.

    Lança:
        HTTPException(400): Se o username informado já estiver em uso.
    """
    # Verifica se o username já está em uso
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já registrado",
        )

    # Cria a entidade de banco, substituindo a senha pura pelo hash gerado em security.py
    db_user = User(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        hashed_password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@user_router.get("/", response_model=list[UserRead])
def read_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """
    Rota para Listar todos os usuários com suporte a paginação (Operação R - Read).

    Parâmetros:
        session (SessionDep): A sessão do banco de dados para realizar consultas.
        skip (int): Número de usuários a serem "pulados" antes de começar a retornar. Padrão é 0.
        limit (int): Número máximo de usuários a serem retornados. Padrão é 100.

    Retorno:
        Uma lista de usuários. O response_model=list[UserRead] garante que a senha (hash) nunca é exposta.
    """
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@user_router.get("/{user_id}", response_model=UserRead)
def read_user(
    *, session: SessionDep, user_id: int, current_user: User = Depends(get_current_user)
):
    """
    Rota para Buscar um usuário específico utilizando o seu ID (Operação R - Read).

    Parâmetros:
        session (SessionDep): A sessão do banco de dados.
        user_id (int): O ID do usuário procurado. Extraído da URL (path parameter).

    Retorno:
        Retorna o usuário se encontrado (sem o hash da senha).

    Lança:
        HTTPException(404): Se o usuário com o ID informado não existir no banco de dados.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return user


@user_router.put("/{user_id}", response_model=UserRead)
def update_user(
    *,
    session: SessionDep,
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Rota para Atualizar os dados de um usuário existente (Operação U - Update).

    Parâmetros:
        session (SessionDep): A sessão do banco de dados.
        user_id (int): O ID do usuário a ser atualizado (path parameter).
        user_update (UserUpdate): Os campos a serem alterados. Recebido no corpo da requisição (body).

    Retorno:
        Retorna o usuário com as informações atualizadas (sem o hash da senha).

    Lança:
        HTTPException(404): Se o usuário não for encontrado.
        HTTPException(400): Se o novo username já estiver em uso por outro usuário.
    """
    # Primeiro, verificamos se o usuário existe
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    # Convertemos o modelo de atualização em um dicionário.
    # exclude_unset=True garante que apenas os campos que o cliente efetivamente enviou serão atualizados.
    user_data = user_update.model_dump(exclude_unset=True)

    # Se um novo username foi enviado e é diferente do atual, verifica se já não está em uso
    new_username = user_data.get("username")
    if new_username is not None and new_username != db_user.username:
        statement = select(User).where(User.username == new_username)
        conflicting_user = session.exec(statement).first()
        if conflicting_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já registrado",
            )

    # Se uma nova senha foi enviada, gera o hash antes de salvar (nunca em texto puro)
    if "password" in user_data:
        plain_password = user_data.pop("password")
        db_user.hashed_password = get_password_hash(plain_password)

    # Atualizamos dinamicamente os demais atributos do usuário recuperado do banco
    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@user_router.delete("/{user_id}")
def delete_user(
    *, session: SessionDep, user_id: int, current_user: User = Depends(get_current_user)
):
    """
    Rota para Deletar um usuário do banco de dados (Operação D - Delete).

    Parâmetros:
        session (SessionDep): A sessão do banco de dados.
        user_id (int): O ID do usuário a ser removido (path parameter).

    Retorno:
        Um dicionário confirmando o sucesso da operação.

    Lança:
        HTTPException(404): Se o usuário não for encontrado.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    session.delete(user)
    session.commit()

    return {"ok": True, "message": "Usuário deletado com sucesso"}
