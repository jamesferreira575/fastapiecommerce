# auth.py
#pip install python-jose passlib
from datetime import datetime, timedelta
#datetime= ano, mês, dia, hora, minuto, segundo, microssegundo, 
#timedelta= adição ou subtração de data
from jose import JWTError, jwt
#jose=JavaScript Object Signing and Encryption (JOSE)  tecnologias de Assinatura e Criptografia de Objetos JavaScript 
#JWTError=menssagem de erro de cripitografia
#JWT=JSON Web Token (JWT)é um objeto JSON que traz consigo uma informação codificada e assinada, de forma que ela seja confiável entre duas partes
from passlib.context import CryptContext
#Implementação de contexto de criptografia 
#CryptContext = Auxiliar para hash e verificação de senhas usando múltiplos algoritmos
#pip install
# Chave secreta para assinatura do token (em produção, guarde em variável de ambiente)
SECRET_KEY = "chave-super-secreta"
ALGORITHM = "HS256"
'''
HS256 é um algoritmo simétrico que compartilha uma 
chave secreta entre o provedor de identidade e seu 
aplicativo. A mesma chave é usada para assinar um JWT e 
verificar essa assinatura
'''
ACCESS_TOKEN_EXPIRE_MINUTES = 30#30 minutos de temp0

# Criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# gerar hash de senha
def gerar_hash_senha(senha: str):
    return pwd_context.hash(senha)
#verificar_senha
def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)
#criar_token
def criar_token(dados: dict):
    dados_token = dados.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_token.update({"exp": expira})
    token_jwt = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt
#verificar_token payload =carga útil
def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
