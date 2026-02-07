/**
 * Generador de Anexos OSCE
 * 
 * Genera automáticamente los anexos de licitación con los datos
 * extraídos del análisis de bases y CVs parseados.
 */

export interface DatosProyecto {
    nomenclaturaProceso: string;
    tipoModalidad: string;
    entidadConvocante: string;
    objetoContratacion: string;
    valorReferencial: string;
    plazoEjecucion: string;
}

export interface DatosPostor {
    razonSocial: string;
    ruc: string;
    representanteLegal: string;
    dniRepresentante: string;
}

export interface DatosCV {
    nombre: string;
    dni: string;
    universidad: string;
    titulo: string;
    colegiatura: string;
    habilitacionVigente: boolean;
    experiencias: {
        empresa: string;
        cargo: string;
        fechaInicio: string;
        fechaFin: string;
        descripcion: string;
    }[];
}

export interface AnexoGenerado {
    numero: string;
    nombre: string;
    contenidoHtml: string;
    estilosCss: string;
}

// Estilos base para todos los anexos
const ESTILOS_BASE = `
  body {
    font-family: Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.4;
    margin: 2cm;
    color: #000;
  }
  .header {
    text-align: center;
    margin-bottom: 20px;
    border-bottom: 2px solid #000;
    padding-bottom: 10px;
  }
  .titulo {
    font-size: 14pt;
    font-weight: bold;
    text-align: center;
    margin: 20px 0;
  }
  .subtitulo {
    font-size: 12pt;
    font-weight: bold;
    margin: 15px 0 10px 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
  }
  th, td {
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
  }
  th {
    background-color: #f0f0f0;
    font-weight: bold;
  }
  .campo {
    display: flex;
    margin: 8px 0;
  }
  .campo-label {
    font-weight: bold;
    min-width: 200px;
  }
  .campo-valor {
    flex: 1;
    border-bottom: 1px dotted #000;
    padding-left: 10px;
  }
  .firma {
    margin-top: 60px;
    text-align: center;
  }
  .linea-firma {
    border-top: 1px solid #000;
    width: 250px;
    margin: 0 auto;
    padding-top: 5px;
  }
  .nota {
    font-size: 9pt;
    color: #666;
    margin-top: 20px;
  }
  @media print {
    body { margin: 1.5cm; }
    .no-print { display: none; }
  }
`;

/**
 * Genera Anexo 10: Curriculum Vitae de Personal Clave
 */
export function generarAnexo10_CV(
    proyecto: DatosProyecto,
    postor: DatosPostor,
    cv: DatosCV,
    cargo: string
): AnexoGenerado {
    const html = `
    <div class="header">
      <strong>ANEXO N° 10</strong><br>
      <span>CURRICULUM VITAE DEL PERSONAL CLAVE</span>
    </div>

    <div class="titulo">
      ${proyecto.nomenclaturaProceso}
    </div>

    <table>
      <tr>
        <th colspan="2">DATOS DEL POSTOR</th>
      </tr>
      <tr>
        <td style="width: 30%">Razón Social:</td>
        <td>${postor.razonSocial}</td>
      </tr>
      <tr>
        <td>RUC:</td>
        <td>${postor.ruc}</td>
      </tr>
    </table>

    <table>
      <tr>
        <th colspan="2">DATOS DEL PROFESIONAL</th>
      </tr>
      <tr>
        <td style="width: 30%">Cargo Propuesto:</td>
        <td><strong>${cargo}</strong></td>
      </tr>
      <tr>
        <td>Nombres y Apellidos:</td>
        <td>${cv.nombre}</td>
      </tr>
      <tr>
        <td>DNI:</td>
        <td>${cv.dni}</td>
      </tr>
    </table>

    <div class="subtitulo">I. FORMACIÓN ACADÉMICA</div>
    <table>
      <tr>
        <th>Universidad / Instituto</th>
        <th>Título / Grado</th>
        <th>N° Colegiatura</th>
      </tr>
      <tr>
        <td>${cv.universidad}</td>
        <td>${cv.titulo}</td>
        <td>${cv.colegiatura}</td>
      </tr>
    </table>

    <div class="subtitulo">II. ESTADO DE HABILITACIÓN</div>
    <table>
      <tr>
        <td style="width: 50%">Habilitación Profesional Vigente:</td>
        <td>${cv.habilitacionVigente ? "✓ SÍ" : "✗ NO"}</td>
      </tr>
    </table>

    <div class="subtitulo">III. EXPERIENCIA PROFESIONAL</div>
    <table>
      <tr>
        <th style="width: 25%">Empresa/Entidad</th>
        <th style="width: 20%">Cargo</th>
        <th style="width: 15%">Fecha Inicio</th>
        <th style="width: 15%">Fecha Fin</th>
        <th style="width: 25%">Descripción</th>
      </tr>
      ${cv.experiencias.map(exp => `
        <tr>
          <td>${exp.empresa}</td>
          <td>${exp.cargo}</td>
          <td>${exp.fechaInicio}</td>
          <td>${exp.fechaFin}</td>
          <td>${exp.descripcion}</td>
        </tr>
      `).join('')}
    </table>

    <div class="firma">
      <div class="linea-firma">
        ${cv.nombre}<br>
        <small>DNI: ${cv.dni}</small>
      </div>
    </div>

    <p class="nota">
      Declaro bajo juramento que la información proporcionada es veraz y 
      autorizo su verificación.
    </p>
  `;

    return {
        numero: "10",
        nombre: "Curriculum Vitae del Personal Clave",
        contenidoHtml: html,
        estilosCss: ESTILOS_BASE
    };
}

