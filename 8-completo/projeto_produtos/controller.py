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
#IMPOST'S NOVO
from models import Produto,Usuario,ItemPedido,Pedido#IMPORT NOVO
from auth import gerar_hash_senha,verificar_senha,verificar_token,criar_token
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

#########################################################
#########################################################
#ROTAS DA API PARA AUTENTICAÇÃO

# --------------------------
# Cadastro de usuário
# --------------------------
@router.get("/register", response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def cadastrar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        return {"mensagem": "E-mail já cadastrado!"}

    senha_hash = gerar_hash_senha(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return RedirectResponse(url="/login", status_code=303)

# --------------------------
# Login do usuário
# --------------------------
@router.get("/login", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#novo login

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not verificar_senha(senha, usuario.senha):
        return {"mensagem": "Credenciais inválidas"}

    # Cria o token JWT com o campo is_admin
    token = criar_token({"sub": usuario.email, "is_admin": usuario.is_admin})
    
    # Verifica se o usuário é admin e direciona para a rota certa
    if usuario.is_admin:
        destino = "/admin"
    else:
        destino = "/me/painel"

    response = RedirectResponse(url=destino, status_code=303)
    response.set_cookie(key="token", value=token, httponly=True)
    return response
#########################################################
#########################################################
#########################################################
#########################################################
#rota admin crud nos produtos
@router.get("/admin",response_class=HTMLResponse)
def pagina_admin(request:Request,db:Session=Depends(get_db)):
    #token do admin
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload or not payload.get("is_admin"):
        return RedirectResponse(url="/",status_code=303)
    produtos=db.query(Produto).all()
    return templates.TemplateResponse("admin.html",{
        "request":request,"produtos":produtos
    })
#rota criar produto
@router.post("/admin/produto")
def criar_produto(request:Request,nome:str=Form(...),
    preco:float=Form(...),quantidade:int=Form(...),
    imagem:UploadFile=File(...),db:Session=Depends(get_db)
):
    caminho_arquivo=f"{UPLOAD_DIR}/{imagem.filename}"
    with open(caminho_arquivo,"wb") as arquivo:
        shutil.copyfileobj(imagem.file,arquivo)
    novo_produto=Produto(
        nome=nome,preco=preco,quantidade=quantidade,
        imagem=imagem.filename
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return RedirectResponse(url="/admin",status_code=303)

#editar produto
# Rota GET edição de produto
@router.get("/admin/produto/editar/{id}", response_class=HTMLResponse)
def editar_produto(id: int,request: Request,  db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload or not payload.get("is_admin"):
        return RedirectResponse(url="/", status_code=303)

    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        return RedirectResponse(url="/admin", status_code=303)

    return templates.TemplateResponse("editar.html", {
        "request": request,
        "produto": produto
    })


# Rota Atualizar produto
@router.post("/admin/produto/atualizar/{id}")
def atualizar_produto(
    id: int,
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    imagem: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        return RedirectResponse(url="/admin", status_code=303)

    # Atualiza campos
    produto.nome = nome
    produto.preco = preco
    produto.quantidade = quantidade

    # Atualiza imagem se uma nova for enviada
    if imagem and imagem.filename != "":
        caminho_arquivo = f"{UPLOAD_DIR}/{imagem.filename}"
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
        produto.imagem = imagem.filename

    db.commit()
    db.refresh(produto)
    return RedirectResponse(url="/admin", status_code=303)

#deletar produto
@router.post("/admin/produto/deletar/{id}")
def deletar_produto(id:int,db:Session=Depends(get_db)):
    produto=db.query(Produto).filter(Produto.id==id).first()
    if produto:
        db.delete(produto)
        db.commit()
    return RedirectResponse(url="/admin",status_code=303)

###################################################
#carrinho
# Carrinho simples em memória (simulação)
carrinhos = {}

# ---------------------------------------
# Página inicial: lista produtos
# ---------------------------------------
@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return templates.TemplateResponse("index.html", {"request": request, "produtos": produtos})


# ---------------------------------------
# Adicionar item ao carrinho
# ---------------------------------------
@router.post("/carrinho/adicionar/{produto_id}")
def adicionar_ao_carrinho(request: Request, 
produto_id: int, quantidade: int = Form(1),
db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(Usuario).filter_by(email=email).first()

    produto = db.query(Produto).filter_by(id=produto_id).first()
    if not produto:
        return {"mensagem": "Produto não encontrado"}

    carrinho = carrinhos.get(usuario.id, [])
    carrinho.append({
        "id": produto.id,
        "nome": produto.nome,
        "preco": produto.preco,
        "quantidade": quantidade
    })
    carrinhos[usuario.id] = carrinho

    return RedirectResponse(url="/carrinho", status_code=303)

# ---------------------------------------
# Visualizar carrinho
# ---------------------------------------
@router.get("/carrinho", response_class=HTMLResponse)
def ver_carrinho(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(Usuario).filter_by(email=email).first()
    carrinho = carrinhos.get(usuario.id, [])
    total = sum(item["preco"] * item["quantidade"] for item in carrinho)

    return templates.TemplateResponse("carrinho.html", 
        {"request": request, "carrinho": carrinho, "total": total})

# ---------------------------------------
# Finalizar compra (Checkout)
# ---------------------------------------
@router.post("/checkout")
def checkout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(Usuario).filter_by(email=email).first()
    carrinho = carrinhos.get(usuario.id, [])
    if not carrinho:
        return {"mensagem": "Carrinho vazio"}

    total = sum(item["preco"] * item["quantidade"] for item in carrinho)
    pedido = Pedido(usuario_id=usuario.id, total=total)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    for item in carrinho:
        novo_item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=item["id"],
            quantidade=item["quantidade"],
            preco_unitario=item["preco"]
        )
        db.add(novo_item)
    db.commit()

    carrinhos[usuario.id] = []  # limpa o carrinho
    return RedirectResponse(url="/meus-pedidos", status_code=303)

# ---------------------------------------
# Listar pedidos do usuário
# ---------------------------------------
@router.get("/meus-pedidos", response_class=HTMLResponse)
def meus_pedidos(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(Usuario).filter_by(email=email).first()
    pedidos = db.query(Pedido).filter_by(usuario_id=usuario.id).all()

    return templates.TemplateResponse("meus_pedidos.html",
                 {"request": request, "pedidos": pedidos})

######################################################
######################################################
######################################################
#user pedido
# -------------------------------
# Rota: Painel do usuário
# -------------------------------
@router.get("/me/painel", response_class=HTMLResponse)
def painel_usuario(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/", status_code=303)

    usuario = db.query(Usuario).filter(Usuario.email == payload["sub"]).first()
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()

    return templates.TemplateResponse(
        "painel_usuario.html",
        {"request": request, "usuario": usuario, "pedidos": pedidos},
    )

# -------------------------------
# Rota: Meus dados
# -------------------------------
@router.get("/me/dados", response_class=HTMLResponse)
def meus_dados(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/", status_code=303)

    usuario = db.query(Usuario).filter(Usuario.email == payload["sub"]).first()
    return templates.TemplateResponse("meus_dados.html", {"request": request, "usuario": usuario})

# -------------------------------
# Rota: Meus pedidos
# -------------------------------
@router.get("/me/pedidos", response_class=HTMLResponse)
def meus_pedidos(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/", status_code=303)

    usuario = db.query(Usuario).filter(Usuario.email == payload["sub"]).first()
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()
    return templates.TemplateResponse("meus_pedidos.html", {"request": request, "pedidos": pedidos})

'''
3. Atualizar /checkout para persistir o pedido
'''
@router.post("/checkout")
def checkout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    usuario = db.query(Usuario).filter(Usuario.email == payload["sub"]).first()

    # Aqui você pode recuperar os itens do carrinho (fake por enquanto)
    total = 199.90  # valor simulado

    novo_pedido = Pedido(usuario_id=usuario.id, total=total, status="Pendente")
    db.add(novo_pedido)
    db.commit()

    return RedirectResponse(url="/me/pedidos", status_code=303)
@router.get("/logout")
def logout(request: Request):
    """
    Remove o cookie do token JWT e redireciona para a página inicial.
    """
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="token")  # Apaga o token
    return response