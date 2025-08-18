// This is an example that uses mineflayer-pathfinder to showcase how simple it is to walk to goals

const mineflayer = require('mineflayer')
const { pathfinder, Movements, goals: { GoalNear } } = require('mineflayer-pathfinder')
const readline = require('readline') // Add readline for console input

// Command configuration
const CONFIG = {
  rangeGoal: 1  // Get within this radius of the target
}

// Set up console colors for better logging
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
  magenta: "\x1b[35m",
}

// Improved logging function
function log(type, message) {
  const timestamp = new Date().toLocaleTimeString()
  switch (type) {
    case 'info':
      console.log(`${colors.cyan}[${timestamp}] ${colors.bright}[INFO] ${colors.reset}${message}`)
      break
    case 'success':
      console.log(`${colors.green}[${timestamp}] ${colors.bright}[SUCCESS] ${colors.reset}${message}`)
      break
    case 'error':
      console.log(`${colors.red}[${timestamp}] ${colors.bright}[ERROR] ${colors.reset}${message}`)
      break
    case 'command':
      console.log(`${colors.yellow}[${timestamp}] ${colors.bright}[COMMAND] ${colors.reset}${message}`)
      break
    case 'chat':
      console.log(`${colors.magenta}[${timestamp}] ${colors.bright}[CHAT] ${colors.reset}${message}`)
      break
    default:
      console.log(`${colors.dim}[${timestamp}] ${message}${colors.reset}`)
  }
}

const bot = mineflayer.createBot({
    host: 'voidclan.de', // minecraft server ip
    username: 'VoidNet_Bot1', // username to join as if auth is `offline`, else a unique identifier for this account
    auth: 'microsoft', // for offline mode servers, you can set this to 'offline'
    // port: 25565,              // set if you need a port that isn't 25565
    // version: false,           // only set if you need a specific version or snapshot
    // password: '12345678'      // set if you want to use password-based auth
    chatLengthLimit: 256, // Fix the chat validation error by setting a length limit
    hideErrors: false // Display all errors for debugging
  })

// Using the config value instead of a constant
const RANGE_GOAL = CONFIG.rangeGoal 

bot.loadPlugin(pathfinder)

// Set up readline interface for console commands
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'bot> '
})

