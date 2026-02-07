import { NextRequest, NextResponse } from "next/server";
import { geminiModel } from "@/lib/gemini";
import { parseDocument } from "@/lib/parsers/document-parser";

// ============== INTERFACES ==============

export interface CVParseado {
    nombre: string;
    dni: string;
    universidad: string;
    titulo: string;
    colegiatura?: string;
    habilitacionVigente?: boolean;
    fechaHabilidad?: string;
    email?: string;
    telefono?: string;
    experiencias: {
        cargo: string;
        entidad: string;
        proyecto?: string;
        fechaInicio: string;
        fechaFin: string;
        descripcion?: string;
        meses?: number; // Calculado
    }[];
    certificaciones?: string[];
    maestrias?: string[];
    diplomados?: string[];
}

export interface RequisitoPersonal {
    perfil: string;
    cantidad: number;
    experienciaMinima: string;      // "5 años"
    experienciaEspecifica: string;  // "3 años en supervisión"
    formacionRequerida: string[];   // ["Ingeniero Civil", "Arquitecto"]
    certificaciones: string[];      // ["CIP vigente", "Maestría"]
}

export interface ValidacionProfesional {
    perfil: string;
    profesionalAsignado: string;

    // C.1 Calificación
    titulo: {
        requerido: string[];
        tiene: string;
        cumple: boolean;
    };
    colegiatura: {
        requerido: boolean;
        tiene: string | null;
        cumple: boolean;
    };
    habilidad: {
        requerido: boolean;
        vigente: boolean;
        fecha: string | null;
        cumple: boolean;
    };

    // C.2 Experiencia
    experienciaGeneral: {
        requerida: string;
        mesesRequeridos: number;
        mesesTiene: number;
        cumple: boolean;
    };
    experienciaEspecifica: {
        requerida: string;
        mesesRequeridos: number;
        mesesTiene: number;
        cumple: boolean;
    };

    // C.3 Certificaciones
    certificaciones: {
        requeridas: string[];
        tiene: string[];
        faltantes: string[];
        cumple: boolean;
    };

    // Estado general
    estado: "CUMPLE" | "REVISAR" | "NO_CUMPLE";
    documentosFaltantes: string[];
}

// ============== HELPERS ==============

function parsearMesesDeTexto(texto: string): number {
    if (!texto) return 0;

    const textoLower = texto.toLowerCase();
    let meses = 0;

    // Buscar años
    const aniosMatch = textoLower.match(/(\d+)\s*(años?|a[ñn]os?)/);
    if (aniosMatch) {
        meses += parseInt(aniosMatch[1]) * 12;
    }

    // Buscar meses adicionales
    const mesesMatch = textoLower.match(/(\d+)\s*meses?/);
    if (mesesMatch) {
        meses += parseInt(mesesMatch[1]);
    }

    return meses;
}

function calcularMesesExperiencia(experiencias: CVParseado["experiencias"]): number {
    let totalMeses = 0;

    for (const exp of experiencias) {
        if (!exp.fechaInicio || !exp.fechaFin) continue;

        // Parsear fechas (formatos: dd/mm/yyyy, mm/yyyy, yyyy)
        const parseDate = (fecha: string): Date | null => {
            const parts = fecha.split(/[\/\-]/);
            if (parts.length === 3) {
                // dd/mm/yyyy
                return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
            } else if (parts.length === 2) {
                // mm/yyyy
                return new Date(parseInt(parts[1]), parseInt(parts[0]) - 1, 1);
            } else if (parts.length === 1 && parts[0].length === 4) {
                // yyyy
                return new Date(parseInt(parts[0]), 0, 1);
            }
            return null;
        };

        const inicio = parseDate(exp.fechaInicio);
        let fin = parseDate(exp.fechaFin);

        // Si dice "actualidad" o "presente", usar fecha actual
        if (exp.fechaFin.toLowerCase().includes("actual") ||
            exp.fechaFin.toLowerCase().includes("presente")) {
            fin = new Date();
        }

        if (inicio && fin) {
            const meses = (fin.getFullYear() - inicio.getFullYear()) * 12 +
                (fin.getMonth() - inicio.getMonth());
            totalMeses += Math.max(0, meses);
        }
    }

    return totalMeses;
}

