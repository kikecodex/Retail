// Generador de Anexos SEACE en formato DOCX
import {
    Document,
    Paragraph,
    Table,
    TableRow,
    TableCell,
    TextRun,
    AlignmentType,
    WidthType,
    Packer,
} from "docx";

export interface DatosGenerales {
    entidadContratante: string;
    nomenclaturaProceso: string;
    objetoContratacion: string;
    postor: {
        razonSocial: string;
        ruc: string;
        representanteLegal: string;
        dni: string;
        domicilio: string;
        telefono: string;
        email: string;
    };
    ciudad: string;
    fecha: string;
}

export interface PersonalClaveItem {
    puesto: string;
    nombres: string;
    dni: string;
    universidad: string;
    titulo: string;
    experienciaAnios: number;
    experienciaMeses: number;
    experienciaDias: number;
}

export interface ExperienciaPostorItem {
    numero: number;
    cliente: string;
    objetoContrato: string;
    montoContrato: number;
    fechaInicio: string;
    fechaFin: string;
    tipoDocumento: string;
    numeroDocumento: string;
}

export interface IntegranteConsorcio {
    razonSocial: string;
    ruc: string;
    representante: string;
    dni: string;
    participacion: number;
    obligaciones: string;
}

// Estilos comunes
const TITULO_STYLE = { bold: true, size: 24, font: "Arial" };
const NORMAL_STYLE = { size: 20, font: "Arial" };

function crearEncabezado(datos: DatosGenerales): Paragraph[] {
    return [
        new Paragraph({ children: [new TextRun({ text: "Señores", ...NORMAL_STYLE })] }),
        new Paragraph({ children: [new TextRun({ text: "EVALUADORES", bold: true, ...NORMAL_STYLE })] }),
        new Paragraph({ children: [new TextRun({ text: datos.nomenclaturaProceso, ...NORMAL_STYLE })] }),
        new Paragraph({ children: [new TextRun({ text: "Presente.-", ...NORMAL_STYLE })] }),
        new Paragraph({ children: [] }),
    ];
}

function crearFirma(datos: DatosGenerales): Paragraph[] {
    return [
        new Paragraph({ children: [] }),
        new Paragraph({ children: [new TextRun({ text: `${datos.ciudad}, ${datos.fecha}`, ...NORMAL_STYLE })] }),
        new Paragraph({ children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: ".................................................................", ...NORMAL_STYLE })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Firma, nombres y apellidos del representante legal", ...NORMAL_STYLE })] }),
    ];
}

// ANEXO 1
export function generarAnexo01(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 1", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DECLARACIÓN JURADA DE DATOS DEL POSTOR", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `El que suscribe, ${datos.postor.representanteLegal}, identificado con DNI N° ${datos.postor.dni}, representante legal de ${datos.postor.razonSocial}, con RUC N° ${datos.postor.ruc}, DECLARO BAJO JURAMENTO que la siguiente información se sujeta a la verdad:`, ...NORMAL_STYLE })] }),
                new Paragraph({ children: [] }),
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Razón Social", bold: true })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: datos.postor.razonSocial })] })] })] }),
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "RUC", bold: true })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: datos.postor.ruc })] })] })] }),
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Domicilio", bold: true })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: datos.postor.domicilio })] })] })] }),
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Email", bold: true })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: datos.postor.email })] })] })] }),
                    ],
                }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 2
