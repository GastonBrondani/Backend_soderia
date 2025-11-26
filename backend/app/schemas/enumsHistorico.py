# app/schemas/enums_historico.py
from enum import StrEnum


class TipoEventoCodigoEnum(StrEnum):
    CLIENTE_ACTUALIZADO = "CLIENTE_ACTUALIZADO"
    # Más adelante:
    # VISITA_REGISTRADA = "VISITA_REGISTRADA"
    # PEDIDO_CREADO = "PEDIDO_CREADO"
    # PEDIDO_ACTUALIZADO = "PEDIDO_ACTUALIZADO"
