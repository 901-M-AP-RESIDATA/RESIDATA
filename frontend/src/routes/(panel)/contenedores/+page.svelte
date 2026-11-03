<script lang="ts">
	import { onMount } from 'svelte';
	import { ErrorApi } from '#lib/api/cliente.ts';
	import {
		actualizarContenedor,
		crearContenedor,
		eliminarContenedor,
		listarContenedores,
		obtenerContenedor,
		regenerarClaveContenedor
	} from '#lib/api/contenedores.ts';
	import Boton from '#lib/components/Boton.svelte';
	import CampoSelect from '#lib/components/CampoSelect.svelte';
	import CampoTexto from '#lib/components/CampoTexto.svelte';
	import Cargando from '#lib/components/Cargando.svelte';
	import EstadoVacio from '#lib/components/EstadoVacio.svelte';
	import Insignia from '#lib/components/Insignia.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import Tarjeta from '#lib/components/Tarjeta.svelte';
	import { toasts } from '#lib/stores/toast.svelte.ts';
	import type {
		Contenedor,
		EstadoContenedorDetalle,
		EstadoContenedorValor
	} from '#lib/tipos/index.ts';
	import { formatearFechaHora } from '#lib/util/formato.ts';

	const opcionesEstado = [
		{ valor: 'activo', etiqueta: 'Activo' },
		{ valor: 'inactivo', etiqueta: 'Inactivo' },
		{ valor: 'mantenimiento', etiqueta: 'Mantenimiento' }
	];

	function varianteEstado(estado: EstadoContenedorValor): 'verde' | 'gris' | 'ambar' {
		if (estado === 'activo') return 'verde';
		if (estado === 'mantenimiento') return 'ambar';
		return 'gris';
	}

	function etiquetaEstado(estado: EstadoContenedorValor): string {
		return opcionesEstado.find((o) => o.valor === estado)?.etiqueta ?? estado;
	}

	let items = $state<Contenedor[]>([]);
	let cargando = $state(true);
	let error = $state<string | null>(null);

	let modalForm = $state(false);
	let modo = $state<'crear' | 'editar'>('crear');
	let editandoId = $state<number | null>(null);
	let form = $state({ nombre: '', ubicacion: '', estado: 'activo' as EstadoContenedorValor });
	let errores = $state<{ nombre?: string; ubicacion?: string }>({});
	let guardando = $state(false);

	let modalDetalle = $state(false);
	let detalle = $state<EstadoContenedorDetalle | null>(null);
	let cargandoDetalle = $state(false);

	let modalClave = $state(false);
	let clave = $state('');

	let modalEliminar = $state(false);
	let aEliminar = $state<Contenedor | null>(null);
	let eliminando = $state(false);

	async function cargar(): Promise<void> {
		cargando = true;
		error = null;
		try {
			const respuesta = await listarContenedores();
			items = respuesta.items;
		} catch (e) {
			error = e instanceof ErrorApi ? e.message : 'No se pudieron cargar los contenedores.';
		} finally {
			cargando = false;
		}
	}

	function abrirCrear(): void {
		modo = 'crear';
		editandoId = null;
		form = { nombre: '', ubicacion: '', estado: 'activo' };
		errores = {};
		modalForm = true;
	}

	function abrirEditar(contenedor: Contenedor): void {
		modo = 'editar';
		editandoId = contenedor.id;
		form = {
			nombre: contenedor.nombre,
			ubicacion: contenedor.ubicacion,
			estado: contenedor.estado
		};
		errores = {};
		modalForm = true;
	}

	async function guardar(): Promise<void> {
		errores = {};
		if (!form.nombre.trim()) errores.nombre = 'El nombre es obligatorio.';
		if (!form.ubicacion.trim()) errores.ubicacion = 'La ubicacion es obligatoria.';
		if (errores.nombre || errores.ubicacion) return;

		guardando = true;
		try {
			if (modo === 'crear') {
				const creado = await crearContenedor({
					nombre: form.nombre.trim(),
					ubicacion: form.ubicacion.trim(),
					estado: form.estado
				});
				modalForm = false;
				clave = creado.api_key;
				modalClave = true;
				toasts.exito('Contenedor creado', 'Guarda la API key: no volvera a mostrarse.');
			} else if (editandoId !== null) {
				await actualizarContenedor(editandoId, {
					nombre: form.nombre.trim(),
					ubicacion: form.ubicacion.trim(),
					estado: form.estado
				});
				modalForm = false;
				toasts.exito('Contenedor actualizado');
			}
			await cargar();
		} catch (e) {
			toasts.error('No se pudo guardar', e instanceof ErrorApi ? e.message : 'Intenta de nuevo.');
		} finally {
			guardando = false;
		}
	}

	async function abrirDetalle(contenedor: Contenedor): Promise<void> {
		modalDetalle = true;
		cargandoDetalle = true;
		detalle = null;
		try {
			detalle = await obtenerContenedor(contenedor.id);
		} catch (e) {
			toasts.error('No se pudo cargar', e instanceof ErrorApi ? e.message : 'Intenta de nuevo.');
			modalDetalle = false;
		} finally {
			cargandoDetalle = false;
		}
	}

	async function regenerar(contenedor: Contenedor): Promise<void> {
		try {
			const resultado = await regenerarClaveContenedor(contenedor.id);
			clave = resultado.api_key;
			modalClave = true;
			toasts.exito('API key regenerada', 'La clave anterior dejo de ser valida.');
		} catch (e) {
			toasts.error('No se pudo regenerar', e instanceof ErrorApi ? e.message : 'Intenta de nuevo.');
		}
	}

	function abrirEliminar(contenedor: Contenedor): void {
		aEliminar = contenedor;
		modalEliminar = true;
	}

	async function confirmarEliminar(): Promise<void> {
		if (!aEliminar) return;
		eliminando = true;
		try {
			await eliminarContenedor(aEliminar.id);
			modalEliminar = false;
			toasts.exito('Contenedor eliminado');
			await cargar();
		} catch (e) {
			toasts.error('No se pudo eliminar', e instanceof ErrorApi ? e.message : 'Intenta de nuevo.');
		} finally {
			eliminando = false;
			aEliminar = null;
		}
	}

	async function copiarClave(): Promise<void> {
		try {
			await navigator.clipboard.writeText(clave);
			toasts.exito('Copiada', 'La API key se copio al portapapeles.');
		} catch {
			toasts.error('No se pudo copiar', 'Copia la clave manualmente.');
		}
	}

	onMount(cargar);
