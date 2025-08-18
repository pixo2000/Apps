// Command processing module for handling user input

const { goals: { GoalNear } } = require('mineflayer-pathfinder')
const Vec3 = require('vec3')
const { log } = require('./logger')
const { CONFIG } = require('./config')
const { getBlockColorAtCoords, placeBlockAt } = require('./blockActions')
const { selectBlackConcrete, selectPurpleConcrete } = require('./inventory')

function setupCommandHandler(bot, rl, defaultMove, startPathfindingMonitor, stopPathfindingMonitor) {
  // Handle console commands
  rl.on('line', (line) => {
    const commandMessage = line.trim()
    log('command', `Received console command: ${commandMessage}`)
    
    // Process the command
    processCommand(commandMessage)
    rl.prompt()
  })
  
  // Main command processing function - now only handles console commands
  async function processCommand(commandMessage) {
    // Handle the goto X Y Z command
    const gotoMatch = commandMessage.match(/^goto\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)$/i)
    if (gotoMatch) {
      const x = parseFloat(gotoMatch[1])
      const y = parseFloat(gotoMatch[2])
      const z = parseFloat(gotoMatch[3])
      
      log('info', `Setting path to coordinates: X: ${x}, Y: ${y}, Z: ${z}`)
      
      try {
        bot.pathfinder.setMovements(defaultMove)
        bot.pathfinder.setGoal(new GoalNear(x, y, z, CONFIG.rangeGoal))
        // Start monitoring pathfinding progress
        startPathfindingMonitor()
        log('success', 'Path calculated successfully')
      } catch (error) {
        log('error', `Failed to set path: ${error.message}`)
      }
      return
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

    // Handle the blockcolor command to check color at coordinates
    const blockColorMatch = commandMessage.match(/^blockcolor\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)$/i)
    if (blockColorMatch) {
      const x = parseInt(blockColorMatch[1])
      const z = parseInt(blockColorMatch[2])
      
      if (!isNaN(x) && !isNaN(z)) {
        const color = getBlockColorAtCoords(x, z)
        log('info', `Block at coordinates X: ${x}, Z: ${z} should be ${color} concrete`)
      } else {
        log('error', "Invalid coordinates. Please use numeric values.")
      }
      return
    }

    // Handle the verify command to check and fix a block
    const verifyMatch = commandMessage.match(/^verify\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)$/i)
    if (verifyMatch) {
      const x = parseInt(verifyMatch[1])
      const z = parseInt(verifyMatch[2])
      
      if (!isNaN(x) && !isNaN(z)) {
        log('info', `Verifying block at X: ${x}, Z: ${z}`)
        
        // Get the correct color that should be at these coordinates
        const correctColor = getBlockColorAtCoords(x, z)
        log('info', `Block at X: ${x}, Z: ${z} should be ${correctColor} concrete`)
        
        // Get the current Y position where the bot is standing
        const y = Math.floor(bot.entity.position.y - 1)
        
        // Set pathfinder to navigate to the block
        try {
          bot.pathfinder.setMovements(defaultMove)
          bot.pathfinder.setGoal(new GoalNear(x, y + 1, z, CONFIG.rangeGoal))
          startPathfindingMonitor()
          
          // Set up a listener to check the block when we arrive
          const checkBlock = () => {
            const blockPos = new Vec3(x, y, z)
            const block = bot.blockAt(blockPos)
            
            if (!block || block.name === 'air') {
              log('info', `No block found at position. Placing ${correctColor} concrete...`)
              const isBlack = correctColor === 'black'
              
              // Use the simplified select functions
              if (isBlack) {
                selectBlackConcrete(bot)
              } else {
                selectPurpleConcrete(bot)
              }
              
              // Give time for selection to take effect
              setTimeout(async () => {
                try {
                  await placeBlockAt(bot, x, y, z, isBlack)
                  log('success', `Placed ${correctColor} concrete at X: ${x}, Z: ${z}`)
                } catch (error) {
                  log('error', `Failed to place block: ${error.message}`)
                }
              }, 500)
            } 
            else if ((correctColor === 'black' && block.name !== 'black_concrete') || 
                     (correctColor === 'magenta' && block.name !== 'purple_concrete')) {
              log('info', `Incorrect block found: ${block.name}. Should be ${correctColor} concrete. Fixing...`)
              const isBlack = correctColor === 'black'
              
              // First break the incorrect block
              try {
                log('info', 'Breaking incorrect block...')
                bot.dig(block)
                
                // Wait for the block to break and then place the correct one
                setTimeout(async () => {
                  if (isBlack) {
                    selectBlackConcrete(bot)
                  } else {
                    selectPurpleConcrete(bot)
                  }
                  await placeBlockAt(bot, x, y, z, isBlack)
                  log('success', `Replaced with ${correctColor} concrete at X: ${x}, Z: ${z}`)
                }, 1000)
              } catch (error) {
                log('error', `Failed to fix block: ${error.message}`)
              }
            } 
            else {
              log('success', `Block at X: ${x}, Z: ${z} is correct: ${block.name}`)
            }
            
            // Remove this one-time listener
            bot.removeListener('goal_reached', checkBlock)
          }
          
          // Listen for when we reach the destination
          bot.once('goal_reached', checkBlock)
          
          // Also set a timeout in case the event doesn't fire
          setTimeout(() => {
            if (bot.pathfinder.isMoving()) {
              log('info', 'Still moving to target...')
            } else if (bot.entity.position.distanceTo(new Vec3(x, y + 1, z)) <= CONFIG.rangeGoal + 1) {
              log('info', 'Near target but goal_reached event didn\'t fire. Checking block anyway...')
              checkBlock()
            } else {
              log('error', 'Failed to reach the target position')
              bot.removeListener('goal_reached', checkBlock)
            }
          }, 10000)
        } catch (error) {
          log('error', `Failed to set path: ${error.message}`)
        }
      } else {
        log('error', "Invalid coordinates. Please use numeric values.")
      }
      return
    }

    // Handle the stop command - stop moving
    if (commandMessage === 'stop') {
      try {
        bot.pathfinder.setGoal(null)
        stopPathfindingMonitor() // Also stop the monitor
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

    // Handle the inventory setup command
    if (commandMessage === 'setup' || commandMessage === 'setupinv') {
      log('info', 'Setting up inventory with concrete blocks...')
      
      try {
        // Try direct setInventorySlot first
        if (bot.creative && typeof bot.creative.setInventorySlot === 'function') {
          // Try to find the item IDs
          const blackId = bot.registry?.itemsByName?.black_concrete?.id || 251
          const purpleId = bot.registry?.itemsByName?.purple_concrete?.id || 251
          
          // Set the slots directly
          await bot.creative.setInventorySlot(36, { id: blackId, count: 64 })
          await new Promise(resolve => setTimeout(resolve, 500))
          await bot.creative.setInventorySlot(37, { id: purpleId, count: 64 })
          
          // Select the first slot
          bot.setQuickBarSlot(0)
          log('success', 'Inventory setup complete using direct method')
        } else {
          log('error', 'Creative API not available, trying fallback')
          // Fall back to the previous implementations
        }
      } catch (error) {
        log('error', `Failed to set up inventory: ${error.message}`)
      }
      return
    }

    // Handle the select black concrete command
    if (commandMessage === 'black' || commandMessage === 'selectblack') {
      log('info', 'Manually selecting black concrete...')
      
      try {
        // Try to select black concrete in hand
        selectBlackConcrete(bot)
        
        // After a moment, check if the selection worked
        setTimeout(() => {
          if (bot.heldItem && bot.heldItem.name === 'black_concrete') {
            log('success', 'Black concrete is now in hand')
          } else {
            log('error', `Selection failed. Held item: ${bot.heldItem ? bot.heldItem.name : 'nothing'}`)
            log('info', 'Trying fallback method...')
            
            // Try to select slot directly
            bot.setQuickBarSlot(0)
            log('info', 'Selected first hotbar slot directly')
          }
        }, 500)
      } catch (error) {
        log('error', `Failed to select black concrete: ${error.message}`)
      }
      return
    }

    // Handle the select purple concrete command
    if (commandMessage === 'purple' || commandMessage === 'selectpurple') {
      log('info', 'Manually selecting purple concrete...')
      
      try {
        // Try to select purple concrete in hand
        selectPurpleConcrete(bot)
        
        // After a moment, check if the selection worked
        setTimeout(() => {
          if (bot.heldItem && bot.heldItem.name === 'purple_concrete') {
            log('success', 'Purple concrete is now in hand')
          } else {
            log('error', `Selection failed. Held item: ${bot.heldItem ? bot.heldItem.name : 'nothing'}`)
            log('info', 'Trying fallback method...')
            
            // Try to select slot directly
            bot.setQuickBarSlot(1)
            log('info', 'Selected second hotbar slot directly')
          }
        }, 500)
      } catch (error) {
        log('error', `Failed to select purple concrete: ${error.message}`)
      }
      return
    }

    // Handle the help command
    if (commandMessage === 'help') {
      log('info', '=== Available Commands ===')
      log('info', 'goto X Y Z - Navigate to specific coordinates')
      log('info', 'pos/position - Show current bot position')
      log('info', 'blockcolor X Z - Check which color block (black/magenta) should be at coordinates')
      log('info', 'verify X Z - Check if block at X,Z has correct color and fix if needed')
      log('info', 'setup/setupinv - Try to get concrete blocks in the hotbar')
      log('info', 'black/selectblack - Select black concrete in hand')
      log('info', 'purple/selectpurple - Select purple concrete in hand')
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
            bot.pathfinder.setGoal(new GoalNear(x, y, z, CONFIG.rangeGoal))
            // Start monitoring pathfinding progress
            startPathfindingMonitor()
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
}

module.exports = { setupCommandHandler }
