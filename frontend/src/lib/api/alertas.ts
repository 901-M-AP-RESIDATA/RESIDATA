/** Endpoints de alertas. */

import type { Alerta, FiltrosAlertas, RespuestaPaginada } from '#lib/tipos/index.ts';
import { http } from './cliente';

/** Lista alertas de forma paginada, con filtros opcionales. */
export function listarAlertas(
	filtros: FiltrosAlertas = {},
	signal?: AbortSignal
): Promise<RespuestaPaginada<Alerta>> {
	const parametros = new URLSearchParams();
	if (filtros.atendida !== undefined) parametros.set('atendida', String(filtros.atendida));
	if (filtros.tipo) parametros.set('tipo', filtros.tipo);
	if (filtros.contenedor_id !== undefined)
		parametros.set('contenedor_id', String(filtros.contenedor_id));
	parametros.set('pagina', String(filtros.pagina ?? 1));
	parametros.set('limite', String(filtros.limite ?? 20));

	return http.get<RespuestaPaginada<Alerta>>(`/api/v1/alertas?${parametros.toString()}`, { signal });
}

/** Marca (o desmarca) una alerta como atendida. */
export function marcarAlertaAtendida(id: number, atendida = true): Promise<Alerta> {
	return http.patch<Alerta>(`/api/v1/alertas/${id}`, { atendida });
}
