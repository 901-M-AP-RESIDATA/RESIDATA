/**
 * Store de sesion (Svelte 5 runes).
 *
 * Mantiene el usuario autenticado, restaura la sesion al recargar y
 * reacciona al vencimiento del token limpiando el estado.
 */

import {
	guardarTokens,
	guardarUsuarioEnCache,
	limpiarSesion as limpiarAlmacen,
	obtenerTokenAcceso,
	obtenerUsuarioEnCache
} from '#lib/api/almacenamiento.ts';
import { iniciarSesion, obtenerPerfil } from '#lib/api/auth.ts';
import { alExpirarSesion } from '#lib/api/cliente.ts';
import type { Usuario } from '#lib/tipos/index.ts';

class AlmacenSesion {
	/** Usuario autenticado (null si no hay sesion). */
	usuario = $state<Usuario | null>(null);
	/** Indica si ya se intento restaurar la sesion persistida. */
	inicializado = $state(false);
	/** Indica si hay una operacion de login en curso. */
	cargando = $state(false);

	get autenticado(): boolean {
		return this.usuario !== null;
	}

	get esAdministrador(): boolean {
		return this.usuario?.rol?.nombre === 'administrador';
	}

	get nombreRol(): string {
		return this.usuario?.rol?.nombre ?? '';
	}

	/**
	 * Restaura la sesion desde el almacenamiento local.
	 * Debe llamarse una vez al montar la aplicacion.
	 */
	async iniciar(): Promise<void> {
		if (this.inicializado) return;
		const token = obtenerTokenAcceso();
		if (!token) {
			this.inicializado = true;
			return;
		}
		// Muestra el usuario en cache mientras se valida el token.
		const cache = obtenerUsuarioEnCache();
		if (cache) this.usuario = cache;
		try {
			this.usuario = await obtenerPerfil();
			guardarUsuarioEnCache(this.usuario);
		} catch {
			this.usuario = null;
			limpiarAlmacen();
		} finally {
			this.inicializado = true;
		}
	}

	/** Inicia sesion con correo y contrasena. */
	async entrar(correo: string, contrasena: string): Promise<Usuario> {
		this.cargando = true;
		try {
			const respuesta = await iniciarSesion(correo, contrasena);
			guardarTokens(respuesta.access_token, respuesta.refresh_token);
			this.usuario = await obtenerPerfil();
			guardarUsuarioEnCache(this.usuario);
			return this.usuario;
		} finally {
			this.cargando = false;
		}
	}

	/** Cierra la sesion local. */
	salir(): void {
		limpiarAlmacen();
		this.usuario = null;
		this.inicializado = true;
	}

	/** Conecta el vencimiento de token con la limpieza de la sesion. */
	vincularExpiracion(): void {
		alExpirarSesion(() => this.salir());
	}
}

/** Instancia unica del store de sesion. */
export const sesion = new AlmacenSesion();
