// Game state
const gameState = {
    resources: {
        gold: 1000,
        elixir: 1000
    },
    buildings: [],
    troops: [],
    selectedBuilding: null,
    placementMode: false,
    gameTime: 0,
};

// Debug function to help troubleshoot issues
function debugLog(message) {
    console.log(`DEBUG: ${message}`);
}

// Building types and properties
const buildingTypes = {
    townhall: { width: 2, height: 2, health: 1000, cost: { type: 'gold', amount: 0 } },
    goldmine: { width: 1, height: 1, health: 300, production: { resource: 'gold', rate: 10 }, cost: { type: 'gold', amount: 200 } },
    elixircollector: { width: 1, height: 1, health: 300, production: { resource: 'elixir', rate: 10 }, cost: { type: 'gold', amount: 200 } },
    cannon: { width: 1, height: 1, health: 500, damage: 50, range: 5, cost: { type: 'gold', amount: 400 } }
};

// Troop types and properties
const troopTypes = {
    barbarian: { health: 100, damage: 30, speed: 3, cost: { type: 'elixir', amount: 50 } },
    archer: { health: 70, damage: 25, range: 4, speed: 4, cost: { type: 'elixir', amount: 80 } }
};

// Initialize the game
function initGame() {
    debugLog("Game initializing...");
    createVillageGrid();
    initEventListeners();
    startGameLoop();
    
    // Add initial townhall
    placeBuilding('townhall', 4, 4);
    
    // Update UI
    updateResourcesDisplay();
    
    // For testing - add some troops automatically
    trainTroop('barbarian');
    trainTroop('barbarian');
    trainTroop('archer');
    
    debugLog("Game initialized successfully");
}

// Create the grid for village layout
function createVillageGrid() {
    const grid = document.getElementById('village-grid');
    
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            grid.appendChild(cell);
        }
    }
}

// Initialize event listeners
function initEventListeners() {
    // Building selection
    document.querySelectorAll('.building-item').forEach(item => {
        item.addEventListener('click', () => {
            const buildingType = item.dataset.building;
            const cost = parseInt(item.dataset.cost);
            
            if (gameState.resources.gold >= cost) {
                gameState.selectedBuilding = buildingType;
                gameState.placementMode = true;
            } else {
                alert("Not enough gold!");
            }
        });
    });
    
    // Tab switching
    document.getElementById('buildings-tab').addEventListener('click', () => {
        document.getElementById('buildings-tab').classList.add('active-tab');
        document.getElementById('troops-tab').classList.remove('active-tab');
        document.getElementById('buildings-menu').classList.remove('hidden');
        document.getElementById('troops-menu').classList.add('hidden');
    });
    
    document.getElementById('troops-tab').addEventListener('click', () => {
        document.getElementById('troops-tab').classList.add('active-tab');
        document.getElementById('buildings-tab').classList.remove('active-tab');
        document.getElementById('troops-menu').classList.remove('hidden');
        document.getElementById('buildings-menu').classList.add('hidden');
    });
    
    // Village grid interactions
    document.getElementById('village-grid').addEventListener('click', (event) => {
        if (!gameState.placementMode) return;
        
        const cell = event.target.closest('.grid-cell');
        if (!cell) return;
        
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        if (canPlaceBuilding(gameState.selectedBuilding, row, col)) {
            placeBuilding(gameState.selectedBuilding, row, col);
            deductResources(buildingTypes[gameState.selectedBuilding].cost);
            gameState.placementMode = false;
            gameState.selectedBuilding = null;
            updateResourcesDisplay();
        } else {
            alert("Cannot place building here!");
        }
    });
    
    // Troop training
    document.querySelectorAll('.troop-item').forEach(item => {
        item.addEventListener('click', () => {
            const troopType = item.dataset.troop;
            const cost = troopTypes[troopType].cost.amount;
            
            if (gameState.resources.elixir >= cost) {
                trainTroop(troopType);
                gameState.resources.elixir -= cost;
                updateResourcesDisplay();
            } else {
                alert("Not enough elixir!");
            }
        });
    });
    
    // Attack button with improved error handling
    document.getElementById('attack-button').addEventListener('click', () => {
        debugLog("Attack button clicked");
        try {
            startAttack();
        } catch (error) {
            console.error("Error in battle:", error);
            alert("There was an error starting the battle. Check console for details.");
        }
    });
    
    // End battle button with improved error handling
    document.getElementById('end-battle').addEventListener('click', () => {
        debugLog("End battle button clicked");
        document.getElementById('battle-screen').classList.add('hidden');
    });
    
    // Save button
    document.getElementById('save-button').addEventListener('click', () => {
        saveGameState();
    });
}

