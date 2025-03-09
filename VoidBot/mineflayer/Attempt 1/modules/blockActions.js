// Block manipulation and placement functions

const Vec3 = require('vec3')
const { log } = require('./logger')
const { CONFIG } = require('./config')
const { equipBlackConcrete, equipPurpleConcrete, setupConcreteBlocks, selectBlackConcrete, selectPurpleConcrete } = require('./inventory')
const { navigateToPosition } = require('./navigation')

// Function to determine block color at specific coordinates
function getBlockColorAtCoords(x, z) {
  // Even sum means black, odd sum means magenta/purple
  return ((x + z) % 2 === 0) ? 'black' : 'magenta';
}

// Function to break the block below the bot
async function breakBlockBelow(bot) {
  // First look down to see the block better
  await lookDown(bot)
  
  // Get the block below the bot
  const pos = bot.entity.position.clone()
  pos.y -= 1 // Block directly below
  
  const blockBelow = bot.blockAt(pos)
  
  if (!blockBelow || blockBelow.name === 'air') {
    log('info', "There's no block below me to break")
    return
  }
  
  try {
    log('info', `Breaking ${blockBelow.name} below bot...`)
    await bot.dig(blockBelow)
    log('success', "Block broken successfully!")
  } catch (error) {
    log('error', `Error breaking block: ${error.message}`)
  }
}

// Function to make the bot look down
async function lookDown(bot) {
  log('info', "Looking down...")
  try {
    // Look down with pitch -PI/2 (negative value for looking down)
    await bot.look(bot.entity.yaw, -Math.PI/2, true)
    log('info', "Now looking down")
    
    // Wait a moment to ensure the look action completes
    await new Promise(resolve => setTimeout(resolve, 250))
    return true
  } catch (error) {
    log('error', `Error looking down: ${error.message}`)
    return false
  }
}

// Function to place a block at specific coordinates
async function placeBlockAt(bot, x, y, z, isBlack) {
  const blockType = isBlack ? 'black_concrete' : 'purple_concrete'
  const blockPos = new Vec3(x, y, z)
  
  // Check if there's already a block of the right type
  const existingBlock = bot.blockAt(blockPos)
  if (existingBlock && existingBlock.name === blockType) {
    log('info', `Block at (${x}, ${y}, ${z}) is already ${blockType}, skipping`)
    return true
  }
  
  try {
    // First look at the position
    await bot.lookAt(blockPos)
    
    // Try to find a reference block to place against
    const adjacentPositions = [
      new Vec3(x - 1, y, z),
      new Vec3(x + 1, y, z),
      new Vec3(x, y, z - 1),
      new Vec3(x, y, z + 1),
      new Vec3(x, y - 1, z)
    ]
    
    for (const refPos of adjacentPositions) {
      const refBlock = bot.blockAt(refPos)
      if (!refBlock || refBlock.name === 'air' || refBlock.material.isReplaceable) continue
      
      // Found a block to place against
      const faceVector = getFaceVector(refPos, blockPos)
      await bot.placeBlock(refBlock, faceVector)
      log('success', `Placed ${blockType} at (${x}, ${y}, ${z})`)
      return true
    }
    
    // If we can't find a suitable reference block, try to place on the block below first
    const botPos = bot.entity.position.clone()
    const distToBlock = Math.sqrt(
      Math.pow(botPos.x - x, 2) + 
      Math.pow(botPos.z - z, 2)
    )
    
    // If we're close enough, try to place directly
    if (distToBlock < 3) {
      // Look down
      await bot.look(bot.entity.yaw, Math.PI / 2, true)
      await new Promise(resolve => setTimeout(resolve, 250))
      
      // Get the block below where we want to place
      const blockBelow = bot.blockAt(new Vec3(x, y - 1, z))
      if (blockBelow && blockBelow.name !== 'air') {
        await bot.placeBlock(blockBelow, new Vec3(0, 1, 0))
        log('success', `Placed ${blockType} at (${x}, ${y}, ${z}) on block below`)
        return true
      }
    }
    
    log('error', `No suitable reference block found for placing at (${x}, ${y}, ${z})`)
    return false
  } catch (error) {
    log('error', `Error placing block at (${x}, ${y}, ${z}): ${error.message}`)
    return false
  }
}

