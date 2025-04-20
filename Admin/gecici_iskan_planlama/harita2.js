let map, markers = [], earthquakeMarkers = [], infoWindow, autocomplete, weatherAutocomplete, trafficLayer, drawingManager, polygons = [], heatmap;
let streetViewPanorama, elevationService;
let userLocation = null;
let selectedMarkerType = null;
let pendingTeamMarker = null;
let directionsService, directionsRenderer;
let activePolygon = null;
let polygonNotes = new Map();

// API keys and earthquakes data will be set by Python
const weatherApiKey = window.WEATHER_API_KEY || '';
const earthquakes = window.EARTHQUAKES || [];

function initMap() {
    try {
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
                drawingModes: [
                    'polygon',
                    'circle',
                    'rectangle'
                ]
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
            circleOptions: {
                fillColor: "#4CAF50",
                fillOpacity: 0.3,
                strokeWeight: 2,
                strokeColor: "#4CAF50",
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
            }
        });
        drawingManager.setMap(map);

        // Directions Service başlat
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

        // Polygon tamamlandığında not ekleme
        google.maps.event.addListener(drawingManager, 'overlaycomplete', function(event) {
            let shape = event.overlay;
            activePolygon = shape;
            
            // Not ekleme dialogunu göster
            const note = prompt('Bu alan için not ekleyin:', '');
            if (note) {
                polygonNotes.set(shape, note);
                
                // Şekle tıklama event listener'ı ekle
                google.maps.event.addListener(shape, 'click', function() {
                    const existingNote = polygonNotes.get(shape);
                    infoWindow.setContent(
                        '<div style="padding: 10px;">' +
                        '<h3>Alan Bilgisi</h3>' +
                        '<p>Not: ' + existingNote + '</p>' +
                        '<button onclick="editPolygonNote()" class="btn-custom">Notu Düzenle</button>' +
                        '</div>'
                    );
                    infoWindow.setPosition(shape.getBounds().getCenter());
                    infoWindow.open(map);
                });
            }
            
            // Şekil tipine göre bilgi göster
            let shapeInfo = '';
            if (event.type === 'polygon') {
                const path = shape.getPath();
                const area = google.maps.geometry.spherical.computeArea(path);
                shapeInfo = 'Poligon Alanı: ' + (area / 1000000).toFixed(2) + ' km²';
            } else if (event.type === 'circle') {
                const radius = shape.getRadius();
                const area = Math.PI * radius * radius;
                shapeInfo = 'Daire Alanı: ' + (area / 1000000).toFixed(2) + ' km²<br>Yarıçap: ' + (radius / 1000).toFixed(2) + ' km';
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
                shapeInfo = 'Dikdörtgen Alanı: ' + ((width * height) / 1000000).toFixed(2) + ' km²';
            }
            
            document.getElementById('info-panel').innerHTML = shapeInfo + '<br>Not: ' + (note || 'Not eklenmedi');
        });

        // Harita tıklama olayı
        map.addListener('click', e => {
            if (selectedMarkerType) {
                const latLng = e.latLng;
                const note = prompt("Bu işaretçi için bir not ekleyin (isteğe bağlı):") || "";
                if (selectedMarkerType === 'team') {
                    pendingTeamMarker = { latLng: latLng, note: note };
                    showTeamModal();
                } else {
                    let title, iconUrl;
                    switch (selectedMarkerType) {
                        case 'ambulance':
                            title = 'Ambulans';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/2979/2979016.png';
                            break;
                        case 'police':
                            title = 'Polis';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/3063/3063177.png';
                            break;
                        case 'gendarmerie':
                            title = 'Jandarma';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/1865/1865269.png';
                            break;
                        case 'soldier':
                            title = 'Asker';
                            iconUrl = 'https://cdn-icons-png.flaticon.com/512/1865/1865269.png';
                            break;
                        case 'general':
                            title = 'Olay Yeri';
                            iconUrl = 'https://maps.google.com/mapfiles/ms/icons/red-dot.png';
                            break;
                        default:
                            return;
                    }
                    addMarker(latLng, title, note, iconUrl, selectedMarkerType);
                    map.setCenter(latLng);
                    map.setZoom(12);
                    fetchAirQuality(latLng.lat(), latLng.lng());
                    getElevation({ lat: latLng.lat(), lng: latLng.lng() });
                    selectedMarkerType = null;
                }
            }
        });

        // Yer arama
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            autocomplete = new google.maps.places.Autocomplete(searchInput, {
                types: ['(regions)'],
                componentRestrictions: { country: 'tr' },
                fields: ['geometry', 'name', 'formatted_address', 'place_id']
            });
            autocomplete.bindTo('bounds', map);
            autocomplete.addListener('place_changed', () => {
                const place = autocomplete.getPlace();
                if (!place.geometry) {
                    showOverlayMessage("Seçilen yer için detay bulunamadı: '" + place.name + "'", true);
                    return;
                }
                map.setCenter(place.geometry.location);
                map.setZoom(13);
                showPlaceDetails(place.place_id);
                showStreetView(place.geometry.location);
                getElevation({ lat: place.geometry.location.lat(), lng: place.geometry.location.lng() });
            });

            searchInput.addEventListener('input', () => {
                const query = searchInput.value;
                if (query.length > 2) {
                    const request = {
                        query: query,
                        fields: ['name', 'geometry', 'place_id'],
                        locationBias: { lat: 39.9334, lng: 32.8597 },
                        componentRestrictions: { country: 'tr' }
                    };
                    const placesService = new google.maps.places.PlacesService(map);
                    placesService.findPlaceFromQuery(request, (searchData, status) => {
                        if (status === google.maps.places.PlacesServiceStatus.OK && searchData) {
                            clearMarkers();
                            searchData.forEach(place => {
                                if (place.geometry && place.geometry.location) {
                                    const marker = new google.maps.Marker({
                                        position: place.geometry.location,
                                        map: map,
                                        title: place.name,
                                        icon: {
                                            url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                                            scaledSize: new google.maps.Size(45, 45)
                                        }
                                    });
                                    markers.push({ marker: marker, place_id: place.place_id, type: 'search' });
                                    marker.addListener('click', () => {
                                        showPlaceDetails(place.place_id);
                                        showStreetView(place.geometry.location);
                                        getElevation({ lat: place.geometry.location.lat(), lng: place.geometry.location.lng() });
                                    });
                                }
                            });
                            updateSearchResults(searchData);
                            if (searchData[0]?.geometry?.location) {
                                map.setCenter(searchData[0].geometry.location);
                                map.setZoom(12);
                            }
                        }
                    });
                }
            });
        }

        // Şehir arama (hava durumu)
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
                    showOverlayMessage("Şehir bulunamadı: '" + weatherInput.value + "'", true);
                    return;
                }
                fetchWeather(place.name);
                if (place.geometry?.location) {
                    map.setCenter(place.geometry.location);
                    map.setZoom(10);
                }
            });
        }

        // PlaceDetailsElement
        function showPlaceDetails(placeId) {
            const detailsElement = document.getElementById('place-details');
            detailsElement.placeId = placeId;
            detailsElement.style.display = 'block';
        }

        // Street View
        function showStreetView(location) {
            streetViewPanorama.setPosition(location);
            streetViewPanorama.setVisible(true);
            document.getElementById('street-view-pane').style.display = 'block';
        }

        // Elevation API
        function getElevation(location) {
            const elevationRequest = {
                locations: [new google.maps.LatLng(location.lat, location.lng)]
            };
            elevationService.getElevationForLocations(elevationRequest, (results, status) => {
                if (status === google.maps.ElevationStatus.OK && results?.[0]) {
                    document.getElementById('elevation-info').innerHTML = 'Yükseklik: ' + results[0].elevation.toFixed(2) + ' m';
                } else {
                    document.getElementById('elevation-info').innerHTML = 'Yükseklik bilgisi alınamadı.';
                }
            });
        }

        // Aerial View
        map.addListener('zoom_changed', () => {
            const zoom = map.getZoom();
            const aerialView = document.getElementById('aerial-view');
            if (zoom >= 18) {
                const center = map.getCenter();
                aerialView.location = { lat: center.lat(), lng: center.lng() };
                aerialView.style.display = 'block';
            } else {
                aerialView.style.display = 'none';
            }
        });

        // Arama sonuçlarını güncelle
        function updateSearchResults(searchData) {
            const resultList = document.getElementById('search-results');
            resultList.innerHTML = '';
            searchData.forEach(place => {
                const li = document.createElement('li');
                li.textContent = place.name;
                li.style.cursor = 'pointer';
                li.addEventListener('click', () => {
                    map.setCenter(place.geometry.location);
                    map.setZoom(14);
                    showPlaceDetails(place.place_id);
                    showStreetView(place.geometry.location);
                    getElevation({ lat: place.geometry.location.lat(), lng: place.geometry.location.lng() });
                });
                resultList.appendChild(li);
            });
        }

        // Sidebar toggle
        document.getElementById('toggle-btn').addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            const btn = document.getElementById('toggle-btn');
            if (sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                btn.style.left = '20px';
                btn.textContent = '☰';
            } else {
                sidebar.classList.add('open');
                btn.style.left = '380px';
                btn.textContent = '✕';
            }
        });

        // Hava durumu arama butonu
        document.getElementById('weather-search-btn').addEventListener('click', () => {
            const city = document.getElementById('weather-input').value;
            if (city) {
                fetchWeather(city);
            } else {
                showOverlayMessage('Lütfen bir şehir adı girin.', true);
            }
        });

        // Ekip modal olayları
        document.getElementById('team-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const teamName = document.getElementById('team-name').value;
            const teamStatus = document.getElementById('team-status').value;
            const teamType = document.getElementById('team-type').value;
            if (!teamName) {
                showOverlayMessage('Lütfen bir ekip adı girin.', true);
                return;
            }
            const note = pendingTeamMarker.note + (pendingTeamMarker.note ? ' | ' : '') +
                         'Aktiflik: ' + teamStatus + ' | Tür: ' + (teamType || 'Belirtilmemiş');
            addMarker(pendingTeamMarker.latLng, teamName, note, 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png', 'team');
            map.setCenter(pendingTeamMarker.latLng);
            map.setZoom(12);
            fetchAirQuality(pendingTeamMarker.latLng.lat(), pendingTeamMarker.latLng.lng());
            getElevation({ lat: pendingTeamMarker.latLng.lat(), lng: pendingTeamMarker.latLng.lng() });
            closeTeamModal();
            selectedMarkerType = null;
            pendingTeamMarker = null;
        });

        document.getElementById('cancel-team-btn').addEventListener('click', () => {
            closeTeamModal();
            selectedMarkerType = null;
            pendingTeamMarker = null;
        });

        // Diğer buton event'leri
        document.getElementById('clear-markers').addEventListener('click', clearMarkers);
        document.getElementById('zoom-to-fit').addEventListener('click', zoomToFit);
        document.getElementById('current-location').addEventListener('click', getCurrentLocation);
        document.getElementById('traffic-btn').addEventListener('click', toggleTraffic);
        document.getElementById('clear-polygons').addEventListener('click', () => {
            polygons.forEach(polygon => polygon.setMap(null));
            polygons = [];
            document.getElementById('info-panel').innerHTML = 'Poligonlar temizlendi.';
        });
        document.getElementById('heatmap-btn').addEventListener('click', toggleHeatmap);
        document.getElementById('air-quality-btn').addEventListener('click', () => {
            const city = document.getElementById('weather-input').value || 'Ankara';
            fetchWeather(city);
        });
        document.getElementById('assembly-areas-btn').addEventListener('click', () => {
            const city = document.getElementById('weather-input').value || 'Ankara';
            showAssemblyAreas(city);
        });
        document.getElementById('toggle-3d-btn').addEventListener('click', () => {
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

        // Event listeners ekle
        document.getElementById('shortest-path-btn').addEventListener('click', calculateShortestPath);
        document.getElementById('draw-hexagon-btn').addEventListener('click', startHexagonDraw);

        getCurrentLocation();
        setInterval(checkProximityAlerts, 300000);
        displayEarthquakes();
        initHeatmap();
    } catch (error) {
        console.error('initMap failed:', error);
        showOverlayMessage('Harita yüklenemedi: ' + error.message, true);
    }
}

