/**
 * Learning System - Registro de feedback y detección de patrones
 * Alimenta el sistema RAG con propuestas calificadas
 */

import { generateEmbedding, crearTextoPropuesta } from "./embeddings";
import { upsertPropuesta, upsertPatron, getRAGStats } from "./vector-store";

export interface FeedbackData {
    modulo: string;  // "supervision" | "consultoria" | "obras"
    contenido: string;
    tipo: string;  // "anexo_01" | "anexo_02" | "anexo_03" | "tecnica" | "economica"
    exitosa: boolean;
    calificacion: number;  // 1-5
    notas?: string;
    tipoLicitacion?: string;
    entidad?: string;
    montoReferencial?: number;
    projectId?: string;
}

/**
 * Registra feedback del usuario sobre una propuesta generada
 * Almacena el contenido + embedding para futuras búsquedas RAG
 */
export async function registrarFeedback(feedback: FeedbackData): Promise<void> {
    const { modulo, contenido, tipo, exitosa, calificacion, notas, tipoLicitacion, entidad, montoReferencial, projectId } = feedback;

    try {
        // 1. Crear texto representativo y generar embedding
        const texto = crearTextoPropuesta({
            tipo,
            contenido,
            tipoLicitacion,
            entidad,
        });
        const embedding = await generateEmbedding(texto);

        // 2. Guardar propuesta con embedding
        await upsertPropuesta(contenido, embedding, {
            modulo,
            tipo,
            exitosa,
            calificacion,
            tipoLicitacion,
            entidad,
            montoReferencial,
            projectId,
            notas,
        });

        // 3. Si es exitosa y bien calificada, detectar y guardar patrones
        if (exitosa && calificacion >= 4) {
            await detectarYAlmacenarPatrones(contenido, modulo);
        }

        console.log(`✅ Feedback registrado: ${exitosa ? "Exitosa" : "Fallida"} (${calificacion}/5) - ${tipo}`);
    } catch (error) {
        console.error("Error registrando feedback:", error);
        throw error;
    }
}

/**
 * Detecta patrones de éxito en propuestas bien calificadas
 * y los almacena para futuras referencias
 */
async function detectarYAlmacenarPatrones(contenido: string, modulo: string): Promise<void> {
    // Patrones a buscar en propuestas exitosas
    const patrones = [
        { regex: /experiencia\s+específica/gi, tipo: "experiencia_especifica", desc: "Enfatiza experiencia específica en el rubro" },
        { regex: /certificación\s+vigente/gi, tipo: "certificacion_vigente", desc: "Incluye certificaciones vigentes relevantes" },
        { regex: /años?\s+de\s+experiencia/gi, tipo: "experiencia_años", desc: "Destaca años de experiencia profesional" },
        { regex: /título\s+profesional/gi, tipo: "titulo_profesional", desc: "Menciona título profesional universitario" },
        { regex: /colegiado/gi, tipo: "colegiatura", desc: "Indica colegiatura profesional habilitada" },
        { regex: /capacitación/gi, tipo: "capacitacion", desc: "Incluye capacitaciones especializadas" },
        { regex: /especialización|especialista/gi, tipo: "especializacion", desc: "Destaca especializaciones del personal" },
        { regex: /contrato|orden\s+de\s+servicio/gi, tipo: "documentacion_respaldo", desc: "Referencia documentación de respaldo" },
    ];

    for (const patron of patrones) {
        if (patron.regex.test(contenido)) {
            try {
                const embedding = await generateEmbedding(
                    `Patrón de éxito: ${patron.desc}`
                );
                await upsertPatron(patron.tipo, patron.desc, embedding, modulo);
                console.log(`📊 Patrón detectado: ${patron.tipo}`);
            } catch (error) {
                console.error(`Error guardando patrón ${patron.tipo}:`, error);
            }
        }
    }
}

/**
 * Obtiene estadísticas del sistema de aprendizaje
 */
export async function obtenerEstadisticasAprendizaje(modulo?: string): Promise<{
    totalPropuestas: number;
    propuestasExitosas: number;
    tasaExito: number;
    totalPatrones: number;
}> {
    try {
        const stats = await getRAGStats(modulo);
        return {
            totalPropuestas: stats.totalPropuestas,
            propuestasExitosas: stats.propuestasExitosas,
            tasaExito: stats.tasaExito,
            totalPatrones: stats.totalPatrones,
        };
    } catch (error) {
        console.error("Error obteniendo estadísticas:", error);
        return {
            totalPropuestas: 0,
            propuestasExitosas: 0,
            tasaExito: 0,
            totalPatrones: 0,
        };
    }
}
