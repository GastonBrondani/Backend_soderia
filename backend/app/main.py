# app/main.py
from fastapi import FastAPI
from app.routers import persona,cliente,empresa,emailCliente,telefonoCliente  # luego sumaremos clientes

app = FastAPI()
app.include_router(persona.router)
app.include_router(cliente.router)
app.include_router(empresa.router)
app.include_router(telefonoCliente.router)
app.include_router(emailCliente.router)

@app.get("/")
def root():
    return {"ok": True}

