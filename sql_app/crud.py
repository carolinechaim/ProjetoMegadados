from sqlalchemy.orm import Session
from . import models, schemas

#Pega item com id especifico
def read_item(db: Session, id: int):
    return db.query(models.Item).filter(models.Item.id == id).first()

#Pega a lista de itens
def read_all_items(db: Session):
    return db.query(models.Item).all()

#Cria um item
def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

#Deleta um item
def delete_item(db: Session, id: int):
    db_item = db.query(models.Item).filter(models.Item.id == id).first()
    db.delete(db_item)
    db.commit()
    db.refresh()
    return {'Deleted': db_item}

#Atualiza parcialmente as infos de um item
def update_partial_item(db: Session, item: schemas.Item, id: int, nome: str, descricao: str, preco: float):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if nome != None:
        db_item.nome = nome
    if descricao != None:
        db_item.descricao = descricao
    if preco != None:
        db_item.preco = preco
    db.commit()
    db.refresh(db_item)
    return db_item

#Atualiza a quantidade de um item baseado numa movimentacao
def update_item_move(db: Session, move: schemas.MoveCreate):
    db_item = db.query(models.Item).filter(models.Item.id == move.item_id).first()
    db_item.quantidade = db_item.quantidade + move.quantidade
    if db_item.quantidade <= 0:
        db_item.quantidade = 0
        db_item.esgotado = False
    db.commit()
    db.refresh(db_item)
    return db_item

#Cria uma movimentação
def create_move(db: Session, move: schemas.MoveCreate):
    db_move = models.Move(**move.dict())
    db_item = db.query(models.Item).filter(models.Item.id == db_move.item_id).first()
    db_item.quantidade = db_item.quantidade + move.quantidade
    if db_item.quantidade <= 0:
        db_item.quantidade = 0
        db_item.esgotado = False
    db.add(db_move)
    db.commit()
    db.refresh(db_move)
    return db_move

#Pega uma movimentação específica
def read_move(db: Session, move_id: int):
    return db.query(models.Move).filter(models.Move.id == move_id).first()

#Pega todas as movimentações
def read_all_moves(db: Session):
    return db.query(models.Move).all()

#Deleta uma movimentação
def delete_move(db: Session, move_id: int):
    db_move = db.query(models.Move).filter(models.Move.id == move_id).first()
    db_item = db.query(models.Item).filter(models.Item.id == db_move.item_id).first()
    db_item.quantidade -= db_move.quantidade
    db.delete(db_move)
    db.commit()

    return db_move