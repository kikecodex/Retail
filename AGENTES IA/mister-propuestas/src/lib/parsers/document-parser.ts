import mammoth from "mammoth";

export interface DatosExtraidos {
    texto: string;
    datosPersonales?: {
        nombre?: string;
        dni?: string;
        colegiatura?: string;
        email?: string;
        telefono?: string;
    };
    formacion?: {
        titulo: string;
        institucion: string;
        fecha?: string;
    }[];
    experiencias?: {
        cargo: string;
        entidad: string;
        proyecto?: string;
        fechaInicio?: string;
        fechaFin?: string;
        monto?: string;
        descripcion?: string;
    }[];
}

export async function parsePDF(buffer: Buffer): Promise<string> {
    try {
        // Usar pdf-parse-fork para mejor compatibilidad con Node.js
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const pdfParse = require("pdf-parse-fork");
        const data = await pdfParse(buffer);
        return data.text;
    } catch (error) {
        console.error("Error parsing PDF:", error);
        // Fallback: retornar mensaje de error informativo
        throw new Error(`No se pudo parsear el PDF. Error: ${error instanceof Error ? error.message : "desconocido"}`);
    }
}

export async function parseDOCX(buffer: Buffer): Promise<string> {
    const result = await mammoth.extractRawText({ buffer });
    return result.value;
}

export async function parseDocument(
    buffer: Buffer,
    fileName: string
): Promise<string> {
    const extension = fileName.toLowerCase().split(".").pop();

    if (extension === "pdf") {
        return parsePDF(buffer);
    } else if (extension === "docx" || extension === "doc") {
        return parseDOCX(buffer);
    }

    throw new Error(`Formato no soportado: ${extension}`);
}

// Extracción de patrones comunes en CVs peruanos
export function extraerDatosBasicos(texto: string): DatosExtraidos["datosPersonales"] {
    const patterns = {
        dni: /\b(\d{8})\b/,
        colegiatura: /CIP[:\s]*(\d+)/i,
        email: /[\w.-]+@[\w.-]+\.\w+/,
        telefono: /\b9\d{8}\b/,
    };

    return {
        dni: texto.match(patterns.dni)?.[1],
        colegiatura: texto.match(patterns.colegiatura)?.[1],
        email: texto.match(patterns.email)?.[0],
        telefono: texto.match(patterns.telefono)?.[0],
    };
}
