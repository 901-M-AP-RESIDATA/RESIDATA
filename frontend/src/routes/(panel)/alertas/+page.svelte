<script lang="ts">
	import { ErrorApi } from '#lib/api/cliente.ts';
	import { listarAlertas } from '#lib/api/alertas.ts';
	import Boton from '#lib/components/Boton.svelte';
	import Cargando from '#lib/components/Cargando.svelte';
	import EstadoVacio from '#lib/components/EstadoVacio.svelte';
	import Insignia from '#lib/components/Insignia.svelte';
	import Tarjeta from '#lib/components/Tarjeta.svelte';
	import { alertas } from '#lib/stores/alertas.svelte.ts';
	import { toasts } from '#lib/stores/toast.svelte.ts';
	import type { Alerta, TipoAlerta } from '#lib/tipos/index.ts';
	import {
		etiquetaTipoAlerta,
		formatearFechaHora,
		varianteTipoAlerta
	} from '#lib/util/formato.ts';

	type Vista = 'pendientes' | 'atendidas' | 'todas';

	const TIPOS: TipoAlerta[] = [
		'residuo_peligroso',
		'baja_confianza',
		'error_contenedor',
		'sistema'
	];

	const vistas: Array<{ valor: Vista; etiqueta: string }> = [
		{ valor: 'pendientes', etiqueta: 'Pendientes' },
		{ valor: 'atendidas', etiqueta: 'Atendidas' },
		{ valor: 'todas', etiqueta: 'Todas' }
	];

	let vista = $state<Vista>('pendientes');
	let filtroTipo = $state<TipoAlerta | ''>('');
	let lista = $state<Alerta[]>([]);
	let cargando = $state(false);
	let error = $state<string | null>(null);
	let atendiendoId = $state<number | null>(null);

	const pendientesFiltradas = $derived(
		filtroTipo ? alertas.pendientes.filter((a) => a.tipo === filtroTipo) : alertas.pendientes
	);

	const mostradas = $derived(vista === 'pendientes' ? pendientesFiltradas : lista);

	async function cargarLista(v: Vista, t: TipoAlerta | ''): Promise<void> {
		cargando = true;
		error = null;
		try {
			const respuesta = await listarAlertas({
				atendida: v === 'atendidas' ? true : undefined,
				tipo: t || undefined,
				limite: 50
			});
			lista = respuesta.items;
		} catch (e) {
			error = e instanceof ErrorApi ? e.message : 'No se pudieron cargar las alertas.';
		} finally {
			cargando = false;
		}
	}

	function cambiarVista(v: Vista): void {
		vista = v;
		if (v !== 'pendientes') void cargarLista(v, filtroTipo);
	}

	function cambiarTipo(evento: Event): void {
		const valor = (evento.currentTarget as HTMLSelectElement).value as TipoAlerta | '';
		filtroTipo = valor;
		if (vista !== 'pendientes') void cargarLista(vista, valor);
	}

	async function alAtender(alerta: Alerta): Promise<void> {
		atendiendoId = alerta.id;
		try {
			await alertas.atender(alerta.id);
			if (vista !== 'pendientes') {
				await cargarLista(vista, filtroTipo);
			}
		} catch (e) {
			toasts.error(
				'No se pudo atender',
				e instanceof ErrorApi ? e.message : 'Intenta de nuevo.'
			);
		} finally {
			atendiendoId = null;
		}
	}

	async function alRefrescar(): Promise<void> {
		if (vista === 'pendientes') {
			await alertas.cargar();
		} else {
			await cargarLista(vista, filtroTipo);
		}
	}
</script>

