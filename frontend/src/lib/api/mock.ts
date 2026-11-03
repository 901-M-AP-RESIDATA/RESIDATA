/**
 * Datos simulados para desarrollar el frontend sin backend.
 *
 * Se activa con `VITE_USAR_MOCK=true`. Implementa las mismas rutas que el
 * backend real y comparte la forma de los tipos de `#lib/tipos`.
 * En fases posteriores se amplia con contenedores, historico, alertas y
 * dashboard.
 */

import type {
	ActualizarContenedor,
	ActualizarUsuario,
	Alerta,
	Contenedor,
	ContenedorConApiKey,
	CategoriaResiduo,
	CrearContenedor,
	CrearUsuario,
	EstadoContenedorDetalle,
	EstadoContenedorValor,
	EventoWS,
	HistoricoClasificacion,
	ResumenDashboard,
	RespuestaLogin,
	Rol,
	Usuario
} from '#lib/tipos/index.ts';
import { ErrorApi, type OpcionesPeticion } from './cliente';

const RETARDO_MS = 220;

// ---------------------------------------------------------------------
// Datos simulados
// ---------------------------------------------------------------------
const ROL_ADMIN: Rol = { id: 1, nombre: 'administrador', descripcion: 'Acceso total.' };
const ROL_OPER: Rol = { id: 2, nombre: 'operador', descripcion: 'Consulta y alertas.' };
const ROLES: Rol[] = [ROL_ADMIN, ROL_OPER];

const USUARIOS: Array<Usuario & { contrasena: string }> = [
	{
		id: 1,
		nombre: 'Administrador ResiData',
		correo: 'admin@residata.local',
		contrasena: 'admin123',
		rol_id: 1,
		rol: ROL_ADMIN,
		activo: true,
		fecha_creacion: new Date().toISOString(),
		ultimo_acceso: null
	},
	{
		id: 2,
		nombre: 'Operador de Turno',
		correo: 'operador@residata.local',
		contrasena: 'operador123',
		rol_id: 2,
		rol: ROL_OPER,
		activo: true,
		fecha_creacion: new Date().toISOString(),
		ultimo_acceso: null
	}
];

const CATEGORIAS: CategoriaResiduo[] = [
	{ id: 1, nombre: 'Organico', nivel_peligrosidad: 1, color_bolsa: 'verde', descripcion: null },
	{ id: 2, nombre: 'Inorganico', nivel_peligrosidad: 2, color_bolsa: 'azul', descripcion: null },
	{ id: 3, nombre: 'Peligroso', nivel_peligrosidad: 3, color_bolsa: 'rojo', descripcion: null }
];

const CONTENEDORES: Contenedor[] = [
	{
		id: 1,
		nombre: 'Contenedor Patio A',
		ubicacion: 'Edificio A - Patio central',
		estado: 'activo',
		ultima_conexion: new Date().toISOString(),
		fecha_creacion: new Date().toISOString()
	},
	{
		id: 2,
		nombre: 'Contenedor Entrada B',
		ubicacion: 'Edificio B - Acceso principal',
		estado: 'activo',
		ultima_conexion: new Date(Date.now() - 3600_000).toISOString(),
		fecha_creacion: new Date().toISOString()
	}
];

let usuarioActual: Usuario | null = null;
let secuenciaId = 100;
const siguienteId = () => ++secuenciaId;

// ---------------------------------------------------------------------
// Generadores de datos simulados
// ---------------------------------------------------------------------
const ANGULOS_POR_CATEGORIA: Record<number, number> = { 1: 0, 2: 90, 3: 180 };

