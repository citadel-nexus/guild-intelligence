# ─── CGRF Header ───────────────────────────────────────────────
# File: docker/Dockerfile
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .nvmrc, package.json
# EnumType: ConfigDoc
# EnumEdges: DEPENDS_ON .nvmrc; DEPENDS_ON package.json
# DAG Node: none
# Intent: Build and run the distribution with the same pinned Node runtime as CI.
# ───────────────────────────────────────────────────────────────

FROM node:22.17.0-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22.17.0-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 8000
CMD ["node", "dist/index.js"]