// Helper function to get the face vector for block placement
function getFaceVector(referencePos, targetPos) {
  const dx = targetPos.x - referencePos.x
  const dy = targetPos.y - referencePos.y
  const dz = targetPos.z - referencePos.z
  
  // Return the unit vector in the direction of the greatest difference
  if (Math.abs(dx) >= Math.abs(dy) && Math.abs(dx) >= Math.abs(dz)) {
    return new Vec3(Math.sign(dx), 0, 0)
  } else if (Math.abs(dy) >= Math.abs(dx) && Math.abs(dy) >= Math.abs(dz)) {
    return new Vec3(0, Math.sign(dy), 0)
  } else {
    return new Vec3(0, 0, Math.sign(dz))
  }
}

// Function to create a void pattern (black-purple checkerboard)
async function createVoidPattern(bot, x1, z1, x2, z2) {
  if (!bot.creative) {
    throw new Error("Bot must be in creative mode for this operation")
  }
  
  // Sort coordinates to ensure x1,z1 is the minimum and x2,z2 is the maximum
  const minX = Math.min(x1, x2)
  const maxX = Math.max(x1, x2)
  const minZ = Math.min(z1, z2)
  const maxZ = Math.max(z1, z2)
  
  log('info', `Creating void pattern in area: (${minX}, ${minZ}) to (${maxX}, ${maxZ})`)
  
  // Get the current y coordinate where the bot is standing
  const y = Math.floor(bot.entity.position.y - 1)
  
  log('info', "Setting up concrete blocks in inventory...")
  
  // Setup concrete blocks with error handling
  try {
    await setupConcreteBlocks(bot)
  } catch (error) {
    log('warning', `Issue with setting up concrete blocks: ${error.message}`)
    log('info', "Will try to continue using quick bar slots directly")
    // We'll continue anyway and try to use whatever is in the slots
  }
  
  // Pre-select the first slot to ensure we have something in hand
  bot.setQuickBarSlot(0)
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // Process each position in the area
  let totalBlocks = 0
  let skippedBlocks = 0
  
  for (let x = minX; x <= maxX; x++) {
    for (let z = minZ; z <= maxZ; z++) {
      // Use the new function to determine block color
      const isBlack = getBlockColorAtCoords(x, z) === 'black';
      
      try {
        // First, move to a position near the target
        await navigateToPosition(bot, x, y + 1, z)
        
        // Equip the right concrete with simplified approach
        if (isBlack) {
          selectBlackConcrete(bot)
        } else {
          selectPurpleConcrete(bot)
        }
        
        // Give time for selection to take effect
        await new Promise(resolve => setTimeout(resolve, 250))
        
        // Look down at the target position
        await bot.look(bot.entity.yaw, -Math.PI/2, true)
        await new Promise(resolve => setTimeout(resolve, 250))
        
        // Place the block
        await placeBlockAt(bot, x, y, z, isBlack)
        
        totalBlocks++
        
        // Small delay to prevent server kick for too many actions
        await new Promise(resolve => setTimeout(resolve, CONFIG.blockPlaceDelay))
      } catch (error) {
        log('error', `Failed at position (${x}, ${z}): ${error.message}`)
      }
    }
    
    // Give progress update after each row
    log('info', `Completed row ${x} (${x-minX+1}/${maxX-minX+1}), placed ${totalBlocks} blocks so far`)
  }
  
  log('success', `Void pattern creation finished. Placed ${totalBlocks} blocks, skipped ${skippedBlocks} existing blocks.`)
}

module.exports = {
  breakBlockBelow,
  lookDown,
  placeBlockAt,
  createVoidPattern,
  getBlockColorAtCoords
}
