<script lang="ts">
	import { toasts, type TipoToast } from '#lib/stores/toast.svelte.ts';

	const estilos: Record<TipoToast, string> = {
		exito: 'border-marca-300 bg-marca-50 text-marca-900',
		info: 'border-sky-300 bg-sky-50 text-sky-900',
		error: 'border-peligro-300 bg-peligro-500/10 text-peligro-700',
		peligro: 'border-peligro-500 bg-peligro-600 text-white'
	};

	const iconos: Record<TipoToast, string> = {
		exito: 'M5 13l4 4L19 7',
		info: 'M12 8h.01M11 12h1v4h1',
		error: 'M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z',
		peligro: 'M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z'
	};
</script>

<div
	class="pointer-events-none fixed right-4 top-4 z-[60] flex w-[min(92vw,22rem)] flex-col gap-2"
	role="region"
	aria-label="Notificaciones"
>
	{#each toasts.items as toast (toast.id)}
		<div
			class="pointer-events-auto flex items-start gap-3 rounded-lg border px-4 py-3 shadow-lg {estilos[
				toast.tipo
			]}"
			role="alert"
			aria-live={toast.tipo === 'peligro' ? 'assertive' : 'polite'}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				class="mt-0.5 h-5 w-5 shrink-0"
				aria-hidden="true"
			>
				<path stroke-linecap="round" stroke-linejoin="round" d={iconos[toast.tipo]} />
			</svg>
			<div class="min-w-0 flex-1">
				<p class="text-sm font-semibold">{toast.titulo}</p>
				{#if toast.mensaje}
					<p class="mt-0.5 text-sm opacity-90">{toast.mensaje}</p>
				{/if}
			</div>
			<button
				type="button"
				class="rounded p-1 opacity-70 transition hover:opacity-100"
				aria-label="Cerrar notificacion"
				onclick={() => toasts.cerrar(toast.id)}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					class="h-4 w-4"
					aria-hidden="true"
				>
					<path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" />
				</svg>
			</button>
		</div>
	{/each}
</div>
