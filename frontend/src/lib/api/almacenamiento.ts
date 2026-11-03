/**
 * Persistencia de la sesion en el navegador.
 *
 * Los tokens se guardan en `localStorage` para sobrevivir a recargas.
 * Se centraliza aqui el acceso para que el cliente HTTP y los stores no
 * dupliquen claves ni manejen `undefined`.
 */

import type { Usuario } from '#lib/tipos/index.ts';

const CLAVE_ACCESO = 'residata.access_token';
const CLAVE_REFRESCO = 'residata.refresh_token';
const CLAVE_USUARIO = 'residata.usuario';

const hayAlmacen = (): boolean => typeof localStorage !== 'undefined';

export function obtenerTokenAcceso(): string | null {
	if (!hayAlmacen()) return null;
	return localStorage.getItem(CLAVE_ACCESO);
}

export function obtenerTokenRefresco(): string | null {
	if (!hayAlmacen()) return null;
	return localStorage.getItem(CLAVE_REFRESCO);
}

export function guardarTokens(acceso: string, refresco: string): void {
	if (!hayAlmacen()) return;
	localStorage.setItem(CLAVE_ACCESO, acceso);
	localStorage.setItem(CLAVE_REFRESCO, refresco);
}

export function limpiarTokens(): void {
	if (!hayAlmacen()) return;
	localStorage.removeItem(CLAVE_ACCESO);
	localStorage.removeItem(CLAVE_REFRESCO);
}

export function guardarUsuarioEnCache(usuario: Usuario): void {
	if (!hayAlmacen()) return;
	localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
}

export function obtenerUsuarioEnCache(): Usuario | null {
	if (!hayAlmacen()) return null;
	const crudo = localStorage.getItem(CLAVE_USUARIO);
	if (!crudo) return null;
	try {
		return JSON.parse(crudo) as Usuario;
	} catch {
		return null;
	}
}

export function limpiarUsuarioEnCache(): void {
	if (!hayAlmacen()) return;
	localStorage.removeItem(CLAVE_USUARIO);
}

/** Elimina toda la informacion de sesion persistida. */
export function limpiarSesion(): void {
	limpiarTokens();
	limpiarUsuarioEnCache();
}
