// Configuration constants for the bot

const CONFIG = {
  rangeGoal: 1,  // Get within this radius of the target
  blockPlaceDelay: 150, // Delay between block placements to avoid kick
  navigationTimeout: 10000, // 10 seconds timeout for navigation
  inventoryOperationTimeout: 10000, // 10 seconds timeout for inventory operations
}

module.exports = { CONFIG }
