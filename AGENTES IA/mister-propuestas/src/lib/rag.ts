/**
 * RAG - Retrieval Augmented Generation para propuestas inteligentes
 * Busca propuestas similares exitosas y patrones de éxito para mejorar la generación
 */

import { generateEmbedding, crearTextoRequisitos } from "./embeddings";
import { searchSimilarPropuestas, searchSimilarPatrones, SearchResult } from "./vector-store";
import { geminiModel } from "./gemini";

export interface RAGContext {
    propuestasExitosas: SearchResult[];
    patronesDetectados: SearchResult[];
    estadisticas: {
        propuestasEncontradas: number;
        patronesEncontrados: number;
    };
}

/**
 * Busca contexto relevante para mejorar una propuesta
 */
export async function buscarContextoRelevante(
    requisitos: {
        modulo?: string; // Módulo vertical para aislamiento
        perfiles?: string[];
        experiencia?: string;
        certificaciones?: string[];
        tipoLicitacion?: string;
    },
    topK: number = 3
): Promise<RAGContext> {
    try {
        // Crear texto de búsqueda
        const textoQuery = crearTextoRequisitos(requisitos);

        // Generar embedding
        const queryEmbedding = await generateEmbedding(textoQuery);

        // Buscar en paralelo
        const [propuestasExitosas, patronesDetectados] = await Promise.all([
            searchSimilarPropuestas(queryEmbedding, topK, {
                modulo: requisitos.modulo,
                soloExitosas: true,
                tipoLicitacion: requisitos.tipoLicitacion
            }),
            searchSimilarPatrones(queryEmbedding, topK, requisitos.modulo),
        ]);

        return {
            propuestasExitosas,
            patronesDetectados,
            estadisticas: {
                propuestasEncontradas: propuestasExitosas.length,
                patronesEncontrados: patronesDetectados.length,
            }
        };
    } catch (error) {
        console.error("Error buscando contexto RAG:", error);
        // Retornar contexto vacío si hay error (graceful degradation)
        return {
            propuestasExitosas: [],
            patronesDetectados: [],
            estadisticas: { propuestasEncontradas: 0, patronesEncontrados: 0 }
        };
    }
}

/**
 * Construye un prompt enriquecido con contexto de propuestas exitosas
 */
export function construirPromptConContexto(
    promptBase: string,
    contexto: RAGContext
): string {
    let contextoPropuestas = "";
    let contextoPatrones = "";

    // Agregar ejemplos de propuestas exitosas
    if (contexto.propuestasExitosas.length > 0) {
        contextoPropuestas = `
## EJEMPLOS DE PROPUESTAS EXITOSAS ANTERIORES:
${contexto.propuestasExitosas
                .map((p, i) => `### Ejemplo ${i + 1} (Calificación: ${p.metadata.calificacion || "N/A"}/5)
${p.metadata.contenido || ""}`)
                .join("\n\n")}

Usa estos ejemplos como referencia para el estilo, formato y nivel de detalle.
`;
    }

    // Agregar patrones de éxito detectados
    if (contexto.patronesDetectados.length > 0) {
        contextoPatrones = `
## PATRONES DE ÉXITO DETECTADOS:
${contexto.patronesDetectados
                .map(p => `- **${p.metadata.tipo}**: ${p.metadata.descripcion || ""}`)
                .join("\n")}

Aplica estos patrones en tu respuesta para maximizar probabilidad de éxito.
`;
    }

    // Agregar indicador de contexto usado
    const indicador = contexto.estadisticas.propuestasEncontradas > 0 || contexto.estadisticas.patronesEncontrados > 0
        ? `\n> 🧠 RAG activo: ${contexto.estadisticas.propuestasEncontradas} propuestas + ${contexto.estadisticas.patronesEncontrados} patrones de referencia\n`
        : "";

    return `${indicador}${contextoPropuestas}${contextoPatrones}

${promptBase}`;
}

/**
 * Genera respuesta mejorada con contexto RAG
 */
export async function generarConRAG(
    promptBase: string,
    requisitos: {
        modulo?: string;
        perfiles?: string[];
        experiencia?: string;
        certificaciones?: string[];
        tipoLicitacion?: string;
    }
): Promise<{ respuesta: string; contextoUsado: RAGContext }> {
    // Buscar contexto relevante
    const contexto = await buscarContextoRelevante(requisitos);

    // Construir prompt enriquecido
    const promptMejorado = construirPromptConContexto(promptBase, contexto);

    // Generar con Gemini
    const result = await geminiModel.generateContent(promptMejorado);

    return {
        respuesta: result.response.text(),
        contextoUsado: contexto,
    };
}

/**
 * Analiza bases de licitación con contexto RAG
 */
export async function analizarBasesConRAG(
    contenidoBases: string,
    tipoLicitacion?: string,
    modulo?: string
): Promise<{
    analisis: string;
    contextoUsado: RAGContext;
}> {
    // Extraer requisitos básicos del texto para búsqueda
    const requisitosBasicos = {
        modulo,
        tipoLicitacion,
        experiencia: contenidoBases.includes("experiencia") ? "experiencia profesional" : undefined,
    };

    const contexto = await buscarContextoRelevante(requisitosBasicos, 5);

    const promptBase = `
Eres un experto en licitaciones públicas peruanas (SEACE).
Analiza los siguientes términos de referencia y extrae requisitos clave.

${contenidoBases}
`;

    const promptMejorado = construirPromptConContexto(promptBase, contexto);
    const result = await geminiModel.generateContent(promptMejorado);

    return {
        analisis: result.response.text(),
        contextoUsado: contexto,
    };
}
