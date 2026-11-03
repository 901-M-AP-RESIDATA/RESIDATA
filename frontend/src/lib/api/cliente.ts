/**
 * Cliente HTTP tipado del backend ResiData.
 *
 * Caracteristicas:
 *  - Adjunta automaticamente el token de acceso (Bearer).
 *  - Ante un 401 intenta refrescar el token una vez y reintenta.
 *  - Si el refresco falla, limpia la sesion y notifica a quien escuche
 *    (el store de sesion redirige a /login).
 *  - Centraliza los errores en `ErrorApi`.
 *  - Si `VITE_USAR_MOCK=true`, delega en el modulo de datos simulados.
 */

import { API_URL, USAR_MOCK } from '#lib/config.ts';
import type { CuerpoError, RespuestaLogin } from '#lib/tipos/index.ts';
import {
	guardarTokens,
	limpiarSesion,
	obtenerTokenAcceso,
	obtenerTokenRefresco
} from './almacenamiento';

// ---------------------------------------------------------------------
// Errores
// ---------------------------------------------------------------------
export class ErrorApi extends Error {
	constructor(
		public readonly estado: number,
		public readonly codigo: string,
		mensaje: string
	) {
		super(mensaje);
		this.name = 'ErrorApi';
	}
}

/** Error de red (servidor caido, sin conexion, CORS...). */
export class ErrorRed extends Error {
	constructor(mensaje = 'No se pudo conectar con el servidor.') {
		super(mensaje);
		this.name = 'ErrorRed';
	}
}

// ---------------------------------------------------------------------
// Sesion expirada
// ---------------------------------------------------------------------
type ManejadorExpiracion = () => void;
const manejadoresExpiracion = new Set<ManejadorExpiracion>();

/** Registra un callback que se ejecuta cuando la sesion ya no es valida. */
export function alExpirarSesion(manejador: ManejadorExpiracion): () => void {
	manejadoresExpiracion.add(manejador);
	return () => manejadoresExpiracion.delete(manejador);
}

function notificarExpiracion(): void {
	for (const manejador of manejadoresExpiracion) manejador();
}

// ---------------------------------------------------------------------
// Peticion base
// ---------------------------------------------------------------------
type Metodo = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface OpcionesPeticion {
	metodo?: Metodo;
	cuerpo?: unknown;
	/** Enviar el cuerpo como formulario (application/x-www-form-urlencoded). */
	formulario?: boolean;
	/** Adjuntar token de acceso. Por defecto true. */
	autenticado?: boolean;
	/** Reintentar tras refrescar el token ante un 401. Por defecto true. */
	reintentarEn401?: boolean;
	cabeceras?: Record<string, string>;
	signal?: AbortSignal;
}

function construirCabeceras(opciones: OpcionesPeticion): Record<string, string> {
	const cabeceras: Record<string, string> = { Accept: 'application/json', ...opciones.cabeceras };
	const autenticado = opciones.autenticado !== false;
	if (autenticado) {
		const token = obtenerTokenAcceso();
		if (token) cabeceras['Authorization'] = `Bearer ${token}`;
	}
	return cabeceras;
}

function construirCuerpo(opciones: OpcionesPeticion, cabeceras: Record<string, string>): BodyInit | undefined {
	if (opciones.cuerpo === undefined || opciones.cuerpo === null) return undefined;
	if (opciones.formulario) {
		cabeceras['Content-Type'] = 'application/x-www-form-urlencoded';
		const datos = new URLSearchParams();
		for (const [clave, valor] of Object.entries(opciones.cuerpo as Record<string, unknown>)) {
			if (valor !== undefined && valor !== null) datos.append(clave, String(valor));
		}
		return datos.toString();
	}
	cabeceras['Content-Type'] = 'application/json';
	return JSON.stringify(opciones.cuerpo);
}

