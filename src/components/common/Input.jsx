import React, { useState } from 'react';

export default function Input({
  label,
  id,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  helperText,
  icon,
  options = [], // Para select
  rows = 3,     // Para textarea
  className = '',
  allowTogglePassword = true,
  ...props
}) {
  const inputId = id || name;
  const isPasswordField = type === 'password';
  const [showPassword, setShowPassword] = useState(false);

  const effectiveType = isPasswordField && showPassword ? 'text' : type;

  return (
    <div className={`form-group ${className}`}>
      {label && (
        <label htmlFor={inputId}>
          {label} {required && <span style={{ color: 'var(--primary)' }}>*</span>}
        </label>
      )}

      {type === 'select' ? (
        <select
          id={inputId}
          name={name}
          value={value ?? ''}
          onChange={onChange}
          required={required}
          className={`form-control ${error ? 'is-invalid' : ''}`}
          {...props}
        >
          <option value="">Selecciona una opción...</option>
          {options.map((opt) => (
            <option
              key={typeof opt === 'object' ? opt.value : opt}
              value={typeof opt === 'object' ? opt.value : opt}
            >
              {typeof opt === 'object' ? opt.label : opt}
            </option>
          ))}
        </select>
      ) : type === 'textarea' ? (
        <textarea
          id={inputId}
          name={name}
          value={value ?? ''}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          rows={rows}
          className={`form-control ${error ? 'is-invalid' : ''}`}
          {...props}
        />
      ) : (
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          {icon && (
            <span
              style={{
                position: 'absolute',
                left: '12px',
                color: 'var(--text-dim)',
                display: 'flex',
                alignItems: 'center',
                pointerEvents: 'none',
                zIndex: 1,
              }}
            >
              {icon}
            </span>
          )}

          <input
            id={inputId}
            name={name}
            type={effectiveType}
            value={value ?? ''}
            onChange={onChange}
            placeholder={placeholder}
            required={required}
            className={`form-control ${error ? 'is-invalid' : ''}`}
            style={{
              paddingLeft: icon ? '38px' : undefined,
              paddingRight: isPasswordField && allowTogglePassword ? '44px' : undefined,
            }}
            {...props}
          />

          {isPasswordField && allowTogglePassword && (
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Ver contraseña'}
              style={{
                position: 'absolute',
                right: '10px',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '6px',
                transition: 'color 0.2s, background 0.2s',
              }}
              title={showPassword ? 'Ocultar contraseña' : 'Ver contraseña'}
            >
              {showPassword ? (
                // Icono ojo tachado
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
              ) : (
                // Icono ojo visible
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              )}
            </button>
          )}
        </div>
      )}

      {error && (
        <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: '0.8rem', marginTop: '4px' }}>
          {error}
        </p>
      )}
      {helperText && !error && (
        <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>
          {helperText}
        </p>
      )}
    </div>
  );
}
