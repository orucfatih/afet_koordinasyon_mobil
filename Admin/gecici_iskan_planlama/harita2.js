let map, infoWindow, autocomplete, weatherAutocomplete, trafficLayer, drawingManager, polygons = [], heatmap;
let streetViewPanorama, elevationService;
let userLocation = null;
let selectedMarkerType = null;
let pendingTeamMarker = null;
let directionsService, directionsRenderer;
let activePolygon = null;
let polygonNotes = new Map();

// Katmanlar için global nesneler
const layers = {
    userMarkers: [],
    assemblyMarkers: [],
    earthquakeMarkers: [],
    tentcityMarkers: [],
    heatmap: null
};

// API anahtarları
const weatherApiKey = window.WEATHER_API_KEY || '';
const mapsApiKey = window.MAPS_API_KEY || '';

// replaceChildren polyfill
if (!Element.prototype.replaceChildren) {
    Element.prototype.replaceChildren = function(...nodes) {
        console.log('replaceChildren called, this:', this);
        if (!(this instanceof Element)) {
            throw new TypeError('replaceChildren must be called on an Element');
        }
        while (this.firstChild) {
            this.removeChild(this.firstChild);
        }
        this.append(...nodes);
    };
}


// Katman Yöneticisi
class LayerManager {
    constructor() {
        this.layers = {};
    }

    addLayer(name, items = [], visible = true) {
        this.layers[name] = { items, visible };
    }

    toggleLayer(name) {
        if (this.layers[name]) {
            this.layers[name].visible = !this.layers[name].visible;
            console.log(`Toggling layer: ${name}, Visible: ${this.layers[name].visible}`);
            this.layers[name].items.forEach(item => {
                if (item.setMap) {
                    item.setMap(this.layers[name].visible ? map : null);
                } else if (item.marker && item.marker.setMap) {
                    item.marker.setMap(this.layers[name].visible ? map : null);
                }
            });
            if (name === 'heatmap' && layers.heatmap) {
                layers.heatmap.setMap(this.layers[name].visible ? map : null);
            }
            const checkbox = document.querySelector(`.layer-checkbox[data-layer="${name}"]`);
            if (checkbox) {
                checkbox.checked = this.layers[name].visible;
            }
        } else {
            console.error(`Layer not found: ${name}`);
        }
    }

    clearLayer(name) {
        if (this.layers[name]) {
            this.layers[name].items.forEach(item => {
                if (item.setMap) {
                    item.setMap(null);
                } else if (item.marker && item.marker.setMap) {
                    item.marker.setMap(null);
                }
            });
            this.layers[name].items = [];
        }
    }

    updateLayer(name, newItems) {
        this.clearLayer(name);
        this.layers[name].items = newItems;
        if (this.layers[name].visible) {
            newItems.forEach(item => {
                if (item.setMap) {
                    item.setMap(map);
                } else if (item.marker && item.marker.setMap) {
                    item.marker.setMap(map);
                }
            });
        }
    }
}

const layerManager = new LayerManager();

