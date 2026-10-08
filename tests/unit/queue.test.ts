import { describe, it, expect } from "vitest";
import { BUILD_QUEUE_NAME, type AndroidBuildJobPayload } from "@/lib/queue";

describe("Queue Contract Foundation", () => {
  it("should have correct queue name configured", () => {
    expect(BUILD_QUEUE_NAME).toBe("android-build-jobs");
  });

  it("should enforce strong typing for build payload", () => {
    const payload: AndroidBuildJobPayload = {
      buildId: "b_123",
      projectId: "p_456",
      userId: "u_789",
      appName: "My Cool App",
      packageId: "com.example.cool",
      webUrl: "https://generated.business.web.id",
      primaryColor: "#1E40AF",
      splashColor: "#FFFFFF",
      appVersion: "1.0.0",
      versionCode: 1,
      buildType: "APK",
    };

    expect(payload.buildId).toBe("b_123");
    expect(payload.buildType).toBe("APK");
    expect(payload.packageId).toBe("com.example.cool");
  });
});
