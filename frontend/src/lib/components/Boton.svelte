<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';

	type Variante = 'primario' | 'secundario' | 'peligro' | 'fantasma';

	interface Props extends HTMLButtonAttributes {
		variante?: Variante;
		tipo?: 'button' | 'submit' | 'reset';
		cargando?: boolean;
		clase?: string;
		children: Snippet;
	}

	let {
		variante = 'primario',
		tipo = 'button',
		cargando = false,
		clase = '',
		onclick,
		disabled,
		children,
		...resto
	}: Props = $props();

	const estilos: Record<Variante, string> = {
		primario: 'bg-marca-600 text-white hover:bg-marca-700 shadow-sm',
		secundario: 'bg-white text-marca-700 border border-borde hover:bg-marca-50',
		peligro: 'bg-peligro-600 text-white hover:bg-peligro-700 shadow-sm',
		fantasma: 'bg-transparent text-texto-suave hover:bg-black/5'
	};
</script>

<button
	type={tipo}
	class="inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 {estilos[
		variante
	]} {clase}"
	disabled={disabled || cargando}
	aria-busy={cargando}
	{onclick}
	{...resto}
>
	{#if cargando}
		<span
			class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
			aria-hidden="true"
		></span>
	{/if}
	{@render children()}
</button>
