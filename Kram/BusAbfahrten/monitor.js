const API_BASE = 'https://v6.db.transport.rest';
let STATION_ID = '125295'; // Start with the user provided ID
const REFRESH_INTERVAL = 60000; // 60 Sekunden
const TRIP_CACHE = new Map(); // Cache for trip details to reduce API calls

// Load route cache from localStorage
let ROUTE_CACHE = {};
try {
    const stored = localStorage.getItem('bus_route_cache');
    if (stored) {
        ROUTE_CACHE = JSON.parse(stored);
    }
} catch (e) {
    console.error('Failed to load route cache', e);
}

function saveRouteCache() {
    try {
        localStorage.setItem('bus_route_cache', JSON.stringify(ROUTE_CACHE));
    } catch (e) {
        console.error('Failed to save route cache', e);
    }
}

// Helper to fetch with retry on 429

// Helper to fetch with retry on 429
async function fetchWithRetry(url, options = {}, retries = 2, backoff = 1000) {
    try {
        const response = await fetch(url, options);
        if (response.status === 429) {
            if (retries > 0) {
                console.warn(`Rate limit hit (429). Retrying in ${backoff}ms...`);
                await new Promise(r => setTimeout(r, backoff));
                return fetchWithRetry(url, options, retries - 1, backoff * 2);
            }
        }
        return response;
    } catch (error) {
        if (retries > 0) {
             await new Promise(r => setTimeout(r, backoff));
             return fetchWithRetry(url, options, retries - 1, backoff * 2);
        }
        throw error;
    }
}

