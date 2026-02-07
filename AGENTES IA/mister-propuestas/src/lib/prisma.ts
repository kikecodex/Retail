import { PrismaClient } from "@prisma/client";

// Prisma v7 requires adapter configuration
// For development without actual DB, we'll use a mock or skip initialization
const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

function createPrismaClient() {
    try {
        // Para producción con Neon, usar:
        // import { PrismaNeon } from "@prisma/adapter-neon";
        // const adapter = new PrismaNeon(process.env.DATABASE_URL);
        return new PrismaClient({
            // Configuración básica para desarrollo
        });
    } catch {
        console.warn("PrismaClient not initialized - database not configured");
        return null as unknown as PrismaClient;
    }
}

export const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== "production") {
    globalForPrisma.prisma = prisma;
}
