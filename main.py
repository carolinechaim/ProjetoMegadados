#python -m uvicorn main:app --reload

#imports
from doctest import Example
import logging
from fastapi import FastAPI, HTTPException, Request, Path, Body
from typing import Union, List
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
logger = logging.getLogger("uvicorn")

# Item Class
class Item(BaseModel):
    nome: str = Field( default="Title", title="Nome do Item", max_length=50, example="Arroz")
    descricao: Union[str, None] = Field( default=None, title="Detalhes adicionais do produto", max_length=300, example="Marca Tio João, saco com 5kg." )
    preco: float = Field(default= 0.0,  title= "Preço do produto", ge=0, description="O preço do produto tem que ser positivo", example=12.5)
    quantidade: int = Field(default= 0,  title= "Quantidade do produto", ge=0, description="A quantidade do produto tem que ser positiva", example=5)
    esgotado: bool = Field(default=False, title="Se o produto está esgotado")


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


itens= {1: {"nome":"produto 1", "descricao": "descricao 1", "preco": 20.00, "quantidade": 1, "esgotado": True},
2: {"nome":"produto 2", "descricao": "descricao 2", "preco": 10.00, "quantidade": 2, "esgotado": True}
}

app = FastAPI()

#cria um item
@app.post("/itens/create", status_code=201, response_model=Item)
async def create_item(item: Item = Body(
        examples={
            "Correto": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um item **normal** criado com sucesso.",
                "value": {
                    "nome": "Arroz",
                    "descricao": "Marca Tio João, saco com 5kg.",
                    "preco": 12.5,
                    "quantidade": 5,
                    "esgotado": False
                },
            },
            "Convertido": {
                "summary": "Um exemplo com números convertidos",
                "description": "A FastAPI converte `strings` para `números` automaticamente",
                "value": {
                    "nome": "Arroz",
                    "descricao": "Marca Tio João, saco com 5kg.",
                    "preco": 12.5,
                    "quantidade": "5",
                    "esgotado": False
                },
            },
            "Inválido": {
                "summary": "Um exemplo com dados inválidos",
                "description": "Dados inválidos são rejeitados com erro",
                "value": {
                    "nome": "Arroz",
                    "descricao": "Marca Tio João, saco com 5kg.",
                    "preco": 12.5,
                    "quantidade": "cinco",
                    "esgotado": False
                },
            },
        },
)):
    """
    Cria um novo item no estoque com:

    - **Nome**: todos os itens precisam de um nome
    - **Descrição**: Um espaço para detalhes extra sobre o produto
    - **Preço**: obrigatório
    - **Quantidade**: Quanto tem do produto no estoque
    - **Esgotado**: Se o produto está esgotado

    Retorna o item criado como:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
        "esgotado": false
    }
    """

    if (item.quantidade == 0) | (item.quantidade == None):
        item.esgotado = True
    else:
        item.esgotado = False

    item = item.dict()
    itens.append(item)

    return item


#Pega a lista de itens
@app.get("/itens/", status_code=200, response_model = list[Item])
async def read_all_items():
    """
   Retorna todos os itens presentes no estoque com essa configuração:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
        "esgotado": false
    },
    {
        "nome": "Ovos",
        "descricao": "Estilo caipira, cartela com 12.",
        "preco": 10,
        "quantidade": 7,
        "esgotado": false
    }
    """
    return itens

#Pega item com id especifico
@app.get("/itens/{item_id}", status_code=200, response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: int = Path(title="Id do item que deseja procurar", ge=0)):
    """
   Retorna o item selecionado do estoque com essa configuração:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
        "esgotado": false
    }
    """
    if item_id not in itens:
        raise HTTPException(status_code=422, detail="Item não encontrado")
    return itens[item_id]

