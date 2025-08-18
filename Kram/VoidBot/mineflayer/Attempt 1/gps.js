const mineflayer = require('mineflayer')
const { pathfinder, Movements } = require('mineflayer-pathfinder')
const readline = require('readline')

// Import from our modules
const { CONFIG } = require('./modules/config')
const { colors, log } = require('./modules/logger')
const { setupCommandHandler } = require('./modules/commands')
const { setupPathfindingMonitor } = require('./modules/navigation')
const { setupConcreteBlocks } = require('./modules/inventory') // Add this import

const bot = mineflayer.createBot({
  host: 'voidclan.de',
  username: 'VoidNet_Bot1', 
  auth: 'microsoft',
  chatLengthLimit: 256,
  hideErrors: false
})

bot.loadPlugin(pathfinder)

// Set up readline interface for console commands
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'bot> '
})

bot.once('spawn', () => {
  const defaultMove = new Movements(bot)
  
  // Notify console that bot has spawned first
  log('success', 'Bot spawned and ready to receive commands!')
  
  // Set up inventory with concrete blocks after a longer delay
  setupInventoryOnStart(bot);
  
  setTimeout(() => {
    log('info', 'Available commands: goto X Y Z, pos/position, verify X Z, stop, exit')
    log('info', 'Type "help" for a complete list of commands')
    rl.prompt()
  }, 1000)

  // Setup the pathfinding monitor
  const { startPathfindingMonitor, stopPathfindingMonitor } = setupPathfindingMonitor(bot, CONFIG.rangeGoal)
  
  // Setup command handlers with all dependencies
  setupCommandHandler(bot, rl, defaultMove, startPathfindingMonitor, stopPathfindingMonitor)
  
  // Add error handling for the bot
  bot.on('error', (err) => {
    log('error', `Bot encountered an error: ${err.message}`)
  })

  // Add debugging for kicked events
  bot.on('kicked', (reason, loggedIn) => {
    log('error', `Bot was kicked. Logged in: ${loggedIn}. Reason: ${reason}`)
  })

  // Handle end events
  bot.on('end', () => {
    log('info', 'Bot disconnected from server')
    rl.close() // Close readline interface when bot disconnects
  })
})

// Function to set up inventory on bot start
function setupInventoryOnStart(bot) {
  // Wait longer to ensure the bot is fully connected
  setTimeout(async () => {
    try {
      log('info', 'Setting up inventory with concrete blocks...')
      
      // Try the main setup function first
      await setupConcreteBlocks(bot)
      log('success', 'Inventory setup complete: Slot 1 = Black Concrete, Slot 2 = Purple Concrete')
      
      // Ensure black concrete is in hand
      setTimeout(() => {
        verifyAndSelectBlackConcrete(bot)
      }, 1000)
    } catch (error) {
      log('error', `Failed to set up inventory: ${error.message}`)
      
      // Attempt direct creative.setInventorySlot method as a last resort
      try {
        log('info', 'Trying to directly set inventory slots as a last resort...')
        
        if (bot.creative && typeof bot.creative.setInventorySlot === 'function') {
          // Try to find the item IDs from registry or network IDs
          const items = bot.registry ? bot.registry.itemsByName : null
          const blackId = items && items.black_concrete ? items.black_concrete.id : 251 // Fallback ID
          const purpleId = items && items.purple_concrete ? items.purple_concrete.id : 251 // Fallback ID
          
          // Set the items directly
          await bot.creative.setInventorySlot(36, { id: blackId, count: 64, metadata: items ? 0 : 15 })
          await new Promise(resolve => setTimeout(resolve, 500))
          await bot.creative.setInventorySlot(37, { id: purpleId, count: 64, metadata: items ? 0 : 10 })
          
          // Select the first slot
          bot.setQuickBarSlot(0)
          log('success', 'Successfully set inventory slots using direct method')
        } else {
          throw new Error('Creative API not available')
        }
      } catch (directError) {
        log('error', `Direct inventory setup failed: ${directError.message}`)
        log('warning', 'Could not set up inventory automatically')
        log('info', 'Please make sure the bot has black concrete in slot 1 and purple concrete in slot 2')
      }
    }
  }, 5000) // 5 second delay to ensure bot is ready
}

// Function to verify and select black concrete in hand
function verifyAndSelectBlackConcrete(bot) {
  log('info', 'Verifying black concrete is in hand...')
  
  // Check if currently holding black concrete
  if (bot.heldItem && bot.heldItem.name === 'black_concrete') {
    log('success', 'Black concrete already in hand')
    return
  }
  
  // Try to select it multiple times with increasing delays
  let attemptCount = 0
  const maxAttempts = 3
  
  function trySelectConcrete() {
    if (attemptCount < maxAttempts) {
      log('info', `Attempt ${attemptCount + 1} to select black concrete...`)
      
      // Try to select black concrete directly
      bot.setQuickBarSlot(0)
      
      // Wait and check if we got it
      setTimeout(() => {
        if (bot.heldItem && bot.heldItem.name === 'black_concrete') {
          log('success', 'Successfully selected black concrete in hand')
        } else {
          attemptCount++
          log('warning', `Black concrete not in hand. Held item: ${bot.heldItem ? bot.heldItem.name : 'nothing'}`)
          
          // Retry with increasing delay
          setTimeout(trySelectConcrete, 1000 * attemptCount)
        }
      }, 500)
    } else {
      log('error', 'Failed to select black concrete after multiple attempts')
      log('info', 'Please ensure black concrete is in the first hotbar slot')
    }
  }
  
  // Start the selection attempts
  trySelectConcrete()
}