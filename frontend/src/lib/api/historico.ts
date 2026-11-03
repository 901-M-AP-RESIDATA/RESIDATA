/** Endpoints del histórico de clasificaciones. */

import type { FiltrosHistorico, HistoricoClasificacion, RespuestaPaginada } from '#lib/tipos/index.ts';
import { http } from './cliente';

/** Lista el histórico de clasificaciones de forma paginada, con filtros. */
export function listarHistorico(
	filtros: FiltrosHistorico = {},
	signal?: AbortSignal
): Promise<RespuestaPaginada<HistoricoClasificacion>> {
	const parametros = new URLSearchParams();
	if (filtros.fecha_desde) parametros.set('fecha_desde', filtros.fecha_desde);
	if (filtros.fecha_hasta) parametros.set('fecha_hasta', filtros.fecha_hasta);
	if (filtros.categoria) parametros.set('categoria', filtros.categoria);
	if (filtros.contenedor_id !== undefined)
		parametros.set('contenedor_id', String(filtros.contenedor_id));
	parametros.set('pagina', String(filtros.pagina ?? 1));
	parametros.set('limite', String(filtros.limite ?? 20));

	return http.get<RespuestaPaginada<HistoricoClasificacion>>(
		`/api/v1/historico?${parametros.toString()}`,
		{ signal }
	);
}
