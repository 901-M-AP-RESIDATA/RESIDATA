/**
 * Sonido de alerta generado con Web Audio API (sin archivos de audio).
 *
 * Se crea el contexto de forma perezosa porque los navegadores requieren una
 * interaccion del usuario para poder reproducir audio.
 */

let contexto: AudioContext | null = null;

type ConstructorAudioContext = typeof AudioContext;

function obtenerContexto(): AudioContext | null {
	if (typeof window === 'undefined') return null;
	const Ctor: ConstructorAudioContext | undefined =
		window.AudioContext ??
		(window as unknown as { webkitAudioContext?: ConstructorAudioContext }).webkitAudioContext;
	if (!Ctor) return null;
	contexto ??= new Ctor();
	return contexto;
}

function emitirTono(tono: AudioContext, frecuencia: number, inicio: number, duracion: number): void {
	const oscilador = tono.createOscillator();
	const ganancia = tono.createGain();
	oscilador.type = 'sine';
	oscilador.frequency.setValueAtTime(frecuencia, inicio);
	ganancia.gain.setValueAtTime(0.0001, inicio);
	ganancia.gain.exponentialRampToValueAtTime(0.18, inicio + 0.02);
	ganancia.gain.exponentialRampToValueAtTime(0.0001, inicio + duracion);
	oscilador.connect(ganancia);
	ganancia.connect(tono.destination);
	oscilador.start(inicio);
	oscilador.stop(inicio + duracion);
}

/** Reproduce un aviso de dos tonos. Silencioso ante cualquier error. */
export function reproducirAlerta(): void {
	try {
		const tono = obtenerContexto();
		if (!tono) return;
		if (tono.state === 'suspended') void tono.resume();
		const ahora = tono.currentTime;
		emitirTono(tono, 880, ahora, 0.16);
		emitirTono(tono, 660, ahora + 0.2, 0.22);
	} catch {
		// El audio no es critico: se ignora cualquier fallo del navegador.
	}
}
