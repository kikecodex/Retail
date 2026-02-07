// ANEXO 1 - Formato exacto según BASES+SUPER.pdf líneas 2929-2990
// Declaración Jurada de Datos del Postor - Persona Jurídica

import {
    Document,
    Paragraph,
    Table,
    TableRow,
    TableCell,
    TextRun,
    AlignmentType,
    WidthType,
    BorderStyle,
    CheckBox,
} from "docx";

export interface DatosPostorCompleto {
    // Datos del procedimiento (extraídos de las bases)
    nomenclaturaProceso: string; // ej: "CONCURSO PUBLICO N° 01-2026-MDHs/CS"

    // Datos del postor (del formulario)
    tipoPostor: "PERSONA_JURIDICA" | "PERSONA_NATURAL" | "CONSORCIO";
    razonSocial: string;
    ruc: string;
    domicilioLegal: string;
    telefono: string;
    email: string;
    esMype: boolean;

    // Datos del representante legal (persona jurídica)
    representanteLegal: {
        nombres: string;
        tipoDocumento: "DNI" | "CE" | "PASAPORTE";
        numeroDocumento: string;
        sedeRegistral: string;
        partidaRegistral: string;
        asiento: string;
    };

    // Ciudad y fecha
    ciudad: string;
    fecha: string;
}

const FONT_ARIAL_10 = { size: 20, font: "Arial" }; // size 20 = 10pt

function crearCeldaLabel(texto: string): TableCell {
    return new TableCell({
        width: { size: 35, type: WidthType.PERCENTAGE },
        children: [
            new Paragraph({
                children: [new TextRun({ text: texto, bold: true, ...FONT_ARIAL_10 })],
            }),
        ],
        borders: {
            top: { style: BorderStyle.SINGLE, size: 1 },
            bottom: { style: BorderStyle.SINGLE, size: 1 },
            left: { style: BorderStyle.SINGLE, size: 1 },
            right: { style: BorderStyle.SINGLE, size: 1 },
        },
    });
}

function crearCeldaValor(texto: string): TableCell {
    return new TableCell({
        width: { size: 65, type: WidthType.PERCENTAGE },
        children: [
            new Paragraph({
                children: [new TextRun({ text: texto, ...FONT_ARIAL_10 })],
            }),
        ],
        borders: {
            top: { style: BorderStyle.SINGLE, size: 1 },
            bottom: { style: BorderStyle.SINGLE, size: 1 },
            left: { style: BorderStyle.SINGLE, size: 1 },
            right: { style: BorderStyle.SINGLE, size: 1 },
        },
    });
}

