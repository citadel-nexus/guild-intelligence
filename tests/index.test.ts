// ─── CGRF Header ───────────────────────────────────────────────
// File: tests/index.test.ts
// Stage: 08_TEST
// SRS: SRS-CN-INTELLIGENCE-BUILD-001
// CAPS: pending
// CK: pending
// Dispatch: DISP-BUILD-intelligence
// Seat: BITS-CODEGEN
// Owner: Citadel Nexus Inc.
// Created: 2026-10-20
// Depends: src/index.ts
// EnumType: Test
// EnumEdges: DEPENDS_ON src/index.ts
// DAG Node: none
// Intent: Verify SDK initialization without opening a real service or event-bus connection.
// ───────────────────────────────────────────────────────────────

import { expect, it, vi } from 'vitest';

const { GuildClient, start } = vi.hoisted(() => {
  const start = vi.fn();
  return { start, GuildClient: vi.fn(function () { return { start }; }) };
});

vi.mock('@citadel-guilds/sdk', () => ({ default: GuildClient }));

it('starts the Intelligence guild using the existing SDK configuration', async () => {
  await import('../src/index.js');
  expect(GuildClient).toHaveBeenCalledWith({
    name: 'intelligence', natsPrefix: 'citadel.intel', port: 8000,
  });
  expect(start).toHaveBeenCalledTimes(1);
});
