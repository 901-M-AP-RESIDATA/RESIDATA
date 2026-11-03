/** Endpoints de catálogos simples. */

import type { CategoriaResiduo } from '#lib/tipos/index.ts';
import { http } from './cliente';

/** Lista las categorías de residuo. */
export function listarCategorias(signal?: AbortSignal): Promise<CategoriaResiduo[]> {
	return http.get<CategoriaResiduo[]>('/api/v1/categorias', { signal });
}