// Check if a building can be placed at the specified position
function canPlaceBuilding(buildingType, row, col) {
    const building = buildingTypes[buildingType];
    
    // Check if position is within grid
    if (row < 0 || row + building.height > 10 || col < 0 || col + building.width > 10) {
        return false;
    }
    
    // Check if position overlaps with existing buildings
    for (let r = row; r < row + building.height; r++) {
        for (let c = col; c < col + building.width; c++) {
            for (const existingBuilding of gameState.buildings) {
                if (c >= existingBuilding.col && 
                    c < existingBuilding.col + buildingTypes[existingBuilding.type].width &&
                    r >= existingBuilding.row && 
                    r < existingBuilding.row + buildingTypes[existingBuilding.type].height) {
                    return false;
                }
            }
        }
    }
    
    return true;
}

// Place a building on the grid
function placeBuilding(buildingType, row, col) {
    const building = {
        type: buildingType,
        row,
        col,
        health: buildingTypes[buildingType].health,
        lastCollected: gameState.gameTime
    };
    
    gameState.buildings.push(building);
    
    // Render the building
    for (let r = row; r < row + buildingTypes[buildingType].height; r++) {
        for (let c = col; c < col + buildingTypes[buildingType].width; c++) {
            const cell = document.querySelector(`.grid-cell[data-row="${r}"][data-col="${c}"]`);
            cell.innerHTML = '';
            
            if (r === row && c === col) {
                const buildingElement = document.createElement('div');
                buildingElement.className = 'building';
                buildingElement.style.backgroundImage = `url('images/${buildingType}.png')`;
                cell.appendChild(buildingElement);
            }
        }
    }
}

// Training troops (modified to show more feedback)
function trainTroop(troopType) {
    const troop = {
        type: troopType,
        health: troopTypes[troopType].health
    };
    
    gameState.troops.push(troop);
    
    // Show feedback in UI
    const message = document.createElement('div');
    message.textContent = `Trained a ${troopType}!`;
    message.style.color = 'green';
    message.style.position = 'fixed';
    message.style.bottom = '50px';
    message.style.left = '50%';
    message.style.transform = 'translateX(-50%)';
    message.style.padding = '10px';
    message.style.backgroundColor = 'rgba(0,0,0,0.7)';
    message.style.borderRadius = '5px';
    message.style.zIndex = '1000';
    
    document.body.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 2000);
    
    debugLog(`Trained a ${troopType}. Total troops: ${gameState.troops.length}`);
}

// Deduct resources for costs
function deductResources(cost) {
    if (cost.type === 'gold') {
        gameState.resources.gold -= cost.amount;
    } else if (cost.type === 'elixir') {
        gameState.resources.elixir -= cost.amount;
    }
}

// Update resources display
function updateResourcesDisplay() {
    document.getElementById('gold-amount').textContent = gameState.resources.gold;
    document.getElementById('elixir-amount').textContent = gameState.resources.elixir;
}

// Game loop (for resource production, etc.)
function startGameLoop() {
    setInterval(() => {
        gameState.gameTime++;
        collectResources();
        updateResourcesDisplay();
    }, 1000);
}

// Collect resources from production buildings
function collectResources() {
    for (const building of gameState.buildings) {
        const buildingInfo = buildingTypes[building.type];
        
        if (buildingInfo.production) {
            const timeSinceLastCollection = gameState.gameTime - building.lastCollected;
            const resourceGenerated = Math.floor(buildingInfo.production.rate * timeSinceLastCollection / 10);
            
            if (resourceGenerated > 0) {
                gameState.resources[buildingInfo.production.resource] += resourceGenerated;
                building.lastCollected = gameState.gameTime;
            }
        }
    }
}

