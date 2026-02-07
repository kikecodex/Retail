import { Document, Packer, Paragraph, Table, TableRow, TableCell, TextRun } from "docx";
import mammoth from "mammoth";

export interface CampoAnexo {
    fila: number;
    columna: number;
    nombreCampo: string;
    valor?: string;
}

export interface AnexoTemplate {
    nombre: string;
    campos: CampoAnexo[];
    contenidoOriginal: string;
}

/**
 * Detecta campos vacíos o con placeholders en un documento DOCX
 */
export async function detectarCamposAnexo(buffer: Buffer): Promise<CampoAnexo[]> {
    const result = await mammoth.extractRawText({ buffer });
    const texto = result.value;

    // Patrones comunes de campos a llenar en anexos SEACE
    const patronesCampos = [
        /\[.*?\]/g,           // [Campo a llenar]
        /\{.*?\}/g,           // {Campo}
        /___+/g,              // ________
        /\.\.\.+/g,           // .......
        /\(\s*\)/g,           // ( )
    ];

    const campos: CampoAnexo[] = [];
    let fila = 0;

    const lineas = texto.split("\n");
    lineas.forEach((linea, index) => {
        patronesCampos.forEach(patron => {
            const matches = linea.match(patron);
            if (matches) {
                matches.forEach(match => {
                    campos.push({
                        fila: index,
                        columna: linea.indexOf(match),
                        nombreCampo: match.replace(/[\[\]\{\}\_\.]/g, "").trim() || `Campo_${campos.length + 1}`
                    });
                });
            }
        });
    });

    return campos;
}

/**
 * Rellena un documento DOCX con los valores proporcionados
 */
export async function rellenarAnexo(
    templateBuffer: Buffer,
    valores: Record<string, string>
): Promise<Buffer> {
    const result = await mammoth.extractRawText({ buffer: templateBuffer });
    let contenido = result.value;

    // Reemplazar cada campo con su valor
    Object.entries(valores).forEach(([campo, valor]) => {
        // Reemplazar diferentes formatos de placeholder
        contenido = contenido
            .replace(new RegExp(`\\[${campo}\\]`, "gi"), valor)
            .replace(new RegExp(`\\{${campo}\\}`, "gi"), valor)
            .replace(/___+/g, valor)  // Solo el primero
            .replace(/\.\.\.+/g, valor);
    });

    // Crear nuevo documento con el contenido modificado
    const doc = new Document({
        sections: [{
            properties: {},
            children: contenido.split("\n").map(linea =>
                new Paragraph({
                    children: [new TextRun(linea)]
                })
            )
        }]
    });

    return await Packer.toBuffer(doc);
}

/**
 * Extrae tablas de un documento y detecta celdas vacías
 */
export async function extraerTablasVacias(buffer: Buffer): Promise<{
    tablaIndex: number;
    celdasVacias: { fila: number; columna: number }[];
}[]> {
    // Por ahora retornamos estructura básica
    // TODO: Implementar extracción completa de tablas con xml2js
    return [];
}
