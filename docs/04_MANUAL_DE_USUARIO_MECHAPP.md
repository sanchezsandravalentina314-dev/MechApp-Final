# MANUAL DE USUARIO DEL SISTEMA - MECHAPP
**Plataforma Digital Integral para la Gestión del Tejo Colombiano**

---

### INFORMACIÓN GENERAL
- **Sistema:** MechApp (Web & Mobile Responsive)
- **Programa de Formación:** ADSO - SENA | Ficha: 3407178
- **Autoras:** Sandra Valentina Sánchez, Geraldine Juliana Rico
- **Instructor:** Daniel López
- **Versión:** 2.0
- **Fecha:** Noviembre de 2026

---

## 1. BIENVENIDA E INTRODUCCIÓN

¡Bienvenido a **MechApp**! Esta aplicación web ha sido diseñada para revolucionar la forma en que los apasionados del tejo (deporte nacional de Colombia) reservan sus canchas, organizan partidas con amigos, disfrutan de combos y bebidas tradicionales, y participan en torneos competitivos.

Este manual te guiará paso a paso en el uso de la plataforma según tu rol:
- **Jugador / Cliente:** Amante del tejo que busca canchas, agenda horarios, compra combos y compite.
- **Propietario de Cancha:** Dueño o administrador de un club de tejo que gestiona sus pistas, tarifas y ventas.
- **Administrador General:** Supervisor general de la plataforma y de los torneos oficiales.

---

## 2. ACCESO Y SEGURIDAD (TODOS LOS USUARIOS)

### 2.1 Registro de Cuenta
1. Ingresa a la página principal de MechApp y haz clic en el botón superior **"Registrarse"** o navega a `/registro`.
2. Diligencia el formulario con tus datos:
   - **Nombre completo** (ej. Sandra Sánchez).
   - **Número de Documento** (cédula o documento de identidad).
   - **Correo electrónico** (debe ser un correo válido y único).
   - **Teléfono de contacto** (celular para confirmaciones).
   - **Contraseña segura** (mínimo 6 caracteres).
   - **Rol:** Selecciona *Jugador* (para reservar y jugar) o *Propietario de Cancha* (para publicar tu club).
3. Haz clic en **"Crear Cuenta"**. El sistema validará tus datos, registrará tu perfil con contraseña encriptada y te dará la bienvenida inmediatamente.

### 2.2 Inicio de Sesión (Login)
1. Haz clic en **"Iniciar Sesión"** o ve a `/login`.
2. Ingresa tu correo y contraseña registrados.
3. Haz clic en **"Entrar a MechApp"**. El sistema generará tu credencial de sesión segura (JWT) y te redirigirá a tu panel correspondiente.

### 2.3 ¿Olvidaste tu Contraseña?
1. En la pantalla de login, haz clic en **"¿Olvidaste tu contraseña?"** (`/restablecer-contrasena`).
2. Digita tu correo electrónico registrado y presiona **"Enviar Enlace"**.
3. Recibirás un mensaje en tu bandeja de entrada asistido por la pasarela de correo con un enlace temporal válido por 30 minutos.
4. Ingresa tu nueva contraseña y confírmala para recuperar tu acceso.

---

## 3. MANUAL DEL JUGADOR / CLIENTE

### 3.1 Exploración y Búsqueda de Canchas
1. Dirígete a la sección **"Canchas"** (`/user/canchas`).
2. En la barra superior puedes:
   - **Buscar por texto:** Escribe el nombre del club, barrio o dirección.
   - **Filtrar por ciudad:** Selecciona Bogotá, Tunja, Medellín, Cali, etc.
3. Cada tarjeta de cancha te muestra:
   - Fotografía del escenario deportivo.
   - Tarifa por hora en Pesos Colombianos ($ COP).
   - Capacidad máxima de jugadores.
   - Calificación promedio en estrellas ⭐.
   - Botón **"🗺️ Mapa"**: Abre la ubicación exacta directamente en Google Maps.

### 3.2 Cómo Hacer una Reserva de Cancha
1. En la cancha de tu preferencia, presiona el botón **"Reservar Cancha"**.
2. Selecciona la **Fecha** en el calendario. El sistema consultará automáticamente qué horarios ya están ocupados para evitar cruces.
3. Selecciona la **Hora de Inicio** y la **Hora de Fin** (ej. 18:00 a 20:00).
4. Haz clic en **"Continuar al Pago"**.