<div class="space-y-5">
	<Tarjeta>
		<div class="flex flex-wrap items-center justify-between gap-3">
			<div
				class="inline-flex rounded-lg border border-borde bg-white p-0.5"
				role="group"
				aria-label="Estado de las alertas"
			>
				{#each vistas as opcion (opcion.valor)}
					<button
						type="button"
						class="rounded-md px-3 py-1.5 text-sm font-medium transition {vista ===
						opcion.valor
							? 'bg-marca-600 text-white'
							: 'text-texto-suave hover:bg-black/5'}"
						aria-pressed={vista === opcion.valor}
						onclick={() => cambiarVista(opcion.valor)}
					>
						{opcion.etiqueta}
					</button>
				{/each}
			</div>

			<div class="flex flex-wrap items-center gap-2">
				<label class="sr-only" for="filtro-tipo">Filtrar por tipo</label>
				<select
					id="filtro-tipo"
					value={filtroTipo}
					onchange={cambiarTipo}
					class="rounded-lg border border-borde bg-white px-3 py-2 text-sm text-texto focus:border-marca-500"
				>
					<option value="">Todos los tipos</option>
					{#each TIPOS as tipo (tipo)}
						<option value={tipo}>{etiquetaTipoAlerta(tipo)}</option>
					{/each}
				</select>

				<Boton
					variante={alertas.sonidoActivo ? 'secundario' : 'fantasma'}
					onclick={() => alertas.alternarSonido()}
					aria-pressed={alertas.sonidoActivo}
					title={alertas.sonidoActivo ? 'Silenciar alertas' : 'Activar sonido'}
				>
					{alertas.sonidoActivo ? 'Sonido activo' : 'Sin sonido'}
				</Boton>

				<Boton variante="secundario" cargando={cargando} onclick={alRefrescar}>
					Actualizar
				</Boton>
			</div>
		</div>
	</Tarjeta>

	{#if cargando && mostradas.length === 0}
		<Tarjeta>
			<Cargando mensaje="Cargando alertas..." />
		</Tarjeta>
	{:else if error}
		<Tarjeta>
			<EstadoVacio titulo="No se pudieron cargar las alertas" mensaje={error}>
				{#snippet accion()}
					<Boton variante="secundario" onclick={alRefrescar}>Reintentar</Boton>
				{/snippet}
			</EstadoVacio>
		</Tarjeta>
	{:else if mostradas.length === 0}
		<Tarjeta>
			<EstadoVacio
				titulo={vista === 'pendientes' ? 'Sin alertas pendientes' : 'Sin resultados'}
				mensaje={vista === 'pendientes'
					? 'Todo en orden. Las alertas de residuo peligroso apareceran aqui en tiempo real.'
					: 'No hay alertas que coincidan con los filtros seleccionados.'}
			/>
		</Tarjeta>
	{:else}
		<ul class="space-y-3">
			{#each mostradas as alerta (alerta.id)}
				{@const esPeligro = alerta.tipo === 'residuo_peligroso'}
				<li
					class="rounded-tarjeta border bg-superficie p-4 shadow-sm {esPeligro
						? 'border-peligro-300'
						: 'border-borde'}"
				>
					<div class="flex flex-wrap items-start gap-3">
						<span
							class="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full {esPeligro
								? 'bg-peligro-500/10 text-peligro-700'
								: 'bg-black/5 text-texto-suave'}"
							aria-hidden="true"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.8"
								class="h-5 w-5"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z"
								/>
							</svg>
						</span>

						<div class="min-w-0 flex-1">
							<div class="flex flex-wrap items-center gap-2">
								<Insignia variante={varianteTipoAlerta(alerta.tipo)}>
									{etiquetaTipoAlerta(alerta.tipo)}
								</Insignia>
								{#if alerta.atendida}
									<Insignia variante="verde">Atendida</Insignia>
								{/if}
								<span class="text-xs text-texto-suave">
									{formatearFechaHora(alerta.fecha_creacion)}
								</span>
							</div>
							<p class="mt-1.5 text-sm font-medium text-texto">{alerta.mensaje}</p>
							<p class="mt-0.5 text-xs text-texto-suave">
								{alerta.contenedor_nombre ?? `Contenedor #${alerta.contenedor_id}`}
								{#if alerta.categoria_nombre}· {alerta.categoria_nombre}{/if}
								{#if alerta.atendida && alerta.fecha_atencion}
									· Atendida el {formatearFechaHora(alerta.fecha_atencion)}
								{/if}
							</p>
						</div>

						{#if !alerta.atendida}
							<Boton
								variante="secundario"
								cargando={atendiendoId === alerta.id}
								onclick={() => alAtender(alerta)}
							>
								Marcar atendida
							</Boton>
						{/if}
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</div>
