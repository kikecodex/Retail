// ANEXO 3 - Formato exacto según modelo real CONSORCIO TEC PISCOBAMBA
// Declaración Jurada General

import {
    Document,
    Paragraph,
    TextRun,
    AlignmentType,
} from "docx";

export interface DatosDeclaracionJurada {
    nomenclaturaProceso: string;
    tipoPostor: "PERSONA_JURIDICA" | "PERSONA_NATURAL" | "CONSORCIO";
    // Datos del firmante
    nombreFirmante: string;
    tipoDocumento: "DNI" | "CE" | "PASAPORTE";
    numeroDocumento: string;
    // Si es persona jurídica
    razonSocialEmpresa?: string;
    // Si es representante común de consorcio
    esRepresentanteComun?: boolean;
    nombreConsorcio?: string;
    // Ubicación y fecha
    ciudad: string;
    dia: number;
    mes: string;
    anio: number;
}

const FONT_ARIAL_10 = { size: 20, font: "Arial" }; // size 20 = 10pt
const FONT_ARIAL_10_BOLD = { size: 20, font: "Arial", bold: true };

export function generarAnexo03Exacto(datos: DatosDeclaracionJurada): Document {
    const parrafos: Paragraph[] = [];

    // Título
    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            children: [new TextRun({ text: "ANEXO N°03", ...FONT_ARIAL_10_BOLD })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
            children: [new TextRun({ text: "DECLARACIÓN JURADA", ...FONT_ARIAL_10_BOLD })],
        })
    );

    // Encabezado estándar
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "Señores", ...FONT_ARIAL_10 })] }));
    parrafos.push(new Paragraph({ children: [new TextRun({ text: datos.nomenclaturaProceso, ...FONT_ARIAL_10_BOLD })] }));
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "Presente.-", ...FONT_ARIAL_10 })] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Párrafo de identificación
    let textoIdentificacion = `Mediante el presente el suscrito, `;
    textoIdentificacion += `${datos.nombreFirmante}, `;

    if (datos.esRepresentanteComun && datos.nombreConsorcio) {
        textoIdentificacion += `postor y/o representante común del ${datos.nombreConsorcio}, `;
    } else if (datos.tipoPostor === "PERSONA_JURIDICA" && datos.razonSocialEmpresa) {
        textoIdentificacion += `postor y/o representante legal de ${datos.razonSocialEmpresa}, `;
    } else {
        textoIdentificacion += `postor, `;
    }

    textoIdentificacion += `identificado con ${datos.tipoDocumento} N°${datos.numeroDocumento}, declaro bajo juramento:`;

    parrafos.push(
        new Paragraph({
            spacing: { after: 200 },
            children: [
                new TextRun({ text: "Mediante el presente el suscrito, ", ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.nombreFirmante, ...FONT_ARIAL_10_BOLD }),
                new TextRun({ text: ", ", ...FONT_ARIAL_10 }),
                ...(datos.esRepresentanteComun && datos.nombreConsorcio
                    ? [new TextRun({ text: `postor y/o representante común del `, ...FONT_ARIAL_10 }), new TextRun({ text: datos.nombreConsorcio, ...FONT_ARIAL_10_BOLD })]
                    : datos.tipoPostor === "PERSONA_JURIDICA" && datos.razonSocialEmpresa
                        ? [new TextRun({ text: `postor y/o representante legal de `, ...FONT_ARIAL_10 }), new TextRun({ text: datos.razonSocialEmpresa, ...FONT_ARIAL_10_BOLD })]
                        : [new TextRun({ text: `postor`, ...FONT_ARIAL_10 })]),
                new TextRun({ text: `, identificado con `, ...FONT_ARIAL_10 }),
                new TextRun({ text: `${datos.tipoDocumento} N°${datos.numeroDocumento}`, ...FONT_ARIAL_10_BOLD }),
                new TextRun({ text: `, declaro bajo juramento:`, ...FONT_ARIAL_10 }),
            ],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));

    // Declaraciones (6 puntos según el modelo)
    const declaraciones = [
        "No tener impedimento para postular en el procedimiento de selección ni para contratar con el Estado, conforme al artículo 30 de la Ley General de Contrataciones Públicas.",
        "Conocer las sanciones contenidas en la Ley General de Contrataciones Públicas y su Reglamento, así como las disposiciones aplicables de la Ley N° 27444, Ley del Procedimiento Administrativo General.",
        "Participar en el presente proceso de contratación en forma independiente sin mediar consulta, comunicación, acuerdo, arreglo o convenio con ningún proveedor; y, conocer las disposiciones del Decreto Legislativo N° 1034, Decreto Legislativo que aprueba la Ley de Represión de Conductas Anticompetitivas.",
        "Conocer, aceptar y someterme a las bases, condiciones y reglas del procedimiento de selección.",
        "Ser responsable de la veracidad de los documentos e información que presento en el presente procedimiento de selección.",
        "Comprometerme a mantener la oferta presentada durante el procedimiento de selección y a perfeccionar el contrato, en caso de resultar favorecido con la buena pro.",
    ];

    declaraciones.forEach((decl, idx) => {
        parrafos.push(
            new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: `${idx + 1}. ${decl}`, ...FONT_ARIAL_10 })],
            })
        );
    });

    parrafos.push(new Paragraph({ children: [] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Fecha y lugar
    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.LEFT,
            spacing: { after: 400 },
            children: [
                new TextRun({ text: `[${datos.ciudad.toUpperCase()}, ${datos.dia} DE ${datos.mes.toUpperCase()} DEL ${datos.anio}]`, ...FONT_ARIAL_10 }),
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

    // Si es representante común
    if (datos.esRepresentanteComun) {
        parrafos.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "REPRESENTANTE COMUN", ...FONT_ARIAL_10_BOLD })],
            })
        );
    }

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
