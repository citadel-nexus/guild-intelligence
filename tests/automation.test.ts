// ─── CGRF Header ───────────────────────────────────────────────
// File: tests/automation.test.ts
// Stage: 08_TEST
// SRS: SRS-CN-INTELLIGENCE-BUILD-001
// CAPS: pending
// CK: pending
// Dispatch: DISP-BUILD-intelligence
// Seat: BITS-CODEGEN
// Owner: Citadel Nexus Inc.
// Created: 2026-10-20
// Depends: src/automation/nats-listener.ts, src/automation/cml-bridge.ts
// EnumType: Test
// EnumEdges: DEPENDS_ON src/automation/nats-listener.ts; DEPENDS_ON src/automation/cml-bridge.ts
// DAG Node: none
// Intent: Exercise listener decoding and CML success/failure behavior with isolated network mocks.
// ───────────────────────────────────────────────────────────────

import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { connect, type NatsConnection } from 'nats';
import { startListener } from '../src/automation/nats-listener.js';
import { startCmlBridge } from '../src/automation/cml-bridge.js';

vi.mock('nats', () => ({
  connect: vi.fn(),
  StringCodec: () => ({
    encode: (value: string) => new TextEncoder().encode(value),
    decode: (value: Uint8Array) => new TextDecoder().decode(value),
  }),
}));

function connection(payloads: string[]) {
  const subscribe = vi.fn(async function* () {
    for (const payload of payloads) {
      yield { subject: 'citadel.intel.cml.task', data: new TextEncoder().encode(payload) };
    }
  });
  const publish = vi.fn();
  // A test double at the network boundary; runtime imports remain the real NATS package.
  vi.mocked(connect).mockResolvedValue({ subscribe, publish } as unknown as NatsConnection);
  return { subscribe, publish };
}

beforeEach(() => {
  vi.mocked(connect).mockReset();
  vi.stubEnv('NATS_URL', 'nats://127.0.0.1:4222');
  vi.spyOn(console, 'log').mockImplementation(() => {});
});
afterEach(() => vi.unstubAllEnvs());

describe('NATS listener', () => {
  it('uses the configured server and decodes subscribed messages', async () => {
    const nc = connection(['watch-event']);
    await startListener();
    expect(connect).toHaveBeenCalledWith({ servers: 'nats://127.0.0.1:4222' });
    expect(nc.subscribe).toHaveBeenCalledWith('citadel.intel.>');
    expect(console.log).toHaveBeenCalledWith('[intelligence] Message', {
      subject: 'citadel.intel.cml.task', data: 'watch-event',
    });
    expect(nc.publish).not.toHaveBeenCalled();
  });

  it('propagates connection failures instead of reporting a healthy listener', async () => {
    vi.mocked(connect).mockRejectedValueOnce(new Error('connection unavailable'));
    await expect(startListener()).rejects.toThrow('connection unavailable');
  });
});

describe('CML bridge', () => {
  it('publishes a result for each task and preserves its task id', async () => {
    const nc = connection(['{"task_id":"first"}', '{"task_id":"second"}']);
    await startCmlBridge();
    expect(connect).toHaveBeenCalledWith({ servers: 'nats://127.0.0.1:4222' });
    expect(nc.subscribe).toHaveBeenCalledWith('citadel.intel.cml.task');
    expect(nc.publish).toHaveBeenCalledTimes(2);
    for (const [index, taskId] of ['first', 'second'].entries()) {
      const [subject, payload] = nc.publish.mock.calls[index];
      expect(subject).toBe('citadel.intel.cml.result');
      expect(JSON.parse(new TextDecoder().decode(payload))).toEqual({
        task_id: taskId, status: 'done', output: 'ok',
      });
    }
  });

  it('preserves the failure result when publishing the success result throws', async () => {
    const nc = connection(['{"task_id":"failed-task"}']);
    nc.publish.mockImplementationOnce(() => { throw new Error('publish failed'); });
    await startCmlBridge();
    const [subject, payload] = nc.publish.mock.calls[1];
    expect(subject).toBe('citadel.intel.cml.result');
    expect(JSON.parse(new TextDecoder().decode(payload))).toEqual({
      task_id: 'failed-task', status: 'failed', error: 'Error: publish failed',
    });
  });

  it('rejects invalid JSON without publishing a success result', async () => {
    const nc = connection(['invalid JSON']);
    await expect(startCmlBridge()).rejects.toThrow(SyntaxError);
    expect(nc.publish).not.toHaveBeenCalled();
  });
});
