import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class CategoryItem(Base):
    __tablename__ = 'category_item'
    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    items = relationship(CategoryItem)