function addMarker(latLng, title, note, iconUrl, markerType) {
    const marker = new google.maps.Marker({
        position: latLng,
        map: map,
        title: title || "Olay Yeri",
        icon: {
            url: iconUrl,
            scaledSize: new google.maps.Size(45, 45)
        },
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
    markers.push(markerInfo);
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
            '<div style="padding:15px; font-family: Poppins;">' +
            '<h3 style="color: #007bff; font-size: 20px;">' + (title || 'Olay Yeri') + '</h3>' +
            '<p style="font-size: 16px;">Tip: ' + (markerType.charAt(0).toUpperCase() + markerType.slice(1)) + '</p>' +
            '<p style="font-size: 16px;">Koordinatlar: ' + latLng.lat().toFixed(4) + ', ' + latLng.lng().toFixed(4) + '</p>' +
            '<p style="font-size: 16px;">Not: ' + (note || 'Yok') + '</p>' +
            '<button class="btn-small btn-primary" onclick="centerMap(' + latLng.lat() + ', ' + latLng.lng() + ')"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>' +
            '<button class="btn-small btn-danger" onclick="deleteMarker(' + markers.indexOf(markerInfo) + ')"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" style="width: 16px;"> Sil</button>' +
            '</div>'
        );
        infoWindow.open(map, marker);
    });
}

