/**
 * Store de alertas (Svelte 5 runes).
 *
 * Mantiene las alertas pendientes, se alimenta del flujo de tiempo real y
 * expone acciones para atenderlas. Tambien controla el sonido de aviso.
 */

import { listarAlertas, marcarAlertaAtendida } from '#lib/api/alertas.ts';
import { SONIDO_ALERTAS } from '#lib/config.ts';
import { toasts } from '#lib/stores/toast.svelte.ts';
import { tiempoReal } from '#lib/stores/tiempoReal.ts';
import { reproducirAlerta } from '#lib/util/sonido.ts';
import type { Alerta, EventoWS } from '#lib/tipos/index.ts';

class AlmacenAlertas {
	/** Alertas pendientes (no atendidas), la mas reciente primero. */
	pendientes = $state<Alerta[]>([]);
	/** Indica si hay una carga en curso. */
	cargando = $state(false);
	/** Si el aviso sonoro esta activo. */
	sonidoActivo = $state(SONIDO_ALERTAS);

	private cancelarSuscripcion: (() => void) | null = null;
	private iniciado = false;

	get total(): number {
		return this.pendientes.length;
	}

	/** Carga las alertas pendientes desde el API. */
	async cargar(): Promise<void> {
		this.cargando = true;
		try {
			const respuesta = await listarAlertas({ atendida: false, limite: 50 });
			this.pendientes = respuesta.items;
		} finally {
			this.cargando = false;
		}
	}

	private manejarEvento = (evento: EventoWS): void => {
		if (evento.tipo !== 'alerta_peligroso') return;
		const alerta = evento.data;
		this.pendientes = [alerta, ...this.pendientes.filter((a) => a.id !== alerta.id)];
		toasts.peligro('Residuo peligroso', alerta.mensaje);
		if (this.sonidoActivo) reproducirAlerta();
	};

	/** Comienza a escuchar el flujo en tiempo real y carga las pendientes. */
	iniciar(): void {
		if (this.iniciado) return;
		this.iniciado = true;
		void this.cargar();
		this.cancelarSuscripcion = tiempoReal.suscribir(this.manejarEvento);
	}

	/** Deja de escuchar el flujo de tiempo real. */
	detener(): void {
		this.cancelarSuscripcion?.();
		this.cancelarSuscripcion = null;
		this.iniciado = false;
	}

	alternarSonido(): void {
		this.sonidoActivo = !this.sonidoActivo;
	}

	/** Marca una alerta como atendida y la quita de pendientes. */
	async atender(id: number): Promise<void> {
		const actualizada = await marcarAlertaAtendida(id);
		this.pendientes = this.pendientes.filter((a) => a.id !== id);
		toasts.exito('Alerta atendida', `Alerta #${actualizada.id} marcada como atendida.`);
	}
}

/** Instancia unica del store de alertas. */
export const alertas = new AlmacenAlertas();
