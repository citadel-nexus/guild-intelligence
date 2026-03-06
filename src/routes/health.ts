export function healthCheck() {
  return {
    guild: 'intelligence',
    status: 'healthy',
    version: '0.1.0',
    nats_prefix: 'citadel.intel.*',
    timestamp: new Date().toISOString(),
  };
}