function deleteMarker(index) {
    console.log("Marker siliniyor, index:", index);
    if (index < 0 || index >= markers.length) {
        console.error("Geçersiz marker index:", index);
        return;
    }
    const markerInfo = markers[index];
    if (markerInfo.marker) {
        markerInfo.marker.setMap(null);
        console.log("Marker haritadan kaldırıldı:", markerInfo.title);
    }
    markers.splice(index, 1);
    updateMarkerList();
}

function updateMarkerList() {
    const markerList = document.getElementById('marker-list');
    markerList.innerHTML = '';
    markers.forEach((marker, idx) => {
        const markerItem = document.createElement('div');
        markerItem.className = 'marker-item';
        markerItem.innerHTML = 
            '<p><strong>' + (marker.title || 'Olay Yeri') + '</strong></p>' +
            '<p>Tip: ' + (marker.type.charAt(0).toUpperCase() + marker.type.slice(1)) + '</p>' +
            '<p>Koordinatlar: ' + marker.lat.toFixed(4) + ', ' + marker.lng.toFixed(4) + '</p>' +
            '<p>Not: ' + (marker.note || 'Yok') + '</p>' +
            '<button class="btn-small btn-primary" onclick="centerMap(' + marker.lat + ', ' + marker.lng + ')"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>' +
            '<button class="btn-small btn-danger" onclick="deleteMarker(' + idx + ')"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" style="width: 16px;"> Sil</button>';
        markerList.appendChild(markerItem);
    });
}