/**
 * Genera Anexo 11: Declaración Jurada de Personal Clave
 */
export function generarAnexo11_DeclaracionPersonal(
    proyecto: DatosProyecto,
    postor: DatosPostor,
    personalClave: { nombre: string; dni: string; cargo: string }[]
): AnexoGenerado {
    const html = `
    <div class="header">
      <strong>ANEXO N° 11</strong><br>
      <span>DECLARACIÓN JURADA DEL PERSONAL CLAVE PROPUESTO</span>
    </div>

    <div class="titulo">
      ${proyecto.nomenclaturaProceso}
    </div>

    <p>
      Señores<br>
      <strong>${proyecto.entidadConvocante}</strong><br>
      Presente.-
    </p>

    <p>
      El que suscribe, <strong>${postor.representanteLegal}</strong>, 
      identificado con DNI N° ${postor.dniRepresentante}, Representante Legal 
      de <strong>${postor.razonSocial}</strong> con RUC N° ${postor.ruc}, 
      declara bajo juramento que el personal clave propuesto para la ejecución 
      del contrato se encuentra disponible y se compromete a participar en la 
      ejecución de la obra:
    </p>

    <div class="subtitulo">OBJETO DE CONTRATACIÓN:</div>
    <p style="text-align: justify">${proyecto.objetoContratacion}</p>

    <div class="subtitulo">PERSONAL CLAVE PROPUESTO:</div>
    <table>
      <tr>
        <th style="width: 10%">N°</th>
        <th style="width: 40%">Nombres y Apellidos</th>
        <th style="width: 20%">DNI</th>
        <th style="width: 30%">Cargo Propuesto</th>
      </tr>
      ${personalClave.map((p, i) => `
        <tr>
          <td style="text-align: center">${i + 1}</td>
          <td>${p.nombre}</td>
          <td>${p.dni}</td>
          <td>${p.cargo}</td>
        </tr>
      `).join('')}
    </table>

    <p>
      Asimismo, declaro que el personal propuesto no tiene impedimento para 
      contratar con el Estado y cumple con los requisitos establecidos en las 
      Bases del presente proceso de selección.
    </p>

    <p>
      Lima, _________ de _________________ de 20____
    </p>

    <div class="firma">
      <div class="linea-firma">
        ${postor.representanteLegal}<br>
        <small>Representante Legal</small><br>
        <small>${postor.razonSocial}</small>
      </div>
    </div>
  `;

    return {
        numero: "11",
        nombre: "Declaración Jurada del Personal Clave Propuesto",
        contenidoHtml: html,
        estilosCss: ESTILOS_BASE
    };
}

/**
 * Genera Anexo 8: Experiencia del Postor en la Especialidad
 */