// Harita başlatma
window.initMap = function() {
    try {
        console.log('initMap called');
        map = new google.maps.Map(document.getElementById('map'), {
            center: { lat: 39.9334, lng: 32.8597 },
            zoom: 6,
            mapTypeId: 'roadmap',
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true,
            zoomControl: true,
            tilt: 0,
            heading: 0,
            styles: [
                { featureType: "water", stylers: [{ color: "#0288d1" }] },
                { featureType: "road", stylers: [{ color: "#555" }, { lightness: 10 }] },
                { featureType: "poi", stylers: [{ visibility: "simplified" }, { lightness: 20 }] },
                { featureType: "landscape", stylers: [{ lightness: 30 }] },
                { featureType: "administrative", stylers: [{ visibility: "on" }] }
            ]
        });

        infoWindow = new google.maps.InfoWindow();
        trafficLayer = new google.maps.TrafficLayer();
        elevationService = new google.maps.ElevationService();
        streetViewPanorama = new google.maps.StreetViewPanorama(
            document.getElementById('street-view-pane'),
            {
                position: { lat: 39.9334, lng: 32.8597 },
                pov: { heading: 165, pitch: 0 },
                zoom: 1,
                visible: false
            }
        );

        drawingManager = new google.maps.drawing.DrawingManager({
            drawingMode: null,
            drawingControl: true,
            drawingControlOptions: {
                position: google.maps.ControlPosition.TOP_CENTER,
                drawingModes: ['polygon', 'rectangle', 'circle', 'hexagon']
            },
            polygonOptions: {
                fillColor: "#FF4500",
                fillOpacity: 0.3,
                strokeWeight: 2,
                strokeColor: "#FF4500",
                clickable: true,
                editable: true,
                draggable: true
            },
            rectangleOptions: {
                fillColor: "#2196F3",
                fillOpacity: 0.3,
                strokeWeight: 2,
                strokeColor: "#2196F3",
                clickable: true,
                editable: true,
                draggable: true
            },
            circleOptions: {
                fillColor: "#4CAF50",
                fillOpacity: 0.3,
                strokeWeight: 2,
                strokeColor: "#4CAF50",
                clickable: true,
                editable: true,
                draggable: true
            }
        });
        drawingManager.setMap(map);

        directionsService = new google.maps.DirectionsService();
        directionsRenderer = new google.maps.DirectionsRenderer({
            map: map,
            suppressMarkers: false,
            polylineOptions: {
                strokeColor: '#FF4500',
                strokeWeight: 6,
                strokeOpacity: 0.8
            }
        });

        layerManager.addLayer('userMarkers', layers.userMarkers, true);
        layerManager.addLayer('assemblyMarkers', layers.assemblyMarkers, false);
        layerManager.addLayer('earthquakeMarkers', layers.earthquakeMarkers, true);
        layerManager.addLayer('tentcityMarkers', layers.tentcityMarkers, true);
        layerManager.addLayer('heatmap', [], false);

        google.maps.event.addListener(drawingManager, 'overlaycomplete', function(event) {
            try {
                const shape = event.overlay;
                console.log('Overlay completed, shape type:', event.type);
                shape.set('clickable', true); // Tıklanabilirliği garantile
                console.log('Shape clickable set to:', shape.get('clickable'));
                activePolygon = shape;
                polygons.push(shape);
                const note = prompt('Bu alan için not ekleyin:', '') || 'Not eklenmedi';
                polygonNotes.set(shape, note);
                console.log('Polygon note set:', polygonNotes.get(shape));
        
                let shapeInfo = '';
                if (event.type === 'polygon') {
                    const path = shape.getPath();
                    const area = google.maps.geometry.spherical.computeArea(path);
                    shapeInfo = `Poligon Alanı: ${(area / 1000000).toFixed(2)} km²`;
                } else if (event.type === 'rectangle') {
                    const bounds = shape.getBounds();
                    const ne = bounds.getNorthEast();
                    const sw = bounds.getSouthWest();
                    const width = google.maps.geometry.spherical.computeDistanceBetween(
                        new google.maps.LatLng(ne.lat(), sw.lng()),
                        new google.maps.LatLng(ne.lat(), ne.lng())
                    );
                    const height = google.maps.geometry.spherical.computeDistanceBetween(
                        new google.maps.LatLng(ne.lat(), sw.lng()),
                        new google.maps.LatLng(sw.lat(), sw.lng())
                    );
                    shapeInfo = `Kare/Dikdörtgen Alanı: ${((width * height) / 1000000).toFixed(2)} km²`;
                } else if (event.type === 'circle') {
                    const radius = shape.getRadius();
                    const area = Math.PI * radius * radius;
                    shapeInfo = `Daire Alanı: ${(area / 1000000).toFixed(2)} km²<br>Yarıçap: ${(radius / 1000).toFixed(2)} km`;
                }
        
                document.getElementById('info-panel').innerHTML = `${shapeInfo}<br>Not: ${note}`;
                showPolygonModal(shape);
        
                google.maps.event.addListener(shape, 'click', function(e) {
                    console.log('Polygon clicked, shape type:', shape instanceof google.maps.Polygon ? 'Polygon' : shape instanceof google.maps.Circle ? 'Circle' : 'Rectangle');
                    console.log('Shape clickable:', shape.get('clickable'));
                    activePolygon = shape;
                    console.log('Calling showPolygonModal, event:', e);
                    showPolygonModal(shape);
                });
                console.log('Click listener added for shape:', shape);
            } catch (error) {
                console.error('Poligon oluşturma hatası:', error);
                showOverlayMessage(`Poligon oluşturulamadı: ${error.message}`, true);
            }
        });

        map.addListener('click', e => {
            console.log('Map clicked, selectedMarkerType:', selectedMarkerType);
            if (selectedMarkerType) {
                const latLng = e.latLng;
                console.log('Adding marker at:', latLng.lat(), latLng.lng());
                if (selectedMarkerType === 'tentcity') {
                    pendingTeamMarker = { latLng: latLng, type: 'tentcity' };
                    showTentcityModal();
                } else if (selectedMarkerType === 'team') {
                    pendingTeamMarker = { latLng: latLng, type: 'team' };
                    showTeamModal();
                } else {
                    let title, iconUrl, note = prompt("Bu işaretçi için bir not ekleyin (isteğe bağlı):") || "";
                    switch (selectedMarkerType) {
                        case 'ambulance':
                            title = 'Ambulans';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/2979/2979016.png';
                            break;
                        case 'police':
                            title = 'Polis';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/3063/3063177.png';
                            break;
                        case 'healthcare':
                            title = 'Sağlıkçı';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/2888/2888679.png';
                            break;
                        case 'gendarmerie':
                            title = 'Jandarma';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/1865/1865269.png';
                            break;
                        default:
                            console.error('Invalid marker type:', selectedMarkerType);
                            return;
                    }
                    try {
                        addMarker(latLng, title, note, iconUrl, selectedMarkerType);
                        map.setCenter(latLng);
                        map.setZoom(12);
                        fetchAirQuality(latLng.lat(), latLng.lng());
                        getElevation({ lat: latLng.lat(), lng: latLng.lng() });
                        selectedMarkerType = null;
                    } catch (error) {
                        console.error('addMarker error:', error);
                    }
                }
            } else {
                console.log('No marker type selected, allowing polygon click');
            }
        });

        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            autocomplete = new google.maps.places.Autocomplete(searchInput, {
                types: ['geocode'],
                componentRestrictions: { country: 'tr' },
                fields: ['geometry', 'name', 'formatted_address', 'place_id']
            });
            autocomplete.bindTo('bounds', map);
            autocomplete.addListener('place_changed', () => {
                const place = autocomplete.getPlace();
                if (!place.geometry) {
                    showOverlayMessage(`Seçilen yer için detay bulunamadı: ${place.name}`, true);
                    return;
                }
                map.setCenter(place.geometry.location);
                map.setZoom(13);
                addMarker(
                    place.geometry.location,
                    place.name,
                    place.formatted_address,
                    'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                    'search'
                );
                showPlaceDetails(place.place_id);
                showStreetView(place.geometry.location);
                getElevation({ lat: place.geometry.location.lat(), lng: place.geometry.location.lng() });
                fetchWeather(place.name);
                fetchAirQuality(place.geometry.location.lat(), place.geometry.location.lng(), place.name);
            });
        } else {
            console.error('Search input not found');
        }

        const weatherInput = document.getElementById('weather-input');
        if (weatherInput) {
            weatherAutocomplete = new google.maps.places.Autocomplete(weatherInput, {
                types: ['(cities)'],
                componentRestrictions: { country: 'tr' },
                fields: ['name', 'geometry']
            });
            weatherAutocomplete.bindTo('bounds', map);
            weatherAutocomplete.addListener('place_changed', () => {
                const place = weatherAutocomplete.getPlace();
                if (!place || !place.name) {
                    showOverlayMessage(`Şehir bulunamadı: ${weatherInput.value}`, true);
                    return;
                }
                fetchWeather(place.name);
                fetchAirQuality(place.geometry.location.lat(), place.geometry.location.lng(), place.name);
                if (place.geometry?.location) {
                    map.setCenter(place.geometry.location);
                    map.setZoom(10);
                }
            });
        } else {
            console.error('Weather input not found');
        }

        setupEventListeners();
        getCurrentLocation();
        loadTentcities();
        loadEarthquakes();
    } catch (error) {
        console.error('initMap failed:', error);
        showOverlayMessage(`Harita yüklenemedi: ${error.message}`, true);
    }
};

// Sidebar açma/kapama
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const btn = document.getElementById('toggle-btn');
    if (sidebar && btn) {
        if (sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            btn.style.left = '20px';
            btn.textContent = '☰';
        } else {
            sidebar.classList.add('open');
            btn.style.left = '380px';
            btn.textContent = '✕';
        }
        console.log('Sidebar toggled:', sidebar.classList.contains('open') ? 'Opened' : 'Closed');
    } else {
        console.error('Sidebar or toggle button not found');
    }
}


