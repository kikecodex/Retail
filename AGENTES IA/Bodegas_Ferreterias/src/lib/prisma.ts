import { PrismaClient } from "@prisma/client";
import { PrismaNeon } from "@prisma/adapter-neon";

// Create PrismaClient with Neon adapter
// Prisma 7 uses the adapter with just the connection string
const createPrismaClient = () => {
    const connectionString = process.env.DATABASE_URL;

    if (!connectionString) {
        throw new Error("DATABASE_URL is not configured");
    }

    // Create adapter with connection string
    const adapter = new PrismaNeon({
        connectionString
    });

    return new PrismaClient({ adapter });
};

// Global for development hot-reload (prevents multiple instances)
const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== "production") {
    globalForPrisma.prisma = prisma;
}

export default prisma;
