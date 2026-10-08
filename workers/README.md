# Android Build Worker Architecture

## Overview
The Android Build Worker is an isolated Node.js/TypeScript daemon service that processes asynchronous build jobs queued by the web API through Redis (via BullMQ).

## Core Isolation Principles
1. **Physical & Process Isolation**: Android builds require significant CPU and memory spikes (Gradle daemons, Java Virtual Machine, AAPT2 resource compiling). Compiling must **never** take place inside the web application container.
2. **Dedicated Environment**: The worker container is built with OpenJDK 17, Android command-line tools (SDK Manager, build-tools, platforms), and Gradle.
3. **No Shell Interpolation**: All build commands in subsequent phases will use direct argument array invocations (`execFile` / `spawn`), never unchecked shell strings.
4. **Volume Mounting**: Builds write output APK and AAB files to shared persistent storage or upload directly to S3-compatible storage.

## Job Pipeline (Target for Phase 03)
1. **INIT**: Worker claims job from BullMQ queue `android-build-jobs`.
2. **CHECKOUT TEMPLATE**: Clone clean Android template (`android-template/`).
3. **INJECT CONFIGURATION**: Update `build.gradle.kts`, `AndroidManifest.xml`, `strings.xml`, colors, and icons.
4. **GRADLE BUILD**: Run `./gradlew assembleRelease` (for APK) or `./gradlew bundleRelease` (for AAB).
5. **SIGNING**: Sign artifact using Android `apksigner` / `jarsigner` with project keystore.
6. **EXPORT ARTIFACT**: Copy signed `.apk` and `.aab` to artifact storage, compute SHA-256 checksums, and update `Artifact` records in PostgreSQL.
7. **FINALIZE**: Update `Build` record status to `COMPLETED` and stream logs to `BuildLog`.
