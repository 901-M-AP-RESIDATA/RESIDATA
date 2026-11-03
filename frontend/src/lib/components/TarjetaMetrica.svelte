<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variante = 'verde' | 'azul' | 'ambar' | 'peligro' | 'gris';

	interface Props {
		etiqueta: string;
		valor: string;
		detalle?: string;
		variante?: Variante;
		icono?: Snippet;
	}

	let { etiqueta, valor, detalle, variante = 'verde', icono }: Props = $props();

	const estilos: Record<Variante, string> = {
		verde: 'bg-marca-50 text-marca-700',
		azul: 'bg-sky-50 text-sky-700',
		ambar: 'bg-amber-50 text-amber-700',
		peligro: 'bg-peligro-500/10 text-peligro-700',
		gris: 'bg-black/5 text-texto-suave'
	};
</script>

<div class="rounded-tarjeta border border-borde bg-superficie p-5 shadow-[0_1px_2px_rgba(16,24,40,0.04)]">
	<div class="flex items-center justify-between gap-3">
		<p class="text-sm font-medium text-texto-suave">{etiqueta}</p>
		<span
			class="flex h-9 w-9 items-center justify-center rounded-lg {estilos[variante]}"
			aria-hidden="true"
		>
			{#if icono}
				{@render icono()}
			{/if}
		</span>
	</div>
	<p class="mt-3 text-2xl font-bold text-texto">{valor}</p>
	{#if detalle}
		<p class="mt-1 text-xs text-texto-suave">{detalle}</p>
	{/if}
</div>
