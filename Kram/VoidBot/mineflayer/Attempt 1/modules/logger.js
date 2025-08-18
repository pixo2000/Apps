// Logger module for consistent console output

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

module.exports = { colors, log }
