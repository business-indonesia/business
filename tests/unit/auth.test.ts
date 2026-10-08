import { describe, it, expect } from "vitest";
import {
  UnauthorizedError,
  ForbiddenError,
  getSessionFromRequest,
} from "@/lib/auth";

describe("Auth Module Foundation", () => {
  it("should create UnauthorizedError with default message", () => {
    const error = new UnauthorizedError();
    expect(error.message).toBe("Unauthorized access");
    expect(error.name).toBe("UnauthorizedError");
  });

  it("should create ForbiddenError with custom message", () => {
    const error = new ForbiddenError("Custom forbidden");
    expect(error.message).toBe("Custom forbidden");
    expect(error.name).toBe("ForbiddenError");
  });

  it("should return unauthenticated session context in phase 01 foundation", async () => {
    const session = await getSessionFromRequest();
    expect(session.isAuthenticated).toBe(false);
    expect(session.user).toBeNull();
  });
});