export function generarAnexo02(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO N° 2", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PACTO DE INTEGRIDAD", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `El que suscribe, ${datos.postor.representanteLegal}, representante legal de ${datos.postor.razonSocial}, DECLARO BAJO JURAMENTO:`, ...NORMAL_STYLE })] }),
                new Paragraph({ children: [] }),
                new Paragraph({ children: [new TextRun({ text: "1. Me comprometo a conducirme con veracidad, probidad y transparencia.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "2. Me comprometo a no incurrir en actos de corrupción, fraude o colusión.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "3. Me comprometo a comunicar cualquier acto o conducta ilícita.", ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 3
export function generarAnexo03(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 3", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DECLARACIÓN JURADA", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `El que suscribe, ${datos.postor.representanteLegal}, con RUC N° ${datos.postor.ruc}, DECLARO BAJO JURAMENTO:`, ...NORMAL_STYLE })] }),
                new Paragraph({ children: [] }),
                new Paragraph({ children: [new TextRun({ text: "1. No tener impedimento para contratar con el Estado (Art. 30 Ley N° 32069).", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "2. Conocer y aceptar las bases del procedimiento de selección.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "3. Ser responsable de la veracidad de los documentos presentados.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "4. Mantener la oferta durante el procedimiento.", ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 4
export function generarAnexo04(datos: DatosGenerales, integrantes: IntegranteConsorcio[], representanteComun: string): Document {
    const rows = [
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Integrante", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "RUC", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "% Participación", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Obligaciones", bold: true })] })] }),
            ]
        }),
        ...integrantes.map(i => new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: i.razonSocial })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: i.ruc })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: `${i.participacion}%` })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: i.obligaciones })] })] }),
            ]
        })),
    ];
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 4", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PROMESA DE CONSORCIO", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: "Los que suscriben declaran su compromiso de constituir consorcio:", ...NORMAL_STYLE })] }),
                new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows }),
                new Paragraph({ children: [new TextRun({ text: `Representante común: ${representanteComun}`, bold: true, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 5
export function generarAnexo05(datos: DatosGenerales, nombreProfesional: string, cargo: string): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 5", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "CARTA DE COMPROMISO DEL PERSONAL CLAVE", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `El que suscribe, ${nombreProfesional}, me COMPROMETO a prestar servicios como ${cargo} en caso de que ${datos.postor.razonSocial} resulte adjudicado.`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 6
export function generarAnexo06(datos: DatosGenerales, montoTotal: number, incluyeIGV: boolean = true): Document {
    const montoSinIGV = incluyeIGV ? montoTotal / 1.18 : montoTotal;
    const igv = incluyeIGV ? montoTotal - montoSinIGV : montoTotal * 0.18;
    const montoConIGV = incluyeIGV ? montoTotal : montoTotal * 1.18;
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 6", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PRECIO DE LA OFERTA", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "CONCEPTO", bold: true })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "MONTO (S/)", bold: true })] })] })] }),
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Sub Total" })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: montoSinIGV.toFixed(2) })] })] })] }),
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "IGV (18%)" })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: igv.toFixed(2) })] })] })] }),
                        new TableRow({ children: [new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "TOTAL", bold: true })] })] }), new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: montoConIGV.toFixed(2), bold: true })] })] })] }),
                    ],
                }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 7
