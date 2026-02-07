"use client";

import { useState } from "react";

interface NumeralRequisito {
  numeral: string;           // Ej: "2.1", "3.2.1"
  titulo: string;            // Título del numeral
  requisito: string;         // Qué están pidiendo específicamente
  documento?: string;        // Documento o anexo relacionado
  obligatorio: boolean;
}

interface Capitulo {
  numero: string;
  titulo: string;
  resumen: string;
  numerales?: NumeralRequisito[];  // Requisitos específicos de cada numeral
  puntosClaves: string[];
}

interface ExperienciaRequerida {
  especialidad: string;
  subespecialidad?: string;
  tipologias: string[];
  tiempoMeses: number;
  tiempoTexto: string;
  participacionRequerida?: string;
}

interface Requisito {
  cargo: string;
  cantidad: number;
  profesionesAceptadas: string[];
  cargosDesempenados: string[];
  experienciaGeneral: ExperienciaRequerida;
  experienciaEspecifica: ExperienciaRequerida;
  certificacionesRequeridas: string[];
  funcionesPrincipales: string[];
  requisitosAdicionales?: string;
  // Compatibilidad con versión anterior
  perfil?: string;
  experienciaMinima?: string;
  formacionRequerida?: string[];
  certificaciones?: string[];
}

interface Anexo {
  numero: string;
  nombre: string;
  tipo: string;
  campos: string[];
  obligatorio: boolean;
}

interface CriterioEvaluacion {
  factor: string;
  puntajeMaximo: number;
  descripcion: string;
}

interface AlertaBase {
  tipo: string;
  severidad: "CRITICO" | "ALTO" | "MEDIO";
  descripcion: string;
  seccion: string;
  requisito_exacto: string;
  recomendacion: string;
}

interface AnalisisData {
  // CRÍTICO para anexos - extraído automáticamente de las bases
  nomenclaturaProceso: string;
  tipoModalidad: string;
  entidadConvocante: string;
  objetoContratacion: string;
  valorReferencial: string;
  plazoEjecucion: string;
  // Especialidad del Proceso
  especialidadProceso?: string;
  subespecialidadProceso?: string;
  tipologiasProceso?: string[];
  capitulos: Capitulo[];
  requisitos: Requisito[];
  anexosDetectados: Anexo[];
  criteriosEvaluacion: CriterioEvaluacion[];
  alertas?: AlertaBase[];
  resumen: string;
}

interface CVParseado {
  nombre: string;
  dni: string;
  universidad: string;
  titulo: string;
  colegiatura?: string;
  habilitacionVigente?: boolean;
  experiencias: { cargo: string; entidad: string; fechaInicio: string; fechaFin: string; meses?: number }[];
  certificaciones?: string[];
  maestrias?: string[];
  diplomados?: string[];
}

interface ValidacionProfesional {
  perfil: string;
  profesionalAsignado: string;
  titulo: { requerido: string[]; tiene: string; cumple: boolean };
  colegiatura: { requerido: boolean; tiene: string | null; cumple: boolean };
  habilidad: { requerido: boolean; vigente: boolean; fecha: string | null; cumple: boolean };
  experienciaGeneral: { requerida: string; mesesRequeridos: number; mesesTiene: number; cumple: boolean };
  experienciaEspecifica: { requerida: string; mesesRequeridos: number; mesesTiene: number; cumple: boolean };
  certificaciones: { requeridas: string[]; tiene: string[]; faltantes: string[]; cumple: boolean };
  estado: "CUMPLE" | "REVISAR" | "NO_CUMPLE";
  documentosFaltantes: string[];
}

interface DatosPostor {
  // Tipo de postor
  tipoPostor: "PERSONA_JURIDICA" | "PERSONA_NATURAL" | "CONSORCIO";
  // Datos de la empresa/persona
  razonSocial: string;
  ruc: string;
  domicilio: string;
  telefono: string;
  email: string;
  esMype: boolean;
  // Datos del representante legal
  representanteLegal: string;
  tipoDocumento: "DNI" | "CE" | "PASAPORTE";
  dni: string;
  // Datos registrales (solo persona jurídica)
  sedeRegistral: string;
  partidaRegistral: string;
  asiento: string;
}

interface ChecklistItem {
  id: string;
  categoria: "admision" | "calificacion" | "personal" | "evaluacion" | "economica" | "contrato";
  descripcion: string;
  anexo?: string;
  obligatorio: boolean;
  checked: boolean;
  observacion?: string;
  puntaje?: number;
}

