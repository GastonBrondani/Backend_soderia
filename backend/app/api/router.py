from fastapi import APIRouter
from app.routers import (empresa, persona, cliente,direccionCliente, emailCliente, telefonoCliente, empleado,
                          clienteCuenta, producto, listaPrecios,stock, movimientoStock, recorrido,camionReparto,
                          repartoDia, usuario, clienteDiaSemana, diaSemana, clienteRepartoDia,pedido,medioPago, auth)

#Los comentados por ahora no se usan
api_router = APIRouter()
api_router.include_router(empresa.router)
api_router.include_router(persona.router)
api_router.include_router(cliente.router)
api_router.include_router(direccionCliente.router)
api_router.include_router(emailCliente.router)
api_router.include_router(telefonoCliente.router)
api_router.include_router(empleado.router)
api_router.include_router(clienteCuenta.router)
api_router.include_router(producto.router)
api_router.include_router(listaPrecios.router)
api_router.include_router(stock.router)
api_router.include_router(movimientoStock.router)
api_router.include_router(recorrido.router)
api_router.include_router(camionReparto.router)
api_router.include_router(repartoDia.router)
api_router.include_router(usuario.router)
api_router.include_router(clienteDiaSemana.router)
api_router.include_router(diaSemana.router)
api_router.include_router(clienteRepartoDia.router)
api_router.include_router(pedido.router)
api_router.include_router(medioPago.router)
api_router.include_router(auth.router)
