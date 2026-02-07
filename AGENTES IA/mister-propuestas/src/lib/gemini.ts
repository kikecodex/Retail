import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export const geminiModel = genAI.getGenerativeModel({
  model: "gemini-2.0-flash"
});

export interface NumeralRequisito {
  numeral: string;           // Ej: "2.1", "3.2.1"
  titulo: string;            // Título del numeral
  requisito: string;         // Qué están pidiendo específicamente
  documento?: string;        // Documento o anexo relacionado
  obligatorio: boolean;
}

export interface CapituloAnalizado {
  numero: string;
  titulo: string;
  resumen: string;           // Resumen breve del capítulo
  numerales: NumeralRequisito[];  // Requisitos específicos de cada numeral
  puntosClaves: string[];    // Solo los puntos más críticos
}

export interface ExperienciaRequerida {
  especialidad: string;           // Ej: "Obras Viales, Puertos y Afines"
  subespecialidad?: string;       // Ej: "Vías Urbanas"
  tipologias: string[];           // Ej: ["Vías expresas", "arteriales", "pistas"]
  tiempoMeses: number;            // Tiempo en meses
  tiempoTexto: string;            // Ej: "36 meses desde colegiatura"
  participacionRequerida?: string; // Ej: "100% del tiempo de ejecución"
}

export interface RequisitoPerfil {
  cargo: string;                  // Ej: "Supervisor de Obra"
  cantidad: number;
  profesionesAceptadas: string[]; // Ej: ["Ingeniero Civil", "Ingeniero de Higiene y Seguridad"]
  cargosDesempenados: string[];   // Ej: ["Residente y/o jefe", "supervisor y/o residente principal"]
  experienciaGeneral: ExperienciaRequerida;    // Experiencia general mínima
  experienciaEspecifica: ExperienciaRequerida; // Experiencia específica en tipologías
  certificacionesRequeridas: string[];
  funcionesPrincipales: string[];
  requisitosAdicionales?: string; // Otros requisitos (habilitación, colegiatura, etc.)
}

export interface AnexoDetectado {
  numero: string;
  nombre: string;
  tipo: string;
  campos: string[];
  obligatorio: boolean;
}

export interface AlertaBase {
  tipo: "requisito_oculto" | "contradiccion" | "plazo_critico" | "experiencia_restrictiva" | "certificacion_especifica" | "formato_documento" | "penalidad_abusiva" | "garantia_adicional" | "rnp_especifico" | "consorcio_restringido" | "direccionamiento" | "subsanacion_corta";
  severidad: "CRITICO" | "ALTO" | "MEDIO";
  descripcion: string;
  seccion: string;          // Dónde se encontró: "Cap. III, numeral 3.2.1"
  requisito_exacto: string; // Texto exacto del requisito problemático
  recomendacion: string;    // Qué hacer al respecto
}

export interface AnalisisBasesResult {
  // Información General
  nomenclaturaProceso: string;
  tipoModalidad: string;
  entidadConvocante: string;
  objetoContratacion: string;
  valorReferencial: string;
  plazoEjecucion: string;

  // Especialidad del Proceso
  especialidadProceso: string;
  subespecialidadProceso?: string;
  tipologiasProceso: string[];

  // Análisis por Capítulos
  capitulos: CapituloAnalizado[];

  // Requisitos de Personal
  requisitos: RequisitoPerfil[];

  // Anexos detectados
  anexosDetectados: AnexoDetectado[];

  // Criterios de Evaluación
  criteriosEvaluacion: {
    factor: string;
    puntajeMaximo: number;
    descripcion: string;
  }[];

  // 🚨 ALERTAS Y TRAMPAS DETECTADAS
  alertas: AlertaBase[];

  // Resumen ejecutivo
  resumen: string;
}

