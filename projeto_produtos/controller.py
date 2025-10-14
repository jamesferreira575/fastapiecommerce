#controller.py
from fastapi import APIRouter,Request,Form,UploadFile,File,Depends
# APIRouter=rota api para o front-end,
# Request=Requesição HTTP,
# Form=Formulário para criar e editar,
# UploadFile=Upload da foto,
# File=Função para gravar o caminho da imagem,
# Depends=dependência do banco de dados sqlite para o fastapi
from fastapi.responses import HTMLResponse,RedirectResponse
# HTMLResponse=resposta do html GET,POST,PUT,DELETE,
# RedirectResponse=redirecionar a página ao receber o método'GET'
from fastapi.templating import Jinja2Templates
#Jinja2Templates=responsável por renderizar o front-end,
#html,css,javascript
import os,shutil
#os=função de sistema, pegar caminhos de pasta 'imagem'
#shutil=salvar ou pegar o caminho do diretório 'caminho/imagem'
from sqlalchemy.orm import Session
#Session=modelagem dos daos ORM 'id,nome,preco'
from database import get_db,SessionLocal#novo import
#get_db=coletar o banco 'produtos.db' para a API
from models import Produto,Usuario#import novo
from auth import gerar_hash_senha,verificar_hash_senha#import novo
#Produto manipular o models Produtos
router=APIRouter()#rotas da api
templates=Jinja2Templates(directory="templates")#pasta front-end
#pasta para salvar as imagens
UPLOAD_DIR="static/uploads"
#caminho para o 'os'
os.makedirs(UPLOAD_DIR,exist_ok=True)
#rota para página inicial listar os produtos
@router.get("/",response_class=HTMLResponse)
async def listar(request:Request,
                 db:Session=Depends(get_db)):#coletar o banco 'produtos,db'
    #query banco de dados
    produtos=db.query(Produto).all()#puxar produtos do banco
    return templates.TemplateResponse("index.html",{
        "request":request,"produtos":produtos
    })

#rota detalhe do produto
@router.get("/produto/{id_produto}",
            response_class=HTMLResponse)
async def detalhe(request:Request,id_produto:int,
                  db:Session=Depends(get_db)):
    #query do produto
    produto=db.query(Produto).filter(Produto.id==id_produto).first()
    return templates.TemplateResponse("produto.html",{
        "request":request,"produto":produto
    })

###################################################
#controller.py
#CRUD dos produtos
#from database import get_db,SessionLocal#novo import

#função criar produto
async def criar_produto(
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    #caminho para salavar a imagem
    caminho=os.path.join(UPLOAD_DIR,imagem.filename)
    with open(caminho,"wb") as arquivo:
        shutil.copyfileobj(imagem.file,arquivo)
    #grava o produto
    novo=Produto(nome=nome,preco=preco,quantidade=quantidade,
                 imagem=imagem.filename)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

#rota da api para criar um item novo
@router.get("/novo",response_class=HTMLResponse)
async def form_novo(request:Request):
    return templates.TemplateResponse("novo.html",{
        "request":request
    })
#criar o método post para criar
@router.post("/novo")
async def criar(
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    await criar_produto(nome,preco,quantidade,imagem,db)
    return RedirectResponse("/",status_code=303)

#editar produto
async def atualizar_produto(
        id:int,
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    #buscar produto pelo id
    produto=db.query(Produto).filter(Produto.id==id).first()
    if not produto:
        return None
    produto.nome=nome
    produto.preco=preco
    produto.quantidade=quantidade
    #if para imagem
    if imagem and imagem.filename !="":
        #caminho para salvar
        #caminho para salavar a imagem
        caminho=os.path.join(UPLOAD_DIR,imagem.filename)
        with open(caminho,"wb") as arquivo:
            shutil.copyfileobj(imagem.file,arquivo)
        produto.imagem=imagem.filename
    db.commit()
    db.refresh(produto)
    return produto
#rota para editar o produto
@router.get("/editar/{id}",response_class=HTMLResponse)
async def form_editar(
    id:int,request:Request,db:Session=Depends(get_db)
):
    #query produto id
    produto=db.query(Produto).filter(Produto.id==id).first()
    return templates.TemplateResponse("editar.html",{
        "request":request,"produto":produto
    })

#criar o método post para editar
@router.post("/editar/{id}")
async def editar(
        id:int,
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    await atualizar_produto(id,nome,preco,quantidade,imagem,db)
    return RedirectResponse("/",status_code=303)

####################################
#deletar produto
async def deletar_produto(
    id:int,
    db:Session=Depends(get_db)      
): 
    produto=db.query(Produto).filter(Produto.id==id).first()
    if produto:
        db.delete(produto)
        db.commit()
    else:
        return None
    return produto
#rota para deletar
@router.get("/deletar/{id}")
async def deletar(id:int,
                  db:Session=Depends(get_db)):
    await deletar_produto(id,db)
    return RedirectResponse("/",status_code=303)

################################################
################################################
#Cadastro de usuário rotas de autenticação
@router.get("/register",response_class=HTMLResponse)
def pagina_cadastro(request:Request):
    return templates.TemplateResponse("register.html",{
        "request":request
    })
#formulário criar usuário
@router.post("/register")
def cadastrar_usuario( request:Request,
    nome:str = Form(...), email:str=Form(...),
    senha:str=Form(...),db:Session=Depends(get_db)
):
    usuario=db.query(Usuario).filter(Usuario.email==email).first()
    if usuario:
        return {"mensagem":"E-mail já cadastrado!"}
    senha_hash=gerar_hash_senha(senha)
    novo_usuario=Usuario(nome=nome,email=email,senha=senha_hash)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return RedirectResponse(url="/",status_code=303)
