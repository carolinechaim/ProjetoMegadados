#python -m uvicorn main:app --reload

#imports
from doctest import Example
import logging
from fastapi import FastAPI,  HTTPException, Request
from enum import Enum
from typing import Union, List
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
logger = logging.getLogger("uvicorn")

# Item Class
class Item(BaseModel):
    nome: str = Field( default=None, title="Nome do Item", max_length=50, example="Arroz")
    descricao: Union[str, None] = Field( default=None, title="Detalhes adicionais do produto", max_length=300, example="Marca Tio João, saco com 5kg." )
    preco: float = Field(default= 0.0,  title= "Preço do produto", ge=0, description="O preço do produto tem que ser positivo", example=12.5)
    quantidade: int = Field(default= 0,  title= "quantidade do produto", ge=0, description="A quantidade do produto tem que ser positiva", example=5)
    esgotado: bool


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

itens= {1: {"nome":"produto 1", "descricao": "descricao 1", "preco": 20.00, "quantidade": 1, "esgotado": True},
2: {"nome":"produto 2", "descricao": "descricao 2", "preco": 10.00, "quantidade": 2, "esgotado": True}
}

    
app = FastAPI()

#cria um item
@app.post("/itens/create", status_code=201, response_model=Item)
async def create_item(item: Item):

    if (item.quantidade == 0) | (item.quantidade == None):
        item.esgotado = True
    else:
        item.esgotado = False

    return item


#Pega a lista de itens
@app.get("/itens/")
async def read_item():
    return itens

#Pega item com id especifico
@app.get("/itens/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: int):
    if item_id not in itens:
        raise HTTPException(status_code=422, detail="Item não encontrado")
    return itens[item_id]

#Update apenas um campo
@app.patch("/itens/{item_id}", response_model=Item)
async def update_partial_item(item_id: int, item: Item):
    if item_id not in itens:
            raise HTTPException(status_code=422, detail="Item não encontrado")

    stored_item_data = itens[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    itens[item_id] = jsonable_encoder(updated_item)
    return updated_item

#Update tudo
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id not in itens:
            raise HTTPException(status_code=422, detail="Item não encontrado")
            
    update_item_encoded = jsonable_encoder(item)
    itens[item_id] = update_item_encoded
    return update_item_encoded

#Delete
@app.delete("/itens/{item_id}")
async def delete_item(item_id: int):
    if item_id not in itens:
            raise HTTPException(status_code=422, detail="Item não encontrado")

    deleted_item = itens[item_id]
    itens.pop(item_id)
    return {'Deleted': deleted_item}

#Error 404

@app.exception_handler(404)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=404,
        content={"mensagem": f"Pagina não encontrada"},
    )