"""
Módulo que define as rotas (endpoints) da API para o recurso 'Item'.
Aqui implementamos o CRUD completo (Create, Read, Update, Delete).
"""
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

# Importações dos nossos módulos
from database import SessionDep
from models import Item, ItemCreate, ItemUpdate

# Criação do router, que é como se fosse um "mini-aplicativo" que agrupa rotas relacionadas
app_router = APIRouter()


@app_router.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(*, session: SessionDep, item: ItemCreate):
    """
    Rota para Criar um novo Item no banco de dados (Operação C - Create).
    
    Parâmetros:
        session (SessionDep): A sessão do banco de dados injetada automaticamente pelo FastAPI. Usada para interagir com o banco.
        item (ItemCreate): Os dados do item a ser criado, validados pelo Pydantic com base no modelo ItemCreate. Recebido no body (corpo) da requisição.
    
    Retorno:
        Retorna o item recém-criado, incluindo o 'id' que foi gerado pelo banco de dados.
    """
    # Cria a entidade de banco a partir dos dados recebidos
    # Para Pydantic V2 e SQLModel recente, usamos model_validate() para converter o schema de criação para o modelo do banco
    db_item = Item.model_validate(item)

    # Adiciona o item à sessão (ainda não salvo de fato)
    session.add(db_item)
    # Comita a transação, salvando o item permanentemente no banco
    session.commit()
    # Atualiza o objeto db_item com os dados do banco (ex: preenchendo o 'id' gerado)
    session.refresh(db_item)
    
    return db_item


@app_router.get("/items/", response_model=list[Item])
def read_items(session: SessionDep, skip: int = 0, limit: int = 100):
    """
    Rota para Listar todos os Itens com suporte a paginação (Operação R - Read).
    
    Parâmetros:
        session (SessionDep): A sessão do banco de dados para realizar consultas.
        skip (int): Número de itens a serem "pulados" antes de começar a retornar (útil para paginação). Padrão é 0.
        limit (int): Número máximo de itens a serem retornados. Padrão é 100.
    
    Retorno:
        Uma lista de Itens. O response_model=list[Item] garante que o retorno será serializado corretamente.
    """
    # Cria uma consulta (select) na tabela Item, aplica o offset (skip) e o limite (limit), e busca todos (all)
    items = session.exec(select(Item).offset(skip).limit(limit)).all()
    return items


@app_router.get("/items/{item_id}", response_model=Item)
def read_item(*, session: SessionDep, item_id: int):
    """
    Rota para Buscar um Item específico utilizando o seu ID (Operação R - Read).
    
    Parâmetros:
        session (SessionDep): A sessão do banco de dados.
        item_id (int): O ID do item procurado. Extraído da URL (path parameter).
    
    Retorno:
        Retorna o item se encontrado.
    
    Lança:
        HTTPException(404): Se o item com o ID informado não existir no banco de dados.
    """
    # Busca um item pelo seu ID (chave primária)
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado"
        )
    return item


@app_router.patch("/items/{item_id}", response_model=Item)
def update_item(*, session: SessionDep, item_id: int, item_update: ItemUpdate):
    """
    Rota para Atualizar dados parciais de um Item existente (Operação U - Update).
    Usamos o método PATCH pois estamos modificando apenas alguns campos (diferente do PUT que geralmente substitui tudo).
    
    Parâmetros:
        session (SessionDep): A sessão do banco de dados.
        item_id (int): O ID do item a ser atualizado (path parameter).
        item_update (ItemUpdate): Os campos a serem alterados. Recebido no corpo da requisição (body).
    
    Retorno:
        Retorna o item com as informações atualizadas.
        
    Lança:
        HTTPException(404): Se o item não for encontrado.
    """
    # Primeiro, verificamos se o item existe
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado"
        )

    # Convertemos o modelo de atualização em um dicionário. 
    # exclude_unset=True garante que apenas os campos que o usuário efetivamente enviou na requisição serão atualizados.
    item_data = item_update.model_dump(exclude_unset=True)
    
    # Atualizamos dinamicamente os atributos do item recuperado do banco
    for key, value in item_data.items():
        setattr(db_item, key, value)

    # Salva as alterações
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    
    return db_item


@app_router.delete("/items/{item_id}")
def delete_item(*, session: SessionDep, item_id: int):
    """
    Rota para Deletar um Item do banco de dados (Operação D - Delete).
    
    Parâmetros:
        session (SessionDep): A sessão do banco de dados.
        item_id (int): O ID do item a ser removido (path parameter).
        
    Retorno:
        Um dicionário confirmando o sucesso da operação.
        
    Lança:
        HTTPException(404): Se o item não for encontrado.
    """
    # Primeiro, buscamos o item para ter certeza que ele existe
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado"
        )

    # Remove o item da sessão e comita para aplicar no banco
    session.delete(item)
    session.commit()
    
    return {"ok": True, "message": "Item deletado com sucesso"}
