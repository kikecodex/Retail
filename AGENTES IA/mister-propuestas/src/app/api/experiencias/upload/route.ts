import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { parseDocument, extraerDatosBasicos } from "@/lib/parsers/document-parser";

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const files = formData.getAll("files") as File[];
        const projectId = formData.get("projectId") as string;

        if (!files.length || !projectId) {
            return NextResponse.json(
                { error: "Archivos y projectId requeridos" },
                { status: 400 }
            );
        }

        const resultados = [];

        for (const file of files) {
            // Convertir archivo a buffer
            const bytes = await file.arrayBuffer();
            const buffer = Buffer.from(bytes);

            // Extraer texto
            const texto = await parseDocument(buffer, file.name);

            // Extraer datos básicos
            const datosBasicos = extraerDatosBasicos(texto);

            // Guardar en BD
            const experiencia = await prisma.experiencia.create({
                data: {
                    fileUrl: "", // TODO: subir a storage
                    fileName: file.name,
                    fileType: file.name.split(".").pop() || "unknown",
                    datosPersonales: datosBasicos,
                    projectId,
                },
            });

            resultados.push({
                id: experiencia.id,
                fileName: file.name,
                datosExtraidos: datosBasicos,
                textoPreview: texto.substring(0, 500) + "...",
            });
        }

        return NextResponse.json({
            success: true,
            experiencias: resultados,
        });

    } catch (error) {
        console.error("Error procesando experiencias:", error);
        return NextResponse.json(
            { error: "Error procesando archivos" },
            { status: 500 }
        );
    }
}
