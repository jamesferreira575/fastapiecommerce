#main.py
from fastapi import FastAPI#import principal
from controller import router#import back-end
from fastapi.staticfiles import StaticFiles#montar a pasta 'imagens'
#app da aplicação
app=FastAPI(title="MVC Produtos")
#montar a pasta das imagens
app.mount("/static",StaticFiles(directory="static"),
          name="static")
#incluir a rota das apis
app.include_router(router)
#python -m uvicorn main:app --reload
