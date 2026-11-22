import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useApp } from '@/context/AppContext';
import { authService } from '@/features/auth/services/authService';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import PasswordStrengthMeter from '@/components/common/PasswordStrengthMeter';
import { validatePasswordRequirements } from '@/utils/passwordSecurity';

export default function RestablecerContrasenaPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';

  const [nuevaContrasena, setNuevaContrasena] = useState('');
  const [confirmarContrasena, setConfirmarContrasena] = useState('');
  const [loading, setLoading] = useState(false);
  const [exito, setExito] = useState(false);

  const { showSuccess, showError } = useApp();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!token) {
      showError('El enlace de recuperación no es válido o ha expirado. Por favor solicita uno nuevo.');
      return;
    }

    // 1. Validación de requisitos de seguridad de contraseña (mínimo 12 caracteres, mayúsculas, minúsculas, números, símbolos, no común)
    const errorReq = validatePasswordRequirements(nuevaContrasena);
    if (errorReq) {
      showError(errorReq);
      return;
    }

    // 2. Validación de coincidencia
    if (nuevaContrasena !== confirmarContrasena) {
      showError('Las contraseñas no coinciden. Por favor verifica la confirmación.');
      return;
    }

    try {
      setLoading(true);
      await authService.restablecerContrasena({
        token,
        nueva_contrasena: nuevaContrasena,
      });

      showSuccess('¡Tu contraseña ha sido actualizada con éxito y cifrada de forma segura!');
      setExito(true);
      setTimeout(() => navigate('/login'), 2200);
    } catch (err) {
      showError(err.message || 'El enlace de recuperación ha expirado o ya fue utilizado. Solicita uno nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card" style={{ maxWidth: '480px' }}>
        <div className="auth-header">
          <Link to="/">
            <img src="/logo.jpeg" alt="Logo MechApp" className="auth-logo" />
          </Link>
          <h1>Restablecer Contraseña</h1>
          <p>Establece una nueva contraseña segura para tu cuenta</p>
        </div>

        {exito ? (
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <div
              style={{
                width: '64px',
                height: '64px',
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
            <h3 style={{ color: 'var(--color-success, #10b981)', fontWeight: 700, fontSize: '1.2rem', marginBottom: '8px' }}>
              ¡Contraseña Actualizada!
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>
              Tu contraseña fue modificada exitosamente. Redirigiendo a la pantalla de inicio de sesión...
            </p>
            <div style={{ marginTop: '20px' }}>
              <Link to="/login">
                <Button variant="primary">Ir a Iniciar Sesión</Button>
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {!token && (
              <div
                style={{
                  background: 'rgba(239, 68, 68, 0.12)',
                  border: '1px solid var(--color-danger, #ef4444)',
                  borderRadius: '8px',
                  padding: '12px 14px',
                  color: 'var(--color-danger, #ef4444)',
                  fontSize: '0.86rem',
                  marginBottom: '16px',
                }}
              >
                ⚠️ No se proporcionó un token de recuperación. Por favor accede a través del enlace enviado a tu correo o solicita uno nuevo.
              </div>
            )}

            <Input
              label="Nueva Contraseña"
              name="nueva_contrasena"
              type="password"
              value={nuevaContrasena}
              onChange={(e) => setNuevaContrasena(e.target.value)}
              placeholder="Mínimo 12 caracteres"
              required
              disabled={!token}
            />

            <Input
              label="Confirmar Nueva Contraseña"
              name="confirmar_contrasena"
              type="password"
              value={confirmarContrasena}
              onChange={(e) => setConfirmarContrasena(e.target.value)}
              placeholder="Repite tu nueva contraseña"
              required
              disabled={!token}
            />

            {/* Medidor visual de fortaleza con checklist interactivo */}
            <PasswordStrengthMeter password={nuevaContrasena} showCriteria={true} />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              disabled={!token}
              style={{ width: '100%', marginTop: '12px' }}
            >
              Guardar Nueva Contraseña
            </Button>
          </form>
        )}

        <div className="auth-footer">
          <p>
            <Link to="/login" style={{ fontWeight: 600 }}>
              ← Volver al inicio de sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