function generarClasificacion(id: number, haceMs = 0): HistoricoClasificacion {
	const categoria = CATEGORIAS[Math.floor(Math.random() * CATEGORIAS.length)];
	const contenedor = CONTENEDORES[Math.floor(Math.random() * CONTENEDORES.length)];
	const confianza = Math.round((0.75 + Math.random() * 0.24) * 100) / 100;
	return {
		id,
		fecha_hora: new Date(Date.now() - haceMs).toISOString(),
		contenedor_id: contenedor.id,
		categoria_id: categoria.id,
		confianza,
		angulo: ANGULOS_POR_CATEGORIA[categoria.id] ?? 0,
		ruta_imagen: `storage/imagenes/clasificacion_${id}.jpg`,
		tiempo_inferencia_ms: Math.round(180 + Math.random() * 420),
		corregida_manualmente: false,
		categoria_nombre: categoria.nombre,
		contenedor_nombre: contenedor.nombre
	};
}

function generarAlerta(id: number, haceMs = 0, atendida = false): Alerta {
	const clasificacion = generarClasificacion(id, haceMs);
	return {
		id,
		historico_id: clasificacion.id,
		contenedor_id: clasificacion.contenedor_id,
		tipo: 'residuo_peligroso',
		mensaje: 'Se detecto un residuo peligroso. Requiere atencion.',
		atendida,
		fecha_creacion: new Date(Date.now() - haceMs).toISOString(),
		fecha_atencion: atendida ? new Date(Date.now() - haceMs + 120_000).toISOString() : null,
		atendida_por: atendida ? USUARIOS[0].id : null,
		contenedor_nombre: clasificacion.contenedor_nombre,
		categoria_nombre: clasificacion.categoria_nombre
	};
}

const ALERTAS: Alerta[] = [
	generarAlerta(3001, 5 * 60_000, false),
	generarAlerta(3002, 42 * 60_000, false),
	generarAlerta(3003, 3 * 3600_000, false),
	generarAlerta(3004, 20 * 3600_000, true),
	generarAlerta(3005, 30 * 3600_000, true)
];

const alertasPendientes = () => ALERTAS.filter((a) => !a.atendida).length;

const HISTORICO: HistoricoClasificacion[] = Array.from({ length: 180 }, (_, indice) =>
	generarClasificacion(2000 + indice, indice * 160 * 60_000 + Math.floor(Math.random() * 120_000))
).sort((a, b) => b.fecha_hora.localeCompare(a.fecha_hora));

function generarResumen(): ResumenDashboard {
	const por_categoria = CATEGORIAS.map((categoria) => ({
		categoria: categoria.nombre,
		total: 12 + Math.floor(Math.random() * 60)
	}));

	const por_dia = Array.from({ length: 7 }, (_, indice) => {
		const fecha = new Date(Date.now() - (6 - indice) * 86_400_000);
		return {
			dia: fecha.toISOString().slice(0, 10),
			total: 8 + Math.floor(Math.random() * 35)
		};
	});

	const total_historico = por_categoria.reduce((acumulado, c) => acumulado + c.total, 0);

	const ultimas = Array.from({ length: 8 }, (_, indice) =>
		generarClasificacion(1000 + indice, indice * 45_000)
	).sort((a, b) => b.fecha_hora.localeCompare(a.fecha_hora));

	return {
		total_hoy: por_dia[por_dia.length - 1].total,
		total_historico,
		por_categoria,
		por_dia,
		confianza_promedio: Math.round((0.83 + Math.random() * 0.12) * 100) / 100,
		alertas_pendientes: alertasPendientes(),
		ultimas
	};
}

// ---------------------------------------------------------------------
// Utilidades
// ---------------------------------------------------------------------
const esperar = (ms = RETARDO_MS) => new Promise((r) => setTimeout(r, ms));

function emitirTokens(usuario: Usuario): RespuestaLogin {
	const sello = usuario.rol?.nombre ?? 'operador';
	return {
		access_token: `mock-access-${sello}-${usuario.id}`,
		refresh_token: `mock-refresh-${sello}-${usuario.id}`,
		token_type: 'bearer'
	};
}

/** Genera una API key simulada en texto plano. */
function claveAleatoria(): string {
	return `rd_${Math.random().toString(36).slice(2, 12)}${Math.random().toString(36).slice(2, 12)}`;
}

