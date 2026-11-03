<script lang="ts">
	import { goto } from '$app/navigation';
	import { conexion } from '#lib/stores/conexion.svelte.ts';
	import { sesion } from '#lib/stores/sesion.svelte.ts';
	import { toasts } from '#lib/stores/toast.svelte.ts';

	interface Props {
		onalternar: () => void;
	}
	let { onalternar }: Props = $props();

	const coloresConexion: Record<string, string> = {
		conectado: 'bg-marca-500',
		conectando: 'bg-amber-400 animate-pulse',
		reconectando: 'bg-amber-400 animate-pulse',
		desconectado: 'bg-slate-400'
	};

	function cerrarSesion(): void {
		sesion.salir();
		toasts.info('Sesion cerrada', 'Hasta pronto.');
		goto('/login');
	}
</script>

<header
	class="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b border-borde bg-superficie/95 px-4 backdrop-blur sm:px-6"
>
	<div class="flex items-center gap-3">
		<button
			type="button"
			class="rounded-md p-2 text-texto-suave transition hover:bg-black/5 lg:hidden"
			aria-label="Abrir menu de navegacion"
			onclick={onalternar}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				class="h-6 w-6"
				aria-hidden="true"
			>
				<path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16" />
			</svg>
		</button>
		<div class="flex items-center gap-2">
			<span
				class="flex h-8 w-8 items-center justify-center rounded-lg bg-marca-600 text-sm font-bold text-white"
				aria-hidden="true">R</span
			>
			<span class="text-base font-semibold text-texto lg:hidden">ResiData</span>
		</div>
	</div>

	<div class="flex items-center gap-3">
		<!-- Indicador de conexion WebSocket -->
		<div
			class="hidden items-center gap-2 rounded-full border border-borde px-3 py-1 text-xs font-medium text-texto-suave sm:flex"
			role="status"
			aria-live="polite"
			title="Estado de la conexion en tiempo real"
		>
			<span class="h-2 w-2 rounded-full {coloresConexion[conexion.estado]}" aria-hidden="true"
			></span>
			<span>{conexion.etiqueta}</span>
		</div>

		<!-- Usuario -->
		<div class="flex items-center gap-3">
			<div class="hidden text-right sm:block">
				<p class="text-sm font-semibold leading-tight text-texto">{sesion.usuario?.nombre ?? ''}</p>
				<p class="text-xs capitalize leading-tight text-texto-suave">{sesion.nombreRol}</p>
			</div>
			<button
				type="button"
				class="flex items-center gap-2 rounded-lg border border-borde px-3 py-1.5 text-sm font-medium text-texto-suave transition hover:bg-black/5"
				onclick={cerrarSesion}
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
					<path stroke-linecap="round" stroke-linejoin="round" d="M15 17l5-5-5-5M20 12H9M12 4H5v16h7" />
				</svg>
				<span class="hidden sm:inline">Salir</span>
			</button>
		</div>
	</div>
</header>
