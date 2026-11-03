<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variante = 'verde' | 'azul' | 'rojo' | 'gris' | 'ambar';

	interface Props {
		variante?: Variante;
		clase?: string;
		children: Snippet;
	}

	let { variante = 'gris', clase = '', children }: Props = $props();

	const estilos: Record<Variante, string> = {
		verde: 'bg-marca-100 text-marca-800',
		azul: 'bg-sky-100 text-sky-800',
		rojo: 'bg-peligro-500/10 text-peligro-700',
		gris: 'bg-black/5 text-texto-suave',
		ambar: 'bg-amber-100 text-amber-800'
	};
</script>

<span
	class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold {estilos[
		variante
	]} {clase}"
>
	{@render children()}
</span>