// Olay dinleyicilerini ayarlama
function setupEventListeners() {
    // Sidebar toggle butonu
    const toggleBtn = document.getElementById('toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleSidebar);
    } else {
        console.error('Toggle button not found');
    }

    // Katman kontrol checkbox'ları
    document.querySelectorAll('.layer-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const layerName = checkbox.getAttribute('data-layer');
            console.log(`Checkbox changed: ${layerName}, Checked: ${checkbox.checked}`); // Hata ayıklama
            layerManager.toggleLayer(layerName);
            // Katman verilerini yeniden yükle (gerekirse)
            if (checkbox.checked && layerName === 'earthquakeMarkers') {
                loadEarthquakes();
            } else if (checkbox.checked && layerName === 'tentcityMarkers') {
                loadTentcities();
            } else if (checkbox.checked && layerName === 'assemblyMarkers') {
                const city = document.getElementById('weather-input').value || 'Ankara';
                showAssemblyAreas(city);
            }
        });
    });

    const weatherSearchBtn = document.getElementById('weather-search-btn');
    if (weatherSearchBtn) {
        weatherSearchBtn.addEventListener('click', () => {
            const city = document.getElementById('weather-input').value;
            if (city) {
                fetchWeather(city);
                fetchAirQuality(null, null, city);
            } else {
                showOverlayMessage('Lütfen bir şehir adı girin.', true);
            }
        });
    }

    const teamForm = document.getElementById('team-form');
    if (teamForm) {
        teamForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const teamName = document.getElementById('team-name').value;
            const teamStatus = document.getElementById('team-status').value;
            const teamType = document.getElementById('team-type').value;
            const teamSize = document.getElementById('team-size').value;
            if (!teamName) {
                showOverlayMessage('Lütfen bir ekip adı girin.', true);
                return;
            }
            const note = `${pendingTeamMarker.note ? pendingTeamMarker.note + ' | ' : ''}Aktiflik: ${teamStatus} | Tür: ${teamType || 'Belirtilmemiş'} | Kişi Sayısı: ${teamSize || 'Belirtilmemiş'}`;
            addMarker(pendingTeamMarker.latLng, teamName, note, 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png', 'team');
            map.setCenter(pendingTeamMarker.latLng);
            map.setZoom(12);
            fetchAirQuality(pendingTeamMarker.latLng.lat(), pendingTeamMarker.latLng.lng());
            getElevation({ lat: pendingTeamMarker.latLng.lat(), lng: pendingTeamMarker.latLng.lng() });
            closeTeamModal();
            selectedMarkerType = null;
            pendingTeamMarker = null;
        });
    }

    const tentcityForm = document.getElementById('tentcity-form');
    if (tentcityForm) {
        tentcityForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const tentcityName = document.getElementById('tentcity-name').value;
            const capacity = document.getElementById('tentcity-capacity').value;
            const status = document.getElementById('tentcity-status').value;
            const resources = document.getElementById('tentcity-resources').value;
            if (!tentcityName) {
                showOverlayMessage('Lütfen bir çadırkent adı girin.', true);
                return;
            }
            const note = `Kapasite: ${capacity || 'Belirtilmemiş'} kişi | Durum: ${status} | Kaynaklar: ${resources || 'Yok'}`;
            addMarker(
                pendingTeamMarker.latLng,
                tentcityName,
                note,
                'https://cdn-icons-png.flaticon.com/512/2457/2457421.png',
                'tentcity'
            );
            map.setCenter(pendingTeamMarker.latLng);
            map.setZoom(12);
            fetchAirQuality(pendingTeamMarker.latLng.lat(), pendingTeamMarker.latLng.lng());
            getElevation({ lat: pendingTeamMarker.latLng.lat(), lng: pendingTeamMarker.latLng.lng() });
            closeTentcityModal();
            selectedMarkerType = null;
            pendingTeamMarker = null;
        });
    }

    const cancelTeamBtn = document.getElementById('cancel-team-btn');
    if (cancelTeamBtn) {
        cancelTeamBtn.addEventListener('click', () => {
            closeTeamModal();
            selectedMarkerType = null;
            pendingTeamMarker = null;
        });
    }

    const cancelTentcityBtn = document.getElementById('cancel-tentcity-btn');
    if (cancelTentcityBtn) {
        cancelTentcityBtn.addEventListener('click', () => {
            closeTentcityModal();
            selectedMarkerType = null;
            pendingTeamMarker = null;
        });
    }

    const clearMarkersBtn = document.getElementById('clear-markers');
    if (clearMarkersBtn) clearMarkersBtn.addEventListener('click', () => layerManager.clearLayer('userMarkers'));

    const zoomToFitBtn = document.getElementById('zoom-to-fit');
    if (zoomToFitBtn) zoomToFitBtn.addEventListener('click', zoomToFit);

    const currentLocationBtn = document.getElementById('current-location');
    if (currentLocationBtn) currentLocationBtn.addEventListener('click', getCurrentLocation);

    const trafficBtn = document.getElementById('traffic-btn');
    if (trafficBtn) trafficBtn.addEventListener('click', toggleTraffic);

    const clearPolygonsBtn = document.getElementById('clear-polygons');
    if (clearPolygonsBtn) clearPolygonsBtn.addEventListener('click', () => {
        polygons.forEach(polygon => polygon.setMap(null));
        polygons = [];
        polygonNotes.clear();
        document.getElementById('info-panel').innerHTML = 'Poligonlar temizlendi.';
    });

    const heatmapBtn = document.getElementById('heatmap-btn');
    if (heatmapBtn) heatmapBtn.addEventListener('click', () => layerManager.toggleLayer('heatmap'));

    const airQualityBtn = document.getElementById('air-quality-btn');
    if (airQualityBtn) airQualityBtn.addEventListener('click', () => {
        const city = document.getElementById('weather-input').value || 'Ankara';
        fetchWeather(city);
        fetchAirQuality(null, null, city);
    });

    const assemblyAreasBtn = document.getElementById('assembly-areas-btn');
    if (assemblyAreasBtn) assemblyAreasBtn.addEventListener('click', () => {
        const city = document.getElementById('weather-input').value || 'Ankara';
        showAssemblyAreas(city);
    });

    const toggle3dBtn = document.getElementById('toggle-3d-btn');
    if (toggle3dBtn) toggle3dBtn.addEventListener('click', () => {
        const btn = document.getElementById('toggle-3d-btn');
        if (map.getTilt() === 0) {
            map.setTilt(45);
            map.setHeading(0);
            map.setMapTypeId('satellite');
            btn.textContent = '2D Görünüme Geç';
        } else {
            map.setTilt(0);
            map.setHeading(0);
            map.setMapTypeId('roadmap');
            btn.textContent = '3D Görünüme Geç';
        }
    });

    const shortestPathBtn = document.getElementById('shortest-path-btn');
    if (shortestPathBtn) shortestPathBtn.addEventListener('click', calculateShortestPath);
}

