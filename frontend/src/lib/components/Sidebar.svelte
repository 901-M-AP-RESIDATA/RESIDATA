<script lang="ts">
	import { page } from '$app/state';
	import { alertas } from '#lib/stores/alertas.svelte.ts';
	import { sesion } from '#lib/stores/sesion.svelte.ts';

	interface Props {
		abierto?: boolean;
		oncerrar?: () => void;
	}
	let { abierto = $bindable(false), oncerrar }: Props = $props();

	interface ItemNav {
		ruta: string;
		etiqueta: string;
		icono: string;
		soloAdmin?: boolean;
	}

	const items: ItemNav[] = [
		{ ruta: '/dashboard', etiqueta: 'Dashboard', icono: 'M3 13h8V3H3v10Zm10 8h8V11h-8v10ZM3 21h8v-6H3v6Zm10-12h8V3h-8v6Z' },
		{ ruta: '/contenedores', etiqueta: 'Contenedores', icono: 'M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13' },
		{ ruta: '/historico', etiqueta: 'Historico', icono: 'M12 8v4l3 2M12 3a9 9 0 1 0 9 9' },
		{ ruta: '/alertas', etiqueta: 'Alertas', icono: 'M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z' },
		{ ruta: '/usuarios', etiqueta: 'Usuarios', icono: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm13 10v-2a4 4 0 0 0-3-3.87M16 3.13A4 4 0 0 1 16 11', soloAdmin: true }
	];

	const rutaActual = $derived(page.url.pathname);
	const estaActivo = (ruta: string) => rutaActual === ruta || rutaActual.startsWith(ruta + '/');
</script>

<!-- Capa para movil -->
{#if abierto}
	<div
		class="fixed inset-0 z-40 bg-black/40 lg:hidden"
		role="presentation"
		onclick={() => (abierto = false)}
	></div>
{/if}

<aside
	class="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-borde bg-superficie transition-transform duration-200 lg:static lg:translate-x-0 {abierto
		? 'translate-x-0'
		: '-translate-x-full'}"
	aria-label="Navegacion principal"
>
	<div class="flex h-16 items-center gap-2 border-b border-borde px-5">
		<span
			class="flex h-9 w-9 items-center justify-center rounded-lg bg-marca-600 text-base font-bold text-white"
			aria-hidden="true">R</span
		>
		<div>
			<p class="text-sm font-bold leading-tight text-texto">ResiData</p>
			<p class="text-xs leading-tight text-texto-suave">Panel de control</p>
		</div>
	</div>

	<nav class="flex-1 space-y-1 overflow-y-auto p-3">
		{#each items as item (item.ruta)}
			{#if !item.soloAdmin || sesion.esAdministrador}
				<a
					href={item.ruta}
					class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition {estaActivo(
						item.ruta
					)
						? 'bg-marca-50 text-marca-800'
						: 'text-texto-suave hover:bg-black/5 hover:text-texto'}"
					aria-current={estaActivo(item.ruta) ? 'page' : undefined}
					onclick={() => (abierto = false)}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						class="h-5 w-5 shrink-0"
						aria-hidden="true"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d={item.icono} />
					</svg>
					<span>{item.etiqueta}</span>
					{#if item.ruta === '/alertas' && alertas.total > 0}
						<span
							class="ml-auto inline-flex min-w-5 items-center justify-center rounded-full bg-peligro-600 px-1.5 text-xs font-semibold text-white"
							aria-label="{alertas.total} alertas pendientes"
						>
							{alertas.total > 99 ? '99+' : alertas.total}
						</span>
					{/if}
				</a>
			{/if}
		{/each}
	</nav>

	<div class="border-t border-borde p-4">
		<button
			type="button"
			class="w-full rounded-lg px-3 py-2 text-left text-xs text-texto-suave transition hover:bg-black/5 lg:hidden"
			onclick={() => (abierto = false)}
		>
			Cerrar menu
		</button>
		<p class="mt-2 text-xs text-texto-suave/70">ResiData v1.0.0</p>
	</div>
</aside>
