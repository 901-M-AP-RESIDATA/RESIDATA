<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Cargando from '#lib/components/Cargando.svelte';
	import Navbar from '#lib/components/Navbar.svelte';
	import Sidebar from '#lib/components/Sidebar.svelte';
	import { alertas } from '#lib/stores/alertas.svelte.ts';
	import { sesion } from '#lib/stores/sesion.svelte.ts';
	import { tiempoReal } from '#lib/stores/tiempoReal.ts';

	let { children } = $props();

	let menuAbierto = $state(false);

	const tituloPagina = $derived.by(() => {
		const ruta = page.url.pathname;
		if (ruta.startsWith('/contenedores')) return 'Contenedores';
		if (ruta.startsWith('/historico')) return 'Historico';
		if (ruta.startsWith('/alertas')) return 'Alertas';
		if (ruta.startsWith('/usuarios')) return 'Usuarios';
		return 'Dashboard';
	});

	// Guard: cuando la sesion termina de inicializarse, si no hay usuario, al login.
	$effect(() => {
		if (sesion.inicializado && !sesion.autenticado) {
			void goto('/login', { replaceState: true });
		}
	});

	// Conecta el flujo de tiempo real y las alertas mientras haya sesion activa.
	$effect(() => {
		if (!sesion.autenticado) return;
		tiempoReal.conectar();
		alertas.iniciar();
		return () => {
			alertas.detener();
			tiempoReal.desconectar();
		};
	});
</script>

{#if sesion.autenticado}
	<div class="flex min-h-screen bg-fondo">
		<Sidebar bind:abierto={menuAbierto} />
		<div class="flex min-w-0 flex-1 flex-col">
			<Navbar onalternar={() => (menuAbierto = !menuAbierto)} />
			<main class="flex-1 px-4 py-6 sm:px-6 lg:px-8">
				<div class="mx-auto w-full max-w-6xl">
					<h1 class="mb-5 text-xl font-bold text-texto">{tituloPagina}</h1>
					{@render children()}
				</div>
			</main>
		</div>
	</div>
{:else}
	<div class="flex min-h-screen items-center justify-center bg-fondo">
		<Cargando mensaje="Verificando sesion..." />
	</div>
{/if}
