import { NextRequest, NextResponse } from "next/server";
import { registrarFeedback, obtenerEstadisticasAprendizaje } from "@/lib/learning";

/**
 * POST /api/feedback
 * Registra el feedback del usuario sobre una propuesta generada
 */
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const {
            contenido,
            tipo,
            exitosa,
            calificacion,
            notas,
            tipoLicitacion,
            entidad,
            montoReferencial,
            projectId
        } = body;

        // Validar datos mínimos
        if (!contenido || !tipo || calificacion === undefined) {
            return NextResponse.json(
                { error: "Datos incompletos. Requeridos: contenido, tipo, calificacion" },
                { status: 400 }
            );
        }

        if (calificacion < 1 || calificacion > 5) {
            return NextResponse.json(
                { error: "Calificación debe estar entre 1 y 5" },
                { status: 400 }
            );
        }

        // Registrar feedback
        await registrarFeedback({
            contenido,
            tipo,
            exitosa: exitosa ?? calificacion >= 3,
            calificacion,
            notas,
            tipoLicitacion,
            entidad,
            montoReferencial,
            projectId,
        });

        return NextResponse.json({
            success: true,
            message: "✅ Feedback registrado. ¡El agente aprenderá de esta propuesta!",
        });

    } catch (error) {
        console.error("Error registrando feedback:", error);
        return NextResponse.json(
            { error: "Error procesando feedback" },
            { status: 500 }
        );
    }
}

/**
 * GET /api/feedback
 * Obtiene estadísticas del sistema de aprendizaje RAG
 */
export async function GET() {
    try {
        const stats = await obtenerEstadisticasAprendizaje();

        return NextResponse.json({
            success: true,
            estadisticas: {
                ...stats,
                mensaje: stats.totalPropuestas > 0
                    ? `🧠 ${stats.totalPropuestas} propuestas aprendidas (${stats.tasaExito.toFixed(1)}% exitosas)`
                    : "📊 Aún no hay propuestas registradas. ¡Califica las propuestas generadas para que el agente aprenda!"
            },
        });

    } catch (error) {
        console.error("Error obteniendo estadísticas:", error);
        return NextResponse.json(
            { error: "Error obteniendo estadísticas" },
            { status: 500 }
        );
    }
}
