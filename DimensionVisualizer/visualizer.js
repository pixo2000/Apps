// Canvas und Kontextvariablen
const canvas = document.getElementById('dimension-canvas');
const ctx = canvas.getContext('2d');

// Globale Variablen
let dimensionData = null;
let scale = 1;
let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let lastX, lastY;
let selectedObject = null;

// Event Listener für Dateiupload
document.getElementById('dimension-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                dimensionData = JSON.parse(e.target.result);
                resetView();
                drawDimension();
                updateDimensionInfo();
            } catch (error) {
                alert('Fehler beim Parsen der JSON-Datei: ' + error.message);
            }
        };
        reader.readAsText(file);
    }
});

// Event Listener für Beispieldaten
document.getElementById('load-sample').addEventListener('click', function() {
    fetch('/workspaces/Apps/Spacer/dimensions/C12.json')
        .then(response => response.json())
        .then(data => {
            dimensionData = data;
            resetView();
            drawDimension();
            updateDimensionInfo();
        })
        .catch(error => {
            alert('Fehler beim Laden der Beispieldaten: ' + error.message);
        });
});

// Zoom-Funktionen
document.getElementById('zoom-in').addEventListener('click', function() {
    scale *= 1.2;
    drawDimension();
});

document.getElementById('zoom-out').addEventListener('click', function() {
    scale *= 0.8;
    drawDimension();
});

document.getElementById('reset-view').addEventListener('click', resetView);

// Mausbewegung für Panning
canvas.addEventListener('mousedown', function(e) {
    isDragging = true;
    lastX = e.offsetX;
    lastY = e.offsetY;
    canvas.style.cursor = 'grabbing';
});

canvas.addEventListener('mousemove', function(e) {
    if (isDragging) {
        offsetX += e.offsetX - lastX;
        offsetY += e.offsetY - lastY;
        lastX = e.offsetX;
        lastY = e.offsetY;
        drawDimension();
    } else {
        checkHover(e.offsetX, e.offsetY);
    }
});

canvas.addEventListener('mouseup', function() {
    isDragging = false;
    canvas.style.cursor = 'move';
});

canvas.addEventListener('mouseleave', function() {
    isDragging = false;
    canvas.style.cursor = 'move';
});

canvas.addEventListener('click', function(e) {
    selectObjectAt(e.offsetX, e.offsetY);
});

// Funktion zum Zurücksetzen der Ansicht
function resetView() {
    scale = 1;
    offsetX = canvas.width / 2;
    offsetY = canvas.height / 2;
    selectedObject = null;
    drawDimension();
}

// Funktion zum Aktualisieren der Dimensionsinfo
function updateDimensionInfo() {
    if (!dimensionData) return;
    
    const dimension = Object.values(dimensionData)[0];
    document.getElementById('dimension-title').textContent = dimension.title || dimension.name;
    document.getElementById('dimension-description').textContent = dimension.description || '';
}

// Funktion zum Überprüfen, ob der Mauszeiger über einem Objekt ist
function checkHover(x, y) {
    if (!dimensionData) return;
    
    canvas.style.cursor = 'move';
    const dimension = Object.values(dimensionData)[0];
    const bodies = dimension.bodies;
    
    for (const bodyName in bodies) {
        const body = bodies[bodyName];
        const bodyX = (parseFloat(body.Coordinates.x) * scale) + offsetX;
        const bodyY = (parseFloat(body.Coordinates.y) * scale) + offsetY;
        const bodyWidth = parseFloat(body.size.width) * scale;
        const bodyHeight = parseFloat(body.size.height) * scale;
        
        if (x >= bodyX - bodyWidth && x <= bodyX + bodyWidth && 
            y >= bodyY - bodyHeight && y <= bodyY + bodyHeight) {
            canvas.style.cursor = 'pointer';
            return;
        }
        
        // Prüfen von Stationen
        if (body.Stations) {
            for (const stationName in body.Stations) {
                const station = body.Stations[stationName];
                const stationX = (parseFloat(station.Coordinates.x) * scale) + offsetX;
                const stationY = (parseFloat(station.Coordinates.y) * scale) + offsetY;
                
                if (x >= stationX - 5 && x <= stationX + 5 && 
                    y >= stationY - 5 && y <= stationY + 5) {
                    canvas.style.cursor = 'pointer';
                    return;
                }
            }
        }
        
        // Prüfen von Monden
        if (body.Moons) {
            for (const moonName in body.Moons) {
                const moon = body.Moons[moonName];
                const moonX = (parseFloat(moon.Coordinates.x) * scale) + offsetX;
                const moonY = (parseFloat(moon.Coordinates.y) * scale) + offsetY;
                const moonWidth = parseFloat(moon.size.width) * scale;
                const moonHeight = parseFloat(moon.size.height) * scale;
                
                if (x >= moonX - moonWidth && x <= moonX + moonWidth && 
                    y >= moonY - moonHeight && y <= moonY + moonHeight) {
                    canvas.style.cursor = 'pointer';
                    return;
                }
            }
        }
    }
}

