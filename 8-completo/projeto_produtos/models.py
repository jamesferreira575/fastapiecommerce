#models.py
from sqlalchemy import Column,Integer,String,Float,Boolean,ForeignKey#novo import
from database import Base,engine,SessionLocal
#novo import para sql puro no orm sqlalchemy
from sqlalchemy import text
#import criar user adm
from auth import*
##############################
#novo import
from sqlalchemy.orm import relationship

##############################
#tabela produtos
class Produto(Base):
    __tablename__="produtos"
    id=Column(Integer,primary_key=True,index=True)
    nome=Column(String,nullable=False)
    preco=Column(Float,nullable=False)
    quantidade=Column(Integer, nullable=False)
    imagem=Column(String,nullable=True)
#criar banco de dados com a tabela e colunas
#Base.metadata.create_all(bind=engine)
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
#################add login
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50))
    email = Column(String(100), unique=True)
    senha = Column(String(200))  # senha será armazenada com hash
    is_admin = Column(Boolean, default=False)#novo campo
    #########################
    #novo
    pedidos=relationship("Pedido",back_populates="usuario")

###########testado ok estar na pasta local

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    total = Column(Float, default=0.0)

    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco_unitario = Column(Float)

    pedido = relationship("Pedido", back_populates="itens")
Base.metadata.create_all(bind=engine)
'''
with engine.connect() as conexao:
    conexao.execute(text(
"ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
'''
#db = SessionLocal()
#admin = Usuario(nome="Admin2", email="admin2@loja.com", 
# senha=gerar_hash_senha("123456"), is_admin=True)
#db.add(admin)
#db.commit()