function clearMarkers() {
    markers.forEach(marker => marker.marker.setMap(null));
    markers = [];
    updateMarkerList();
}

function zoomToFit() {
    if (markers.length === 0) {
        showOverlayMessage('Yakınlaştırılacak işaretçi yok.', true);
        return;
    }
    const bounds = new google.maps.LatLngBounds();
    markers.forEach(marker => bounds.extend(new google.maps.LatLng(marker.lat, marker.lng)));
    map.fitBounds(bounds);
}

function toggleTraffic() {
    if (trafficLayer.getMap()) {
        trafficLayer.setMap(null);
        document.getElementById('traffic-btn').textContent = 'Trafik Göster';
    } else {
        trafficLayer.setMap(map);
        document.getElementById('traffic-btn').textContent = 'Trafik Gizle';
    }
}

async function fetchWeather(city) {
    try {
        const response = await fetch('https://api.openweathermap.org/data/2.5/weather?q=' + encodeURIComponent(city) + ',tr&appid=' + weatherApiKey + '&units=metric&lang=tr');
        if (!response.ok) throw new Error('HTTP hatası: ' + response.status);
        const data = await response.json();
        if (data.cod === 200) {
            const weatherIcon = 'http://openweathermap.org/img/wn/' + data.weather[0].icon + '@2x.png';
            const weatherMessage = 
                '<div class="weather-info">' +
                '<img src="' + weatherIcon + '" alt="Hava Durumu">' +
                '<div>' +
                '<strong>' + data.name + '</strong>:<br>' +
                'Hava: ' + data.weather[0].description.charAt(0).toUpperCase() + data.weather[0].description.slice(1) + '<br>' +
                'Sıcaklık: ' + data.main.temp.toFixed(1) + '°C<br>' +
                'Hissedilen: ' + data.main.feels_like.toFixed(1) + '°C<br>' +
                'Nem: ' + data.main.humidity + '%<br>' +
                'Rüzgar: ' + (data.wind.speed * 3.6).toFixed(1) + ' km/s' +
                '</div>' +
                '</div>';
            const lat = data.coord.lat;
            const lng = data.coord.lon;
            fetchAirQuality(lat, lng, data.name, weatherMessage);
            map.setCenter({ lat: lat, lng: lng });
            map.setZoom(10);
        } else {
            showOverlayMessage('Şehir bulunamadı: ' + city + '. Lütfen geçerli bir şehir adı girin.', true);
        }
    } catch (error) {
        console.error('Hava durumu alınamadı:', error);
        showOverlayMessage('Hava durumu alınamadı: ' + error.message + '. Lütfen API anahtarınızı veya internet bağlantınızı kontrol edin.', true);
    }
}

