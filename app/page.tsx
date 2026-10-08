import Link from "next/link";
import {
  Smartphone,
  Layers,
  Cpu,
  ShieldCheck,
  Server,
  Database,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Header */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shadow-md">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 dark:text-white">
                URL to APK & AAB
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
                Phase 01 Foundation
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <a
              href="https://generated.business.web.id"
              target="_blank"
              rel="noreferrer"
              className="text-xs sm:text-sm font-mono text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400"
            >
              generated.business.web.id
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 text-sm font-medium mb-6">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>Architecture & Core Foundation Ready</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Convert Web Applications into Native Android Packages
          </h1>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-300">
            A production-ready platform architecture designed to safely build, sign, and distribute
            Android APK and Google Play AAB bundles from web URLs using isolated build workers.
          </p>
        </div>

        {/* Architectural Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {/* Card 1 */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-blue-50 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-4">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">
              Next.js & React Frontend
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Modern App Router architecture equipped with TypeScript strict mode, responsive
              Tailwind UI components, and real-time build monitoring interfaces.
            </p>
          </div>

          {/* Card 2 */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">
              PostgreSQL & Prisma ORM
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Relational data models covering User, Project, Build, Artifact, and BuildLog with
              complete foreign key integrity and scalable indexes.
            </p>
          </div>

          {/* Card 3 */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-amber-50 dark:bg-amber-950 flex items-center justify-center text-amber-600 dark:text-amber-400 mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">
              Isolated Build Worker
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Strict isolation: heavy Android Gradle, JDK 17, and Kotlin SDK builds operate in
              dedicated worker containers completely segregated from the web API.
            </p>
          </div>

          {/* Card 4 */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-rose-50 dark:bg-rose-950 flex items-center justify-center text-rose-600 dark:text-rose-400 mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">
              Security by Default
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Zod input sanitization, strict URL validation, Java package ID verification, zero shell
              interpolation, and secure credential separation.
            </p>
          </div>

          {/* Card 5 */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-4">
              <Server className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">
              Job Queue & Redis
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Asynchronous BullMQ job distribution ensuring high availability, retry mechanisms,
              and horizontal scalability for concurrent compile workloads.
            </p>
          </div>

          {/* Card 6 */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-purple-50 dark:bg-purple-950 flex items-center justify-center text-purple-600 dark:text-purple-400 mb-4">
              <Smartphone className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">
              APK & AAB Outputs
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Dual artifact output support: standalone APK for direct side-loading and Android App
              Bundle (AAB) optimized for Google Play Store publication.
            </p>
          </div>
        </div>

        {/* Phase Roadmap Overview */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-100 dark:border-slate-800 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Platform Delivery Roadmap
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                Structured phased rollout for production readiness.
              </p>
            </div>
            <div className="mt-4 md:mt-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300">
                Phase 01 In Progress
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                ✓
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 dark:text-white">
                  Phase 01: Audit, Foundation & Architecture
                </h4>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Project repository audit, Next.js 14 App Router, TypeScript strict configuration,
                  Prisma schema (User, Project, Build, Artifact, BuildLog), BullMQ definitions,
                  Docker container configurations, and ARCHITECTURE.md documentation.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 opacity-75">
              <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center font-bold text-sm flex-shrink-0">
                2
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 dark:text-white">
                  Phase 02: Authentication & Project Management
                </h4>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  User accounts, session management, secure project CRUD, web app URL metadata
                  fetching, and application icon uploading.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 opacity-75">
              <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center font-bold text-sm flex-shrink-0">
                3
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 dark:text-white">
                  Phase 03: Android Template & Isolated Worker Build Pipeline
                </h4>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Native Android template customization engine, Gradle compile worker execution,
                  keystore signing, and APK / AAB artifact generation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-sm text-slate-500">
          <p>© 2026 generatedurltoapkaab. Target: generated.business.web.id</p>
          <div className="flex space-x-6 mt-4 sm:mt-0">
            <Link href="/api/health" className="hover:text-blue-600 transition">
              Healthcheck API
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
