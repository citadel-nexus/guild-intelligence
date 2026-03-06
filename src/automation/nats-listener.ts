import  connect, StringCodec  from 'nats';

const sc = StringCodec();

export async function startListener() {
  const nc = await connect( servers: process.env.NATS_URL );
  const sub = nc.subscribe('citadel.intel.>');
  console.log(`[intelligence] Listening on citadel.intel.*`);
  for await (const msg of sub) {
    const data = sc.decode(msg.data);
    console.log(`[intelligence] $msg.subject: $data`);
    // Route to handlers based on msg.subject
  }
}
