/**
 * Document Vision - Extracción de tablas de PDFs usando Gemini Vision
 * 
 * Convierte páginas de PDF a imágenes y usa Gemini Vision para extraer
 * tablas estructuradas como Personal Clave (B.1 y B.2)
 */

import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

// Modelo con capacidades de visión
const visionModel = genAI.getGenerativeModel({
    model: "gemini-2.0-flash"
});

export interface PersonalClaveExtraido {
    cargo: string;
    cantidad: number;
    profesionesAceptadas: string[];
    cargosDesempenados: string[];
    experienciaGeneral: {
        tiempoMeses: number;
        tiempoTexto: string;
        especialidad: string;
        tipologias: string[];
    };
    experienciaEspecifica: {
        tiempoMeses: number;
        tiempoTexto: string;
        tipologias: string[];
    };
    participacionRequerida: string;
}

export interface TablaExtraidaResult {
    tipoTabla: "B1_CALIFICACION" | "B2_EXPERIENCIA" | "OTRA";
    personal: PersonalClaveExtraido[];
    especialidadProceso?: string;
    subespecialidadProceso?: string;
    tipologiasProceso?: string[];
}

/**
 * Analiza una imagen de tabla y extrae los datos estructurados
 * usando Gemini Vision
 */
export async function analizarTablaConVision(
    imageBase64: string,
    mimeType: string = "image/png"
): Promise<TablaExtraidaResult | null> {

    const prompt = `Eres un experto en licitaciones públicas peruanas. Analiza esta TABLA de un documento de bases de licitación.

IDENTIFICA EL TIPO DE TABLA:
1. **B.1 CALIFICACIÓN DEL PERSONAL CLAVE**: Tabla con columnas como "Cantidad", "Cargo", "Título Profesional"
2. **B.2 EXPERIENCIA DEL PERSONAL CLAVE**: Tabla detallada con "Cargo", "Profesión", "Cargo desempeñado", "Tipo de experiencia", "Tiempo de experiencia"

EXTRAE TODOS LOS DATOS DE LA TABLA:

Para cada fila de profesional, extrae:
- **cargo**: El puesto exacto (ej: "Supervisor de Obra", "Especialista en Seguridad")
- **cantidad**: Número requerido (default 1)
- **profesionesAceptadas**: TODAS las profesiones válidas mencionadas (ej: ["Ingeniero Civil", "Ingeniero de Higiene y Seguridad Industrial"])
- **cargosDesempenados**: Cargos que pueden haber tenido para validar experiencia (ej: ["Residente y/o jefe", "supervisor"])
- **experienciaGeneral**: 
  - tiempoMeses: Número EXACTO de meses (convertir años a meses: 3 años = 36 meses)
  - tiempoTexto: Texto original (ej: "36 meses computados desde la colegiatura")
  - especialidad: Especialidad requerida
  - tipologias: Lista de tipologías válidas
- **experienciaEspecifica**:
  - tiempoMeses: Meses de experiencia específica
  - tiempoTexto: Texto original
  - tipologias: Tipologías específicas requeridas
- **participacionRequerida**: Porcentaje de participación (ej: "100% del tiempo de ejecución")

TAMBIÉN EXTRAE si está visible:
- especialidadProceso: La especialidad general del proceso
- subespecialidadProceso: La subespecialidad
- tipologiasProceso: Lista de tipologías del listado DGA

Responde SOLO en formato JSON válido:
{
  "tipoTabla": "B1_CALIFICACION" | "B2_EXPERIENCIA" | "OTRA",
  "especialidadProceso": "Obras Viales, Puertos y Afines",
  "subespecialidadProceso": "Vías Urbanas",
  "tipologiasProceso": ["Vías expresas", "arteriales", "pistas"],
  "personal": [
    {
      "cargo": "Supervisor de Obra",
      "cantidad": 1,
      "profesionesAceptadas": ["Ingeniero Civil"],
      "cargosDesempenados": ["Residente y/o jefe", "supervisor"],
      "experienciaGeneral": {
        "tiempoMeses": 36,
        "tiempoTexto": "36 meses desde colegiatura",
        "especialidad": "Obras Viales",
        "tipologias": ["vías expresas", "arteriales"]
      },
      "experienciaEspecifica": {
        "tiempoMeses": 24,
        "tiempoTexto": "24 meses en obras similares",
        "tipologias": ["pistas", "veredas"]
      },
      "participacionRequerida": "100% del tiempo de ejecución"
    }
  ]
}

Si NO es una tabla de personal clave, retorna: {"tipoTabla": "OTRA", "personal": []}`;

    try {
        const imagePart = {
            inlineData: {
                data: imageBase64,
                mimeType: mimeType,
            },
        };

        const result = await visionModel.generateContent([prompt, imagePart]);
        const response = result.response.text();

        // Extraer JSON de la respuesta
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            console.error("No se pudo extraer JSON de la respuesta de Vision");
            return null;
        }

        const parsed = JSON.parse(jsonMatch[0]) as TablaExtraidaResult;
        return parsed;

    } catch (error) {
        console.error("Error analizando tabla con Vision:", error);
        return null;
    }
}

