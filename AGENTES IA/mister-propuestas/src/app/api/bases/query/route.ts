import { NextRequest, NextResponse } from "next/server";
import {
    responderPreguntaRAG,
    indexarDocumento,
    obtenerEstadisticasRAG,
} from "@/lib/vector-store-chroma";

/**
 * POST /api/bases/query
 * 
 * Hace una consulta inteligente sobre las bases indexadas
 */
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { accion, pregunta, documentoId, contenido, nombreArchivo, proyecto } = body;

        // Acción: indexar documento
        if (accion === "indexar") {
            if (!documentoId || !contenido) {
                return NextResponse.json(
                    { error: "Para indexar se requiere: documentoId, contenido" },
                    { status: 400 }
                );
            }

            console.log(`📚 Indexando documento: ${nombreArchivo || documentoId}`);

            const resultado = await indexarDocumento(
                documentoId,
                nombreArchivo || "documento.pdf",
                proyecto || "Sin proyecto",
                contenido
            );

            return NextResponse.json({
                success: true,
                mensaje: `Documento indexado exitosamente`,
                documento: resultado,
            });
        }

        // Acción: consultar (por defecto)
        if (!pregunta) {
            return NextResponse.json(
                { error: "Se requiere el campo 'pregunta'" },
                { status: 400 }
            );
        }

        console.log(`🔍 Consulta RAG: "${pregunta}"`);

        const resultado = await responderPreguntaRAG(pregunta, documentoId);

        return NextResponse.json({
            success: true,
            pregunta,
            respuesta: resultado.respuesta,
            fragmentosUsados: resultado.fragmentosUsados.map((f) => ({
                texto: f.texto.substring(0, 200) + "...",
                archivo: f.metadata.nombreArchivo,
                relevancia: (1 - f.score).toFixed(2),
            })),
        });

    } catch (error) {
        console.error("❌ Error en consulta RAG:", error);
        const errorMessage = error instanceof Error ? error.message : "Error desconocido";

        return NextResponse.json(
            { error: "Error procesando consulta", detalle: errorMessage },
            { status: 500 }
        );
    }
}

/**
 * GET /api/bases/query
 * 
 * Obtiene estadísticas del RAG
 */
export async function GET() {
    try {
        const stats = await obtenerEstadisticasRAG();

        return NextResponse.json({
            success: true,
            estadisticas: stats,
        });
    } catch (error) {
        console.error("❌ Error obteniendo stats RAG:", error);
        return NextResponse.json(
            { error: "Error obteniendo estadísticas" },
            { status: 500 }
        );
    }
}
