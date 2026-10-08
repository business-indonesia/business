# Generated URL to APK & AAB Platform

Enterprise-grade web platform designed to convert responsive websites and web applications into native Android packages (**APK** and **AAB**) with isolated compilation workers and automated signing.

Target Production: [https://generated.business.web.id](https://generated.business.web.id)

---

## Architecture Highlights

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide icons.
- **Backend**: Next.js Server Components & Route Handlers, Zod input validation layer.
- **Database**: PostgreSQL 16 managed via Prisma ORM (`User`, `Project`, `Build`, `Artifact`, `BuildLog`).
- **Job Queue**: BullMQ backed by Redis for asynchronous job dispatch and horizontal scalability.
- **Android Worker**: Isolated container environment containing OpenJDK 17, Android SDK tools, Gradle, and Kotlin.
- **Deployment**: Multi-stage Docker containers with Nginx reverse proxy and SSL termination.

Detailed architectural documentation is available in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Directory Structure

```
generatedurltoapkaab/
├── app/                  # Next.js App Router (pages, layouts, API routes)
│   ├── api/health/       # System healthcheck API route
│   ├── globals.css       # Tailwind base styles and theme tokens
│   ├── layout.tsx        # Root HTML metadata and layout
│   └── page.tsx          # Platform landing and architectural overview
├── components/           # Reusable UI component modules
├── lib/                  # Shared core utilities & contracts
│   ├── auth.ts           # Authentication boundaries and security models
│   ├── env.ts            # Type-safe environment validation
│   ├── prisma.ts         # PrismaClient global singleton
│   ├── queue.ts          # BullMQ queue configuration and payload types
│   ├── utils.ts          # UI style merge utilities
│   └── validations/      # Zod request input validation schemas
├── prisma/
│   └── schema.prisma     # Relational PostgreSQL database schema
├── workers/              # Dedicated Android build worker daemon
│   ├── build-worker.ts   # BullMQ worker daemon entrypoint
│   └── README.md         # Worker architecture documentation
├── android-template/     # Base native Android template specification
├── docker/
│   ├── Dockerfile.worker # Isolated Android SDK build worker container
│   ├── docker-compose.prod.yml # Production Docker compose configuration
│   └── nginx.conf        # Production Nginx reverse proxy configuration
├── scripts/
│   ├── entrypoint-web.sh    # Web service container entrypoint
│   └── entrypoint-worker.sh # Worker container entrypoint
├── tests/                # Automated Vitest test suite
│   ├── setup.ts          # Vitest testing setup
│   └── unit/             # Unit tests for validations, env, auth, and queue
├── .env.example          # Documented environment variable template
├── Dockerfile            # Multi-stage production Next.js Dockerfile
├── docker-compose.yml    # Development Docker stack
├── package.json          # Node dependencies and project scripts
├── tsconfig.json         # Strict TypeScript compiler options
├── ARCHITECTURE.md       # Comprehensive system architecture documentation
└── README.md             # Project documentation and developer guide
```

---

## Prerequisites

- Node.js 20.x or 22.x LTS
- npm 10.x+
- Docker & Docker Compose (optional for containerized execution)
- PostgreSQL 16 & Redis 7 (or run via Docker Compose)

---

## Quick Start (Local Development)

### 1. Clone & Install Dependencies
```bash
git clone <repository-url>
cd generatedurltoapkaab
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Review and update credentials in .env as needed
```

### 3. Generate Database Client & Push Schema
```bash
npm run db:generate
# When PostgreSQL is active:
npm run db:migrate
```

### 4. Start Local Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

---

## Development Commands

| Command | Description |
| :--- | :--- |
| `npm run dev` | Launch Next.js local development server |
| `npm run build` | Compile Next.js production standalone bundle |
| `npm run start` | Start Next.js production server |
| `npm run lint` | Run ESLint across codebase |
| `npm run typecheck` | Run TypeScript type checking (`tsc --noEmit`) |
| `npm run test` | Execute unit and integration tests via Vitest |
| `npm run test:watch` | Run Vitest in watch mode |
| `npm run format` | Auto-format source code using Prettier |
| `npm run format:check` | Check code formatting compliance |
| `npm run db:generate` | Generate Prisma client from schema |
| `npm run db:migrate` | Apply Prisma database migrations |
| `npm run db:push` | Push Prisma schema directly to database |
| `npm run worker:dev` | Start isolated Android build worker daemon locally |

---

## Running with Docker Compose

### Development Stack
To spin up the web application, isolated worker, PostgreSQL, and Redis together:
```bash
docker-compose up --build
```

### Production Stack
```bash
docker-compose -f docker/docker-compose.prod.yml up -d --build
```

---

## Security Foundation

- **Input Validation**: Strict Zod schemas enforcing Android package conventions (`^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`) and HTTP/HTTPS URLs.
- **Zero Shell Interpolation**: All external build tools are invoked via parameterized argument arrays.
- **Credential Separation**: Secrets and sensitive keys are decoupled via environment variables.
- **Container Isolation**: Heavy Gradle build processes run inside a separate, unprivileged worker container.

---

## License
Proprietary — All rights reserved.
