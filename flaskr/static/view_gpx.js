function initializeMap(filename) {
    const map = L.map('map');
    const defaultView = [51.505, -0.09];
    let startExists = false;
    let endExists = false;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => map.setView([position.coords.latitude, position.coords.longitude], 13),
            () => map.setView(defaultView, 13)
        );
    } else {
        map.setView(defaultView, 13);
    }
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    if (!filename) return

    let elevationOptions = {
        theme: "lime-theme",
        detached: true,
        elevationDiv: "#elevation-div",
        autohide: false,
        collapsed: true,
        position: "topright",
        closeBtn: true,
        followMarker: true,
        autofitBounds: true,
        imperial: false,
        reverseCoords: false,
        altitude: true,
        distance: true,
        summary: 'inline',
        summaryContainer: '<div class="elevation-summary"></div>',
        downloadLink: false,
        ruler: true,
        legend: false,
        almostOver: true,
        distanceMarkers: false,
        edgeScale: false,
        hotline: false,
        timestamps: false,
        waypoints: true,
        wptLabels: true,
        preferCanvas: true,
        height: 200
    };

    let controlElevation = L.control.elevation(elevationOptions).addTo(map);
    const gpxLayer = new L.GPX(`/downloads/${encodeURIComponent(filename)}`, {
        async: true,
        marker_options: {
            startIconUrl: 'https://cdn.jsdelivr.net/npm/leaflet-gpx@1.7.0/pin-icon-start.png',
            endIconUrl: 'https://cdn.jsdelivr.net/npm/leaflet-gpx@1.7.0/pin-icon-end.png',
            shadowUrl: 'https://cdn.jsdelivr.net/npm/leaflet-gpx@1.7.0/pin-shadow.png',
            clickable: true,
            draggable: true
        }
    }).on('loaded', function(e) {
        map.fitBounds(e.target.getBounds());
        const points = e.target.getLayers()[0].getLayers();
        let start = points.filter(layer => layer.options?.icon?.options?.iconUrl === "https://cdn.jsdelivr.net/npm/leaflet-gpx@1.7.0/pin-icon-start.png")
        startExists = start !== 0;
        if (startExists) {
            let end = points.filter(layer => layer.options?.icon?.options?.iconUrl === "https://cdn.jsdelivr.net/npm/leaflet-gpx@1.7.0/pin-icon-end.png")
            if (start[0].getLatLng() !== end[0].getLatLng()) {
                endExists = true;
            }
        }
        points.filter(layer => layer.options?.type === "waypoint").forEach((waypoint, index) => {
            waypoint.setIcon(createNumberedIcon(index + 1));
        });
    }).addTo(map);

    gpxLayer.on('click', function(e) {
        let marker = e.layer;
        marker.dragging.enable();
        let position = marker.getLatLng();
        let popupContent = createPopupContent('remove_point', filename, position);
        marker.bindPopup(popupContent, { offset: L.point(0, -40) }).openPopup();
        

        handleMarkerDrag(filename, marker);
    });

    map.on('click', function(event) {
        handleMapClick(filename, event, map, startExists, endExists);
    });

    gpxLayer.on("addline", function(e) {
        controlElevation.addData(e.line);
    });
}

function handleMarkerDrag(filename, marker) {
    let originalPosition;
    marker.on('dragstart', function() {
        originalPosition = marker.getLatLng();
    });

    marker.on('dragend', function() {
        let position = marker.getLatLng();
        let latitude = originalPosition.lat.toFixed(6);
        let longitude = originalPosition.lng.toFixed(6);
        let newLatitude = position.lat.toFixed(6);
        let newLongitude = position.lng.toFixed(6);
        submitForm('move_point', filename, latitude, longitude, newLatitude, newLongitude);
    });
}

function handleMapClick(filename, event, map, startExists, endExists) {
    let position = event.latlng;
    reverseGeocode(position, function(placeName) {
        let popupContent = `${placeName}<br>`;
        popupContent += `<div style="display: flex; justify-content: center; gap: 10px;">`;
        if (startExists && endExists) {
            popupContent += createPopupContent('add_point', filename, position);
            popupContent += createPopupContent('append_point', filename, position);
        } else {
            if (!startExists) {
                popupContent += createPopupContent('set_start', filename, position);
            }
            else {
                popupContent += createPopupContent('set_end', filename, position);
            }
        }
        popupContent += `</div>`;
        L.popup().setLatLng(position).setContent(popupContent).openOn(map);
    });
}

function reverseGeocode(latlng, callback) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}&zoom=18&addressdetails=1`;

    fetch(url)
        .then(response => response.json())
        .then(data => callback(data.display_name))
        .catch(error => {
            console.error('Error with reverse geocoding:', error);
            callback('Unknown place');
        });
}

function createPopupContent(action, filename, position, newPosition = null) {
    let latitude = position.lat.toFixed(6);
    let longitude = position.lng.toFixed(6);
    let newLatitude = newPosition ? newPosition.lat.toFixed(6) : null;
    let newLongitude = newPosition ? newPosition.lng.toFixed(6) : null;

    return `
        <div style="text-align: center;">
            <form onsubmit="submitForm('${action}', '${filename}', ${latitude}, ${longitude}, ${newLatitude}, ${newLongitude}); return false;">
                <input type="submit" value="${action.replace('_', ' ')}">
            </form>
        </div>`;
}

function submitForm(action, filename, latitude, longitude, newLatitude, newLongitude) {
    let form = document.createElement('form');
    form.style.display = 'none';
    form.method = 'POST';
    form.action = `/${action}/${encodeURIComponent(filename)}`;

    [['latitude', latitude], ['longitude', longitude], ['new_latitude', newLatitude], ['new_longitude', newLongitude]].forEach(([name, value]) => {
        if (value != null) {
            let input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            form.appendChild(input);
        }
    });

    document.body.appendChild(form);
    form.submit();
}

function createNumberedIcon(number) {
    let canvas = document.createElement('canvas');
    canvas.width = 24;
    canvas.height = 24;
    let context = canvas.getContext('2d');

    context.fillStyle = '#0c94ea'; // Blue color
    context.beginPath();
    context.arc(12, 12, 10, 0, Math.PI * 2, true);
    context.closePath();
    context.fill();

    context.fillStyle = '#FFFFFF'; // White color
    context.font = '10px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(number, 12, 12);

    return new L.Icon({
        iconUrl: canvas.toDataURL(),
        iconSize: [24, 24]
    });
}