export function generarAnexo07(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO N° 7", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "AUTORIZACIÓN DE RETENCIÓN COMO GARANTÍA", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `El que suscribe, ${datos.postor.representanteLegal}, AUTORIZO a la entidad a retener el 10% del monto del contrato como garantía de fiel cumplimiento.`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 8
export function generarAnexo08(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 8", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "AUTORIZACIÓN DE NOTIFICACIONES", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `AUTORIZO notificaciones a: ${datos.postor.email}`, ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: `Domicilio: ${datos.postor.domicilio}`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 9
export function generarAnexo09(datos: DatosGenerales, institucionArbitral: string = "Centro de Arbitraje PUCP"): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO N° 9", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ELECCIÓN DE INSTITUCIÓN ARBITRAL", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `ELIJO la siguiente institución arbitral: ${institucionArbitral}`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 10
export function generarAnexo10(datos: DatosGenerales, experiencias: ExperienciaPostorItem[]): Document {
    const rows = [
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "N°", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Cliente", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Objeto", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Monto", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Fecha Inicio", bold: true })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Fecha Fin", bold: true })] })] }),
            ]
        }),
        ...experiencias.map(e => new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: e.numero.toString() })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: e.cliente })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: e.objetoContrato })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: e.montoContrato.toString() })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: e.fechaInicio })] })] }),
                new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: e.fechaFin })] })] }),
            ]
        })),
    ];
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 10", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "EXPERIENCIA DEL POSTOR EN LA ESPECIALIDAD", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 11
export function generarAnexo11(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 11", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DECLARACIÓN JURADA", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: "1. Documentación veraz y auténtica.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "2. Sin procesos judiciales pendientes.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "3. Cumplimiento de obligaciones tributarias y laborales.", ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 12
export function generarAnexo12(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 12", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DJ CUMPLIMIENTO DE CONDICIONES", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: "1. Inscrito en RNP.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "2. No inhabilitado.", ...NORMAL_STYLE })] }),
                new Paragraph({ children: [new TextRun({ text: "3. Capacidad libre de contratación.", ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 13
export function generarAnexo13(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 13", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "SOLICITUD BONIFICACIÓN 10% (PROVINCIAS)", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `SOLICITO bonificación del 10% por domicilio fuera de Lima y Callao.`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 14
export function generarAnexo14(datos: DatosGenerales, plazoOfertado: string): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 14", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PLAZO DE EJECUCIÓN OFERTADO", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `Plazo ofertado: ${plazoOfertado}`, bold: true, size: 28, font: "Arial" })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 15
export function generarAnexo15(datos: DatosGenerales, personalClave: PersonalClaveItem[]): Document {
    const headerRow = new TableRow({
        children: [
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "PUESTO", bold: true })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "NOMBRES", bold: true })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "DNI", bold: true })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "UNIVERSIDAD", bold: true })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "TÍTULO", bold: true })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "EXPERIENCIA", bold: true })] })] }),
        ]
    });
    const dataRows = personalClave.map(p => new TableRow({
        children: [
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: p.puesto })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: p.nombres })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: p.dni })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: p.universidad })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: p.titulo })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: `${p.experienciaAnios}a ${p.experienciaMeses}m ${p.experienciaDias}d` })] })] }),
        ]
    }));
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 15", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "EXPERIENCIA Y CALIFICACIONES DEL PERSONAL CLAVE", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [headerRow, ...dataRows] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 16
export function generarAnexo16(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 16", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DECLARACIÓN JURADA - REDAM", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `DECLARO no estar inscrito en el REDAM del Poder Judicial.`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// ANEXO 17
export function generarAnexo17(datos: DatosGenerales): Document {
    return new Document({
        sections: [{
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ANEXO Nº 17", ...TITULO_STYLE })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "SOLICITUD BONIFICACIÓN 5% (MYPE)", ...TITULO_STYLE })] }),
                ...crearEncabezado(datos),
                new Paragraph({ children: [new TextRun({ text: `SOLICITO bonificación del 5% por condición de MYPE.`, ...NORMAL_STYLE })] }),
                ...crearFirma(datos),
            ],
        }],
    });
}

// Utilidad
export async function generarDocxBuffer(doc: Document): Promise<Buffer> {
    return await Packer.toBuffer(doc);
}

// Lista completa
export const ANEXOS_DISPONIBLES = [
    { numero: "01", nombre: "Datos del Postor" },
    { numero: "02", nombre: "Pacto de Integridad" },
    { numero: "03", nombre: "Declaración Jurada (Art. 30)" },
    { numero: "04", nombre: "Promesa de Consorcio" },
    { numero: "05", nombre: "Carta de Compromiso Personal" },
    { numero: "06", nombre: "Precio de la Oferta" },
    { numero: "07", nombre: "Autorización de Retención" },
    { numero: "08", nombre: "Autorización de Notificaciones" },
    { numero: "09", nombre: "Elección Institución Arbitral" },
    { numero: "10", nombre: "Experiencia del Postor" },
    { numero: "11", nombre: "Declaración Jurada General" },
    { numero: "12", nombre: "DJ Cumplimiento Condiciones" },
    { numero: "13", nombre: "Bonificación 10% Provincias" },
    { numero: "14", nombre: "Plazo de Ejecución" },
    { numero: "15", nombre: "Personal Clave" },
    { numero: "16", nombre: "DJ REDAM" },
    { numero: "17", nombre: "Bonificación 5% MYPE" },
];
