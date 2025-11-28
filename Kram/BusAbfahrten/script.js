const API_BASE = 'https://v6.db.transport.rest';

document.getElementById('station-search').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        searchStation();
    }
});

async function searchStation() {
    const query = document.getElementById('station-search').value;
    if (!query) return;

    const resultsDiv = document.getElementById('station-results');
    resultsDiv.innerHTML = 'Suche...';

    try {
        const response = await fetch(`${API_BASE}/locations?query=${encodeURIComponent(query)}&results=5`);
        const data = await response.json();

        resultsDiv.innerHTML = '';
        
        // Filter only stops/stations
        const stops = data.filter(item => item.type === 'stop' || item.type === 'station');

        if (stops.length === 0) {
            resultsDiv.innerHTML = '<p>Keine Haltestellen gefunden.</p>';
            return;
        }

        stops.forEach(stop => {
            const div = document.createElement('div');
            div.className = 'station-item';
            div.innerHTML = `<strong>${stop.name}</strong> <br><small>ID: ${stop.id}</small>`;
            div.onclick = () => showDepartures(stop.id, stop.name);
            resultsDiv.appendChild(div);
        });

    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = '<p>Fehler bei der Suche.</p>';
    }
}

async function showDepartures(stationId, stationName) {
    document.getElementById('station-results').style.display = 'none';
    document.getElementById('departures-container').style.display = 'block';
    document.getElementById('selected-station-name').textContent = 'Abfahrten: ' + stationName;
    
    const listDiv = document.getElementById('departures-list');
    listDiv.innerHTML = 'Lade Abfahrten...';

    try {
        const response = await fetch(`${API_BASE}/stops/${stationId}/departures?duration=60`);
        const data = await response.json();
        const departures = data.departures || data; // Sometimes it's directly an array, sometimes wrapped

        listDiv.innerHTML = '';

        if (departures.length === 0) {
            listDiv.innerHTML = '<p>Keine Abfahrten in den nächsten 60 Minuten.</p>';
            return;
        }

        departures.forEach(dep => {
            const div = document.createElement('div');
            div.className = 'departure-item';
            
            const time = new Date(dep.when || dep.plannedWhen);
            const timeString = time.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
            
            let delayInfo = '';
            if (dep.delay !== null && dep.delay !== undefined) {
                const delayMin = Math.round(dep.delay / 60);
                if (delayMin > 0) {
                    delayInfo = `<span class="delay">+${delayMin}</span>`;
                } else {
                    delayInfo = `<span class="on-time">Pünktlich</span>`;
                }
            }

            const lineName = dep.line && dep.line.name ? dep.line.name : '?';
            const productClass = dep.line && dep.line.product ? dep.line.product : '';

            div.innerHTML = `
                <div style="display:flex; align-items:center; flex:1;">
                    <span class="line-badge ${productClass}">${lineName}</span>
                    <span class="direction">${dep.direction}</span>
                </div>
                <div class="time">
                    ${timeString}
                    ${delayInfo}
                </div>
            `;
            listDiv.appendChild(div);
        });

    } catch (error) {
        console.error('Error:', error);
        listDiv.innerHTML = '<p>Fehler beim Laden der Abfahrten.</p>';
    }
}

function backToSearch() {
    document.getElementById('station-results').style.display = 'flex';
    document.getElementById('departures-container').style.display = 'none';
}