/**
 * Convierte un buffer de imagen a base64
 */
export function bufferToBase64(buffer: Buffer): string {
    return buffer.toString("base64");
}

/**
 * Detecta páginas con tablas de personal clave en el texto del PDF
 * Retorna los números de página que probablemente contienen tablas B.1/B.2
 */
export function detectarPaginasConTablas(texto: string): {
    tieneTablaB1: boolean;
    tieneTablaB2: boolean;
    indicadores: string[];
} {
    const indicadoresB1 = [
        "B.1 CALIFICACIÓN DEL PERSONAL",
        "CALIFICACIÓN DEL PERSONAL CLAVE",
        "Cantidad.*Cargo.*Título Profesional",
    ];

    const indicadoresB2 = [
        "B.2 EXPERIENCIA DEL PERSONAL",
        "EXPERIENCIA DEL PERSONAL CLAVE",
        "PLANTEL PROFESIONAL CLAVE",
        "Cargo desempeñado.*Tipo de experiencia.*Tiempo",
    ];

    const encontrados: string[] = [];

    const tieneB1 = indicadoresB1.some(ind => {
        const regex = new RegExp(ind, "i");
        if (regex.test(texto)) {
            encontrados.push(`B.1: ${ind}`);
            return true;
        }
        return false;
    });

    const tieneB2 = indicadoresB2.some(ind => {
        const regex = new RegExp(ind, "i");
        if (regex.test(texto)) {
            encontrados.push(`B.2: ${ind}`);
            return true;
        }
        return false;
    });

    return {
        tieneTablaB1: tieneB1,
        tieneTablaB2: tieneB2,
        indicadores: encontrados
    };
}

/**
 * Combina resultados de múltiples tablas extraídas
 */
export function combinarResultadosTablas(
    resultados: TablaExtraidaResult[]
): PersonalClaveExtraido[] {
    const personalMap = new Map<string, PersonalClaveExtraido>();

    for (const resultado of resultados) {
        if (resultado.tipoTabla === "OTRA") continue;

        for (const persona of resultado.personal) {
            const key = persona.cargo.toLowerCase().trim();

            if (personalMap.has(key)) {
                // Combinar información si ya existe
                const existing = personalMap.get(key)!;

                // Merge profesiones
                const profesiones = new Set([
                    ...existing.profesionesAceptadas,
                    ...persona.profesionesAceptadas
                ]);
                existing.profesionesAceptadas = Array.from(profesiones);

                // Usar la experiencia más detallada
                if (persona.experienciaGeneral.tiempoMeses > 0) {
                    existing.experienciaGeneral = persona.experienciaGeneral;
                }
                if (persona.experienciaEspecifica.tiempoMeses > 0) {
                    existing.experienciaEspecifica = persona.experienciaEspecifica;
                }

            } else {
                personalMap.set(key, { ...persona });
            }
        }
    }

    return Array.from(personalMap.values());
}