/** Quita la contraseña antes de devolver un usuario por el API. */
function publicoUsuario(usuario: Usuario & { contrasena: string }): Usuario {
	const { contrasena: _contrasena, ...resto } = usuario;
	return resto;
}

// ---------------------------------------------------------------------
// Enrutador de mocks
// ---------------------------------------------------------------------
type ManejadorMock = (
	coincidencia: RegExpMatchArray,
	opciones: OpcionesPeticion,
	ruta: string
) => unknown | Promise<unknown>;

interface RutaMock {
	metodo: string;
	patron: RegExp;
	manejador: ManejadorMock;
}

const rutas: RutaMock[] = [];

function registrar(metodo: string, patron: RegExp, manejador: ManejadorMock): void {
	rutas.push({ metodo, patron, manejador });
}

// --- Auth -------------------------------------------------------------
registrar('POST', /^\/api\/v1\/auth\/login$/, async (_c, opciones) => {
	const cuerpo = (opciones.cuerpo ?? {}) as { username?: string; password?: string };
	// El cliente envia el formulario como objeto {username,password}.
	const usuario = USUARIOS.find((u) => u.correo === cuerpo.username);
	if (!usuario || usuario.contrasena !== cuerpo.password) {
		throw new ErrorApi(401, 'credenciales_invalidas', 'Correo o contrasena incorrectos.');
	}
	usuarioActual = { ...usuario, ultimo_acceso: new Date().toISOString() };
	return emitirTokens(usuarioActual);
});

registrar('POST', /^\/api\/v1\/auth\/refresh$/, async (_c, opciones) => {
	const cuerpo = (opciones.cuerpo ?? {}) as { refresh_token?: string };
	const id = Number(cuerpo.refresh_token?.split('-').pop());
	const usuario = USUARIOS.find((u) => u.id === id);
	if (!usuario) throw new ErrorApi(401, 'token_invalido', 'Token de refresco invalido.');
	usuarioActual = { ...usuario };
	return emitirTokens(usuarioActual);
});

registrar('GET', /^\/api\/v1\/auth\/me$/, async () => {
	if (!usuarioActual) throw new ErrorApi(401, 'no_autenticado', 'Sesion no valida.');
	return usuarioActual;
});

// --- Catalogos (fases posteriores amplian) ----------------------------
registrar('GET', /^\/api\/v1\/categorias$/, async () => CATEGORIAS);

// --- Dashboard --------------------------------------------------------
registrar('GET', /^\/api\/v1\/dashboard\/resumen$/, async () => generarResumen());

// --- Contenedores (CRUD) ----------------------------------------------
registrar('GET', /^\/api\/v1\/contenedores$/, async (_c, _o, ruta) => {
	const params = new URL(ruta, 'http://mock.local').searchParams;
	const pagina = Math.max(1, Number(params.get('pagina') ?? 1));
	const limite = Math.max(1, Number(params.get('limite') ?? 20));
	const inicio = (pagina - 1) * limite;
	return {
		items: CONTENEDORES.slice(inicio, inicio + limite),
		total: CONTENEDORES.length,
		pagina,
		limite,
		paginas: Math.max(1, Math.ceil(CONTENEDORES.length / limite))
	};
});

registrar('POST', /^\/api\/v1\/contenedores$/, async (_c, opciones) => {
	const cuerpo = (opciones.cuerpo ?? {}) as CrearContenedor;
	if (!cuerpo.nombre || !cuerpo.ubicacion) {
		throw new ErrorApi(422, 'datos_invalidos', 'El nombre y la ubicacion son obligatorios.');
	}
	const nuevo: Contenedor = {
		id: siguienteId(),
		nombre: cuerpo.nombre,
		ubicacion: cuerpo.ubicacion,
		estado: cuerpo.estado ?? 'activo',
		ultima_conexion: null,
		fecha_creacion: new Date().toISOString()
	};
	CONTENEDORES.push(nuevo);
	return { ...nuevo, api_key: claveAleatoria() } as ContenedorConApiKey;
});

