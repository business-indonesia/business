# ARCHITECTURE.md — Generated URL to APK & AAB Platform

## 1. System Architecture Overview

The **Generated URL to APK & AAB Platform** (`generatedurltoapkaab`) is an enterprise-grade web application platform that enables users to convert web applications and responsive websites into native, installable Android packages:
- **APK** (Android Package Kit) for direct installation and side-loading.
- **AAB** (Android App Bundle) compliant with Google Play Store publication requirements.

Production Target Domain: `https://generated.business.web.id`

### Core Design Philosophy
1. **Strict Service Decoupling**: Heavy Android compilation workloads (JVM, Android SDK, Gradle, AAPT2) are physically isolated in dedicated worker containers to prevent starvation or crashes on the web tier.
2. **Asynchronous Event-Driven Processing**: Build tasks are dispatched asynchronously through Redis-backed BullMQ queues with real-time status reporting.
3. **Security by Default**: All inputs (package names, URLs, colors, keystore configurations) are strictly validated; zero raw shell string interpolations are allowed.

### High-Level System Architecture Diagram (ASCII)

```
                       +---------------------------------------+
                       |           End User / Browser          |
                       +---------------------------------------+
                                           |
                                  HTTPS (TLS 1.2/1.3)
                                           v
                       +---------------------------------------+
                       |        Nginx Reverse Proxy            |
                       |    (generated.business.web.id)        |
                       |  - SSL Termination / Certbot          |
                       |  - Security Headers / Gzip / Rate Lim |
                       +---------------------------------------+
                                           |
                                     HTTP (Port 3000)
                                           v
                       +---------------------------------------+
                       |        Next.js Web Service            |
                       |  - App Router / React 18 / Tailwind   |
                       |  - REST & Health API Route Handlers   |
                       |  - Zod Request Validation Boundary    |
                       |  - Prisma Client ORM                  |
                       +-------------------+-------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
            (SQL via Prisma)                               (Enqueue Job)
                    v                                             v
+---------------------------------------+     +---------------------------------------+
|         PostgreSQL Database           |     |              Redis Cache              |
|  - Users, Projects, Builds            |     |  - BullMQ Queue ('android-build-jobs')|
|  - Artifacts, BuildLogs               |     |  - Job status & locks                 |
+-------------------+-------------------+     +-------------------+-------------------+
                    ^                                             |
                    | (Update Status / Logs)             (Poll Job Payload)
                    |                                             v
                    +---------------------------------------------+
                    |        Dedicated Build Worker               |
                    |  - BullMQ Worker Daemon                     |
                    |  - OpenJDK 17 & Android SDK 34              |
                    |  - Gradle 8.x + Android Gradle Plugin       |
                    |  - Android Template Injection Engine        |
                    |  - APK / AAB Signing (apksigner)            |
                    +---------------------+-----------------------+
                                          |
                               (Export APK / AAB)
                                          v
                    +---------------------------------------------+
                    |       Persistent Storage Subsystem          |
                    |  - Local Mount: /storage/artifacts          |
                    |  - Cloud Object Storage: S3 / MinIO         |
                    +---------------------------------------------+
```

---

## 2. Frontend Architecture

- **Framework**: Next.js 14 (App Router)
- **UI Framework**: React 18, Tailwind CSS, Lucide Icons, accessible component design system.
- **Language**: TypeScript with strict mode enabled (`strict: true`, `noImplicitAny: true`).
- **Key Client Interfaces**:
  - Landing & feature showcase page.
  - Project Dashboard: Creation wizard with live package name validation, URL validation, and theme customizers.
  - Build Monitor: Real-time progress tracker with streaming build logs and download links for APK/AAB packages.
  - Security Guard: Client-side Zod validation reflecting server schemas for instant feedback.

---

## 3. Backend Architecture

- **Runtime**: Node.js 20+ (standalone containerized runner).
- **Architecture Pattern**: Next.js Server Components, Server Actions, and REST Route Handlers (`/api/*`).
- **Validation Layer**: Zod schema validators guarding every mutation and input parameter.
- **Prisma ORM**: Type-safe query engine connecting to PostgreSQL with singleton lifecycle management to prevent connection pool exhaustion.

---

## 4. Database Architecture (PostgreSQL + Prisma)

The database models are designed to capture the full lifecycle of project configuration, compilation runs, generated files, and diagnostic audit logs.

```
+--------------------+        +---------------------+        +--------------------+
|       User         | 1    * |       Project       | 1    * |       Build        |
|--------------------|--------|---------------------|--------|--------------------|
| id (cuid)          |        | id (cuid)           |        | id (cuid)          |
| email (unique)     |        | userId (FK)         |        | projectId (FK)     |
| passwordHash       |        | appName             |        | userId (FK)        |
| role (USER|ADMIN)  |        | packageId           |        | buildType          |
| createdAt          |        | webUrl              |        | status             |
| updatedAt          |        | primaryColor        |        | progress (0-100)   |
+--------------------+        | appVersion          |        | errorMessage       |
                              | versionCode         |        | startedAt          |
                              +---------------------+        | completedAt        |
                                                             +---------+----------+
                                                                       | 1
                                                     +-----------------+-----------------+
                                                     | *                                 | *
                                           +---------v----------+              +---------v----------+
                                           |     Artifact       |              |      BuildLog      |
                                           |--------------------|              |--------------------|
                                           | id (cuid)          |              | id (cuid)          |
                                           | buildId (FK)       |              | buildId (FK)       |
                                           | artifactType       |              | level (INFO|WARN..) |
                                           | fileName           |              | stage              |
                                           | filePath           |              | message            |
                                           | fileSize           |              | timestamp          |
                                           | checksumSha256     |              +--------------------+
                                           | downloadUrl        |
                                           +--------------------+
```

