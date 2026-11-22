from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import datetime


class UsuarioRegistro(BaseModel):
    id_rol: int
    nombre: str
    documento: str
    correo: EmailStr
    telefono: Optional[str] = None
    contrasena: str

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número.")
        return v

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        return v

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, v: str) -> str:
        v = v.strip()
        if not v.isalnum():
            raise ValueError("El documento solo puede contener letras y números.")
        return v


class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class UsuarioAuthResponse(BaseModel):
    id_usuario: int
    id_rol: int
    nombre: str
    documento: str
    correo: str
    telefono: Optional[str] = None
    estado: bool
    fecha_registro: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioAuthResponse


class SolicitudRecuperacion(BaseModel):
    correo: EmailStr


class RestablecerContrasena(BaseModel):
    token: str
    nueva_contrasena: str

    @field_validator("nueva_contrasena")
    @classmethod
    def validar_nueva_contrasena(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número.")
        return v