// Contexto especializado por módulo vertical
function getContextoModulo(modulo: string): string {
  switch (modulo) {
    case "supervision":
      return `
## CONTEXTO DEL MÓDULO: SUPERVISIÓN DE OBRAS
Estas bases son para SUPERVISIÓN DE OBRA. Presta especial atención a:
- **Personal clave típico**: Jefe de Supervisión, Ingeniero de Control, Especialista en Calidad, 
  Especialista en Seguridad, Especialista en Medio Ambiente, Especialista en Estructuras
- **Cargos válidos para experiencia**: "Supervisor", "Jefe de Supervisión", "Inspector", 
  "Coordinador de Supervisión", "Residente de Supervisión"
- **Documentos clave de supervisión**: Plan de Supervisión, reportes mensuales/semanales, 
  cuaderno de obra, control de calidad, ensayos de laboratorio
- **Experiencia específica**: Buscar "supervisión de obra" o "inspección de obra", NO confundir 
  con "ejecución" o "consultoría"
- **Tipologías comunes**: Edificaciones, viales, saneamiento, electromecánicas, hidráulicas
- **Participación requerida**: Generalmente 100% del plazo de supervisión
`;
    case "obras":
      return `
## CONTEXTO DEL MÓDULO: EJECUCIÓN DE OBRAS
Estas bases son para EJECUCIÓN/CONSTRUCCIÓN DE OBRA. Presta especial atención a:
- **Personal clave típico**: Residente de Obra, Maestro de Obra, Ing. de Seguridad y Salud, 
  Ing. Ambiental, Topógrafo, Especialistas por disciplina (Estructuras, Sanitarias, Eléctricas)
- **Cargos válidos para experiencia**: "Residente", "Jefe de Obra", "Director de Obra", 
  "Ingeniero de campo", "Maestro de Obra"
- **Documentos clave**: Calendario de Avance de Obra, PERT-CPM, Calendario Valorizado, 
  Plan de Seguridad y Salud, Plan de Manejo Ambiental, Presupuesto/S10
- **Experiencia específica**: Buscar "ejecución de obra" o "construcción", NO confundir con 
  "supervisión" o "consultoría"
- **Equipamiento**: Buscar equipamiento mínimo (maquinaria, herramientas, laboratorio)
- **Metrados**: Prestar atención a metrados y partidas del presupuesto
`;
    case "consultoria":
    default:
      return `
## CONTEXTO DEL MÓDULO: CONSULTORÍA DE OBRAS
Estas bases son para CONSULTORÍA (estudios, expedientes técnicos, perfiles). Atención a:
- **Personal clave típico**: Jefe de Proyecto, Especialista en Estructuras, Especialista en 
  Arquitectura, Especialista en Instalaciones Sanitarias/Eléctricas/Mecánicas, Especialista en 
  Geotecnia, Especialista en Impacto Ambiental, Especialista en Costos y Presupuestos
- **Cargos válidos para experiencia**: "Jefe de Proyecto", "Jefe de Estudio", "Proyectista", 
  "Consultor", "Especialista"
- **Entregables clave**: Expediente Técnico, Estudio de Pre-Inversión, Informe de 
  Compatibilidad, Memoria Descriptiva, Planos, Especificaciones Técnicas, Metrados, Presupuesto
- **Experiencia específica**: Buscar "consultoría de obra" o "elaboración de expediente técnico"
- **TDR**: Los Términos de Referencia son el capítulo más crítico
`;
  }
}

