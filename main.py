#imports
import logging
from fastapi import FastAPI, Path, Query
from enum import Enum
from typing import Union, List
from pydantic import BaseModel
logger = logging.getLogger("uvicorn")
# Item Class

class Item(BaseModel):
    nome: str
    descricao: Union[str, None] = None
    preco: float
    quantidade: int = None
    esgotado: bool

itens= {1: {"nome":"produto 1", "descricao": "descricao 1", "preco": 20.00, "quantidade": 1, "esgotado": True},
2: {"nome":"produto 2", "descricao": "descricao 2", "preco": 10.00, "quantidade": 2, "esgotado": True}
}

    
app = FastAPI()

#cria um item

@app.post("/itens/create")
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
    return itens[item_id]