registrar('GET', /^\/api\/v1\/contenedores\/(\d+)$/, async (coincidencia) => {
	const id = Number(coincidencia[1]);
	const contenedor = CONTENEDORES.find((c) => c.id === id);
	if (!contenedor) throw new ErrorApi(404, 'no_encontrado', 'El contenedor no existe.');
	const registros = HISTORICO.filter((h) => h.contenedor_id === id);
	const ultimo = registros.reduce<HistoricoClasificacion | null>(
		(acumulado, h) =>
			!acumulado || h.fecha_hora > acumulado.fecha_hora ? h : acumulado,
		null
	);
	return {
		id: contenedor.id,
		nombre: contenedor.nombre,
		ubicacion: contenedor.ubicacion,
		estado: contenedor.estado,
		ultima_conexion: contenedor.ultima_conexion,
		total_clasificaciones: registros.length,
		ultima_clasificacion: ultimo?.fecha_hora ?? null,
		ultima_categoria: ultimo?.categoria_nombre ?? null
	} as EstadoContenedorDetalle;
});

registrar('PATCH', /^\/api\/v1\/contenedores\/(\d+)$/, async (coincidencia, opciones) => {
	const id = Number(coincidencia[1]);
	const contenedor = CONTENEDORES.find((c) => c.id === id);
	if (!contenedor) throw new ErrorApi(404, 'no_encontrado', 'El contenedor no existe.');
	const cuerpo = (opciones.cuerpo ?? {}) as ActualizarContenedor;
	if (cuerpo.nombre !== undefined) contenedor.nombre = cuerpo.nombre;
	if (cuerpo.ubicacion !== undefined) contenedor.ubicacion = cuerpo.ubicacion;
	if (cuerpo.estado !== undefined) contenedor.estado = cuerpo.estado as EstadoContenedorValor;
	return contenedor;
});

registrar('DELETE', /^\/api\/v1\/contenedores\/(\d+)$/, async (coincidencia) => {
	const id = Number(coincidencia[1]);
	const indice = CONTENEDORES.findIndex((c) => c.id === id);
	if (indice < 0) throw new ErrorApi(404, 'no_encontrado', 'El contenedor no existe.');
	CONTENEDORES.splice(indice, 1);
	return undefined;
});

registrar('POST', /^\/api\/v1\/contenedores\/(\d+)\/regenerar-clave$/, async (coincidencia) => {
	const id = Number(coincidencia[1]);
	const contenedor = CONTENEDORES.find((c) => c.id === id);
	if (!contenedor) throw new ErrorApi(404, 'no_encontrado', 'El contenedor no existe.');
	return { ...contenedor, api_key: claveAleatoria() } as ContenedorConApiKey;
});

// --- Usuarios y roles -------------------------------------------------
registrar('GET', /^\/api\/v1\/roles$/, async () => ROLES);

registrar('GET', /^\/api\/v1\/usuarios$/, async (_c, _o, ruta) => {
	const params = new URL(ruta, 'http://mock.local').searchParams;
	const pagina = Math.max(1, Number(params.get('pagina') ?? 1));
	const limite = Math.max(1, Number(params.get('limite') ?? 20));
	const inicio = (pagina - 1) * limite;
	return {
		items: USUARIOS.slice(inicio, inicio + limite).map(publicoUsuario),
		total: USUARIOS.length,
		pagina,
		limite,
		paginas: Math.max(1, Math.ceil(USUARIOS.length / limite))
	};
});

registrar('POST', /^\/api\/v1\/usuarios$/, async (_c, opciones) => {
	const cuerpo = (opciones.cuerpo ?? {}) as CrearUsuario;
	if (!cuerpo.nombre || !cuerpo.correo || !cuerpo.contrasena || !cuerpo.rol_id) {
		throw new ErrorApi(422, 'datos_invalidos', 'Nombre, correo, contrasena y rol son obligatorios.');
	}
	if (USUARIOS.some((u) => u.correo.toLowerCase() === cuerpo.correo.toLowerCase())) {
		throw new ErrorApi(409, 'correo_duplicado', 'Ya existe un usuario con ese correo.');
	}
	const rol = ROLES.find((r) => r.id === cuerpo.rol_id);
	if (!rol) throw new ErrorApi(422, 'rol_invalido', 'El rol indicado no existe.');
	const nuevo: Usuario & { contrasena: string } = {
		id: siguienteId(),
		nombre: cuerpo.nombre,
		correo: cuerpo.correo,
		contrasena: cuerpo.contrasena,
		rol_id: cuerpo.rol_id,
		rol,
		activo: cuerpo.activo ?? true,
		fecha_creacion: new Date().toISOString(),
		ultimo_acceso: null
	};
	USUARIOS.push(nuevo);
	return publicoUsuario(nuevo);
});

