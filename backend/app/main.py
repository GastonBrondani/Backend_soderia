# app/main.py
from fastapi import FastAPI
from app.routers import personas  # luego sumaremos clientes

app = FastAPI()
app.include_router(personas.router)

@app.get("/")
def root():
    return {"ok": True}

