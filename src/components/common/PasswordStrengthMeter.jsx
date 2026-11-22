import React from 'react';
import { evaluatePassword } from '@/utils/passwordSecurity';

export default function PasswordStrengthMeter({ password = '', showCriteria = true }) {
  if (!password) return null;

  const evaluation = evaluatePassword(password);
  const { score, level, color, criteria } = evaluation;

  return (
    <div className="password-strength-container" style={{ marginTop: '8px', marginBottom: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
          Seguridad de la contraseña:
        </span>
        <span
          style={{
            fontSize: '0.78rem',
            fontWeight: 700,
            color: color,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {level} ({score}%)
        </span>
      </div>

      {/* Barra de progreso visual con gradiente dinámico */}
      <div
        style={{
          width: '100%',
          height: '6px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '999px',
          overflow: 'hidden',
          marginBottom: showCriteria ? '10px' : '4px',
        }}
      >
        <div
          style={{
            width: `${score}%`,
            height: '100%',
            background: color,
            transition: 'width 0.3s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease',
            borderRadius: '999px',
          }}
        />
      </div>

      {/* Lista de chequeo interactiva */}
      {showCriteria && (
        <ul
          style={{
            listStyle: 'none',
            padding: 0,
            margin: 0,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '6px',
            fontSize: '0.75rem',
          }}
        >
          {criteria.map((item) => (
            <li
              key={item.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: item.passed ? 'var(--color-success, #10b981)' : 'var(--text-dim, #7a8099)',
                transition: 'color 0.2s ease',
              }}
            >
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '15px',
                  height: '15px',
                  borderRadius: '50%',
                  fontSize: '0.65rem',
                  fontWeight: 'bold',
                  background: item.passed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                  color: item.passed ? '#10b981' : 'var(--text-dim)',
                }}
              >
                {item.passed ? '✓' : '×'}
              </span>
              <span>{item.label}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