// İşaretçi ekleme
function addMarker(latLng, title, note, iconUrl, markerType) {
    const marker = new google.maps.Marker({
        position: latLng,
        map: map,
        title: title || 'Olay Yeri',
        icon: { url: iconUrl, scaledSize: new google.maps.Size(45, 45) },
        draggable: true
    });

    const markerInfo = {
        lat: latLng.lat(),
        lng: latLng.lng(),
        title: title,
        markerType: markerType,
        note: note,
        marker: marker,
        type: markerType
    };
    layers.userMarkers.push(markerInfo);
    layerManager.updateLayer('userMarkers', layers.userMarkers);
    updateMarkerList();

    marker.addListener('dragend', () => {
        const newPos = marker.getPosition();
        markerInfo.lat = newPos.lat();
        markerInfo.lng = newPos.lng();
        updateMarkerList();
        fetchAirQuality(newPos.lat(), newPos.lng());
        getElevation({ lat: newPos.lat(), lng: newPos.lng() });
    });

    marker.addListener('click', () => {
        infoWindow.setContent(
            `<div style="padding:15px; font-family: Poppins;">
                <h3 style="color: #007bff; font-size: 20px;">${title || 'Olay Yeri'}</h3>
                <p style="font-size: 16px;">Tip: ${markerType.charAt(0).toUpperCase() + markerType.slice(1)}</p>
                <p style="font-size: 16px;">Koordinatlar: ${latLng.lat().toFixed(4)}, ${latLng.lng().toFixed(4)}</p>
                <p style="font-size: 16px;">Not: ${note || 'Yok'}</p>
                <button class="btn-small btn-primary" onclick="centerMap(${latLng.lat()}, ${latLng.lng()})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>
                <button class="btn-small btn-danger" onclick="deleteMarker(${layers.userMarkers.indexOf(markerInfo)})"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" style="width: 16px;"> Sil</button>
            </div>`
        );
        infoWindow.open(map, marker);
    });
}

// İşaretçi silme
function deleteMarker(index) {
    if (index >= 0 && index < layers.userMarkers.length) {
        const markerInfo = layers.userMarkers[index];
        markerInfo.marker.setMap(null);
        layers.userMarkers.splice(index, 1);
        layerManager.updateLayer('userMarkers', layers.userMarkers);
        updateMarkerList();
    }
}

// İşaretçi listesini güncelleme
function updateMarkerList() {
    console.log('updateMarkerList called');
    try {
        const markerList = document.getElementById('marker-list');
        if (!markerList) {
            console.error('Marker list element not found');
            return;
        }
        while (markerList.firstChild) {
            markerList.removeChild(markerList.firstChild);
        }
        layers.userMarkers.forEach((marker, idx) => {
            const markerItem = document.createElement('div');
            markerItem.className = 'marker-item';
            markerItem.innerHTML = `
                <p><strong>${marker.title || 'Olay Yeri'}</strong></p>
                <p>Tip: ${marker.type.charAt(0).toUpperCase() + marker.type.slice(1)}</p>
                <p>Koordinatlar: ${marker.lat.toFixed(4)}, ${marker.lng.toFixed(4)}</p>
                <p>Not: ${marker.note || 'Yok'}</p>
                <button class="btn-small btn-primary" onclick="centerMap(${marker.lat}, ${marker.lng})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>
                <button class="btn-small btn-danger" onclick="deleteMarker(${idx})"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" style="width: 16px;"> Sil</button>`;
            markerList.appendChild(markerItem);
        });
    } catch (error) {
        console.error('updateMarkerList error:', error);
    }
}

// İşaretçilere yakınlaştırma
function zoomToFit() {
    if (layers.userMarkers.length === 0) {
        showOverlayMessage('Yakınlaştırılacak işaretçi yok.', true);
        return;
    }
    const bounds = new google.maps.LatLngBounds();
    layers.userMarkers.forEach(marker => bounds.extend(new google.maps.LatLng(marker.lat, marker.lng)));
    map.fitBounds(bounds);
}

// Trafik katmanını açma/kapama
function toggleTraffic() {
    const trafficBtn = document.getElementById('traffic-btn');
    if (!trafficBtn) return;
    if (trafficLayer.getMap()) {
        trafficLayer.setMap(null);
        trafficBtn.textContent = 'Trafik Göster';
    } else {
        trafficLayer.setMap(map);
        trafficBtn.textContent = 'Trafik Gizle';
    }
}