async function fetchAirQuality(lat, lng, cityName, weatherMessage) {
    try {
        const response = await fetch('http://api.openweathermap.org/data/2.5/air_pollution?lat=' + lat + '&lon=' + lng + '&appid=' + weatherApiKey);
        if (!response.ok) throw new Error('HTTP hatası: ' + response.status);
        const data = await response.json();
        if (data.list?.[0]) {
            const aqi = data.list[0].main.aqi;
            const components = data.list[0].components;
            const aqiDescription = {
                1: "İyi",
                2: "Orta",
                3: "Hassas gruplar için sağlıksız",
                4: "Sağlıksız",
                5: "Çok sağlıksız"
            };
            const aqiClass = {
                1: "good",
                2: "moderate",
                3: "unhealthy",
                4: "unhealthy",
                5: "very-unhealthy"
            };
            const airQualityMessage = 
                '<div class="air-quality-info ' + (aqiClass[aqi] || '') + '">' +
                '<strong>Hava Kalitesi (' + cityName + ')</strong>:<br>' +
                'Durum: ' + (aqiDescription[aqi] || "Bilinmiyor") + '<br>' +
                'AQI: ' + aqi + '<br>' +
                'PM2.5: ' + components.pm2_5.toFixed(1) + ' µg/m³<br>' +
                'PM10: ' + components.pm10.toFixed(1) + ' µg/m³' +
                '</div>';
            showOverlayMessage(weatherMessage + airQualityMessage, false);
        } else {
            showOverlayMessage('Hava kalitesi verisi alınamadı: ' + cityName + '.', true);
        }
    } catch (error) {
        console.error('Hava kalitesi alınamadı:', error);
        showOverlayMessage('Hava kalitesi alınamadı: ' + error.message + '. Lütfen API anahtarınızı veya internet bağlantınızı kontrol edin.', true);
    }
}