async function updateDepartures() {
    const colWartestrasse = document.getElementById('col-wartestrasse');
    const colOther = document.getElementById('col-other');
    const title = document.getElementById('station-title');
    const lastUpdate = document.getElementById('last-update');

    try {
        // Use fetchWithRetry for the main list
        let response = await fetchWithRetry(`${API_BASE}/stops/${STATION_ID}/departures?duration=60`);
        
        if (response.status === 429) {
             throw new Error('Rate limit exceeded (Too Many Requests)');
        }

        let data = await response.json();
        console.log('API Response:', data);

        // Smart Fix: If ID is invalid
        if (data.message && (data.message.includes('IBNR') || data.message.includes('station ID'))) {
            console.log('Invalid IBNR, trying to search for station...');
            const searchResponse = await fetch(`${API_BASE}/locations?query=${STATION_ID}&results=1`);
            const searchData = await searchResponse.json();
            
            if (Array.isArray(searchData) && searchData.length > 0) {
                const foundStation = searchData[0];
                console.log('Found station:', foundStation);
                STATION_ID = foundStation.id;
                title.textContent = foundStation.name;
                
                // Retry fetching departures with new ID
                response = await fetchWithRetry(`${API_BASE}/stops/${STATION_ID}/departures?duration=60`);
                data = await response.json();
            } else {
                throw new Error('Station ID invalid and no station found via search.');
            }
        }

        let departures = [];
        if (Array.isArray(data)) {
            departures = data;
        } else if (data.departures && Array.isArray(data.departures)) {
            departures = data.departures;
        } else {
            console.error('Unexpected data format:', data);
            return;
        }

        // Update title
        if (departures.length > 0 && departures[0].stop && departures[0].stop.name) {
             title.textContent = departures[0].stop.name;
        } else if (title.textContent === 'Lade Station...') {
             fetch(`${API_BASE}/stops/${STATION_ID}`)
                .then(res => res.json())
                .then(stop => { title.textContent = stop.name; })
                .catch(() => title.textContent = 'Abfahrten');
        }

        // Fetch trip details sequentially with caching and throttling
        const enrichedDepartures = [];
        
        for (const dep of departures) {
            let tripDetails = null;
            let lineName = dep.line && dep.line.name ? dep.line.name.replace('Bus ', '') : '?';
            let direction = dep.direction || '';
            let cacheKey = `${lineName}|${direction}`;

            // Check if we already know the column for this route
            if (ROUTE_CACHE[cacheKey]) {
                // We know where it goes! No need to fetch trip details just for sorting.
                // We will fetch trip details lazily on hover for the tooltip.
                enrichedDepartures.push({ ...dep, tripDetails: null, cachedColumn: ROUTE_CACHE[cacheKey] });
                continue;
            }
            
            if (TRIP_CACHE.has(dep.tripId)) {
                tripDetails = TRIP_CACHE.get(dep.tripId);
            } else {
                try {
                    // Throttle: 100ms delay between requests
                    await new Promise(r => setTimeout(r, 100));
                    
                    const encodedTripId = encodeURIComponent(dep.tripId);
                    const tripRes = await fetch(`${API_BASE}/trips/${encodedTripId}`);
                    
                    if (tripRes.status === 429) {
                        console.warn('Rate limit hit for trip details. Skipping...');
                    } else if (tripRes.ok) {
                        const tripData = await tripRes.json();
                        tripDetails = tripData.trip || tripData;
                        TRIP_CACHE.set(dep.tripId, tripDetails);
                    }
                } catch (e) {
                    console.error('Failed to fetch trip', dep.tripId, e);
                }
            }
            enrichedDepartures.push({ ...dep, tripDetails });
        }

        // Clear columns only after we have data ready
        colWartestrasse.innerHTML = '';
        colOther.innerHTML = '';

        if (enrichedDepartures.length === 0) {
            colWartestrasse.innerHTML = '<p style="text-align:center;">Keine Abfahrten</p>';
            colOther.innerHTML = '<p style="text-align:center;">Keine Abfahrten</p>';
        } else {
            enrichedDepartures.forEach(dep => {
                const div = document.createElement('div');
                div.className = 'departure-item';
                
                const isCancelled = dep.cancelled;
                const time = new Date(dep.when || dep.plannedWhen);
                const timeString = time.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
                
                let delayInfo = '';
                let timeDisplay = timeString;

                let delay = dep.delay;
                if (delay === null || delay === undefined) {
                    if (dep.when && dep.plannedWhen) {
                        const whenTime = new Date(dep.when).getTime();
                        const plannedTime = new Date(dep.plannedWhen).getTime();
                        delay = (whenTime - plannedTime) / 1000;
                    }
                }

                if (isCancelled) {
                    div.style.opacity = '0.5';
                    delayInfo = '<span class="delay" style="color: #ff4d4d; font-weight: bold; margin-left: 10px;">Fällt aus</span>';
                    timeDisplay = `<span style="text-decoration: line-through;">${timeString}</span>`;
                } else if (delay !== null && delay !== undefined) {
                    const delayMin = Math.round(delay / 60);
                    if (delayMin > 0) {
                        delayInfo = `<span class="delay" style="color: #ff4d4d; margin-left: 10px;">+ ${delayMin} min</span>`;
                    } else if (delayMin < 0) {
                         delayInfo = `<span class="on-time" style="margin-left: 10px;">${delayMin} min</span>`;
                    } else {
                        delayInfo = `<span class="on-time" style="margin-left: 10px;">+0 min</span>`;
                    }
                }

                let lineName = dep.line && dep.line.name ? dep.line.name : '?';
                lineName = lineName.replace('Bus ', '');
                const productClass = dep.line && dep.line.product ? dep.line.product : '';

                let nextStopName = 'Unbekannt';
                let isWartestrasse = false;
                
                // If we have a cached decision, use it
                if (dep.cachedColumn) {
                    isWartestrasse = (dep.cachedColumn === 'wartestrasse');
                    // We don't have nextStopName yet, but that's okay, tooltip will fetch it.
                    div.dataset.nextStop = ''; // Clear it so tooltip fetches
                } else if (dep.tripDetails && dep.tripDetails.stopovers) {
                    const stopovers = dep.tripDetails.stopovers;
                    let currentIndex = stopovers.findIndex(s => s.stop.id === dep.stop.id);
                    if (currentIndex === -1) {
                         currentIndex = stopovers.findIndex(s => s.stop.id.includes(dep.stop.id) || dep.stop.id.includes(s.stop.id));
                    }

                    if (currentIndex !== -1 && currentIndex < stopovers.length - 1) {
                        const nextStop = stopovers[currentIndex + 1];
                        nextStopName = nextStop.stop.name;
                        const nextTime = new Date(nextStop.arrival || nextStop.plannedArrival);
                        const nextTimeString = nextTime.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
                        div.dataset.nextStop = `<strong>Nächster Halt:</strong> ${nextStopName} (${nextTimeString})`;
                    } else if (currentIndex === stopovers.length - 1) {
                        nextStopName = 'Endstation';
                        div.dataset.nextStop = 'Endstation';
                    }
                    
                    // Determine column logic
                    const dir = (dep.direction || '').toLowerCase();
                    const nextStopLower = nextStopName.toLowerCase();
                    
                    if (dir.includes('wartestraße') || dir.includes('wartestrasse') || dir.includes('wartestr') ||
                        nextStopLower.includes('wartestraße') || nextStopLower.includes('wartestrasse') || nextStopLower.includes('wartestr')) {
                        isWartestrasse = true;
                    }
                    
                    // Save to cache!
                    let cacheKey = `${lineName}|${dep.direction || ''}`;
                    ROUTE_CACHE[cacheKey] = isWartestrasse ? 'wartestrasse' : 'other';
                    saveRouteCache();
                } else {
                    // Fallback if no trip details and no cache (e.g. API error)
                    // Just guess based on direction string
                    const dir = (dep.direction || '').toLowerCase();
                    if (dir.includes('wartestraße') || dir.includes('wartestrasse') || dir.includes('wartestr')) {
                        isWartestrasse = true;
                    }
                }

                div.dataset.tripId = dep.tripId;
                div.dataset.stopId = dep.stop.id;

                div.innerHTML = `
                    <div style="display:flex; align-items:center; flex:1;">
                        <span class="line-badge ${productClass}">${lineName}</span>
                        <div style="display:flex; flex-direction:column;">
                            <span class="direction">${dep.direction}</span>
                        </div>
                    </div>
                    <div class="time">
                        ${timeDisplay}
                        ${delayInfo}
                    </div>
                `;
                
                div.addEventListener('mouseenter', (e) => showNextStop(e, dep.tripId, dep.stop.id));
                div.addEventListener('mouseleave', hideNextStop);
                
                if (isWartestrasse) {
                    colWartestrasse.appendChild(div);
                } else {
                    colOther.appendChild(div);
                }
            });
            
            if (colWartestrasse.children.length === 0) colWartestrasse.innerHTML = '<p style="text-align:center; color: #888;">Keine Abfahrten</p>';
            if (colOther.children.length === 0) colOther.innerHTML = '<p style="text-align:center; color: #888;">Keine Abfahrten</p>';
        }

        const now = new Date();
        lastUpdate.textContent = `Zuletzt aktualisiert: ${now.toLocaleTimeString('de-DE')}`;
        lastUpdate.style.color = '#888'; // Reset color on success

    } catch (error) {
        console.error('Error:', error);
        const errorMsg = error.message.includes('Rate limit') ? 'Zu viele Anfragen (Rate Limit). Warte...' : 'Fehler beim Laden';
        lastUpdate.textContent = `Fehler: ${errorMsg}`;
        lastUpdate.style.color = '#ff4d4d';
    }
}