// Funktion zum Auswählen eines Objekts an einer Position
function selectObjectAt(x, y) {
    if (!dimensionData) return;
    
    const dimension = Object.values(dimensionData)[0];
    const bodies = dimension.bodies;
    let found = null;
    
    // Prüfen der Körper
    for (const bodyName in bodies) {
        const body = bodies[bodyName];
        const bodyX = (parseFloat(body.Coordinates.x) * scale) + offsetX;
        const bodyY = (parseFloat(body.Coordinates.y) * scale) + offsetY;
        const bodyWidth = parseFloat(body.size.width) * scale;
        const bodyHeight = parseFloat(body.size.height) * scale;
        
        if (x >= bodyX - bodyWidth && x <= bodyX + bodyWidth && 
            y >= bodyY - bodyHeight && y <= bodyY + bodyHeight) {
            found = { name: bodyName, data: body, type: 'body' };
        }
        
        // Prüfen von Stationen
        if (body.Stations) {
            for (const stationName in body.Stations) {
                const station = body.Stations[stationName];
                const stationX = (parseFloat(station.Coordinates.x) * scale) + offsetX;
                const stationY = (parseFloat(station.Coordinates.y) * scale) + offsetY;
                
                if (x >= stationX - 5 && x <= stationX + 5 && 
                    y >= stationY - 5 && y <= stationY + 5) {
                    found = { name: stationName, data: station, type: 'station', parent: bodyName };
                }
            }
        }
        
        // Prüfen von Monden
        if (body.Moons) {
            for (const moonName in body.Moons) {
                const moon = body.Moons[moonName];
                const moonX = (parseFloat(moon.Coordinates.x) * scale) + offsetX;
                const moonY = (parseFloat(moon.Coordinates.y) * scale) + offsetY;
                const moonWidth = parseFloat(moon.size.width) * scale;
                const moonHeight = parseFloat(moon.size.height) * scale;
                
                if (x >= moonX - moonWidth && x <= moonX + moonWidth && 
                    y >= moonY - moonHeight && y <= moonY + moonHeight) {
                    found = { name: moonName, data: moon, type: 'moon', parent: bodyName };
                }
            }
        }
    }
    
    selectedObject = found;
    drawDimension();
    displayObjectDetails();
}

// Funktion zum Anzeigen der Objektdetails
function displayObjectDetails() {
    const detailsContainer = document.getElementById('object-details');
    const infoHeader = document.getElementById('selected-object-info').querySelector('h3');
    
    if (!selectedObject) {
        infoHeader.textContent = 'Wählen Sie ein Objekt für Details';
        detailsContainer.innerHTML = '';
        return;
    }
    
    infoHeader.textContent = `${selectedObject.name} (${selectedObject.data.type})`;
    
    let detailsHTML = '';
    
    if (selectedObject.type === 'body') {
        detailsHTML += `<p><strong>Typ:</strong> ${selectedObject.data.type}</p>`;
        detailsHTML += `<p><strong>Position:</strong> X: ${selectedObject.data.Coordinates.x}, Y: ${selectedObject.data.Coordinates.y}</p>`;
        detailsHTML += `<p><strong>Größe:</strong> B: ${selectedObject.data.size.width}, H: ${selectedObject.data.size.height}</p>`;
        
        if (selectedObject.data.Stations) {
            detailsHTML += `<p><strong>Stationen:</strong> ${Object.keys(selectedObject.data.Stations).length}</p>`;
        }
        
        if (selectedObject.data.Moons) {
            detailsHTML += `<p><strong>Monde:</strong> ${Object.keys(selectedObject.data.Moons).length}</p>`;
        }
    } else if (selectedObject.type === 'station') {
        detailsHTML += `<p><strong>Typ:</strong> ${selectedObject.data.type}</p>`;
        detailsHTML += `<p><strong>Bezugskörper:</strong> ${selectedObject.parent}</p>`;
        detailsHTML += `<p><strong>Position:</strong> X: ${selectedObject.data.Coordinates.x}, Y: ${selectedObject.data.Coordinates.y}</p>`;
        
        if (selectedObject.data.description) {
            detailsHTML += `<p><strong>Beschreibung:</strong> ${selectedObject.data.description}</p>`;
        }
    } else if (selectedObject.type === 'moon') {
        detailsHTML += `<p><strong>Typ:</strong> ${selectedObject.data.type}</p>`;
        detailsHTML += `<p><strong>Planet:</strong> ${selectedObject.parent}</p>`;
        detailsHTML += `<p><strong>Position:</strong> X: ${selectedObject.data.Coordinates.x}, Y: ${selectedObject.data.Coordinates.y}</p>`;
        detailsHTML += `<p><strong>Größe:</strong> B: ${selectedObject.data.size.width}, H: ${selectedObject.data.size.height}</p>`;
    }
    
    detailsContainer.innerHTML = detailsHTML;
}

