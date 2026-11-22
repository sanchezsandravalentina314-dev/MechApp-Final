/**
 * Utilidades de seguridad para contraseñas de MechApp.
 * Cumple con los requisitos de:
 * - Mínimo 12 caracteres.
 * - Mayúsculas, minúsculas, números y caracteres especiales.
 * - Detección de contraseñas comunes o comprometidas.
 * - Indicador visual de fortaleza y checklist interactivo.
 * - Control contra intentos repetidos de acceso (brute-force lockout).
 */

// Lista de contraseñas y patrones comunes o fácilmente vulnerables
const COMMON_PASSWORDS = [
  'password', 'password123', 'password1234', '123456789012', '1234567890123',
  'admin123456', 'admin1234567', 'mechapp1234', 'mechapp2024!', 'mechapp2025!',
  'mechapp2026!', 'qwertyuiop12', 'colombia1234', 'tejo12345678', 'contrasena12',
  'contrasena123', 'password12345', 'supersecret1', 'iloveyou1234', 'welcome12345',
  '111111111111', '000000000000', '123123123123', 'abc123abc123'
];

/**
 * Evalúa los criterios de seguridad de una contraseña.
 */
export function evaluatePassword(password = '') {
  const pwd = String(password || '');

  const rules = {
    length: pwd.length >= 12,
    hasUpper: /[A-Z]/.test(pwd),
    hasLower: /[a-z]/.test(pwd),
    hasNumber: /[0-9]/.test(pwd),
    hasSpecial: /[^A-Za-z0-9]/.test(pwd),
    notCommon: !COMMON_PASSWORDS.some((common) => pwd.toLowerCase().includes(common))
  };

  const checksPassed = Object.values(rules).filter(Boolean).length;
  const isFullyValid = rules.length && rules.hasUpper && rules.hasLower && rules.hasNumber && rules.hasSpecial && rules.notCommon;

  // Cálculo de puntaje 0-100
  let score = 0;
  if (pwd.length >= 12) score += 25;
  if (pwd.length >= 16) score += 10;
  if (rules.hasUpper) score += 15;
  if (rules.hasLower) score += 15;
  if (rules.hasNumber) score += 15;
  if (rules.hasSpecial) score += 20;
  if (!rules.notCommon) score = Math.min(score, 20); // penalización severa por común

  score = Math.min(Math.max(score, 0), 100);

  let level = 'Muy Débil';
  let color = '#ef4444'; // rojo
  if (score >= 90) {
    level = 'Muy Fuerte';
    color = '#10b981'; // verde esmeralda
  } else if (score >= 75) {
    level = 'Fuerte';
    color = '#22c55e'; // verde
  } else if (score >= 50) {
    level = 'Aceptable';
    color = '#f59e0b'; // ámbar / naranja
  } else if (score >= 25) {
    level = 'Débil';
    color = '#f97316'; // naranja fuerte
  }

  const criteria = [
    { id: 'length', label: 'Mínimo 12 caracteres', passed: rules.length },
    { id: 'hasUpper', label: 'Al menos una letra mayúscula (A-Z)', passed: rules.hasUpper },
    { id: 'hasLower', label: 'Al menos una letra minúscula (a-z)', passed: rules.hasLower },
    { id: 'hasNumber', label: 'Al menos un número (0-9)', passed: rules.hasNumber },
    { id: 'hasSpecial', label: 'Al menos un carácter especial (!@#$%^&*...)', passed: rules.hasSpecial },
    { id: 'notCommon', label: 'No utilizar palabras comunes o comprometidas', passed: rules.notCommon },
  ];

  return {
    rules,
    score,
    level,
    color,
    criteria,
    isValid: isFullyValid,
  };
}

/**
 * Validador para frontend que devuelve mensaje de error descriptivo o null si es válida.
 */
export function validatePasswordRequirements(password) {
  if (!password || password.length < 12) {
    return 'La contraseña debe tener mínimo 12 caracteres.';
  }
  if (!/[A-Z]/.test(password)) {
    return 'La contraseña debe incluir al menos una letra mayúscula.';
  }
  if (!/[a-z]/.test(password)) {
    return 'La contraseña debe incluir al menos una letra minúscula.';
  }
  if (!/[0-9]/.test(password)) {
    return 'La contraseña debe incluir al menos un número.';
  }
  if (!/[^A-Za-z0-9]/.test(password)) {
    return 'La contraseña debe incluir al menos un carácter especial (ej. !@#$%^&*).';
  }
  const evalResult = evaluatePassword(password);
  if (!evalResult.rules.notCommon) {
    return 'La contraseña ingresada es demasiado común o insegura. Por favor utiliza otra combinación.';
  }
  return null;
}

// -------------------------------------------------------------
// CONTROL CONTRA INTENTOS REPETIDOS DE ACCESO (RATE LIMITING / LOCKOUT)
// -------------------------------------------------------------
const MAX_FAILED_ATTEMPTS = 5;
const LOCKOUT_MINUTES = 15;
const STORAGE_KEY = 'mechapp_auth_attempts';

function getAttemptStore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveAttemptStore(store) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch (e) {
    console.error('Error guardando intentos de auth', e);
  }
}

/**
 * Verifica si un usuario o IP/navegador está temporalmente bloqueado por intentos fallidos.
 * @param {string} identifier - correo electrónico o identificador
 */
export function checkAccountLockout(identifier = 'default') {
  const store = getAttemptStore();
  const record = store[identifier.toLowerCase().trim()];

  if (!record) {
    return { locked: false, remainingAttempts: MAX_FAILED_ATTEMPTS, minutesRemaining: 0 };
  }

  const now = Date.now();
  if (record.lockedUntil && record.lockedUntil > now) {
    const minutesRemaining = Math.ceil((record.lockedUntil - now) / 60000);
    return {
      locked: true,
      remainingAttempts: 0,
      minutesRemaining,
      lockedUntil: record.lockedUntil,
    };
  }

  // Si el tiempo de bloqueo ya pasó, reiniciamos el contador
  if (record.lockedUntil && record.lockedUntil <= now) {
    delete store[identifier.toLowerCase().trim()];
    saveAttemptStore(store);
    return { locked: false, remainingAttempts: MAX_FAILED_ATTEMPTS, minutesRemaining: 0 };
  }

  const remaining = Math.max(0, MAX_FAILED_ATTEMPTS - (record.attempts || 0));
  return { locked: false, remainingAttempts: remaining, minutesRemaining: 0 };
}

/**
 * Registra un intento fallido de inicio de sesión.
 */
export function recordFailedAttempt(identifier = 'default') {
  const store = getAttemptStore();
  const idKey = identifier.toLowerCase().trim();
  const now = Date.now();
  const record = store[idKey] || { attempts: 0 };

  record.attempts = (record.attempts || 0) + 1;
  record.lastAttempt = now;

  if (record.attempts >= MAX_FAILED_ATTEMPTS) {
    record.lockedUntil = now + (LOCKOUT_MINUTES * 60 * 1000);
  }

  store[idKey] = record;
  saveAttemptStore(store);

  return checkAccountLockout(identifier);
}

/**
 * Restablece los intentos tras un login exitoso.
 */
export function clearFailedAttempts(identifier = 'default') {
  const store = getAttemptStore();
  const idKey = identifier.toLowerCase().trim();
  if (store[idKey]) {
    delete store[idKey];
    saveAttemptStore(store);
  }
}
