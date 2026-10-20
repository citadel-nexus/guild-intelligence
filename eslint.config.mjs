// ─── CGRF Header ───────────────────────────────────────────────
// File: eslint.config.mjs
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
// Intent: Apply ESLint flat configuration and TypeScript recommended rules to source and tests.
// ───────────────────────────────────────────────────────────────

import js from '@eslint/js';
import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';

export default [
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**'] },
  js.configs.recommended,
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: tsParser,
      globals: { console: 'readonly', process: 'readonly', TextEncoder: 'readonly', TextDecoder: 'readonly' },
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      ...tsPlugin.configs['eslint-recommended'].overrides[0].rules,
      ...tsPlugin.configs.recommended.rules,
    },
  },
];
