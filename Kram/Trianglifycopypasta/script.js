// =============================================================================
// TRIANGLIFY BACKGROUND GENERATOR - COPY-PASTE READY
// ============================================================================

// CONFIG - Modify these settings as needed
const TRIANGLIFY_CONFIG = {
    cellSize: 60,           // Size of triangular cells (smaller = more detail)
    variance: 0.9,          // Randomness factor (0-1, higher = more varied)
    colorScheme: 'sunset',   // 'ocean', 'sunset', 'forest', 'purple', 'grayscale'
    autoResize: true        // Automatically regenerate on window resize
};

// Store current options for consistent resizing
let currentOptions = {};

// =============================================================================
// MAIN FUNCTIONS - No need to modify below this line
// =============================================================================

function createTrianglifyBackground(options = {}) {
    const defaults = {
        width: window.innerWidth,
        height: window.innerHeight,
        cellSize: TRIANGLIFY_CONFIG.cellSize,
        variance: TRIANGLIFY_CONFIG.variance,
        seed: null,
        xColors: 'random',
        yColors: 'match'
    };
    
    const config = { ...defaults, ...options };
    
    // Store current options for resize consistency
    currentOptions = { ...config };
    
    try {
        const pattern = trianglify(config);
        const canvas = pattern.toCanvas();
        const dataURL = canvas.toDataURL();
        
        document.body.style.backgroundImage = `url(${dataURL})`;
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundRepeat = 'no-repeat';
        document.body.style.backgroundAttachment = 'fixed';
    } catch (error) {
        console.error('Error generating trianglify background:', error);
    }
}

function applyColorScheme(scheme) {
    const colorSchemes = {
        ocean: { xColors: ['#001f3f', '#0074D9', '#0077be', '#00a8cc', '#00c9b7', '#4fc3f7', '#26c6da', '#80deea', '#b2ebf2'] },
        sunset: { xColors: ['#8B0000', '#DC143C', '#ff6b6b', '#ffa726', '#ffcc02', '#ff8a65', '#ffb74d', '#ffcc80', '#ffe0b2'] },
        forest: { xColors: ['#1B5E20', '#2E7D32', '#43a047', '#66bb6a', '#81c784', '#a5d6a7', '#c8e6c9', '#dcedc8', '#f1f8e9'] },
        purple: { xColors: ['#4A148C', '#6a1b9a', '#8e24aa', '#ab47bc', '#ba68c8', '#ce93d8', '#e1bee7', '#f3e5f5', '#fce4ec'] },
        grayscale: { xColors: ['#000000', '#212121', '#424242', '#616161', '#757575', '#9e9e9e', '#bdbdbd', '#e0e0e0', '#f5f5f5'] }
    };
    
    return colorSchemes[scheme] || {};
}

function handleResize() {
    const resizeOptions = { 
        ...currentOptions, 
        width: window.innerWidth, 
        height: window.innerHeight 
    };
    createTrianglifyBackground(resizeOptions);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    if (typeof trianglify === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/trianglify@^4/dist/trianglify.bundle.js';
        script.onload = function() {
            setTimeout(() => {
                const options = applyColorScheme(TRIANGLIFY_CONFIG.colorScheme);
                createTrianglifyBackground(options);
                
                if (TRIANGLIFY_CONFIG.autoResize) {
                    window.addEventListener('resize', handleResize);
                }
            }, 100);
        };
        script.onerror = () => document.body.style.background = 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)';
        document.head.appendChild(script);
    }
});

// Optional: Global function to change background programmatically
// Usage: changeTrianglifyBg('ocean')
window.changeTrianglifyBg = function(scheme = 'ocean') {
    if (typeof trianglify !== 'undefined') {
        const options = applyColorScheme(scheme);
        createTrianglifyBackground(options);
    }
};