function calcularMesesExperienciaEspecifica(
    experiencias: CVParseado["experiencias"],
    perfil: string
): number {
    // Palabras clave por perfil
    const palabrasClave: Record<string, string[]> = {
        "jefe": ["jefe", "gerente", "director", "coordinador", "supervisor"],
        "arquitectura": ["arquitect", "diseño arquitect"],
        "estructuras": ["estructur", "calculo estructural"],
        "electrica": ["electric", "electromecan", "instalacion electr"],
        "sanitaria": ["sanitari", "drenaje", "agua", "desague"],
        "equipamiento": ["equipamiento", "mobiliario"],
        "geotecnia": ["geotecn", "suelo", "mecanica de suelos"],
        "costos": ["metrado", "costo", "presupuesto", "valorizacion"],
        "ambiental": ["ambiental", "impacto", "eia"],
        "comunicaciones": ["comunicacion", "data", "cableado"],
        "riesgos": ["riesgo", "desastre", "seguridad"],
        "formulacion": ["formulacion", "proyecto", "pip", "snip"],
        "modelamiento": ["bim", "modelamiento", "revit", "3d"],
    };

    // Encontrar palabras clave relevantes
    const perfilLower = perfil.toLowerCase();
    let keywords: string[] = [];
    for (const [key, words] of Object.entries(palabrasClave)) {
        if (perfilLower.includes(key)) {
            keywords = words;
            break;
        }
    }

    if (keywords.length === 0) {
        // Si no hay keywords específicas, contar todo
        return calcularMesesExperiencia(experiencias);
    }

    // Filtrar experiencias relevantes
    const expRelevantes = experiencias.filter(exp => {
        const texto = `${exp.cargo} ${exp.proyecto || ""} ${exp.descripcion || ""}`.toLowerCase();
        return keywords.some(kw => texto.includes(kw));
    });

    return calcularMesesExperiencia(expRelevantes);
}

function verificarFormacion(cv: CVParseado, formacionRequerida: string[]): boolean {
    if (!formacionRequerida.length) return true;

    const tituloLower = (cv.titulo || "").toLowerCase();
    const uniLower = (cv.universidad || "").toLowerCase();

    return formacionRequerida.some(req => {
        const reqLower = req.toLowerCase();
        return tituloLower.includes(reqLower) || reqLower.includes(tituloLower);
    });
}

function verificarCertificaciones(cv: CVParseado, certRequeridas: string[]): {
    requeridas: string[];
    tiene: string[];
    faltantes: string[];
    cumple: boolean;
} {
    const tiene: string[] = [
        ...(cv.certificaciones || []),
        ...(cv.maestrias || []),
        ...(cv.diplomados || []),
    ];

    if (cv.colegiatura) {
        tiene.push(`Colegiatura: ${cv.colegiatura}`);
    }

    const faltantes = certRequeridas.filter(req => {
        const reqLower = req.toLowerCase();
        return !tiene.some(t => t.toLowerCase().includes(reqLower));
    });

    return {
        requeridas: certRequeridas,
        tiene,
        faltantes,
        cumple: faltantes.length === 0,
    };
}

// ============== VALIDACIÓN PRINCIPAL ==============

