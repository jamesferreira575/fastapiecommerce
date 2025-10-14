#auth.py
from datetime import datetime,timedelta
#datetime tempo do token do usuário
from jose import JWSError,jwt
#jwt=json web token , 
#jose=javascript object signing encryption
from passlib.context import CryptContext
#CryptContext = implementação de criptografia
#criar a chave de assinatura do programa
SECRET_KEY="chave_secreta"#mudar em produção guardar em uma variável
ALGORITHM="HS256"
'''HS256 algoritimo simétrico de 256 bites para criptografia'''
#tempo do token de usuário
ACCESS_TOKEN=30#30 MINUTOS de tempo de token
#criptografia de senha
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
#bcrypt=base da criptografia do passlib
#função de gerar o hash da senha
def gerar_hash_senha(senha:str):
    return pwd_context.hash(senha)
#função para verificar o hash da senha
def verificar_hash_senha(senha:str,senha_hash:str):
    return pwd_context.verify(senha,senha_hash)
