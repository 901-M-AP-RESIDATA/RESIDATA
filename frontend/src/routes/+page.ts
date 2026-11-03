import { redirect } from '@sveltejs/kit';

// La raiz redirige al dashboard (que aplicara el guard de sesion).
export function load(): void {
	throw redirect(307, '/dashboard');
}
