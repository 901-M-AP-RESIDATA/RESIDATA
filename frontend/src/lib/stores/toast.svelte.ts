/**
 * Store de notificaciones tipo "toast" (Svelte 5 runes).
 * Se usa para mensajes de exito, error, informacion y peligro.
 */

export type TipoToast = 'exito' | 'error' | 'info' | 'peligro';

export interface Toast {
	id: number;
	tipo: TipoToast;
	titulo: string;
	mensaje?: string;
	/** Duracion en milisegundos (0 = no se cierra solo). */
	duracion: number;
}

class AlmacenToasts {
	/** Lista de toasts activos. */
	items = $state<Toast[]>([]);
	private contador = 0;

	mostrar(tipo: TipoToast, titulo: string, mensaje?: string, duracion = 5000): number {
		const id = ++this.contador;
		this.items = [...this.items, { id, tipo, titulo, mensaje, duracion }];
		if (duracion > 0) {
			setTimeout(() => this.cerrar(id), duracion);
		}
		return id;
	}

	exito(titulo: string, mensaje?: string, duracion = 4000): number {
		return this.mostrar('exito', titulo, mensaje, duracion);
	}

	error(titulo: string, mensaje?: string, duracion = 6000): number {
		return this.mostrar('error', titulo, mensaje, duracion);
	}

	info(titulo: string, mensaje?: string, duracion = 4000): number {
		return this.mostrar('info', titulo, mensaje, duracion);
	}

	peligro(titulo: string, mensaje?: string, duracion = 0): number {
		return this.mostrar('peligro', titulo, mensaje, duracion);
	}

	cerrar(id: number): void {
		this.items = this.items.filter((t) => t.id !== id);
	}
}

/** Instancia unica del store de toasts. */
export const toasts = new AlmacenToasts();
