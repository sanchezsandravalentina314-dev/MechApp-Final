import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useApp } from '@/context/AppContext';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import PasswordStrengthMeter from '@/components/common/PasswordStrengthMeter';
import CaptchaWidget from '@/components/common/CaptchaWidget';
import { isValidEmail, isValidDocument } from '@/utils/validators';
import { validatePasswordRequirements } from '@/utils/passwordSecurity';

export default function RegisterPage() {
  const [form, setForm] = useState({
    nombre: '',
    documento: '',
    correo: '',
    telefono: '',
    id_rol: '2', // Por defecto 2 = Jugador / Deportista
    contrasena: '',
    confirmarContrasena: '',
  });

  const [loading, setLoading] = useState(false);
  const [aceptaTratamiento, setAceptaTratamiento] = useState(false);
  const [showPolicyModal, setShowPolicyModal] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const [captchaError, setCaptchaError] = useState('');

  const { registro } = useAuth();
  const { showSuccess, showError } = useApp();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.nombre.trim() || !form.documento.trim() || !form.correo.trim() || !form.contrasena) {
      showError('Por favor completa todos los campos obligatorios.');
      return;
    }

    if (!isValidDocument(form.documento)) {
      showError('Por favor ingresa un número de documento válido (mínimo 5 caracteres numéricos o alfanuméricos).');
      return;
    }

    if (!isValidEmail(form.correo)) {
      showError('Por favor ingresa un correo electrónico válido.');
      return;
    }

    // 1. Validación estricta de seguridad de contraseña (mínimo 12 caracteres, mayúsculas, minúsculas, números, símbolos, no común)
    const passwordError = validatePasswordRequirements(form.contrasena);
    if (passwordError) {
      showError(passwordError);
      return;
    }

    // 2. Validación de coincidencia de confirmación
    if (form.contrasena !== form.confirmarContrasena) {
      showError('Las contraseñas no coinciden. Por favor verifica la confirmación.');
      return;
    }

    // 3. Validación de autorización de tratamiento de datos personales
    if (!aceptaTratamiento) {
      showError('Debes autorizar el tratamiento de tus datos personales para registrarte.');
      return;
    }

    // 4. Verificación obligatoria de CAPTCHA "No soy un robot"
    if (!captchaToken) {
      setCaptchaError('Por favor completa la verificación de seguridad "No soy un robot".');
      showError('Debes resolver el CAPTCHA para crear tu cuenta.');
      return;
    }
    setCaptchaError('');

    // Prevenir inyección de rol de administrador (Rol 1) en registro público
    let rolSeleccionado = Number(form.id_rol);
    if (rolSeleccionado === 1) {
      rolSeleccionado = 2;
    }

    try {
      setLoading(true);
      const payload = {
        id_rol: rolSeleccionado,
        nombre: form.nombre.trim(),
        documento: form.documento.trim(),
        correo: form.correo.trim().toLowerCase(),
        telefono: form.telefono.trim() || null,
        contrasena: form.contrasena,
        captcha_token: captchaToken,
        acepta_tratamiento_datos: aceptaTratamiento,
      };

      const user = await registro(payload);
      showSuccess(`¡Cuenta creada con éxito! Bienvenido a MechApp, ${user.nombre}.`);
      
      const userRoleId = Number(user.id_rol);
      if (userRoleId === 1) {
        navigate('/admin/dashboard');
      } else if (userRoleId === 3) {
        navigate('/propietario/panel');
      } else {
        navigate('/user/canchas');
      }
    } catch (err) {
      showError(err.message || 'Error al registrar la cuenta. Verifica los datos.');
      setCaptchaToken(null); // Requiere reverificación ante error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card" style={{ maxWidth: '580px' }}>
        <div className="auth-header">
          <Link to="/">
            <img src="/logo.jpeg" alt="Logo MechApp" className="auth-logo" />
          </Link>
          <h1>Crear Cuenta en MechApp</h1>
          <p>Únete a la plataforma digital del tejo colombiano</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid-2">
            <Input
              label="Nombre Completo"
              name="nombre"
              value={form.nombre}
              onChange={handleChange}
              placeholder="Ej. Geraldine Rico"
              required
            />
            <Input
              label="Documento (Cédula/ID)"
              name="documento"
              value={form.documento}
              onChange={handleChange}
              placeholder="Ej. 1015404883"
              required
            />
          </div>

          <div className="form-grid-2">
            <Input
              label="Correo Electrónico"
              name="correo"
              type="email"
              value={form.correo}
              onChange={handleChange}
              placeholder="correo@ejemplo.com"
              required
            />
            <Input
              label="Teléfono / Celular"
              name="telefono"
              type="tel"
              value={form.telefono}
              onChange={handleChange}
              placeholder="Ej. 3101234567"
            />
          </div>

          {/* Selector de Rol: Jugador o Propietario */}
          <Input
            label="Tipo de Usuario / Rol"
            name="id_rol"
            type="select"
            value={form.id_rol}
            onChange={handleChange}
            required
            options={[
              { value: '2', label: 'Jugador / Deportista de Tejo' },
              { value: '3', label: 'Propietario / Administrador de Canchas' },
            ]}
          />

          {/* Campos de Contraseña con soporte para mostrar/ocultar */}
          <div className="form-grid-2">
            <Input
              label="Contraseña"
              name="contrasena"
              type="password"
              value={form.contrasena}
              onChange={handleChange}
              placeholder="Mínimo 12 caracteres seguros"
              required
            />
            <Input
              label="Confirmar Contraseña"
              name="confirmarContrasena"
              type="password"
              value={form.confirmarContrasena}
              onChange={handleChange}
              placeholder="Repite exactamente la contraseña"
              required
            />
          </div>

          {/* Indicador visual de seguridad de la contraseña con criterios interactivos */}
          <PasswordStrengthMeter password={form.contrasena} showCriteria={true} />

          {/* Verificación CAPTCHA "No soy un robot" */}
          <CaptchaWidget
            onVerify={(token) => {
              setCaptchaToken(token);
              setCaptchaError('');
            }}
            onExpire={() => setCaptchaToken(null)}
            error={captchaError}
          />

          {/* Casilla independiente para Tratamiento de Datos Personales */}
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              margin: '18px 0 22px',
              padding: '12px 14px',
              background: 'var(--bg-input, #1a2238)',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
            }}
          >
            <input
              type="checkbox"
              id="aceptaTratamiento"
              checked={aceptaTratamiento}
              onChange={(e) => setAceptaTratamiento(e.target.checked)}
              style={{ marginTop: '3px', cursor: 'pointer', width: '16px', height: '16px' }}
            />
            <label htmlFor="aceptaTratamiento" style={{ fontSize: '0.84rem', lineHeight: 1.45, cursor: 'pointer', color: 'var(--text-muted)' }}>
              Autorizo el tratamiento de mis datos personales de acuerdo con la{' '}
              <button
                type="button"
                onClick={() => setShowPolicyModal(true)}
                style={{
                  textDecoration: 'underline',
                  color: 'var(--primary, #ff5722)',
                  fontWeight: 600,
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  cursor: 'pointer',
                }}
              >
                Política de Tratamiento de Datos Personales
              </button>{' '}
              de MechApp.
            </label>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            style={{ width: '100%' }}
          >
            Registrarse e Iniciar Sesión
          </Button>
        </form>

        <div className="auth-footer">
          <p>
            ¿Ya tienes una cuenta?{' '}
            <Link to="/login" style={{ fontWeight: 600 }}>
              Inicia sesión aquí
            </Link>
          </p>
          <p style={{ marginTop: '10px' }}>
            <Link to="/" style={{ color: 'var(--text-dim)' }}>
              ← Volver al inicio
            </Link>
          </p>
        </div>
      </div>

      {/* Modal de Política de Tratamiento de Datos Personales */}
      {showPolicyModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '16px',
          }}
          onClick={() => setShowPolicyModal(false)}
        >
          <div
            style={{
              background: 'var(--bg-surface, #161d30)',
              color: 'var(--text-main, #fff)',
              maxWidth: '620px',
              width: '100%',
              maxHeight: '85vh',
              overflowY: 'auto',
              borderRadius: '16px',
              padding: '28px',
              boxShadow: 'var(--shadow-lg)',
              border: '1px solid var(--border-color)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Política de Tratamiento de Datos Personales</h2>
              <button
                type="button"
                onClick={() => setShowPolicyModal(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ fontSize: '0.88rem', lineHeight: 1.6, color: 'var(--text-muted)' }}>
              <h4 style={{ color: 'var(--text-main)', marginTop: '14px', marginBottom: '4px' }}>1. ¿Qué datos recopilamos?</h4>
              <p>Nombre, documento de identidad, correo electrónico, teléfono, datos de reservas, torneos inscritos y contraseñas cifradas con algoritmos de alta seguridad (Argon2id).</p>

              <h4 style={{ color: 'var(--text-main)', marginTop: '14px', marginBottom: '4px' }}>2. ¿Para qué los usamos?</h4>
              <p>Para la administración de cuentas, gestión de reservas en canchas, confirmación de torneos y equipos, prevención de fraudes y cumplimiento legal según la Ley 1581 de 2012.</p>

              <h4 style={{ color: 'var(--text-main)', marginTop: '14px', marginBottom: '4px' }}>3. Seguridad y Almacenamiento</h4>
              <p>Las contraseñas nunca se almacenan en texto plano y se aplican controles de limitación de solicitudes y bloqueo contra ataques automatizados.</p>

              <h4 style={{ color: 'var(--text-main)', marginTop: '14px', marginBottom: '4px' }}>4. Derechos del Titular</h4>
              <p>Puedes conocer, actualizar, rectificar o solicitar la supresión de tus datos en cualquier momento desde tu perfil o mediante nuestros canales de atención.</p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
              <Button type="button" variant="primary" onClick={() => setShowPolicyModal(false)}>
                Entendido y Cerrar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