export function generarAnexo01Exacto(datos: DatosPostorCompleto): Document {
    const parrafos: Paragraph[] = [];

    // Título
    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            children: [new TextRun({ text: "ANEXO Nº 1", bold: true, size: 24, font: "Arial" })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
            children: [new TextRun({ text: "DECLARACIÓN JURADA DE DATOS DEL POSTOR", bold: true, size: 24, font: "Arial" })],
        })
    );

    // Encabezado: Señores, Evaluadores, etc.
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "Señores", ...FONT_ARIAL_10 })] }));
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "EVALUADORES", bold: true, ...FONT_ARIAL_10 })] }));
    parrafos.push(
        new Paragraph({
            children: [
                new TextRun({ text: "CONCURSO PÚBLICO PARA CONSULTORÍA DE OBRA ", ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.nomenclaturaProceso, ...FONT_ARIAL_10 }),
            ],
        })
    );
    parrafos.push(new Paragraph({ children: [new TextRun({ text: "Presente.-", ...FONT_ARIAL_10 })] }));
    parrafos.push(new Paragraph({ children: [] })); // Línea en blanco

    // Cuerpo de la declaración
    const tipoDoc = datos.representanteLegal.tipoDocumento;
    const numDoc = datos.representanteLegal.numeroDocumento;

    parrafos.push(
        new Paragraph({
            spacing: { after: 200 },
            children: [
                new TextRun({ text: `El que suscribe, `, ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.representanteLegal.nombres, bold: true, ...FONT_ARIAL_10 }),
                new TextRun({ text: `, postor o representante legal de `, ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.razonSocial, bold: true, ...FONT_ARIAL_10 }),
                new TextRun({ text: `, identificado con ${tipoDoc} N° `, ...FONT_ARIAL_10 }),
                new TextRun({ text: numDoc, bold: true, ...FONT_ARIAL_10 }),
                new TextRun({ text: `, con poder inscrito en la Sede Registral de `, ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.representanteLegal.sedeRegistral, bold: true, ...FONT_ARIAL_10 }),
                new TextRun({ text: ` en la Partida Registral Nº `, ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.representanteLegal.partidaRegistral, bold: true, ...FONT_ARIAL_10 }),
                new TextRun({ text: ` Asiento Nº `, ...FONT_ARIAL_10 }),
                new TextRun({ text: datos.representanteLegal.asiento, bold: true, ...FONT_ARIAL_10 }),
                new TextRun({ text: `, DECLARO BAJO JURAMENTO que la siguiente información se sujeta a la verdad:`, ...FONT_ARIAL_10 }),
            ],
        })
    );

    parrafos.push(new Paragraph({ children: [] })); // Línea en blanco

    // Tabla de datos del postor
    const tablaDatos = new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
            new TableRow({ children: [crearCeldaLabel("Nombre, Denominación o Razón Social:"), crearCeldaValor(datos.razonSocial)] }),
            new TableRow({ children: [crearCeldaLabel("Domicilio Legal:"), crearCeldaValor(datos.domicilioLegal)] }),
            new TableRow({
                children: [
                    new TableCell({
                        width: { size: 17.5, type: WidthType.PERCENTAGE },
                        children: [new Paragraph({ children: [new TextRun({ text: "RUC:", bold: true, ...FONT_ARIAL_10 })] })],
                        borders: { top: { style: BorderStyle.SINGLE, size: 1 }, bottom: { style: BorderStyle.SINGLE, size: 1 }, left: { style: BorderStyle.SINGLE, size: 1 }, right: { style: BorderStyle.SINGLE, size: 1 } },
                    }),
                    new TableCell({
                        width: { size: 32.5, type: WidthType.PERCENTAGE },
                        children: [new Paragraph({ children: [new TextRun({ text: datos.ruc, ...FONT_ARIAL_10 })] })],
                        borders: { top: { style: BorderStyle.SINGLE, size: 1 }, bottom: { style: BorderStyle.SINGLE, size: 1 }, left: { style: BorderStyle.SINGLE, size: 1 }, right: { style: BorderStyle.SINGLE, size: 1 } },
                    }),
                    new TableCell({
                        width: { size: 17.5, type: WidthType.PERCENTAGE },
                        children: [new Paragraph({ children: [new TextRun({ text: "Teléfono(s):", bold: true, ...FONT_ARIAL_10 })] })],
                        borders: { top: { style: BorderStyle.SINGLE, size: 1 }, bottom: { style: BorderStyle.SINGLE, size: 1 }, left: { style: BorderStyle.SINGLE, size: 1 }, right: { style: BorderStyle.SINGLE, size: 1 } },
                    }),
                    new TableCell({
                        width: { size: 32.5, type: WidthType.PERCENTAGE },
                        children: [new Paragraph({ children: [new TextRun({ text: datos.telefono, ...FONT_ARIAL_10 })] })],
                        borders: { top: { style: BorderStyle.SINGLE, size: 1 }, bottom: { style: BorderStyle.SINGLE, size: 1 }, left: { style: BorderStyle.SINGLE, size: 1 }, right: { style: BorderStyle.SINGLE, size: 1 } },
                    }),
                ],
            }),
            new TableRow({
                children: [
                    new TableCell({
                        width: { size: 17.5, type: WidthType.PERCENTAGE },
                        children: [new Paragraph({ children: [new TextRun({ text: "MYPE:", bold: true, ...FONT_ARIAL_10 })] })],
                        borders: { top: { style: BorderStyle.SINGLE, size: 1 }, bottom: { style: BorderStyle.SINGLE, size: 1 }, left: { style: BorderStyle.SINGLE, size: 1 }, right: { style: BorderStyle.SINGLE, size: 1 } },
                    }),
                    new TableCell({
                        columnSpan: 3,
                        children: [
                            new Paragraph({
                                children: [
                                    new TextRun({ text: datos.esMype ? "[X] Sí   [ ] No" : "[ ] Sí   [X] No", ...FONT_ARIAL_10 }),
                                ],
                            }),
                        ],
                        borders: { top: { style: BorderStyle.SINGLE, size: 1 }, bottom: { style: BorderStyle.SINGLE, size: 1 }, left: { style: BorderStyle.SINGLE, size: 1 }, right: { style: BorderStyle.SINGLE, size: 1 } },
                    }),
                ],
            }),
            new TableRow({ children: [crearCeldaLabel("Correo electrónico:"), crearCeldaValor(datos.email)] }),
        ],
    });

    parrafos.push(new Paragraph({ children: [] })); // Espaciado

    // Autorización de notificación
    parrafos.push(
        new Paragraph({
            spacing: { before: 200 },
            children: [new TextRun({ text: "Autorización de notificación por correo electrónico:", bold: true, ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));

    parrafos.push(
        new Paragraph({
            children: [new TextRun({ text: "Autorizo que se notifiquen al correo electrónico indicado las siguientes actuaciones:", ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));

    // Lista de actuaciones
    const actuaciones = [
        "1. Solicitud de negociación regulado en el artículo 132 del Reglamento de la Ley N° 32069, Ley General de Contrataciones Públicas, aprobado por Decreto Supremo N° 009-2025-EF.",
        "2. Solicitud de subsanación de los requisitos para perfeccionar el contrato.",
        "3. Solicitud para presentar los documentos para perfeccionar el contrato, según orden de prelación, de conformidad con lo previsto en el numeral 91.3 del artículo 91 del Reglamento de la Ley N° 32069, Ley General de Contrataciones Públicas, aprobado mediante Decreto Supremo N° 009-2025-EF.",
        "4. Respuesta a la solicitud de acceso al expediente de contratación.",
        "5. Notificación de la orden de servicio, de ser el caso.",
    ];

    actuaciones.forEach((act) => {
        parrafos.push(
            new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: act, size: 18, font: "Arial" })], // size 18 = 9pt para las actuaciones
            })
        );
    });

    parrafos.push(new Paragraph({ children: [] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Ciudad y fecha
    parrafos.push(
        new Paragraph({
            children: [new TextRun({ text: `${datos.ciudad}, ${datos.fecha}`, ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Firma
    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: ".................................................................", ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "Firma, nombres y apellidos del postor o", ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "representante legal, según corresponda", ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(new Paragraph({ children: [] }));
    parrafos.push(new Paragraph({ children: [] }));

    // Advertencia
    parrafos.push(
        new Paragraph({
            children: [new TextRun({ text: "Advertencia", bold: true, ...FONT_ARIAL_10 })],
        })
    );

    parrafos.push(
        new Paragraph({
            spacing: { after: 100 },
            children: [
                new TextRun({
                    text: "La notificación dirigida a la dirección de correo electrónico consignada en esta declaración jurada se entiende válidamente efectuada al día hábil siguiente de su realización, de conformidad con la Decimotercera Disposición Complementaria Transitoria del Reglamento.",
                    size: 18,
                    font: "Arial",
                    italics: true,
                }),
            ],
        })
    );

    return new Document({
        sections: [
            {
                properties: {
                    page: {
                        margin: {
                            top: 720, // 0.5 inch
                            right: 720,
                            bottom: 720,
                            left: 720,
                        },
                    },
                },
                children: [
                    ...parrafos.slice(0, 7),
                    tablaDatos,
                    ...parrafos.slice(7),
                ],
            },
        ],
    });
}