// Hava durumu verisi çekme
async function fetchWeather(city) {
    try {
        const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)},tr&appid=${weatherApiKey}&units=metric&lang=tr`);
        if (!response.ok) throw new Error(`HTTP hatası: ${response.status}`);
        const data = await response.json();
        if (data.cod === 200) {
            const weatherMessage = `
                <div class="weather-info">
                    <img src="http://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png" alt="Hava Durumu">
                    <div>
                        <strong>${data.name}</strong>:<br>
                        Hava: ${data.weather[0].description.charAt(0).toUpperCase() + data.weather[0].description.slice(1)}<br>
                        Sıcaklık: ${data.main.temp.toFixed(1)}°C<br>
                        Hissedilen: ${data.main.feels_like.toFixed(1)}°C<br>
                        Nem: ${data.main.humidity}%<br>
                        Rüzgar: ${(data.wind.speed * 3.6).toFixed(1)} km/s
                    </div>
                </div>`;
            showOverlayMessage(weatherMessage, false);
            return data;
        } else {
            showOverlayMessage(`Şehir bulunamadı: ${city}`, true);
        }
    } catch (error) {
        console.error('Hava durumu alınamadı:', error);
        showOverlayMessage(`Hava durumu alınamadı: ${error.message}`, true);
    }
}

// Hava kalitesi verisi çekme
async function fetchAirQuality(lat, lng, cityName) {
    try {
        let url;
        if (lat && lng) {
            url = `http://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lng}&appid=${weatherApiKey}`;
        } else {
            const weatherData = await fetchWeather(cityName);
            if (!weatherData) return;
            url = `http://api.openweathermap.org/data/2.5/air_pollution?lat=${weatherData.coord.lat}&lon=${weatherData.coord.lon}&appid=${weatherApiKey}`;
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP hatası: ${response.status}`);
        const data = await response.json();
        if (data.list?.[0]) {
            const aqi = data.list[0].main.aqi;
            const components = data.list[0].components;
            const aqiDescription = {
                1: "İyi", 2: "Orta", 3: "Hassas gruplar için sağlıksız", 4: "Sağlıksız", 5: "Çok sağlıksız"
            };
            const aqiClass = {
                1: "good", 2: "moderate", 3: "unhealthy", 4: "unhealthy", 5: "very-unhealthy"
            };
            const airQualityMessage = `
                <div class="air-quality-info ${aqiClass[aqi] || ''}">
                    <strong>Hava Kalitesi (${cityName || 'Konum'})</strong>:<br>
                    Durum: ${aqiDescription[aqi] || "Bilinmiyor"}<br>
                    AQI: ${aqi}<br>
                    PM2.5: ${components.pm2_5.toFixed(1)} µg/m³<br>
                    PM10: ${components.pm10.toFixed(1)} µg/m³
                </div>`;
            showOverlayMessage(airQualityMessage, false);
        } else {
            showOverlayMessage(`Hava kalitesi verisi alınamadı: ${cityName || 'Konum'}`, true);
        }
    } catch (error) {
        console.error('Hava kalitesi alınamadı:', error);
        showOverlayMessage(`Hava kalitesi alınamadı: ${error.message}`, true);
    }
}

// Toplanma alanlarını gösterme
async function showAssemblyAreas(city) {
    try {
        const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)},tr&appid=${weatherApiKey}&units=metric`);
        if (!response.ok) throw new Error(`HTTP hatası: ${response.status}`);
        const data = await response.json();
        if (data.cod === 200) {
            const lat = data.coord.lat;
            const lng = data.coord.lon;
            const placesService = new google.maps.places.PlacesService(map);
            placesService.textSearch({
                query: `Acil durum toplanma alanı near ${city}, Türkiye`,
                location: { lat: lat, lng: lng },
                radius: 10000
            }, (searchData, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && searchData.length > 0) {
                    const newMarkers = [];
                    searchData.slice(0, 5).forEach(place => {
                        if (place.geometry?.location) {
                            const marker = new google.maps.Marker({
                                position: place.geometry.location,
                                map: null,
                                title: place.name,
                                icon: { url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png', scaledSize: new google.maps.Size(45, 45) }
                            });
                            const markerInfo = {
                                lat: place.geometry.location.lat(),
                                lng: place.geometry.location.lng(),
                                title: place.name,
                                note: `Toplanma Alanı | Adres: ${place.formatted_address || 'Bilinmiyor'} | Kapasite: Bilinmiyor`,
                                marker: marker,
                                type: 'assembly'
                            };
                            newMarkers.push(markerInfo);
                            marker.addListener('click', () => {
                                infoWindow.setContent(
                                    `<div style="padding:15px; font-family: Poppins;">
                                        <h3 style="color: #007bff; font-size: 20px;">${place.name}</h3>
                                        <p style="font-size: 16px;">Adres: ${place.formatted_address || 'Bilinmiyor'}</p>
                                        <p style="font-size: 16px;">Tür: ${place.types?.includes('park') ? 'Park' : 'Toplanma Alanı'}</p>
                                        <button class="btn-small btn-primary" onclick="centerMap(${place.geometry.location.lat()}, ${place.geometry.location.lng()})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>
                                    </div>`
                                );
                                infoWindow.open(map, marker);
                            });
                        }
                    });
                    layerManager.updateLayer('assemblyMarkers', newMarkers);
                    layers.assemblyMarkers = newMarkers;
                    layerManager.toggleLayer('assemblyMarkers');
                    document.getElementById('info-panel').innerHTML = `<strong>${city}</strong> için toplanma alanları gösteriliyor.`;
                    const bounds = new google.maps.LatLngBounds();
                    newMarkers.forEach(marker => bounds.extend(new google.maps.LatLng(marker.lat, marker.lng)));
                    map.fitBounds(bounds);
                } else {
                    showOverlayMessage(`Toplanma alanları bulunamadı: ${city}`, true);
                }
            });
        } else {
            showOverlayMessage(`Şehir bulunamadı: ${city}`, true);
        }
    } catch (error) {
        console.error('Toplanma alanları alınamadı:', error);
        showOverlayMessage(`Toplanma alanları alınamadı: ${error.message}`, true);
    }
}

// Yer detaylarını gösterme
function showPlaceDetails(placeId) {
    const detailsElement = document.getElementById('place-details');
    if (!detailsElement) {
        console.error('Place details element not found');
        return;
    }
    while (detailsElement.firstChild) {
        detailsElement.removeChild(detailsElement.firstChild);
    }
    const request = {
        placeId: placeId,
        fields: ['name', 'formatted_address', 'geometry', 'rating', 'user_ratings_total']
    };
    const service = new google.maps.places.PlacesService(map);
    service.getDetails(request, (place, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            const div = document.createElement('div');
            div.innerHTML = `
                <h3>${place.name}</h3>
                <p>Adres: ${place.formatted_address || 'Bilinmiyor'}</p>
                <p>Değerlendirme: ${place.rating || 'Yok'} (${place.user_ratings_total || 0} oy)</p>`;
            detailsElement.appendChild(div);
            detailsElement.style.display = 'block';
        } else {
            console.error('Place details failed:', status);
            showOverlayMessage(`Yer detayları alınamadı: ${status}`, true);
        }
    });
}

// Sokak görünümünü gösterme
function showStreetView(location) {
    const streetViewPane = document.getElementById('street-view-pane');
    if (!streetViewPane) {
        console.error('Street view pane not found');
        return;
    }
    streetViewPanorama.setPosition(location);
    streetViewPanorama.setVisible(true);
    streetViewPane.style.display = 'block';
}

// Yükseklik bilgisi alma
function getElevation(location) {
    const elevationInfo = document.getElementById('elevation-info');
    if (!elevationInfo) {
        console.error('Elevation info element not found');
        return;
    }
    const elevationRequest = {
        locations: [new google.maps.LatLng(location.lat, location.lng)]
    };
    elevationService.getElevationForLocations(elevationRequest, (results, status) => {
        if (status === google.maps.ElevationStatus.OK && results?.[0]) {
            elevationInfo.innerHTML = `Yükseklik: ${results[0].elevation.toFixed(2)} m`;
        } else {
            elevationInfo.innerHTML = 'Yükseklik bilgisi alınamadı.';
        }
    });
}

// Havadan görünüm
map.addListener('zoom_changed', () => {
    const zoom = map.getZoom();
    const aerialView = document.getElementById('aerial-view');
    if (!aerialView) {
        console.error('Aerial view element not found');
        return;
    }
    if (zoom >= 18) {
        const center = map.getCenter();
        aerialView.location = { lat: center.lat(), lng: center.lng() };
        aerialView.style.display = 'block';
    } else {
        aerialView.style.display = 'none';
    }
});

