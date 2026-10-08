import { describe, it, expect } from "vitest";
import { createProjectSchema } from "@/lib/validations/project";
import { createBuildSchema } from "@/lib/validations/build";

describe("Project Validation Schema", () => {
  it("should accept valid project creation input", () => {
    const input = {
      name: "My Business App",
      appName: "Business App",
      packageId: "id.web.business.generated",
      webUrl: "https://generated.business.web.id",
      primaryColor: "#1E40AF",
      splashColor: "#FFFFFF",
      appVersion: "1.0.0",
      versionCode: 1,
    };

    const result = createProjectSchema.safeParse(input);
    expect(result.success).toBe(true);
  });

  it("should reject invalid Java package IDs", () => {
    const invalidPackageIds = [
      "invalid", // single segment
      "com..invalid", // double dot
      "123com.app", // segment starts with number
      "com.app-dash", // contains hyphen
      "com.app/slash", // contains slash
      "", // empty
    ];

    for (const packageId of invalidPackageIds) {
      const result = createProjectSchema.safeParse({
        name: "Test App",
        appName: "Test App",
        packageId,
        webUrl: "https://generated.business.web.id",
      });
      expect(result.success).toBe(false);
    }
  });

  it("should reject invalid web URLs (e.g., non-http schemes, xss vectors)", () => {
    const invalidUrls = [
      "javascript:alert(1)",
      "file:///etc/passwd",
      "ftp://example.com",
      "not-a-url",
      "",
    ];

    for (const webUrl of invalidUrls) {
      const result = createProjectSchema.safeParse({
        name: "Test App",
        appName: "Test App",
        packageId: "com.example.testapp",
        webUrl,
      });
      expect(result.success).toBe(false);
    }
  });

  it("should reject invalid hex color formats", () => {
    const invalidColors = ["red", "1E40AF", "#12", "#GGGGGG"];

    for (const primaryColor of invalidColors) {
      const result = createProjectSchema.safeParse({
        name: "Test App",
        appName: "Test App",
        packageId: "com.example.testapp",
        webUrl: "https://example.com",
        primaryColor,
      });
      expect(result.success).toBe(false);
    }
  });
});

describe("Build Validation Schema", () => {
  it("should accept valid build types", () => {
    for (const buildType of ["APK", "AAB", "BOTH"] as const) {
      const result = createBuildSchema.safeParse({
        projectId: "proj_12345",
        buildType,
      });
      expect(result.success).toBe(true);
    }
  });

  it("should reject unknown build types", () => {
    const result = createBuildSchema.safeParse({
      projectId: "proj_12345",
      buildType: "EXE",
    });
    expect(result.success).toBe(false);
  });
});
