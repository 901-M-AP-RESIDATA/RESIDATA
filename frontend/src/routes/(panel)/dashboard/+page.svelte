<script lang="ts">
	import type { ChartConfiguration } from 'chart.js';
	import { onMount } from 'svelte';
	import { ErrorApi } from '#lib/api/cliente.ts';
	import { obtenerResumen } from '#lib/api/dashboard.ts';
	import Boton from '#lib/components/Boton.svelte';
	import Cargando from '#lib/components/Cargando.svelte';
	import EstadoVacio from '#lib/components/EstadoVacio.svelte';
	import Grafica from '#lib/components/Grafica.svelte';
	import Tarjeta from '#lib/components/Tarjeta.svelte';
	import TarjetaMetrica from '#lib/components/TarjetaMetrica.svelte';
	import TablaReciente from '#lib/components/TablaReciente.svelte';
	import { tiempoReal } from '#lib/stores/tiempoReal.ts';
	import type { EventoWS, ResumenDashboard } from '#lib/tipos/index.ts';
	import {
		COLORES,
		colorCategoria,
		formatearDia,
		formatearNumero,
		formatearPorcentaje
	} from '#lib/util/formato.ts';

	const MAX_ULTIMAS = 8;

	let resumen = $state<ResumenDashboard | null>(null);
	let cargando = $state(true);
	let error = $state<string | null>(null);
	let actualizadoEn = $state<Date | null>(null);

	async function cargar(): Promise<void> {
		cargando = true;
		error = null;
		try {
			resumen = await obtenerResumen();
			actualizadoEn = new Date();
		} catch (e) {
			error = e instanceof ErrorApi ? e.message : 'No se pudo cargar el resumen.';
		} finally {
			cargando = false;
		}
	}

	function alRecibirEvento(evento: EventoWS): void {
		if (!resumen) return;

		if (evento.tipo === 'nueva_clasificacion') {
			const clasificacion = evento.data;
			resumen.total_hoy += 1;
			resumen.total_historico += 1;
			resumen.ultimas = [clasificacion, ...resumen.ultimas].slice(0, MAX_ULTIMAS);
			const categoria = resumen.por_categoria.find(
				(c) => c.categoria === clasificacion.categoria_nombre
			);
			if (categoria) categoria.total += 1;
			actualizadoEn = new Date();
		} else if (evento.tipo === 'alerta_peligroso') {
			resumen.alertas_pendientes += 1;
		}
	}

	onMount(() => {
		void cargar();
		return tiempoReal.suscribir(alRecibirEvento);
	});

	const configDona = $derived<ChartConfiguration<'doughnut'>>({
		type: 'doughnut',
		data: {
			labels: resumen?.por_categoria.map((c) => c.categoria) ?? [],
			datasets: [
				{
					data: resumen?.por_categoria.map((c) => c.total) ?? [],
					backgroundColor: resumen?.por_categoria.map((c) => colorCategoria(c.categoria)) ?? [],
					borderWidth: 0
				}
			]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			cutout: '64%',
			plugins: {
				legend: { position: 'bottom', labels: { boxWidth: 12, usePointStyle: true } }
			}
		}
	});

	const configLineas = $derived<ChartConfiguration<'line'>>({
		type: 'line',
		data: {
			labels: resumen?.por_dia.map((d) => formatearDia(d.dia)) ?? [],
			datasets: [
				{
					label: 'Clasificaciones',
					data: resumen?.por_dia.map((d) => d.total) ?? [],
					borderColor: COLORES.verde,
					backgroundColor: 'rgba(12, 166, 120, 0.12)',
					pointBackgroundColor: COLORES.verde,
					fill: true,
					tension: 0.35
				}
			]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: { legend: { display: false } },
			scales: {
				y: { beginAtZero: true, ticks: { precision: 0 } },
				x: { grid: { display: false } }
			}
		}
	});
</script>

{#if cargando && !resumen}
	<Cargando mensaje="Cargando metricas..." clase="py-24" />
{:else if error && !resumen}
	<Tarjeta>
		<EstadoVacio titulo="No se pudieron cargar las metricas" mensaje={error}>
			{#snippet accion()}
				<Boton variante="secundario" onclick={cargar}>Reintentar</Boton>
			{/snippet}
		</EstadoVacio>
	</Tarjeta>
{:else if resumen}
	<div class="space-y-5">
		<div class="flex flex-wrap items-center justify-between gap-3">
			{#if actualizadoEn}
				<p class="text-xs text-texto-suave">
					Actualizado a las {actualizadoEn.toLocaleTimeString('es-MX')}
				</p>
			{/if}
			<Boton variante="secundario" onclick={cargar} cargando={cargando}>
				Actualizar
			</Boton>
		</div>

		<!-- KPIs -->
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
			<TarjetaMetrica
				etiqueta="Clasificaciones hoy"
				valor={formatearNumero(resumen.total_hoy)}
				variante="verde"
			>
				{#snippet icono()}
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-5 w-5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13h8V3H3v10Zm10 8h8V11h-8v10ZM3 21h8v-6H3v6Zm10-12h8V3h-8v6Z" /></svg>
				{/snippet}
			</TarjetaMetrica>

			<TarjetaMetrica
				etiqueta="Total historico"
				valor={formatearNumero(resumen.total_historico)}
				variante="azul"
			>
				{#snippet icono()}
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-5 w-5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 2M12 3a9 9 0 1 0 9 9" /></svg>
				{/snippet}
			</TarjetaMetrica>

			<TarjetaMetrica
				etiqueta="Confianza promedio"
				valor={formatearPorcentaje(resumen.confianza_promedio)}
				variante="verde"
			>
				{#snippet icono()}
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-5 w-5"><path stroke-linecap="round" stroke-linejoin="round" d="m5 13 4 4L19 7" /></svg>
				{/snippet}
			</TarjetaMetrica>

			<TarjetaMetrica
				etiqueta="Alertas pendientes"
				valor={formatearNumero(resumen.alertas_pendientes)}
				variante={resumen.alertas_pendientes > 0 ? 'peligro' : 'gris'}
				detalle={resumen.alertas_pendientes > 0 ? 'Requieren atencion' : 'Sin pendientes'}
			>
				{#snippet icono()}
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-5 w-5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z" /></svg>
				{/snippet}
			</TarjetaMetrica>
		</div>

		<!-- Graficas -->
		<div class="grid grid-cols-1 gap-4 lg:grid-cols-5">
			<Tarjeta titulo="Distribucion por categoria" clase="lg:col-span-2">
				<Grafica configuracion={configDona} alto="16rem" />
			</Tarjeta>

			<Tarjeta titulo="Clasificaciones (ultimos 7 dias)" clase="lg:col-span-3">
				<Grafica configuracion={configLineas} alto="16rem" />
			</Tarjeta>
		</div>

		<!-- Ultimas clasificaciones -->
		<Tarjeta titulo="Ultimas clasificaciones" subtitulo="Se actualiza en tiempo real">
			{#if resumen.ultimas.length > 0}
				<TablaReciente filas={resumen.ultimas} />
			{:else}
				<EstadoVacio
					titulo="Sin clasificaciones todavia"
					mensaje="Cuando la IA procese residuos, apareceran aqui al instante."
				/>
			{/if}
		</Tarjeta>
	</div>
{/if}
