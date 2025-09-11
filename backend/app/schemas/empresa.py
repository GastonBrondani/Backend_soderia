from pydantic import BaseModel


class EmpresaBase(BaseModel):
    razon_social : str

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaRead(EmpresaBase):
    id_empresa: int
    