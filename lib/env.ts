import { z } from "zod";

export const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.string().default("3000"),
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  DATABASE_URL: z
    .string()
    .min(1, "DATABASE_URL is required")
    .default(
      "postgresql://postgres:postgres@localhost:5432/generatedurltoapkaab_dev?schema=public"
    ),
  REDIS_URL: z.string().default("redis://localhost:6379"),
  AUTH_SECRET: z
    .string()
    .min(16, "AUTH_SECRET must be at least 16 characters long")
    .default("dev-insecure-secret-key-32-characters-minimum-for-testing"),
  STORAGE_DRIVER: z.enum(["local", "s3"]).default("local"),
  STORAGE_LOCAL_PATH: z.string().default("./storage/artifacts"),
  S3_ENDPOINT: z.string().optional(),
  S3_REGION: z.string().optional().default("us-east-1"),
  S3_BUCKET: z.string().optional(),
  S3_ACCESS_KEY: z.string().optional(),
  S3_SECRET_KEY: z.string().optional(),
});

export const env = {
  NODE_ENV: process.env.NODE_ENV || "development",
  PORT: process.env.PORT || "3000",
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  DATABASE_URL:
    process.env.DATABASE_URL ||
    "postgresql://postgres:postgres@localhost:5432/generatedurltoapkaab_dev?schema=public",
  REDIS_URL: process.env.REDIS_URL || "redis://localhost:6379",
  AUTH_SECRET:
    process.env.AUTH_SECRET || "dev-insecure-secret-key-32-characters-minimum-for-testing",
  STORAGE_DRIVER: (process.env.STORAGE_DRIVER as "local" | "s3") || "local",
  STORAGE_LOCAL_PATH: process.env.STORAGE_LOCAL_PATH || "./storage/artifacts",
  S3_ENDPOINT: process.env.S3_ENDPOINT,
  S3_REGION: process.env.S3_REGION || "us-east-1",
  S3_BUCKET: process.env.S3_BUCKET,
  S3_ACCESS_KEY: process.env.S3_ACCESS_KEY,
  S3_SECRET_KEY: process.env.S3_SECRET_KEY,
};

export function validateEnv(customEnv: Record<string, string | undefined> = process.env) {
  return envSchema.safeParse(customEnv);
}
