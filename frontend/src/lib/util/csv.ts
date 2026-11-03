/**
 * Utilidades para generar y descargar archivos CSV.
 *
 * Se agrega BOM UTF-8 para que Excel (Windows) respete los acentos.
 */

export interface ColumnaCsv<T> {
	/** Encabezado de la columna. */
	titulo: string;
	/** Extrae el valor de una fila. */
	valor: (fila: T) => string | number | null | undefined;
}

function celda(valor: string | number | null | undefined): string {
	const texto = valor === null || valor === undefined ? '' : String(valor);
	if (/[",\r\n]/.test(texto)) {
		return `"${texto.replace(/"/g, '""')}"`;
	}
	return texto;
}

/** Construye el contenido CSV (encabezado incluido) usando CRLF. */
export function generarCsv<T>(filas: T[], columnas: Array<ColumnaCsv<T>>): string {
	const encabezado = columnas.map((c) => celda(c.titulo)).join(',');
	const lineas = filas.map((fila) => columnas.map((c) => celda(c.valor(fila))).join(','));
	return [encabezado, ...lineas].join('\r\n');
}

/** Dispara la descarga de un archivo CSV en el navegador. */
export function descargarCsv(nombreArchivo: string, contenido: string): void {
	const blob = new Blob(['\ufeff' + contenido], { type: 'text/csv;charset=utf-8;' });
	const url = URL.createObjectURL(blob);
	const enlace = document.createElement('a');
	enlace.href = url;
	enlace.download = nombreArchivo;
	document.body.appendChild(enlace);
	enlace.click();
	document.body.removeChild(enlace);
	URL.revokeObjectURL(url);
}
