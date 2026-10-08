#!/bin/sh
set -e

echo "[Web Entrypoint] Running database migrations..."
npx prisma migrate deploy || echo "[Web Entrypoint] Note: migrations skipped or database not ready yet."

echo "[Web Entrypoint] Starting web application server..."
exec node server.js