### 3.3 Pasarela de Pago y Comprobante Digital
1. Se abrirá la **Pasarela de Pago Segura de MechApp** mostrando el resumen de tu alquiler.
2. Selecciona tu método de pago simulado:
   - **Tarjeta de Crédito / Débito** (ingresa número, titular, vencimiento y CVC).
   - **PSE** (selecciona tu banco).
   - **Nequi / Daviplata** (ingresa tu número de celular).
3. Haz clic en **"Pagar Ahora"**.
4. **¡EXPLOSIÓN DE MECHA! 🎯💥:** 
   Al confirmarse la transacción, la pantalla disparará una espectacular animación con chispas de pólvora, el bocín metálico y el sonido característico del tejo celebrando tu jugada: **"¡¡MECHAAAAA!! ¡Reserva confirmada con éxito!"**.
5. Recibirás tu **Comprobante Digital** con código de referencia único (`TXN-000XXX`), valor y detalles, el cual puedes imprimir o consultar siempre en **"Mis Reservas"**.

### 3.4 Pedidos de Bebidas y Combos (Carta de Consumo)
¿Quieres polas frías o una picada lista cuando llegues a la cancha?
1. Ve a la pestaña **"Consumo / Combos"** (`/user/consumo`).
2. Explora las pestañas: *Combos del Parche*, *Cervezas*, *Comidas Típicas*, *Bebidas*.
3. Haz clic en **"Añadir al Carrito"**. Cada vez que añadas un producto, una chispa explosiva confirmará tu elección.
4. En el panel lateral derecho verás tu **Carrito de Pedido**:
   - Ajusta las cantidades con los botones `+` y `-`.
   - Si tienes una reserva activa, el pedido se vinculará a tu pista para que el encargado te lo lleve directamente.
5. Presiona **"Confirmar Pedido de Consumo"** y realiza el pago. ¡Nuevamente la mecha estallará confirmando tu orden!

### 3.5 Inscripción a Torneos
1. Ingresa a **"Torneos"** (`/user/torneos`).
2. Consulta los campeonatos abiertos, fechas, sedes y premios en efectivo.
3. Haz clic en **"Inscribirme"** para registrar tu equipo y disputar el trofeo.

---

## 4. MANUAL DEL PROPIETARIO DE CANCHA

### 4.1 Panel de Control del Club
Al iniciar sesión con tu cuenta de Propietario, tendrás acceso a la barra de gestión exclusiva:
- **Mis Canchas:** Da de alta nuevas pistas de tejo, define si son de tejo largo o minitejo, fija el valor por hora y la capacidad.
- **Disponibilidad:** Configura qué días y horas está abierto tu establecimiento y bloquea pistas cuando requieran mantenimiento de greda o cambio de bocines.
- **Administración de Consumo:** Agrega tus cervezas, gaseosas, picadas y crea promociones (ej. *6 cervezas + 2 horas de juego con descuento*).

---

## 5. MANUAL DEL ADMINISTRADOR GENERAL

### 5.1 Dashboard y Estadísticas del Sistema
En `/admin/dashboard`, el administrador visualiza en tiempo real:
- Total de ingresos recaudados por concepto de reservas y consumos.
- Gráficas de ocupación de pistas y horarios de mayor demanda.
- Número total de usuarios activos y canchas afiliadas.

### 5.2 Gestión de Usuarios y Roles
- Permite promover usuarios a administradores o propietarios.
- Desactivación preventiva de usuarios en caso de incumplimiento de normas.

### 5.3 Gestión de Torneos y Marcadores
- Creación de fechas y cruces de partidas.
- Registro de puntuación tradicional: mecha (3 pts), embocinada (6 pts), moñona (9 pts) y figura.

---

## 6. PREGUNTAS FRECUENTES (FAQ)

- **¿Qué pasa si intento reservar una cancha que ya está ocupada?**
  El sistema valida al segundo la disponibilidad. Si intentas agendar un horario traslapado, el sistema te avisará con una alerta y no permitirá la colisión.
- **¿Puedo cancelar una reserva?**
  Sí, dirigiéndote a *Mis Reservas* y presionando *Cancelar*, siempre y cuando se realice con anterioridad a la fecha programada.
- **¿Cómo escucho el sonido de la mecha?**
  El sonido se sintetiza automáticamente en cualquier navegador moderno sin necesidad de descargas adicionales.