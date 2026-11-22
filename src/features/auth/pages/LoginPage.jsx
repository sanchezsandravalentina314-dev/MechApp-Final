import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useApp } from '@/context/AppContext';
import { authService } from '@/features/auth/services/authService';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import CaptchaWidget from '@/components/common/CaptchaWidget';
import {
  checkAccountLockout,
  recordFailedAttempt,
  clearFailedAttempts,
} from '@/utils/passwordSecurity';

export default function LoginPage() {
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [loading, setLoading] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const [captchaError, setCaptchaError] = useState('');

  // Control de bloqueo contra intentos repetidos (Rate Limiting / Lockout)
  const [lockoutStatus, setLockoutStatus] = useState({ locked: false, remainingAttempts: 5, minutesRemaining: 0 });

  // Estado modal recuperación de contraseña
  const [showRecovery, setShowRecovery] = useState(false);
  const [correoRecuperacion, setCorreoRecuperacion] = useState('');
  const [loadingRecovery, setLoadingRecovery] = useState(false);
  const [recoveryEnviado, setRecoveryEnviado] = useState(false);
  const [recoveryCaptchaToken, setRecoveryCaptchaToken] = useState(null);
  const [recoveryCaptchaError, setRecoveryCaptchaError] = useState('');
  const [recoveryLinkGenerado, setRecoveryLinkGenerado] = useState('');

  const { login } = useAuth();
  const { showSuccess, showError, showWarning } = useApp();
  const navigate = useNavigate();

  // Verificar estado de bloqueo al cambiar de correo
  useEffect(() => {
    if (correo.trim()) {
      const status = checkAccountLockout(correo);
      setLockoutStatus(status);
    }
  }, [correo]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!correo.trim() || !contrasena) {
      showError('Por favor ingresa tu correo y contraseña.');
      return;
    }

    // 1. Validar bloqueo por intentos repetidos
    const currentLockout = checkAccountLockout(correo);
    if (currentLockout.locked) {
      setLockoutStatus(currentLockout);
      showError(
        `Acceso bloqueado por seguridad: has superado los 5 intentos fallidos. Por favor espera ${currentLockout.minutesRemaining} minuto(s).`
      );
      return;
    }

    // 2. Validar respuesta de CAPTCHA obligatoria
    if (!captchaToken) {
      setCaptchaError('Por favor completa la verificación de seguridad "No soy un robot".');
      showError('Debes validar el CAPTCHA antes de continuar.');
      return;
    }
    setCaptchaError('');

    try {
      setLoading(true);
      const user = await login(correo.trim(), contrasena, captchaToken);
      
      // Limpiar intentos fallidos tras login exitoso
      clearFailedAttempts(correo);
      setLockoutStatus({ locked: false, remainingAttempts: 5, minutesRemaining: 0 });

      showSuccess(`¡Bienvenido de nuevo, ${user.nombre}!`);
      const userRoleId = Number(user.id_rol);
      if (userRoleId === 1) {
        navigate('/admin/dashboard');
      } else if (userRoleId === 3) {
        navigate('/propietario/panel');
      } else {
        navigate('/user/canchas');
      }
    } catch (err) {
      // Registrar intento fallido
      const updatedStatus = recordFailedAttempt(correo);
      setLockoutStatus(updatedStatus);

      if (updatedStatus.locked) {
        showError(
          `¡Alerta de seguridad! Cuenta bloqueada por 15 minutos debido a 5 intentos fallidos.`
        );
      } else {
        showWarning(
          `Credenciales inválidas. Te quedan ${updatedStatus.remainingAttempts} intento(s) antes del bloqueo temporal.`
        );
      }
      setCaptchaToken(null); // Obligar a reverificar en próximo intento
    } finally {
      setLoading(false);
    }
  };

  const handleRecuperacion = async (e) => {
    e.preventDefault();
    if (!correoRecuperacion.trim()) {
      showError('Por favor ingresa tu correo electrónico.');
      return;
    }

    if (!recoveryCaptchaToken) {
      setRecoveryCaptchaError('Debes completar la verificación de seguridad para solicitar la recuperación.');
      return;
    }
    setRecoveryCaptchaError('');

    try {
      setLoadingRecovery(true);
      const res = await authService.solicitarRecuperacion({
        correo: correoRecuperacion.trim(),
        captcha_token: recoveryCaptchaToken,
      });

      setRecoveryEnviado(true);
      if (res?.enlace_recuperacion) {
        setRecoveryLinkGenerado(res.enlace_recuperacion);
      }
      showSuccess('Solicitud procesada con éxito.');
    } catch (err) {
      showError(err.message || 'Error al procesar la solicitud de recuperación.');
    } finally {
      setLoadingRecovery(false);
    }
  };

  const cerrarModal = () => {
    setShowRecovery(false);
    setCorreoRecuperacion('');
    setRecoveryEnviado(false);
    setRecoveryCaptchaToken(null);
    setRecoveryCaptchaError('');
    setRecoveryLinkGenerado('');
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card" style={{ maxWidth: '480px' }}>
        <div className="auth-header">
          <Link to="/">
            <img src="/logo.jpeg" alt="Logo MechApp" className="auth-logo" />
          </Link>
          <h1>Iniciar Sesión</h1>
          <p>Ingresa tus credenciales para acceder a MechApp</p>
        </div>

        {/* Alerta de bloqueo por intentos repetidos */}
        {lockoutStatus.locked && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid var(--color-danger, #ef4444)',
              borderRadius: '10px',
              padding: '14px',
              marginBottom: '18px',
              color: 'var(--color-danger, #ef4444)',
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
            }}
          >
            <span style={{ fontSize: '1.2rem', lineHeight: 1 }}>⏳</span>
            <div>
              <strong>Acceso bloqueado temporalmente</strong>
              <p style={{ margin: '4px 0 0', fontSize: '0.82rem', color: 'var(--text-main)' }}>
                Se detectaron múltiples intentos fallidos de acceso. Como medida de seguridad, el acceso está suspendido por <strong>{lockoutStatus.minutesRemaining} minuto(s)</strong>.
              </p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <Input
            label="Correo Electrónico"
            name="correo"
            type="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            placeholder="ejemplo@correo.com"
            required
            disabled={lockoutStatus.locked}
          />

          <Input
            label="Contraseña"
            name="contrasena"
            type="password"
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            placeholder="Tu contraseña secreta"
            required
            disabled={lockoutStatus.locked}
          />

          <div style={{ textAlign: 'right', marginTop: '2px', marginBottom: '8px' }}>
            <button
              type="button"
              onClick={() => setShowRecovery(true)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary, #ff5722)',
                fontSize: '0.85rem',
                cursor: 'pointer',
                textDecoration: 'underline',
                padding: 0,
                fontWeight: 500,
              }}
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>

          {/* Widget CAPTCHA oficial "No soy un robot" */}
          <CaptchaWidget
            onVerify={(token) => {
              setCaptchaToken(token);
              setCaptchaError('');
            }}
            onExpire={() => {
              setCaptchaToken(null);
            }}
            error={captchaError}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            disabled={lockoutStatus.locked}
            style={{ width: '100%', marginTop: '8px' }}
          >
            {lockoutStatus.locked ? 'Acceso Bloqueado Temporalmente' : 'Ingresar a MechApp'}
          </Button>
        </form>

        <div className="auth-footer">
          <p>
            ¿Aún no tienes cuenta?{' '}
            <Link to="/registro" style={{ fontWeight: 600 }}>
              Regístrate aquí
            </Link>
          </p>
          <p style={{ marginTop: '10px' }}>
            <Link to="/" style={{ color: 'var(--text-dim)' }}>
              ← Volver al inicio
            </Link>
          </p>
        </div>
      </div>

      {/* Modal de Recuperación de Contraseña */}
      {showRecovery && (
        <div
          onClick={cerrarModal}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '16px',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'var(--bg-surface, #111625)',
              borderRadius: '16px',
              padding: '32px',
              width: '100%',
              maxWidth: '460px',
              boxShadow: 'var(--shadow-lg, 0 20px 60px rgba(0,0,0,0.5))',
              border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.4rem' }}>🔐</span>
                <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Recuperar Contraseña</h2>
              </div>
              <button
                onClick={cerrarModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.3rem',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  lineHeight: 1,
                }}
              >
                ✕
              </button>
            </div>

            {recoveryEnviado ? (
              <div style={{ textAlign: 'center', padding: '12px 0' }}>
                <div
                  style={{
                    width: '60px',
                    height: '60px',
                    margin: '0 auto 16px',
                    borderRadius: '50%',
                    background: 'rgba(16, 185, 129, 0.15)',
                    color: 'var(--color-success, #10b981)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '2rem',
                  }}
                >
                  ✓
                </div>
                <h3 style={{ fontWeight: 600, fontSize: '1.15rem', marginBottom: '8px' }}>
                  Solicitud procesada
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                  Si la dirección <strong>{correoRecuperacion}</strong> corresponde a una cuenta registrada en MechApp, recibirás un enlace de un solo uso con validez de 30 minutos para restablecer tu contraseña.
                </p>
                <p style={{ color: 'var(--text-dim)', fontSize: '0.82rem', marginTop: '8px' }}>
                  Por seguridad, no revelamos si un correo existe o no en nuestra base de datos. Recuerda revisar la bandeja de entrada y la carpeta de spam.
                </p>

                {/* Enlace directo para entorno de pruebas/desarrollo */}
                {recoveryLinkGenerado && (
                  <div
                    style={{
                      margin: '18px 0',
                      padding: '12px',
                      background: 'var(--bg-input, #1a2238)',
                      borderRadius: '8px',
                      border: '1px solid var(--border-color)',
                      textAlign: 'left',
                    }}
                  >
                    <span style={{ fontSize: '0.75rem', color: 'var(--primary, #ff5722)', fontWeight: 600 }}>
                      [Entorno de Pruebas] Enlace generado:
                    </span>
                    <a
                      href={recoveryLinkGenerado}
                      style={{
                        display: 'block',
                        fontSize: '0.8rem',
                        color: 'var(--text-main)',
                        textDecoration: 'underline',
                        wordBreak: 'break-all',
                        marginTop: '4px',
                      }}
                      onClick={cerrarModal}
                    >
                      {recoveryLinkGenerado}
                    </a>
                  </div>
                )}

                <Button
                  onClick={cerrarModal}
                  variant="primary"
                  style={{ marginTop: '16px', width: '100%' }}
                >
                  Entendido y Volver
                </Button>
              </div>
            ) : (
              <form onSubmit={handleRecuperacion}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '18px', lineHeight: 1.5 }}>
                  Ingresa tu correo electrónico registrado. Se enviará un enlace temporal seguro para crear una nueva contraseña.
                </p>

                <Input
                  label="Correo Electrónico Registrado"
                  name="correo_recuperacion"
                  type="email"
                  value={correoRecuperacion}
                  onChange={(e) => setCorreoRecuperacion(e.target.value)}
                  placeholder="ejemplo@correo.com"
                  required
                />

                {/* CAPTCHA de recuperación */}
                <CaptchaWidget
                  onVerify={(token) => {
                    setRecoveryCaptchaToken(token);
                    setRecoveryCaptchaError('');
                  }}
                  onExpire={() => setRecoveryCaptchaToken(null)}
                  error={recoveryCaptchaError}
                />

                <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={cerrarModal}
                    style={{ flex: 1 }}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={loadingRecovery}
                    style={{ flex: 2 }}
                  >
                    Enviar Enlace Seguro
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