### Models Summary:
1. **User**: Authentication, roles, and ownership boundaries.
2. **Project**: Target web application configuration (URL, package ID, app name, visual branding).
3. **Build**: Lifecycle tracking for individual compilation tasks (`PENDING`, `QUEUED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`).
4. **Artifact**: Output files produced by the build pipeline (`APK_DEBUG`, `APK_RELEASE`, `AAB_RELEASE`, `KEYSTORE`, `LOG_BUNDLE`) with SHA-256 integrity checksums.
5. **BuildLog**: Granular timestamped log stream by build stage for troubleshooting.

---

## 5. Job Queue & Background Processing

- **Queue Engine**: BullMQ backed by Redis 7.
- **Queue Name**: `android-build-jobs`.
- **Resilience & Fault Tolerance**:
  - Automatic exponential backoff retries for transient build failures.
  - Job deduplication and locking to prevent concurrent compiles on identical configurations.
  - Configurable retention: completed jobs retained for 24 hours, failed jobs retained for 7 days for post-mortem diagnostics.

---

## 6. Android Build Worker (Dedicated & Isolated)

### Strict Isolation Rules
- Compilations **must not** run inside the web application container.
- Build workers run as unprivileged Linux containers with access to:
  - OpenJDK 17 (`JAVA_HOME`)
  - Android SDK Command-Line Tools & Platform 34 (`ANDROID_SDK_ROOT`)
  - Android Gradle Plugin & Gradle 8.x
- Concurrency is throttled (default: 2 parallel builds per worker node) to prevent CPU/memory thrashing during AAPT2 and Kotlin compiler daemon runs.

### Command Execution Architecture (No Shell Interpolation)
```ts
// Safe parameterized execution:
import { execFile } from "child_process";
execFile("./gradlew", ["assembleRelease", "--no-daemon", "--stacktrace"], { cwd: buildDir });
```

---

## 7. Artifact Storage Architecture

- **Driver Abstraction**: Supports both `local` (filesystem volume) and `s3` (S3/MinIO compatible object store).
- **Storage Path Conventions**:
  - `storage/artifacts/{projectId}/{buildId}/app-release.apk`
  - `storage/artifacts/{projectId}/{buildId}/app-release.aab`
  - `storage/artifacts/{projectId}/{buildId}/build.log`
- **Integrity**: SHA-256 hashes generated on write and stored in the database.
- **Security**: Direct download links are gated behind authentication or signed expiring URLs.

---

## 8. Authentication & Authorization Boundaries

- **Role-Based Access Control (RBAC)**: `USER` and `ADMIN` roles.
- **Object-Level Authorization**: Every project, build, and artifact query is filtered by the authenticated user's ID, preventing horizontal privilege escalation (IDOR).
- **Session Layer**: Standardized server-side session contract prepared for JWT/Cookie session integration.

---

## 9. Security Foundation & Defense-in-Depth

1. **Input Validation (Zod)**:
   - Java Package Name validation: Regex `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$` preventing command or filesystem injection.
   - Web URL validation: Whitelisted schemes (`http://`, `https://`), blocking `javascript:`, `file:`, `data:`.
   - App Display Name: Sanitized against XML special characters (`<`, `>`, `&`, `"`, `'`) to prevent XML injection into Android resource files.
2. **Secret Separation**:
   - Zero hard-coded credentials; all secrets stored in `.env` and injected via Docker environment variables.
   - Android keystore passwords and private keys stored encrypted at rest using AES-256-GCM.
3. **No Secret Logging**:
   - Logging redaction rules implemented in worker and API handlers to mask credentials, tokens, and keystore passwords.
4. **Network & Transport**:
   - HSTS, X-Frame-Options (`SAMEORIGIN`), X-Content-Type-Options (`nosniff`), Referrer-Policy, and TLS 1.2/1.3 enforced at Nginx layer.

---

## 10. Production Deployment Architecture

- **Target Domain**: `https://generated.business.web.id`
- **Reverse Proxy**: Nginx container handling HTTPS termination with automated Let's Encrypt certificates.
- **Docker Compose Stack**:
  - `nginx`: Ports 80 & 443
  - `web`: Next.js standalone container (port 3000 internal)
  - `worker`: Android build daemon container (isolated, internal network only)
  - `postgres`: PostgreSQL 16 Alpine (internal network only)
  - `redis`: Redis 7 Alpine with password authentication (internal network only)
- **Persistent Data Volumes**:
  - `postgres_prod_data`: Database records
  - `redis_prod_data`: Queue state and job logs
  - `prod_artifacts`: Generated APK/AAB outputs
  - `certbot_conf` & `certbot_www`: SSL certificates
