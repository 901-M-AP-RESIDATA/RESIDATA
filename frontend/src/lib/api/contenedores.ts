/** Endpoints de contenedores (CRUD). */

import type {
	ActualizarContenedor,
	Contenedor,
	ContenedorConApiKey,
	CrearContenedor,
	EstadoContenedorDetalle,
	RespuestaPaginada
} from '#lib/tipos/index.ts';
import { http } from './cliente';

/** Lista los contenedores (hasta 100). */
export function listarContenedores(signal?: AbortSignal): Promise<RespuestaPaginada<Contenedor>> {
	return http.get<RespuestaPaginada<Contenedor>>('/api/v1/contenedores?limite=100', { signal });
}

/** Obtiene el detalle de un contenedor con metricas de uso. */
export function obtenerContenedor(id: number, signal?: AbortSignal): Promise<EstadoContenedorDetalle> {
	return http.get<EstadoContenedorDetalle>(`/api/v1/contenedores/${id}`, { signal });
}

/** Crea un contenedor. La respuesta incluye la API key en texto plano UNA vez. */
export function crearContenedor(datos: CrearContenedor): Promise<ContenedorConApiKey> {
	return http.post<ContenedorConApiKey>('/api/v1/contenedores', datos);
}

/** Actualiza un contenedor existente. */
export function actualizarContenedor(
	id: number,
	datos: ActualizarContenedor
): Promise<Contenedor> {
	return http.patch<Contenedor>(`/api/v1/contenedores/${id}`, datos);
}

/** Elimina un contenedor. */
export function eliminarContenedor(id: number): Promise<void> {
	return http.delete<void>(`/api/v1/contenedores/${id}`);
}

/** Regenera la API key de un contenedor. Devuelve la clave nueva en texto plano. */
export function regenerarClaveContenedor(id: number): Promise<ContenedorConApiKey> {
	return http.post<ContenedorConApiKey>(`/api/v1/contenedores/${id}/regenerar-clave`);
}
