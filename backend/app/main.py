# app/main.py
from fastapi import FastAPI
from app.routers import persona,cliente,empresa  # luego sumaremos clientes

app = FastAPI()
app.include_router(persona.router)
app.include_router(cliente.router)
app.include_router(empresa.router)

@app.get("/")
def root():
    return {"ok": True}

