// Deutsche Bahn Bus Abfahrten
// Verwendet die transport.rest API (basierend auf db-hafas)

const API_BASE = 'https://v6.db.transport.rest';

// API Configuration
const SEARCH_RESULTS = 10;
const DEPARTURE_RESULTS = 30;
const DEPARTURE_DURATION = 120; // Minutes

// DOM Elements
const stopSearchInput = document.getElementById('stopSearch');
const searchBtn = document.getElementById('searchBtn');
const suggestionsContainer = document.getElementById('suggestions');
const selectedStopDiv = document.getElementById('selectedStop');
const departures1Div = document.getElementById('departures1');
const departures2Div = document.getElementById('departures2');

let selectedStop = null;
let searchTimeout = null;

// Event Listeners
stopSearchInput.addEventListener('input', handleSearchInput);
stopSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        searchStops();
    }
});
searchBtn.addEventListener('click', searchStops);

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-section')) {
        suggestionsContainer.classList.remove('active');
    }
});

// Handle search input with debounce
function handleSearchInput() {
    clearTimeout(searchTimeout);
    const query = stopSearchInput.value.trim();
    
    if (query.length < 2) {
        suggestionsContainer.classList.remove('active');
        return;
    }
    
    searchTimeout = setTimeout(() => {
        searchStops();
    }, 300);
}

// Search for stops
async function searchStops() {
    const query = stopSearchInput.value.trim();
    
    if (query.length < 2) {
        return;
    }
    
    try {
        const response = await fetch(
            `${API_BASE}/locations?query=${encodeURIComponent(query)}&results=${SEARCH_RESULTS}&stops=true&addresses=false&poi=false`
        );
        
        if (!response.ok) {
            throw new Error('API Fehler');
        }
        
        const locations = await response.json();
        displaySuggestions(locations.filter(loc => loc.type === 'stop'));
    } catch (error) {
        console.error('Fehler bei der Suche:', error);
        suggestionsContainer.innerHTML = '<div class="suggestion-item"><span class="stop-name">Fehler bei der Suche</span></div>';
        suggestionsContainer.classList.add('active');
    }
}

// Display stop suggestions
function displaySuggestions(stops) {
    if (stops.length === 0) {
        suggestionsContainer.innerHTML = '<div class="suggestion-item"><span class="stop-name">Keine Haltestellen gefunden</span></div>';
        suggestionsContainer.classList.add('active');
        return;
    }
    
    suggestionsContainer.innerHTML = stops.map(stop => `
        <div class="suggestion-item" data-id="${stop.id}" data-name="${escapeHtml(stop.name)}">
            <div class="stop-name">${escapeHtml(stop.name)}</div>
            ${stop.location ? `<div class="stop-location">📍 ${stop.location.latitude.toFixed(4)}, ${stop.location.longitude.toFixed(4)}</div>` : ''}
        </div>
    `).join('');
    
    // Add click handlers
    suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', () => selectStop(item.dataset.id, item.dataset.name));
    });
    
    suggestionsContainer.classList.add('active');
}

// Select a stop
function selectStop(stopId, stopName) {
    selectedStop = { id: stopId, name: stopName };
    
    // Update UI
    stopSearchInput.value = stopName;
    suggestionsContainer.classList.remove('active');
    selectedStopDiv.innerHTML = `<h3>📍 ${escapeHtml(stopName)}</h3>`;
    selectedStopDiv.classList.add('active');
    
    // Load departures
    loadDepartures(stopId);
}

// Load departures for both directions
async function loadDepartures(stopId) {
    departures1Div.innerHTML = '<div class="loading"><p>Lade Abfahrten...</p></div>';
    departures2Div.innerHTML = '<div class="loading"><p>Lade Abfahrten...</p></div>';
    
    try {
        // Fetch departures
        const response = await fetch(
            `${API_BASE}/stops/${stopId}/departures?results=${DEPARTURE_RESULTS}&duration=${DEPARTURE_DURATION}&bus=true&ferry=false&express=false&regional=false`
        );
        
        if (!response.ok) {
            throw new Error('API Fehler beim Laden der Abfahrten');
        }
        
        const data = await response.json();
        const departures = data.departures || data;
        
        // Group departures by direction
        const { direction1, direction2 } = groupByDirection(departures);
        
        // Display departures
        displayDepartures(departures1Div, direction1, 'Richtung 1');
        displayDepartures(departures2Div, direction2, 'Richtung 2');
        
        // Update area headers with direction info
        updateAreaHeaders(direction1, direction2);
        
    } catch (error) {
        console.error('Fehler beim Laden der Abfahrten:', error);
        const errorHtml = `<div class="error"><p>❌ Fehler beim Laden der Abfahrten</p><p>${error.message}</p></div>`;
        departures1Div.innerHTML = errorHtml;
        departures2Div.innerHTML = errorHtml;
    }
}

