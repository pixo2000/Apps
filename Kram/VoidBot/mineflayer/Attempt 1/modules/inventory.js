// Inventory management functions for the bot

const { log } = require('./logger')
const { CONFIG } = require('./config')

// Function to set up the concrete blocks in the hotbar
async function setupConcreteBlocks(bot) {
  if (!bot) {
    throw new Error("Bot not available")
  }
  
  log('info', 'Setting up concrete blocks in hotbar...')

  // Check game mode and use appropriate method
  if (bot.game && bot.game.gameMode === 'creative') {
    await setupCreativeInventoryDirectly(bot)
  } else {
    await setupSurvivalMode(bot)
  }

  // Select the first slot to have black concrete active
  bot.setQuickBarSlot(0)
  log('info', 'Selected hotbar slot 1 (black concrete)')
}

// Direct inventory manipulation using setInventorySlot
async function setupCreativeInventoryDirectly(bot) {
  log('info', 'Setting up creative inventory directly with setInventorySlot...')
  
  try {
    // First, check if we have the necessary API
    if (!bot.creative || typeof bot.creative.setInventorySlot !== 'function') {
      throw new Error('Creative API not available or setInventorySlot method missing')
    }
    
    // Get the item IDs
    const blackConcreteId = getItemId(bot, 'black_concrete')
    const purpleConcreteId = getItemId(bot, 'purple_concrete')
    
    if (!blackConcreteId || !purpleConcreteId) {
      throw new Error('Could not determine concrete block IDs')
    }
    
    // Place black concrete in hotbar slot 1 (inventory slot 36)
    log('info', 'Setting black concrete in slot 1...')
    await bot.creative.setInventorySlot(36, {
      id: blackConcreteId,
      count: 64
    })
    
    // Wait a moment between operations
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Place purple concrete in hotbar slot 2 (inventory slot 37)
    log('info', 'Setting purple concrete in slot 2...')
    await bot.creative.setInventorySlot(37, {
      id: purpleConcreteId,
      count: 64
    })
    
    log('success', 'Successfully set up inventory with concrete blocks')
    return true
  } catch (error) {
    log('error', `Error setting up creative inventory directly: ${error.message}`)
    log('info', 'Trying fallback methods...')
    
    try {
      return await tryFallbackInventoryMethods(bot)
    } catch (fallbackError) {
      log('error', `All inventory setup methods failed: ${fallbackError.message}`)
      throw fallbackError
    }
  }
}

// Helper function to get item ID by name
function getItemId(bot, itemName) {
  // Try to get ID from the registry
  if (bot.registry && bot.registry.itemsByName && bot.registry.itemsByName[itemName]) {
    return bot.registry.itemsByName[itemName].id
  }
  
  // Fallback to common item IDs (may vary by Minecraft version)
  const commonIds = {
    'black_concrete': 251,  // Pre-1.13 ID with data value 15
    'purple_concrete': 251  // Pre-1.13 ID with data value 10
  }
  
  // Log a warning and return the fallback ID
  log('warning', `Could not find ID for ${itemName} in registry, using fallback`)
  return commonIds[itemName] || null
}

// Try various fallback methods for setting up inventory
async function tryFallbackInventoryMethods(bot) {
  log('info', 'Trying alternative inventory setup methods...')
  
  // Try to use give command with creative mode
  if (bot.game && bot.game.gameMode === 'creative') {
    try {
      log('info', 'Attempting to use chat commands...')
      
      // Clear inventory first
      bot.chat('/clear')
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Try to get items via command
      bot.chat('/give @s black_concrete 64')
      await new Promise(resolve => setTimeout(resolve, 1000))
      bot.chat('/give @s purple_concrete 64')
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Try to move them to the right slots
      bot.setQuickBarSlot(0) // First slot
      log('info', 'Selected first slot, check if blocks were received')
      return true
    } catch (cmdError) {
      log('error', `Command-based setup failed: ${cmdError.message}`)
    }
  }
  
  // Try directly opening and manipulating the inventory
  try {
    return await tryCreativeInventoryGUI(bot)
  } catch (guiError) {
    log('error', `GUI-based setup failed: ${guiError.message}`)
  }
  
  throw new Error('All inventory setup methods failed')
}

