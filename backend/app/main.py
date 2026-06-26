from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler, stop_scheduler
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(
    title="Soderia API",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(api_router)

# 👇 permite que el front en localhost pueda pegarle
origins = [
    "http://localhost:53703",  # tu flutter web hoy
    "http://localhost:5173",  # si usás otro puerto
    "http://localhost:8500",  # por las dudas
    "http://localhost:51935",
    "*",  # si querés abrirlo del todo mientras desarrollás
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # o ["*"] en dev
    allow_credentials=True,
    allow_methods=["*"],  # 👈 IMPORTANTE (GET, POST, OPTIONS, etc)
    allow_headers=["*"],
)

DATA_DIR = os.getenv("DATA_DIR", "/data")

_pagos_dir = os.path.join(DATA_DIR, "comprobantes", "pagos")
_pedidos_dir = os.path.join(DATA_DIR, "comprobantes", "pedidos")

os.makedirs(_pagos_dir, exist_ok=True)
os.makedirs(_pedidos_dir, exist_ok=True)

app.mount(
    "/docs/comprobantes/pagos",
    StaticFiles(directory=_pagos_dir),
    name="comprobantes_pagos",
)

app.mount(
    "/docs/comprobantes/pedidos",
    StaticFiles(directory=_pedidos_dir),
    name="comprobantes_pedidos",
)


@app.get("/health")
def health():
    return {"status": "ok"}
