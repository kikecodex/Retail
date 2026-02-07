// Script para analizar la estructura de las bases SEACE
import { readFileSync, writeFileSync } from "fs";

async function analizarBases() {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const pdfParse = require("pdf-parse-fork");

    console.log("📄 Leyendo BASES+SUPER.pdf...");
    const basesBuffer = readFileSync("./BASES+SUPER.pdf");
    const basesData = await pdfParse(basesBuffer);

    console.log(`✅ Extraídos ${basesData.text.length} caracteres`);

    // Guardar texto completo
    writeFileSync("./analisis-bases.txt", basesData.text);
    console.log("📝 Guardado en analisis-bases.txt");

    // Buscar capítulos
    const capitulos = basesData.text.match(/CAPÍTULO\s+[IVX]+[:\.\s]+[^\n]+/gi) || [];
    console.log("\n📑 CAPÍTULOS DETECTADOS:");
    capitulos.forEach((c: string) => console.log(`  - ${c.trim()}`));

    // Buscar anexos
    const anexos = basesData.text.match(/ANEXO\s+N[°º]?\s*\d+[:\.\s]+[^\n]+/gi) || [];
    console.log("\n📎 ANEXOS DETECTADOS:");
    anexos.forEach((a: string) => console.log(`  - ${a.trim()}`));

    // Buscar perfiles
    const perfiles = basesData.text.match(/(JEFE|ESPECIALISTA|COORDINADOR|PROFESIONAL|INGENIERO|ABOGADO|CONTADOR)[^\n]+/gi) || [];
    console.log("\n👤 PERFILES MENCIONADOS:");
    [...new Set(perfiles.slice(0, 15)) as Set<string>].forEach((p) => console.log(`  - ${p.trim().substring(0, 80)}`));

    console.log("\n✅ Análisis completado");
}

analizarBases().catch(console.error);
