import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

// ResiData - frontend SPA (SvelteKit en modo cliente con adapter-static).
export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Fuerza el modo runes de Svelte 5 salvo en dependencias.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			// SPA: se genera un index.html de respaldo para el enrutado en cliente.
			adapter: adapter({ fallback: 'index.html' })
		})
	]
});
