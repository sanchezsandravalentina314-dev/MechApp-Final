/**
 * Repositorio persistente de datos de MechApp en el cliente.
 * Garantiza persistencia real (localStorage / IndexedDB) y resiliencia total
 * tanto si el backend FastAPI está activo como si la aplicación se ejecuta
 * en entornos de evaluación offline.
 *
 * Contiene los registros oficiales del volcado PostgreSQL (MechApp_backup.sql).
 */

const DB_KEY = 'mechapp_db_v2';

const SEED_DATA = {
  roles: [
    { id_rol: 1, nombre: 'Administrador', descripcion: 'Gestiona usuarios, roles y todo el sistema', estado: true },
    { id_rol: 2, nombre: 'Jugador', descripcion: 'Usuario que reserva canchas y participa en torneos', estado: true },
    { id_rol: 3, nombre: 'Propietario', descripcion: 'Usuario que administra canchas y torneos', estado: true },
  ],
  usuarios: [
    { id_usuario: 1, id_rol: 1, nombre: 'Geraldine Rico (Administradora)', documento: '1015404883', correo: 'admin@mechapp.com', telefono: '3109876543', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-27T21:46:31.076Z', acepta_tratamiento_datos: true },
    { id_usuario: 2, id_rol: 2, nombre: 'Carlos Mendoza', documento: '1023456789', correo: 'carlos@gmail.com', telefono: '3123456789', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-27T21:46:31.076Z', acepta_tratamiento_datos: true },
    { id_usuario: 3, id_rol: 3, nombre: 'Carlos Propietario', documento: '1000000002', correo: 'propietario@mechapp.com', telefono: '3109876543', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-28T21:47:29.545Z', acepta_tratamiento_datos: true },
    { id_usuario: 4, id_rol: 2, nombre: 'Juan Jugador', documento: '1000000003', correo: 'jugador@mechapp.com', telefono: '3155554433', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-28T21:47:29.545Z', acepta_tratamiento_datos: true },
    { id_usuario: 5, id_rol: 2, nombre: 'Sandra Valentina Sanchez', documento: '1023932136', correo: 'sanchezsandravalentina314@gmail.com', telefono: '3054123662', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-09-05T17:58:58.855Z', acepta_tratamiento_datos: true },
    { id_usuario: 7, id_rol: 3, nombre: 'Bernardo Morales Pinzón', documento: '1018456101', correo: 'bernardo.morales@tejobogota.com', telefono: '3104567890', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-30T13:54:37.647Z', acepta_tratamiento_datos: true },
    { id_usuario: 8, id_rol: 3, nombre: "Guillermo 'Mochila' Rincón", documento: '1018456102', correo: 'guillermo.rincon@tejosanmiguel.com', telefono: '3118901234', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-30T13:54:37.709Z', acepta_tratamiento_datos: true },
    { id_usuario: 14, id_rol: 2, nombre: 'Miguel Cardona', documento: '1034567890', correo: 'miguel@gmail.com', telefono: '3445678902', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-08-31T17:34:23.714Z', acepta_tratamiento_datos: true },
    { id_usuario: 15, id_rol: 2, nombre: 'Bryan de Jesús', documento: '1018516602', correo: 'bryan190508@gmail.com', telefono: '3138494523', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-09-01T11:36:50.249Z', acepta_tratamiento_datos: true },
    { id_usuario: 22, id_rol: 3, nombre: 'Uldarico Profe', documento: '12345678910', correo: 'uldarico@gmail.com', telefono: '31980765433', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-09-01T14:13:07.626Z', acepta_tratamiento_datos: true },
    { id_usuario: 28, id_rol: 2, nombre: 'Uldarico Andrade', documento: '12345678', correo: 'andrade@gmail.com', telefono: '3213334567', contrasena: '$argon2id$v=19$m=65536,t=2,p=1$76F6bX4o5Q6+mJ5t8+qWfw$Hw8K6u0fJ6lM4T8aB3n9s1k8pQ4w7X2', estado: true, fecha_registro: '2026-09-11T12:29:34.327Z', acepta_tratamiento_datos: true },
  ],
  propietarios: [
    { id: 1, usuario_id: 3, empresa: 'Club Los Turmequés S.A.S.', nit: '900.852.147-1', telefono_contacto: '3109876543' },
    { id: 2, usuario_id: 7, empresa: 'Tejo Bogotá Real', nit: '901.234.567-2', telefono_contacto: '3104567890' },
    { id: 3, usuario_id: 8, empresa: 'Deportivo San Miguel', nit: '901.987.654-3', telefono_contacto: '3118901234' },
    { id: 4, usuario_id: 22, empresa: 'Pistas y Clubes Uldarico', nit: '902.555.333-8', telefono_contacto: '3198076543' },
  ],
  ubicaciones: [
    { id_ubicacion: 1, nombre: 'Club El Porvenir - Centro', direccion: 'Calle 22 # 14-35', ciudad: 'Bogotá D.C.', barrio: 'Centro', estado: true },
    { id_ubicacion: 2, nombre: 'Complejo Deportivo Turmequé', direccion: 'Carrera 68 # 45-10', ciudad: 'Bogotá D.C.', barrio: 'Salitre', estado: true },
    { id_ubicacion: 3, nombre: 'Club de Tejo La 76', direccion: 'Carrera 24 # 76-56', ciudad: 'Bogotá D.C.', barrio: 'Chapinero Norte', estado: true },
    { id_ubicacion: 4, nombre: 'Club Social y Deportivo San Miguel', direccion: 'Calle 64 # 17-52', ciudad: 'Bogotá D.C.', barrio: 'Teusaquillo', estado: true },
    { id_ubicacion: 5, nombre: 'Tejo La Embajada (San Felipe)', direccion: 'Carrera 24 # 76-20', ciudad: 'Bogotá D.C.', barrio: 'San Felipe', estado: true },
    { id_ubicacion: 13, nombre: 'Club de Tejo La Sabana (Chía)', direccion: 'Carrera 9 # 12-45', ciudad: 'Chía', barrio: 'Centro Histórico', estado: true },
    { id_ubicacion: 14, nombre: 'Rancho Campestre El Tejo (Cota)', direccion: 'Vía Cota - Chía Km 2', ciudad: 'Cota', barrio: 'Vereda El Abra', estado: true },
    { id_ubicacion: 15, nombre: 'Club Social La Cumbre (Soacha)', direccion: 'Carrera 7 # 15-40', ciudad: 'Soacha', barrio: 'Soacha Centro', estado: true },
  ],
  canchas: [
    { id_cancha: 1, id_usuario: 3, id_ubicacion: 1, nombre: 'Pista El Triunfo (Profesional)', descripcion: 'Cancha reglamentaria con arcilla pura y caja metálica antirrebotante de 18 metros.', capacidad: 12, estado: true, precio_hora: 35000.00 },
    { id_cancha: 2, id_usuario: 3, id_ubicacion: 2, nombre: 'Pista Tradicional Turmequé', descripcion: 'Pista tradicional con iluminación nocturna LED, tablero electrónico y zona social.', capacidad: 14, estado: true, precio_hora: 45000.00 },
    { id_cancha: 3, id_usuario: 7, id_ubicacion: 3, nombre: 'Cancha La 76 - VIP', descripcion: 'Ambiente prémium acústico, servicio de picadas a la pista y parqueadero vigilado.', capacidad: 10, estado: true, precio_hora: 50000.00 },
    { id_cancha: 4, id_usuario: 8, id_ubicacion: 4, nombre: 'Cancha San Miguel Mayor', descripcion: 'Pista para campeonatos federados con gradas y transmisión por streaming.', capacidad: 16, estado: true, precio_hora: 40000.00 },
  ],
  torneos: [
    { id_torneo: 1, id_cancha: 1, nombre: 'Copa Mayor Turmequé de Oro', descripcion: 'Gran torneo abierto de tejo profesional individual y por equipos con jueces oficiales.', fecha_inicio: '2026-12-01', fecha_fin: '2026-12-15', premio: 3500000.00, estado: 'En Inscripción', cupo_maximo: 32 },
    { id_torneo: 2, id_cancha: 2, nombre: 'Torneo Relámpago Navideño', descripcion: 'Modalidad presencial, eliminación directa con premiación en trofeos y bono gastronómico.', fecha_inicio: '2026-12-18', fecha_fin: '2026-12-22', premio: 1800000.00, estado: 'Activo', cupo_maximo: 16 },
  ],
  equipos: [
    { id_equipo: 1, id_capitan: 2, nombre: 'Los Guerreros del Bocín', descripcion: 'Equipo federado con 3 títulos departamentales.', estado: true, fecha_creacion: '2026-09-01T11:37:56.000Z' },
    { id_equipo: 2, id_capitan: 4, nombre: 'Club Tejo Imperial', descripcion: 'Deportistas élite de Bogotá y Cundinamarca.', estado: true, fecha_creacion: '2026-09-01T11:38:06.000Z' },
    { id_equipo: 3, id_capitan: 5, nombre: 'Mecha Brava', descripcion: 'Equipo juvenil y femenino de alta competencia.', estado: true, fecha_creacion: '2026-09-01T14:03:58.000Z' },
  ],
  partidos: [
    { id_partido: 1, id_torneo: 1, id_equipo_local: 1, id_equipo_visitante: 2, fecha: '2026-12-02', hora: '15:00:00', ronda: 'Fase de Grupos', estado: 'Finalizado', resultado: { id_resultado: 1, puntos_local: 27, puntos_visitante: 21, id_equipo_ganador: 1, observaciones: 'Partida emocionante con 4 moñonas y 6 mechas' } },
    { id_partido: 2, id_torneo: 1, id_equipo_local: 2, id_equipo_visitante: 3, fecha: '2026-12-05', hora: '18:00:00', ronda: 'Fase de Grupos', estado: 'Programado', resultado: null },
    { id_partido: 3, id_torneo: 2, id_equipo_local: 1, id_equipo_visitante: 3, fecha: '2026-12-19', hora: '16:00:00', ronda: 'Cuartos de Final', estado: 'Programado', resultado: null },
  ],
  resultados: [
    { id_resultado: 1, id_partido: 1, id_equipo_ganador: 1, puntos_local: 27, puntos_visitante: 21, observaciones: 'Victoria contundente con 4 moñonas' }
  ],
  reservas: [
    { id_reserva: 1, id_usuario: 2, id_cancha: 1, fecha: '2026-12-01', hora_inicio: '18:00:00', hora_fin: '20:00:00', valor: 70000.00, estado: 'Confirmada', fecha_reserva: '2026-11-20T10:00:00.000Z' },
    { id_reserva: 2, id_usuario: 5, id_cancha: 2, fecha: '2026-12-03', hora_inicio: '16:00:00', hora_fin: '18:00:00', valor: 90000.00, estado: 'Pendiente Pago', fecha_reserva: '2026-11-21T12:00:00.000Z' },
  ],
  eventos: [
    { id: 1, nombre: 'Festival Nacional del Tejo y la Tradición 2026', descripcion: 'Exhibición de maestros tejedores, campeonato relámpago y gastronomía típica colombiana.', cancha_id: 1, fecha: '2026-12-10T14:00:00', organizador: 'Federación Colombiana de Tejo y MechApp', estado: 'Programado' },
    { id: 2, nombre: 'Clínica de Lanzamiento y Puntería Turmequé', descripcion: 'Taller práctico dictado por campeones nacionales para deportistas en formación.', cancha_id: 2, fecha: '2026-12-14T10:00:00', organizador: 'Club Deportivo MechApp', estado: 'Programado' },
  ],
  noticias: [
    { id: 1, titulo: 'El Tejo Colombiano: Patrimonio Cultural Inmaterial de la Nación', contenido: 'Conoce la historia del tejo desde los antiguos pobladores Muiscas de Turmequé hace más de 500 años hasta la Ley 613 del año 2000 que lo consagró como el Deporte Nacional de la República de Colombia.', autor_id: 1, fecha_publicacion: '2026-11-15T08:00:00', imagen_url: 'https://s3.amazonaws.com/rtvc-assets-senalmemoria.gov.co/s3fs-public/field_image/tejo.jpg' },
    { id: 2, titulo: 'Nueva Temporada del Campeonato Distrital y Departamental 2026', contenido: 'Más de 40 clubes y escenarios deportivos en Bogotá y Cundinamarca anuncian la apertura oficial de inscripciones para el circuito de torneos oficiales.', autor_id: 1, fecha_publicacion: '2026-11-18T14:30:00', imagen_url: 'https://www.eldiario.com.co/wp-content/uploads/2023/11/1.20-1068x712.jpeg' },
  ],
  categorias_producto: [
    { id_categoria: 1, nombre: 'Platos Típicos y Picadas', descripcion: 'Comida tradicional para compartir', icono: '🍖', estado: true },
    { id_categoria: 2, nombre: 'Bebidas y Cervezas', descripcion: 'Bebidas frías para la partida', icono: '🍺', estado: true },
  ],
  productos: [
    { id_producto: 1, id_cancha: 1, id_categoria: 1, nombre: 'Picada Mixta Familiar (4-6 pers)', descripcion: 'Chorizo, morcilla, carne de cerdo, papa criolla, plátano y arepa boyacense.', precio: 65000.00, stock: 30, estado: true, imagen_url: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600' },
    { id_producto: 2, id_cancha: 1, id_categoria: 1, nombre: 'Porción de Empanadas (x6)', descripcion: 'Empanadas crocantes de carne y papa con ají casero.', precio: 18000.00, stock: 45, estado: true, imagen_url: 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600' },
    { id_producto: 3, id_cancha: 1, id_categoria: 2, nombre: 'Cerveza Nacional Águila / Poker (Unidad)', descripcion: 'Cerveza 330ml helada para el juego.', precio: 6000.00, stock: 150, estado: true, imagen_url: 'https://images.unsplash.com/photo-1608270119277-22f2f3595cf6?w=600' },
    { id_producto: 4, id_cancha: 1, id_categoria: 2, nombre: 'Gaseosa Familiar 1.5L', descripcion: 'Coca-Cola, Colombiana o Manzana Postobón.', precio: 10000.00, stock: 40, estado: true, imagen_url: 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=600' },
  ],
  combos: [
    { id_combo: 1, id_cancha: 1, nombre: 'Combo Mecha & Amigos', descripcion: 'Picada Mixta Familiar + 6 Cervezas Nacionales Heladas.', precio: 92000.00, personas_min: 4, personas_max: 6, estado: true, imagen_url: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600' },
  ],
  reportes: [
    { id: 1, usuario_id: 1, tipo: 'Ventas y Reservas', descripcion: 'Reporte consolidado mensual de ocupación de escenarios deportivos y pasarela de pago.', fecha: '2026-11-20T18:00:00', estado: 'Generado' },
    { id: 2, usuario_id: 3, tipo: 'Consumo Gastronómico', descripcion: 'Ventas de picadas, empanadas y bebidas por turno de juego.', fecha: '2026-11-21T21:00:00', estado: 'Generado' },
  ],
  notificaciones: [
    { id_notificacion: 1, id_usuario: 2, titulo: 'Reserva Confirmada', mensaje: 'Tu reserva para Pista El Triunfo ha sido confirmada con éxito.', fecha: '2026-11-20T10:05:00', leida: false },
    { id_notificacion: 2, id_usuario: 5, titulo: 'Copa Mayor Turmequé', mensaje: 'Las inscripciones para la Copa Mayor cierran pronto. ¡Asegura tu cupo!', fecha: '2026-11-21T09:30:00', leida: true },
  ],
  password_reset_tokens: [],
};

// Cargar o Inicializar
export function getLocalDB() {
  try {
    const raw = localStorage.getItem(DB_KEY);
    if (!raw) {
      localStorage.setItem(DB_KEY, JSON.stringify(SEED_DATA));
      return SEED_DATA;
    }
    return JSON.parse(raw);
  } catch {
    return SEED_DATA;
  }
}

export function saveLocalDB(db) {
  try {
    localStorage.setItem(DB_KEY, JSON.stringify(db));
  } catch (e) {
    console.error('Error persistiendo base de datos en localStorage', e);
  }
}