async function showAssemblyAreas(city) {
    try {
        const response = await fetch('https://api.openweathermap.org/data/2.5/weather?q=' + encodeURIComponent(city) + ',tr&appid=' + weatherApiKey + '&units=metric');
        if (!response.ok) throw new Error('HTTP hatası: ' + response.status);
        const data = await response.json();
        if (data.cod === 200) {
            const lat = data.coord.lat;
            const lng = data.coord.lon;
            const placesService = new google.maps.places.PlacesService(map);
            placesService.textSearch({
                query: 'Acil durum toplanma alanı near ' + city + ', Türkiye',
                location: { lat: lat, lng: lng },
                radius: 10000
            }, (searchData, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && searchData.length > 0) {
                    clearMarkers();
                    searchData.slice(0, 5).forEach(place => {
                        if (place.geometry?.location) {
                            const marker = new google.maps.Marker({
                                position: place.geometry.location,
                                map: map,
                                title: place.name,
                                icon: {
                                    url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                                    scaledSize: new google.maps.Size(45, 46)
                                }
                            });
                            const markerInfo = {
                                lat: place.geometry.location.lat(),
                                lng: place.geometry.location.lng(),
                                title: place.name,
                                note: 'Toplanma Alanı',
                                marker: marker,
                                type: 'assembly'
                            };
                            markers.push(markerInfo);
                            marker.addListener('click', () => {
                                infoWindow.setContent(
                                    '<div style="padding:15px; font-family: Poppins;">' +
                                    '<h3 style="color: #007bff; font-size: 20px;">' + place.name + '</h3>' +
                                    '<p style="font-size: 16px;">Adres: ' + (place.formatted_address || 'Bilinmiyor') + '</p>' +
                                    '<p style="font-size: 16px;">Tür: ' + (place.types?.includes('park') ? 'Park' : 'Toplanma Alanı') + '</p>' +
                                    '<button class="btn-small btn-primary" onclick="centerMap(' + place.geometry.location.lat() + ', ' + place.geometry.location.lng() + ')"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" style="width: 16px;"> Merkeze Al</button>' +
                                    '<button class="btn-small btn-danger" onclick="deleteMarker(' + markers.indexOf(markerInfo) + ')"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" style="width: 16px;"> Sil</button>' +
                                    '</div>'
                                );
                                infoWindow.open(map, marker);
                            });
                        }
                    });
                    updateMarkerList();
                    document.getElementById('info-panel').innerHTML = '<strong>' + city + '</strong> için toplanma alanları gösteriliyor.';
                    const bounds = new google.maps.LatLngBounds();
                    markers.forEach(marker => bounds.extend(new google.maps.LatLng(marker.lat, marker.lng)));
                    map.fitBounds(bounds);
                } else {
                    showOverlayMessage('Toplanma alanları bulunamadı: ' + city + '. Lütfen başka bir şehir deneyin.', true);
                }
            });
        } else {
            showOverlayMessage('Şehir bulunamadı: ' + city + '.', true);
        }
    } catch (error) {
        console.error('Toplanma alanları alınamadı:', error);
        showOverlayMessage('Toplanma alanları alınamadı: ' + error.message + '. Lütfen internet bağlantınızı kontrol edin.', true);
    }
}

function showTeamModal() {
    document.getElementById('team-modal').style.display = 'block';
    document.getElementById('team-name').focus();
}

function closeTeamModal() {
    document.getElementById('team-modal').style.display = 'none';
    document.getElementById('team-form').reset();
}

function checkProximityAlerts() {
    if (!userLocation) return;
    const userLat = userLocation.lat();
    const userLng = userLocation.lng();
    let alerts = [];
    earthquakes.forEach(eq => {
        const distance = google.maps.geometry.spherical.computeDistanceBetween(
            new google.maps.LatLng(userLat, userLng),
            new google.maps.LatLng(eq.lat, eq.lng)
        ) / 1000;
        if (distance <= 50) {
            alerts.push('Yakınınızda deprem: ' + eq.location + ' (' + distance.toFixed(1) + ' km uzakta, Büyüklük: ' + eq.magnitude + ')');
        }
    });
    if (alerts.length > 0) {
        const alertMessage = 
            '<div class="proximity-alert">' +
            '<strong>Uyarı!</strong><br>' +
            alerts.join('<br>') +
            '</div>';
        showOverlayMessage(alertMessage, true);
    }
}

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
                addMarker(new google.maps.LatLng(userLocation.lat, userLocation.lng), 'Konumum', note, 'https://maps.google.com/mapfiles/ms/icons/red-dot.png', 'general');
                checkProximityAlerts();
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

