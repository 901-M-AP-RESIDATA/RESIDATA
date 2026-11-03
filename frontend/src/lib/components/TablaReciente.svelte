<script lang="ts">
	import type { HistoricoClasificacion } from '#lib/tipos/index.ts';
	import Insignia from '#lib/components/Insignia.svelte';
	import { formatearFechaHora, formatearPorcentaje, varianteCategoria } from '#lib/util/formato.ts';

	interface Props {
		filas: HistoricoClasificacion[];
	}

	let { filas }: Props = $props();
</script>

<div class="overflow-x-auto">
	<table class="w-full min-w-[34rem] border-collapse text-sm">
		<thead>
			<tr class="border-b border-borde text-left text-xs uppercase tracking-wide text-texto-suave">
				<th class="px-3 py-2 font-semibold">Fecha y hora</th>
				<th class="px-3 py-2 font-semibold">Categoria</th>
				<th class="px-3 py-2 font-semibold">Contenedor</th>
				<th class="px-3 py-2 font-semibold">Confianza</th>
				<th class="px-3 py-2 font-semibold">Inferencia</th>
			</tr>
		</thead>
		<tbody>
			{#each filas as fila (fila.id)}
				<tr class="border-b border-borde/70 last:border-0 hover:bg-black/[0.02]">
					<td class="px-3 py-2.5 text-texto-suave">{formatearFechaHora(fila.fecha_hora)}</td>
					<td class="px-3 py-2.5">
						<Insignia variante={varianteCategoria(fila.categoria_nombre)}>
							{fila.categoria_nombre ?? `Cat. ${fila.categoria_id}`}
						</Insignia>
					</td>
					<td class="px-3 py-2.5 text-texto">{fila.contenedor_nombre ?? `#${fila.contenedor_id}`}</td>
					<td class="px-3 py-2.5 font-medium text-texto">{formatearPorcentaje(fila.confianza)}</td>
					<td class="px-3 py-2.5 text-texto-suave">{fila.tiempo_inferencia_ms} ms</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
