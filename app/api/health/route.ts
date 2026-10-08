import { NextResponse } from "next/server";
import { env } from "@/lib/env";

export async function GET() {
  return NextResponse.json(
    {
      status: "ok",
      platform: "generatedurltoapkaab",
      targetProductionDomain: "generated.business.web.id",
      phase: "01-foundation",
      timestamp: new Date().toISOString(),
      environment: env.NODE_ENV,
      checks: {
        databaseConfigured: Boolean(env.DATABASE_URL),
        redisConfigured: Boolean(env.REDIS_URL),
        storageDriver: env.STORAGE_DRIVER,
      },
    },
    { status: 200 }
  );
}
