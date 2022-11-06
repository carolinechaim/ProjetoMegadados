from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base

class Move(Base):
    __tablename__ = "move"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("itens.id"))
    quantidade = Column(Integer)
    descricao = Column(String(100), index=True)
    estoque = relationship("Item", back_populates="move")


class Item(Base):
    __tablename__ = "itens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(300), index=True)
    descricao = Column(String(100), index=True)
    preco = Column(Float, index=True)
    quantidade = Column(Integer, primary_key = True, index=True, default=0)
    esgotado = Column(Boolean, default=True)

    move = relationship("Move", back_populates="estoque", cascade="all, delete")