function displayAssemblyAreas() {
    console.log('displayAssemblyAreas called');
    if (!window.ASSEMBLY_DATA) {
        console.error('ASSEMBLY_DATA not found');
        showOverlayMessage('Toplanma alanı verileri bulunamadı.', true);
        return;
    }

    // Mevcut marker'ları temizle
    assemblyMarkers.forEach(marker => marker.setMap(null));
    assemblyMarkers = [];

    window.ASSEMBLY_DATA.forEach(area => {
        const marker = new google.maps.Marker({
            position: { lat: area.lat, lng: area.lng },
            map: map,
            title: area.name,
            icon: {
                url: 'https://cdn-icons-png.flaticon.com/512/684/684908.png', // Toplanma alanı ikonu
                scaledSize: new google.maps.Size(32, 32)
            }
        });

        const infoContent = `
            <div style="padding: 10px;">
                <h3>${area.name}</h3>
                <p><strong>Kapasite:</strong> ${area.capacity} kişi</p>
                <p><strong>Durum:</strong> ${area.status}</p>
                <p><strong>Kaynaklar:</strong> ${area.resources || 'Yok'}</p>
            </div>
        `;

        marker.addListener('click', () => {
            infoWindow.setContent(infoContent);
            infoWindow.open(map, marker);
        });

        assemblyMarkers.push(marker);
    });

    console.log('Assembly markers created:', assemblyMarkers.length);
}

// Ekip modalını gösterme
function showTeamModal() {
    const teamModal = document.getElementById('team-modal');
    if (!teamModal) {
        console.error('Team modal not found');
        return;
    }
    teamModal.style.display = 'block';
    const teamNameInput = document.getElementById('team-name');
    if (teamNameInput) teamNameInput.focus();
}

// Çadırkent modalını gösterme
function showTentcityModal() {
    const tentcityModal = document.getElementById('tentcity-modal');
    if (!tentcityModal) {
        console.error('Tentcity modal not found');
        return;
    }
    tentcityModal.style.display = 'block';
    const tentcityNameInput = document.getElementById('tentcity-name');
    if (tentcityNameInput) tentcityNameInput.focus();
}

// Ekip modalını kapatma
function closeTeamModal() {
    const teamModal = document.getElementById('team-modal');
    if (!teamModal) return;
    teamModal.style.display = 'none';
    const teamForm = document.getElementById('team-form');
    if (teamForm) teamForm.reset();
}

// Çadırkent modalını kapatma
function closeTentcityModal() {
    const tentcityModal = document.getElementById('tentcity-modal');
    if (!tentcityModal) return;
    tentcityModal.style.display = 'none';
    const tentcityForm = document.getElementById('tentcity-form');
    if (tentcityForm) tentcityForm.reset();
}

// Mevcut konumu alma
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(userLocation);
                map.setZoom(12);
                const note = prompt("Bu işaretçi için bir not ekleyin (isteğe bağlı):") || "";
                addMarker(
                    new google.maps.LatLng(userLocation.lat, userLocation.lng),
                    'Konumum',
                    note,
                    'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                    'general'
                );
            },
            error => {
                console.warn('Konum alınamadı:', error.message);
                showOverlayMessage('Konum alınamadı, varsayılan konuma geçiliyor.', true);
            }
        );
    } else {
        console.warn('Tarayıcı konum servisini desteklemiyor.');
        showOverlayMessage('Tarayıcınız konum servisini desteklemiyor.', true);
    }
}

// Mesaj overlay'i gösterme
function showOverlayMessage(message, isError) {
    const overlay = document.getElementById('overlay-info');
    if (!overlay) {
        console.error('Overlay info element not found');
        return;
    }
    overlay.innerHTML = `
        <button class="close-btn" onclick="this.parentElement.classList.remove('show'); setTimeout(() => { this.parentElement.style.display='none'; }, 300);">✕</button>
        ${message}`;
    overlay.style.display = 'block';
    setTimeout(() => overlay.classList.add('show'), 10);
    if (!isError) {
        setTimeout(() => {
            overlay.classList.remove('show');
            setTimeout(() => overlay.style.display = 'none', 300);
        }, 15000);
    }
}

// Heatmap başlatma
function initHeatmap() {
    const heatmapData = layers.earthquakeMarkers.map(markerInfo => markerInfo.marker.getPosition());
    layers.heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        map: null,
        radius: 20,
        opacity: 0.6
    });
    layerManager.updateLayer('heatmap', [layers.heatmap]);
}

// Çadırkentleri yükleme
function loadTentcities() {
    try {
        const tentcities = window.TENTCITY_DATA || [];
        if (!tentcities.length) {
            console.warn('Çadırkent verisi bulunamadı');
            showOverlayMessage('Çadırkent verisi bulunamadı.', true);
            return;
        }
        const newMarkers = [];

        tentcities.forEach(tentcity => {
            const latLng = new google.maps.LatLng(tentcity.latitude, tentcity.longitude);
            const marker = new google.maps.Marker({
                position: latLng,
                map: map,
                title: tentcity.name,
                icon: { url: 'https://cdn-icons-png.flaticon.com/512/2457/2457421.png', scaledSize: new google.maps.Size(45, 45) }
            });

            const markerInfo = {
                lat: tentcity.latitude,
                lng: tentcity.longitude,
                title: tentcity.name,
                note: `Şehir: ${tentcity.city} | Kuruluş: ${tentcity.established_date}`,
                marker: marker,
                type: 'tentcity'
            };
            newMarkers.push(markerInfo);

            marker.addListener('click', () => {
                infoWindow.setContent(
                    `<div style="padding:15px; font-family: Poppins;">
                        <h3 style="color: #007bff; font-size: 20px;">${tentcity.name}</h3>
                        <p style="font-size: 16px;">Şehir: ${tentcity.city}</p>
                        <p style="font-size: 16px;">Kuruluş: ${tentcity.established_date}</p>
                        <p style="font-size: 16px;">Koordinatlar: ${tentcity.latitude.toFixed(4)}, ${tentcity.longitude.toFixed(4)}</p>
                        <button class="btn-small btn-primary" onclick="centerMap(${tentcity.latitude}, ${tentcity.longitude})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>
                    </div>`
                );
                infoWindow.open(map, marker);
            });
        });

        layerManager.updateLayer('tentcityMarkers', newMarkers);
        layers.tentcityMarkers = newMarkers;
        console.log(`Loaded ${newMarkers.length} tentcity markers`);
    } catch (error) {
        console.error('Çadırkent verileri yüklenemedi:', error);
        showOverlayMessage(`Çadırkent verileri yüklenemedi: ${error.message}`, true);
    }
}

