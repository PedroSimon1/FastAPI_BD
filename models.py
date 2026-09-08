"""
Módulo de definição dos modelos de dados.
Utilizamos o SQLModel, que une o melhor do Pydantic (validação de dados) com o SQLAlchemy (interação com o banco de dados).
"""
from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    """
    Classe base contendo os atributos comuns a todos os modelos de 'Item'.
    Serve como fundação para evitar repetição de código.
    O Pydantic usará isso para validar os dados de entrada e saída.
    """
    # Field(index=True) cria um índice no banco de dados para agilizar buscas por nome.
    name: str = Field(index=True)
    # Atributo opcional (pode ser null). O default=None indica que não é obrigatório.
    description: str | None = Field(default=None)
    price: float
    is_active: bool = Field(default=True)


class Item(ItemBase, table=True):
    """
    Modelo que representa a tabela 'item' no banco de dados (por causa do table=True).
    Herda os campos de ItemBase e adiciona o campo 'id'.
    """
    # primary_key=True define esta coluna como chave primária (identificador único).
    # Como é int | None e default=None, o banco de dados gerará o ID automaticamente (auto-incremento).
    id: int | None = Field(default=None, primary_key=True)


class ItemCreate(ItemBase):
    """
    Modelo (Schema) utilizado para validar os dados recebidos ao CRIAR um item (POST).
    Herda de ItemBase. Não precisa de ID, pois o banco de dados é quem o criará.
    """
    pass


class ItemUpdate(SQLModel):
    """
    Modelo (Schema) utilizado para validar os dados recebidos ao ATUALIZAR um item (PATCH).
    Todos os campos são opcionais, pois o usuário pode querer alterar apenas o 'name' ou apenas o 'price'.
    """
    name: str | None = None
    description: str | None = None
    price: float | None = None
    is_active: bool | None = None


# ==========================================
# Modelos de Autenticação e Usuários
# ==========================================

class UserBase(SQLModel):
    """
    Classe base para Usuários. Contém os dados em comum.
    """
    username: str = Field(index=True, unique=True)
    email: str | None = Field(default=None)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    """
    Schema utilizado para criar um usuário. 
    """
    password: str


class UserLogin(SQLModel):
    """
    Schema simplificado para receber apenas username e password no login (via JSON).
    """
    username: str
    password: str


class UserRead(UserBase):
    id: int


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None
