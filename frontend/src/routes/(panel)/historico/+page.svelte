<script lang="ts">
	import { onMount } from 'svelte';
	import { ErrorApi } from '#lib/api/cliente.ts';
	import { listarCategorias } from '#lib/api/catalogos.ts';
	import { listarContenedores } from '#lib/api/contenedores.ts';
	import { listarHistorico } from '#lib/api/historico.ts';
	import Boton from '#lib/components/Boton.svelte';
	import Cargando from '#lib/components/Cargando.svelte';
	import EstadoVacio from '#lib/components/EstadoVacio.svelte';
	import Insignia from '#lib/components/Insignia.svelte';
	import Tarjeta from '#lib/components/Tarjeta.svelte';
	import { tiempoReal } from '#lib/stores/tiempoReal.ts';
	import { toasts } from '#lib/stores/toast.svelte.ts';
	import type {
		CategoriaResiduo,
		Contenedor,
		EventoWS,
		FiltrosHistorico,
		HistoricoClasificacion
	} from '#lib/tipos/index.ts';
	import { descargarCsv, generarCsv, type ColumnaCsv } from '#lib/util/csv.ts';
	import {
		formatearFechaHora,
		formatearPorcentaje,
		varianteCategoria
	} from '#lib/util/formato.ts';

	const LIMITE = 15;

	let desde = $state('');
	let hasta = $state('');
	let categoria = $state('');
	let contenedorId = $state<number | ''>('');

	let pagina = $state(1);
	let items = $state<HistoricoClasificacion[]>([]);
	let total = $state(0);
	let paginas = $state(1);
	let cargando = $state(false);
	let error = $state<string | null>(null);
	let exportando = $state(false);

	let categorias = $state<CategoriaResiduo[]>([]);
	let contenedores = $state<Contenedor[]>([]);

	function filtros(): FiltrosHistorico {
		return {
			fecha_desde: desde || undefined,
			fecha_hasta: hasta || undefined,
			categoria: categoria || undefined,
			contenedor_id: contenedorId === '' ? undefined : contenedorId,
			pagina,
			limite: LIMITE
		};
	}

	function coincide(registro: HistoricoClasificacion): boolean {
		const fecha = registro.fecha_hora.slice(0, 10);
		if (desde && fecha < desde) return false;
		if (hasta && fecha > hasta) return false;
		if (categoria && (registro.categoria_nombre ?? '').toLowerCase() !== categoria.toLowerCase())
			return false;
		if (contenedorId !== '' && registro.contenedor_id !== contenedorId) return false;
		return true;
	}

	function alRecibirEvento(evento: EventoWS): void {
		if (evento.tipo !== 'nueva_clasificacion') return;
		if (pagina !== 1 || !coincide(evento.data)) return;
		items = [evento.data, ...items].slice(0, LIMITE);
		total += 1;
	}

	async function cargar(): Promise<void> {
		cargando = true;
		error = null;
		try {
			const respuesta = await listarHistorico(filtros());
			items = respuesta.items;
			total = respuesta.total;
			paginas = respuesta.paginas;
		} catch (e) {
			error = e instanceof ErrorApi ? e.message : 'No se pudo cargar el historico.';
		} finally {
			cargando = false;
		}
	}

	function aplicar(): void {
		pagina = 1;
		void cargar();
	}

	function limpiar(): void {
		desde = '';
		hasta = '';
		categoria = '';
		contenedorId = '';
		pagina = 1;
		void cargar();
	}

	function cambiarPagina(destino: number): void {
		if (destino < 1 || destino > paginas || destino === pagina) return;
		pagina = destino;
		void cargar();
	}

	const columnasCsv: Array<ColumnaCsv<HistoricoClasificacion>> = [
		{ titulo: 'Fecha y hora', valor: (f) => f.fecha_hora },
		{ titulo: 'Categoria', valor: (f) => f.categoria_nombre ?? '' },
		{ titulo: 'Contenedor', valor: (f) => f.contenedor_nombre ?? '' },
		{ titulo: 'Confianza', valor: (f) => formatearPorcentaje(f.confianza) },
		{ titulo: 'Angulo', valor: (f) => f.angulo },
		{ titulo: 'Tiempo inferencia (ms)', valor: (f) => f.tiempo_inferencia_ms },
		{ titulo: 'Corregida manualmente', valor: (f) => (f.corregida_manualmente ? 'Si' : 'No') },
		{ titulo: 'Ruta imagen', valor: (f) => f.ruta_imagen }
	];

	async function exportar(): Promise<void> {
		exportando = true;
		try {
			const respuesta = await listarHistorico({ ...filtros(), pagina: 1, limite: 1000 });
			const csv = generarCsv(respuesta.items, columnasCsv);
			const marca = new Date().toISOString().slice(0, 10);
			descargarCsv(`historico_residata_${marca}.csv`, csv);
			toasts.exito('Exportacion lista', `${respuesta.items.length} registros exportados.`);
		} catch (e) {
			toasts.error(
				'No se pudo exportar',
				e instanceof ErrorApi ? e.message : 'Intenta de nuevo.'
			);
		} finally {
			exportando = false;
		}
	}

	onMount(() => {
		void Promise.all([listarCategorias(), listarContenedores()])
			.then(([cats, conts]) => {
				categorias = cats;
				contenedores = conts.items;
			})
			.catch(() => {
				// Los selectores quedan vacios si falla la carga de catalogos.
			});
		void cargar();
		return tiempoReal.suscribir(alRecibirEvento);
	});

	const inicio = $derived(total === 0 ? 0 : (pagina - 1) * LIMITE + 1);
	const fin = $derived(Math.min(pagina * LIMITE, total));
