import re
import os
import datetime
from sqlalchemy.orm import Session
from database import (
    SessionLocal, init_db, Rol, Usuario, Ubicacion, Cancha, Torneo, Equipo,
    Reserva, Producto, CategoriaProducto, Combo, Noticia, Evento, Propietario
)
from core.security import hash_password

def seed_database():
    init_db()
    db: Session = SessionLocal()

    # Si ya hay usuarios, no re-insertar
    if db.query(Usuario).first():
        db.close()
        return

    print("Inicializando base de datos MechApp con datos auténticos...")

    # 1. Roles
    roles_data = [
        Rol(id_rol=1, nombre="Administrador", descripcion="Gestiona usuarios y todo el sistema"),
        Rol(id_rol=2, nombre="Jugador", descripcion="Usuario que reserva canchas y participa en torneos"),
        Rol(id_rol=3, nombre="Propietario", descripcion="Usuario que administra canchas y torneos"),
    ]
    for r in roles_data:
        db.merge(r)
    db.commit()

    # 2. Ubicaciones
    ubicaciones_data = [
        Ubicacion(id_ubicacion=1, nombre="Club El Porvenir - Centro", direccion="Calle 22 # 14-35", ciudad="Bogotá D.C.", barrio="Centro"),
        Ubicacion(id_ubicacion=2, nombre="Complejo Deportivo Turmequé", direccion="Carrera 68 # 45-10", ciudad="Bogotá D.C.", barrio="Salitre"),
        Ubicacion(id_ubicacion=3, nombre="Club de Tejo La 76", direccion="Carrera 24 # 76-56", ciudad="Bogotá D.C.", barrio="Chapinero Norte"),
        Ubicacion(id_ubicacion=4, nombre="Club Social y Deportivo San Miguel", direccion="Calle 64 # 17-52", ciudad="Bogotá D.C.", barrio="Baquero - Teusaquillo"),
        Ubicacion(id_ubicacion=5, nombre="Tejo La Embajada (San Felipe)", direccion="Carrera 24 # 76-20", ciudad="Bogotá D.C.", barrio="San Felipe"),
        Ubicacion(id_ubicacion=13, nombre="Club de Tejo La Sabana (Chía)", direccion="Carrera 9 # 12-45", ciudad="Chía", barrio="Centro Histórico"),
        Ubicacion(id_ubicacion=14, nombre="Rancho Campestre El Tejo (Cota)", direccion="Vía Cota - Chía Km 2", ciudad="Cota", barrio="Vereda El Abra"),
        Ubicacion(id_ubicacion=15, nombre="Club Social La Cumbre (Soacha)", direccion="Carrera 7 # 15-40", ciudad="Soacha", barrio="Soacha Centro"),
    ]
    for u in ubicaciones_data:
        db.merge(u)
    db.commit()

    # 3. Usuarios oficiales
    # Contraseña por defecto hasheada con Argon2id: 'MechApp2026*Segura' (cumple 12+ caracteres, mayúsculas, minúsculas, números y símbolos)
    default_argon2 = hash_password("MechApp2026*Segura")

    usuarios_data = [
        Usuario(id_usuario=1, id_rol=1, nombre="Geraldine Rico (Administradora)", documento="1015404883", correo="admin@mechapp.com", telefono="3109876543", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=2, id_rol=2, nombre="Carlos Mendoza", documento="1023456789", correo="carlos@gmail.com", telefono="3123456789", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=3, id_rol=3, nombre="Carlos Propietario", documento="1000000002", correo="propietario@mechapp.com", telefono="3109876543", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=4, id_rol=2, nombre="Juan Jugador", documento="1000000003", correo="jugador@mechapp.com", telefono="3155554433", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=5, id_rol=2, nombre="Sandra Valentina Sanchez", documento="1023932136", correo="valita653@gmail.com", telefono="3054123662", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=7, id_rol=3, nombre="Bernardo Morales Pinzón", documento="1018456101", correo="bernardo.morales@tejobogota.com", telefono="3104567890", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=8, id_rol=3, nombre="Guillermo 'Mochila' Rincón", documento="1018456102", correo="guillermo.rincon@tejosanmiguel.com", telefono="3118901234", contrasena=default_argon2, acepta_tratamiento_datos=True),
        Usuario(id_usuario=14, id_rol=2, nombre="Miguel Cardona", documento="1034567890", correo="miguel@gmail.com", telefono="3445678902", contrasena=default_argon2, acepta_tratamiento_datos=True),
    ]
    for usr in usuarios_data:
        db.merge(usr)
    db.commit()

    # 4. Propietarios
    propietarios_data = [
        Propietario(id=1, usuario_id=3, empresa="Club Los Turmequés S.A.S.", nit="900.852.147-1", telefono_contacto="3109876543"),
        Propietario(id=2, usuario_id=7, empresa="Tejo Bogotá Real", nit="901.234.567-2", telefono_contacto="3104567890"),
        Propietario(id=3, usuario_id=8, empresa="Deportivo San Miguel", nit="901.987.654-3", telefono_contacto="3118901234"),
    ]
    for p in propietarios_data:
        db.merge(p)
    db.commit()

    # 5. Canchas
    canchas_data = [
        Cancha(id_cancha=1, id_usuario=3, id_ubicacion=1, nombre="Pista El Triunfo (Profesional)", descripcion="Cancha reglamentaria con arcilla purificada y caja metálica antirrebotante.", capacidad=12, precio_hora=35000.00),
        Cancha(id_cancha=2, id_usuario=3, id_ubicacion=2, nombre="Pista Tradicional Turmequé", descripcion="Pista tradicional con iluminación nocturna LED y zona social familiar.", capacidad=14, precio_hora=45000.00),
        Cancha(id_cancha=3, id_usuario=7, id_ubicacion=3, nombre="Cancha La 76 - VIP", descripcion="Ambiente prémium, sonido envolvente y servicio directo a mesa.", capacidad=10, precio_hora=50000.00),
        Cancha(id_cancha=4, id_usuario=8, id_ubicacion=4, nombre="Cancha San Miguel Mayor", descripcion="Pista para campeonatos y torneos federados de alta exigencia.", capacidad=16, precio_hora=40000.00),
    ]
    for c in canchas_data:
        db.merge(c)
    db.commit()

    # 6. Torneos
    torneos_data = [
        Torneo(id_torneo=1, id_cancha=1, nombre="Copa Mayor Turmequé de Oro", descripcion="Gran torneo departamental abierto de tejo profesional individual y por equipos.", fecha_inicio=datetime.date(2026, 12, 1), fecha_fin=datetime.date(2026, 12, 15), premio=3500000.00, cupo_maximo=32),
        Torneo(id_torneo=2, id_cancha=2, nombre="Torneo Relámpago Navideño", descripcion="Modalidad presencial, eliminación directa con premiación en efectivo y trofeos.", fecha_inicio=datetime.date(2026, 12, 18), fecha_fin=datetime.date(2026, 12, 22), premio=1800000.00, cupo_maximo=16),
    ]
    for t in torneos_data:
        db.merge(t)
    db.commit()

    # 7. Equipos
    equipos_data = [
        Equipo(id_equipo=1, id_capitan=2, nombre="Los Guerreros del Bocín", descripcion="Equipo federado con 3 títulos departamentales."),
        Equipo(id_equipo=2, id_capitan=4, nombre="Club Tejo Imperial", descripcion="Deportistas élite de Bogotá y Cundinamarca."),
        Equipo(id_equipo=3, id_capitan=5, nombre="Mecha Brava", descripcion="Equipo femenino y mixto juvenil de tejo."),
    ]
    for eq in equipos_data:
        db.merge(eq)
    db.commit()

    # 8. Categorías y Productos gastronómicos
    cat1 = CategoriaProducto(id_categoria=1, nombre="Platos Típicos y Picadas", icono="🍖")
    cat2 = CategoriaProducto(id_categoria=2, nombre="Bebidas y Cervezas", icono="🍺")
    db.merge(cat1)
    db.merge(cat2)
    db.commit()

    productos_data = [
        Producto(id_producto=1, id_cancha=1, id_categoria=1, nombre="Picada Mixta Familiar (4-6 pers)", descripcion="Chorizo, morcilla, carne de cerdo, papa criolla, plátano y arepa boyacense.", precio=65000.00, stock=30),
        Producto(id_producto=2, id_cancha=1, id_categoria=1, nombre="Porción de Empanadas (x6)", descripcion="Empanadas crocantes de carne desmechada y papa con ají casero.", precio=18000.00, stock=45),
        Producto(id_producto=3, id_cancha=1, id_categoria=2, nombre="Cerveza Nacional Águila / Poker (Unidad)", descripcion="Cerveza 330ml fría para el juego.", precio=6000.00, stock=150),
        Producto(id_producto=4, id_cancha=1, id_categoria=2, nombre="Gaseosa Familiar 1.5L", descripcion="Coca-Cola, Colombiana o Manzana Postobón.", precio=10000.00, stock=40),
    ]
    for p in productos_data:
        db.merge(p)
    db.commit()

    # 9. Combos
    combos_data = [
        Combo(id_combo=1, id_cancha=1, nombre="Combo Mecha & Amigos", descripcion="Picada Mixta Familiar + 6 Cervezas Nacionales Frías.", precio=92000.00, personas_min=4, personas_max=6),
    ]
    for cmb in combos_data:
        db.merge(cmb)
    db.commit()

    # 10. Noticias y Eventos
    db.merge(Noticia(
        id=1,
        titulo="El Tejo Colombiano: Patrimonio Cultural y Deporte Nacional",
        contenido="Conoce la historia del tejo desde los Muiscas de Turmequé hasta la Ley 613 del año 2000 que lo oficializó como deporte de nuestra patria.",
        autor_id=1,
        fecha_publicacion=datetime.datetime.utcnow(),
        imagen_url="https://s3.amazonaws.com/rtvc-assets-senalmemoria.gov.co/s3fs-public/field_image/tejo.jpg"
    ))
    db.merge(Evento(
        id=1,
        nombre="Festival Nacional del Tejo y la Tradición 2026",
        descripcion="Exhibición de maestros tejedores, campeonato relámpago y gastronomía típica.",
        cancha_id=1,
        fecha=datetime.datetime(2026, 12, 10, 14, 0),
        organizador="Federación Colombiana de Tejo y MechApp"
    ))
    db.commit()

    print("¡Base de datos MechApp inicializada con éxito!")
    db.close()

if __name__ == "__main__":
    seed_database()
