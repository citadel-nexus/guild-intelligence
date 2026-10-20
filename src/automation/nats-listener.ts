// ─── CGRF Header ───────────────────────────────────────────────
// File: src/automation/nats-listener.ts
// Stage: 07_BUILD
// SRS: SRS-CN-INTELLIGENCE-BUILD-001
// CAPS: pending
// CK: pending
// Dispatch: DISP-BUILD-intelligence
// Seat: BITS-CODEGEN
// Owner: Citadel Nexus Inc.
// Created: 2026-10-20
// Depends: package.json
// EnumType: Service
// EnumEdges: DEPENDS_ON package.json
// DAG Node: none
// Intent: Restore valid TypeScript NATS listener syntax and retain the subscribed message data.
// ───────────────────────────────────────────────────────────────

import { connect, StringCodec } from 'nats';

const sc = StringCodec();

export async function startListener(): Promise<void> {
  const nc = await connect({ servers: process.env.NATS_URL });
  const sub = nc.subscribe('citadel.intel.>');
  console.log('[intelligence] Listening on citadel.intel.*');
  for await (const msg of sub) {
    const data = sc.decode(msg.data);
    console.log('[intelligence] Message', { subject: msg.subject, data });
    // Route to handlers based on msg.subject
  }
}
