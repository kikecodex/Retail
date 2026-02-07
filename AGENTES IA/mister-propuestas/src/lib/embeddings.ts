/**
 * Embeddings - Generación de vectores con Gemini
 * Simplificado para el sistema RAG de propuestas
 */

import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

// Modelo de embeddings de Gemini (768 dimensiones)
const embeddingModel = genAI.getGenerativeModel({
    model: "text-embedding-004"
});

/**
 * Genera embedding para un texto usando Gemini
 * Retorna vector de 768 dimensiones
 */
export async function generateEmbedding(text: string): Promise<number[]> {
    const result = await embeddingModel.embedContent(text);
    return result.embedding.values;
}

/**
 * Genera embeddings para múltiples textos
 */
export async function generateEmbeddings(texts: string[]): Promise<number[][]> {
    const results: number[][] = [];
    for (const text of texts) {
        const embedding = await generateEmbedding(text);
        results.push(embedding);
    }
    return results;
}

/**
 * Crea texto representativo de una propuesta para embedding
 */
export function crearTextoPropuesta(propuesta: {
    tipo: string;
    contenido: string;
    tipoLicitacion?: string;
    entidad?: string;
}): string {
    const partes = [
        `Tipo: ${propuesta.tipo}`,
        propuesta.tipoLicitacion ? `Licitación: ${propuesta.tipoLicitacion}` : "",
        propuesta.entidad ? `Entidad: ${propuesta.entidad}` : "",
        `Contenido: ${propuesta.contenido.substring(0, 2000)}`,
    ];
    return partes.filter(Boolean).join("\n");
}

/**
 * Crea texto representativo de requisitos para búsqueda
 */
export function crearTextoRequisitos(requisitos: {
    perfiles?: string[];
    experiencia?: string;
    certificaciones?: string[];
    tipoLicitacion?: string;
}): string {
    const partes = [
        requisitos.tipoLicitacion ? `Tipo: ${requisitos.tipoLicitacion}` : "",
        requisitos.perfiles?.length ? `Perfiles: ${requisitos.perfiles.join(", ")}` : "",
        requisitos.experiencia ? `Experiencia: ${requisitos.experiencia}` : "",
        requisitos.certificaciones?.length ? `Certificaciones: ${requisitos.certificaciones.join(", ")}` : "",
    ];
    return partes.filter(Boolean).join("\n");
}
