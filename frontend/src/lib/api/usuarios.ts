/** Endpoints de usuarios y roles (CRUD, solo administradores). */

import type {
	ActualizarUsuario,
	CrearUsuario,
	RespuestaPaginada,
	Rol,
	Usuario
} from '#lib/tipos/index.ts';
import { http } from './cliente';

/** Lista los usuarios (hasta 100). */
export function listarUsuarios(signal?: AbortSignal): Promise<RespuestaPaginada<Usuario>> {
	return http.get<RespuestaPaginada<Usuario>>('/api/v1/usuarios?limite=100', { signal });
}

/** Crea un usuario. */
export function crearUsuario(datos: CrearUsuario): Promise<Usuario> {
	return http.post<Usuario>('/api/v1/usuarios', datos);
}

/** Actualiza un usuario existente. */
export function actualizarUsuario(id: number, datos: ActualizarUsuario): Promise<Usuario> {
	return http.patch<Usuario>(`/api/v1/usuarios/${id}`, datos);
}

/** Elimina un usuario. */
export function eliminarUsuario(id: number): Promise<void> {
	return http.delete<void>(`/api/v1/usuarios/${id}`);
}

/** Lista los roles disponibles. */
export function listarRoles(signal?: AbortSignal): Promise<Rol[]> {
	return http.get<Rol[]>('/api/v1/roles', { signal });
}