bot.once('spawn', () => {
  const defaultMove = new Movements(bot)
  
  // Notify console when bot spawns
  setTimeout(() => {
    log('success', 'Bot spawned and ready to receive commands!')
    log('info', 'Available commands: goto X Y Z, pos/position, prep, stop, exit')
    log('info', 'The "come" command is now "goto <x> <y> <z>" with specific coordinates')
    rl.prompt()
  }, 1000)

  // Add event listener for goal reached
  bot.pathfinder.on('goal_reached', () => {
    log('success', 'Goal reached! Bot has arrived at the destination.')
  })

  // Handle console commands
  rl.on('line', (line) => {
    const commandMessage = line.trim()
    log('command', `Received console command: ${commandMessage}`)
    
    // Process the command
    processCommand(commandMessage)
    rl.prompt()
  })
  
  // Main command processing function - now only handles console commands
  function processCommand(commandMessage) {
    // Handle the goto X Y Z command
    const gotoMatch = commandMessage.match(/^goto\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)$/i)
    if (gotoMatch) {
      const x = parseFloat(gotoMatch[1])
      const y = parseFloat(gotoMatch[2])
      const z = parseFloat(gotoMatch[3])
      
      log('info', `Setting path to coordinates: X: ${x}, Y: ${y}, Z: ${z}`)
      
      try {
        bot.pathfinder.setMovements(defaultMove)
        bot.pathfinder.setGoal(new GoalNear(x, y, z, RANGE_GOAL))
        log('success', 'Path calculated successfully')
      } catch (error) {
        log('error', `Failed to set path: ${error.message}`)
      }
      return
    }

    // Handle the prep command
    if (commandMessage === 'prep') {
      log('info', 'Preparing to modify the ground...')
      
      // Find and equip black concrete
      equipBlackConcrete()
        .then(() => {
          log('success', 'Black concrete equipped')
          // After equipping, break block below
          return breakBlockBelow();
        })
        .then(() => {
          log('success', 'Ground preparation completed')
        })
        .catch((error) => {
          log('error', `Failed prep: ${error.message}`)
        });
      return;
    }

    // Handle the position command
    if (commandMessage === 'pos' || commandMessage === 'position') {
      try {
        const pos = bot.entity.position;
        // Round coordinates to 2 decimal places for readability
        const x = Math.round(pos.x * 100) / 100;
        const y = Math.round(pos.y * 100) / 100;
        const z = Math.round(pos.z * 100) / 100;
        
        const positionMessage = `Current position: X: ${x}, Y: ${y}, Z: ${z}`;
        log('info', positionMessage);
      } catch (error) {
        log('error', `Error reporting position: ${error.message}`);
      }
      return;
    }

    // Handle the stop command - stop moving
    if (commandMessage === 'stop') {
      try {
        bot.pathfinder.setGoal(null)
        log('success', 'Movement stopped')
      } catch (error) {
        log('error', `Error stopping movement: ${error.message}`)
      }
      return
    }

    // Handle the exit command - disconnect from server
    if (commandMessage === 'exit') {
      log('info', "Exit command received, disconnecting bot")
      
      // Set a timeout to ensure everything finishes before disconnecting
      setTimeout(() => {
        bot.quit()
      }, 500)
      return
    }

    // Handle the help command
    if (commandMessage === 'help') {
      log('info', '=== Available Commands ===')
      log('info', 'goto X Y Z - Navigate to specific coordinates')
      log('info', 'pos/position - Show current bot position')
      log('info', 'prep - Prepare ground (equip black concrete and break block below)')
      log('info', 'stop - Stop all movement')
      log('info', 'help - Show this help message')
      log('info', 'exit - Disconnect bot from server')
      return
    }

    // Alternative implementation for goto command as fallback
    if (commandMessage.startsWith('goto ')) {
      const parts = commandMessage.split(' ').filter(Boolean)
      if (parts.length >= 4) {
        const x = parseInt(parts[1])
        const y = parseInt(parts[2])
        const z = parseInt(parts[3])
        
        if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
          log('info', `Using fallback method. Coordinates: ${x}, ${y}, ${z}`)
          
          try {
            bot.pathfinder.setMovements(defaultMove)
            bot.pathfinder.setGoal(new GoalNear(x, y, z, RANGE_GOAL))
            log('success', 'Path calculated successfully using fallback method')
          } catch (error) {
            log('error', `Error in fallback pathfinding: ${error.message}`)
          }
          return
        }
      }
      
      log('error', "Invalid goto format. Use goto X Y Z with numeric coordinates.")
    }

    // If no command matched
    log('info', `Unknown command: '${commandMessage}'. Type 'help' for a list of commands.`)
  }
  
  // Function to find and equip black concrete
  async function equipBlackConcrete() {
    try {
      // Check if creative mode is available
      if (!bot.creative) {
        log('error', 'Creative mode not available for getting black concrete')
        throw new Error("Creative mode not available");
      }
      
      log('info', "Attempting to get black concrete from creative inventory...");
      
      // For newer Minecraft versions, we need to use the proper item name
      const Item = require('prismarine-item')(bot.version);
      
      try {
        // Try modern approach first
        const blackConcrete = new Item(bot.registry.itemsByName.black_concrete.id, 1, 0);
        log('info', "Created black concrete item:", blackConcrete);
        
        // Add black concrete to the bot's inventory
        await bot.creative.setInventorySlot(36, blackConcrete);
        log('info', "Added black concrete to inventory slot 36");
      } catch (itemError) {
        log('error', "Error with modern item method:", itemError);
        log('info', "Trying fallback method...");
        
        // Fallback for different server versions
        try {
          // Alternative approach for older versions
          await bot.creative.setInventorySlot(36, {
            id: bot.registry.itemsByName.black_concrete?.id || 251,
            count: 64,
            metadata: 0 // Modern versions don't use metadata like older versions did
          });
          log('info', "Used fallback method to set inventory slot");
        } catch (fallbackError) {
          log('error', "Fallback method also failed:", fallbackError);
          throw new Error("Could not add black concrete to inventory");
        }
      }
      
      // Wait a moment for the inventory to update
      log('info', "Waiting for inventory update...");
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Try to hold the item using a different approach
      try {
        // Find the black concrete in inventory after setting the slot
        log('info', "Checking inventory for black concrete...");
        const items = bot.inventory.items();
        log('info', `Found ${items.length} items in inventory`);
        
        // Find the black concrete item
        const blackConcreteItem = items.find(item => 
          item && (item.name === 'black_concrete' || 
                  (item.name === 'concrete' && item.metadata === 15))
        );
        
        if (blackConcreteItem) {
          log('info', "Found black concrete in inventory:", blackConcreteItem);
          // Hold the item directly
          await bot.equip(blackConcreteItem, 'hand');
        } else {
          // Alternative approach - directly hold the item in slot 36
          log('info', "Using direct slot approach to equip...");
          bot.setQuickBarSlot(0); // Select the first hotbar slot (0-based index)
        }
        
        return true;
      } catch (equipError) {
        log('error', "Error during equip:", equipError);
        
        // Last resort approach
        log('info', "Trying last resort approach...");
        bot.setQuickBarSlot(0);
        return true;
      }
    } catch (error) {
      log('error', 'Error getting black concrete (full details):', error);
      throw error;
    }
  }
  
  // Function to break the block below the bot
  async function breakBlockBelow() {
    // First look down to see the block better
    await lookDown();
    
    // Get the block below the bot
    const pos = bot.entity.position.clone();
    pos.y -= 1; // Block directly below
    
    const blockBelow = bot.blockAt(pos);
    
    if (!blockBelow || blockBelow.name === 'air') {
      log('info', "There's no block below me to break");
      return;
    }
    
    try {
      log('info', `Breaking ${blockBelow.name} below bot...`);
      await bot.dig(blockBelow);
      log('success', "Block broken successfully!");
    } catch (error) {
      log('error', `Error breaking block: ${error.message}`);
    }
  }
  
  // Function to make the bot look down
  async function lookDown() {
    log('info', "Looking down...");
    try {
      // Look down with pitch -PI/2 (negative value for looking down)
      await bot.look(bot.entity.yaw, -Math.PI/2, true);
      log('info', "Now looking down");
      
      // Wait a moment to ensure the look action completes
      await new Promise(resolve => setTimeout(resolve, 250));
      return true;
    } catch (error) {
      log('error', `Error looking down: ${error.message}`);
      return false;
    }
  }
})

// Add error handling for the bot
bot.on('error', (err) => {
  log('error', `Bot encountered an error: ${err.message}`);
});

// Add debugging for kicked events
bot.on('kicked', (reason, loggedIn) => {
  log('error', `Bot was kicked. Logged in: ${loggedIn}. Reason: ${reason}`);
});

// Handle end events
bot.on('end', () => {
  log('info', 'Bot disconnected from server');
  rl.close(); // Close readline interface when bot disconnects
});