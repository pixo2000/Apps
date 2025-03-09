// Navigation and pathfinding utilities

const Vec3 = require('vec3')
const { goals: { GoalNear } } = require('mineflayer-pathfinder')
const { log } = require('./logger')
const { CONFIG } = require('./config')

function setupPathfindingMonitor(bot, rangeGoal) {
  let pathfindingMonitorInterval = null
  let currentGoal = null
  
  // Function to start monitoring the pathfinding process
  function startPathfindingMonitor() {
    // Clear any existing monitor first
    stopPathfindingMonitor()
    
    // Set the current goal
    currentGoal = bot.pathfinder.goal
    
    // Check progress periodically
    pathfindingMonitorInterval = setInterval(() => {
      // If no current goal, stop monitoring
      if (!currentGoal) {
        stopPathfindingMonitor()
        return
      }
      
      // If bot isn't moving anymore and is close to the goal, we consider it reached
      if (currentGoal) {
        const distance = bot.entity.position.distanceTo(new Vec3(
          currentGoal.x, 
          currentGoal.y,
          currentGoal.z
        ))
        
        if (distance <= rangeGoal + 0.5) {  // Small buffer for precision
          log('success', 'Goal reached! Bot has arrived at the destination.')
          stopPathfindingMonitor()
        }
      }
    }, 500)  // Check every 500ms
  }
  
  // Function to stop the pathfinding monitor
  function stopPathfindingMonitor() {
    if (pathfindingMonitorInterval) {
      clearInterval(pathfindingMonitorInterval)
      pathfindingMonitorInterval = null
    }
    currentGoal = null
  }

  return { startPathfindingMonitor, stopPathfindingMonitor }
}

// Helper function to navigate to a position
async function navigateToPosition(bot, x, y, z) {
  return new Promise((resolve, reject) => {
    try {
      const movements = new (require('mineflayer-pathfinder').Movements)(bot)
      bot.pathfinder.setMovements(movements)
      bot.pathfinder.setGoal(new GoalNear(x, y, z, CONFIG.rangeGoal))
      
      // Use our monitoring approach
      const checkInterval = setInterval(() => {
        // If we're close enough to the target
        if (bot.entity.position.distanceTo(new Vec3(x, y, z)) < CONFIG.rangeGoal + 0.5) {
          clearInterval(checkInterval)
          resolve()
        }
      }, 250)
      
      // Set a timeout in case pathfinding gets stuck
      setTimeout(() => {
        clearInterval(checkInterval)
        
        // If we're close enough, consider it a success
        if (bot.entity.position.distanceTo(new Vec3(x, y, z)) < 3) {
          resolve()
        } else {
          reject(new Error('Navigation timeout'))
        }
      }, CONFIG.navigationTimeout)
    } catch (error) {
      reject(error)
    }
  })
}

module.exports = {
  setupPathfindingMonitor,
  navigateToPosition
}