function showOverlayMessage(message, isError) {
    const overlay = document.getElementById('overlay-info');
    overlay.innerHTML = 
        '<button class="close-btn" onclick="this.parentElement.classList.remove(\'show\'); setTimeout(() => { this.parentElement.style.display=\'none\'; }, 300);">✕</button>' +
        message;
    overlay.style.display = 'block';
    setTimeout(() => overlay.classList.add('show'), 10);
    if (!isError) {
        setTimeout(() => {
            overlay.classList.remove('show');
            setTimeout(() => overlay.style.display = 'none', 300);
        }, 15000);
    }
}

function showPolygonInfo(coords) {
    let info = '<div><h4>Poligon Bilgisi</h4><p><strong>Koordinatlar:</strong></p><ul>';
    coords.forEach(coord => {
        info += '<li>Lat: ' + coord.lat.toFixed(4) + ', Lng: ' + coord.lng.toFixed(4) + '</li>';
    });
    info += '</ul></div>';
    document.getElementById('info-panel').innerHTML = info;
}

function initHeatmap() {
    const heatmapData = earthquakes.map(eq => new google.maps.LatLng(eq.lat, eq.lng));
    heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        map: null,
        radius: 20,
        opacity: 0.6
    });
}

function toggleHeatmap() {
    if (heatmap.getMap()) {
        heatmap.setMap(null);
        document.getElementById('heatmap-btn').textContent = 'Heatmap Göster';
    } else {
        heatmap.setMap(map);
        document.getElementById('heatmap-btn').textContent = 'Heatmap Gizle';
    }
}

function displayEarthquakes() {
    earthquakeMarkers.forEach(marker => marker.setMap(null));
    earthquakeMarkers = [];
    earthquakes.forEach(eq => {
        const marker = new google.maps.Marker({
            position: { lat: eq.lat, lng: eq.lng },
            map: map,
            title: 'Deprem: ' + eq.location,
            icon: {
                url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                scaledSize: new google.maps.Size(45, 45)
            }
        });
        marker.addListener('click', () => {
            infoWindow.setContent(
                '<div style="padding:15px; font-family: Poppins;">' +
                '<h3 style="color: #007bff; font-size: 20px;">Deprem: ' + eq.location + '</h3>' +
                '<p style="font-size: 16px;">Tarih: ' + eq.date + ' ' + eq.time + '</p>' +
                '<p style="font-size: 16px;">Büyüklük: ' + eq.magnitude + '</p>' +
                '<p style="font-size: 16px;">Derinlik: ' + eq.depth + ' km</p>' +
                '<p style="font-size: 16px;">Koordinatlar: ' + eq.lat.toFixed(4) + ', ' + eq.lng.toFixed(4) + '</p>' +
                '</div>'
            );
            infoWindow.open(map, marker);
        });
        earthquakeMarkers.push(marker);
    });
}

function centerMap(lat, lng) {
    map.setCenter({ lat: lat, lng: lng });
    map.setZoom(15);
}