registrar('GET', /^\/api\/v1\/usuarios\/(\d+)$/, async (coincidencia) => {
	const id = Number(coincidencia[1]);
	const usuario = USUARIOS.find((u) => u.id === id);
	if (!usuario) throw new ErrorApi(404, 'no_encontrado', 'El usuario no existe.');
	return publicoUsuario(usuario);
});

registrar('PATCH', /^\/api\/v1\/usuarios\/(\d+)$/, async (coincidencia, opciones) => {
	const id = Number(coincidencia[1]);
	const usuario = USUARIOS.find((u) => u.id === id);
	if (!usuario) throw new ErrorApi(404, 'no_encontrado', 'El usuario no existe.');
	const cuerpo = (opciones.cuerpo ?? {}) as ActualizarUsuario;
	if (cuerpo.correo && USUARIOS.some((u) => u.id !== id && u.correo.toLowerCase() === cuerpo.correo?.toLowerCase())) {
		throw new ErrorApi(409, 'correo_duplicado', 'Ya existe un usuario con ese correo.');
	}
	if (cuerpo.nombre !== undefined) usuario.nombre = cuerpo.nombre;
	if (cuerpo.correo !== undefined) usuario.correo = cuerpo.correo;
	if (cuerpo.contrasena) usuario.contrasena = cuerpo.contrasena;
	if (cuerpo.rol_id !== undefined) {
		const rol = ROLES.find((r) => r.id === cuerpo.rol_id);
		if (!rol) throw new ErrorApi(422, 'rol_invalido', 'El rol indicado no existe.');
		usuario.rol_id = cuerpo.rol_id;
		usuario.rol = rol;
	}
	if (cuerpo.activo !== undefined) usuario.activo = cuerpo.activo;
	return publicoUsuario(usuario);
});

registrar('DELETE', /^\/api\/v1\/usuarios\/(\d+)$/, async (coincidencia) => {
	const id = Number(coincidencia[1]);
	const indice = USUARIOS.findIndex((u) => u.id === id);
	if (indice < 0) throw new ErrorApi(404, 'no_encontrado', 'El usuario no existe.');
	USUARIOS.splice(indice, 1);
	return undefined;
});

// --- Historico --------------------------------------------------------
registrar('GET', /^\/api\/v1\/historico$/, async (_c, _o, ruta) => {
	const params = new URL(ruta, 'http://mock.local').searchParams;
	const desde = params.get('fecha_desde');
	const hasta = params.get('fecha_hasta');
	const categoria = params.get('categoria');
	const contenedorId = params.get('contenedor_id');
	const pagina = Math.max(1, Number(params.get('pagina') ?? 1));
	const limite = Math.min(1000, Math.max(1, Number(params.get('limite') ?? 20)));

	const filtradas = HISTORICO.filter((registro) => {
		const fecha = registro.fecha_hora.slice(0, 10);
		if (desde && fecha < desde) return false;
		if (hasta && fecha > hasta) return false;
		if (categoria && (registro.categoria_nombre ?? '').toLowerCase() !== categoria.toLowerCase())
			return false;
		if (contenedorId && String(registro.contenedor_id) !== contenedorId) return false;
		return true;
	});

	const inicio = (pagina - 1) * limite;
	return {
		items: filtradas.slice(inicio, inicio + limite),
		total: filtradas.length,
		pagina,
		limite,
		paginas: Math.max(1, Math.ceil(filtradas.length / limite))
	};
});

