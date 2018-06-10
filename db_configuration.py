import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    picture = Column(String(255))

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)
    
class CategoryItem(Base):
    __tablename__ = 'category_item'
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(255), nullable=False)
    details = Column("details", String(255))
    category_id = Column("category_id", Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

