/**
 * Interfaces TypeScript del dominio ResiData.
 * Reflejan el contrato del backend FastAPI (prefijo /api/v1).
 */

// ---------------------------------------------------------------------
// Seguridad y usuarios
// ---------------------------------------------------------------------
export type NombreRol = 'administrador' | 'operador';

export interface Rol {
	id: number;
	nombre: NombreRol;
	descripcion: string | null;
}

export interface Usuario {
	id: number;
	nombre: string;
	correo: string;
	rol_id: number;
	rol?: Rol;
	activo: boolean;
	fecha_creacion: string;
	ultimo_acceso: string | null;
}

export interface CrearUsuario {
	nombre: string;
	correo: string;
	contrasena: string;
	rol_id: number;
	activo?: boolean;
}

export interface ActualizarUsuario {
	nombre?: string;
	correo?: string;
	contrasena?: string;
	rol_id?: number;
	activo?: boolean;
}

export interface RespuestaLogin {
	access_token: string;
	refresh_token: string;
	token_type: string;
}

// ---------------------------------------------------------------------
// Contenedores
// ---------------------------------------------------------------------
export type EstadoContenedorValor = 'activo' | 'inactivo' | 'mantenimiento';

export interface Contenedor {
	id: number;
	nombre: string;
	ubicacion: string;
	estado: EstadoContenedorValor;
	ultima_conexion: string | null;
	fecha_creacion: string;
}

/** Contenedor recien creado: incluye la API key en texto plano UNA sola vez. */
export interface ContenedorConApiKey extends Contenedor {
	api_key: string;
}

export interface CrearContenedor {
	nombre: string;
	ubicacion: string;
	estado?: EstadoContenedorValor;
}

export interface ActualizarContenedor {
	nombre?: string;
	ubicacion?: string;
	estado?: EstadoContenedorValor;
}

export interface EstadoContenedorDetalle {
	id: number;
	nombre: string;
	ubicacion: string;
	estado: EstadoContenedorValor;
	ultima_conexion: string | null;
	total_clasificaciones: number;
	ultima_clasificacion: string | null;
	ultima_categoria: string | null;
}

// ---------------------------------------------------------------------
// Categorias y clasificaciones
// ---------------------------------------------------------------------
export interface CategoriaResiduo {
	id: number;
	nombre: string;
	nivel_peligrosidad: number;
	color_bolsa: string;
	descripcion: string | null;
}

export interface HistoricoClasificacion {
	id: number;
	fecha_hora: string;
	contenedor_id: number;
	categoria_id: number;
	confianza: number;
	angulo: number;
	ruta_imagen: string;
	tiempo_inferencia_ms: number;
	corregida_manualmente: boolean;
	categoria_nombre?: string;
	contenedor_nombre?: string;
}

export interface FiltrosHistorico {
	fecha_desde?: string;
	fecha_hasta?: string;
	categoria?: string;
	contenedor_id?: number;
	pagina?: number;
	limite?: number;
}

// ---------------------------------------------------------------------
// Alertas
// ---------------------------------------------------------------------
export type TipoAlerta =
	| 'residuo_peligroso'
	| 'baja_confianza'
	| 'error_contenedor'
	| 'sistema';

export interface Alerta {
	id: number;
	historico_id: number;
	contenedor_id: number;
	tipo: TipoAlerta;
	mensaje: string;
	atendida: boolean;
	fecha_creacion: string;
	fecha_atencion: string | null;
	atendida_por: number | null;
	contenedor_nombre?: string;
	categoria_nombre?: string;
}

export interface FiltrosAlertas {
	atendida?: boolean;
	tipo?: TipoAlerta;
	contenedor_id?: number;
	pagina?: number;
	limite?: number;
}

// ---------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------
export interface ConteoCategoria {
	categoria: string;
	total: number;
}

export interface ConteoDia {
	dia: string;
	total: number;
}

export interface ResumenDashboard {
	total_hoy: number;
	total_historico: number;
	por_categoria: ConteoCategoria[];
	por_dia: ConteoDia[];
	confianza_promedio: number;
	alertas_pendientes: number;
	ultimas: HistoricoClasificacion[];
}

// ---------------------------------------------------------------------
// Paginacion generica
// ---------------------------------------------------------------------
export interface RespuestaPaginada<T> {
	items: T[];
	total: number;
	pagina: number;
	limite: number;
	paginas: number;
}

// ---------------------------------------------------------------------
// Eventos WebSocket
// ---------------------------------------------------------------------
export interface EventoNuevaClasificacion {
	tipo: 'nueva_clasificacion';
	data: HistoricoClasificacion;
}

export interface EventoAlertaPeligroso {
	tipo: 'alerta_peligroso';
	data: Alerta;
}

export type EventoWS = EventoNuevaClasificacion | EventoAlertaPeligroso;

// ---------------------------------------------------------------------
// Errores del API
// ---------------------------------------------------------------------
export interface CuerpoError {
	error?: {
		codigo: string;
		mensaje: string;
	};
	detail?: string;
}
