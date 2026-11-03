<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		titulo?: string;
		subtitulo?: string;
		clase?: string;
		acciones?: Snippet;
		pie?: Snippet;
		children: Snippet;
	}

	let { titulo, subtitulo, clase = '', acciones, pie, children }: Props = $props();
</script>

<section
	class="rounded-tarjeta border border-borde bg-superficie shadow-[0_1px_2px_rgba(16,24,40,0.04)] {clase}"
>
	{#if titulo || acciones}
		<header class="flex items-start justify-between gap-4 border-b border-borde px-5 py-4">
			<div>
				{#if titulo}<h2 class="text-base font-semibold text-texto">{titulo}</h2>{/if}
				{#if subtitulo}<p class="mt-0.5 text-sm text-texto-suave">{subtitulo}</p>{/if}
			</div>
			{#if acciones}
				<div class="flex shrink-0 items-center gap-2">{@render acciones()}</div>
			{/if}
		</header>
	{/if}
	<div class="px-5 py-4">
		{@render children()}
	</div>
	{#if pie}
		<footer class="border-t border-borde px-5 py-3">{@render pie()}</footer>
	{/if}
</section>
