from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session,selectinload
from sqlalchemy import and_
from app.database import get_db
from app.models.cliente import Cliente
from app.models.persona import Persona
from app.schemas.cliente import ClienteCreate, ClienteOut,ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def CrearCliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    try:
        # Resolver DNI final coherente
        dni_final = payload.persona.dni if payload.persona else payload.dni
        
        persona = db.get(Persona, dni_final)
        if payload.persona:
            if not persona:
                persona = Persona(**payload.persona.model_dump())
                db.add(persona)
            else:
                # Si quisieras sincronizar nombre/apellido si vinieran distintos, podrías actualizar acá
                pass
        else:
            if not persona:
                raise HTTPException(status_code=404, detail="La persona (dni) no existe. Envía 'persona' para crearla.")

        # Evitar duplicado por regla de negocio (dni, id_empresa)
        duplicado = db.query(Cliente).filter(
            and_(Cliente.dni == dni_final, Cliente.id_empresa == payload.id_empresa)
        ).first()
        if duplicado:
            raise HTTPException(status_code=409, detail="Ya existe un cliente para ese DNI en esa empresa.")
        
        nuevo = Cliente(
            id_empresa=payload.id_empresa,
            dni=dni_final,
            observacion=payload.observacion,
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        nuevo.persona = persona
        return nuevo

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando cliente: {e}")
    
@router.get("/", response_model=List[ClienteOut])
def ListarClientes(limit: int = 50,offset: int = 0,db: Session = Depends(get_db),):
    """ -limit y offset son para paginación en el GET /clientes.
        -limit: int = 50 → cuántos registros como máximo devolver (por defecto 50).
        -offset: int = 0 → cuántos registros saltar desde el inicio (por defecto 0, o sea desde el primero).
    """
    q = (
        db.query(Cliente)
        .options(selectinload(Cliente.persona))
        .offset(offset)
        .limit(limit)
    )
    return q.all()


@router.get("/{legajo}", response_model=ClienteOut)
def BuscarCliente(legajo: int, db: Session = Depends(get_db)):
    cliente = (
        db.query(Cliente)
        .options(selectinload(Cliente.persona))
        .filter(Cliente.legajo == legajo)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/{legajo}", response_model=ClienteOut)
def ActualizarCliente(legajo: int, payload: ClienteUpdate, db: Session = Depends(get_db)):
    try:
        cliente = db.get(Cliente, legajo)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # actualizar campos del cliente
        data_cliente = payload.model_dump(exclude_unset=True)
        persona_patch = data_cliente.pop("persona", None)

        for campo, valor in data_cliente.items():
            setattr(cliente, campo, valor)

        # actualizar (opcional) nombre/apellido de la persona vinculada
        if persona_patch:
            persona = db.get(Persona, cliente.dni)
            if not persona:
                raise HTTPException(status_code=409, detail="Inconsistencia: el cliente no tiene persona asociada.")
            for campo, valor in persona_patch.items():
                if valor is not None:
                    setattr(persona, campo, valor)

        db.commit()
        db.refresh(cliente)
        # asegurar persona cargada en salida
        cliente = (
            db.query(Cliente)
            .options(selectinload(Cliente.persona))
            .filter(Cliente.legajo == legajo)
            .first()
        )
        return cliente

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando cliente: {e}")


@router.delete("/{legajo}", status_code=status.HTTP_204_NO_CONTENT)
def BorrarCliente(legajo: int, db: Session = Depends(get_db)):
    try:
        cliente = db.get(Cliente, legajo)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        db.delete(cliente)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        # Si hay FKs (pedidos, usuarios, etc.) puede fallar por restricción
        raise HTTPException(status_code=409, detail=f"No se pudo eliminar el cliente (referencias activas): {e}")