#Update apenas um campo
@app.patch("/itens/{item_id}", response_model=Item)
async def update_partial_item(item: Item = Body(
        examples={
            "Nome": {
                "summary": "Um exemplo atualizando apenas o nome",
                "value": {
                    "Nome": "Panqueca"
                },
            },
            "Descrição": {
                "summary": "Um exemplo atualizando apenas a descrição",
                "value": {
                    "Descrição": "Marca Tio João, saco com 2kg."
                },
            },
            "Preço": {
                "summary": "Um exemplo atualizando apenas o preço",
                "value": {
                    "Preço": 15,
                },
            },
            "Quantidade": {
                "summary": "Um exemplo atualizando apenas a quantidade",
                "value": {
                    "Quantidade": 10,
                },
            },
        },
), item_id: int = Path(title="Id do item que deseja procurar", ge=0)):
    """
    Atualiza parcialmente as seguintes informações de um item do estoque:

    - **Nome**: todos os itens precisam de um nome
    - **Descrição**: Um espaço para detalhes extra sobre o produto
    - **Preço**: obrigatório
    - **Quantidade**: Quanto tem do produto no estoque
    - **Esgotado**: Se o produto está esgotado

    Retorna o item atualizado como:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 15,
        "quantidade": 5,
        "esgotado": false
    }
    """
    if item_id not in itens:
            raise HTTPException(status_code=422, detail="Item não encontrado")
    
    if (item.quantidade == 0):
        item.esgotado = True
    else:
        item.esgotado = False

    stored_item_data = itens[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    itens[item_id] = jsonable_encoder(updated_item)
    return updated_item

#Update tudo
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item: Item = Body(
        examples={
            "Correto": {
                    "summary": "Um exemplo normal de sucesso",
                    "description": "Um item **normal** criado com sucesso.",
                    "value": {
                        "nome": "Arroz",
                        "descricao": "Marca Tio João, saco com 5kg.",
                        "preco": 12.5,
                        "quantidade": 9,
                        "esgotado": False
                    },
                },
                "Convertido": {
                    "summary": "Um exemplo com números convertidos",
                    "description": "A FastAPI converte `strings` para `números` automaticamente",
                    "value": {
                        "nome": "Arroz",
                        "descricao": "Marca Tio João, saco com 5kg.",
                        "preco": 12.5,
                        "quantidade": "9",
                        "esgotado": False
                    },
                },
                "Inválido": {
                    "summary": "Um exemplo com dados inválidos",
                    "description": "Dados inválidos são rejeitados com erro",
                    "value": {
                        "nome": "Arroz",
                        "descricao": "Marca Tio João, saco com 5kg.",
                        "preco": 12.5,
                        "quantidade": "nove",
                        "esgotado": False
                    },
                },
        },
), item_id: int = Path(title="Id do item que deseja atualizar", ge=0)):
    """
    Atualiza completamente as seguintes informações de um item do estoque, reescrevendo-o:

    - **Nome**: todos os itens precisam de um nome
    - **Descrição**: Um espaço para detalhes extra sobre o produto
    - **Preço**: obrigatório
    - **Quantidade**: Quanto tem do produto no estoque
    - **Esgotado**: Se o produto está esgotado

    Retorna o item atualizado como:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 15,
        "quantidade": 5,
        "esgotado": false
    }
    """
    if item_id not in itens:
            raise HTTPException(status_code=422, detail="Item não encontrado")
    
    if (item.quantidade == 0):
        item.esgotado = True
    else:
        item.esgotado = False

    update_item_encoded = jsonable_encoder(item)
    itens[item_id] = update_item_encoded
    return update_item_encoded

#Delete
@app.delete("/itens/{item_id}")
async def delete_item(item_id: int = Path(title="Id do item que deseja deletar", ge=0)):
    """
   Retorna o item deletado do estoque com essa configuração:

    {
        "nome": "Arroz",
        "descricao": "Marca Tio João, saco com 5kg.",
        "preco": 12.5,
        "quantidade": 5,
        "esgotado": false
    }
    """
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