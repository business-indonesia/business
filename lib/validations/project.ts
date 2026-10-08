import { z } from "zod";

// Java package name regex conforming to Android package naming conventions
const PACKAGE_NAME_REGEX = /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/;
const HEX_COLOR_REGEX = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/;

export const createProjectSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, "Project name must be at least 2 characters")
    .max(100, "Project name cannot exceed 100 characters"),
  appName: z
    .string()
    .trim()
    .min(2, "App display name must be at least 2 characters")
    .max(50, "App display name cannot exceed 50 characters")
    .regex(/^[^<>&"']+$/, "App name contains disallowed characters"),
  packageId: z
    .string()
    .trim()
    .toLowerCase()
    .regex(
      PACKAGE_NAME_REGEX,
      "Package ID must be a valid Java package identifier (e.g., com.example.myapp)"
    ),
  webUrl: z
    .string()
    .trim()
    .url("A valid HTTP or HTTPS URL is required")
    .refine((url) => url.startsWith("http://") || url.startsWith("https://"), {
      message: "URL must start with http:// or https://",
    }),
  iconUrl: z.string().url("Must be a valid URL").optional().nullable(),
  primaryColor: z
    .string()
    .regex(HEX_COLOR_REGEX, "Must be a valid hex color (e.g., #1E40AF)")
    .default("#1E40AF"),
  splashColor: z
    .string()
    .regex(HEX_COLOR_REGEX, "Must be a valid hex color (e.g., #FFFFFF)")
    .default("#FFFFFF"),
  appVersion: z
    .string()
    .regex(/^\d+\.\d+\.\d+$/, "Version must follow semantic format (e.g., 1.0.0)")
    .default("1.0.0"),
  versionCode: z.number().int().positive().default(1),
});

export type CreateProjectInput = z.infer<typeof createProjectSchema>;
