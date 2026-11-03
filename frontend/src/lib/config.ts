/**
 * Configuracion del frontend a partir de las variables de entorno de Vite.
 * Solo las variables con prefijo `VITE_` llegan al navegador.
 */

const apiUrlCruda = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/** URL base del backend FastAPI, sin barra final. */
export const API_URL: string = apiUrlCruda.replace(/\/+$/, '');

/** Indica si se deben usar datos simulados en lugar del backend real. */
export const USAR_MOCK: boolean = String(import.meta.env.VITE_USAR_MOCK ?? 'false') === 'true';

/** Indica si se reproduce sonido al recibir alertas de peligro. */
export const SONIDO_ALERTAS: boolean =
	String(import.meta.env.VITE_SONIDO_ALERTAS ?? 'true') === 'true';

/** URL base del WebSocket, derivada de la URL del API. */
export const WS_URL: string = API_URL.replace(/^http/, 'ws');

/** Nombre legible de la aplicacion. */
export const NOMBRE_APP = 'ResiData';