export function validarCumplimiento(
    cvs: CVParseado[],
    requisitos: RequisitoPersonal[],
    mapeo: Record<string, string>
): ValidacionProfesional[] {
    const validaciones: ValidacionProfesional[] = [];

    for (const req of requisitos) {
        const nombreProfesional = mapeo[req.perfil];
        const cv = cvs.find(c => c.nombre === nombreProfesional);

        const documentosFaltantes: string[] = [];

        // Si no hay CV asignado
        if (!cv) {
            validaciones.push({
                perfil: req.perfil,
                profesionalAsignado: "SIN ASIGNAR",
                titulo: { requerido: req.formacionRequerida, tiene: "", cumple: false },
                colegiatura: { requerido: true, tiene: null, cumple: false },
                habilidad: { requerido: true, vigente: false, fecha: null, cumple: false },
                experienciaGeneral: {
                    requerida: req.experienciaMinima,
                    mesesRequeridos: parsearMesesDeTexto(req.experienciaMinima),
                    mesesTiene: 0,
                    cumple: false
                },
                experienciaEspecifica: {
                    requerida: req.experienciaEspecifica,
                    mesesRequeridos: parsearMesesDeTexto(req.experienciaEspecifica),
                    mesesTiene: 0,
                    cumple: false
                },
                certificaciones: {
                    requeridas: req.certificaciones,
                    tiene: [],
                    faltantes: req.certificaciones,
                    cumple: false
                },
                estado: "NO_CUMPLE",
                documentosFaltantes: ["CV del profesional"],
            });
            continue;
        }

        // C.1 Título
        const tieneTitulo = verificarFormacion(cv, req.formacionRequerida);
        if (!tieneTitulo) documentosFaltantes.push("Título profesional requerido");

        // C.1 Colegiatura
        const tieneColegiatura = !!cv.colegiatura;
        if (!tieneColegiatura) documentosFaltantes.push("Colegiatura");

        // C.1 Habilidad
        const tieneHabilidad = cv.habilitacionVigente ?? false;
        if (!tieneHabilidad) documentosFaltantes.push("Certificado de Habilidad vigente");

        // C.2 Experiencia General
        const mesesReqGeneral = parsearMesesDeTexto(req.experienciaMinima);
        const mesesTieneGeneral = calcularMesesExperiencia(cv.experiencias);
        const cumpleExpGeneral = mesesTieneGeneral >= mesesReqGeneral;
        if (!cumpleExpGeneral) documentosFaltantes.push(`Experiencia general (faltan ${mesesReqGeneral - mesesTieneGeneral} meses)`);

        // C.2 Experiencia Específica
        const mesesReqEspecifica = parsearMesesDeTexto(req.experienciaEspecifica);
        const mesesTieneEspecifica = calcularMesesExperienciaEspecifica(cv.experiencias, req.perfil);
        const cumpleExpEspecifica = mesesTieneEspecifica >= mesesReqEspecifica;
        if (!cumpleExpEspecifica) documentosFaltantes.push(`Experiencia específica (faltan ${mesesReqEspecifica - mesesTieneEspecifica} meses)`);

        // C.3 Certificaciones
        const certResult = verificarCertificaciones(cv, req.certificaciones);
        if (!certResult.cumple) {
            documentosFaltantes.push(`Certificaciones: ${certResult.faltantes.join(", ")}`);
        }

        // Estado general
        let estado: "CUMPLE" | "REVISAR" | "NO_CUMPLE" = "CUMPLE";
        if (!tieneTitulo || !cumpleExpGeneral) {
            estado = "NO_CUMPLE";
        } else if (!tieneColegiatura || !tieneHabilidad || !cumpleExpEspecifica || !certResult.cumple) {
            estado = "REVISAR";
        }

        validaciones.push({
            perfil: req.perfil,
            profesionalAsignado: cv.nombre,
            titulo: {
                requerido: req.formacionRequerida,
                tiene: cv.titulo || "",
                cumple: tieneTitulo,
            },
            colegiatura: {
                requerido: true,
                tiene: cv.colegiatura || null,
                cumple: tieneColegiatura,
            },
            habilidad: {
                requerido: true,
                vigente: tieneHabilidad,
                fecha: cv.fechaHabilidad || null,
                cumple: tieneHabilidad,
            },
            experienciaGeneral: {
                requerida: req.experienciaMinima,
                mesesRequeridos: mesesReqGeneral,
                mesesTiene: mesesTieneGeneral,
                cumple: cumpleExpGeneral,
            },
            experienciaEspecifica: {
                requerida: req.experienciaEspecifica,
                mesesRequeridos: mesesReqEspecifica,
                mesesTiene: mesesTieneEspecifica,
                cumple: cumpleExpEspecifica,
            },
            certificaciones: certResult,
            estado,
            documentosFaltantes,
        });
    }

    return validaciones;
}