export async function analizarBases(contenidoBases: string, modulo: string = "consultoria"): Promise<AnalisisBasesResult> {
  const contextoModulo = getContextoModulo(modulo);
  const prompt = `
Eres un experto en licitaciones públicas peruanas (SEACE/OSCE). 
Analiza las siguientes BASES DE LICITACIÓN por capítulos.
${contextoModulo}

## ESTRUCTURA TÍPICA DE BASES SEACE:
- CAPÍTULO I: Disposiciones Generales
- CAPÍTULO II: Del Procedimiento de Selección  
- CAPÍTULO III: Términos de Referencia / Especificaciones Técnicas
- CAPÍTULO IV: Criterios de Evaluación y Calificación
- CAPÍTULO V: Proforma del Contrato
- ANEXOS: Formatos a llenar

## ANALIZA Y EXTRAE:

### 1. INFORMACIÓN GENERAL (CRÍTICO - BUSCAR EN LAS PRIMERAS PÁGINAS):
- **NOMENCLATURA DEL PROCESO**: Es el identificador oficial, ejemplo: 
  "CONCURSO PÚBLICO N°001-2025-ENTIDAD-1"
  "ADJUDICACIÓN SIMPLIFICADA N°002-2025-MDCH/CS"
  "CONCURSO PÚBLICO ABREVIADO N°021-2025-GRA/E-1"
  Buscar después de frases como "BASES INTEGRADAS", "BASES ADMINISTRATIVAS", "CONVOCATORIA"
- **TIPO DE MODALIDAD**: Solo el tipo (CONCURSO PÚBLICO, ADJUDICACIÓN SIMPLIFICADA, SUBASTA INVERSA, etc.)
- Entidad convocante
- Objeto de contratación
- Valor referencial (S/)
- Plazo de ejecución

### 2. ANÁLISIS POR CAPÍTULOS - EXTRACCIÓN DETALLADA NUMERAL POR NUMERAL:
Para cada capítulo, extrae TODOS los requisitos específicos:
- Número y título del capítulo
- Resumen ejecutivo (máximo 2 líneas)
- **NUMERALES**: Para CADA numeral/numeral del capítulo extraer:
  - Número del numeral (ej: "2.1", "3.2.1", "II.5")
  - Título del numeral  
  - QUÉ ESTÁN PIDIENDO exactamente (ser muy específico)
  - Documento o anexo relacionado si aplica
  - Si es obligatorio o no
- Solo los 3-5 puntos más críticos como puntosClaves

IMPORTANTE - REGLAS ESTRICTAS:
❌ NO generes resúmenes teóricos como "Este capítulo trata sobre...", "Este numeral establece..."
❌ NO escribas descripciones de lo que contiene el capítulo
✅ SÍ extrae TEXTUALMENTE lo que piden: documentos, plazos, montos, requisitos específicos

EJEMPLOS:
❌ INCORRECTO: "Este numeral trata sobre las declaraciones juradas que debe presentar el postor"
✅ CORRECTO: "Presentar Anexo N°3 - Declaración Jurada firmada por representante legal"

❌ INCORRECTO: "Este capítulo describe el procedimiento de selección y sus etapas"
✅ CORRECTO: numerales: [
  {"numeral": "2.1", "titulo": "Convocatoria", "requisito": "Publicación en SEACE", "obligatorio": true},
  {"numeral": "2.2", "titulo": "Registro", "requisito": "Electrónico automático hasta antes de presentación de ofertas", "obligatorio": true}
]

### 3. ESPECIALIDAD DEL PROCESO (CRÍTICO - buscar en sección de Requisitos de Calificación):
- **Especialidad**: Ej: "Obras Viales, Puertos y Afines", "Consultoría de Obras", "Edificaciones"
- **Subespecialidad**: Ej: "Vías Urbanas", "Saneamiento", "Edificaciones Educativas"
- **Tipologías aceptadas**: Lista de tipologías del listado DGA (ej: "vías expresas", "arteriales", "pistas", "colectoras")

### 4. PERSONAL CLAVE - EXTRACCIÓN DETALLADA (buscar tablas B.1 y B.2):
Para cada profesional requerido extraer EXACTAMENTE:

**DATOS DEL CARGO:**
- Cargo exacto: "Supervisor de Obra", "Especialista en Seguridad y Salud en Obra"
- Cantidad requerida
- Todas las profesiones aceptadas: ["Ingeniero Civil", "Ingeniero de Higiene y Seguridad Industrial", "Ingeniero de Seguridad y Salud en el Trabajo"]
- Cargos desempeñados válidos para experiencia: ["Residente y/o jefe", "supervisor y/o jefe", "residente principal"]

**EXPERIENCIA GENERAL:**
- Tiempo en MESES (convertir años a meses si es necesario)
- Texto original (ej: "36 meses computados desde la colegiatura")
- Especialidad requerida para la experiencia

**EXPERIENCIA ESPECÍFICA:**
- Tiempo en MESES
- Especialidad/Subespecialidad/Tipologías requeridas
- Participación del profesional (ej: "100% del tiempo de ejecución de la obra")

**OTROS REQUISITOS:**
- Certificaciones obligatorias
- Requisitos adicionales (habilitación vigente, colegiatura, etc.)

### 4. ANEXOS DETECTADOS:
- Número del anexo
- Nombre completo
- Tipo (CV, experiencia, declaración jurada, etc.)
- Campos que debe contener
- Si es obligatorio

### 5. CRITERIOS DE EVALUACIÓN (Capítulo IV):
- Factor de evaluación
- Puntaje máximo
- Descripción del criterio

### 6. 🚨 DETECCIÓN FORENSE DE TRAMPAS Y REQUISITOS OCULTOS (CRÍTICO):
Analiza CADA LÍNEA buscando estos 12 tipos de trampas que descalifican propuestas:

**TIPO 1 - requisito_oculto**: Requisitos escondidos en secciones inesperadas (ej: en la proforma del contrato piden documentos de presentación)
**TIPO 2 - contradiccion**: Información contradictoria entre capítulos (Cap. II dice X, Cap. V dice Y)
**TIPO 3 - plazo_critico**: Plazos que hacen imposible tramitar documentos a tiempo (vigencia de poder, certificaciones, etc.)
**TIPO 4 - experiencia_restrictiva**: Experiencia específica excesivamente limitante (tipologías muy estrechas, meses exagerados, cargos muy específicos)
**TIPO 5 - certificacion_especifica**: Certificaciones ISO u otras que pocos tienen y dan mucho puntaje
**TIPO 6 - formato_documento**: Requisitos de formato muy específicos (original notarializado, legalizado, apostillado, firmado digitalmente)
**TIPO 7 - penalidad_abusiva**: Penalidades desproporcionadas en la proforma del contrato
**TIPO 8 - garantia_adicional**: Garantías adicionales a la de fiel cumplimiento (adelantos, adicionales, etc.)
**TIPO 9 - rnp_especifico**: RNP con especialidad o categoría muy específica que limita participación
**TIPO 10 - consorcio_restringido**: Restricciones a consorcios (líder debe tener X%, experiencia solo del líder, etc.)
**TIPO 11 - direccionamiento**: Especificaciones que apuntan a una marca/modelo/proveedor específico
**TIPO 12 - subsanacion_corta**: Plazos de subsanación muy cortos (24h, 48h) para documentos complejos

Para CADA trampa encontrada, indicar:
- tipo: uno de los 12 tipos
- severidad: CRITICO (descalifica seguro), ALTO (probable descalificación), MEDIO (ventaja/desventaja)
- descripcion: explicación clara de por qué es una trampa
- seccion: dónde está exactamente (Cap., numeral, página)
- requisito_exacto: copiar el TEXTO EXACTO de las bases
- recomendacion: qué hacer para cumplir o impugnar

⚠️ SÉ EXHAUSTIVO: es mejor reportar una alerta de más que perder una. Una sola alerta no detectada puede significar la descalificación.

Responde ÚNICAMENTE en formato JSON válido:
{
  "nomenclaturaProceso": "CONCURSO PÚBLICO N°XXX-2025-ENTIDAD-X",
  "tipoModalidad": "CONCURSO PÚBLICO",
  "entidadConvocante": "...",
  "objetoContratacion": "...",
  "valorReferencial": "S/ XXX,XXX.XX",
  "plazoEjecucion": "XXX días calendario",
  "especialidadProceso": "Obras Viales, Puertos y Afines",
  "subespecialidadProceso": "Vías Urbanas",
  "tipologiasProceso": ["Vías expresas", "arteriales", "colectoras", "pistas"],
  "capitulos": [
    {
      "numero": "I", 
      "titulo": "ASPECTOS GENERALES", 
      "resumen": "Breve resumen de 2 líneas",
      "numerales": [
        {"numeral": "1.1", "titulo": "Objeto", "requisito": "Requisito específico", "documento": "Anexo X", "obligatorio": true}
      ],
      "puntosClaves": ["Punto crítico 1"]
    }
  ],
  "requisitos": [
    {
      "cargo": "Supervisor de Obra",
      "cantidad": 1,
      "profesionesAceptadas": ["Ingeniero Civil"],
      "cargosDesempenados": ["Residente y/o jefe", "supervisor y/o jefe de supervisión"],
      "experienciaGeneral": {
        "especialidad": "Obras Viales, Puertos y Afines",
        "subespecialidad": "Vías Urbanas",
        "tipologias": ["vías expresas", "arteriales", "pistas"],
        "tiempoMeses": 36,
        "tiempoTexto": "36 meses computados desde la colegiatura",
        "participacionRequerida": "100% del tiempo de ejecución"
      },
      "experienciaEspecifica": {
        "especialidad": "Obras Viales",
        "tipologias": ["pistas", "veredas", "arteriales"],
        "tiempoMeses": 24,
        "tiempoTexto": "24 meses en obras similares"
      },
      "certificacionesRequeridas": ["Habilitación vigente CIP"],
      "funcionesPrincipales": ["Supervisar ejecución de obra"]
    }
  ],
  "anexosDetectados": [
    {"numero": "1", "nombre": "...", "tipo": "...", "campos": ["..."], "obligatorio": true}
  ],
  "criteriosEvaluacion": [
    {"factor": "...", "puntajeMaximo": 100, "descripcion": "..."}
  ],
  "alertas": [
    {
      "tipo": "experiencia_restrictiva",
      "severidad": "CRITICO",
      "descripcion": "Se exige experiencia específica en supervisión de obras de saneamiento rural con más de 5000 conexiones, lo cual es muy restrictivo",
      "seccion": "Cap. III, numeral 3.2, Tabla B.2",
      "requisito_exacto": "El profesional deberá acreditar experiencia específica en supervisión de obras de saneamiento rural con más de 5000 conexiones domiciliarias",
      "recomendacion": "Verificar si el personal propuesto tiene obras de saneamiento con esa cantidad de conexiones. Si no, considerar impugnar por ser excesivamente restrictivo."
    }
  ],
  "resumen": "..."
}

CONTENIDO DE LAS BASES:
${contenidoBases}
`;

  const result = await geminiModel.generateContent(prompt);
  const response = result.response.text();

  // Extraer JSON de la respuesta
  const jsonMatch = response.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("No se pudo extraer JSON de la respuesta de Gemini");
  }

  try {
    return JSON.parse(jsonMatch[0]);
  } catch {
    console.error("JSON inválido:", jsonMatch[0].substring(0, 500));
    throw new Error("La respuesta de Gemini no es JSON válido");
  }
}

