import { NextRequest, NextResponse } from "next/server";
import { parseDocument } from "@/lib/parsers/document-parser";
import { analizarBases } from "@/lib/gemini";
import { getRAGStats } from "@/lib/vector-store";
import { detectarPaginasConTablas } from "@/lib/document-vision";

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const file = formData.get("file") as File;
        const projectName = formData.get("projectName") as string;
        const modulo = (formData.get("modulo") as string) || "consultoria";

        if (!file || !projectName) {
            return NextResponse.json(
                { error: "Archivo y nombre del proyecto requeridos" },
                { status: 400 }
            );
        }

        console.log(`📄 Procesando: ${file.name} (${Math.round(file.size / 1024)} KB) [Módulo: ${modulo}]`);

        // Convertir archivo a buffer
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);

        // Extraer texto del documento
        const textoExtraido = await parseDocument(buffer, file.name);
        console.log(`📝 Texto extraído: ${textoExtraido.length} caracteres`);

        // Limitar texto para evitar exceder contexto de Gemini
        const textoLimitado = textoExtraido.substring(0, 100000);

        // Analizar con Gemini
        console.log("🤖 Analizando con Gemini...");
        const analisis = await analizarBases(textoLimitado, modulo);
        console.log(`✅ Análisis completado: ${analisis.capitulos?.length || 0} capítulos, ${analisis.requisitos?.length || 0} requisitos`);

        // Generar ID de proyecto temporal
        const projectId = `demo_${Date.now()}`;

        // Obtener estadísticas RAG
        let ragStats = { totalPropuestas: 0, propuestasExitosas: 0, tasaExito: 0, totalPatrones: 0 };
        try {
            ragStats = await getRAGStats(modulo);
        } catch {
            console.log("⚠️ RAG stats no disponible (tablas aún no migradas)");
        }

        // Detectar si hay tablas de personal clave en el documento
        const deteccionTablas = detectarPaginasConTablas(textoExtraido);
        if (deteccionTablas.tieneTablaB1 || deteccionTablas.tieneTablaB2) {
            console.log(`📊 Tablas detectadas: ${deteccionTablas.indicadores.join(", ")}`);
        }

        return NextResponse.json({
            success: true,
            projectId,
            modulo,
            // Información General - CRÍTICO PARA ANEXOS
            nomenclaturaProceso: analisis.nomenclaturaProceso || "PROCESO DE SELECCIÓN",
            tipoModalidad: analisis.tipoModalidad || "CONCURSO PÚBLICO",
            entidadConvocante: analisis.entidadConvocante,
            objetoContratacion: analisis.objetoContratacion,
            valorReferencial: analisis.valorReferencial,
            plazoEjecucion: analisis.plazoEjecucion,
            // Especialidad del Proceso
            especialidadProceso: analisis.especialidadProceso || "",
            subespecialidadProceso: analisis.subespecialidadProceso || "",
            tipologiasProceso: analisis.tipologiasProceso || [],
            // Análisis por capítulos
            capitulos: analisis.capitulos || [],
            // Requisitos de personal
            requisitos: analisis.requisitos || [],
            // Anexos
            anexos: analisis.anexosDetectados || [],
            // Criterios de evaluación
            criteriosEvaluacion: analisis.criteriosEvaluacion || [],
            // Resumen
            resumen: analisis.resumen,
            // Detección de tablas para Vision API (futuro)
            tablasDetectadas: {
                tieneB1: deteccionTablas.tieneTablaB1,
                tieneB2: deteccionTablas.tieneTablaB2,
                indicadores: deteccionTablas.indicadores
            },
            // Info de aprendizaje RAG
            aprendizaje: {
                activo: ragStats.totalPropuestas > 0,
                propuestasAprendidas: ragStats.totalPropuestas,
                patronesDetectados: ragStats.totalPatrones,
                mensaje: ragStats.totalPropuestas > 0
                    ? `🧠 RAG activo: ${ragStats.totalPropuestas} propuestas aprendidas`
                    : "📊 Sistema de aprendizaje listo - califica tus propuestas para mejorar"
            }
        });

    } catch (error) {
        console.error("❌ Error analizando bases:", error);

        const errorMessage = error instanceof Error ? error.message : "Error desconocido";

        return NextResponse.json(
            {
                error: "Error procesando el archivo",
                detalle: errorMessage,
                sugerencia: "Verifica que GEMINI_API_KEY esté configurado en .env"
            },
            { status: 500 }
        );
    }
}
