function initializeMap(filename) {
    let map = L.map('map').setView([51.505, -0.09], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let elevation_options = {
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

    let controlElevation = L.control.elevation(elevation_options).addTo(map);

    let gpx = `/downloads/${encodeURIComponent(filename)}`;
    let gpxLayer = new L.GPX(gpx, {
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

        // Number the waypoints
        let waypoints = e.target.getLayers()[0].getLayers().filter(layer => layer.options.type === "waypoint");
        waypoints.forEach((waypoint, index) => {
            let number = index + 1;
            let icon = createNumberedIcon(number);
            waypoint.setIcon(icon);
        });

        controlElevation.load(gpxLayer);
    }).addTo(map);

    // Handle marker click and drag events
    gpxLayer.on('click', function(e) {
        let marker = e.layer;
        marker.dragging.enable();
        let position = marker.getLatLng();
        let popupContent = createPopupContent('remove_point', filename, position);
        marker.bindPopup(popupContent, { offset: L.point(0, -40) }).openPopup();

        handleMarker(filename, marker);
    });

    // Handle map click events
    map.on('click', function(event) {
        handleMap(filename, event, map);
    });

    gpxLayer.on("addline", function(e) {
        controlElevation.addData(e.line);
    });

}

function handleMarker(filename, marker) {
    let originalPosition;
    marker.on('dragstart', function(_) {
        originalPosition = marker.getLatLng();
    });

    marker.on('dragend', function(_) {
        let position = marker.getLatLng();
        let latitude = originalPosition.lat.toFixed(6);
        let longitude = originalPosition.lng.toFixed(6);
        let newLatitude = position.lat.toFixed(6);
        let newLongitude = position.lng.toFixed(6);
        submitForm('move_point', filename, latitude, longitude, newLatitude, newLongitude);
    });
}

function handleMap(filename, event, map) {
    let position = event.latlng;
    reverseGeocode(position, function(placeName) {
        let popupContent = `${placeName}<br>`;
        popupContent += `<div style="display: flex; justify-content: center; gap: 10px;">`;
        popupContent += createPopupContent('add_point', filename, position);
        popupContent += createPopupContent('append_point', filename, position);
        popupContent += `</div>`;
        L.popup().setLatLng(position).setContent(popupContent).openOn(map);
    });
}

function reverseGeocode(latlng, callback) {
    let url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}&zoom=18&addressdetails=1`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            let placeName = data.display_name;
            callback(placeName);
        })
        .catch(error => {
            console.error('Error with reverse geocoding:', error);
            callback('Unknown place');
        });
}

function createPopupContent(action, filename, position, newPosition = null) {
    let latitude = position.lat.toFixed(6);
    let longitude = position.lng.toFixed(6);
    let newLatitude = null;
    let newLongitude = null;
    if (newPosition != null) {
        newLatitude = newPosition.lat.toFixed(6);
        newLongitude = newPosition.lng.toFixed(6);
    }

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
            const input = document.createElement('input');
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

    // Draw the base pin icon (simplified for demonstration)
    context.fillStyle = '#0c94ea'; // Blue color
    context.beginPath();
    context.arc(12, 12, 10, 0, Math.PI * 2, true);
    context.closePath();
    context.fill();

    // Draw the number
    context.fillStyle = '#FFFFFF'; // White color
    context.font = '10px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(number, 12, 12);

    // Create the icon
    return new L.Icon({
        iconUrl: canvas.toDataURL(),
        iconSize: [24, 24]
    });
}