// Tooltip Logic
const tooltip = document.getElementById('hover-tooltip');
let currentFetch = null;

async function showNextStop(event, tripId, currentStopId) {
    const target = event.currentTarget;
    
    const rect = target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.bottom + 5) + 'px';
    tooltip.style.display = 'block';
    tooltip.innerHTML = 'Lade nächste Haltestelle...';

    if (target.dataset.nextStop) {
        tooltip.innerHTML = target.dataset.nextStop;
        return;
    }

    try {
        let trip;
        if (TRIP_CACHE.has(tripId)) {
            trip = TRIP_CACHE.get(tripId);
        } else {
            const encodedTripId = encodeURIComponent(tripId);
            const response = await fetch(`${API_BASE}/trips/${encodedTripId}`);
            const data = await response.json();
            trip = data.trip || data;
            TRIP_CACHE.set(tripId, trip);
        }

        if (!trip.stopovers) {
            tooltip.innerHTML = 'Keine Routeninformationen verfügbar.';
            return;
        }

        let currentIndex = trip.stopovers.findIndex(s => s.stop.id === currentStopId);
        if (currentIndex === -1) {
             currentIndex = trip.stopovers.findIndex(s => s.stop.id.includes(currentStopId) || currentStopId.includes(s.stop.id));
        }

        if (currentIndex !== -1 && currentIndex < trip.stopovers.length - 1) {
            const nextStop = trip.stopovers[currentIndex + 1];
            const nextStopName = nextStop.stop.name;
            const nextTime = new Date(nextStop.arrival || nextStop.plannedArrival);
            const nextTimeString = nextTime.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
            
            const tooltipContent = `<strong>Nächster Halt:</strong> ${nextStopName} (${nextTimeString})`;
            
            target.dataset.nextStop = tooltipContent;
            tooltip.innerHTML = tooltipContent;
        } else if (currentIndex === trip.stopovers.length - 1) {
            const content = 'Endstation';
            target.dataset.nextStop = content;
            tooltip.innerHTML = content;
        } else {
            tooltip.innerHTML = 'Nächster Halt nicht gefunden.';
        }

    } catch (error) {
        console.error('Error fetching trip:', error);
        tooltip.innerHTML = 'Fehler beim Laden.';
    }
}

function hideNextStop() {
    tooltip.style.display = 'none';
}

// Initial load
updateDepartures();

// Auto refresh
setInterval(updateDepartures, REFRESH_INTERVAL);
