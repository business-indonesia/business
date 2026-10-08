export interface AuthSessionUser {
  id: string;
  email: string;
  name?: string | null;
  role: "USER" | "ADMIN";
}

export interface SessionContext {
  user: AuthSessionUser | null;
  isAuthenticated: boolean;
}

/**
 * Validates request authentication header or cookie session token.
 * Phase 01 provides the boundary contract and authorization guard.
 */
export async function getSessionFromRequest(
  _request?: Request
): Promise<SessionContext> {
  // In Phase 01, this returns the foundational session shape.
  // Full auth adapter (NextAuth or custom JWT) integrates in Phase 02.
  return {
    user: null,
    isAuthenticated: false,
  };
}

export class UnauthorizedError extends Error {
  constructor(message = "Unauthorized access") {
    super(message);
    this.name = "UnauthorizedError";
  }
}

export class ForbiddenError extends Error {
  constructor(message = "Forbidden: Insufficient privileges") {
    super(message);
    this.name = "ForbiddenError";
  }
}
