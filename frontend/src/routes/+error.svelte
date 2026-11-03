<script lang="ts">
	import { page } from '$app/state';

	const titulos: Record<number, string> = {
		404: 'Pagina no encontrada',
		403: 'Acceso denegado',
		500: 'Error interno'
	};
</script>

<div class="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
	<p class="text-6xl font-bold text-marca-600">{page.status}</p>
	<h1 class="text-xl font-semibold text-texto">
		{titulos[page.status] ?? 'Ha ocurrido un problema'}
	</h1>
	<p class="max-w-md text-sm text-texto-suave">
		{page.error?.message ?? 'Intenta volver al panel principal.'}
	</p>
	<a
		href="/dashboard"
		class="rounded-lg bg-marca-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-marca-700"
		>Volver al panel</a
	>
</div>