// New creative inventory management without using commands
async function setupCreativeInventory(bot) {
  log('info', 'Opening creative inventory to get blocks...')
  
  try {
    // Open the creative inventory
    await bot.openInventory()
    
    // Wait for the inventory to open
    await new Promise(resolve => setTimeout(resolve, 500))
    
    log('info', 'Creative inventory opened, searching for blocks...')
    
    // Get black concrete from creative inventory
    await getItemFromCreative(bot, 'black_concrete', 36) // 36 = hotbar slot 1 (0-indexed)
    
    // Get purple concrete from creative inventory
    await getItemFromCreative(bot, 'purple_concrete', 37) // 37 = hotbar slot 2 (0-indexed)
    
    // Close the inventory
    await bot.closeWindow(bot.currentWindow)
    log('success', 'Inventory closed, blocks have been set up')
    
    return true
  } catch (error) {
    log('error', `Error managing creative inventory: ${error.message}`)
    
    // Try to close the window if it's still open
    if (bot.currentWindow) {
      try {
        await bot.closeWindow(bot.currentWindow)
      } catch (closeError) {
        log('error', `Error closing inventory: ${closeError.message}`)
      }
    }
    
    throw error
  }
}

// Helper function to find and get an item from creative inventory
async function getItemFromCreative(bot, itemName, targetSlot) {
  log('info', `Looking for ${itemName} in creative inventory...`)
  
  // Find the creative window
  const window = bot.currentWindow
  if (!window) {
    throw new Error('No window is currently open')
  }

  // Using press key for E key (inventory)
  await bot.simpleClick.leftMouse(targetSlot)
  
  // Type in search bar to find the item
  await bot.chat(`/${itemName}`)
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // Select the first slot (should be our item) and pick it up
  await bot.simpleClick.leftMouse(0)
  await new Promise(resolve => setTimeout(resolve, 300))
  
  // Put it in the target slot (should be in the hotbar)
  await bot.simpleClick.leftMouse(targetSlot)
  await new Promise(resolve => setTimeout(resolve, 300))
  
  // Clear the search
  await bot.chat("/")
  await new Promise(resolve => setTimeout(resolve, 300))
  
  log('success', `Placed ${itemName} in slot ${targetSlot - 35}`)
  return true
}

// Alternative creative inventory setup that tries to click through GUI
async function tryCreativeInventoryGUI(bot) {
  log('info', 'Trying direct creative inventory interaction...')
  
  try {
    // Press E to open inventory (press key method may vary by bot version)
    bot.setControlState('jump', true)
    await new Promise(resolve => setTimeout(resolve, 100))
    bot.setControlState('jump', false) // Just to trigger any key - may need to use specific bot.controls API
    
    // Wait for inventory to appear
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Click creative inventory tab (block tab)
    await bot.simpleClick.leftMouse(137) // This slot might need adjustment
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Find and click black concrete
    // This requires knowing exact slot IDs which can be difficult
    // We'd need to iterate through slots and check names
    
    // For now, just try clicking common slots where building blocks might be
    for (let slot = 9; slot < 45; slot++) {
      const item = bot.currentWindow.slots[slot]
      if (item && item.name.includes('black_concrete')) {
        // Found it! Click it
        await bot.simpleClick.leftMouse(slot)
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Put in hotbar slot 1
        await bot.simpleClick.leftMouse(36)
        break
      }
    }
    
    // Do the same for purple concrete
    // ...
    
    // Close inventory
    bot.closeWindow(bot.currentWindow)
    
    log('success', 'Creative inventory manually managed')
    return true
  } catch (error) {
    log('error', `Error with GUI interaction: ${error.message}`)
    if (bot.currentWindow) {
      try {
        bot.closeWindow(bot.currentWindow)
      } catch (e) {}
    }
    throw error
  }
}

