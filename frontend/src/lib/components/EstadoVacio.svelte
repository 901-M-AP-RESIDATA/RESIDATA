<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		titulo: string;
		mensaje?: string;
		icono?: Snippet;
		accion?: Snippet;
	}

	let { titulo, mensaje, icono, accion }: Props = $props();
</script>

<div class="flex flex-col items-center justify-center gap-3 px-6 py-12 text-center">
	<div class="flex h-14 w-14 items-center justify-center rounded-full bg-marca-50 text-marca-600">
		{#if icono}
			{@render icono()}
		{:else}
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="1.6"
				class="h-7 w-7"
				aria-hidden="true"
			>
				<path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" />
			</svg>
		{/if}
	</div>
	<div>
		<p class="text-base font-semibold text-texto">{titulo}</p>
		{#if mensaje}
			<p class="mt-1 max-w-md text-sm text-texto-suave">{mensaje}</p>
		{/if}
	</div>
	{#if accion}
		<div class="mt-2">{@render accion()}</div>
	{/if}
</div>
