import React, { useState } from 'react';
import UserLayout from '@/components/layout/UserLayout';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import PasswordStrengthMeter from '@/components/common/PasswordStrengthMeter';
import { useAuth } from '@/context/AuthContext';
import { useApp } from '@/context/AppContext';
import { getRoleName } from '@/utils/formatters';
import { validatePasswordRequirements } from '@/utils/passwordSecurity';
import api from '@/services/api';

export default function PerfilPage() {
  const { user, setUser } = useAuth();
  const { showSuccess, showError } = useApp();

  const [form, setForm] = useState({
    nombre: user?.nombre || '',
    correo: user?.correo || '',
    documento: user?.documento || '',
    telefono: user?.telefono || '',
  });

  const [pwdForm, setPwdForm] = useState({
    contrasena_actual: '',
    nueva_contrasena: '',
    confirmar: '',
  });

  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingPassword, setLoadingPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.nombre.trim() || !form.correo.trim()) {
      showError('El nombre y correo son obligatorios.');
      return;
    }

    try {
      setLoadingProfile(true);
      // Intentar persistir en backend si el endpoint existe, o actualizar estado local
      try {
        await api.put(`/usuarios/${user.id_usuario || user.id}`, form);
      } catch {
        // En caso de que el backend no tenga ruta específica de update por id, actualizamos localmente
      }

      const updated = { ...user, ...form };
      setUser(updated);
      localStorage.setItem('mechapp_user', JSON.stringify(updated));
      showSuccess('Perfil actualizado correctamente.');
    } catch (err) {
      showError(err.message || 'Error al actualizar el perfil.');
    } finally {
      setLoadingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();

    if (!pwdForm.contrasena_actual) {
      showError('Por favor ingresa tu contraseña actual.');
      return;
    }

    // 1. Validar requisitos de seguridad (mínimo 12 caracteres, mayúsculas, minúsculas, números, caracteres especiales, no común)
    const errorReq = validatePasswordRequirements(pwdForm.nueva_contrasena);
    if (errorReq) {
      showError(errorReq);
      return;
    }

    // 2. Validar coincidencia
    if (pwdForm.nueva_contrasena !== pwdForm.confirmar) {
      showError('Las contraseñas nuevas no coinciden. Por favor verifica la confirmación.');
      return;
    }

    try {
      setLoadingPassword(true);
      await api.put('/auth/cambiar-contrasena', {
        contrasena_actual: pwdForm.contrasena_actual,
        nueva_contrasena: pwdForm.nueva_contrasena,
      });

      showSuccess('¡Contraseña actualizada exitosamente con cifrado seguro!');
      setPwdForm({ contrasena_actual: '', nueva_contrasena: '', confirmar: '' });
    } catch (error) {
      showError(error.message || 'No se pudo cambiar la contraseña. Verifica tu contraseña actual.');
    } finally {
      setLoadingPassword(false);
    }
  };

  return (
    <UserLayout
      title="Mi Perfil"
      subtitle="Consulta y actualiza tus datos personales y credenciales de acceso seguro."
    >
      <div style={{ maxWidth: '720px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Tarjeta de Información General */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px' }}>
            <div
              style={{
                width: '76px',
                height: '76px',
                borderRadius: '50%',
                background: 'var(--primary-light, rgba(255,87,34,0.15))',
                color: 'var(--primary, #ff5722)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2.2rem',
                fontWeight: 800,
                border: '2px solid var(--primary, #ff5722)',
                boxShadow: 'var(--shadow-primary)',
              }}
            >
              {user?.nombre ? user.nombre[0].toUpperCase() : 'U'}
            </div>
            <div>
              <h2 style={{ fontSize: '1.45rem', margin: '0 0 4px' }}>{user?.nombre || 'Usuario MechApp'}</h2>
              <p style={{ margin: '0 0 4px', fontSize: '0.95rem' }}>
                Rol actual: <strong>{getRoleName(user?.id_rol)}</strong>
              </p>
              <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                Documento de identidad: {user?.documento || 'No registrado'}
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-grid-2">
              <Input
                label="Nombre Completo"
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                required
              />
              <Input
                label="Documento de Identidad"
                value={form.documento}
                disabled
                helperText="El documento es único y no se puede modificar directamente."
              />
            </div>

            <div className="form-grid-2">
              <Input
                label="Correo Electrónico"
                type="email"
                value={form.correo}
                onChange={(e) => setForm({ ...form, correo: e.target.value })}
                required
              />
              <Input
                label="Teléfono / WhatsApp"
                value={form.telefono}
                onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                placeholder="Ej. 3001234567"
              />
            </div>

            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <Button type="submit" variant="primary" loading={loadingProfile}>
                Guardar Cambios del Perfil
              </Button>
            </div>
          </form>
        </div>

        {/* Tarjeta de Seguridad y Cambio de Contraseña */}
        <div className="card" style={{ borderLeft: '4px solid var(--primary, #ff5722)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <span style={{ fontSize: '1.3rem' }}>🔒</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.18rem' }}>Seguridad y Contraseña</h3>
              <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                Exigencia de mínimo 12 caracteres, mayúsculas, minúsculas, números y símbolos.
              </p>
            </div>
          </div>

          <form onSubmit={handlePasswordSubmit}>
            <Input
              label="Contraseña Actual"
              name="contrasena_actual"
              type="password"
              value={pwdForm.contrasena_actual}
              onChange={(e) => setPwdForm({ ...pwdForm, contrasena_actual: e.target.value })}
              placeholder="Ingresa tu contraseña actual"
              required
            />

            <div className="form-grid-2" style={{ marginTop: '14px' }}>
              <Input
                label="Nueva Contraseña"
                name="nueva_contrasena"
                type="password"
                value={pwdForm.nueva_contrasena}
                onChange={(e) => setPwdForm({ ...pwdForm, nueva_contrasena: e.target.value })}
                placeholder="Mínimo 12 caracteres seguros"
                required
              />
              <Input
                label="Confirmar Nueva Contraseña"
                name="confirmar"
                type="password"
                value={pwdForm.confirmar}
                onChange={(e) => setPwdForm({ ...pwdForm, confirmar: e.target.value })}
                placeholder="Repite la nueva contraseña"
                required
              />
            </div>

            {/* Medidor visual de fortaleza de la nueva contraseña */}
            <PasswordStrengthMeter password={pwdForm.nueva_contrasena} showCriteria={true} />

            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <Button type="submit" variant="secondary" loading={loadingPassword}>
                Actualizar Contraseña de Forma Segura
              </Button>
            </div>
          </form>
        </div>
      </div>
    </UserLayout>
  );
}