async function leerError(respuesta: Response): Promise<ErrorApi> {
	let codigo = 'error';
	let mensaje = `Error ${respuesta.status}`;
	try {
		const cuerpo = (await respuesta.json()) as CuerpoError;
		if (cuerpo.error) {
			codigo = cuerpo.error.codigo;
			mensaje = cuerpo.error.mensaje;
		} else if (cuerpo.detail) {
			mensaje = typeof cuerpo.detail === 'string' ? cuerpo.detail : mensaje;
		}
	} catch {
		// Respuesta sin cuerpo JSON: se conserva el mensaje generico.
	}
	return new ErrorApi(respuesta.status, codigo, mensaje);
}

async function solicitar<T>(ruta: string, opciones: OpcionesPeticion = {}): Promise<T> {
	if (USAR_MOCK) {
		const { peticionMock } = await import('./mock');
		return peticionMock<T>(ruta, opciones);
	}

	const metodo = opciones.metodo ?? 'GET';
	const cabeceras = construirCabeceras(opciones);
	const cuerpo = construirCuerpo(opciones, cabeceras);

	let respuesta: Response;
	try {
		respuesta = await fetch(`${API_URL}${ruta}`, {
			method: metodo,
			headers: cabeceras,
			body: cuerpo,
			signal: opciones.signal
		});
	} catch (error) {
		if ((error as Error)?.name === 'AbortError') throw error;
		throw new ErrorRed();
	}

	// Token caducado: intentar refrescar y reintentar una sola vez.
	const autenticado = opciones.autenticado !== false;
	if (respuesta.status === 401 && autenticado && opciones.reintentarEn401 !== false) {
		const refrescado = await refrescarToken();
		if (refrescado) {
			return solicitar<T>(ruta, { ...opciones, reintentarEn401: false });
		}
		notificarExpiracion();
		throw await leerError(respuesta);
	}

	if (!respuesta.ok) {
		throw await leerError(respuesta);
	}

	if (respuesta.status === 204) return undefined as T;

	const tipoContenido = respuesta.headers.get('content-type') ?? '';
	if (tipoContenido.includes('application/json')) {
		return (await respuesta.json()) as T;
	}
	return (await respuesta.text()) as unknown as T;
}

// ---------------------------------------------------------------------
// Refresco de token (una sola peticion concurrente)
// ---------------------------------------------------------------------
let refrescoEnCurso: Promise<boolean> | null = null;

async function ejecutarRefresco(): Promise<boolean> {
	const refresco = obtenerTokenRefresco();
	if (!refresco) return false;
	try {
		const respuesta = await fetch(`${API_URL}/api/v1/auth/refresh`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
			body: JSON.stringify({ refresh_token: refresco })
		});
		if (!respuesta.ok) return false;
		const datos = (await respuesta.json()) as RespuestaLogin;
		if (!datos.access_token || !datos.refresh_token) return false;
		guardarTokens(datos.access_token, datos.refresh_token);
		return true;
	} catch {
		return false;
	}
}

/** Intenta refrescar el token. Devuelve `true` si se renovo correctamente. */
export async function refrescarToken(): Promise<boolean> {
	if (!refrescoEnCurso) {
		refrescoEnCurso = ejecutarRefresco().finally(() => {
			refrescoEnCurso = null;
		});
	}
	const resultado = await refrescoEnCurso;
	if (!resultado) limpiarSesion();
	return resultado;
}

// ---------------------------------------------------------------------
// Helpers publicos
// ---------------------------------------------------------------------
export const http = {
	get: <T>(ruta: string, opciones?: OpcionesPeticion) =>
		solicitar<T>(ruta, { ...opciones, metodo: 'GET' }),
	post: <T>(ruta: string, cuerpo?: unknown, opciones?: OpcionesPeticion) =>
		solicitar<T>(ruta, { ...opciones, metodo: 'POST', cuerpo }),
	put: <T>(ruta: string, cuerpo?: unknown, opciones?: OpcionesPeticion) =>
		solicitar<T>(ruta, { ...opciones, metodo: 'PUT', cuerpo }),
	patch: <T>(ruta: string, cuerpo?: unknown, opciones?: OpcionesPeticion) =>
		solicitar<T>(ruta, { ...opciones, metodo: 'PATCH', cuerpo }),
	delete: <T>(ruta: string, opciones?: OpcionesPeticion) =>
		solicitar<T>(ruta, { ...opciones, metodo: 'DELETE' })
};
