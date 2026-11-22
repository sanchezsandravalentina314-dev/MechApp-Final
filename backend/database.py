import os
import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, Numeric, DateTime, Date, Time, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mechapp.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# Modelos de Base de Datos
# ==========================================

class Rol(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255))
    estado = Column(Boolean, default=True)

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"), nullable=False, default=2)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=True)
    contrasena = Column(String(255), nullable=False) # Almacenada con Argon2id
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)
    acepta_tratamiento_datos = Column(Boolean, default=False)
    fecha_aceptacion_tratamiento = Column(DateTime, nullable=True)
    version_politica_aceptada = Column(String(10), nullable=True)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    correo = Column(String(150), nullable=False)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)
    expira_en = Column(DateTime, nullable=False)
    utilizado = Column(Boolean, default=False)

class Propietario(Base):
    __tablename__ = "propietarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    empresa = Column(String(150))
    nit = Column(String(50))
    telefono_contacto = Column(String(30))

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    id_ubicacion = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=False)
    ciudad = Column(String(100), nullable=False)
    barrio = Column(String(100))
    estado = Column(Boolean, default=True)

class Cancha(Base):
    __tablename__ = "canchas"
    id_cancha = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_ubicacion = Column(Integer, ForeignKey("ubicaciones.id_ubicacion"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    capacidad = Column(Integer, default=12)
    estado = Column(Boolean, default=True)
    precio_hora = Column(Numeric(10, 2), default=35000.00)

class Torneo(Base):
    __tablename__ = "torneos"
    id_torneo = Column(Integer, primary_key=True, autoincrement=True)
    id_cancha = Column(Integer, ForeignKey("canchas.id_cancha"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    premio = Column(Numeric(12, 2))
    estado = Column(String(30), default="En Inscripción")
    cupo_maximo = Column(Integer, default=16)

class Equipo(Base):
    __tablename__ = "equipos"
    id_equipo = Column(Integer, primary_key=True, autoincrement=True)
    id_capitan = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)

class Partido(Base):
    __tablename__ = "partidos"
    id_partido = Column(Integer, primary_key=True, autoincrement=True)
    id_torneo = Column(Integer, ForeignKey("torneos.id_torneo"), nullable=False)
    id_equipo_local = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    id_equipo_visitante = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    ronda = Column(String(50), default="Fase Regular")
    estado = Column(String(30), default="Programado")

class Resultado(Base):
    __tablename__ = "resultados"
    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_partido = Column(Integer, ForeignKey("partidos.id_partido"), unique=True, nullable=False)
    id_equipo_ganador = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=True)
    puntos_local = Column(Integer, default=0)
    puntos_visitante = Column(Integer, default=0)
    observaciones = Column(Text)

class Reserva(Base):
    __tablename__ = "reservas"
    id_reserva = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_cancha = Column(Integer, ForeignKey("canchas.id_cancha"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(30), default="Confirmada")
    fecha_reserva = Column(DateTime, default=datetime.datetime.utcnow)

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    cancha_id = Column(Integer, ForeignKey("canchas.id_cancha"), nullable=True)
    fecha = Column(DateTime, nullable=False)
    organizador = Column(String(100))
    estado = Column(String(30), default="Programado")

class Noticia(Base):
    __tablename__ = "noticias"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    fecha_publicacion = Column(DateTime, default=datetime.datetime.utcnow)
    imagen_url = Column(String(255))

class CategoriaProducto(Base):
    __tablename__ = "categorias_producto"
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255))
    icono = Column(String(10))
    estado = Column(Boolean, default=True)

class Producto(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    id_cancha = Column(Integer, ForeignKey("canchas.id_cancha"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias_producto.id_categoria"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    imagen_url = Column(String(500))
    stock = Column(Integer, default=50)
    stock_minimo = Column(Integer, default=5)
    estado = Column(Boolean, default=True)

class Combo(Base):
    __tablename__ = "combos"
    id_combo = Column(Integer, primary_key=True, autoincrement=True)
    id_cancha = Column(Integer, ForeignKey("canchas.id_cancha"), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    personas_min = Column(Integer, default=2)
    personas_max = Column(Integer, default=6)
    imagen_url = Column(String(500))
    estado = Column(Boolean, default=True)

class Reporte(Base):
    __tablename__ = "reportes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo = Column(String(50))
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    estado = Column(String(30), default="Generado")

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id_notificacion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    titulo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    leida = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)
