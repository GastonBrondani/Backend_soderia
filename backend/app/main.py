from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from app.api.router import api_router 

app = FastAPI()
app.include_router(api_router)

# 👇 permite que el front en localhost pueda pegarle
origins = [
    "http://localhost:53703",   # tu flutter web hoy
    "http://localhost:5173",    # si usás otro puerto
    "http://localhost:8500",    # por las dudas
    "http://localhost:51935",
    "*"                         # si querés abrirlo del todo mientras desarrollás
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # o ["*"] en dev
    allow_credentials=True,
    allow_methods=["*"],            # 👈 IMPORTANTE (GET, POST, OPTIONS, etc)
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jornadas")
def jornadas(year: int, month: int):
    data = [
        {"fecha": date(year, month, 1).isoformat(), "clientes": ["Ana", "Luis"]},
        {"fecha": date(year, month, 1).isoformat(), "clientes": ["Carla"]},
        {"fecha": date(year, month, 2).isoformat(), "clientes": []},
        {"fecha": date(year, month, 3).isoformat(), "clientes": ["Marcos", "Tania", "Luz"]},
    ]
    return data
