from pydantic import BaseModel, Field
from typing import Union, List

class ItemBase(BaseModel):
    nome: str = Field( default="Title", title="Nome do Item", max_length=50, example="Arroz")
    descricao: Union[str, None] = Field(default=None, title="Detalhes adicionais do produto", max_length=300, example="Marca Tio João, saco com 5kg." )
    preco: float = Field(default=0.0,  title= "Preço do produto", ge=0, description="O preço do produto tem que ser positivo", example=12.5)
    
class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    quantidade: int = Field(default= 0,  title= "Quantidade do produto", ge=0, description="A quantidade do produto tem que ser positiva", example=5)

    class Config:
        orm_mode = True

class MoveBase(BaseModel):
    quantidade: int = Field(default= 0,  title= "Quantidade do produto a ser alterada", example=5)
    item_id: int = Field(title="O id do item a ser movimentado", example=1)
    descricao: str = Field(title="Uma descrição da movimentação feita", max_length=100, example="5 sacos de arroz (id = 1) movimentados")

class MoveCreate(MoveBase):
    pass

class Move(MoveBase):
    id: int

    class Config:
        orm_mode = True