<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { ErrorApi } from '#lib/api/cliente.ts';
	import {
		actualizarUsuario,
		crearUsuario,
		eliminarUsuario,
		listarRoles,
		listarUsuarios
	} from '#lib/api/usuarios.ts';
	import Boton from '#lib/components/Boton.svelte';
	import CampoSelect from '#lib/components/CampoSelect.svelte';
	import CampoTexto from '#lib/components/CampoTexto.svelte';
	import Cargando from '#lib/components/Cargando.svelte';
	import EstadoVacio from '#lib/components/EstadoVacio.svelte';
	import Insignia from '#lib/components/Insignia.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import Tarjeta from '#lib/components/Tarjeta.svelte';
	import { sesion } from '#lib/stores/sesion.svelte.ts';
	import { toasts } from '#lib/stores/toast.svelte.ts';
	import type { Rol, Usuario } from '#lib/tipos/index.ts';
	import { formatearFechaHora } from '#lib/util/formato.ts';

	let items = $state<Usuario[]>([]);
	let roles = $state<Rol[]>([]);
	let cargando = $state(true);
	let error = $state<string | null>(null);

	let modalForm = $state(false);
	let modo = $state<'crear' | 'editar'>('crear');
	let editandoId = $state<number | null>(null);
	let form = $state({ nombre: '', correo: '', contrasena: '', rol_id: 2, activo: true });
	let errores = $state<{ nombre?: string; correo?: string; contrasena?: string }>({});
	let guardando = $state(false);

	let modalEliminar = $state(false);
	let aEliminar = $state<Usuario | null>(null);
	let eliminando = $state(false);

	const opcionesRoles = $derived(roles.map((rol) => ({ valor: rol.id, etiqueta: rol.nombre })));

	// Solo administradores pueden ver esta seccion.
	$effect(() => {
		if (sesion.inicializado && sesion.autenticado && !sesion.esAdministrador) {
			void goto('/dashboard', { replaceState: true });
		}
	});

	function varianteRol(nombre?: string): 'verde' | 'azul' {
		return nombre === 'administrador' ? 'verde' : 'azul';
	}

	function esUsuarioActual(usuario: Usuario): boolean {
		return sesion.usuario?.id === usuario.id;
	}

	async function cargar(): Promise<void> {
		cargando = true;
		error = null;
		try {
			const respuesta = await listarUsuarios();
			items = respuesta.items;
		} catch (e) {
			error = e instanceof ErrorApi ? e.message : 'No se pudieron cargar los usuarios.';
		} finally {
			cargando = false;
		}
	}

	function abrirCrear(): void {
		modo = 'crear';
		editandoId = null;
		form = { nombre: '', correo: '', contrasena: '', rol_id: roles[1]?.id ?? 2, activo: true };
		errores = {};
		modalForm = true;
	}

	function abrirEditar(usuario: Usuario): void {
		modo = 'editar';
		editandoId = usuario.id;
		form = {
			nombre: usuario.nombre,
			correo: usuario.correo,
			contrasena: '',
			rol_id: usuario.rol_id,
			activo: usuario.activo
		};
		errores = {};
		modalForm = true;
	}

	async function guardar(): Promise<void> {
		errores = {};
		if (!form.nombre.trim()) errores.nombre = 'El nombre es obligatorio.';
		if (!form.correo.trim()) errores.correo = 'El correo es obligatorio.';
		if (modo === 'crear' && !form.contrasena) errores.contrasena = 'La contrasena es obligatoria.';
		if (errores.nombre || errores.correo || errores.contrasena) return;

		guardando = true;
		try {
			if (modo === 'crear') {
				await crearUsuario({
					nombre: form.nombre.trim(),
					correo: form.correo.trim(),
					contrasena: form.contrasena,
					rol_id: form.rol_id,
					activo: form.activo
				});
				toasts.exito('Usuario creado');
			} else if (editandoId !== null) {
				await actualizarUsuario(editandoId, {
					nombre: form.nombre.trim(),
					correo: form.correo.trim(),
					rol_id: form.rol_id,
					activo: form.activo,
					...(form.contrasena ? { contrasena: form.contrasena } : {})
				});
				toasts.exito('Usuario actualizado');
			}
			modalForm = false;
			await cargar();
		} catch (e) {
			toasts.error('No se pudo guardar', e instanceof ErrorApi ? e.message : 'Intenta de nuevo.');
		} finally {
			guardando = false;
		}
	}

	function abrirEliminar(usuario: Usuario): void {
		aEliminar = usuario;
		modalEliminar = true;
	}

	async function confirmarEliminar(): Promise<void> {
		if (!aEliminar) return;
		eliminando = true;
		try {
			await eliminarUsuario(aEliminar.id);
			modalEliminar = false;
			toasts.exito('Usuario eliminado');
			await cargar();
		} catch (e) {
			toasts.error('No se pudo eliminar', e instanceof ErrorApi ? e.message : 'Intenta de nuevo.');
		} finally {
			eliminando = false;
			aEliminar = null;
		}
	}

	onMount(() => {
		void listarRoles()
			.then((r) => {
				roles = r;
			})
			.catch(() => {
				// El selector de roles queda vacio si falla la carga.
			});
		void cargar();
	});
</script>

