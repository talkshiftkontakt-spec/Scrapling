import { z } from "zod";

const baseEnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development")
});

const serverEnvSchema = baseEnvSchema.extend({
  PORT: z.coerce.number().int().positive().default(3001),
  STORAGE_MODE: z.enum(["local", "drive"]).default("local"),
  DESIGN_LIBRARY_PATH: z.string().default("./DesignLibrary"),
  STATIC_BASE_URL: z.string().url().default("http://127.0.0.1:3001/static")
});

const databaseEnvSchema = baseEnvSchema.extend({
  DATABASE_URL: z.string().min(1)
});

const searchEnvSchema = baseEnvSchema.extend({
  QDRANT_URL: z.string().url(),
  QDRANT_API_KEY: z.string().optional()
});

const aiEnvSchema = baseEnvSchema.extend({
  OPENAI_API_KEY: z.string().optional(),
  GEMINI_API_KEY: z.string().optional()
});

const driveEnvSchema = baseEnvSchema.extend({
  GOOGLE_DRIVE_SHARED_ROOT: z.string().default("DesignLibrary"),
  GOOGLE_SERVICE_ACCOUNT_EMAIL: z.string().email().optional(),
  GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY: z.string().optional()
});

const fullEnvSchema = serverEnvSchema.merge(databaseEnvSchema).merge(searchEnvSchema).merge(aiEnvSchema).merge(driveEnvSchema);

export type AppEnv = z.infer<typeof fullEnvSchema>;
export type ServerEnv = z.infer<typeof serverEnvSchema>;
export type DatabaseEnv = z.infer<typeof databaseEnvSchema>;
export type SearchEnv = z.infer<typeof searchEnvSchema>;
export type AiEnv = z.infer<typeof aiEnvSchema>;
export type DriveEnv = z.infer<typeof driveEnvSchema>;

export function readEnv(source: NodeJS.ProcessEnv = process.env): AppEnv {
  return fullEnvSchema.parse(source);
}

export function readServerEnv(source: NodeJS.ProcessEnv = process.env): ServerEnv {
  return serverEnvSchema.parse(source);
}

export function readDatabaseEnv(source: NodeJS.ProcessEnv = process.env): DatabaseEnv {
  return databaseEnvSchema.parse(source);
}

export function readSearchEnv(source: NodeJS.ProcessEnv = process.env): SearchEnv {
  return searchEnvSchema.parse(source);
}

export function readAiEnv(source: NodeJS.ProcessEnv = process.env): AiEnv {
  return aiEnvSchema.parse(source);
}

export function readDriveEnv(source: NodeJS.ProcessEnv = process.env): DriveEnv {
  return driveEnvSchema.parse(source);
}
