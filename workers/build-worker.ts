import { Worker, Job } from "bullmq";
import Redis from "ioredis";
import { BUILD_QUEUE_NAME, AndroidBuildJobPayload } from "../lib/queue";

const redisUrl = process.env.REDIS_URL || "redis://localhost:6379";
const concurrency = parseInt(process.env.WORKER_CONCURRENCY || "2", 10);

console.log("[Worker] Initializing Android Build Worker...");
console.log(`[Worker] Connecting to Redis at ${redisUrl}...`);
console.log(`[Worker] Build queue: ${BUILD_QUEUE_NAME}, Concurrency: ${concurrency}`);

const connection = new Redis(redisUrl, {
  maxRetriesPerRequest: null,
});

export const buildWorker = new Worker<AndroidBuildJobPayload>(
  BUILD_QUEUE_NAME,
  async (job: Job<AndroidBuildJobPayload>) => {
    console.log(`[Worker] Received build job ${job.id} for project ${job.data.projectName || job.data.appName}`);
    console.log(`[Worker] Package ID: ${job.data.packageId}, Build Type: ${job.data.buildType}`);

    // NOTE: In Phase 01, the build worker foundation and queue contract are initialized.
    // The actual Android SDK, Gradle compilation, keystore signing, and artifact generation
    // pipeline will be implemented in Phase 03.
    // No fake/mocked APK generation is allowed in Phase 01 per architecture standards.
    return {
      status: "QUEUED_FOUNDATION_READY",
      jobId: job.id,
      receivedAt: new Date().toISOString(),
    };
  },
  {
    connection,
    concurrency,
  }
);

buildWorker.on("completed", (job) => {
  console.log(`[Worker] Job ${job.id} acknowledged successfully.`);
});

buildWorker.on("failed", (job, err) => {
  console.error(`[Worker] Job ${job?.id} failed with error:`, err);
});

// Graceful shutdown handling
const shutdown = async (signal: string) => {
  console.log(`[Worker] Received ${signal}. Closing worker gracefully...`);
  await buildWorker.close();
  connection.disconnect();
  console.log("[Worker] Worker shutdown complete.");
  process.exit(0);
};

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
