/**
 * Vector Store con ChromaDB
 * 
 * Implementación de RAG (Retrieval Augmented Generation) para
 * hacer consultas inteligentes sobre documentos de licitación.
 */

import { ChromaClient, Collection } from "chromadb";
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

// Cliente de ChromaDB (en memoria para desarrollo)
let chromaClient: ChromaClient | null = null;
let documentosCollection: Collection | null = null;

/**
 * Inicializa la conexión a ChromaDB
 */
async function getChromaClient(): Promise<ChromaClient> {
    if (!chromaClient) {
        chromaClient = new ChromaClient();
    }
    return chromaClient;
}

/**
 * Obtiene o crea la colección de documentos
 */
async function getDocumentosCollection(): Promise<Collection> {
    if (!documentosCollection) {
        const client = await getChromaClient();
        documentosCollection = await client.getOrCreateCollection({
            name: "documentos_licitacion",
            metadata: { description: "Documentos de bases de licitación indexados" },
        });
    }
    return documentosCollection;
}

/**
 * Divide un texto largo en chunks más pequeños para indexación
 */
function dividirEnChunks(texto: string, chunkSize: number = 1000, overlap: number = 200): string[] {
    const chunks: string[] = [];
    let inicio = 0;

    while (inicio < texto.length) {
        const fin = Math.min(inicio + chunkSize, texto.length);
        chunks.push(texto.slice(inicio, fin));
        inicio += chunkSize - overlap;
    }

    return chunks;
}

/**
 * Genera embeddings usando Gemini
 */
async function generarEmbeddings(textos: string[]): Promise<number[][]> {
    const model = genAI.getGenerativeModel({ model: "text-embedding-004" });

    const embeddings: number[][] = [];

    for (const texto of textos) {
        try {
            const result = await model.embedContent(texto);
            embeddings.push(result.embedding.values);
        } catch (error) {
            console.error("Error generando embedding:", error);
            // Embedding vacío como fallback
            embeddings.push(new Array(768).fill(0));
        }
    }

    return embeddings;
}

export interface DocumentoIndexado {
    id: string;
    nombreArchivo: string;
    proyecto: string;
    chunks: number;
    fechaIndexado: Date;
}

/**
 * Indexa un documento de licitación en ChromaDB
 */
export async function indexarDocumento(
    documentoId: string,
    nombreArchivo: string,
    proyecto: string,
    contenido: string
): Promise<DocumentoIndexado> {
    const collection = await getDocumentosCollection();

    // Dividir en chunks
    const chunks = dividirEnChunks(contenido);
    console.log(`📚 Dividiendo documento en ${chunks.length} chunks...`);

    // Generar IDs únicos para cada chunk
    const ids = chunks.map((_, i) => `${documentoId}_chunk_${i}`);

    // Metadatos para cada chunk
    const metadatas = chunks.map((_, i) => ({
        documentoId,
        nombreArchivo,
        proyecto,
        chunkIndex: i,
        totalChunks: chunks.length,
    }));

    // Generar embeddings
    console.log("🧠 Generando embeddings...");
    const embeddings = await generarEmbeddings(chunks);

    // Añadir a ChromaDB
    await collection.add({
        ids,
        embeddings,
        documents: chunks,
        metadatas,
    });

    console.log(`✅ Documento indexado: ${nombreArchivo} (${chunks.length} chunks)`);

    return {
        id: documentoId,
        nombreArchivo,
        proyecto,
        chunks: chunks.length,
        fechaIndexado: new Date(),
    };
}

export interface ResultadoBusqueda {
    texto: string;
    score: number;
    metadata: {
        documentoId: string;
        nombreArchivo: string;
        chunkIndex: number;
    };
}

/**
 * Busca fragmentos relevantes para una consulta
 */
export async function buscarFragmentosRelevantes(
    consulta: string,
    documentoId?: string,
    maxResultados: number = 5
): Promise<ResultadoBusqueda[]> {
    const collection = await getDocumentosCollection();

    // Generar embedding de la consulta
    const [queryEmbedding] = await generarEmbeddings([consulta]);

    // Construir filtro si se especifica documento
    const whereFilter = documentoId ? { documentoId } : undefined;

    // Buscar en ChromaDB
    const results = await collection.query({
        queryEmbeddings: [queryEmbedding],
        nResults: maxResultados,
        where: whereFilter,
    });

    // Formatear resultados
    const fragmentos: ResultadoBusqueda[] = [];

    if (results.documents && results.documents[0]) {
        for (let i = 0; i < results.documents[0].length; i++) {
            fragmentos.push({
                texto: results.documents[0][i] || "",
                score: results.distances?.[0]?.[i] ?? 0,
                metadata: {
                    documentoId: (results.metadatas?.[0]?.[i] as { documentoId?: string })?.documentoId || "",
                    nombreArchivo: (results.metadatas?.[0]?.[i] as { nombreArchivo?: string })?.nombreArchivo || "",
                    chunkIndex: (results.metadatas?.[0]?.[i] as { chunkIndex?: number })?.chunkIndex ?? 0,
                },
            });
        }
    }

    return fragmentos;
}

/**
 * Responde una pregunta sobre las bases usando RAG
 */
export async function responderPreguntaRAG(
    pregunta: string,
    documentoId?: string
): Promise<{ respuesta: string; fragmentosUsados: ResultadoBusqueda[] }> {
    // 1. Buscar fragmentos relevantes
    const fragmentos = await buscarFragmentosRelevantes(pregunta, documentoId);

    if (fragmentos.length === 0) {
        return {
            respuesta: "No encontré información relevante para responder tu pregunta. Asegúrate de haber indexado el documento primero.",
            fragmentosUsados: [],
        };
    }

    // 2. Construir contexto con fragmentos
    const contexto = fragmentos
        .map((f, i) => `[Fragmento ${i + 1}]:\n${f.texto}`)
        .join("\n\n");

    // 3. Generar respuesta con Gemini
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    const prompt = `Eres un experto en licitaciones públicas peruanas. 
Responde la siguiente pregunta usando ÚNICAMENTE la información de los fragmentos proporcionados.
Si la información no está en los fragmentos, di que no tienes esa información.

FRAGMENTOS DEL DOCUMENTO:
${contexto}

PREGUNTA: ${pregunta}

RESPUESTA (sé específico y cita números/datos exactos cuando sea posible):`;

    const result = await model.generateContent(prompt);
    const respuesta = result.response.text();

    return {
        respuesta,
        fragmentosUsados: fragmentos,
    };
}

/**
 * Obtiene estadísticas del vector store
 */
export async function obtenerEstadisticasRAG(): Promise<{
    totalDocumentos: number;
    totalChunks: number;
    coleccionActiva: boolean;
}> {
    try {
        const collection = await getDocumentosCollection();
        const count = await collection.count();

        return {
            totalDocumentos: 0, // Se calcularía con consulta más compleja
            totalChunks: count,
            coleccionActiva: true,
        };
    } catch {
        return {
            totalDocumentos: 0,
            totalChunks: 0,
            coleccionActiva: false,
        };
    }
}
