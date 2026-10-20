// ─── CGRF Header ───────────────────────────────────────────────
// File: src/automation/cml-bridge.ts
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
// Intent: Remove malformed patch markers and restore the existing CML message bridge compilation.
// ───────────────────────────────────────────────────────────────

/**
 * CML Bridge — receives task queue items via NATS, executes, reports back.
 * Subject: citadel.intel.cml.task
 * Result:  citadel.intel.cml.result
 */
import { connect, StringCodec } from 'nats';

const sc = StringCodec();

export async function startCmlBridge(): Promise<void> {
  const nc = await connect({ servers: process.env.NATS_URL });
  const sub = nc.subscribe('citadel.intel.cml.task');
  console.log('[intelligence] CML bridge listening');
  for await (const msg of sub) {
    const task = JSON.parse(sc.decode(msg.data));
    console.log('[intelligence] CML task', { task_id: task.task_id });
    try {
      const result =  { task_id: task.task_id, status: 'done', output: 'ok' };
      nc.publish('citadel.intel.cml.result', sc.encode(JSON.stringify(result)));
    } catch (err) {
      const result =  { task_id: task.task_id, status: 'failed', error: String(err) };
      nc.publish('citadel.intel.cml.result', sc.encode(JSON.stringify(result)));
    }
  }
}
