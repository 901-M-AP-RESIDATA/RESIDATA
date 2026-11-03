/** Endpoints de autenticacion y perfil. */

import type { RespuestaLogin, Usuario } from '#lib/tipos/index.ts';
import { http } from './cliente';

/**
 * Inicia sesion con correo y contrasena.
 * El backend usa el formulario OAuth2 (username=correo, password).
 */
export function iniciarSesion(correo: string, contrasena: string): Promise<RespuestaLogin> {
	return http.post<RespuestaLogin>(
		'/api/v1/auth/login',
		{ username: correo, password: contrasena },
		{ formulario: true, autenticado: false, reintentarEn401: false }
	);
}

/** Obtiene el usuario autenticado (incluye su rol). */
export function obtenerPerfil(signal?: AbortSignal): Promise<Usuario> {
	return http.get<Usuario>('/api/v1/auth/me', { signal });
}
