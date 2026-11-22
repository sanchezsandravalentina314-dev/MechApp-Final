import api from '@/services/api';

export const authService = {
  /**
   * Registra un nuevo usuario en FastAPI / PostgreSQL.
   * @param {Object} data { id_rol, nombre, documento, correo, telefono, contrasena, captcha_token, acepta_tratamiento_datos }
   */
  async registro(data) {
    const response = await api.post('/auth/registro', data);
    return response.data;
  },

  /**
   * Inicia sesión con verificación de credenciales y token CAPTCHA.
   * @param {Object} data { correo, contrasena, captcha_token }
   */
  async login(data) {
    const response = await api.post('/auth/login', data);
    return response.data;
  },

  /**
   * Solicita el envío de un enlace temporal de un solo uso para recuperar contraseña.
   * @param {Object} data { correo, captcha_token }
   */
  async solicitarRecuperacion(data) {
    const response = await api.post('/auth/recuperar-contrasena', data);
    return response.data;
  },

  /**
   * Valida si un token de recuperación sigue vigente y sin usar.
   * @param {string} token
   */
  async validarTokenRecuperacion(token) {
    const response = await api.get(`/auth/validar-token-recuperacion?token=${encodeURIComponent(token)}`);
    return response.data;
  },

  /**
   * Restablece la contraseña usando el token seguro recibido por correo.
   * @param {Object} data { token, nueva_contrasena }
   */
  async restablecerContrasena(data) {
    const response = await api.post('/auth/restablecer-contrasena', data);
    return response.data;
  },

  /**
   * Permite al usuario autenticado cambiar su contraseña desde su perfil.
   * @param {Object} data { contrasena_actual, nueva_contrasena }
   */
  async cambiarContrasena(data) {
    const response = await api.put('/auth/cambiar-contrasena', data);
    return response.data;
  },

  /**
   * Verifica la validez de un token CAPTCHA en el backend.
   * @param {string} token
   */
  async verificarCaptcha(token) {
    const response = await api.post('/auth/verificar-captcha', { token });
    return response.data;
  },
};
