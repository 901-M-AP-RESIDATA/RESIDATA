<script lang="ts">
	import type { FullAutoFill } from 'svelte/elements';

	interface Props {
		id?: string;
		etiqueta: string;
		tipo?: 'text' | 'email' | 'password' | 'number' | 'date' | 'search';
		valor?: string | number;
		placeholder?: string;
		requerido?: boolean;
		autocomplete?: FullAutoFill;
		error?: string | null;
		deshabilitado?: boolean;
		ayuda?: string;
	}

	let {
		id = `campo-${Math.random().toString(36).slice(2, 9)}`,
		etiqueta,
		tipo = 'text',
		valor = $bindable(''),
		placeholder = '',
		requerido = false,
		autocomplete = 'off',
		error = null,
		deshabilitado = false,
		ayuda
	}: Props = $props();

	const idError = $derived(`${id}-error`);
</script>

<div class="flex flex-col gap-1">
	<label for={id} class="text-sm font-medium text-texto">
		{etiqueta}
		{#if requerido}<span class="text-peligro-600" aria-hidden="true">*</span>{/if}
	</label>
	<input
		{id}
		type={tipo}
		bind:value={valor}
		{placeholder}
		{autocomplete}
		disabled={deshabilitado}
		required={requerido}
		aria-invalid={error ? true : undefined}
		aria-describedby={error ? idError : undefined}
		class="w-full rounded-lg border bg-white px-3 py-2 text-sm text-texto transition placeholder:text-texto-suave/60 focus:border-marca-500 disabled:bg-black/5 {error
			? 'border-peligro-500'
			: 'border-borde'}"
	/>
	{#if ayuda && !error}
		<p class="text-xs text-texto-suave">{ayuda}</p>
	{/if}
	{#if error}
		<p id={idError} class="text-xs font-medium text-peligro-600" role="alert">{error}</p>
	{/if}
</div>