// Start an attack (completely revised)
function startAttack() {
    debugLog("Starting attack...");
    
    // STEP 1: First make sure we have troops
    if (gameState.troops.length === 0) {
        alert("You need to train troops before attacking! Go to the Troops tab to train some.");
        return;
    }
    
    // STEP 2: Show the battle screen
    const battleScreen = document.getElementById('battle-screen');
    battleScreen.classList.remove('hidden');
    battleScreen.style.backgroundColor = 'rgba(0, 0, 0, 0.9)'; // Make sure it's visible
    
    // STEP 3: Clear and prepare the enemy village
    const enemyVillage = document.getElementById('enemy-village');
    enemyVillage.innerHTML = '';
    enemyVillage.style.backgroundColor = '#7cbe5a';
    enemyVillage.style.border = '2px solid #5a8b42';
    
    // STEP 4: Create simplified enemy village (more reliable)
    for (let i = 0; i < 100; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.dataset.index = i;
        enemyVillage.appendChild(cell);
    }
    
    // STEP 5: Add a few buildings (simplified)
    const buildingPositions = [15, 27, 45, 54, 72, 84];
    const buildingTypes = ['townhall', 'goldmine', 'elixircollector', 'cannon'];
    
    for (let i = 0; i < buildingPositions.length; i++) {
        const cell = enemyVillage.children[buildingPositions[i]];
        if (cell) {
            const type = buildingTypes[i % buildingTypes.length];
            
            // Create colored block if image isn't available
            cell.innerHTML = `
                <div class="building" data-type="${type}" style="
                    background-color: ${getBuildingColor(type)};
                    background-image: url('images/${type}.png');
                    width: 90%; 
                    height: 90%;
                    margin: 5%;
                    border: 2px solid black;
                ">
                    <span style="color: white; text-shadow: 1px 1px 2px black; font-size: 10px;">${type}</span>
                </div>
            `;
        }
    }
    
    // STEP 6: Prepare troop deployment panel
    const deployPanel = document.getElementById('deploy-troops-panel');
    deployPanel.innerHTML = `
        <div style="color: white; text-align: center; margin-bottom: 10px; font-weight: bold;">
            Select a troop to deploy
        </div>
    `;
    
    // STEP 7: Add troop buttons
    const barbarianCount = gameState.troops.filter(t => t.type === 'barbarian').length;
    const archerCount = gameState.troops.filter(t => t.type === 'archer').length;
    
    if (barbarianCount > 0) {
        addTroopButton(deployPanel, 'barbarian', barbarianCount);
    }
    
    if (archerCount > 0) {
        addTroopButton(deployPanel, 'archer', archerCount);
    }
    
    debugLog("Battle setup complete");
}

// Helper function to get building colors
function getBuildingColor(type) {
    const colors = {
        'townhall': '#A52A2A',
        'goldmine': '#DAA520',
        'elixircollector': '#9932CC',
        'cannon': '#696969'
    };
    return colors[type] || '#888';
}

// Add a troop button to the deployment panel
function addTroopButton(panel, troopType, count) {
    const button = document.createElement('div');
    button.className = 'troop-deploy-item';
    button.innerHTML = `
        <div style="
            width: 40px;
            height: 40px;
            background-color: ${troopType === 'barbarian' ? '#CD853F' : '#228B22'};
            background-image: url('images/${troopType}.png');
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            border-radius: 50%;
            margin: 0 auto 5px auto;
        "></div>
        <span>${troopType} (${count})</span>
    `;
    
    panel.appendChild(button);
    
    // Add event listener for deployment
    button.addEventListener('click', () => {
        setupSimplifiedDeployment(troopType);
    });
}

// Set up simplified deployment mode
function setupSimplifiedDeployment(troopType) {
    const enemyVillage = document.getElementById('enemy-village');
    
    // Add message
    const message = document.createElement('div');
    message.style.color = 'white';
    message.style.textAlign = 'center';
    message.style.marginBottom = '10px';
    message.style.padding = '5px';
    message.style.backgroundColor = 'rgba(0,0,0,0.5)';
    message.style.borderRadius = '5px';
    message.innerHTML = `Click anywhere in the enemy village to deploy <strong>${troopType}</strong>`;
    
    const deployPanel = document.getElementById('deploy-troops-panel');
    if (deployPanel.firstChild) {
        deployPanel.insertBefore(message, deployPanel.firstChild);
    } else {
        deployPanel.appendChild(message);
    }
    
    // Highlight the enemy village to show it's clickable
    enemyVillage.style.boxShadow = '0 0 15px yellow';
    
    // Enable click for deployment
    enemyVillage.onclick = function(e) {
        // Find a troop of this type
        const index = gameState.troops.findIndex(t => t.type === troopType);
        if (index === -1) {
            message.innerHTML = `No more <strong>${troopType}</strong> troops available!`;
            enemyVillage.style.boxShadow = 'none';
            return;
        }
        
        // Create a visual representation of the troop
        const troopElement = document.createElement('div');
        troopElement.className = 'deployed-troop';
        troopElement.style.position = 'absolute';
        troopElement.style.left = (e.clientX - enemyVillage.getBoundingClientRect().left) + 'px';
        troopElement.style.top = (e.clientY - enemyVillage.getBoundingClientRect().top) + 'px';
        troopElement.style.width = '30px';
        troopElement.style.height = '30px';
        troopElement.style.backgroundColor = troopType === 'barbarian' ? '#CD853F' : '#228B22';
        troopElement.style.backgroundImage = `url('images/${troopType}.png')`;
        troopElement.style.backgroundSize = 'contain';
        troopElement.style.backgroundPosition = 'center';
        troopElement.style.backgroundRepeat = 'no-repeat';
        troopElement.style.borderRadius = '50%';
        troopElement.style.transform = 'translate(-50%, -50%)';
        troopElement.style.zIndex = '10';
        enemyVillage.appendChild(troopElement);
        
        // Remove the troop from our army
        gameState.troops.splice(index, 1);
        
        // Update troop count
        const count = gameState.troops.filter(t => t.type === troopType).length;
        const buttons = document.querySelectorAll('.troop-deploy-item');
        for (const button of buttons) {
            if (button.textContent.includes(troopType)) {
                button.querySelector('span').textContent = `${troopType} (${count})`;
                if (count === 0) {
                    button.style.opacity = '0.5';
                }
                break;
            }
        }
        
        // Find nearest building and simulate attack
        const targetBuilding = findNearestBuilding(e.clientX, e.clientY);
        if (targetBuilding) {
            simulateSimplifiedAttack(troopElement, targetBuilding);
        } else {
            // Just move around a bit then disappear
            setTimeout(() => {
                troopElement.style.top = (parseInt(troopElement.style.top) + 20) + 'px';
            }, 500);
            setTimeout(() => {
                troopElement.style.top = (parseInt(troopElement.style.top) - 10) + 'px';
            }, 1000);
            setTimeout(() => {
                troopElement.remove();
            }, 2000);
        }
        
        // If no more troops of this type, update message
        if (count === 0) {
            message.innerHTML = `No more <strong>${troopType}</strong> troops available!`;
            message.style.color = 'orange';
        }
    };
}