export default function Home() {
  // Módulo vertical activo
  type ModuloVertical = "supervision" | "consultoria" | "obras" | null;
  const [moduloActivo, setModuloActivo] = useState<ModuloVertical>(null);

  const [step, setStep] = useState<1 | 2 | 3 | 4 | 5 | 6>(1);
  const [loading, setLoading] = useState(false);
  const [analisis, setAnalisis] = useState<AnalisisData | null>(null);
  const [tabActiva, setTabActiva] = useState<"capitulos" | "requisitos" | "anexos" | "evaluacion" | "alertas" | "checklist">("capitulos");
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([]);
  const [cvsParseados, setCvsParseados] = useState<CVParseado[]>([]);
  const [datosPostor, setDatosPostor] = useState<DatosPostor>({
    tipoPostor: "PERSONA_JURIDICA",
    razonSocial: "",
    ruc: "",
    domicilio: "",
    telefono: "",
    email: "",
    esMype: false,
    representanteLegal: "",
    tipoDocumento: "DNI",
    dni: "",
    sedeRegistral: "",
    partidaRegistral: "",
    asiento: "",
  });
  const [mapeoPersonal, setMapeoPersonal] = useState<Record<string, string>>({});
  const [validacionPersonal, setValidacionPersonal] = useState<ValidacionProfesional[]>([]);

  // Estado para el sistema de feedback/aprendizaje
  const [feedbackAnexo, setFeedbackAnexo] = useState<{
    anexoNum: string;
    contenido: string;
    calificacion: number;
    exitosa: boolean | null;
    enviando: boolean;
    enviado: boolean;
  } | null>(null);
  const [estadisticasRAG, setEstadisticasRAG] = useState<{
    totalPropuestas: number;
    propuestasExitosas: number;
    tasaExito: number;
    totalPatrones: number;
    mensaje: string;
  } | null>(null);

  // Generar checklist estructurado desde el análisis de bases
  const generarChecklistDesdeAnalisis = (data: AnalisisData, mod?: string | null): ChecklistItem[] => {
    const modulo = mod || moduloActivo || "consultoria";
    const items: ChecklistItem[] = [];
    let id = 0;

    // CAPÍTULO II - DOCUMENTOS DE ADMISIÍ“N
    const docsAdmision = [
      { desc: "Declaración Jurada de datos del postor", anexo: "Anexo N° 1" },
      { desc: "Pacto de Integridad", anexo: "Anexo N° 2" },
      { desc: "Documento que acredite la representación (Vigencia de poder o DNI)" },
      { desc: "Declaración jurada de veracidad y no impedimento Art. 33", anexo: "Anexo N° 3" },
      { desc: "Promesa de consorcio con firmas digitales/legalizadas (si aplica)", anexo: "Anexo N° 4" },
      { desc: "Documentación de desafectación del impedimento (si aplica)", anexo: "Anexo N° 5" },
      { desc: "Oferta Económica con estructura de costos", anexo: "Anexo N° 6" },
    ];
    docsAdmision.forEach(doc => {
      items.push({ id: `adm-${id++}`, categoria: "admision", descripcion: doc.desc, anexo: doc.anexo, obligatorio: true, checked: false });
    });

    // CAPÍTULO III - REQUISITOS DE CALIFICACIÓN
    const textoExperiencia = modulo === "supervision"
      ? "Acreditación de experiencia del postor en supervisión de obra"
      : modulo === "obras"
        ? "Acreditación de experiencia del postor en ejecución de obra"
        : "Acreditación de experiencia del postor en consultoría de obra";
    items.push({ id: `cal-${id++}`, categoria: "calificacion", descripcion: textoExperiencia, obligatorio: true, checked: false });
    items.push({ id: `cal-${id++}`, categoria: "calificacion", descripcion: "Declaración Jurada de Personal Clave propuesto", anexo: "Anexo N° 15", obligatorio: true, checked: false });

    // Personal clave con requisitos detallados
    if (data.requisitos?.length > 0) {
      data.requisitos.forEach((req, i) => {
        // Construir descripción detallada del perfil
        const detalles: string[] = [];

        // Nueva estructura con profesiones aceptadas
        if (req.profesionesAceptadas && req.profesionesAceptadas.length > 0) {
          detalles.push(`Profesión: ${req.profesionesAceptadas.join(" / ")}`);
        } else if (req.formacionRequerida && req.formacionRequerida.length > 0) {
          detalles.push(`Formación: ${req.formacionRequerida.join(" / ")}`);
        }

        // Experiencia general con meses
        if (req.experienciaGeneral?.tiempoMeses) {
          detalles.push(`Exp. General: ${req.experienciaGeneral.tiempoMeses} meses`);
        } else if (req.experienciaMinima) {
          detalles.push(`Exp. General: ${req.experienciaMinima}`);
        }

        // Experiencia específica con meses
        if (req.experienciaEspecifica && typeof req.experienciaEspecifica === "object" && req.experienciaEspecifica.tiempoMeses) {
          detalles.push(`Exp. Específica: ${req.experienciaEspecifica.tiempoMeses} meses`);
        }

        // Certificaciones
        const certs = req.certificacionesRequeridas || req.certificaciones;
        if (certs && certs.length > 0) {
          detalles.push(`Certificaciones: ${certs.join(", ")}`);
        }

        const cargo = req.cargo || req.perfil || "Sin cargo";
        const descripcionCompleta = `${i + 1}. ${cargo}${req.cantidad > 1 ? ` (${req.cantidad})` : ""} - Título + Colegiatura + Habilitación${detalles.length > 0 ? " | " + detalles.join(" | ") : ""}`;

        items.push({
          id: `per-${id++}`,
          categoria: "personal",
          descripcion: descripcionCompleta,
          observacion: req.funcionesPrincipales?.length > 0 ? `Funciones: ${req.funcionesPrincipales.slice(0, 2).join("; ")}` : undefined,
          obligatorio: true,
          checked: false
        });
      });
    } else {
      // Perfiles por defecto según módulo
      const personalPorModulo: Record<string, string[]> = {
        supervision: [
          "Jefe de Supervisión",
          "Ingeniero de Control de Obra",
          "Especialista en Calidad y Laboratorio",
          "Especialista en Seguridad y Salud",
          "Especialista en Medio Ambiente",
          "Especialista en Estructuras",
          "Asistente Administrativo"
        ],
        obras: [
          "Residente de Obra",
          "Asistente de Residente",
          "Maestro de Obra",
          "Ingeniero de Seguridad y Salud en Obra",
          "Ingeniero Ambiental",
          "Topógrafo",
          "Especialista en Calidad"
        ],
        consultoria: [
          "Jefe de Proyecto",
          "Especialista en Arquitectura",
          "Especialista en Estructuras",
          "Especialista en Instalaciones Sanitarias",
          "Especialista en Instalaciones Eléctricas",
          "Especialista en Costos y Presupuestos",
          "Especialista en Seguridad y Medio Ambiente"
        ],
      };
      const personalDefault = personalPorModulo[modulo] || personalPorModulo.consultoria;
      personalDefault.forEach((perfil, i) => {
        items.push({ id: `per-${id++}`, categoria: "personal", descripcion: `${i + 1}. ${perfil} (Título + Colegiatura + Habilitación)`, obligatorio: true, checked: false });
      });
    }

    items.push({ id: `cal-${id++}`, categoria: "calificacion", descripcion: "Documentación de experiencia de cada profesional", obligatorio: true, checked: false });
    items.push({ id: `cal-${id++}`, categoria: "calificacion", descripcion: "Documentos de equipamiento estratégico", obligatorio: true, checked: false });

    // CAPÍTULO IV - FACTORES DE EVALUACIÍ“N
    const factoresEval = data.criteriosEvaluacion?.length > 0
      ? data.criteriosEvaluacion.map(c => ({ desc: c.factor, pts: c.puntajeMaximo }))
      : [
        { desc: "Experiencia Adicional del Personal Clave", pts: 80 },
        { desc: "Sostenibilidad Ambiental (ISO 14001)", pts: 10 },
        { desc: "Sostenibilidad Social", pts: 5 },
        { desc: "Integridad Antisoborno (ISO 37001)", pts: 5 },
      ];

    factoresEval.forEach(factor => {
      items.push({ id: `eval-${id++}`, categoria: "evaluacion", descripcion: factor.desc, puntaje: factor.pts, obligatorio: false, checked: false });
    });

    // Oferta económica
    items.push({ id: `eco-${id++}`, categoria: "economica", descripcion: "Oferta Económica preparada (verificar límite mínimo 90%)", anexo: "Anexo N° 6", obligatorio: true, checked: false });

    // DOCUMENTOS PARA CONTRATO - diferenciados por módulo
    const docsContratoBase = [
      { desc: "Garantía de fiel cumplimiento (10%)", anexo: "Anexo N° 7" },
      { desc: "Contrato de consorcio con firmas legalizadas (si aplica)" },
      { desc: "Código de Cuenta Interbancaria (CCI)" },
      { desc: "Vigencia de poder + DNI del representante" },
      { desc: "Autorización de notificaciones por email", anexo: "Anexo N° 8" },
      { desc: "Desglose de estructura de costos" },
      { desc: "Elección de Institución Arbitral", anexo: "Anexo N° 9" },
    ];

    // Items específicos por módulo
    const docsEspecificos: Record<string, { desc: string; anexo?: string }[]> = {
      supervision: [
        { desc: "Plan de Supervisión con metodología" },
        { desc: "Formato de reporte mensual de supervisión" },
        { desc: "Formato de cuaderno de supervisión" },
        { desc: "Plan de control de calidad y ensayos" },
      ],
      obras: [
        { desc: "Calendario de Avance de Obra (PERT-CPM)" },
        { desc: "Calendario Valorizado de Avance" },
        { desc: "Plan de Seguridad y Salud en el Trabajo" },
        { desc: "Plan de Manejo Ambiental" },
        { desc: "Relación de equipamiento mínimo" },
      ],
      consultoria: [
        { desc: "Plan de trabajo con memoria descriptiva" },
        { desc: "Cronograma de entregables" },
        { desc: "Metodología de estudio propuesta" },
      ],
    };

    const docsContrato = [...docsContratoBase, ...(docsEspecificos[modulo] || docsEspecificos.consultoria)];
    docsContrato.forEach(doc => {
      items.push({ id: `con-${id++}`, categoria: "contrato", descripcion: doc.desc, anexo: doc.anexo, obligatorio: false, checked: false });
    });

    return items;
  };

  // Exportar checklist a PDF (usando print)
  const exportarChecklistPDF = () => {
    const completados = checklistItems.filter(i => i.checked).length;
    const total = checklistItems.length;
    const pct = total > 0 ? Math.round((completados / total) * 100) : 0;

    const categorias = [
      { cat: "admision", titulo: "ðŸ“„ DOCUMENTOS DE ADMISIÍ“N (Cap. II)" },
      { cat: "calificacion", titulo: "ðŸ“‹ REQUISITOS DE CALIFICACIÍ“N (Cap. III)" },
      { cat: "personal", titulo: "ðŸ‘¥ PERSONAL CLAVE (Cap. III)" },
      { cat: "evaluacion", titulo: "⚖️ FACTORES DE EVALUACIÍ“N (Cap. IV)" },
      { cat: "economica", titulo: "ðŸ’° OFERTA ECONÍ“MICA" },
      { cat: "contrato", titulo: "ðŸ“ DOCUMENTOS PARA CONTRATO" },
    ];

    let html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Checklist - ${analisis?.nomenclaturaProceso || "Licitación"}</title>
    <style>body{font-family:Arial,sans-serif;padding:20px;max-width:800px;margin:0 auto}
    h1{color:#4f46e5;font-size:1.5rem;border-bottom:2px solid #4f46e5;padding-bottom:10px}
    .info{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px;background:#f8fafc;padding:15px;border-radius:8px}
    .info div{font-size:0.85rem}.info strong{color:#1e293b}
    .progreso{background:#e2e8f0;border-radius:10px;height:20px;margin-bottom:20px}
    .progreso-fill{background:linear-gradient(90deg,#8b5cf6,#c084fc);height:100%;border-radius:10px}
    .seccion{margin-bottom:15px}.seccion-titulo{background:#334155;color:white;padding:8px 15px;font-weight:bold;border-radius:6px 6px 0 0}
    .items{border:1px solid #e2e8f0;border-top:none;border-radius:0 0 6px 6px}
    .item{display:flex;align-items:center;padding:8px 15px;border-bottom:1px solid #e2e8f0}
    .item:last-child{border-bottom:none}
    .check{width:16px;height:16px;border:2px solid #64748b;border-radius:3px;margin-right:12px;display:flex;align-items:center;justify-content:center}
    .checked .check{background:#22c55e;border-color:#22c55e}.checked .check::after{content:"âœ“";color:white;font-size:10px}
    .checked .desc{color:#6b7280;text-decoration:line-through}
    .desc{flex:1;font-size:0.85rem}.anexo{font-size:0.7rem;background:#ede9fe;color:#7c3aed;padding:2px 6px;border-radius:4px;margin-left:8px}
    .pts{font-size:0.8rem;font-weight:bold;color:#d97706}
    @media print{body{padding:0}}</style></head><body>`;

    html += `<h1>ðŸ“‹ CHECKLIST DE BASES - ${analisis?.nomenclaturaProceso || "LICITACIÍ“N"}</h1>`;
    html += `<div class="info"><div><strong>Entidad:</strong> ${analisis?.entidadConvocante || "-"}</div>`;
    html += `<div><strong>Cuantía:</strong> ${analisis?.valorReferencial || "-"}</div>`;
    html += `<div><strong>Objeto:</strong> ${analisis?.objetoContratacion || "-"}</div>`;
    html += `<div><strong>Completado:</strong> ${completados}/${total} (${pct}%)</div></div>`;
    html += `<div class="progreso"><div class="progreso-fill" style="width:${pct}%"></div></div>`;

    categorias.forEach(seccion => {
      const itemsSec = checklistItems.filter(i => i.categoria === seccion.cat);
      if (itemsSec.length === 0) return;
      html += `<div class="seccion"><div class="seccion-titulo">${seccion.titulo}</div><div class="items">`;
      itemsSec.forEach(item => {
        html += `<div class="item${item.checked ? " checked" : ""}"><div class="check"></div>`;
        html += `<span class="desc">${item.descripcion}</span>`;
        if (item.anexo) html += `<span class="anexo">${item.anexo}</span>`;
        if (item.puntaje) html += `<span class="pts">${item.puntaje} pts</span>`;
        html += `</div>`;
      });
      html += `</div></div>`;
    });

    html += `<p style="text-align:center;color:#64748b;font-size:0.8rem;margin-top:20px">Generado por Mister Propuestas - ${new Date().toLocaleDateString("es-PE")}</p>`;
    html += `</body></html>`;

    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Checklist_${analisis?.nomenclaturaProceso?.replace(/[^a-zA-Z0-9]/g, "_") || "Licitacion"}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Cargar estadísticas RAG al inicio
  const cargarEstadisticasRAG = async () => {
    try {
      const res = await fetch("/api/feedback");
      const data = await res.json();
      if (data.success) {
        setEstadisticasRAG(data.estadisticas);
      }
    } catch (error) {
      console.error("Error cargando estadísticas RAG:", error);
    }
  };

  // Enviar feedback
  const enviarFeedback = async () => {
    if (!feedbackAnexo || feedbackAnexo.calificacion === 0) return;

    setFeedbackAnexo(prev => prev ? { ...prev, enviando: true } : null);

    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contenido: feedbackAnexo.contenido,
          tipo: `anexo_${feedbackAnexo.anexoNum}`,
          exitosa: feedbackAnexo.exitosa ?? feedbackAnexo.calificacion >= 3,
          calificacion: feedbackAnexo.calificacion,
          tipoLicitacion: analisis?.tipoModalidad,
          entidad: analisis?.entidadConvocante,
        }),
      });

      const data = await res.json();
      if (data.success) {
        setFeedbackAnexo(prev => prev ? { ...prev, enviando: false, enviado: true } : null);
        cargarEstadisticasRAG(); // Actualizar estadísticas
      }
    } catch (error) {
      console.error("Error enviando feedback:", error);
      setFeedbackAnexo(prev => prev ? { ...prev, enviando: false } : null);
    }
  };

  // Subir bases
  const handleUploadBases = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);

    try {
      const res = await fetch("/api/bases/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.success) {
        const analisisData: AnalisisData = {
          nomenclaturaProceso: data.nomenclaturaProceso || "PROCESO DE SELECCIÓN",
          tipoModalidad: data.tipoModalidad || "CONCURSO PÚBLICO",
          entidadConvocante: data.entidadConvocante || "No detectado",
          objetoContratacion: data.objetoContratacion || "No detectado",
          valorReferencial: data.valorReferencial || "No especificado",
          plazoEjecucion: data.plazoEjecucion || "No especificado",
          capitulos: data.capitulos || [],
          requisitos: data.requisitos || [],
          anexosDetectados: data.anexos || data.anexosDetectados || [],
          criteriosEvaluacion: data.criteriosEvaluacion || [],
          alertas: data.alertas || [],
          resumen: data.resumen || "",
        };
        setAnalisis(analisisData);
        // Generar checklist automáticamente desde el análisis
        setChecklistItems(generarChecklistDesdeAnalisis(analisisData, moduloActivo));
        // Si hay alertas críticas, ir directo a esa tab
        if (analisisData.alertas && analisisData.alertas.some(a => a.severidad === "CRITICO" || a.severidad === "ALTO")) {
          setTabActiva("alertas");
        } else {
          setTabActiva("capitulos");
        }
        setStep(2);
      } else {
        alert("Error: " + (data.error || "Error desconocido"));
      }
    } catch {
      alert("Error al procesar el archivo");
    } finally {
      setLoading(false);
    }
  };

  // Subir CVs y parsearlos
  const handleUploadCVs = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    formData.append("perfilesRequeridos", JSON.stringify(analisis?.requisitos?.map(r => r.perfil) || []));

    try {
      const res = await fetch("/api/cvs/parse", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.success) {
        setCvsParseados(data.cvsParseados || []);
        if (data.sugerenciaMapeo) {
          setMapeoPersonal(data.sugerenciaMapeo);
        }
        setStep(4);
      } else {
        alert("Error: " + (data.error || "Error procesando CVs"));
      }
    } catch {
      alert("Error al procesar CVs");
    } finally {
      setLoading(false);
    }
  };

  // Descargar anexo individual
  const handleDescargarAnexo = async (anexoNumero: string) => {
    setLoading(true);

    // Construir personal clave desde CVs parseados y mapeo
    const personalClave = analisis?.requisitos?.map(req => {
      const cargoId = req.cargo || req.perfil || '';
      const cvNombre = mapeoPersonal[cargoId];
      const cv = cvsParseados.find(c => c.nombre === cvNombre);

      return {
        puesto: cargoId,
        nombres: cv?.nombre || "[PENDIENTE]",
        dni: cv?.dni || "",
        universidad: cv?.universidad || "",
        titulo: cv?.titulo || "",
        experienciaAnios: 5,
        experienciaMeses: 0,
        experienciaDias: 0,
      };
    }) || [];

    try {
      const res = await fetch("/api/anexos/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          anexoNumero,
          datosGenerales: {
            entidadContratante: analisis?.entidadConvocante || "",
            nomenclaturaProceso: analisis?.nomenclaturaProceso || "PROCESO DE SELECCIÍ“N",
            objetoContratacion: analisis?.objetoContratacion || "",
            postor: {
              razonSocial: datosPostor.razonSocial,
              ruc: datosPostor.ruc,
              representanteLegal: datosPostor.representanteLegal,
              dni: datosPostor.dni,
              domicilio: datosPostor.domicilio,
              telefono: datosPostor.telefono,
              email: datosPostor.email,
            },
            ciudad: "Lima",
            fecha: new Date().toLocaleDateString("es-PE"),
          },
          datosEspecificos: {
            tipoPostor: datosPostor.tipoPostor,
            esMype: datosPostor.esMype,
            tipoDocumento: datosPostor.tipoDocumento,
            sedeRegistral: datosPostor.sedeRegistral,
            partidaRegistral: datosPostor.partidaRegistral,
            asiento: datosPostor.asiento,
            personalClave,
          },
        }),
      });

      const data = await res.json();

      if (data.success && data.blob) {
        const byteCharacters = atob(data.blob);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = data.fileName || `Anexo_${anexoNumero}.docx`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        alert("Error: " + data.error);
      }
    } catch {
      alert("Error descargando anexo");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            🎩 Mister de las Propuestas
          </h1>
          <span className="text-purple-300 text-sm">SaaS de Licitaciones SEACE</span>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Progress Steps */}
        <div className="flex justify-between mb-12">
          {[
            { num: 1, label: "Bases" },
            { num: 2, label: "Análisis" },
            { num: 3, label: "CVs" },
            { num: 4, label: "Datos" },
            { num: 5, label: "Validación" },
            { num: 6, label: "Anexos" },
          ].map((s) => (
            <div key={s.num} className="flex flex-col items-center">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold transition-all ${step >= s.num
                  ? "bg-purple-600 text-white"
                  : "bg-slate-700 text-slate-400"
                  }`}
              >
                {s.num}
              </div>
              <span className="mt-2 text-sm text-slate-400">{s.label}</span>
            </div>
          ))}
        </div>

        {/* Step 1: Module Selector + Upload Bases */}
        {step === 1 && !moduloActivo && (
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-3">¿Qué tipo de proceso deseas analizar?</h2>
            <p className="text-slate-400 mb-10 max-w-2xl mx-auto">Selecciona el módulo para un análisis especializado OSCE</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <div onClick={() => setModuloActivo("supervision")} className="module-card supervision">
                <div className="module-icon supervision float-animation">🔍</div>
                <h3 className="text-xl font-bold text-white mb-2">Supervisión</h3>
                <p className="text-slate-400 text-sm mb-4">Control de ejecución de obras</p>
                <div className="mt-4 pt-4 border-t border-blue-500/20"><span className="module-badge supervision">📋 Consultoría de Obra</span></div>
              </div>
              <div onClick={() => setModuloActivo("consultoria")} className="module-card consultoria">
                <div className="module-icon consultoria float-animation" style={{ animationDelay: '0.5s' }}>💼</div>
                <h3 className="text-xl font-bold text-white mb-2">Consultoría</h3>
                <p className="text-slate-400 text-sm mb-4">Estudios técnicos y TDR</p>
                <div className="mt-4 pt-4 border-t border-purple-500/20"><span className="module-badge consultoria">📐 Servicios Intelectuales</span></div>
              </div>
              <div onClick={() => setModuloActivo("obras")} className="module-card obras">
                <div className="module-icon obras float-animation" style={{ animationDelay: '1s' }}>🏗️</div>
                <h3 className="text-xl font-bold text-white mb-2">Obras</h3>
                <p className="text-slate-400 text-sm mb-4">Ejecución de obras públicas</p>
                <div className="mt-4 pt-4 border-t border-orange-500/20"><span className="module-badge obras">🚧 Ejecución de Obra</span></div>
              </div>
            </div>
          </div>
        )}
        {/* Step 1: Upload Form (after module selected) */}
        {step === 1 && moduloActivo && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${moduloActivo === 'supervision' ? 'bg-blue-600' : moduloActivo === 'consultoria' ? 'bg-purple-600' : 'bg-orange-600'}`}>
                  {moduloActivo === 'supervision' ? '🔍' : moduloActivo === 'consultoria' ? '💼' : '🏗️'}
                </div>
                <div>
                  <h3 className="text-white font-semibold">Módulo: {moduloActivo === 'supervision' ? 'Supervisión' : moduloActivo === 'consultoria' ? 'Consultoría' : 'Obras'}</h3>
                  <p className="text-slate-400 text-sm">Análisis especializado</p>
                </div>
              </div>
              <button onClick={() => setModuloActivo(null)} className="text-slate-400 hover:text-white text-sm transition-colors">← Cambiar módulo</button>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">
              ðŸ“„ Sube las Bases de Licitación
            </h2>
            <p className="text-slate-400 mb-6">
              Analizaremos las bases por capítulos: TDR, requisitos, anexos y criterios
            </p>

            <form onSubmit={handleUploadBases} className="space-y-6">
              <input type="hidden" name="modulo" value={moduloActivo || "consultoria"} />
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Nombre del Proyecto
                </label>
                <input
                  type="text"
                  name="projectName"
                  required
                  placeholder="Ej: Supervisión I.E. Huachis 2026"
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Archivo de Bases (PDF o DOCX)
                </label>
                <input
                  type="file"
                  name="file"
                  accept=".pdf,.docx"
                  required
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-purple-600 file:text-white"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
              >
                {loading ? "â³ Analizando..." : "ðŸ” Analizar Bases"}
              </button>
            </form>
          </div>
        )}

        {/* Step 2: Show Analysis */}
        {step === 2 && analisis && (
          <div className="space-y-6">
            {/* Info General */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">ðŸ“‹ Información General</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-slate-400 text-sm">Entidad:</span>
                  <p className="text-white font-medium">{analisis.entidadConvocante}</p>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">Valor Referencial:</span>
                  <p className="text-green-400 font-medium">{analisis.valorReferencial}</p>
                </div>
                <div className="col-span-2">
                  <span className="text-slate-400 text-sm">Objeto:</span>
                  <p className="text-white">{analisis.objetoContratacion}</p>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {[
                { id: "capitulos", label: "🔑 Capítulos", count: analisis.capitulos?.length || 0 },
                { id: "requisitos", label: "👤 Requisitos", count: analisis.requisitos?.length || 0 },
                { id: "anexos", label: "📎 Anexos", count: analisis.anexosDetectados?.length || 0 },
                { id: "evaluacion", label: "⚖️ Evaluación", count: analisis.criteriosEvaluacion?.length || 0 },
                { id: "alertas", label: "🚨 Alertas", count: analisis.alertas?.length || 0 },
                { id: "checklist", label: "📋 Checklist", count: checklistItems.length },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setTabActiva(tab.id as typeof tabActiva)}
                  className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${tabActiva === tab.id
                    ? tab.id === "alertas" && tab.count > 0
                      ? "bg-red-600 text-white ring-2 ring-red-400/50"
                      : "bg-purple-600 text-white"
                    : tab.id === "alertas" && tab.count > 0
                      ? "bg-red-900/50 text-red-300 hover:bg-red-800/70 ring-1 ring-red-500/30"
                      : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                    }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-white/10 min-h-[300px]">
              {tabActiva === "capitulos" && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white">📋 Requisitos por Capítulo (Numeral por Numeral)</h3>
                  {analisis.capitulos?.map((cap, i) => (
                    <div key={i} className="bg-slate-700/50 rounded-lg overflow-hidden">
                      {/* Header del Capítulo */}
                      <div className="bg-purple-900/50 px-4 py-3 border-b border-purple-500/30">
                        <h4 className="text-purple-200 font-bold">Capítulo {cap.numero}: {cap.titulo}</h4>
                        <p className="text-slate-400 text-xs mt-1">{cap.resumen}</p>
                      </div>

                      {/* Numerales detallados */}
                      {cap.numerales && cap.numerales.length > 0 ? (
                        <div className="divide-y divide-slate-600/50">
                          {cap.numerales.map((num, j) => (
                            <div key={j} className="px-4 py-3 hover:bg-slate-600/30 transition-colors">
                              <div className="flex items-start gap-3">
                                <span className={`px-2 py-0.5 rounded text-xs font-mono ${num.obligatorio ? 'bg-red-900/50 text-red-300' : 'bg-slate-600 text-slate-400'}`}>
                                  {num.numeral}
                                </span>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <span className="text-white font-medium text-sm">{num.titulo}</span>
                                    {num.obligatorio && <span className="text-red-400 text-xs">⚠️ Obligatorio</span>}
                                  </div>
                                  <p className="text-slate-300 text-sm mt-1">{num.requisito}</p>
                                  {num.documento && (
                                    <span className="inline-block mt-1 px-2 py-0.5 bg-purple-900/40 text-purple-300 text-xs rounded">
                                      📎 {num.documento}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="px-4 py-3">
                          {cap.puntosClaves?.map((punto, k) => (
                            <p key={k} className="text-slate-300 text-sm py-1">• {punto}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {tabActiva === "requisitos" && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white">👷 Requisitos de Personal Clave</h3>

                  {/* Info de Especialidad del Proceso */}
                  {analisis.especialidadProceso && (
                    <div className="bg-purple-900/30 rounded-lg p-4 border border-purple-500/30 mb-4">
                      <h4 className="text-purple-300 font-semibold mb-2">📋 Especialidad del Proceso</h4>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div><span className="text-slate-400">Especialidad:</span> <span className="text-white">{analisis.especialidadProceso}</span></div>
                        <div><span className="text-slate-400">Subespecialidad:</span> <span className="text-white">{analisis.subespecialidadProceso || "-"}</span></div>
                        <div><span className="text-slate-400">Tipologías:</span> <span className="text-white">{analisis.tipologiasProceso?.join(", ") || "-"}</span></div>
                      </div>
                    </div>
                  )}

                  {analisis.requisitos?.map((req, i) => (
                    <div key={i} className="bg-slate-700/50 rounded-lg overflow-hidden">
                      {/* Header del Perfil */}
                      <div className="bg-gradient-to-r from-purple-800/50 to-pink-800/50 px-4 py-3 flex justify-between items-center">
                        <div>
                          <h4 className="text-white font-bold">{req.cargo || req.perfil}</h4>
                          <span className="text-purple-300 text-sm">Cantidad: {req.cantidad}</span>
                        </div>
                      </div>

                      <div className="p-4 space-y-3">
                        {/* Profesiones Aceptadas */}
                        {req.profesionesAceptadas && req.profesionesAceptadas.length > 0 && (
                          <div>
                            <span className="text-slate-400 text-xs font-semibold">PROFESIONES ACEPTADAS:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {req.profesionesAceptadas.map((prof, j) => (
                                <span key={j} className="px-2 py-0.5 bg-blue-900/40 text-blue-300 text-xs rounded">{prof}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Cargos Desempeñados */}
                        {req.cargosDesempenados && req.cargosDesempenados.length > 0 && (
                          <div>
                            <span className="text-slate-400 text-xs font-semibold">CARGOS VÁLIDOS PARA EXPERIENCIA:</span>
                            <p className="text-slate-300 text-sm mt-1">{req.cargosDesempenados.join(" / ")}</p>
                          </div>
                        )}

                        {/* Experiencia General */}
                        {req.experienciaGeneral && (
                          <div className="bg-slate-600/30 rounded p-3">
                            <span className="text-green-400 text-xs font-semibold">📊 EXPERIENCIA GENERAL</span>
                            <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                              <div><span className="text-slate-400">Tiempo:</span> <span className="text-white font-bold">{req.experienciaGeneral.tiempoMeses} meses</span></div>
                              <div><span className="text-slate-400">Detalle:</span> <span className="text-slate-300">{req.experienciaGeneral.tiempoTexto}</span></div>
                              <div><span className="text-slate-400">Especialidad:</span> <span className="text-slate-300">{req.experienciaGeneral.especialidad}</span></div>
                              {req.experienciaGeneral.participacionRequerida && (
                                <div><span className="text-slate-400">Participación:</span> <span className="text-yellow-300">{req.experienciaGeneral.participacionRequerida}</span></div>
                              )}
                            </div>
                            {req.experienciaGeneral.tipologias && req.experienciaGeneral.tipologias.length > 0 && (
                              <div className="mt-2">
                                <span className="text-slate-400 text-xs">Tipologías:</span>
                                <p className="text-slate-300 text-xs">{req.experienciaGeneral.tipologias.join(", ")}</p>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Experiencia Específica */}
                        {req.experienciaEspecifica && typeof req.experienciaEspecifica === "object" && (
                          <div className="bg-slate-600/30 rounded p-3">
                            <span className="text-yellow-400 text-xs font-semibold">🎯 EXPERIENCIA ESPECÍFICA</span>
                            <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                              <div><span className="text-slate-400">Tiempo:</span> <span className="text-white font-bold">{req.experienciaEspecifica.tiempoMeses} meses</span></div>
                              <div><span className="text-slate-400">Detalle:</span> <span className="text-slate-300">{req.experienciaEspecifica.tiempoTexto}</span></div>
                            </div>
                            {req.experienciaEspecifica.tipologias && req.experienciaEspecifica.tipologias.length > 0 && (
                              <div className="mt-2">
                                <span className="text-slate-400 text-xs">Tipologías requeridas:</span>
                                <p className="text-slate-300 text-xs">{req.experienciaEspecifica.tipologias.join(", ")}</p>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Certificaciones */}
                        {(req.certificacionesRequeridas?.length > 0 || req.certificaciones?.length) && (
                          <div>
                            <span className="text-slate-400 text-xs font-semibold">📜 CERTIFICACIONES:</span>
                            <p className="text-slate-300 text-sm mt-1">{(req.certificacionesRequeridas || req.certificaciones || []).join(", ")}</p>
                          </div>
                        )}

                        {/* Compatibilidad con formato antiguo */}
                        {!req.experienciaGeneral && req.experienciaMinima && (
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div><span className="text-slate-400">Exp. General:</span> <span className="text-slate-300">{req.experienciaMinima}</span></div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {tabActiva === "anexos" && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white">Anexos Detectados</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {analisis.anexosDetectados?.map((anexo, i) => (
                      <div key={i} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                        <span className="text-white font-medium">{anexo.numero ? `Anexo ${anexo.numero}` : anexo.nombre}</span>
                        <p className="text-slate-400 text-sm">{anexo.tipo}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {tabActiva === "evaluacion" && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white">Criterios de Evaluación</h3>
                  {analisis.criteriosEvaluacion?.map((c, i) => (
                    <div key={i} className="bg-slate-700/50 rounded-lg p-4 flex justify-between">
                      <div>
                        <h4 className="text-white font-medium">{c.factor}</h4>
                        <p className="text-slate-400 text-sm">{c.descripcion}</p>
                      </div>
                      <span className="text-2xl font-bold text-purple-400">{c.puntajeMaximo}</span>
                    </div>
                  ))}
                </div>
              )}

              {tabActiva === "alertas" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white">🚨 Análisis Forense de Trampas</h3>
                    {analisis.alertas && analisis.alertas.length > 0 && (
                      <div className="flex gap-2">
                        {["CRITICO", "ALTO", "MEDIO"].map(sev => {
                          const count = analisis.alertas!.filter(a => a.severidad === sev).length;
                          if (count === 0) return null;
                          const colors = { CRITICO: "bg-red-600", ALTO: "bg-orange-600", MEDIO: "bg-yellow-600" };
                          return (
                            <span key={sev} className={`${colors[sev as keyof typeof colors]} text-white text-xs px-2 py-1 rounded-full font-bold`}>
                              {count} {sev}
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {(!analisis.alertas || analisis.alertas.length === 0) ? (
                    <div className="text-center py-8">
                      <p className="text-green-400 text-xl">✅ No se detectaron trampas ni requisitos ocultos</p>
                      <p className="text-slate-400 text-sm mt-2">Las bases parecen estar redactadas correctamente</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {analisis.alertas
                        .sort((a, b) => {
                          const orden = { CRITICO: 0, ALTO: 1, MEDIO: 2 };
                          return orden[a.severidad] - orden[b.severidad];
                        })
                        .map((alerta, i) => {
                          const colores = {
                            CRITICO: { border: "border-red-500/50", bg: "bg-red-950/50", badge: "bg-red-600", icon: "🛑" },
                            ALTO: { border: "border-orange-500/50", bg: "bg-orange-950/40", badge: "bg-orange-600", icon: "⚠️" },
                            MEDIO: { border: "border-yellow-500/50", bg: "bg-yellow-950/30", badge: "bg-yellow-600", icon: "🟡" },
                          };
                          const c = colores[alerta.severidad];
                          const tipoLabels: Record<string, string> = {
                            requisito_oculto: "Requisito Oculto",
                            contradiccion: "Contradicción",
                            plazo_critico: "Plazo Crítico",
                            experiencia_restrictiva: "Experiencia Restrictiva",
                            certificacion_especifica: "Certificación Específica",
                            formato_documento: "Formato de Documento",
                            penalidad_abusiva: "Penalidad Abusiva",
                            garantia_adicional: "Garantía Adicional",
                            rnp_especifico: "RNP Específico",
                            consorcio_restringido: "Consorcio Restringido",
                            direccionamiento: "Direccionamiento",
                            subsanacion_corta: "Subsanación Corta",
                          };
                          return (
                            <div key={i} className={`${c.bg} ${c.border} border rounded-xl p-4 space-y-3`}>
                              {/* Header */}
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <span className="text-lg">{c.icon}</span>
                                  <span className={`${c.badge} text-white text-xs px-2 py-0.5 rounded-full font-bold`}>
                                    {alerta.severidad}
                                  </span>
                                  <span className="text-white font-medium">
                                    {tipoLabels[alerta.tipo] || alerta.tipo}
                                  </span>
                                </div>
                                <span className="text-slate-400 text-xs">{alerta.seccion}</span>
                              </div>

                              {/* Descripción */}
                              <p className="text-slate-200 text-sm">{alerta.descripcion}</p>

                              {/* Requisito exacto */}
                              {alerta.requisito_exacto && (
                                <div className="bg-black/30 rounded-lg p-3 border-l-4 border-slate-500">
                                  <p className="text-xs text-slate-500 mb-1">TEXTO EXACTO DE LAS BASES:</p>
                                  <p className="text-slate-300 text-sm italic">"{alerta.requisito_exacto}"</p>
                                </div>
                              )}

                              {/* Recomendación */}
                              <div className="bg-emerald-950/30 rounded-lg p-3 border-l-4 border-emerald-500">
                                <p className="text-xs text-emerald-500 mb-1">💡 RECOMENDACIÓN:</p>
                                <p className="text-emerald-200 text-sm">{alerta.recomendacion}</p>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  )}
                </div>
              )}

              {tabActiva === "checklist" && (
                <div className="space-y-4">
                  {/* Barra de Progreso */}
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white">ðŸ“‹ Checklist de Requisitos</h3>
                    <div className="flex items-center gap-4">
                      <span className="text-slate-300 text-sm">
                        {checklistItems.filter(i => i.checked).length}/{checklistItems.length} completados
                      </span>
                      <button
                        onClick={exportarChecklistPDF}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                      >
                        ðŸ“¥ Descargar PDF
                      </button>
                    </div>
                  </div>

                  {/* Barra de progreso visual */}
                  <div className="w-full bg-slate-700 rounded-full h-3 mb-6">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${checklistItems.length > 0 ? Math.round((checklistItems.filter(i => i.checked).length / checklistItems.length) * 100) : 0}%` }}
                    ></div>
                  </div>

                  {/* Secciones del Checklist */}
                  {[
                    { cat: "admision", titulo: "ðŸ“„ Documentos de Admisión", color: "bg-blue-600" },
                    { cat: "calificacion", titulo: "ðŸ“‹ Requisitos de Calificación", color: "bg-teal-600" },
                    { cat: "personal", titulo: "ðŸ‘¥ Personal Clave", color: "bg-purple-600" },
                    { cat: "evaluacion", titulo: "⚖️ Factores de Evaluación (Opcionales)", color: "bg-amber-600" },
                    { cat: "economica", titulo: "ðŸ’° Oferta Económica", color: "bg-green-600" },
                    { cat: "contrato", titulo: "ðŸ“ Documentos para Contrato", color: "bg-slate-600" },
                  ].map(section => {
                    const itemsSeccion = checklistItems.filter(i => i.categoria === section.cat);
                    if (itemsSeccion.length === 0) return null;
                    const completados = itemsSeccion.filter(i => i.checked).length;

                    return (
                      <div key={section.cat} className="mb-4">
                        <div className={`${section.color} text-white px-4 py-2 rounded-t-lg flex justify-between items-center`}>
                          <span className="font-semibold">{section.titulo}</span>
                          <span className="text-sm opacity-80">{completados}/{itemsSeccion.length}</span>
                        </div>
                        <div className="bg-slate-700/50 rounded-b-lg divide-y divide-slate-600">
                          {itemsSeccion.map(item => (
                            <div
                              key={item.id}
                              className="flex items-center gap-3 p-3 hover:bg-slate-600/50 cursor-pointer"
                              onClick={() => {
                                setChecklistItems(prev =>
                                  prev.map(i => i.id === item.id ? { ...i, checked: !i.checked } : i)
                                );
                              }}
                            >
                              <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${item.checked
                                ? "bg-green-500 border-green-500 text-white"
                                : "border-slate-400"
                                }`}>
                                {item.checked && <span className="text-xs">âœ“</span>}
                              </div>
                              <div className="flex-1">
                                <span className={`text-sm ${item.checked ? "text-slate-400 line-through" : "text-white"}`}>
                                  {item.descripcion}
                                </span>
                                {item.observacion && (
                                  <p className="text-xs text-slate-500 mt-1">{item.observacion}</p>
                                )}
                              </div>
                              {item.anexo && (
                                <span className="text-xs text-purple-400 bg-purple-900/30 px-2 py-1 rounded">
                                  {item.anexo}
                                </span>
                              )}
                              {item.puntaje && (
                                <span className="text-xs text-amber-400 font-bold">
                                  {item.puntaje} pts
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <button onClick={() => setStep(3)} className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-pink-700">
              âž¡ï¸ Continuar - Subir CVs
            </button>
          </div>
        )}

        {/* Step 3: Upload CVs */}
        {step === 3 && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <h2 className="text-2xl font-bold text-white mb-2">ðŸ‘¥ Sube los CVs</h2>
            <p className="text-slate-400 mb-4">Perfiles requeridos:</p>

            <div className="mb-6 flex flex-wrap gap-2">
              {analisis?.requisitos?.map((req, i) => (
                <span key={i} className="px-3 py-1 bg-purple-600/30 text-purple-200 rounded-full text-sm">{req.perfil}</span>
              ))}
            </div>

            <form onSubmit={handleUploadCVs} className="space-y-6">
              <input
                type="file"
                name="files"
                accept=".pdf,.docx"
                multiple
                required
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-purple-600 file:text-white"
              />

              <button type="submit" disabled={loading} className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg disabled:opacity-50">
                {loading ? "â³ Analizando CVs con IA..." : "ðŸ“¤ Procesar CVs"}
              </button>
            </form>
          </div>
        )}

        {/* Step 4: Datos del Postor */}
        {step === 4 && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <h2 className="text-2xl font-bold text-white mb-2">ðŸ“ Datos del Postor</h2>
            <p className="text-slate-400 mb-6">Estos datos se usarán para generar todos los anexos exactamente como piden las bases</p>

            {cvsParseados.length > 0 && (
              <div className="mb-6 p-4 bg-green-900/30 rounded-lg border border-green-600/50">
                <p className="text-green-300 font-medium">âœ… {cvsParseados.length} CVs procesados correctamente</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {cvsParseados.map((cv, i) => (
                    <span key={i} className="px-2 py-1 bg-green-800/50 text-green-200 text-sm rounded">{cv.nombre}</span>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={(e) => { e.preventDefault(); setStep(5); }} className="space-y-6">
              {/* Tipo de Postor */}
              <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <label className="block text-sm font-medium text-slate-300 mb-3">Tipo de Postor</label>
                <div className="flex gap-4">
                  {[
                    { value: "PERSONA_JURIDICA", label: "ðŸ¢ Persona Jurídica" },
                    { value: "PERSONA_NATURAL", label: "ðŸ‘¤ Persona Natural" },
                    { value: "CONSORCIO", label: "ðŸ¤ Consorcio" },
                  ].map((tipo) => (
                    <label key={tipo.value} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="tipoPostor"
                        value={tipo.value}
                        checked={datosPostor.tipoPostor === tipo.value}
                        onChange={(e) => setDatosPostor({ ...datosPostor, tipoPostor: e.target.value as DatosPostor["tipoPostor"] })}
                        className="text-purple-600"
                      />
                      <span className="text-white">{tipo.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Datos de la Empresa */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white border-b border-slate-600 pb-2">ðŸ¢ Datos de la Empresa</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Razón Social *</label>
                    <input
                      type="text"
                      value={datosPostor.razonSocial}
                      onChange={(e) => setDatosPostor({ ...datosPostor, razonSocial: e.target.value })}
                      placeholder="EMPRESA CONSULTORA S.A.C."
                      required
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">RUC * (11 dígitos)</label>
                    <input
                      type="text"
                      value={datosPostor.ruc}
                      onChange={(e) => setDatosPostor({ ...datosPostor, ruc: e.target.value.replace(/\D/g, "").slice(0, 11) })}
                      placeholder="20123456789"
                      pattern="[0-9]{11}"
                      required
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm text-slate-300 mb-1">Domicilio Legal *</label>
                    <input
                      type="text"
                      value={datosPostor.domicilio}
                      onChange={(e) => setDatosPostor({ ...datosPostor, domicilio: e.target.value })}
                      placeholder="Av. Principal 123, Distrito, Provincia, Departamento"
                      required
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Teléfono(s)</label>
                    <input
                      type="text"
                      value={datosPostor.telefono}
                      onChange={(e) => setDatosPostor({ ...datosPostor, telefono: e.target.value })}
                      placeholder="01-1234567 / 999888777"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Correo Electrónico *</label>
                    <input
                      type="email"
                      value={datosPostor.email}
                      onChange={(e) => setDatosPostor({ ...datosPostor, email: e.target.value })}
                      placeholder="contacto@empresa.com"
                      required
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="flex items-center gap-3 cursor-pointer p-3 bg-slate-700/50 rounded-lg border border-slate-600 hover:border-purple-500 transition-colors">
                      <input
                        type="checkbox"
                        checked={datosPostor.esMype}
                        onChange={(e) => setDatosPostor({ ...datosPostor, esMype: e.target.checked })}
                        className="w-5 h-5 text-purple-600 rounded"
                      />
                      <div>
                        <span className="text-white font-medium">Â¿Es MYPE?</span>
                        <p className="text-slate-400 text-xs">Se verifica en REMYPE del Ministerio de Trabajo</p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              {/* Datos del Representante Legal */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white border-b border-slate-600 pb-2">ðŸ‘¤ Representante Legal</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm text-slate-300 mb-1">Nombres y Apellidos *</label>
                    <input
                      type="text"
                      value={datosPostor.representanteLegal}
                      onChange={(e) => setDatosPostor({ ...datosPostor, representanteLegal: e.target.value })}
                      placeholder="Juan Carlos Pérez López"
                      required
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Tipo de Documento</label>
                    <select
                      value={datosPostor.tipoDocumento}
                      onChange={(e) => setDatosPostor({ ...datosPostor, tipoDocumento: e.target.value as "DNI" | "CE" | "PASAPORTE" })}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    >
                      <option value="DNI">DNI</option>
                      <option value="CE">Carné de Extranjería</option>
                      <option value="PASAPORTE">Pasaporte</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Número de Documento *</label>
                    <input
                      type="text"
                      value={datosPostor.dni}
                      onChange={(e) => setDatosPostor({ ...datosPostor, dni: e.target.value.replace(/\D/g, "").slice(0, 12) })}
                      placeholder="12345678"
                      required
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>

              {/* Datos Registrales (solo persona jurídica) */}
              {datosPostor.tipoPostor === "PERSONA_JURIDICA" && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white border-b border-slate-600 pb-2">ðŸ“‹ Datos Registrales (SUNARP)</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Sede Registral *</label>
                      <input
                        type="text"
                        value={datosPostor.sedeRegistral}
                        onChange={(e) => setDatosPostor({ ...datosPostor, sedeRegistral: e.target.value })}
                        placeholder="Lima"
                        required={datosPostor.tipoPostor === "PERSONA_JURIDICA"}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Partida Registral *</label>
                      <input
                        type="text"
                        value={datosPostor.partidaRegistral}
                        onChange={(e) => setDatosPostor({ ...datosPostor, partidaRegistral: e.target.value })}
                        placeholder="12345678"
                        required={datosPostor.tipoPostor === "PERSONA_JURIDICA"}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Asiento NÂº *</label>
                      <input
                        type="text"
                        value={datosPostor.asiento}
                        onChange={(e) => setDatosPostor({ ...datosPostor, asiento: e.target.value })}
                        placeholder="A00001"
                        required={datosPostor.tipoPostor === "PERSONA_JURIDICA"}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                      />
                    </div>
                  </div>
                  <p className="text-slate-500 text-xs">Estos datos se encuentran en la vigencia de poder del representante legal</p>
                </div>
              )}

              <button type="submit" className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-pink-700">
                âž¡ï¸ Validar Cumplimiento
              </button>
            </form>
          </div>
        )}

        {/* Step 5: Validación de Cumplimiento */}
        {step === 5 && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <h2 className="text-2xl font-bold text-white mb-2">âœ… Validación de Cumplimiento</h2>
            <p className="text-slate-400 mb-6">Verifica que cada profesional cumpla con los requisitos de las bases</p>

            {/* Cuadro de Validación */}
            <div className="overflow-x-auto mb-8">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-600">
                    <th className="text-left py-3 px-2 text-slate-300">Perfil Requerido</th>
                    <th className="text-left py-3 px-2 text-slate-300">Profesional</th>
                    <th className="text-center py-3 px-2 text-slate-300">Título</th>
                    <th className="text-center py-3 px-2 text-slate-300">Colegiatura</th>
                    <th className="text-center py-3 px-2 text-slate-300">Habilidad</th>
                    <th className="text-center py-3 px-2 text-slate-300">Exp. General</th>
                    <th className="text-center py-3 px-2 text-slate-300">Exp. Específica</th>
                    <th className="text-center py-3 px-2 text-slate-300">Certificaciones</th>
                    <th className="text-center py-3 px-2 text-slate-300">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {analisis?.requisitos?.map((req, i) => {
                    const cargoId = req.cargo || req.perfil || '';
                    const cvNombre = mapeoPersonal[cargoId];
                    const cv = cvsParseados.find(c => c.nombre === cvNombre);
                    const v = validacionPersonal.find(vp => vp.perfil === cargoId);

                    // Calcular estado simple si no hay validación completa
                    const tieneCV = !!cv;
                    const tieneTitulo = cv?.titulo ? true : false;
                    const tieneColegiatura = !!cv?.colegiatura;
                    const tieneHabilidad = cv?.habilitacionVigente ?? false;
                    const tieneExp = (cv?.experiencias?.length ?? 0) > 0;

                    const estado = v?.estado ?? (
                      !tieneCV ? "NO_CUMPLE" :
                        (!tieneTitulo || !tieneExp) ? "NO_CUMPLE" :
                          (!tieneColegiatura || !tieneHabilidad) ? "REVISAR" : "CUMPLE"
                    );

                    const estadoColor = {
                      "CUMPLE": "bg-green-900/50 text-green-300",
                      "REVISAR": "bg-yellow-900/50 text-yellow-300",
                      "NO_CUMPLE": "bg-red-900/50 text-red-300"
                    }[estado];

                    const estadoLabel = {
                      "CUMPLE": "âœ… Cumple",
                      "REVISAR": "âš ï¸ Revisar",
                      "NO_CUMPLE": "âŒ No Cumple"
                    }[estado];

                    return (
                      <tr key={i} className="border-b border-slate-700 hover:bg-slate-700/30">
                        <td className="py-3 px-2 text-white font-medium">{cargoId}</td>
                        <td className="py-3 px-2">
                          <select
                            value={cvNombre || ""}
                            onChange={(e) => setMapeoPersonal({ ...mapeoPersonal, [cargoId]: e.target.value })}
                            className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-white text-sm w-full"
                          >
                            <option value="">-- Seleccionar --</option>
                            {cvsParseados.map((cv, j) => (
                              <option key={j} value={cv.nombre}>{cv.nombre}</option>
                            ))}
                          </select>
                        </td>
                        <td className="py-3 px-2 text-center">
                          {tieneCV ? (
                            tieneTitulo ?
                              <span title={cv?.titulo} className="text-green-400">âœ…</span> :
                              <span className="text-red-400">âŒ</span>
                          ) : <span className="text-slate-500">-</span>}
                        </td>
                        <td className="py-3 px-2 text-center">
                          {tieneCV ? (
                            tieneColegiatura ?
                              <span title={cv?.colegiatura} className="text-green-400">âœ…</span> :
                              <span className="text-yellow-400">âš ï¸</span>
                          ) : <span className="text-slate-500">-</span>}
                        </td>
                        <td className="py-3 px-2 text-center">
                          {tieneCV ? (
                            tieneHabilidad ?
                              <span className="text-green-400">âœ…</span> :
                              <span className="text-yellow-400">âš ï¸</span>
                          ) : <span className="text-slate-500">-</span>}
                        </td>
                        <td className="py-3 px-2 text-center text-xs">
                          {tieneCV && cv?.experiencias?.length ? (
                            <span className={tieneExp ? "text-green-400" : "text-red-400"}>
                              {cv.experiencias.length} registros
                            </span>
                          ) : <span className="text-slate-500">-</span>}
                        </td>
                        <td className="py-3 px-2 text-center text-xs">
                          {v?.experienciaEspecifica ? (
                            <span className={v.experienciaEspecifica.cumple ? "text-green-400" : "text-red-400"}>
                              {Math.floor(v.experienciaEspecifica.mesesTiene / 12)}a {v.experienciaEspecifica.mesesTiene % 12}m
                            </span>
                          ) : tieneCV ? <span className="text-yellow-400">âš ï¸ Calc.</span> : <span className="text-slate-500">-</span>}
                        </td>
                        <td className="py-3 px-2 text-center">
                          {tieneCV && cv ? (
                            (cv.certificaciones?.length ?? 0) + (cv.maestrias?.length ?? 0) > 0 ?
                              <span className="text-green-400" title={[...(cv.certificaciones || []), ...(cv.maestrias || [])].join(", ")}>
                                âœ… {(cv.certificaciones?.length ?? 0) + (cv.maestrias?.length ?? 0)}
                              </span> :
                              <span className="text-yellow-400">âš ï¸ 0</span>
                          ) : <span className="text-slate-500">-</span>}
                        </td>
                        <td className="py-3 px-2 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${estadoColor}`}>
                            {estadoLabel}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Resumen */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-green-900/30 rounded-lg p-4 text-center border border-green-600/30">
                <div className="text-3xl font-bold text-green-400">
                  {validacionPersonal.filter(v => v.estado === "CUMPLE").length ||
                    analisis?.requisitos?.filter(r => {
                      const cargoId = r.cargo || r.perfil || '';
                      const cv = cvsParseados.find(c => c.nombre === mapeoPersonal[cargoId]);
                      return cv?.titulo && cv?.colegiatura && (cv?.experiencias?.length ?? 0) > 0;
                    }).length || 0}
                </div>
                <div className="text-green-300 text-sm">Cumplen</div>
              </div>
              <div className="bg-yellow-900/30 rounded-lg p-4 text-center border border-yellow-600/30">
                <div className="text-3xl font-bold text-yellow-400">
                  {validacionPersonal.filter(v => v.estado === "REVISAR").length || 0}
                </div>
                <div className="text-yellow-300 text-sm">Revisar</div>
              </div>
              <div className="bg-red-900/30 rounded-lg p-4 text-center border border-red-600/30">
                <div className="text-3xl font-bold text-red-400">
                  {validacionPersonal.filter(v => v.estado === "NO_CUMPLE").length ||
                    analisis?.requisitos?.filter(r => !mapeoPersonal[r.cargo || r.perfil || '']).length || 0}
                </div>
                <div className="text-red-300 text-sm">No Cumplen</div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(4)}
                className="flex-1 py-4 bg-slate-600 text-white font-bold rounded-lg hover:bg-slate-500"
              >
                â¬…ï¸ Volver a Datos
              </button>
              <button
                onClick={() => setStep(6)}
                className="flex-1 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-pink-700"
              >
                âž¡ï¸ Generar Anexos
              </button>
            </div>
          </div>
        )}

        {/* Step 6: Download Annexes */}
        {step === 6 && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">ðŸŽ‰</div>
              <h2 className="text-2xl font-bold text-white">Â¡Anexos Listos para Descargar!</h2>
              <p className="text-slate-400">Haz clic en cada anexo para descargarlo en formato Word</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
              {[
                { num: "01", nombre: "Datos del Postor" },
                { num: "02", nombre: "Pacto de Integridad" },
                { num: "03", nombre: "Declaración Jurada" },
                { num: "04", nombre: "Promesa Consorcio" },
                { num: "05", nombre: "Carta Compromiso" },
                { num: "06", nombre: "Precio Oferta" },
                { num: "07", nombre: "Autorización Retención" },
                { num: "08", nombre: "Autorización Notif." },
                { num: "09", nombre: "Inst. Arbitral" },
                { num: "10", nombre: "Experiencia Postor" },
                { num: "11", nombre: "DJ General" },
                { num: "12", nombre: "DJ Cumplimiento" },
                { num: "13", nombre: "Bonificación 10%" },
                { num: "14", nombre: "Plazo Ejecución" },
                { num: "15", nombre: "Personal Clave" },
                { num: "16", nombre: "DJ REDAM" },
                { num: "17", nombre: "Bonificación 5%" },
              ].map((anexo) => (
                <button
                  key={anexo.num}
                  onClick={() => handleDescargarAnexo(anexo.num)}
                  disabled={loading}
                  className="bg-slate-700/50 rounded-lg p-3 border border-slate-600 hover:border-purple-500 hover:bg-slate-700 transition-all text-left disabled:opacity-50"
                >
                  <div className="flex justify-between items-start">
                    <span className="text-white font-medium text-sm">Anexo {anexo.num}</span>
                    <span className="text-green-400 text-xs">âœ…</span>
                  </div>
                  <p className="text-slate-400 text-xs mt-1">{anexo.nombre}</p>
                </button>
              ))}
            </div>

            <button
              onClick={() => {
                const todosAnexos = ["01", "02", "03", "07", "08", "09", "10", "11", "12", "15", "16"];
                todosAnexos.forEach((num, i) => {
                  setTimeout(() => handleDescargarAnexo(num), i * 500);
                });
              }}
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50"
            >
              ðŸ“¥ Descargar Todos los Anexos
            </button>

            {/* Panel de Feedback RAG */}
            <div className="mt-8 p-6 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500/30">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                ðŸ§  Ayuda al Agente a Aprender
              </h3>

              {!feedbackAnexo ? (
                <div>
                  <p className="text-slate-300 text-sm mb-4">
                    Después de usar los anexos en tu licitación, cuéntanos cómo te fue para mejorar las próximas propuestas.
                  </p>
                  <button
                    onClick={() => {
                      setFeedbackAnexo({
                        anexoNum: "general",
                        contenido: `Propuesta para: ${analisis?.objetoContratacion || "N/A"}. Entidad: ${analisis?.entidadConvocante || "N/A"}`,
                        calificacion: 0,
                        exitosa: null,
                        enviando: false,
                        enviado: false,
                      });
                    }}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                  >
                    â­ Calificar esta Propuesta
                  </button>
                </div>
              ) : feedbackAnexo.enviado ? (
                <div className="text-center py-4">
                  <div className="text-4xl mb-2">âœ…</div>
                  <p className="text-green-400 font-medium">Â¡Gracias! El agente aprenderá de esta experiencia.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Estrellas */}
                  <div>
                    <label className="block text-sm text-slate-300 mb-2">Â¿Qué tan buena fue la propuesta generada?</label>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => setFeedbackAnexo(prev => prev ? { ...prev, calificacion: star } : null)}
                          className={`text-3xl transition-transform hover:scale-110 ${feedbackAnexo.calificacion >= star ? "opacity-100" : "opacity-30"
                            }`}
                        >
                          â­
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Resultado */}
                  <div>
                    <label className="block text-sm text-slate-300 mb-2">Â¿Ganaste la licitación?</label>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setFeedbackAnexo(prev => prev ? { ...prev, exitosa: true } : null)}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${feedbackAnexo.exitosa === true
                          ? "bg-green-600 text-white"
                          : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                          }`}
                      >
                        âœ… Sí, ganamos
                      </button>
                      <button
                        onClick={() => setFeedbackAnexo(prev => prev ? { ...prev, exitosa: false } : null)}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${feedbackAnexo.exitosa === false
                          ? "bg-red-600 text-white"
                          : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                          }`}
                      >
                        âŒ No ganamos
                      </button>
                      <button
                        onClick={() => setFeedbackAnexo(prev => prev ? { ...prev, exitosa: null } : null)}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${feedbackAnexo.exitosa === null
                          ? "bg-slate-600 text-white"
                          : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                          }`}
                      >
                        ðŸ¤· Aún no sé
                      </button>
                    </div>
                  </div>

                  {/* Botón enviar */}
                  <button
                    onClick={enviarFeedback}
                    disabled={feedbackAnexo.calificacion === 0 || feedbackAnexo.enviando}
                    className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
                  >
                    {feedbackAnexo.enviando ? "â³ Enviando..." : "ðŸ“¤ Enviar Feedback"}
                  </button>
                </div>
              )}

              {/* Estadísticas RAG */}
              {estadisticasRAG && estadisticasRAG.totalPropuestas > 0 && (
                <div className="mt-4 pt-4 border-t border-purple-500/30">
                  <p className="text-purple-300 text-sm">{estadisticasRAG.mensaje}</p>
                  <div className="flex gap-4 mt-2 text-xs text-slate-400">
                    <span>ðŸ“Š {estadisticasRAG.totalPropuestas} propuestas</span>
                    <span>âœ… {estadisticasRAG.tasaExito.toFixed(0)}% exitosas</span>
                    <span>ðŸ” {estadisticasRAG.totalPatrones} patrones</span>
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={() => { setStep(1); setAnalisis(null); setCvsParseados([]); setFeedbackAnexo(null); }}
              className="w-full mt-4 py-2 text-purple-400 hover:text-purple-300 underline"
            >
              Nuevo Proyecto
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
