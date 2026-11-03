<script lang="ts">
	import '../app.css';
	import { goto } from '$app/navigation';
	import { alExpirarSesion } from '#lib/api/cliente.ts';
	import Toast from '#lib/components/Toast.svelte';
	import { sesion } from '#lib/stores/sesion.svelte.ts';

	let { children } = $props();

	// Inicializacion del cliente (solo en el navegador).
	if (typeof window !== 'undefined') {
		sesion.vincularExpiracion();
		void sesion.iniciar();
		alExpirarSesion(() => {
			void goto('/login', { replaceState: true });
		});
	}
</script>

{@render children()}
<Toast />
