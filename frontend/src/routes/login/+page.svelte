<script lang="ts">
	import { goto } from '$app/navigation';
	import { ErrorApi } from '#lib/api/cliente.ts';
	import Boton from '#lib/components/Boton.svelte';
	import CampoTexto from '#lib/components/CampoTexto.svelte';
	import { sesion } from '#lib/stores/sesion.svelte.ts';

	let correo = $state('');
	let contrasena = $state('');
	let enviando = $state(false);
	let errorGeneral = $state<string | null>(null);
	let errorCorreo = $state<string | null>(null);
	let errorContrasena = $state<string | null>(null);

	const regexCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

	function validar(): boolean {
		errorCorreo = null;
		errorContrasena = null;

		if (!correo.trim()) {
			errorCorreo = 'El correo es obligatorio.';
		} else if (!regexCorreo.test(correo.trim())) {
			errorCorreo = 'Introduce un correo valido.';
		}

		if (!contrasena) {
			errorContrasena = 'La contrasena es obligatoria.';
		} else if (contrasena.length < 6) {
			errorContrasena = 'La contrasena debe tener al menos 6 caracteres.';
		}

		return !errorCorreo && !errorContrasena;
	}

	async function enviar(evento: SubmitEvent): Promise<void> {
		evento.preventDefault();
		errorGeneral = null;
		if (!validar()) return;

		enviando = true;
		try {
			await sesion.entrar(correo.trim(), contrasena);
			await goto('/dashboard', { replaceState: true });
		} catch (error) {
			if (error instanceof ErrorApi) {
				errorGeneral =
					error.estado === 401
						? 'Credenciales incorrectas. Verifica tu correo y contrasena.'
						: error.message;
			} else {
				errorGeneral = 'No se pudo iniciar sesion. Intenta de nuevo.';
			}
		} finally {
			enviando = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-fondo px-4 py-10">
	<div class="w-full max-w-md">
		<div class="mb-6 flex flex-col items-center gap-2 text-center">
			<span
				class="flex h-14 w-14 items-center justify-center rounded-2xl bg-marca-600 text-2xl font-bold text-white"
				aria-hidden="true">R</span
			>
			<h1 class="text-2xl font-bold text-texto">ResiData</h1>
			<p class="text-sm text-texto-suave">Panel de control de residuos inteligente</p>
		</div>

		<form
			class="space-y-4 rounded-tarjeta border border-borde bg-superficie p-6 shadow-sm"
			onsubmit={enviar}
			novalidate
		>
			<h2 class="text-lg font-semibold text-texto">Iniciar sesion</h2>

			{#if errorGeneral}
				<div
					class="rounded-lg border border-peligro-300 bg-peligro-500/10 px-3 py-2 text-sm text-peligro-700"
					role="alert"
				>
					{errorGeneral}
				</div>
			{/if}

			<CampoTexto
				etiqueta="Correo electronico"
				tipo="email"
				bind:valor={correo}
				placeholder="usuario@residata.local"
				autocomplete="username"
				requerido
				error={errorCorreo}
			/>

			<CampoTexto
				etiqueta="Contrasena"
				tipo="password"
				bind:valor={contrasena}
				placeholder="••••••••"
				autocomplete="current-password"
				requerido
				error={errorContrasena}
			/>

			<Boton tipo="submit" cargando={enviando} clase="w-full">
				{enviando ? 'Ingresando...' : 'Ingresar'}
			</Boton>

			{#if import.meta.env.VITE_USAR_MOCK === 'true'}
				<p class="text-center text-xs text-texto-suave">
					Modo demo: admin@residata.local / admin123
				</p>
			{/if}
		</form>

		<p class="mt-6 text-center text-xs text-texto-suave">ResiData v1.0.0 — 2026</p>
	</div>
</div>
