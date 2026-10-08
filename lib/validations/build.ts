import { z } from "zod";

export const createBuildSchema = z.object({
  projectId: z.string().min(1, "Project ID is required"),
  buildType: z.enum(["APK", "AAB", "BOTH"], {
    errorMap: () => ({ message: "Build type must be APK, AAB, or BOTH" }),
  }),
});

export type CreateBuildInput = z.infer<typeof createBuildSchema>;