<Tarjeta>
	{#snippet acciones()}
		<Boton onclick={abrirCrear}>Nuevo usuario</Boton>
	{/snippet}

	{#if cargando && items.length === 0}
		<Cargando mensaje="Cargando usuarios..." />
	{:else if error}
		<EstadoVacio titulo="No se pudieron cargar los usuarios" mensaje={error}>
			{#snippet accion()}
				<Boton variante="secundario" onclick={cargar}>Reintentar</Boton>
			{/snippet}
		</EstadoVacio>
	{:else if items.length === 0}
		<EstadoVacio titulo="Sin usuarios" mensaje="Crea el primer usuario del sistema." />
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full min-w-[42rem] border-collapse text-sm">
				<thead>
					<tr
						class="border-b border-borde text-left text-xs uppercase tracking-wide text-texto-suave"
					>
						<th class="px-3 py-2 font-semibold">Nombre</th>
						<th class="px-3 py-2 font-semibold">Correo</th>
						<th class="px-3 py-2 font-semibold">Rol</th>
						<th class="px-3 py-2 font-semibold">Estado</th>
						<th class="px-3 py-2 font-semibold">Último acceso</th>
						<th class="px-3 py-2 text-right font-semibold">Acciones</th>
					</tr>
				</thead>
				<tbody>
					{#each items as usuario (usuario.id)}
						<tr class="border-b border-borde/70 last:border-0 hover:bg-black/[0.02]">
							<td class="px-3 py-2.5 font-medium text-texto">
								{usuario.nombre}
								{#if esUsuarioActual(usuario)}
									<span class="text-xs font-normal text-texto-suave">(tú)</span>
								{/if}
							</td>
							<td class="px-3 py-2.5 text-texto-suave">{usuario.correo}</td>
							<td class="px-3 py-2.5">
								<Insignia variante={varianteRol(usuario.rol?.nombre)}>
									{usuario.rol?.nombre ?? `Rol ${usuario.rol_id}`}
								</Insignia>
							</td>
							<td class="px-3 py-2.5">
								<Insignia variante={usuario.activo ? 'verde' : 'gris'}>
									{usuario.activo ? 'Activo' : 'Inactivo'}
								</Insignia>
							</td>
							<td class="px-3 py-2.5 text-texto-suave">
								{usuario.ultimo_acceso ? formatearFechaHora(usuario.ultimo_acceso) : '—'}
							</td>
							<td class="px-3 py-2.5">
								<div class="flex justify-end gap-1">
									<Boton variante="fantasma" clase="px-2 py-1" onclick={() => abrirEditar(usuario)}>
										Editar
									</Boton>
									<Boton
										variante="fantasma"
										clase="px-2 py-1 text-peligro-600"
										disabled={esUsuarioActual(usuario)}
										title={esUsuarioActual(usuario)
											? 'No puedes eliminar tu propio usuario'
											: 'Eliminar'}
										onclick={() => abrirEliminar(usuario)}
									>
										Eliminar
									</Boton>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</Tarjeta>

<!-- Modal de formulario -->
<Modal
	bind:abierto={modalForm}
	titulo={modo === 'crear' ? 'Nuevo usuario' : 'Editar usuario'}
>
	<form
		class="space-y-4"
		onsubmit={(evento) => {
			evento.preventDefault();
			void guardar();
		}}
	>
		<CampoTexto
			etiqueta="Nombre"
			bind:valor={form.nombre}
			requerido
			error={errores.nombre ?? null}
		/>
		<CampoTexto
			etiqueta="Correo"
			tipo="email"
			bind:valor={form.correo}
			requerido
			error={errores.correo ?? null}
			placeholder="usuario@residata.local"
		/>
		<CampoTexto
			etiqueta={modo === 'crear' ? 'Contrasena' : 'Nueva contrasena (opcional)'}
			tipo="password"
			bind:valor={form.contrasena}
			requerido={modo === 'crear'}
			error={errores.contrasena ?? null}
			ayuda={modo === 'editar' ? 'Dejala vacia para conservar la actual.' : undefined}
		/>
		<CampoSelect etiqueta="Rol" bind:valor={form.rol_id} opciones={opcionesRoles} />
		<label class="flex items-center gap-2 text-sm text-texto">
			<input
				type="checkbox"
				bind:checked={form.activo}
				class="h-4 w-4 rounded border-borde text-marca-600 focus:ring-marca-500"
			/>
			Usuario activo
		</label>
	</form>

	{#snippet pie()}
		<Boton variante="secundario" onclick={() => (modalForm = false)}>Cancelar</Boton>
		<Boton cargando={guardando} onclick={guardar}>
			{modo === 'crear' ? 'Crear' : 'Guardar'}
		</Boton>
	{/snippet}
</Modal>

<!-- Modal de eliminación -->
<Modal bind:abierto={modalEliminar} titulo="Eliminar usuario" tamano="sm">
	<p class="text-sm text-texto">
		¿Seguro que deseas eliminar a
		<span class="font-semibold">{aEliminar?.nombre}</span>? Esta acción no se puede deshacer.
	</p>

	{#snippet pie()}
		<Boton variante="secundario" onclick={() => (modalEliminar = false)}>Cancelar</Boton>
		<Boton variante="peligro" cargando={eliminando} onclick={confirmarEliminar}>Eliminar</Boton>
	{/snippet}
</Modal>