// Deprem verilerini yükleme
function loadEarthquakes() {
    try {
        const earthquakes = window.EARTHQUAKE_DATA || [];
        if (!earthquakes.length) {
            console.warn('Deprem verisi bulunamadı, USGS verilerine geçiliyor');
            fetchEarthquakes();
            return;
        }
        const newMarkers = [];

        earthquakes.forEach(eq => {
            const latLng = new google.maps.LatLng(eq.lat, eq.lon);
            const marker = new google.maps.Marker({
                position: latLng,
                map: map,
                title: `Deprem: ${eq.place}`,
                icon: { url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png', scaledSize: new google.maps.Size(45, 45) }
            });

            const markerInfo = {
                lat: eq.lat,
                lng: eq.lon,
                title: `Deprem: ${eq.place}`,
                note: `Büyüklük: ${eq.magnitude} | Tarih: ${eq.date} ${eq.time}`,
                marker: marker,
                type: 'earthquake'
            };
            newMarkers.push(markerInfo);

            marker.addListener('click', () => {
                infoWindow.setContent(
                    `<div style="padding:15px; font-family: Poppins;">
                        <h3 style="color: #007bff; font-size: 20px;">Deprem: ${eq.place}</h3>
                        <p style="font-size: 16px;">Tarih: ${eq.date} ${eq.time}</p>
                        <p style="font-size: 16px;">Büyüklük: ${eq.magnitude}</p>
                        <p style="font-size: 16px;">Koordinatlar: ${eq.lat.toFixed(4)}, ${eq.lon.toFixed(4)}</p>
                        <button class="btn-small btn-primary" onclick="centerMap(${eq.lat}, ${eq.lon})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>
                    </div>`
                );
                infoWindow.open(map, marker);
            });
        });

        layerManager.updateLayer('earthquakeMarkers', newMarkers);
        layers.earthquakeMarkers = newMarkers;
        initHeatmap();
        console.log(`Loaded ${newMarkers.length} earthquake markers`);
    } catch (error) {
        console.error('Deprem verileri yüklenemedi:', error);
        showOverlayMessage(`Deprem verileri yüklenemedi: ${error.message}`, true);
    }
}

// Haritayı merkeze alma
function centerMap(lat, lng) {
    map.setCenter({ lat: lat, lng: lng });
    map.setZoom(15);
}

// En kısa yolu hesaplama
function calculateShortestPath() {
    if (layers.userMarkers.length < 2) {
        showOverlayMessage('En kısa yol için en az 2 nokta gerekli!', true);
        return;
    }

    const waypoints = layers.userMarkers.slice(1, -1).map(marker => ({
        location: new google.maps.LatLng(marker.lat, marker.lng),
        stopover: true
    }));

    const request = {
        origin: new google.maps.LatLng(layers.userMarkers[0].lat, layers.userMarkers[0].lng),
        destination: new google.maps.LatLng(layers.userMarkers[layers.userMarkers.length - 1].lat, layers.userMarkers[layers.userMarkers.length - 1].lng),
        waypoints: waypoints,
        optimizeWaypoints: true,
        travelMode: google.maps.TravelMode.DRIVING
    };

    directionsService.route(request, (response, status) => {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsRenderer.setDirections(response);
            const route = response.routes[0];
            let distance = 0;
            let duration = 0;
            route.legs.forEach(leg => {
                distance += leg.distance.value;
                duration += leg.duration.value;
            });
            const info = `
                <div class="route-info">
                    <h3>Rota Bilgisi</h3>
                    <p>Toplam Mesafe: ${(distance / 1000).toFixed(2)} km</p>
                    <p>Tahmini Süre: ${Math.round(duration / 60)} dakika</p>
                </div>`;
            document.getElementById('info-panel').innerHTML = info;
        } else {
            showOverlayMessage(`Rota hesaplanamadı: ${status}`, true);
        }
    });
}

// Üçgen çizme
function startTriangleDraw() {
    drawingManager.setDrawingMode(null);
    showOverlayMessage('Üçgen çizmek için merkez noktayı seçin', false);

    const clickListener = map.addListener('click', e => {
        const center = e.latLng;
        const radius = 1000;
        const points = 3;
        const coords = [];

        for (let i = 0; i < points; i++) {
            const angle = (2 * Math.PI * i) / points;
            coords.push(new google.maps.LatLng(
                center.lat() + (radius / 111000) * Math.cos(angle),
                center.lng() + (radius / (111000 * Math.cos(center.lat() * Math.PI / 180))) * Math.sin(angle)
            ));
        }

        const triangle = new google.maps.Polygon({
            paths: coords,
            map: map,
            strokeColor: '#FF4500',
            strokeWeight: 2,
            fillColor: '#FF4500',
            fillOpacity: 0.3,
            editable: true,
            draggable: true
        });

        const note = prompt('Üçgen için not ekleyin:', '') || 'Not eklenmedi';
        polygonNotes.set(triangle, note);
        polygons.push(triangle);
        const area = google.maps.geometry.spherical.computeArea(triangle.getPath()) / 1000000;
        document.getElementById('info-panel').innerHTML = `Üçgen Alanı: ${area.toFixed(2)} km²<br>Not: ${note}`;

        google.maps.event.addListener(triangle, 'click', function() {
            activePolygon = triangle;
            showPolygonModal(triangle);
        });

        google.maps.event.removeListener(clickListener);
    });
}


