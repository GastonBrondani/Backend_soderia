# app/main.py
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.scheduler import start_scheduler, stop_scheduler


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
