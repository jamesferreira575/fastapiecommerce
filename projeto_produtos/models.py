#pip install python-jose 
#pip install -U passlib 
#models.py
from sqlalchemy import Column,Integer,String,Float
from database import Base,engine,SessionLocal
#tabela produtos
class Produto(Base):
    __tablename__="produtos"
    id=Column(Integer,primary_key=True,index=True)
    nome=Column(String,nullable=False)
    preco=Column(Float,nullable=False)
    quantidade=Column(Integer, nullable=False)
    imagem=Column(String,nullable=True)

#criar dados no banco
'''
nome="Calça"
preco=119.99
quantidade=7
imagem="sem foto"
novo=Produto(nome=nome,preco=preco,quantidade=quantidade,
             imagem=imagem)
db=SessionLocal()
db.add(novo)
db.commit()
'''

##################################
#aula21
#models.py
class Usuario(Base):
    __tablename__="usuarios"
    id=Column(Integer,primary_key=True,index=True)
    nome=Column(String(50))
    email=Column(String(100),unique=True)
    senha=Column(String(200))
#criar banco de dados com a tabela e colunas
Base.metadata.create_all(bind=engine)