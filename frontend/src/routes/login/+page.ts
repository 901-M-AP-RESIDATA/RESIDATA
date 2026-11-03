import { redirect } from '@sveltejs/kit';
import { sesion } from '#lib/stores/sesion.svelte.ts';

// Si ya hay sesion activa, no tiene sentido mostrar el login.
export function load(): void {
	if (sesion.autenticado) {
		throw redirect(307, '/dashboard');
	}
}
