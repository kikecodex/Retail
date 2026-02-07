// ANEXO 2 - Formato exacto según modelo real CONSORCIO TEC PISCOBAMBA
// Pacto de Integridad

import {
    Document,
    Paragraph,
    TextRun,
    AlignmentType,
} from "docx";

export interface DatosPactoIntegridad {
    nomenclaturaProceso: string;
    tipoPostor: "PERSONA_JURIDICA" | "PERSONA_NATURAL" | "CONSORCIO";
    // Datos del firmante
    nombreFirmante: string;
    tipoDocumento: "DNI" | "CE" | "PASAPORTE";
    numeroDocumento: string;
    // Si es persona jurídica
    razonSocialEmpresa?: string;
    sedeRegistral?: string;
    partidaRegistral?: string;
    asiento?: string;
    // Fecha
    dia: number;
    mes: string;
    anio: number;
}

const FONT_ARIAL_10 = { size: 20, font: "Arial" }; // size 20 = 10pt
const FONT_ARIAL_10_BOLD = { size: 20, font: "Arial", bold: true };

export function generarAnexo02Exacto(datos: DatosPactoIntegridad): Document {
    const parrafos: Paragraph[] = [];

    // Título
    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            children: [new TextRun({ text: "ANEXO N°02", ...FONT_ARIAL_10_BOLD })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
            children: [new TextRun({ text: "PACTO DE INTEGRIDAD", ...FONT_ARIAL_10_BOLD })],
        })
    );

    // Encabezado estándar
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "Señores", ...FONT_ARIAL_10 })] }));
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "EVALUADORES", ...FONT_ARIAL_10_BOLD })] }));
    parrafos.push(new Paragraph({ children: [new TextRun({ text: datos.nomenclaturaProceso, ...FONT_ARIAL_10_BOLD })] }));
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "Presente.-", ...FONT_ARIAL_10 })] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Párrafo de identificación
    let textoIdentificacion = `El que suscribe, `;
    if (datos.tipoPostor === "PERSONA_JURIDICA" && datos.razonSocialEmpresa) {
        textoIdentificacion += `${datos.nombreFirmante}, postor y/o representante legal de ${datos.razonSocialEmpresa}, identificado con ${datos.tipoDocumento} N°${datos.numeroDocumento}, con poder inscrito en la localidad de ${datos.sedeRegistral || "[SEDE]"} en la Partida N°${datos.partidaRegistral || "[PARTIDA]"} asiento ${datos.asiento || "[ASIENTO]"}, `;
    } else {
        textoIdentificacion += `${datos.nombreFirmante}, identificado con ${datos.tipoDocumento} N°${datos.numeroDocumento}, `;
    }
    textoIdentificacion += `en su calidad de proveedor en el ámbito de aplicación de la normativa de contratación pública, suscribo el presente Pacto de Integridad bajo los siguientes términos y condiciones:`;

    parrafos.push(
        new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({ text: textoIdentificacion, ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));

    // PRIMERO: Declaraciones
    parrafos.push(
        new Paragraph({
            spacing: { after: 100 },
            children: [new TextRun({ text: "PRIMERO: ", ...FONT_ARIAL_10_BOLD }), new TextRun({ text: "Declaro, bajo juramento:", ...FONT_ARIAL_10 })],
        })
    );

    const declaraciones = [
        "Que conozco los impedimentos para ser participante, postor, contratista o subcontratista, establecidos en el artículo 30 de la Ley N° 32069, Ley General de Contrataciones Públicas.",
        "Que los recursos que componen mi patrimonio o el patrimonio de la persona jurídica a la que represento no provienen de lavado de activos, narcotráfico, minería ilegal, financiamiento del terrorismo, y/o de cualquier actividad ilícita.",
        "Que conozco la obligación de denunciar cualquier acto de corrupción cometido por los actores del proceso de contratación, así como las medidas de protección que le asisten a los denunciantes; además de las consecuencias administrativas y legales que de estos se derivan.",
        "Que conozco el alcance de la Ley N° 28024, Ley que regula la gestión de intereses en la administración pública y su reglamento, aprobado por Decreto Supremo N° 120-2019-PCM, así como el marco de aplicación de la Ley N° 31564, Ley de prevención y mitigación del conflicto de intereses en el acceso y salida de personal del servicio público, y su reglamento aprobado por Decreto Supremo N° 082-2023-PCM.",
        "Que conozco el alcance de la cláusula anticorrupción y antisoborno de los contratos suscritos en el marco del proceso de contratación y las consecuencias derivadas de su incumplimiento.",
    ];

    declaraciones.forEach((decl, idx) => {
        parrafos.push(
            new Paragraph({
                spacing: { after: 100 },
                indent: { left: 360 },
                children: [new TextRun({ text: `${idx + 1}. ${decl}`, ...FONT_ARIAL_10 })],
            })
        );
    });

    parrafos.push(new Paragraph({ children: [] }));

    // SEGUNDO: Compromisos
    parrafos.push(
        new Paragraph({
            spacing: { after: 100 },
            children: [new TextRun({ text: "SEGUNDO: ", ...FONT_ARIAL_10_BOLD }), new TextRun({ text: "Dentro de ese marco, asumo los siguientes compromisos:", ...FONT_ARIAL_10 })],
        })
    );

    const compromisos = [
        {
            texto: "Que mantendré una conducta proba e íntegra en todas las actividades del proceso de contratación, lo que supone actuar con honestidad y veracidad, sin cometer actos ilícitos, directa o indirectamente, así como respetar la libertad de concurrencia y las condiciones de competencia efectiva en el proceso de contratación y abstenerme de realizar prácticas que la restrinjan o afecten.",
            extensionPJ: "[Solo para personas jurídicas] Lo anterior se hace extensivo, para conocimiento, a los socios, accionistas, participacionistas, integrantes de los órganos de administración, apoderados, representantes legales, funcionarios, asesores y personas vinculadas a la persona jurídica que represento.",
        },
        {
            texto: "Que me abstendré de ofrecer, dar o prometer regalos, cortesías, invitaciones, donativos u otros beneficios similares, a funcionarios o servidores públicos de la dependencia encargada de las contrataciones, actores del proceso de contratación y personal de la entidad contratante.",
        },
        {
            texto: "Que denunciaré ante las autoridades competentes, de manera oportuna, los actos de corrupción, inconducta funcional, conflicto de intereses u otro de naturaleza similar, respecto de lo cual tuviera conocimiento en el marco del proceso de contratación (https://denuncias.servicios.gob.pe/).",
        },
        {
            texto: "Que facilitaré las acciones o mecanismos implementados por la entidad pública responsable del proceso de contratación para fortalecer la transparencia, promover la lucha contra la corrupción y fomentar la rendición de cuentas.",
        },
    ];

    compromisos.forEach((comp, idx) => {
        parrafos.push(
            new Paragraph({
                spacing: { after: 100 },
                indent: { left: 360 },
                children: [new TextRun({ text: `${idx + 1}. ${comp.texto}`, ...FONT_ARIAL_10 })],
            })
        );

        // Extensión para personas jurídicas
        if (comp.extensionPJ && datos.tipoPostor === "PERSONA_JURIDICA") {
            parrafos.push(
                new Paragraph({
                    spacing: { after: 100 },
                    indent: { left: 720 },
                    children: [new TextRun({ text: comp.extensionPJ, italics: true, ...FONT_ARIAL_10 })],
                })
            );
        }
    });

    parrafos.push(new Paragraph({ children: [] }));

    // TERCERO: Vigencia
    parrafos.push(
        new Paragraph({
            spacing: { after: 200 },
            children: [
                new TextRun({ text: "TERCERO: ", ...FONT_ARIAL_10_BOLD }),
                new TextRun({ text: "Este pacto de integridad tiene vigencia desde el momento de su suscripción hasta la culminación de la fase de selección; y, en caso de resultar adjudicado con la buena pro, este mantiene su vigencia hasta la finalización del proceso de contratación.", ...FONT_ARIAL_10 }),
            ],
        })
    );

    // CUARTO: Sometimiento
    parrafos.push(
        new Paragraph({
            spacing: { after: 200 },
            children: [
                new TextRun({ text: "CUARTO: ", ...FONT_ARIAL_10_BOLD }),
                new TextRun({ text: "Para efectos de salvaguardar el contenido del Pacto de Integridad frente a eventuales incumplimientos de los compromisos asumidos, me someto a las acciones de debida diligencia, supervisión, fiscalización posterior, iniciativas de veeduría autorizadas por la entidad contratante u otros que correspondan; así como a las responsabilidades administrativas, civiles y/o penales que se deriven de estos, conforme al marco legal vigente.", ...FONT_ARIAL_10 }),
            ],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));

    // Conformidad y fecha
    parrafos.push(
        new Paragraph({
            spacing: { after: 200 },
            children: [
                new TextRun({ text: `En señal de conformidad, suscribo el presente pacto de integridad, a los `, ...FONT_ARIAL_10 }),
                new TextRun({ text: `(${datos.dia}) `, ...FONT_ARIAL_10_BOLD }),
                new TextRun({ text: `días del mes `, ...FONT_ARIAL_10 }),
                new TextRun({ text: `(${datos.mes.toUpperCase()}) `, ...FONT_ARIAL_10_BOLD }),
                new TextRun({ text: `de ${datos.anio}, `, ...FONT_ARIAL_10 }),
                new TextRun({ text: `manifestando que la información declarada se sujeta al principio de presunción de veracidad, conforme a lo dispuesto en el artículo IV de la Ley N° 27444, Ley del Procedimiento Administrativo General.`, ...FONT_ARIAL_10 }),
            ],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Firma
    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "___________________________________", ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: datos.nombreFirmante, ...FONT_ARIAL_10_BOLD })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: `${datos.tipoDocumento} N°${datos.numeroDocumento}`, ...FONT_ARIAL_10 })],
        })
    );

    return new Document({
        sections: [
            {
                properties: {
                    page: {
                        margin: { top: 720, right: 720, bottom: 720, left: 720 },
                    },
                },
                children: parrafos,
            },
        ],
    });
}
