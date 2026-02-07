import { NextRequest, NextResponse } from "next/server";
import {
    generarAnexo02,
    generarAnexo03,
    generarAnexo04,
    generarAnexo05,
    generarAnexo06,
    generarAnexo07,
    generarAnexo08,
    generarAnexo09,
    generarAnexo10,
    generarAnexo11,
    generarAnexo12,
    generarAnexo13,
    generarAnexo14,
    generarAnexo15,
    generarAnexo16,
    generarAnexo17,
    generarDocxBuffer,
    DatosGenerales,
    PersonalClaveItem,
    ExperienciaPostorItem,
    IntegranteConsorcio,
    ANEXOS_DISPONIBLES,
} from "@/lib/generators/anexos-generator";
import { generarAnexo01Exacto, DatosPostorCompleto } from "@/lib/generators/anexo-01-exacto";
import { generarAnexo02Exacto, DatosPactoIntegridad } from "@/lib/generators/anexo-02-exacto";
import { generarAnexo03Exacto, DatosDeclaracionJurada } from "@/lib/generators/anexo-03-exacto";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { anexoNumero, datosGenerales, datosEspecificos } = body;

        if (!anexoNumero || !datosGenerales) {
            return NextResponse.json(
                { error: "Se requiere anexoNumero y datosGenerales" },
                { status: 400 }
            );
        }

        const datos: DatosGenerales = datosGenerales;
        let doc;
        let nombreArchivo = "";

        switch (anexoNumero) {
            case "01":
                // Usar el nuevo generador exacto
                const datosPostorCompleto: DatosPostorCompleto = {
                    nomenclaturaProceso: datos.nomenclaturaProceso,
                    tipoPostor: datosEspecificos?.tipoPostor || "PERSONA_JURIDICA",
                    razonSocial: datos.postor.razonSocial,
                    ruc: datos.postor.ruc,
                    domicilioLegal: datos.postor.domicilio,
                    telefono: datos.postor.telefono,
                    email: datos.postor.email,
                    esMype: datosEspecificos?.esMype || false,
                    representanteLegal: {
                        nombres: datos.postor.representanteLegal,
                        tipoDocumento: datosEspecificos?.tipoDocumento || "DNI",
                        numeroDocumento: datos.postor.dni,
                        sedeRegistral: datosEspecificos?.sedeRegistral || "",
                        partidaRegistral: datosEspecificos?.partidaRegistral || "",
                        asiento: datosEspecificos?.asiento || "",
                    },
                    ciudad: datos.ciudad,
                    fecha: datos.fecha,
                };
                doc = generarAnexo01Exacto(datosPostorCompleto);
                nombreArchivo = "Anexo_01_Datos_Postor.docx";
                break;

            case "02":
                // Usar nuevo generador exacto del Pacto de Integridad
                const fechaActual = new Date();
                const meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];
                const datosPacto: DatosPactoIntegridad = {
                    nomenclaturaProceso: datos.nomenclaturaProceso,
                    tipoPostor: datosEspecificos?.tipoPostor || "PERSONA_JURIDICA",
                    nombreFirmante: datos.postor.representanteLegal,
                    tipoDocumento: datosEspecificos?.tipoDocumento || "DNI",
                    numeroDocumento: datos.postor.dni,
                    razonSocialEmpresa: datos.postor.razonSocial,
                    sedeRegistral: datosEspecificos?.sedeRegistral,
                    partidaRegistral: datosEspecificos?.partidaRegistral,
                    asiento: datosEspecificos?.asiento,
                    dia: fechaActual.getDate(),
                    mes: meses[fechaActual.getMonth()],
                    anio: fechaActual.getFullYear(),
                };
                doc = generarAnexo02Exacto(datosPacto);
                nombreArchivo = "Anexo_02_Pacto_Integridad.docx";
                break;

            case "03":
                // Usar nuevo generador exacto de Declaración Jurada
                const fechaDJ = new Date();
                const mesesDJ = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];
                const datosDJ: DatosDeclaracionJurada = {
                    nomenclaturaProceso: datos.nomenclaturaProceso,
                    tipoPostor: datosEspecificos?.tipoPostor || "PERSONA_JURIDICA",
                    nombreFirmante: datos.postor.representanteLegal,
                    tipoDocumento: datosEspecificos?.tipoDocumento || "DNI",
                    numeroDocumento: datos.postor.dni,
                    razonSocialEmpresa: datos.postor.razonSocial,
                    ciudad: datos.ciudad,
                    dia: fechaDJ.getDate(),
                    mes: mesesDJ[fechaDJ.getMonth()],
                    anio: fechaDJ.getFullYear(),
                };
                doc = generarAnexo03Exacto(datosDJ);
                nombreArchivo = "Anexo_03_Declaracion_Jurada.docx";
                break;

            case "04":
                const integrantes: IntegranteConsorcio[] = datosEspecificos?.integrantes || [];
                const representanteComun: string = datosEspecificos?.representanteComun || "";
                doc = generarAnexo04(datos, integrantes, representanteComun);
                nombreArchivo = "Anexo_04_Promesa_Consorcio.docx";
                break;

            case "05":
                const nombreProfesional: string = datosEspecificos?.nombreProfesional || "";
                const cargo: string = datosEspecificos?.cargo || "";
                doc = generarAnexo05(datos, nombreProfesional, cargo);
                nombreArchivo = "Anexo_05_Carta_Compromiso.docx";
                break;

            case "06":
                const montoTotal: number = datosEspecificos?.montoTotal || 0;
                const incluyeIGV: boolean = datosEspecificos?.incluyeIGV ?? true;
                doc = generarAnexo06(datos, montoTotal, incluyeIGV);
                nombreArchivo = "Anexo_06_Precio_Oferta.docx";
                break;

            case "07":
                doc = generarAnexo07(datos);
                nombreArchivo = "Anexo_07_Autorizacion_Retencion.docx";
                break;

            case "08":
                doc = generarAnexo08(datos);
                nombreArchivo = "Anexo_08_Autorizacion_Notificaciones.docx";
                break;

            case "09":
                const institucionArbitral: string = datosEspecificos?.institucionArbitral || "Centro de Arbitraje PUCP";
                doc = generarAnexo09(datos, institucionArbitral);
                nombreArchivo = "Anexo_09_Eleccion_Arbitral.docx";
                break;

            case "10":
                const experiencias: ExperienciaPostorItem[] = datosEspecificos?.experiencias || [];
                doc = generarAnexo10(datos, experiencias);
                nombreArchivo = "Anexo_10_Experiencia_Postor.docx";
                break;

            case "11":
                doc = generarAnexo11(datos);
                nombreArchivo = "Anexo_11_Declaracion_Jurada.docx";
                break;

            case "12":
                doc = generarAnexo12(datos);
                nombreArchivo = "Anexo_12_DJ_Cumplimiento.docx";
                break;

            case "13":
                doc = generarAnexo13(datos);
                nombreArchivo = "Anexo_13_Bonificacion_10.docx";
                break;

            case "14":
                const plazoOfertado: string = datosEspecificos?.plazoOfertado || "";
                doc = generarAnexo14(datos, plazoOfertado);
                nombreArchivo = "Anexo_14_Plazo_Ejecucion.docx";
                break;

            case "15":
                const personalClave: PersonalClaveItem[] = datosEspecificos?.personalClave || [];
                doc = generarAnexo15(datos, personalClave);
                nombreArchivo = "Anexo_15_Personal_Clave.docx";
                break;

            case "16":
                doc = generarAnexo16(datos);
                nombreArchivo = "Anexo_16_DJ_REDAM.docx";
                break;

            case "17":
                doc = generarAnexo17(datos);
                nombreArchivo = "Anexo_17_Bonificacion_5.docx";
                break;

            default:
                return NextResponse.json(
                    { error: `Anexo ${anexoNumero} no implementado` },
                    { status: 400 }
                );
        }

        // Generar buffer del documento
        const buffer = await generarDocxBuffer(doc);

        // Retornar como descarga (convertir Buffer a Uint8Array para compatibilidad)
        return new NextResponse(new Uint8Array(buffer), {
            status: 200,
            headers: {
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "Content-Disposition": `attachment; filename="${nombreArchivo}"`,
            },
        });

    } catch (error) {
        console.error("Error generando anexo:", error);
        return NextResponse.json(
            { error: "Error generando el anexo" },
            { status: 500 }
        );
    }
}

// GET: Lista los anexos disponibles
export async function GET() {
    return NextResponse.json({
        anexosDisponibles: ANEXOS_DISPONIBLES.map(a => ({
            ...a,
            estado: "✅ Implementado"
        })),
    });
}
