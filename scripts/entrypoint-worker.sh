#!/bin/sh
set -e

echo "[Worker Entrypoint] Verifying Android SDK environment..."
if [ -d "$ANDROID_SDK_ROOT" ]; then
  echo "[Worker Entrypoint] Android SDK detected at $ANDROID_SDK_ROOT"
else
  echo "[Worker Entrypoint] WARNING: Android SDK not found at $ANDROID_SDK_ROOT"
fi

echo "[Worker Entrypoint] Starting Android Build Worker daemon..."
exec npm run worker:dev
