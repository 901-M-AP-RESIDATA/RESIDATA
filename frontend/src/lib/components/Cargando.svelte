<script lang="ts">
	interface Props {
		mensaje?: string;
		/** Clases adicionales para el contenedor. */
		clase?: string;
	}
	let { mensaje = 'Cargando...', clase = '' }: Props = $props();
</script>

<div
	class="flex flex-col items-center justify-center gap-3 py-10 text-texto-suave {clase}"
	role="status"
	aria-live="polite"
>
	<span
		class="h-8 w-8 animate-spin rounded-full border-3 border-marca-200 border-t-marca-600"
		aria-hidden="true"
	></span>
	<span class="text-sm">{mensaje}</span>
</div>
