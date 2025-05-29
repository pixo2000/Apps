// Simple script to generate placeholder images for the game

(function() {
    // List of required images
    const requiredImages = [
        'gold.png',
        'elixir.png',
        'townhall.png',
        'goldmine.png',
        'elixircollector.png',
        'cannon.png',
        'barbarian.png',
        'archer.png'
    ];
    
    // Colors for each image type
    const colors = {
        'gold.png': '#FFD700',
        'elixir.png': '#8A2BE2',
        'townhall.png': '#A52A2A',
        'goldmine.png': '#DAA520',
        'elixircollector.png': '#9932CC',
        'cannon.png': '#696969',
        'barbarian.png': '#CD853F',
        'archer.png': '#228B22'
    };
    
    // Create a canvas to generate image data
    function createPlaceholder(filename, color) {
        const canvas = document.createElement('canvas');
        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        
        // Fill background
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, 64, 64);
        
        // Add a border
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(2, 2, 60, 60);
        
        // Add image name
        ctx.fillStyle = '#fff';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        
        // Extract name without extension
        const name = filename.split('.')[0];
        ctx.fillText(name, 32, 36);
        
        return canvas.toDataURL();
    }
    
    // Replace all missing images with placeholders
    function replaceMissingImages() {
        document.querySelectorAll('img').forEach(img => {
            // Check if this is one of our game images
            const filename = img.src.split('/').pop();
            if (requiredImages.includes(filename)) {
                // Create an error handler to replace with placeholder
                img.onerror = function() {
                    this.onerror = null; // Prevent infinite loop
                    this.src = createPlaceholder(filename, colors[filename] || '#cccccc');
                };
                
                // Trigger a reload to either load the real image or fall back to placeholder
                const currentSrc = img.src;
                img.src = '';
                img.src = currentSrc;
            }
        });
    }
    
    // Run after page loads
    window.addEventListener('load', replaceMissingImages);
})();
