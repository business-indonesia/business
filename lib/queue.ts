import { Queue } from "bullmq";
import Redis from "ioredis";
import { env } from "./env";

export const BUILD_QUEUE_NAME = "android-build-jobs";

export interface AndroidBuildJobPayload {
  buildId: string;
  projectId: string;
  projectName?: string;
  userId: string;
  appName: string;
  packageId: string;
  webUrl: string;
  primaryColor?: string | null;
  splashColor?: string | null;
  appVersion: string;
  versionCode: number;
  buildType: "APK" | "AAB" | "BOTH";
}

let redisClient: Redis | null = null;
let buildQueueInstance: Queue<AndroidBuildJobPayload> | null = null;

export function getRedisConnection(): Redis {
  if (!redisClient) {
    redisClient = new Redis(env.REDIS_URL, {
      maxRetriesPerRequest: null,
      lazyConnect: true,
      enableOfflineQueue: false,
    });
  }
  return redisClient;
}

export function getBuildQueue(): Queue<AndroidBuildJobPayload> {
  if (!buildQueueInstance) {
    buildQueueInstance = new Queue<AndroidBuildJobPayload>(BUILD_QUEUE_NAME, {
      connection: getRedisConnection(),
      defaultJobOptions: {
        attempts: 2,
        backoff: {
          type: "exponential",
          delay: 5000,
        },
        removeOnComplete: {
          age: 86400, // keep for 24 hours
          count: 500,
        },
        removeOnFail: {
          age: 604800, // keep for 7 days
        },
      },
    });
  }
  return buildQueueInstance;
}
