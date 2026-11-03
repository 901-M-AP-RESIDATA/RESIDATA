<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		abierto?: boolean;
		titulo: string;
		tamano?: 'sm' | 'md' | 'lg';
		oncerrar?: () => void;
		children: Snippet;
		pie?: Snippet;
	}

	let { abierto = $bindable(false), titulo, tamano = 'md', oncerrar, children, pie }: Props =
		$props();

	let contenedor = $state<HTMLDivElement>();

	const anchos = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' };

	function cerrar(): void {
		abierto = false;
		oncerrar?.();
	}

	$effect(() => {
		if (!abierto) return;
		const manejarTecla = (evento: KeyboardEvent) => {
			if (evento.key === 'Escape') cerrar();
		};
		window.addEventListener('keydown', manejarTecla);
		document.body.style.overflow = 'hidden';
		requestAnimationFrame(() => {
			const foco = contenedor?.querySelector<HTMLElement>('[data-autofoco]');
			(foco ?? contenedor)?.focus();
		});
		return () => {
			window.removeEventListener('keydown', manejarTecla);
			document.body.style.overflow = '';
		};
	});
</script>

{#if abierto}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<!-- Capa oscura -->
		<div
			class="absolute inset-0 bg-black/40"
			role="presentation"
			onclick={cerrar}
		></div>

		<div
			bind:this={contenedor}
			class="relative z-10 w-full {anchos[tamano]} max-h-[90vh] overflow-y-auto rounded-tarjeta bg-superficie shadow-xl"
			role="dialog"
			aria-modal="true"
			aria-label={titulo}
			tabindex="-1"
		>
			<header class="flex items-center justify-between border-b border-borde px-5 py-4">
				<h2 class="text-base font-semibold text-texto">{titulo}</h2>
				<button
					type="button"
					class="rounded-md p-1 text-texto-suave transition hover:bg-black/5"
					aria-label="Cerrar"
					onclick={cerrar}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						class="h-5 w-5"
						aria-hidden="true"
					>
						<path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" />
					</svg>
				</button>
			</header>

			<div class="px-5 py-4">
				{@render children()}
			</div>

			{#if pie}
				<footer class="flex justify-end gap-2 border-t border-borde px-5 py-4">
					{@render pie()}
				</footer>
			{/if}
		</div>
	</div>
{/if}