// Funktion zum Zeichnen der Dimension
function drawDimension() {
    // Canvas leeren
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (!dimensionData) return;
    
    const dimension = Object.values(dimensionData)[0];
    const bodies = dimension.bodies;
    
    // Koordinatensystem zeichnen
    drawGrid();
    
    // Alle Körper zeichnen
    for (const bodyName in bodies) {
        const body = bodies[bodyName];
        
        // Position und Größe berechnen
        const x = (parseFloat(body.Coordinates.x) * scale) + offsetX;
        const y = (parseFloat(body.Coordinates.y) * scale) + offsetY;
        const width = parseFloat(body.size.width) * scale;
        const height = parseFloat(body.size.height) * scale;
        
        // Farbe basierend auf Typ wählen
        let color = '#aaa';  // Standardfarbe
        
        if (body.type === 'Star') {
            color = '#ffff00';  // gelb für Sterne
        } else if (body.type === 'Planet') {
            color = '#3498db';  // blau für Planeten
        }
        
        // Körper zeichnen
        ctx.beginPath();
        ctx.arc(x, y, Math.max(width, height), 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        
        // Hervorhebung für ausgewähltes Objekt
        if (selectedObject && selectedObject.type === 'body' && selectedObject.name === bodyName) {
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
        
        // Name des Körpers anzeigen
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(bodyName, x, y - height - 5);
        
        // Stationen zeichnen, falls vorhanden
        if (body.Stations) {
            for (const stationName in body.Stations) {
                const station = body.Stations[stationName];
                const stationX = (parseFloat(station.Coordinates.x) * scale) + offsetX;
                const stationY = (parseFloat(station.Coordinates.y) * scale) + offsetY;
                
                ctx.beginPath();
                ctx.rect(stationX - 5, stationY - 5, 10, 10);
                ctx.fillStyle = '#ff0000';  // rot für Stationen
                ctx.fill();
                
                // Hervorhebung für ausgewähltes Objekt
                if (selectedObject && selectedObject.type === 'station' && selectedObject.name === stationName) {
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
                
                // Name der Station anzeigen
                ctx.fillStyle = '#fff';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(stationName, stationX, stationY - 8);
            }
        }
        
        // Monde zeichnen, falls vorhanden
        if (body.Moons) {
            for (const moonName in body.Moons) {
                const moon = body.Moons[moonName];
                const moonX = (parseFloat(moon.Coordinates.x) * scale) + offsetX;
                const moonY = (parseFloat(moon.Coordinates.y) * scale) + offsetY;
                const moonWidth = parseFloat(moon.size.width) * scale;
                const moonHeight = parseFloat(moon.size.height) * scale;
                
                // Linie vom Planeten zum Mond zeichnen
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(moonX, moonY);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.lineWidth = 1;
                ctx.stroke();
                
                // Mond zeichnen
                ctx.beginPath();
                ctx.arc(moonX, moonY, Math.max(moonWidth, moonHeight), 0, Math.PI * 2);
                ctx.fillStyle = '#ccc';  // grau für Monde
                ctx.fill();
                
                // Hervorhebung für ausgewähltes Objekt
                if (selectedObject && selectedObject.type === 'moon' && selectedObject.name === moonName) {
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
                
                // Name des Mondes anzeigen
                ctx.fillStyle = '#fff';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(moonName, moonX, moonY - moonHeight - 5);
            }
        }
    }
}

// Funktion zum Zeichnen des Koordinatengitters
function drawGrid() {
    const gridSize = 50 * scale;
    const offsetXMod = offsetX % gridSize;
    const offsetYMod = offsetY % gridSize;
    
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // Horizontale Linien
    for (let y = offsetYMod; y < canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
    
    // Vertikale Linien
    for (let x = offsetXMod; x < canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    
    // Hauptachsen
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2;
    
    // X-Achse
    ctx.beginPath();
    ctx.moveTo(0, offsetY);
    ctx.lineTo(canvas.width, offsetY);
    ctx.stroke();
    
    // Y-Achse
    ctx.beginPath();
    ctx.moveTo(offsetX, 0);
    ctx.lineTo(offsetX, canvas.height);
    ctx.stroke();
    
    // Ursprung
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.beginPath();
    ctx.arc(offsetX, offsetY, 3, 0, Math.PI * 2);
    ctx.fill();
}

// Initialisierung
canvas.style.cursor = 'move';
resetView();
drawDimension();