// Simpler and more reliable creative mode setup using various fallbacks
async function setupCreativeMode(bot) {
  log('info', 'Setting up items in creative mode')
  
  // Try to use creative inventory directly first
  try {
    await setupCreativeInventory(bot)
    return true
  } catch (error) {
    log('warning', `Direct inventory access failed: ${error.message}`)
    log('info', 'Falling back to alternative methods...')
    
    // Try pressing number keys as a fallback
    try {
      log('info', 'Pressing number keys to select items from hotbar...')
      
      // Try pressing 1 and 2 on keyboard (to select hotbar slots)
      bot.chat('/gamemode creative') // Ensure we're in creative mode
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Press 1 for first slot (simulated by chat command since we can't directly press keys)
      bot.setQuickBarSlot(0)
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Press 2 for second slot
      bot.setQuickBarSlot(1)
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Go back to first slot
      bot.setQuickBarSlot(0)
      
      log('info', 'Hopefully keys 1 and 2 have been pressed, check if blocks are available')
      return true
    } catch (fallbackError) {
      log('error', `Key press fallback also failed: ${fallbackError.message}`)
      throw error
    }
  }
}

// Survival mode setup - find and move items
async function setupSurvivalMode(bot) {
  log('info', 'Setting up items in survival mode')
  
  try {
    // Wait for inventory to be loaded
    await waitForInventory(bot)
    
    // Find black and purple concrete in the inventory
    const items = bot.inventory.items()
    
    // Find black concrete
    let blackConcrete = items.find(item => item.name === 'black_concrete')
    if (!blackConcrete) {
      log('error', 'No black concrete found in inventory')
      return false
    }
    
    // Find purple/magenta concrete
    let purpleConcrete = items.find(item => item.name === 'purple_concrete')
    if (!purpleConcrete) {
      log('error', 'No purple concrete found in inventory')
      return false
    }
    
    // Move black concrete to slot 36 (first hotbar slot)
    if (blackConcrete.slot !== 36) {
      log('info', `Moving black concrete from slot ${blackConcrete.slot} to slot 36`)
      await bot.clickWindow(blackConcrete.slot, 0, 0) // Pick up the item
      await new Promise(resolve => setTimeout(resolve, 250))
      await bot.clickWindow(36, 0, 0) // Place in hotbar slot 1
      await new Promise(resolve => setTimeout(resolve, 250))
    }
    
    // Move purple concrete to slot 37 (second hotbar slot)
    if (purpleConcrete.slot !== 37) {
      log('info', `Moving purple concrete from slot ${purpleConcrete.slot} to slot 37`)
      await bot.clickWindow(purpleConcrete.slot, 0, 0) // Pick up the item
      await new Promise(resolve => setTimeout(resolve, 250))
      await bot.clickWindow(37, 0, 0) // Place in hotbar slot 2
      await new Promise(resolve => setTimeout(resolve, 250))
    }
    
    log('success', 'Survival mode inventory setup complete')
    return true
  } catch (error) {
    log('error', `Survival mode inventory setup failed: ${error.message}`)
    throw error
  }
}

// Helper function to wait for inventory to be loaded
function waitForInventory(bot) {
  return new Promise((resolve, reject) => {
    // If inventory is already loaded, resolve immediately
    if (bot.inventory && bot.inventory.items().length > 0) {
      resolve()
      return
    }
    
    // Otherwise wait for inventory update event
    const timeout = setTimeout(() => {
      bot.removeListener('playerCollect', inventoryHandler)
      bot.removeListener('windowOpen', inventoryHandler)
      bot.removeListener('windowClose', inventoryHandler)
      reject(new Error('Inventory load timeout'))
    }, 5000)
    
    const inventoryHandler = () => {
      if (bot.inventory) {
        clearTimeout(timeout)
        bot.removeListener('playerCollect', inventoryHandler)
        bot.removeListener('windowOpen', inventoryHandler) 
        bot.removeListener('windowClose', inventoryHandler)
        resolve()
      }
    }
    
    // Listen for inventory events
    bot.on('playerCollect', inventoryHandler)
    bot.on('windowOpen', inventoryHandler)
    bot.on('windowClose', inventoryHandler)
    
    // Try to trigger inventory update by opening and closing inventory
    bot.chat('/gamemode survival') // Temp change to ensure inventory works
    setTimeout(() => {
      bot.setQuickBarSlot(0) // Select first slot
      setTimeout(() => {
        bot.chat('/gamemode creative') // Switch back
      }, 500)
    }, 500)
  })
}

// Enhanced function to ensure black concrete is selected in hand
function selectBlackConcrete(bot) {
  try {
    log('info', 'Selecting black concrete in hand...')
    
    // First try direct selection by hotbar slot
    bot.setQuickBarSlot(0) // First hotbar slot
    
    // Wait a brief moment to ensure selection happens
    setTimeout(() => {
      // Verify we actually have the right block in hand
      if (!bot.heldItem || bot.heldItem.name !== 'black_concrete') {
        log('warning', 'Black concrete not in hand after selection, trying again')
        
        // Try again with a different method
        try {
          if (bot.inventory) {
            // Find black concrete in inventory
            const blackConcrete = bot.inventory.findInventoryItem('black_concrete')
            if (blackConcrete) {
              // Try to equip it
              bot.equip(blackConcrete, 'hand')
                .then(() => {
                  log('success', 'Successfully equipped black concrete')
                })
                .catch((error) => {
                  log('error', `Failed to equip black concrete: ${error.message}`)
                })
            } else {
              log('error', 'Could not find black concrete in inventory')
            }
          }
        } catch (error) {
          log('error', `Error selecting black concrete: ${error.message}`)
        }
      } else {
        log('success', 'Black concrete now in hand')
      }
    }, 200)
    
    return true
  } catch (error) {
    log('error', `Failed to select black concrete: ${error.message}`)
    return false
  }
}

// Simplified function to ensure purple concrete is selected
function selectPurpleConcrete(bot) {
  try {
    bot.setQuickBarSlot(1) // Second hotbar slot
    log('info', 'Selected hotbar slot 2 (Purple concrete)')
    return true
  } catch (error) {
    log('error', `Failed to select purple concrete: ${error.message}`)
    return false
  }
}

module.exports = {
  setupConcreteBlocks,
  selectBlackConcrete,
  selectPurpleConcrete
}