function calculateShortestPath() {
    if (markers.length < 2) {
        showOverlayMessage('En kısa yol için en az 2 nokta gerekli!', true);
        return;
    }

    const waypoints = markers.slice(1, -1).map(marker => ({
        location: new google.maps.LatLng(marker.lat, marker.lng),
        stopover: true
    }));

    const request = {
        origin: new google.maps.LatLng(markers[0].lat, markers[0].lng),
        destination: new google.maps.LatLng(markers[markers.length - 1].lat, markers[markers.length - 1].lng),
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

            const info = 
                '<div class="route-info">' +
                '<h3>Rota Bilgisi</h3>' +
                '<p>Toplam Mesafe: ' + (distance / 1000).toFixed(2) + ' km</p>' +
                '<p>Tahmini Süre: ' + Math.round(duration / 60) + ' dakika</p>' +
                '</div>';
            
            document.getElementById('info-panel').innerHTML = info;
        } else {
            showOverlayMessage('Rota hesaplanamadı: ' + status, true);
        }
    });
}

function startHexagonDraw() {
    drawingManager.setDrawingMode(null);
    showOverlayMessage('Altıgen çizmek için merkez noktayı seçin', false);
    
    const clickListener = map.addListener('click', e => {
        const center = e.latLng;
        const radius = 1000; // 1km yarıçap
        const points = 6;
        const coords = [];
        
        for (let i = 0; i < points; i++) {
            const angle = (2 * Math.PI * i) / points;
            coords.push(new google.maps.LatLng(
                center.lat() + (radius / 111000) * Math.cos(angle),
                center.lng() + (radius / (111000 * Math.cos(center.lat() * Math.PI / 180))) * Math.sin(angle)
            ));
        }
        
        const hexagon = new google.maps.Polygon({
            paths: coords,
            map: map,
            strokeColor: '#FF4500',
            strokeWeight: 2,
            fillColor: '#FF4500',
            fillOpacity: 0.3,
            editable: true,
            draggable: true
        });
        
        const note = prompt('Altıgen için not ekleyin:', '');
        if (note) {
            polygonNotes.set(hexagon, note);
            const area = google.maps.geometry.spherical.computeArea(hexagon.getPath());
            document.getElementById('info-panel').innerHTML = 
                'Altıgen Alanı: ' + (area / 1000000).toFixed(2) + ' km²<br>Not: ' + note;
        }
        
        google.maps.event.removeListener(clickListener);
    });
}

function selectMarkerType(type) {
    selectedMarkerType = type;
    if (type === 'team') {
        showTeamModal();
    } else {
        showOverlayMessage(type.charAt(0).toUpperCase() + type.slice(1) + ' işaretçisi eklemek için haritaya tıklayın.', false);
    }
}

map.addListener('click', function(e) {
    if (selectedMarkerType && selectedMarkerType !== 'team') {
        const latLng = e.latLng;
        const note = prompt("Bu işaretçi için not ekleyin:") || "";
        let title, iconUrl;
        
        switch (selectedMarkerType) {
            case 'ambulance':
                title = 'Ambulans';
                iconUrl = 'https://cdn-icons-png.flaticon.com/512/2979/2979016.png';
                break;
            case 'soldier':
                title = 'Asker';
                iconUrl = 'https://cdn-icons-png.flaticon.com/512/1865/1865269.png';
                break;
            case 'police':
                title = 'Polis';
                iconUrl = 'https://cdn-icons-png.flaticon.com/512/3063/3063177.png';
                break;
            case 'gendarmerie':
                title = 'Jandarma';
                iconUrl = 'https://cdn-icons-png.flaticon.com/512/1865/1865269.png';
                break;
        }
        
        addMarker(latLng, title, note, iconUrl, selectedMarkerType);
        selectedMarkerType = null;
    }
});

document.getElementById('team-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const teamName = document.getElementById('team-name').value;
    const teamType = document.getElementById('team-type').value;
    const teamSize = document.getElementById('team-size').value;
    const teamStatus = document.getElementById('team-status').value;
    
    if (!teamName) {
        showOverlayMessage('Lütfen ekip adını girin', true);
        return;
    }

    const note = `Tür: ${teamType || 'Belirtilmemiş'} | Kişi Sayısı: ${teamSize || 'Belirtilmemiş'} | Durum: ${teamStatus}`;
    const latLng = map.getCenter();
    addMarker(latLng, teamName, note, 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png', 'team');
    closeTeamModal();
});