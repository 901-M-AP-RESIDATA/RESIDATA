<script lang="ts">
	interface Opcion {
		valor: string | number;
		etiqueta: string;
	}

	interface Props {
		id?: string;
		etiqueta: string;
		valor?: string | number;
		opciones: Opcion[];
		placeholder?: string;
		requerido?: boolean;
		deshabilitado?: boolean;
		error?: string | null;
		ayuda?: string;
	}

	let {
		id = `select-${Math.random().toString(36).slice(2, 9)}`,
		etiqueta,
		valor = $bindable(''),
		opciones,
		placeholder,
		requerido = false,
		deshabilitado = false,
		error = null,
		ayuda
	}: Props = $props();

	const idError = $derived(`${id}-error`);
</script>

<div class="flex flex-col gap-1">
	<label for={id} class="text-sm font-medium text-texto">
		{etiqueta}
		{#if requerido}<span class="text-peligro-600" aria-hidden="true">*</span>{/if}
	</label>
	<select
		{id}
		bind:value={valor}
		disabled={deshabilitado}
		required={requerido}
		aria-invalid={error ? true : undefined}
		aria-describedby={error ? idError : undefined}
		class="w-full rounded-lg border bg-white px-3 py-2 text-sm text-texto transition focus:border-marca-500 disabled:bg-black/5 {error
			? 'border-peligro-500'
			: 'border-borde'}"
	>
		{#if placeholder}<option value="">{placeholder}</option>{/if}
		{#each opciones as opcion (opcion.valor)}
			<option value={opcion.valor}>{opcion.etiqueta}</option>
		{/each}
	</select>
	{#if ayuda && !error}
		<p class="text-xs text-texto-suave">{ayuda}</p>
	{/if}
	{#if error}
		<p id={idError} class="text-xs font-medium text-peligro-600" role="alert">{error}</p>
	{/if}
</div>
