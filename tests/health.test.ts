// ─── CGRF Header ───────────────────────────────────────────────
// File: tests/health.test.ts
// Stage: 08_TEST
// SRS: SRS-CN-INTELLIGENCE-BUILD-001
// CAPS: pending
// CK: pending
// Dispatch: DISP-BUILD-intelligence
// Seat: BITS-CODEGEN
// Owner: Citadel Nexus Inc.
// Created: 2026-10-20
// Depends: src/routes/health.ts
// EnumType: Test
// EnumEdges: DEPENDS_ON src/routes/health.ts
// DAG Node: none
// Intent: Verify the public health payload and timestamp behavior without starting a service.
// ───────────────────────────────────────────────────────────────

import { afterEach, describe, expect, it, vi } from 'vitest';
import { healthCheck } from '../src/routes/health.js';

afterEach(() => vi.useRealTimers());

describe('healthCheck', () => {
  it('returns the public health contract with a fresh ISO timestamp', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-10-20T12:00:00Z'));
    expect(healthCheck()).toEqual({
      guild: 'intelligence', status: 'healthy', version: '0.1.0',
      nats_prefix: 'citadel.intel.*', timestamp: '2026-10-20T12:00:00.000Z',
    });
    vi.advanceTimersByTime(1000);
    expect(healthCheck().timestamp).toBe('2026-10-20T12:00:01.000Z');
  });
});
