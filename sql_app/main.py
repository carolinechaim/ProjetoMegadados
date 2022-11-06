#python -m uvicorn main:app --reload

#imports
import logging
from fastapi import FastAPI, HTTPException, Request, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

logger = logging.getLogger("uvicorn")

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#cria um item
@app.post("/itens/create", status_code=201, response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db :Session = Depends(get_db) ):
    """
    Cria um novo item no estoque com:

    - **Nome**: todos os itens precisam de um nome
    - **Descrição**: Um espaço para detalhes extra sobre o produto
    - **Preço**: obrigatório
    - **Quantidade**: Quanto tem do produto no estoque

    Retorna o item criado como:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
    }
    """
    return crud.create_item(db=db, item=item)


#Pega a lista de itens
@app.get("/itens/", status_code=200, response_model = list[schemas.Item])
async def read_all_items(db :Session = Depends(get_db)):
    """
   Retorna todos os itens presentes no estoque com essa configuração:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
    },
    {
        "nome": "Ovos",
        "descricao": "Estilo caipira, cartela com 12.",
        "preco": 10,
        "quantidade": 7,
    }
    """
    itens = crud.read_all_items(db=db)
    return itens

#Pega item com id especifico
@app.get("/itens/{item_id}", status_code=200, response_model=schemas.Item)
async def read_item(item_id: int = Query(title="Id do item que deseja procurar", ge=0), db :Session = Depends(get_db)):
    """
   Retorna o item selecionado do estoque com essa configuração:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
    }
    """
    db_item = crud.read_item(db = db, id = item_id)
    if db_item is None:
        raise HTTPException(status_code=422, detail="Item não encontrado")
    return db_item

#Update apenas um campo
@app.patch("/itens/patch/{item_id}", response_model=schemas.Item)
async def update_partial_item(item: schemas.Item,
item_id: int = Query(title="Id do item que deseja procurar", ge=0),
item_nome: Optional[str] = Query(None, title="Nome do item que quer trocar (Opcional)"),
item_descricao: Optional[str] = Query(None, title="Descrição do item que quer trocar (Opcional)"),
item_preco: Optional[float] = Query(None, title="Preço do item que quer trocar (Opcional)"),
db: Session = Depends(get_db)):
    """
    Atualiza parcialmente as seguintes informações de um item do estoque:

    - **Nome**: todos os itens precisam de um nome
    - **Descrição**: Um espaço para detalhes extra sobre o produto
    - **Preço**: obrigatório

    Retorna o item atualizado como:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 15
    }
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=400, detail="Item não encontrado")
    return crud.update_partial_item(db, item, item_id, item_nome, item_descricao, item_preco)

#Update tudo
@app.put("/items/{item_id}", response_model=schemas.Item)
async def update_item(move: schemas.MoveCreate, db: Session = Depends(get_db)):
    """
    Atualiza completamente as seguintes informações de um item do estoque, reescrevendo-o:

    - **Nome**: todos os itens precisam de um nome
    - **Descrição**: Um espaço para detalhes extra sobre o produto
    - **Preço**: obrigatório
    - **Quantidade**: Quanto tem do produto no estoque

    Retorna o item atualizado como:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 15,
        "quantidade": 5,
    }
    """
    db_item = db.query(models.Item).filter(models.Item.id == move.item_id).first()
    if db_item is None:
        raise HTTPException(status_code=400, detail="Item não encontrado")
    return crud.update_item_move(db, move)

#Deleta um item
@app.delete("/itens/{item_id}")
async def delete_item(item_id: int = Query(title="Id do item que deseja deletar", ge=0), db: Session = Depends(get_db)):
    """
   Retorna o item deletado do estoque com essa configuração:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
    }
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=400, detail="Item não encontrado")
    return crud.delete_item(db, item_id)

#cria uma movimentacao
@app.post("/movimento/create", status_code=201, response_model=schemas.Move)
async def create_move(move: schemas.Move, db :Session = Depends(get_db) ):
    """
    Cria um novo item no estoque com:

    - **Quantidade**: Quanto será movimentado no estoque
    - **Item_id**: Id do produto sofrendo a movimentação
    - **Descrição**: Um espaço para detalhes extra sobre a movimentação

    Retorna o item criado como:

    {
        "quantidade": 3,
        "item_id": 1,
        "descricao": "Marca Tio João, saco com 5kg, adicionado 3 sacos"
    }
    """
    db_move = models.Move(quantidade=move.quantidade, item_id=move.item_id, descricao=move.descricao)
    if db_move is None:
        raise HTTPException(status_code=400, detail="Erro, dados não válidos")
    
    return crud.create_move(db=db, move=move)

#Pega a lista de movimentações
@app.get("/movimento/", status_code=200, response_model = list[schemas.Move])
async def read_all_moves(db :Session = Depends(get_db)):
    """
   Retorna todos as movimentações feitas no estoque com essa configuração:

    {
        "quantidade": 3,
        "item_id": 1,
        "descricao": "Marca Tio João, saco com 5kg, adicionado 3 sacos"
    },
    {
        "quantidade": 1,
        "item_id": 1,
        "descricao": "Marca Tio João, saco com 5kg, adicionado 1 saco"
    }
    """

    return crud.read_all_moves(db=db)

#Pega movimentação com id especifico
@app.get("/movimento/{id}", status_code=200, response_model=schemas.Move)
async def read_item(id: int = Query(title="Id da movimentação que deseja procurar", ge=0), db :Session = Depends(get_db)):
    """
   Retorna a movimentação selecionado do estoque com essa configuração:

    {
       "quantidade": 3,
        "item_id": 1,
        "descricao": "Marca Tio João, saco com 5kg, adicionado 3 sacos"
    }
    """
    db_move = crud.read_move(db = db, move_id = id)
    if db_move is None:
        raise HTTPException(status_code=422, detail="Movimentação não encontrada")
    return db_move

#Deleta uma movimentação
@app.delete("/movimento/{id}")
async def delete_item(id: int = Query(title="Id da movimentação que deseja deletar", ge=0), db: Session = Depends(get_db)):
    """
   Retorna a movimentação deletada do estoque com essa configuração:

    {
        "quantidade": 3,
        "item_id": 1,
        "descricao": "Marca Tio João, saco com 5kg, adicionado 3 sacos"
    }
    """
    db_move = db.query(models.Move).filter(models.Move.id == id).first()
    if db_move is None:
        raise HTTPException(status_code=400, detail="Movimentação não encontrada")
    return crud.delete_move(db, id)