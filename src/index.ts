import  GuildClient  from '@citadel-guilds/sdk';

const guild = new GuildClient({
  name: 'intelligence',
  natsPrefix: 'citadel.intel',
  port: 8000,
});

guild.start();