</script>

<div class="space-y-5">
	<Tarjeta>
		<form
			class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
			onsubmit={(evento) => {
				evento.preventDefault();
				aplicar();
			}}
		>
			<div>
				<label class="mb-1 block text-sm font-medium text-texto" for="f-desde">Desde</label>
				<input
					id="f-desde"
					type="date"
					bind:value={desde}
					class="w-full rounded-lg border border-borde bg-white px-3 py-2 text-sm text-texto focus:border-marca-500"
				/>
			</div>
			<div>
				<label class="mb-1 block text-sm font-medium text-texto" for="f-hasta">Hasta</label>
				<input
					id="f-hasta"
					type="date"
					bind:value={hasta}
					class="w-full rounded-lg border border-borde bg-white px-3 py-2 text-sm text-texto focus:border-marca-500"
				/>
			</div>
			<div>
				<label class="mb-1 block text-sm font-medium text-texto" for="f-categoria">Categoría</label>
				<select
					id="f-categoria"
					bind:value={categoria}
					class="w-full rounded-lg border border-borde bg-white px-3 py-2 text-sm text-texto focus:border-marca-500"
				>
					<option value="">Todas</option>
					{#each categorias as cat (cat.id)}
						<option value={cat.nombre}>{cat.nombre}</option>
					{/each}
				</select>
			</div>
			<div>
				<label class="mb-1 block text-sm font-medium text-texto" for="f-contenedor">
					Contenedor
				</label>
				<select
					id="f-contenedor"
					bind:value={contenedorId}
					class="w-full rounded-lg border border-borde bg-white px-3 py-2 text-sm text-texto focus:border-marca-500"
				>
					<option value="">Todos</option>
					{#each contenedores as cont (cont.id)}
						<option value={cont.id}>{cont.nombre}</option>
					{/each}
				</select>
			</div>

			<div class="flex flex-wrap gap-2 sm:col-span-2 lg:col-span-4">
				<Boton tipo="submit" cargando={cargando}>Buscar</Boton>
				<Boton variante="secundario" onclick={limpiar}>Limpiar</Boton>
			</div>
		</form>
	</Tarjeta>

	<Tarjeta>
		<div class="mb-4 flex flex-wrap items-center justify-between gap-3">
			<p class="text-sm text-texto-suave">
				{#if total > 0}
					Mostrando <span class="font-semibold text-texto">{inicio}–{fin}</span> de
					<span class="font-semibold text-texto">{total}</span> registros
				{:else}
					Sin registros
				{/if}
			</p>
			<Boton
				variante="secundario"
				cargando={exportando}
				disabled={total === 0}
				onclick={exportar}
			>
				Exportar CSV
			</Boton>
		</div>

		{#if cargando && items.length === 0}
			<Cargando mensaje="Cargando historico..." />
		{:else if error}
			<EstadoVacio titulo="No se pudo cargar el historico" mensaje={error}>
				{#snippet accion()}
					<Boton variante="secundario" onclick={cargar}>Reintentar</Boton>
				{/snippet}
			</EstadoVacio>
		{:else if items.length === 0}
			<EstadoVacio
				titulo="Sin clasificaciones"
				mensaje="No hay registros que coincidan con los filtros seleccionados."
			/>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full min-w-[40rem] border-collapse text-sm">
					<thead>
						<tr
							class="border-b border-borde text-left text-xs uppercase tracking-wide text-texto-suave"
						>
							<th class="px-3 py-2 font-semibold">Fecha y hora</th>
							<th class="px-3 py-2 font-semibold">Categoría</th>
							<th class="px-3 py-2 font-semibold">Contenedor</th>
							<th class="px-3 py-2 font-semibold">Confianza</th>
							<th class="px-3 py-2 font-semibold">Inferencia</th>
							<th class="px-3 py-2 font-semibold">Origen</th>
						</tr>
					</thead>
					<tbody>
						{#each items as fila (fila.id)}
							<tr class="border-b border-borde/70 last:border-0 hover:bg-black/[0.02]">
								<td class="px-3 py-2.5 text-texto-suave">
									{formatearFechaHora(fila.fecha_hora)}
								</td>
								<td class="px-3 py-2.5">
									<Insignia variante={varianteCategoria(fila.categoria_nombre)}>
										{fila.categoria_nombre ?? `Cat. ${fila.categoria_id}`}
									</Insignia>
								</td>
								<td class="px-3 py-2.5 text-texto">
									{fila.contenedor_nombre ?? `#${fila.contenedor_id}`}
								</td>
								<td class="px-3 py-2.5 font-medium text-texto">
									{formatearPorcentaje(fila.confianza)}
								</td>
								<td class="px-3 py-2.5 text-texto-suave">{fila.tiempo_inferencia_ms} ms</td>
								<td class="px-3 py-2.5">
									{#if fila.corregida_manualmente}
										<Insignia variante="ambar">Corregida</Insignia>
									{:else}
										<span class="text-texto-suave">Automática</span>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			{#if paginas > 1}
				<div class="mt-4 flex items-center justify-between gap-3">
					<Boton
						variante="secundario"
						disabled={pagina <= 1}
						onclick={() => cambiarPagina(pagina - 1)}
					>
						Anterior
					</Boton>
					<p class="text-sm text-texto-suave">Página {pagina} de {paginas}</p>
					<Boton
						variante="secundario"
						disabled={pagina >= paginas}
						onclick={() => cambiarPagina(pagina + 1)}
					>
						Siguiente
					</Boton>
				</div>
			{/if}
		{/if}
	</Tarjeta>
</div>