export function generarAnexo8_ExperienciaPostor(
    proyecto: DatosProyecto,
    postor: DatosPostor,
    experiencias: {
        cliente: string;
        objetoContrato: string;
        montoFacturado: number;
        fechaConformidad: string;
    }[]
): AnexoGenerado {
    const totalMonto = experiencias.reduce((sum, exp) => sum + exp.montoFacturado, 0);

    const html = `
    <div class="header">
      <strong>ANEXO N° 8</strong><br>
      <span>EXPERIENCIA DEL POSTOR EN LA ESPECIALIDAD</span>
    </div>

    <div class="titulo">
      ${proyecto.nomenclaturaProceso}
    </div>

    <table>
      <tr>
        <th colspan="2">DATOS DEL POSTOR</th>
      </tr>
      <tr>
        <td style="width: 30%">Razón Social:</td>
        <td>${postor.razonSocial}</td>
      </tr>
      <tr>
        <td>RUC:</td>
        <td>${postor.ruc}</td>
      </tr>
    </table>

    <div class="subtitulo">EXPERIENCIA EN LA ESPECIALIDAD</div>
    <table>
      <tr>
        <th style="width: 8%">N°</th>
        <th style="width: 22%">Cliente</th>
        <th style="width: 35%">Objeto del Contrato</th>
        <th style="width: 18%">Monto Facturado (S/)</th>
        <th style="width: 17%">Fecha Conformidad</th>
      </tr>
      ${experiencias.map((exp, i) => `
        <tr>
          <td style="text-align: center">${i + 1}</td>
          <td>${exp.cliente}</td>
          <td>${exp.objetoContrato}</td>
          <td style="text-align: right">${exp.montoFacturado.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</td>
          <td style="text-align: center">${exp.fechaConformidad}</td>
        </tr>
      `).join('')}
      <tr>
        <td colspan="3" style="text-align: right; font-weight: bold">TOTAL:</td>
        <td style="text-align: right; font-weight: bold">S/ ${totalMonto.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</td>
        <td></td>
      </tr>
    </table>

    <p class="nota">
      Nota: La información consignada deberá ser sustentada con la documentación 
      correspondiente (contratos, constancias, actas de conformidad, etc.)
    </p>

    <div class="firma">
      <div class="linea-firma">
        ${postor.representanteLegal}<br>
        <small>Representante Legal</small>
      </div>
    </div>
  `;

    return {
        numero: "8",
        nombre: "Experiencia del Postor en la Especialidad",
        contenidoHtml: html,
        estilosCss: ESTILOS_BASE
    };
}

/**
 * Genera Anexo 15: Declaración Jurada de Compromiso del Personal
 */
export function generarAnexo15_CompromisoPersonal(
    proyecto: DatosProyecto,
    profesional: { nombre: string; dni: string; cargo: string },
    postor: DatosPostor
): AnexoGenerado {
    const html = `
    <div class="header">
      <strong>ANEXO N° 15</strong><br>
      <span>DECLARACIÓN JURADA DE COMPROMISO DEL PERSONAL CLAVE</span>
    </div>

    <div class="titulo">
      ${proyecto.nomenclaturaProceso}
    </div>

    <p>
      Señores<br>
      <strong>${proyecto.entidadConvocante}</strong><br>
      Presente.-
    </p>

    <p style="text-align: justify">
      El que suscribe, <strong>${profesional.nombre}</strong>, identificado con 
      DNI N° <strong>${profesional.dni}</strong>, mediante el presente documento 
      me comprometo a participar en la ejecución del contrato derivado del 
      proceso de selección <strong>${proyecto.nomenclaturaProceso}</strong>, 
      asumiendo el cargo de <strong>${profesional.cargo}</strong>, en caso que 
      la empresa <strong>${postor.razonSocial}</strong> obtenga la buena pro.
    </p>

    <p style="text-align: justify">
      Asimismo, declaro bajo juramento:
    </p>

    <ul>
      <li>No tener impedimento para contratar con el Estado.</li>
      <li>No encontrarme sancionado o inhabilitado para ejercer mi profesión.</li>
      <li>Contar con el título profesional y colegiatura vigente.</li>
      <li>Que mi habilitación profesional se encuentra vigente.</li>
      <li>Que la información y documentación presentada en mi curriculum vitae es veraz.</li>
    </ul>

    <p>
      Lima, _________ de _________________ de 20____
    </p>

    <div class="firma">
      <div class="linea-firma">
        ${profesional.nombre}<br>
        <small>DNI: ${profesional.dni}</small><br>
        <small>${profesional.cargo}</small>
      </div>
    </div>
  `;

    return {
        numero: "15",
        nombre: "Declaración Jurada de Compromiso del Personal Clave",
        contenidoHtml: html,
        estilosCss: ESTILOS_BASE
    };
}

/**
 * Genera documento HTML completo listo para impresión/PDF
 */
export function generarDocumentoCompleto(anexo: AnexoGenerado): string {
    return `
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>ANEXO N° ${anexo.numero} - ${anexo.nombre}</title>
      <style>
        ${anexo.estilosCss}
      </style>
    </head>
    <body>
      ${anexo.contenidoHtml}
    </body>
    </html>
  `;
}