// --- Alertas ----------------------------------------------------------
registrar('GET', /^\/api\/v1\/alertas$/, async (_c, _o, ruta) => {
	const params = new URL(ruta, 'http://mock.local').searchParams;
	const filtroAtendida = params.get('atendida');
	const filtroTipo = params.get('tipo');
	const pagina = Math.max(1, Number(params.get('pagina') ?? 1));
	const limite = Math.max(1, Number(params.get('limite') ?? 20));

	const filtradas = ALERTAS.filter((alerta) => {
		if (filtroAtendida !== null && String(alerta.atendida) !== filtroAtendida) return false;
		if (filtroTipo && alerta.tipo !== filtroTipo) return false;
		return true;
	}).sort((a, b) => b.fecha_creacion.localeCompare(a.fecha_creacion));

	const inicio = (pagina - 1) * limite;
	return {
		items: filtradas.slice(inicio, inicio + limite),
		total: filtradas.length,
		pagina,
		limite,
		paginas: Math.max(1, Math.ceil(filtradas.length / limite))
	};
});

registrar('PATCH', /^\/api\/v1\/alertas\/(\d+)$/, async (coincidencia, opciones) => {
	const id = Number(coincidencia[1]);
	const alerta = ALERTAS.find((a) => a.id === id);
	if (!alerta) throw new ErrorApi(404, 'no_encontrado', 'La alerta no existe.');
	const cuerpo = (opciones.cuerpo ?? {}) as { atendida?: boolean };
	const atendida = cuerpo.atendida ?? true;
	alerta.atendida = atendida;
	alerta.fecha_atencion = atendida ? new Date().toISOString() : null;
	alerta.atendida_por = atendida ? (usuarioActual?.id ?? USUARIOS[0].id) : null;
	return alerta;
});

// ---------------------------------------------------------------------
// Punto de entrada
// ---------------------------------------------------------------------
export async function peticionMock<T>(ruta: string, opciones: OpcionesPeticion = {}): Promise<T> {
	await esperar();
	const metodo = (opciones.metodo ?? 'GET').toUpperCase();
	const sinQuery = ruta.split('?')[0];
	for (const entrada of rutas) {
		if (entrada.metodo !== metodo) continue;
		const coincidencia = sinQuery.match(entrada.patron);
		if (coincidencia) {
			return (await entrada.manejador(coincidencia, opciones, ruta)) as T;
		}
	}
	throw new ErrorApi(404, 'no_encontrado', `Ruta simulada no implementada: ${metodo} ${sinQuery}`);
}

/** Reinicia el estado simulado (util en pruebas). */
export function reiniciarMock(): void {
	usuarioActual = null;
	secuenciaId = 100;
}

/**
 * Simula el flujo de tiempo real emitiendo clasificaciones (y alguna alerta
 * de peligro) periodicamente. Devuelve una funcion para detenerlo.
 */
export function iniciarTiempoRealSimulado(
	emitir: (evento: EventoWS) => void,
	intervaloMs = 6000
): () => void {
	let id = 5000;
	const temporizador = setInterval(() => {
		id += 1;
		const clasificacion = generarClasificacion(id);
		HISTORICO.unshift(clasificacion);
		emitir({ tipo: 'nueva_clasificacion', data: clasificacion });

		const esPeligroso = clasificacion.categoria_nombre?.toLowerCase() === 'peligroso';
		if (esPeligroso && Math.random() < 0.6) {
			const alerta = generarAlerta(id);
			ALERTAS.unshift(alerta);
			emitir({ tipo: 'alerta_peligroso', data: alerta });
		}
	}, intervaloMs);

	return () => clearInterval(temporizador);
}

// Re-exportaciones usadas por otras partes de la app en modo mock.
export const _datosMock = {
	USUARIOS,
	CATEGORIAS,
	CONTENEDORES
};
export type { ContenedorConApiKey, Alerta, HistoricoClasificacion, ResumenDashboard };
