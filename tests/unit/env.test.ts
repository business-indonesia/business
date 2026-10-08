import { describe, it, expect } from "vitest";
import { validateEnv, env } from "@/lib/env";

describe("Environment Configuration", () => {
  it("should have default fallback values defined", () => {
    expect(env.NODE_ENV).toBeDefined();
    expect(env.PORT).toBeDefined();
    expect(env.DATABASE_URL).toBeDefined();
    expect(env.REDIS_URL).toBeDefined();
    expect(env.STORAGE_DRIVER).toMatch(/local|s3/);
  });

  it("should validate valid environment configuration", () => {
    const result = validateEnv();
    expect(result.success).toBe(true);
  });

  it("should reject invalid NEXT_PUBLIC_APP_URL", () => {
    const result = validateEnv({
      NEXT_PUBLIC_APP_URL: "invalid-url",
    });
    expect(result.success).toBe(false);
  });

  it("should reject too short AUTH_SECRET", () => {
    const result = validateEnv({
      AUTH_SECRET: "short",
    });
    expect(result.success).toBe(false);
  });
});
