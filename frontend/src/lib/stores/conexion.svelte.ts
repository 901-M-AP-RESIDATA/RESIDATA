/**
 * Store del estado de conexion en tiempo real (WebSocket).
 * El cliente WS lo actualiza; el indicador del Navbar lo consume.
 */

export type EstadoConexion = 'desconectado' | 'conectando' | 'conectado' | 'reconectando';

class AlmacenConexion {
	estado = $state<EstadoConexion>('desconectado');
	/** Marca de tiempo de la ultima actualizacion recibida. */
	ultimaActividad = $state<number | null>(null);

	establecer(estado: EstadoConexion): void {
		this.estado = estado;
	}

	marcarActividad(): void {
		this.ultimaActividad = Date.now();
	}

	get etiqueta(): string {
		switch (this.estado) {
			case 'conectado':
				return 'Conectado';
			case 'conectando':
				return 'Conectando';
			case 'reconectando':
				return 'Reconectando';
			default:
				return 'Desconectado';
		}
	}
}

/** Instancia unica del store de conexion. */
export const conexion = new AlmacenConexion();
