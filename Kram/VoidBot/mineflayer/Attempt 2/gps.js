// This is an example that uses mineflayer-pathfinder to showcase how simple it is to walk to goals

const mineflayer = require('mineflayer')
const { pathfinder, Movements, goals: { GoalNear } } = require('mineflayer-pathfinder')

const bot = mineflayer.createBot({
  host: 'voidclan.de', // minecraft server ip
  username: 'VoidNet_Bot1', // username to join as if auth is `offline`, else a unique identifier for this account. Switch if you want to change accounts
  auth: 'microsoft' // for offline mode servers, you can set this to 'offline'
  // port: 25565,              // set if you need a port that isn't 25565
  // version: false,           // only set if you need a specific version or snapshot (ie: "1.8.9" or "1.16.5"), otherwise it's set automatically
  // password: '12345678'      // set if you want to use password-based auth (may be unreliable). If specified, the `username` must be an email
})


bot.loadPlugin(pathfinder)

bot.once('spawn', () => {
  
})