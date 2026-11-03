/** Endpoints del dashboard (metricas agregadas). */

import type { ResumenDashboard } from '#lib/tipos/index.ts';
import { http } from './cliente';

/** Obtiene el resumen del dashboard (KPIs, series y ultimas clasificaciones). */
export function obtenerResumen(signal?: AbortSignal): Promise<ResumenDashboard> {
	return http.get<ResumenDashboard>('/api/v1/dashboard/resumen', { signal });
}
