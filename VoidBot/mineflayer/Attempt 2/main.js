const mineflayer = require('mineflayer')
const Item = require('prismarine-item')('1.21.4')

const bot = mineflayer.createBot({
  host: 'voidclan.de', // minecraft server ip
  username: 'VoidNet_Bot1', // username to join as if auth is `offline`, else a unique identifier for this account. Switch if you want to change accounts
  auth: 'microsoft' // for offline mode servers, you can set this to 'offline'
  // port: 25565,              // set if you need a port that isn't 25565
  // version: false,           // only set if you need a specific version or snapshot (ie: "1.8.9" or "1.16.5"), otherwise it's set automatically
  // password: '12345678'      // set if you want to use password-based auth (may be unreliable). If specified, the `username` must be an email
})

bot.once('spawn', () => {
  // Log bot spawn
  console.log('Bot spawned and ready to receive commands!')

  const blackConcrete = new Item(251, 15, 1)
  bot.creative.setInventorySlot(36, blackConcrete) // 36 is the first hotbar slot
  
  // Wait a short time to ensure inventory updates, then select the first slot
  setTimeout(() => {
    bot.setQuickBarSlot(0) // Select the first slot (index 0)
    console.log('Black concrete selected in first hotbar slot')
  }, 500)
})

// Log errors and kick reasons:
bot.on('kicked', console.log)
bot.on('error', console.log)