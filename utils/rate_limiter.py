"""
Rate limiter centralizado para MechApp.
Protege endpoints de autenticación contra ataques de fuerza bruta.

Requiere: pip install slowapi
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Límite basado en IP del cliente
limiter = Limiter(key_func=get_remote_address)
