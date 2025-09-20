from fastapi import APIRouter
from app.routers import empresa, persona, cliente,direccionCliente, emailCliente, telefonoCliente, empleado

api_router = APIRouter()
api_router.include_router(empresa.router)
api_router.include_router(persona.router)
api_router.include_router(cliente.router)
api_router.include_router(direccionCliente.router)
api_router.include_router(emailCliente.router)
api_router.include_router(telefonoCliente.router)
api_router.include_router(empleado.router)


