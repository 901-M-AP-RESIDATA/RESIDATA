/**
 * Utilidades de formato y color de ResiData.
 *
 * La paleta verde se usa para datos generales; el rojo se reserva para
 * residuos peligrosos.
 */

/** Colores en formato hex para Chart.js y estilos. */
export const COLORES = {
	verde: '#0ca678',
	verdeClaro: '#20c997',
	azul: '#3b82f6',
	rojo: '#e03131',
	ambar: '#f59e0b',
	gris: '#94a3b8'
} as const;

/** Devuelve el color asociado a una categoria de residuo. */
export function colorCategoria(nombre?: string | null): string {
	switch ((nombre ?? '').toLowerCase()) {
		case 'organico':
			return COLORES.verde;
		case 'inorganico':
			return COLORES.azul;
		case 'peligroso':
			return COLORES.rojo;
		default:
			return COLORES.gris;
	}
}

/** Variante de insignia segun la categoria. */
export function varianteCategoria(nombre?: string | null): 'verde' | 'azul' | 'rojo' | 'gris' {
	switch ((nombre ?? '').toLowerCase()) {
		case 'organico':
			return 'verde';
		case 'inorganico':
			return 'azul';
		case 'peligroso':
			return 'rojo';
		default:
			return 'gris';
	}
}

/** Formatea un numero con separador de miles (es-MX). */
export function formatearNumero(valor: number): string {
	return new Intl.NumberFormat('es-MX').format(valor);
}

/** Formatea una confianza 0..1 como porcentaje. */
export function formatearPorcentaje(valor: number): string {
	return `${Math.round(valor * 100)}%`;
}

/** Formatea una marca ISO como fecha y hora local (es-MX). */
export function formatearFechaHora(iso: string): string {
	const fecha = new Date(iso);
	if (Number.isNaN(fecha.getTime())) return '—';
	return fecha.toLocaleString('es-MX', {
		day: '2-digit',
		month: 'short',
		hour: '2-digit',
		minute: '2-digit'
	});
}

/** Formatea 'YYYY-MM-DD' como dia corto (es-MX), sin desfase de zona horaria. */
export function formatearDia(iso: string): string {
	const [anio, mes, dia] = iso.split('-').map(Number);
	if (!anio || !mes || !dia) return iso;
	const fecha = new Date(anio, mes - 1, dia);
	return fecha.toLocaleDateString('es-MX', { day: '2-digit', month: 'short' });
}

/** Etiqueta legible para un tipo de alerta. */
export function etiquetaTipoAlerta(tipo: string): string {
	switch (tipo) {
		case 'residuo_peligroso':
			return 'Residuo peligroso';
		case 'baja_confianza':
			return 'Baja confianza';
		case 'error_contenedor':
			return 'Error de contenedor';
		case 'sistema':
			return 'Sistema';
		default:
			return tipo;
	}
}

/** Variante de insignia segun el tipo de alerta. */
export function varianteTipoAlerta(tipo: string): 'verde' | 'azul' | 'rojo' | 'gris' | 'ambar' {
	switch (tipo) {
		case 'residuo_peligroso':
			return 'rojo';
		case 'baja_confianza':
			return 'ambar';
		case 'error_contenedor':
			return 'ambar';
		case 'sistema':
			return 'azul';
		default:
			return 'gris';
	}
}
