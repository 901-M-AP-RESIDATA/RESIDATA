<script lang="ts">
	import { Chart, registerables, type ChartConfiguration } from 'chart.js';
	import { onMount } from 'svelte';

	Chart.register(...registerables);

	interface Props {
		configuracion: ChartConfiguration;
		clase?: string;
		alto?: string;
	}

	let { configuracion, clase = '', alto = '18rem' }: Props = $props();

	let lienzo = $state<HTMLCanvasElement>();
	let grafica: Chart | null = null;

	onMount(() => {
		if (!lienzo) return;
		grafica = new Chart(lienzo, configuracion);
		return () => {
			grafica?.destroy();
			grafica = null;
		};
	});

	$effect(() => {
		const config = configuracion;
		if (!grafica) return;
		grafica.data = config.data;
		grafica.options = config.options ?? {};
		grafica.update();
	});
</script>

<div style="height:{alto}" class={clase}>
	<canvas bind:this={lienzo}></canvas>
</div>