// Group departures by direction
function groupByDirection(departures) {
    if (!departures || departures.length === 0) {
        return { direction1: [], direction2: [] };
    }
    
    // Get unique directions
    const directions = {};
    departures.forEach(dep => {
        const dir = dep.direction || 'Unbekannt';
        if (!directions[dir]) {
            directions[dir] = [];
        }
        directions[dir].push(dep);
    });
    
    // Sort directions by number of departures and take top 2 groups
    const sortedDirs = Object.entries(directions)
        .sort((a, b) => b[1].length - a[1].length);
    
    // If only one or no directions, split by line number or other criteria
    if (sortedDirs.length <= 1 && departures.length > 0) {
        // Try to split by line
        const byLine = {};
        departures.forEach(dep => {
            const line = dep.line?.name || 'Unbekannt';
            if (!byLine[line]) {
                byLine[line] = [];
            }
            byLine[line].push(dep);
        });
        
        const lines = Object.values(byLine);
        if (lines.length >= 2) {
            // Distribute lines between two areas
            const half = Math.ceil(lines.length / 2);
            return {
                direction1: lines.slice(0, half).flat(),
                direction2: lines.slice(half).flat()
            };
        }
        
        // Last resort: split departures in half
        const half = Math.ceil(departures.length / 2);
        return {
            direction1: departures.slice(0, half),
            direction2: departures.slice(half)
        };
    }
    
    // Take first two distinct directions
    const direction1 = sortedDirs[0] ? sortedDirs[0][1] : [];
    const direction2 = sortedDirs.slice(1).flatMap(([dirName, deps]) => deps);
    
    return { direction1, direction2 };
}

// Update area headers with actual direction names
function updateAreaHeaders(dir1Deps, dir2Deps) {
    const area1 = document.querySelector('#area1 h2');
    const area2 = document.querySelector('#area2 h2');
    
    if (dir1Deps.length > 0) {
        const mainDir1 = dir1Deps[0].direction || 'Richtung 1';
        area1.textContent = `⬅️ ${mainDir1}`;
    } else {
        area1.textContent = '⬅️ Richtung 1';
    }
    
    if (dir2Deps.length > 0) {
        const mainDir2 = dir2Deps[0].direction || 'Richtung 2';
        area2.textContent = `➡️ ${mainDir2}`;
    } else {
        area2.textContent = '➡️ Richtung 2';
    }
}

// Display departures in a container
function displayDepartures(container, departures, fallbackTitle) {
    if (!departures || departures.length === 0) {
        container.innerHTML = '<div class="no-departures">Keine Abfahrten gefunden</div>';
        return;
    }
    
    // Sort by departure time
    departures.sort((a, b) => {
        const timeA = new Date(a.when || a.plannedWhen);
        const timeB = new Date(b.when || b.plannedWhen);
        return timeA - timeB;
    });
    
    container.innerHTML = departures.slice(0, 10).map(dep => {
        const when = new Date(dep.when || dep.plannedWhen);
        const planned = new Date(dep.plannedWhen);
        const now = new Date();
        
        // Calculate delay in minutes
        const delay = dep.delay ? Math.round(dep.delay / 60) : 0;
        
        // Calculate minutes until departure
        const minutesUntil = Math.round((when - now) / 60000);
        
        // Format time
        const timeStr = when.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
        
        // Get line type for styling
        const lineType = getLineType(dep.line);
        
        return `
            <div class="departure-item">
                <div class="departure-line ${lineType}">${escapeHtml(dep.line?.name || 'Unbekannt')}</div>
                <div class="departure-info">
                    <div class="departure-direction">${escapeHtml(dep.direction || 'Unbekannt')}</div>
                    ${dep.platform ? `<div class="departure-platform">Steig ${escapeHtml(dep.platform)}</div>` : ''}
                </div>
                <div class="departure-time">
                    <div class="time">${timeStr}</div>
                    ${delay > 0 ? `<div class="delay">+${delay} min</div>` : ''}
                    <div class="minutes">${minutesUntil <= 0 ? 'Jetzt' : `in ${minutesUntil} min`}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Get line type for styling
function getLineType(line) {
    if (!line) return '';
    
    const product = line.product || '';
    const name = (line.name || '').toLowerCase();
    
    if (product === 'bus' || name.includes('bus')) return 'bus';
    if (product === 'tram' || name.includes('tram') || name.includes('str')) return 'tram';
    if (product === 'subway' || name.includes('u')) return 'subway';
    
    return '';
}

// Utility: Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh departures every 60 seconds
setInterval(() => {
    if (selectedStop) {
        loadDepartures(selectedStop.id);
    }
}, 60000);
