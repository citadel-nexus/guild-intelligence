// ─── CGRF Header ───────────────────────────────────────────────
// File: vitest.config.ts
// Stage: 11_COMMIT
// SRS: SRS-CN-INTELLIGENCE-BUILD-001
// CAPS: pending
// CK: pending
// Dispatch: DISP-BUILD-intelligence
// Seat: BITS-CODEGEN
// Owner: Citadel Nexus Inc.
// Created: 2026-10-20
// Depends: package.json
// EnumType: ConfigDoc
// EnumEdges: DEPENDS_ON package.json
// DAG Node: none
// Intent: Run Node regression tests with explicit scope and optional coverage gates.
// ───────────────────────────────────────────────────────────────

import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    clearMocks: true,
    restoreMocks: true,
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      thresholds: { statements: 80, branches: 80, functions: 80, lines: 80 },
    },
  },
});