// ============== API HANDLER ==============

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const files = formData.getAll("files") as File[];
        const perfilesRequeridos = formData.get("perfilesRequeridos") as string;
        const requisitosJson = formData.get("requisitos") as string;

        if (!files || files.length === 0) {
            return NextResponse.json(
                { error: "Se requieren archivos de CVs" },
                { status: 400 }
            );
        }

        const cvsParseados: CVParseado[] = [];

        for (const file of files) {
            console.log(`📄 Procesando CV: ${file.name}`);

            const bytes = await file.arrayBuffer();
            const buffer = Buffer.from(bytes);
            const textoCV = await parseDocument(buffer, file.name);

            // Usar Gemini para extraer datos estructurados del CV
            const prompt = `
Eres un experto en analizar CVs de profesionales peruanos para licitaciones SEACE.

EXTRAE la siguiente información del CV:

1. DATOS PERSONALES:
   - Nombre completo
   - DNI
   - Colegiatura (CIP, CAP, etc.) - IMPORTANTE: busca número de colegiado
   - Email
   - Teléfono

2. FORMACIÓN ACADÉMICA:
   - Universidad o institución
   - Título o grado obtenido (Ingeniero Civil, Arquitecto, etc.)

3. HABILITACIÓN PROFESIONAL:
   - ¿Está habilitado/vigente en el colegio profesional?
   - Fecha de última habilidad (si aparece)

4. EXPERIENCIA PROFESIONAL (todas las que encuentres):
   - Cargo o puesto
   - Entidad/empresa
   - Nombre del proyecto (si aplica)
   - Fecha inicio (dd/mm/yyyy o mm/yyyy)
   - Fecha fin (dd/mm/yyyy, mm/yyyy, o "Actualidad")
   - Descripción breve

5. CERTIFICACIONES, MAESTRÍAS Y DIPLOMADOS:
   - Lista todas las certificaciones
   - Lista todas las maestrías
   - Lista todos los diplomados

Responde ÚNICAMENTE en JSON válido:
{
  "nombre": "...",
  "dni": "...",
  "universidad": "...",
  "titulo": "...",
  "colegiatura": "CIP 123456" o null,
  "habilitacionVigente": true/false,
  "fechaHabilidad": "dd/mm/yyyy" o null,
  "email": "...",
  "telefono": "...",
  "experiencias": [
    {
      "cargo": "...",
      "entidad": "...",
      "proyecto": "...",
      "fechaInicio": "mm/yyyy",
      "fechaFin": "mm/yyyy o Actualidad",
      "descripcion": "..."
    }
  ],
  "certificaciones": ["ISO 9001", "..."],
  "maestrias": ["Maestría en...", "..."],
  "diplomados": ["Diplomado en...", "..."]
}

CONTENIDO DEL CV:
${textoCV.substring(0, 20000)}
`;

            const result = await geminiModel.generateContent(prompt);
            const response = result.response.text();

            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const cvData = JSON.parse(jsonMatch[0]) as CVParseado;

                // Calcular meses de cada experiencia
                cvData.experiencias = cvData.experiencias.map(exp => ({
                    ...exp,
                    meses: calcularMesesExperiencia([exp]),
                }));

                cvsParseados.push(cvData);
                console.log(`✅ CV parseado: ${cvData.nombre} - ${cvData.experiencias.length} experiencias`);
            }
        }

        // Si hay perfiles requeridos, sugerir mapeo
        let sugerenciaMapeo: Record<string, string> = {};
        if (perfilesRequeridos) {
            const perfiles = JSON.parse(perfilesRequeridos);
            sugerenciaMapeo = await sugerirMapeo(cvsParseados, perfiles);
        }

        // Si hay requisitos, generar validación
        let validacion: ValidacionProfesional[] = [];
        if (requisitosJson && Object.keys(sugerenciaMapeo).length > 0) {
            const requisitos = JSON.parse(requisitosJson) as RequisitoPersonal[];
            validacion = validarCumplimiento(cvsParseados, requisitos, sugerenciaMapeo);
        }

        return NextResponse.json({
            success: true,
            cvsParseados,
            sugerenciaMapeo,
            validacion,
            mensaje: `${cvsParseados.length} CVs procesados correctamente`,
        });

    } catch (error) {
        console.error("Error procesando CVs:", error);
        return NextResponse.json(
            { error: "Error procesando los CVs" },
            { status: 500 }
        );
    }
}

async function sugerirMapeo(cvs: CVParseado[], perfiles: string[]): Promise<Record<string, string>> {
    const prompt = `
Dado los siguientes CVs y perfiles requeridos, sugiere qué profesional es el mejor para cada puesto.
Basa tu decisión en el título profesional y experiencia relevante.

CVS DISPONIBLES:
${cvs.map((cv, i) => `${i + 1}. ${cv.nombre} - ${cv.titulo} - Exp: ${cv.experiencias.length} registros - Colegiatura: ${cv.colegiatura || "No indicado"}`).join("\n")}

PERFILES REQUERIDOS:
${perfiles.map((p, i) => `${i + 1}. ${p}`).join("\n")}

Responde en JSON con el formato exacto:
{
  "perfil_requerido": "nombre_del_profesional"
}

IMPORTANTE: Usa el nombre exacto del profesional como aparece en la lista.
`;

    const result = await geminiModel.generateContent(prompt);
    const response = result.response.text();
    const jsonMatch = response.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
    }

    return {};
}
