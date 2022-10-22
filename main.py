#imports
from fastapi import FastAPI, Path, Query
from enum import Enum
from typing import Union
from pydantic import BaseModel

# Item Class

class Item(BaseModel):
    nome: str
    descricao: Union[str, None] = None
    preco: float
    quantidade: int = None
    esgotado: bool
    
app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    if (item.quantidade == 0) | (item.quantidade == None):
        item.esgotado = True
    else:
        item.esgotado = False
        
    return item