</script>

<Tarjeta>
	{#snippet acciones()}
		<Boton onclick={abrirCrear}>Nuevo contenedor</Boton>
	{/snippet}

	{#if cargando && items.length === 0}
		<Cargando mensaje="Cargando contenedores..." />
	{:else if error}
		<EstadoVacio titulo="No se pudieron cargar los contenedores" mensaje={error}>
			{#snippet accion()}
				<Boton variante="secundario" onclick={cargar}>Reintentar</Boton>
			{/snippet}
		</EstadoVacio>
	{:else if items.length === 0}
		<EstadoVacio
			titulo="Sin contenedores"
			mensaje="Crea el primer contenedor para empezar a clasificar residuos."
		>
			{#snippet accion()}
				<Boton onclick={abrirCrear}>Nuevo contenedor</Boton>
			{/snippet}
		</EstadoVacio>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full min-w-[42rem] border-collapse text-sm">
				<thead>
					<tr
						class="border-b border-borde text-left text-xs uppercase tracking-wide text-texto-suave"
					>
						<th class="px-3 py-2 font-semibold">Nombre</th>
						<th class="px-3 py-2 font-semibold">Ubicación</th>
						<th class="px-3 py-2 font-semibold">Estado</th>
						<th class="px-3 py-2 font-semibold">Última conexión</th>
						<th class="px-3 py-2 text-right font-semibold">Acciones</th>
					</tr>
				</thead>
				<tbody>
					{#each items as contenedor (contenedor.id)}
						<tr class="border-b border-borde/70 last:border-0 hover:bg-black/[0.02]">
							<td class="px-3 py-2.5 font-medium text-texto">{contenedor.nombre}</td>
							<td class="px-3 py-2.5 text-texto-suave">{contenedor.ubicacion}</td>
							<td class="px-3 py-2.5">
								<Insignia variante={varianteEstado(contenedor.estado)}>
									{etiquetaEstado(contenedor.estado)}
								</Insignia>
							</td>
							<td class="px-3 py-2.5 text-texto-suave">
								{contenedor.ultima_conexion
									? formatearFechaHora(contenedor.ultima_conexion)
									: '—'}
							</td>
							<td class="px-3 py-2.5">
								<div class="flex justify-end gap-1">
									<Boton variante="fantasma" clase="px-2 py-1" onclick={() => abrirDetalle(contenedor)}>
										Ver
									</Boton>
									<Boton variante="fantasma" clase="px-2 py-1" onclick={() => abrirEditar(contenedor)}>
										Editar
									</Boton>
									<Boton variante="fantasma" clase="px-2 py-1" onclick={() => regenerar(contenedor)}>
										Clave
									</Boton>
									<Boton
										variante="fantasma"
										clase="px-2 py-1 text-peligro-600"
										onclick={() => abrirEliminar(contenedor)}
									>
										Eliminar
									</Boton>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</Tarjeta>

<!-- Modal de formulario -->
<Modal
	bind:abierto={modalForm}
	titulo={modo === 'crear' ? 'Nuevo contenedor' : 'Editar contenedor'}
>
	<form
		class="space-y-4"
		onsubmit={(evento) => {
			evento.preventDefault();
			void guardar();
		}}
	>
		<CampoTexto
			etiqueta="Nombre"
			bind:valor={form.nombre}
			requerido
			error={errores.nombre ?? null}
			placeholder="Contenedor Patio A"
		/>
		<CampoTexto
			etiqueta="Ubicación"
			bind:valor={form.ubicacion}
			requerido
			error={errores.ubicacion ?? null}
			placeholder="Edificio A - Patio central"
		/>
		<CampoSelect
			etiqueta="Estado"
			bind:valor={form.estado}
			opciones={opcionesEstado}
		/>
	</form>

	{#snippet pie()}
		<Boton variante="secundario" onclick={() => (modalForm = false)}>Cancelar</Boton>
		<Boton cargando={guardando} onclick={guardar}>
			{modo === 'crear' ? 'Crear' : 'Guardar'}
		</Boton>
	{/snippet}
</Modal>

<!-- Modal de detalle -->
<Modal bind:abierto={modalDetalle} titulo="Detalle del contenedor">
	{#if cargandoDetalle}
		<Cargando mensaje="Cargando detalle..." />
	{:else if detalle}
		<dl class="grid grid-cols-1 gap-3 sm:grid-cols-2">
			<div>
				<dt class="text-xs uppercase tracking-wide text-texto-suave">Nombre</dt>
				<dd class="text-sm font-medium text-texto">{detalle.nombre}</dd>
			</div>
			<div>
				<dt class="text-xs uppercase tracking-wide text-texto-suave">Estado</dt>
				<dd class="mt-0.5">
					<Insignia variante={varianteEstado(detalle.estado)}>
						{etiquetaEstado(detalle.estado)}
					</Insignia>
				</dd>
			</div>
			<div class="sm:col-span-2">
				<dt class="text-xs uppercase tracking-wide text-texto-suave">Ubicación</dt>
				<dd class="text-sm text-texto">{detalle.ubicacion}</dd>
			</div>
			<div>
				<dt class="text-xs uppercase tracking-wide text-texto-suave">Clasificaciones</dt>
				<dd class="text-sm font-semibold text-texto">{detalle.total_clasificaciones}</dd>
			</div>
			<div>
				<dt class="text-xs uppercase tracking-wide text-texto-suave">Última conexión</dt>
				<dd class="text-sm text-texto">
					{detalle.ultima_conexion ? formatearFechaHora(detalle.ultima_conexion) : '—'}
				</dd>
			</div>
			<div>
				<dt class="text-xs uppercase tracking-wide text-texto-suave">
					Última clasificación
				</dt>
				<dd class="text-sm text-texto">
					{detalle.ultima_clasificacion
						? formatearFechaHora(detalle.ultima_clasificacion)
						: 'Sin actividad'}
				</dd>
			</div>
			<div>
				<dt class="text-xs uppercase tracking-wide text-texto-suave">Última categoría</dt>
				<dd class="text-sm text-texto">{detalle.ultima_categoria ?? '—'}</dd>
			</div>
		</dl>
	{/if}

	{#snippet pie()}
		<Boton variante="secundario" onclick={() => (modalDetalle = false)}>Cerrar</Boton>
	{/snippet}
</Modal>

<!-- Modal de API key -->
<Modal bind:abierto={modalClave} titulo="API key del contenedor" tamano="md">
	<div class="space-y-3">
		<p class="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
			Copia y guarda esta clave ahora. No volverá a mostrarse.
		</p>
		<div class="flex items-center gap-2">
			<input
				readonly
				value={clave}
				class="w-full rounded-lg border border-borde bg-black/5 px-3 py-2 font-mono text-sm text-texto"
				aria-label="API key"
			/>
			<Boton variante="secundario" onclick={copiarClave}>Copiar</Boton>
		</div>
	</div>

	{#snippet pie()}
		<Boton onclick={() => (modalClave = false)}>Entendido</Boton>
	{/snippet}
</Modal>

<!-- Modal de eliminación -->
<Modal bind:abierto={modalEliminar} titulo="Eliminar contenedor" tamano="sm">
	<p class="text-sm text-texto">
		¿Seguro que deseas eliminar
		<span class="font-semibold">{aEliminar?.nombre}</span>? Esta acción no se puede deshacer.
	</p>

	{#snippet pie()}
		<Boton variante="secundario" onclick={() => (modalEliminar = false)}>Cancelar</Boton>
		<Boton variante="peligro" cargando={eliminando} onclick={confirmarEliminar}>Eliminar</Boton>
	{/snippet}
</Modal>