// Find the nearest building to a click position
function findNearestBuilding(clickX, clickY) {
    const enemyVillage = document.getElementById('enemy-village');
    const buildings = enemyVillage.querySelectorAll('.building');
    const enemyRect = enemyVillage.getBoundingClientRect();
    
    let nearestBuilding = null;
    let minDistance = Infinity;
    
    buildings.forEach(building => {
        const buildingRect = building.getBoundingClientRect();
        const buildingX = buildingRect.left + buildingRect.width/2;
        const buildingY = buildingRect.top + buildingRect.height/2;
        
        const distance = Math.sqrt(
            Math.pow(clickX - buildingX, 2) + 
            Math.pow(clickY - buildingY, 2)
        );
        
        if (distance < minDistance) {
            minDistance = distance;
            nearestBuilding = building;
        }
    });
    
    // Only return if reasonably close (200px)
    return minDistance < 200 ? nearestBuilding : null;
}

// Simulate a simplified attack on a building
function simulateSimplifiedAttack(troopElement, building) {
    // Create attack animation
    const buildingRect = building.getBoundingClientRect();
    const troopRect = troopElement.getBoundingClientRect();
    
    // Move troop towards building
    const targetX = buildingRect.left + buildingRect.width/2;
    const targetY = buildingRect.top + buildingRect.height/2;
    
    // Get enemy village for coordinate reference
    const enemyVillage = document.getElementById('enemy-village');
    const enemyRect = enemyVillage.getBoundingClientRect();
    
    // Set transitions for smooth movement
    troopElement.style.transition = 'all 1s ease-in-out';
    
    // Move to attack position
    setTimeout(() => {
        troopElement.style.left = (targetX - enemyRect.left) + 'px';
        troopElement.style.top = (targetY - enemyRect.top) + 'px';
    }, 100);
    
    // Flash building to show damage
    setTimeout(() => {
        building.style.transition = 'opacity 0.2s';
        let flashCount = 0;
        const flashInterval = setInterval(() => {
            building.style.opacity = building.style.opacity === '0.5' ? '1' : '0.5';
            flashCount++;
            if (flashCount >= 6) {
                clearInterval(flashInterval);
                building.style.opacity = '0.7';
                building.style.filter = 'grayscale(70%)';
                
                // Remove troop after attack
                setTimeout(() => {
                    troopElement.remove();
                }, 500);
            }
        }, 200);
    }, 1100);
}

// Save game state to server
function saveGameState() {
    const data = {
        resources: gameState.resources,
        buildings: gameState.buildings,
        troops: gameState.troops
    };
    
    fetch('/api/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert('Game saved successfully!');
    })
    .catch(error => {
        console.error('Error saving game:', error);
        alert('Failed to save game. Check the console for details.');
    });
}

// Initialize the game when the page loads
window.addEventListener('load', function() {
    try {
        initGame();
        debugLog("Game loaded successfully");
    } catch (error) {
        console.error("Error loading game:", error);
        alert("There was an error loading the game. Check console for details.");
    }
});