// İşaretçi türü seçme
function selectMarkerType(type) {
    selectedMarkerType = type;
    showOverlayMessage(`"${type.charAt(0).toUpperCase() + type.slice(1)}" işaretçisi eklemek için haritaya tıklayın.`, false);
}
function updatePolygonInfoWindow() {
    const shape = activePolygon;
    if (!shape) {
        console.error('No active polygon');
        return;
    }
    const existingNote = polygonNotes.get(shape) || 'Not eklenmedi';
    let area, shapeType, position;

    if (shape instanceof google.maps.Polygon) {
        area = google.maps.geometry.spherical.computeArea(shape.getPath()) / 1000000;
        shapeType = 'Poligon';
        // Poligon için sınırları manuel olarak hesapla
        const bounds = new google.maps.LatLngBounds();
        shape.getPath().forEach(latLng => bounds.extend(latLng));
        position = bounds.getCenter();
    } else if (shape instanceof google.maps.Circle) {
        const radius = shape.getRadius();
        area = Math.PI * radius * radius / 1000000;
        shapeType = 'Daire';
        position = shape.getCenter();
    } else if (shape instanceof google.maps.Rectangle) {
        const bounds = shape.getBounds();
        const ne = bounds.getNorthEast();
        const sw = bounds.getSouthWest();
        const width = google.maps.geometry.spherical.computeDistanceBetween(
            new google.maps.LatLng(ne.lat(), sw.lng()),
            new google.maps.LatLng(ne.lat(), ne.lng())
        );
        const height = google.maps.geometry.spherical.computeDistanceBetween(
            new google.maps.LatLng(ne.lat(), sw.lng()),
            new google.maps.LatLng(sw.lat(), sw.lng())
        );
        area = (width * height) / 1000000;
        shapeType = 'Kare/Dikdörtgen';
        position = bounds.getCenter();
    } else {
        console.error('Unknown shape type:', shape);
        return;
    }

    infoWindow.setContent(
        `<div style="padding: 10px;">
            <h3>${shapeType} Bilgisi</h3>
            <p>Alan: ${area.toFixed(2)} km²</p>
            <p>Not: ${existingNote}</p>
            <button onclick="editPolygonNote()" class="btn-custom">Notu Düzenle</button>
            <button onclick="deletePolygon()" class="btn-custom btn-danger">Sil</button>
        </div>`
    );
    infoWindow.setPosition(position);
    infoWindow.open(map);
}

function showPolygonInfo(coords) {
    let info = '<div><h4>Poligon Bilgisi</h4><p><strong>Koordinatlar:</strong></p><ul>';
    coords.forEach(coord => {
        info += `<li>Lat: ${coord.lat().toFixed(4)}, Lng: ${coord.lng().toFixed(4)}</li>`;
    });
    info += '</ul></div>';
    document.getElementById('info-panel').innerHTML = info;
}
// Poligon modalını gösterme
function showPolygonModal(shape) {
    console.log('showPolygonModal called, shape:', shape, 'type:', shape.constructor.name);
    const modal = document.getElementById('polygon-modal');
    const infoDiv = document.getElementById('polygon-info');

    // Modal ve infoDiv varlığını kontrol et
    if (!modal || !infoDiv) {
        console.error('Modal or info div not found:', { modal, infoDiv });
        showOverlayMessage('Poligon modalı bulunamadı.', true);
        return;
    }

    try {
        let area, shapeType;
        if (shape instanceof google.maps.Polygon) {
            area = google.maps.geometry.spherical.computeArea(shape.getPath()) / 1000000;
            shapeType = 'Poligon';
        } else if (shape instanceof google.maps.Circle) {
            area = (Math.PI * shape.getRadius() * shape.getRadius()) / 1000000;
            shapeType = 'Daire';
        } else if (shape instanceof google.maps.Rectangle) {
            const bounds = shape.getBounds();
            const ne = bounds.getNorthEast();
            const sw = bounds.getSouthWest();
            const width = google.maps.geometry.spherical.computeDistanceBetween(
                new google.maps.LatLng(ne.lat(), sw.lng()),
                new google.maps.LatLng(ne.lat(), ne.lng())
            );
            const height = google.maps.geometry.spherical.computeDistanceBetween(
                new google.maps.LatLng(ne.lat(), sw.lng()),
                new google.maps.LatLng(sw.lat(), sw.lng())
            );
            area = (width * height) / 1000000;
            shapeType = 'Kare/Dikdörtgen';
        } else {
            console.error('Invalid shape type:', shape);
            showOverlayMessage('Geçersiz poligon türü.', true);
            return;
        }

        const note = polygonNotes.get(shape) || 'Yok';
        console.log('Retrieved note for shape:', note);

        // Modal içeriğini güncelle
        infoDiv.innerHTML = `
            <p><strong>Tür:</strong> ${shapeType}</p>
            <p><strong>Alan:</strong> ${area.toFixed(2)} km²</p>
            <p><strong>Not:</strong> ${note}</p>
            <button class="btn-custom" onclick="editPolygonNote()">Notu Düzenle</button>
            <button class="btn-custom btn-danger" onclick="deletePolygon()">Sil</button>
        `;

        // Modal'ı görünür yap
        modal.style.display = 'block';
        modal.style.visibility = 'visible';
        modal.style.opacity = '1';
        console.log('Modal display set to:', modal.style.display);

        // Modal kapatma butonu için olay dinleyicisi
        const closeBtn = modal.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.onclick = () => closePolygonModal();
        } else {
            console.warn('Modal close button not found');
        }
    } catch (error) {
        console.error('showPolygonModal error:', error);
        showOverlayMessage(`Poligon modalı gösterilemedi: ${error.message}`, true);
    }
}

// Poligon modalını kapatma
function closePolygonModal() {
    console.log('closePolygonModal called');
    const modal = document.getElementById('polygon-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.style.visibility = 'hidden';
        modal.style.opacity = '0';
        console.log('Modal closed');
    } else {
        console.error('Polygon modal not found');
    }
}

// Poligon notunu düzenleme
function editPolygonNote() {
    console.log('editPolygonNote called, activePolygon:', activePolygon);
    try {
        if (!activePolygon) {
            console.error('No active polygon');
            showOverlayMessage('Not düzenlenemedi: Aktif poligon bulunamadı.', true);
            return;
        }

        const currentNote = polygonNotes.get(activePolygon) || '';
        console.log('Current note:', currentNote);
        const newNote = prompt('Yeni notu girin:', currentNote) || currentNote;
        console.log('New note:', newNote);
        polygonNotes.set(activePolygon, newNote);
        console.log('Note updated for shape:', newNote);

        // Modal'ı güncelle
        showPolygonModal(activePolygon);
        document.getElementById('info-panel').innerHTML = `Not güncellendi: ${newNote}`;
    } catch (error) {
        console.error('editPolygonNote error:', error);
        showOverlayMessage(`Not düzenlenemedi: ${error.message}`, true);
    }
}

// Poligon silme
function deletePolygon() {
    console.log('deletePolygon called, activePolygon:', activePolygon);
    try {
        if (!activePolygon) {
            console.error('No active polygon');
            showOverlayMessage('Silinecek poligon bulunamadı.', true);
            return;
        }

        activePolygon.setMap(null);
        polygons = polygons.filter(p => p !== activePolygon);
        polygonNotes.delete(activePolygon);
        activePolygon = null;
        closePolygonModal();
        document.getElementById('info-panel').innerHTML = 'Poligon silindi.';
        console.log('Polygon deleted');
    } catch (error) {
        console.error('deletePolygon error:', error);
        showOverlayMessage(`Poligon silinemedi: ${error.message}`, true);
    }
}