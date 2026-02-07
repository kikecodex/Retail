import { NextRequest, NextResponse } from "next/server";
import {
    generarAnexo10_CV,
    generarAnexo11_DeclaracionPersonal,
    generarAnexo8_ExperienciaPostor,
    generarAnexo15_CompromisoPersonal,
    generarDocumentoCompleto,
    DatosProyecto,
    DatosPostor,
    DatosCV,
} from "@/lib/anexos-generator";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { tipoAnexo, proyecto, postor, datos } = body;

        if (!tipoAnexo || !proyecto || !postor) {
            return NextResponse.json(
                { error: "Faltan datos requeridos: tipoAnexo, proyecto, postor" },
                { status: 400 }
            );
        }

        const datosProyecto: DatosProyecto = {
            nomenclaturaProceso: proyecto.nomenclaturaProceso || "PROCESO DE SELECCIÓN",
            tipoModalidad: proyecto.tipoModalidad || "CONCURSO PÚBLICO",
            entidadConvocante: proyecto.entidadConvocante || "[ENTIDAD]",
            objetoContratacion: proyecto.objetoContratacion || "[OBJETO]",
            valorReferencial: proyecto.valorReferencial || "S/ 0.00",
            plazoEjecucion: proyecto.plazoEjecucion || "[PLAZO]",
        };

        const datosPostor: DatosPostor = {
            razonSocial: postor.razonSocial || "[RAZÓN SOCIAL]",
            ruc: postor.ruc || "[RUC]",
            representanteLegal: postor.representanteLegal || "[REPRESENTANTE]",
            dniRepresentante: postor.dniRepresentante || "[DNI]",
        };

        let anexoGenerado;
        let nombreArchivo;

        switch (tipoAnexo) {
            case "10": // CV de Personal Clave
                if (!datos.cv || !datos.cargo) {
                    return NextResponse.json(
                        { error: "Para Anexo 10 se requiere: datos.cv y datos.cargo" },
                        { status: 400 }
                    );
                }
                const cv: DatosCV = {
                    nombre: datos.cv.nombre || "[NOMBRE]",
                    dni: datos.cv.dni || "[DNI]",
                    universidad: datos.cv.universidad || "[UNIVERSIDAD]",
                    titulo: datos.cv.titulo || "[TÍTULO]",
                    colegiatura: datos.cv.colegiatura || "[N° COLEGIATURA]",
                    habilitacionVigente: datos.cv.habilitacionVigente ?? true,
                    experiencias: datos.cv.experiencias || [],
                };
                anexoGenerado = generarAnexo10_CV(datosProyecto, datosPostor, cv, datos.cargo);
                nombreArchivo = `anexo_10_cv_${cv.nombre.replace(/\s+/g, '_').toLowerCase()}`;
                break;

            case "11": // Declaración Jurada de Personal
                if (!datos.personalClave || !Array.isArray(datos.personalClave)) {
                    return NextResponse.json(
                        { error: "Para Anexo 11 se requiere: datos.personalClave (array)" },
                        { status: 400 }
                    );
                }
                anexoGenerado = generarAnexo11_DeclaracionPersonal(
                    datosProyecto,
                    datosPostor,
                    datos.personalClave
                );
                nombreArchivo = "anexo_11_declaracion_personal";
                break;

            case "8": // Experiencia del Postor
                if (!datos.experiencias || !Array.isArray(datos.experiencias)) {
                    return NextResponse.json(
                        { error: "Para Anexo 8 se requiere: datos.experiencias (array)" },
                        { status: 400 }
                    );
                }
                anexoGenerado = generarAnexo8_ExperienciaPostor(
                    datosProyecto,
                    datosPostor,
                    datos.experiencias
                );
                nombreArchivo = "anexo_8_experiencia_postor";
                break;

            case "15": // Compromiso del Personal
                if (!datos.profesional) {
                    return NextResponse.json(
                        { error: "Para Anexo 15 se requiere: datos.profesional" },
                        { status: 400 }
                    );
                }
                anexoGenerado = generarAnexo15_CompromisoPersonal(
                    datosProyecto,
                    datos.profesional,
                    datosPostor
                );
                nombreArchivo = `anexo_15_compromiso_${datos.profesional.nombre.replace(/\s+/g, '_').toLowerCase()}`;
                break;

            default:
                return NextResponse.json(
                    { error: `Tipo de anexo no soportado: ${tipoAnexo}. Soportados: 8, 10, 11, 15` },
                    { status: 400 }
                );
        }

        // Generar documento HTML completo
        const htmlCompleto = generarDocumentoCompleto(anexoGenerado);

        return NextResponse.json({
            success: true,
            anexo: {
                numero: anexoGenerado.numero,
                nombre: anexoGenerado.nombre,
                nombreArchivo: `${nombreArchivo}.html`,
                htmlContent: htmlCompleto,
            },
        });

    } catch (error) {
        console.error("❌ Error generando anexo:", error);
        const errorMessage = error instanceof Error ? error.message : "Error desconocido";

        return NextResponse.json(
            { error: "Error generando el anexo", detalle: errorMessage },
            { status: 500 }
        );
    }
}