export interface MapeoExperienciasResult {
  camposLlenados: {
    campo: string;
    valor: string;
    fuente: string;
  }[];
}

export async function mapearExperienciasACampos(
  experiencias: string,
  camposAnexo: string[]
): Promise<MapeoExperienciasResult> {
  const prompt = `
Eres un experto en licitaciones peruanas. Mapea las siguientes experiencias profesionales a los campos del anexo SEACE.

CAMPOS DEL ANEXO A LLENAR:
${camposAnexo.join("\n")}

EXPERIENCIAS DISPONIBLES:
${experiencias}

INSTRUCCIONES:
1. Para cada campo, selecciona la experiencia más relevante
2. Adapta el formato al requerido por SEACE
3. Incluye fechas, montos y entidades cuando corresponda
4. Si no hay información disponible, indica "NO DISPONIBLE"

Responde ÚNICAMENTE en formato JSON:
{
  "camposLlenados": [
    {
      "campo": "nombre del campo",
      "valor": "valor formateado para SEACE",
      "fuente": "de dónde se extrajo"
    }
  ]
}
`;

  const result = await geminiModel.generateContent(prompt);
  const response = result.response.text();

  const jsonMatch = response.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("No se pudo extraer JSON de la respuesta");
  }

  return JSON.parse(jsonMatch[0]);
}
