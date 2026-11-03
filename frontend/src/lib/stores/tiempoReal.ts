/**
 * Cliente de tiempo real (WebSocket) de ResiData.
 *
 * Se conecta a `/api/v1/ws?token=<JWT>`, reenvia los eventos a los
 * suscriptores, gestiona reconexion con retroceso exponencial y actualiza
 * el store de conexion. En modo mock simula el flujo de eventos.
 */

import { obtenerTokenAcceso } from '#lib/api/almacenamiento.ts';
import { WS_URL, USAR_MOCK } from '#lib/config.ts';
import { conexion } from '#lib/stores/conexion.svelte.ts';
import type { EventoWS } from '#lib/tipos/index.ts';

type Escucha = (evento: EventoWS) => void;
type Cancelar = () => void;

class TiempoReal {
	private socket: WebSocket | null = null;
	private escuchas = new Set<Escucha>();
	private temporizadorReconexion: ReturnType<typeof setTimeout> | null = null;
	private detenerSimulacion: Cancelar | null = null;
	private activo = false;
	private reintentos = 0;

	/** Registra un oyente de eventos. Devuelve una funcion para cancelarlo. */
	suscribir(escucha: Escucha): Cancelar {
		this.escuchas.add(escucha);
		return () => this.escuchas.delete(escucha);
	}

	/** Abre la conexion (idempotente). */
	conectar(): void {
		if (this.activo) return;
		this.activo = true;
		if (USAR_MOCK) {
			this.conectarSimulado();
		} else {
			this.abrirSocket();
		}
	}

	/** Cierra la conexion y detiene reintentos/simulacion. */
	desconectar(): void {
		this.activo = false;
		if (this.temporizadorReconexion) {
			clearTimeout(this.temporizadorReconexion);
			this.temporizadorReconexion = null;
		}
		this.detenerSimulacion?.();
		this.detenerSimulacion = null;
		this.socket?.close();
		this.socket = null;
		conexion.establecer('desconectado');
	}

	private emitir(evento: EventoWS): void {
		for (const escucha of this.escuchas) escucha(evento);
	}

	private conectarSimulado(): void {
		conexion.establecer('conectando');
		void import('#lib/api/mock.ts').then(({ iniciarTiempoRealSimulado }) => {
			if (!this.activo) return;
			conexion.establecer('conectado');
			this.detenerSimulacion = iniciarTiempoRealSimulado((evento) => {
				conexion.marcarActividad();
				this.emitir(evento);
			});
		});
	}

	private abrirSocket(): void {
		const token = obtenerTokenAcceso();
		if (!token) {
			conexion.establecer('desconectado');
			return;
		}

		conexion.establecer(this.reintentos > 0 ? 'reconectando' : 'conectando');
		const url = `${WS_URL}/api/v1/ws?token=${encodeURIComponent(token)}`;

		let socket: WebSocket;
		try {
			socket = new WebSocket(url);
		} catch {
			this.programarReconexion();
			return;
		}
		this.socket = socket;

		socket.onopen = () => {
			this.reintentos = 0;
			conexion.establecer('conectado');
		};

		socket.onmessage = (mensaje) => {
			conexion.marcarActividad();
			try {
				this.emitir(JSON.parse(mensaje.data as string) as EventoWS);
			} catch {
				// Mensaje no JSON: se ignora.
			}
		};

		socket.onclose = () => {
			if (this.activo) this.programarReconexion();
		};

		socket.onerror = () => {
			socket.close();
		};
	}

	private programarReconexion(): void {
		conexion.establecer('reconectando');
		this.reintentos += 1;
		const espera = Math.min(1000 * 2 ** this.reintentos, 15000);
		this.temporizadorReconexion = setTimeout(() => this.abrirSocket(), espera);
	}
}

/** Instancia unica del cliente de tiempo real. */
export const tiempoReal = new TiempoReal();
