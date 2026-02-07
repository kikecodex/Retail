/**
 * Vector Store - Almacenamiento y búsqueda de embeddings
 * Usa Prisma Client con similitud coseno en JavaScript
 * Compatible con Prisma Postgres local (sin extensión pgvector)
 */

import { prisma } from "./prisma";
import { Prisma } from "@prisma/client";

// ============== TYPES ==============

type PropuestaHistorica = Prisma.PropuestaHistoricaGetPayload<{
    select: {
        id: true;
        contenido: true;
        tipo: true;
        exitosa: true;
        calificacion: true;
        embedding: true;
    };
}>;

type PatronExito = Prisma.PatronExitoGetPayload<{
    select: {
        id: true;
        tipo: true;
        descripcion: true;
        frecuencia: true;
        embedding: true;
    };
}>;

export interface SearchResult {
    id: string;
    score: number;
    metadata: {
        contenido?: string;
        tipo?: string;
        exitosa?: boolean;
        calificacion?: number | null;
        descripcion?: string;
        frecuencia?: number;
        [key: string]: unknown;
    };
}

// ============== HELPER: Similitud Coseno ==============

function cosineSimilarity(a: number[], b: number[]): number {
    if (!a || !b || a.length !== b.length) return 0;

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }

    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// ============== PROPUESTAS ==============

/**
 * Guarda una propuesta con su embedding en la base de datos
 */
export async function upsertPropuesta(
    contenido: string,
    embedding: number[],
    metadata: {
        modulo: string; // "supervision" | "consultoria" | "obras"
        tipo: string;
        exitosa?: boolean;
        calificacion?: number;
        tipoLicitacion?: string;
        entidad?: string;
        montoReferencial?: number;
        projectId?: string;
        notas?: string;
    }
): Promise<string> {
    const propuesta = await prisma.propuestaHistorica.create({
        data: {
            modulo: metadata.modulo,
            contenido,
            tipo: metadata.tipo,
            exitosa: metadata.exitosa || false,
            calificacion: metadata.calificacion,
            tipoLicitacion: metadata.tipoLicitacion,
            entidad: metadata.entidad,
            montoReferencial: metadata.montoReferencial,
            projectId: metadata.projectId,
            notas: metadata.notas,
            embedding: embedding as unknown as Prisma.InputJsonValue,
        },
    });

    return propuesta.id;
}

/**
 * Busca propuestas similares usando similitud coseno
 */
export async function searchSimilarPropuestas(
    queryEmbedding: number[],
    topK: number = 5,
    filters?: {
        modulo?: string; // Filtrar por módulo vertical
        tipo?: string;
        soloExitosas?: boolean;
        tipoLicitacion?: string;
    }
): Promise<SearchResult[]> {
    // Construir filtro Prisma
    const where: Prisma.PropuestaHistoricaWhereInput = {};

    if (filters?.modulo) where.modulo = filters.modulo;
    if (filters?.tipo) where.tipo = filters.tipo;
    if (filters?.soloExitosas) where.exitosa = true;
    if (filters?.tipoLicitacion) where.tipoLicitacion = filters.tipoLicitacion;

    // Obtener todas las propuestas que coincidan con los filtros
    const propuestas = await prisma.propuestaHistorica.findMany({
        where,
        select: {
            id: true,
            contenido: true,
            tipo: true,
            exitosa: true,
            calificacion: true,
            embedding: true,
        },
    });

    // Calcular similitud coseno para cada propuesta con embedding válido
    const scoredResults = propuestas
        .filter((p: PropuestaHistorica) => p.embedding && Array.isArray(p.embedding))
        .map((p: PropuestaHistorica) => ({
            id: p.id,
            score: cosineSimilarity(queryEmbedding, p.embedding as unknown as number[]),
            metadata: {
                contenido: p.contenido?.substring(0, 1000),
                tipo: p.tipo,
                exitosa: p.exitosa,
                calificacion: p.calificacion,
            },
        }))
        .sort((a: SearchResult, b: SearchResult) => b.score - a.score)
        .slice(0, topK);

    return scoredResults;
}

// ============== PATRONES ==============

/**
 * Guarda o actualiza un patrón de éxito detectado
 */
export async function upsertPatron(
    tipo: string,
    descripcion: string,
    embedding: number[],
    modulo: string = "consultoria"
): Promise<void> {
    await prisma.patronExito.upsert({
        where: { modulo_tipo: { modulo, tipo } },
        update: {
            frecuencia: { increment: 1 },
        },
        create: {
            modulo,
            tipo,
            descripcion,
            frecuencia: 1,
            embedding: embedding as unknown as Prisma.InputJsonValue,
        },
    });
}

/**
 * Busca patrones de éxito similares
 */
export async function searchSimilarPatrones(
    queryEmbedding: number[],
    topK: number = 3,
    modulo?: string
): Promise<SearchResult[]> {
    const where: Prisma.PatronExitoWhereInput = {};
    if (modulo) where.modulo = modulo;

    const patrones = await prisma.patronExito.findMany({
        where,
        select: {
            id: true,
            tipo: true,
            descripcion: true,
            frecuencia: true,
            embedding: true,
        },
    });

    const scoredResults = patrones
        .filter((p: PatronExito) => p.embedding && Array.isArray(p.embedding))
        .map((p: PatronExito) => ({
            id: p.id,
            score: cosineSimilarity(queryEmbedding, p.embedding as unknown as number[]),
            metadata: {
                tipo: p.tipo,
                descripcion: p.descripcion,
                frecuencia: p.frecuencia,
            },
        }))
        .sort((a: SearchResult, b: SearchResult) => b.score - a.score)
        .slice(0, topK);

    return scoredResults;
}

// ============== ESTADÍSTICAS ==============

/**
 * Obtiene estadísticas del sistema de aprendizaje
 */
export async function getRAGStats(modulo?: string): Promise<{
    totalPropuestas: number;
    propuestasExitosas: number;
    totalPatrones: number;
    tasaExito: number;
}> {
    const whereP: Prisma.PropuestaHistoricaWhereInput = modulo ? { modulo } : {};
    const wherePat: Prisma.PatronExitoWhereInput = modulo ? { modulo } : {};

    const [totalPropuestas, propuestasExitosas, totalPatrones] = await Promise.all([
        prisma.propuestaHistorica.count({ where: whereP }),
        prisma.propuestaHistorica.count({ where: { ...whereP, exitosa: true } }),
        prisma.patronExito.count({ where: wherePat }),
    ]);

    return {
        totalPropuestas,
        propuestasExitosas,
        totalPatrones,
        tasaExito: totalPropuestas > 0 ? (propuestasExitosas / totalPropuestas) * 100 : 0,
    };
}
