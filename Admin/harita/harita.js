// Polyfill for replaceChildren
if (!Element.prototype.replaceChildren) {
    Element.prototype.replaceChildren = function (...nodes) {
        while (this.lastChild) {
            this.removeChild(this.lastChild);
        }
        if (nodes.length > 0) {
            this.append(...nodes);
        }
    };
}

let map, markers = [], earthquakeMarkers = [], weatherMarkers = [], teamMarkers = [], heatmap, directionsService, directionsRenderer;
let trafficLayer, is3D = false, activeMarkerType = null, mapClickListener = null, currentTravelMode = 'DRIVING';
let currentLayer = 'none';

// Büyük şehirlerin koordinatları (örnek olarak Türkiye şehirleri)
const majorCities = [
    { name: "Adana", lat: 37.0000, lng: 35.3213 },
    { name: "Adıyaman", lat: 37.7648, lng: 38.2786 },
    { name: "Afyonkarahisar", lat: 38.7638, lng: 30.5403 },
    { name: "Aksaray", lat: 38.3687, lng: 34.0360 },
    { name: "Ankara", lat: 39.9334, lng: 32.8597 },
    { name: "Antalya", lat: 36.8969, lng: 30.7133 },
    { name: "Aydın", lat: 37.8450, lng: 27.8396 },
    { name: "Balıkesir", lat: 39.6484, lng: 27.8826 },
    { name: "Batman", lat: 37.8812, lng: 41.1351 },
    { name: "Bursa", lat: 40.1828, lng: 29.0670 },
    { name: "Denizli", lat: 37.7765, lng: 29.0864 },
    { name: "Diyarbakır", lat: 37.9144, lng: 40.2306 },
    { name: "Erzurum", lat: 39.9043, lng: 41.2679 },
    { name: "Eskişehir", lat: 39.7767, lng: 30.5206 },
    { name: "Gaziantep", lat: 37.0662, lng: 37.3833 },
    { name: "Hatay", lat: 36.2028, lng: 36.1600 },
    { name: "Isparta", lat: 37.7648, lng: 30.5566 },
    { name: "İstanbul", lat: 41.0082, lng: 28.9784 },
    { name: "İzmir", lat: 38.4237, lng: 27.1428 },
    { name: "Kahramanmaraş", lat: 37.5736, lng: 36.9371 },
    { name: "Karaman", lat: 37.1759, lng: 33.2287 },
    { name: "Kayseri", lat: 38.7225, lng: 35.4875 },
    { name: "Kilis", lat: 36.7184, lng: 37.1212 },
    { name: "Kocaeli", lat: 40.8533, lng: 29.8815 },
    { name: "Konya", lat: 37.8746, lng: 32.4932 },
    { name: "Malatya", lat: 38.3552, lng: 38.3095 },
    { name: "Manisa", lat: 38.6191, lng: 27.4289 },
    { name: "Mardin", lat: 37.3212, lng: 40.7245 },
    { name: "Mersin", lat: 36.8121, lng: 34.6415 },
    { name: "Muğla", lat: 37.2154, lng: 28.3636 },
    { name: "Ordu", lat: 40.9848, lng: 37.8780 },
    { name: "Sakarya", lat: 40.7561, lng: 30.3782 },
    { name: "Samsun", lat: 41.2867, lng: 36.33 },
    { name: "Şanlıurfa", lat: 37.1674, lng: 38.7955 },
    { name: "Tekirdağ", lat: 40.9780, lng: 27.5110 },
    { name: "Trabzon", lat: 41.0015, lng: 39.7178 },
    { name: "Şırnak", lat: 37.5220, lng: 42.4572 },
    { name: "Van", lat: 38.4942, lng: 43.3832 },
    { name: "Yalova", lat: 40.6500, lng: 29.2667 }
];

const markerIcons = {
    Ambulans: 'https://cdn-icons-png.flaticon.com/512/3097/3097378.png',
    Polis: 'https://cdn-icons-png.flaticon.com/512/3063/3063173.png',
    Sağlıkçı: 'https://cdn-icons-png.flaticon.com/512/2888/2888679.png',
    Jandarma: 'https://cdn-icons-png.flaticon.com/512/2997/2997328.png',
    team: 'https://cdn-icons-png.flaticon.com/512/992/992651.png'
};

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: window.AFAD.latitude, lng: window.AFAD.longitude },
        zoom: 6,
        streetViewControl: true,
        fullscreenControl: true,
        mapTypeId: 'roadmap',
        tilt: is3D ? 45 : 0,
        mapTypeControl: false
    });

    // Street View Panorama oluşturma
    const panorama = new google.maps.StreetViewPanorama(
        document.getElementById('street-view'),
        {
            position: { lat: window.AFAD.latitude, lng: window.AFAD.longitude },
            pov: { heading: 165, pitch: 0 },
            zoom: 1,
            visible: false // İlk başta görünmez
        }
    );

    // Street View paneli kontrolü
    const streetViewPane = document.getElementById('street-view-pane');
    const closeStreetViewButton = document.getElementById('close-street-view');
    closeStreetViewButton.addEventListener('click', () => {
        streetViewPane.style.display = 'none';
        panorama.setVisible(false);
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true
    });

    function initSearch() {
        const input = document.getElementById('search-input');
        const searchBox = new google.maps.places.SearchBox(input, {
            types: ['(cities)']
        });
        const searchContainer = input.parentElement;
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(searchContainer);
    
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('toggle-btn');
        toggleBtn.addEventListener('click', () => {
            setTimeout(() => {
                if (sidebar.classList.contains('open')) {
                    searchContainer.style.marginLeft = '400px'; // Sidebar açıkken arama kutusunu sağa kaydır
                } else {
                    searchContainer.style.marginLeft = '100px'; // Sidebar kapalıyken çok sola gitmesin
                }
            }, 400);
        });
    
        searchBox.addListener('places_changed', () => {
            const places = searchBox.getPlaces();
            if (!places.length) return;
    
            const bounds = new google.maps.LatLngBounds();
            places.forEach(place => {
                if (!place.geometry) return;
                const marker = new google.maps.Marker({
                    map: map,
                    title: place.name,
                    position: place.geometry.location
                });
                markers.push(marker);
                bounds.extend(place.geometry.location);
    
                const lat = place.geometry.location.lat();
                const lng = place.geometry.location.lng();
                const cityName = place.name || 'Bilinmeyen Şehir';
    
                // Hava durumu ve hava kalitesi verilerini al ve modalda göster
                Promise.all([
                    new Promise((resolve, reject) => {
                        fetchWeatherData(lat, lng, cityName, false, (data) => {
                            if (data) resolve(data);
                            else reject(new Error('Hava durumu verisi alınamadı'));
                        });
                    }),
                    new Promise((resolve, reject) => {
                        fetchAirQualityData(lat, lng, cityName, (data) => {
                            if (data) resolve(data);
                            else reject(new Error('Hava kalitesi verisi alınamadı'));
                        });
                    })
                ])
                    .then(([weatherData, airQualityData]) => {
                        showWeatherAirModal(cityName, weatherData, airQualityData);
                    })
                    .catch(error => {
                        console.error('Error fetching weather or air quality:', error);
                        showWeatherAirModal(cityName, null, null);
                    });
    
                // Mevcut fetch çağrıları
                fetchAirQualityData(lat, lng, cityName);
                fetchWeatherData(lat, lng, cityName, false);
    
                findShortestRoute();
    
                // Street View kontrolü
                const streetViewService = new google.maps.StreetViewService();
                streetViewService.getPanorama(
                    { location: place.geometry.location, radius: 50 },
                    (data, status) => {
                        if (status === google.maps.StreetViewStatus.OK) {
                            panorama.setPosition(place.geometry.location);
                            panorama.setPov({ heading: 165, pitch: 0 });
                            panorama.setVisible(true);
                            streetViewPane.style.display = 'block';
                        } else {
                            console.warn(`${place.name} için Street View mevcut değil.`);
                            streetViewPane.style.display = 'none';
                        }
                    }
                );
            });
            map.fitBounds(bounds);
        });
    }

    google.maps.event.addListenerOnce(map, 'tilesloaded', () => {
        addEarthquakeMarkers();
        initSearch();
        initMarkerButtons();
        initDragMarkers();
        initFirebase();
        initSidebarDrag();
        initCaptureButton();
        initHeatmapButton();
        init3DButton();
        if (!window.photosFetched) {
            fetchPhotosFromFirebase();
            window.photosFetched = true;
        }
        fetchWeatherForMajorCities();
    });
}

function addEarthquakeMarkers() {
    window.AFAD.earthquakes.forEach(eq => {
        const marker = new google.maps.Marker({
            position: { lat: eq.lat, lng: eq.lon },
            map: null,
            title: `${eq.place} - ${eq.magnitude}`,
            icon: {
                url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                scaledSize: new google.maps.Size(40, 40)
            },
            magnitude: eq.magnitude
        });
        marker.addListener('click', () => {
            new google.maps.InfoWindow({
                content: `<h3>${eq.place}</h3><p>Magnitude: ${eq.magnitude}<br>Date: ${eq.date} ${eq.time}</p>`
            }).open(map, marker);
        });
        earthquakeMarkers.push(marker);
    });
}

function fetchWeatherForMajorCities() {
    console.log('Fetching weather for major cities:', majorCities);
    majorCities.forEach(city => {
        console.log(`Calling fetchWeatherData for ${city.name}`);
        fetchWeatherData(city.lat, city.lng, city.name, true);
    });
}

function showWeatherAirModal(cityName, weatherData, airQualityData) {
    console.log('Showing weather and air quality modal for:', cityName);
    const modal = document.getElementById('weather-air-modal');
    if (!modal) {
        console.error('Weather and air quality modal not found');
        return;
    }

    const cityNameEl = document.getElementById('modal-city-name');
    const weatherDescEl = document.getElementById('modal-weather-desc');
    const weatherIconEl = document.getElementById('modal-weather-icon');
    const weatherTempEl = document.getElementById('modal-weather-temp');
    const weatherHumidityEl = document.getElementById('modal-weather-humidity');
    const weatherWindEl = document.getElementById('modal-weather-wind');
    const airAqiEl = document.getElementById('modal-air-quality-aqi');
    const airPm25El = document.getElementById('modal-air-pm25');
    const airPm10El = document.getElementById('modal-air-pm10');
    const airCoEl = document.getElementById('modal-air-co');
    const closeBtn = document.getElementById('close-weather-air-modal');

    if (!cityNameEl || !weatherDescEl || !weatherIconEl || !weatherTempEl || !weatherHumidityEl || !weatherWindEl || !airAqiEl || !airPm25El || !airPm10El || !airCoEl || !closeBtn) {
        console.error('Modal elements not found');
        return;
    }

    if (weatherData) {
        weatherDescEl.textContent = weatherData.description || 'Bilinmiyor';
        weatherIconEl.src = weatherData.icon ? `http://openweathermap.org/img/wn/${weatherData.icon}.png` : 'https://via.placeholder.com/50?text=İkon+Yok';
        weatherTempEl.textContent = weatherData.temp ? `${weatherData.temp}°C` : 'Bilinmiyor';
        weatherHumidityEl.textContent = weatherData.humidity ? `${weatherData.humidity}%` : 'Bilinmiyor';
        weatherWindEl.textContent = weatherData.windSpeed ? `${weatherData.windSpeed} m/s` : 'Bilinmiyor';
    } else {
        weatherDescEl.textContent = 'Veri alınamadı';
        weatherIconEl.src = 'https://via.placeholder.com/50?text=Hata';
        weatherTempEl.textContent = 'N/A';
        weatherHumidityEl.textContent = 'N/A';
        weatherWindEl.textContent = 'N/A';
    }

    const aqiDescription = {
        1: 'İyi',
        2: 'Orta',
        3: 'Hassas Gruplar İçin Sağlıksız',
        4: 'Sağlıksız',
        5: 'Çok Sağlıksız'
    };
    if (airQualityData) {
        airAqiEl.textContent = airQualityData.aqi ? `${aqiDescription[airQualityData.aqi]} (AQI: ${airQualityData.aqi})` : 'Bilinmiyor';
        airPm25El.textContent = airQualityData.pm25 ? `${airQualityData.pm25} µg/m³` : 'Bilinmiyor';
        airPm10El.textContent = airQualityData.pm10 ? `${airQualityData.pm10} µg/m³` : 'Bilinmiyor';
        airCoEl.textContent = airQualityData.co ? `${airQualityData.co} µg/m³` : 'Bilinmiyor';
    } else {
        airAqiEl.textContent = 'Veri alınamadı';
        airPm25El.textContent = 'N/A';
        airPm10El.textContent = 'N/A';
        airCoEl.textContent = 'N/A';
    }

    cityNameEl.textContent = cityName || 'Bilinmeyen Şehir';
    modal.style.display = 'block';

    closeBtn.onclick = () => {
        modal.style.display = 'none';
        console.log('Weather and air quality modal closed');
    };

    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            console.log('Weather and air quality modal closed by clicking outside');
        }
    };
}

function fetchWeatherData(lat, lng, cityName, isMajorCity = false, callback) {
    console.log(`Fetching weather for ${cityName} at lat: ${lat}, lng: ${lng}`);
    const apiKey = window.AFAD.openweatherApiKey;

    if (!apiKey) {
        console.warn('OpenWeather API anahtarı bulunamadı, hava durumu verisi alınamıyor.');
        const weatherDiv = document.getElementById('weather-info');
        if (weatherDiv) {
            weatherDiv.innerHTML = 'Hava durumu verisi alınamadı: API anahtarı eksik.';
        }
        if (callback) callback(null);
        return;
    }

    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${apiKey}&units=metric&lang=tr`;
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Hava durumu API'sinden yanıt alınamadı: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (!data.weather || !data.main) {
                throw new Error('API yanıtında beklenen veri yapısı bulunamadı.');
            }
            const weather = data.weather[0];
            const temp = data.main.temp;
            const humidity = data.main.humidity;
            const windSpeed = data.wind.speed;
            const icon = weather.icon;

            const weatherData = {
                description: weather.description,
                icon: icon,
                temp: temp,
                humidity: humidity,
                windSpeed: windSpeed
            };

            if (!isMajorCity) {
                const weatherDiv = document.getElementById('weather-info');
                if (weatherDiv) {
                    weatherDiv.innerHTML = `
                        <p><strong>${cityName}</strong></p>
                        <p>Hava: ${weather.description} <img src="http://openweathermap.org/img/wn/${icon}.png" alt="Hava durumu ikonu" style="width: 30px;"></p>
                        <p>Sıcaklık: ${temp}°C</p>
                        <p>Nem: ${humidity}%</p>
                        <p>Rüzgar Hızı: ${windSpeed} m/s</p>
                    `;
                }
            }

            if (map && google.maps) {
                const marker = new google.maps.Marker({
                    position: { lat: lat, lng: lng },
                    map: isMajorCity && currentLayer === 'weather' ? map : null,
                    title: cityName,
                    icon: {
                        url: `http://openweathermap.org/img/wn/${icon}@2x.png`,
                        scaledSize: new google.maps.Size(60, 60),
                        anchor: new google.maps.Point(30, 30)
                    },
                    animation: google.maps.Animation.DROP
                });
                marker.addListener('click', () => {
                    new google.maps.InfoWindow({
                        content: `
                            <div style="padding: 10px;">
                                <h3>${cityName}</h3>
                                <p>Hava: ${weather.description} <img src="http://openweathermap.org/img/wn/${icon}.png" alt="Hava durumu ikonu" style="width: 30px;"></p>
                                <p>Sıcaklık: ${temp}°C</p>
                                <p>Nem: ${humidity}%</p>
                                <p>Rüzgar Hızı: ${windSpeed} m/s</p>
                            </div>
                        `
                    }).open(map, marker);
                });
                weatherMarkers.push(marker);
                console.log(`Weather marker added for ${cityName} with icon: ${icon}, animation: DROP`);
            }

            const list = document.getElementById('marker-list');
            if (list && !isMajorCity) {
                const li = document.createElement('li');
                li.className = 'marker-item';
                li.innerHTML = `
                    <div class="marker-item-content">
                        <img src="http://openweathermap.org/img/wn/${icon}.png" alt="Hava durumu ikonu" style="width: 32px; vertical-align: middle; margin-right: 8px;">
                        <strong>${cityName}</strong>
                        <p>${weather.description}</p>
                        <p>Sıcaklık: ${temp}°C | Nem: ${humidity}% | Rüzgar: ${windSpeed} m/s</p>
                    </div>
                `;
                list.appendChild(li);
            }

            if (callback) callback(weatherData);
        })
        .catch(error => {
            console.error(`Hava durumu verisi alınamadı (${cityName}):`, error);
            const weatherDiv = document.getElementById('weather-info');
            if (weatherDiv) {
                weatherDiv.innerHTML = `Hava durumu verisi alınamadı: ${error.message}`;
            }
            if (callback) callback(null);
        });
}

function fetchAirQualityData(lat, lng, cityName, callback) {
    console.log(`Fetching air quality for ${cityName} at lat: ${lat}, lng: ${lng}`);
    const apiKey = window.AFAD.openweatherApiKey;
    console.log('OpenWeather API Key:', apiKey);

    if (!apiKey) {
        console.warn('OpenWeather API anahtarı bulunamadı, hava kalitesi verisi alınamıyor.');
        const airQualityDiv = document.getElementById('air-quality-info');
        if (airQualityDiv) {
            airQualityDiv.innerHTML = 'Hava kalitesi verisi alınamadı: API anahtarı eksik.';
        } else {
            console.error('air-quality-info div not found');
        }
        const list = document.getElementById('marker-list');
        if (list) {
            const li = document.createElement('li');
            li.className = 'marker-item';
            li.innerHTML = `<strong>${cityName}</strong><p>Hava kalitesi verisi alınamadı: API anahtarı eksik.</p>`;
            list.appendChild(li);
        } else {
            console.error('marker-list div not found');
        }
        if (callback) callback(null);
        return;
    }

    const url = `https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lng}&appid=${apiKey}`;
    console.log('Air Quality API URL:', url);

    fetch(url)
        .then(response => {
            console.log('Air Quality API Response Status:', response.status);
            if (!response.ok) throw new Error(`Hava kalitesi API'sinden yanıt alınamadı: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('Air Quality API Response:', data);
            if (!data.list || !data.list[0]) {
                throw new Error('API yanıtında beklenen veri yapısı bulunamadı.');
            }
            const aqi = data.list[0].main.aqi;
            const components = data.list[0].components;

            const airQualityData = {
                aqi: aqi,
                pm25: components.pm2_5,
                pm10: components.pm10,
                co: components.co
            };

            const aqiDescription = {
                1: 'İyi',
                2: 'Orta',
                3: 'Hassas Gruplar İçin Sağlıksız',
                4: 'Sağlıksız',
                5: 'Çok Sağlıksız'
            };

            const list = document.getElementById('marker-list');
            if (list) {
                const li = document.createElement('li');
                li.className = 'marker-item';
                li.innerHTML = `
                    <strong>${cityName}</strong>
                    <p>Hava Kalitesi: ${aqiDescription[aqi] || 'Bilinmiyor'} (AQI: ${aqi})</p>
                    <p>PM2.5: ${components.pm2_5} µg/m³</p>
                    <p>PM10: ${components.pm10} µg/m³</p>
                    <p>CO: ${components.co} µg/m³</p>
                `;
                list.appendChild(li);
            } else {
                console.error('marker-list div not found');
            }

            const airQualityDiv = document.getElementById('air-quality-info');
            if (airQualityDiv) {
                airQualityDiv.innerHTML = `
                    <p><strong>${cityName}</strong></p>
                    <p>Hava Kalitesi: ${aqiDescription[aqi] || 'Bilinmiyor'} (AQI: ${aqi})</p>
                    <p>PM2.5: ${components.pm2_5} µg/m³</p>
                    <p>PM10: ${components.pm10} µg/m³</p>
                    <p>CO: ${components.co} µg/m³</p>
                `;
            } else {
                console.error('air-quality-info div not found');
            }

            if (callback) callback(airQualityData);
        })
        .catch(error => {
            console.error(`Hava kalitesi verisi alınamadı (${cityName}):`, error);
            const airQualityDiv = document.getElementById('air-quality-info');
            if (airQualityDiv) {
                airQualityDiv.innerHTML = `Hava kalitesi verisi alınamadı: ${error.message}`;
            } else {
                console.error('air-quality-info div not found');
            }
            const list = document.getElementById('marker-list');
            if (list) {
                const li = document.createElement('li');
                li.className = 'marker-item';
                li.innerHTML = `<strong>${cityName}</strong><p>Hava kalitesi verisi alınamadı: ${error.message}</p>`;
                list.appendChild(li);
            } else {
                console.error('marker-list div not found');
            }
            if (callback) callback(null);
        });
}


function addPhotoMarker(url, metadata) {
    console.log('addPhotoMarker called with URL:', url, 'Metadata:', metadata);
    if (!metadata.latitude || !metadata.longitude || isNaN(metadata.latitude) || isNaN(metadata.longitude)) {
        console.error('Invalid location data for photo:', metadata);
        return;
    }

    if (!map) {
        console.error('Map object is not initialized');
        return;
    }

    const MarkerClass = (google.maps.marker && google.maps.marker.AdvancedMarkerElement) || google.maps.Marker;
    const markerOptions = {
        position: { lat: metadata.latitude, lng: metadata.longitude },
        map: map
    };

    if (MarkerClass === google.maps.Marker) {
        markerOptions.icon = {
            url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            scaledSize: new google.maps.Size(40, 40)
        };
    } else {
        markerOptions.content = createMarkerIcon('https://maps.google.com/mapfiles/ms/icons/blue-dot.png');
    }

    try {
        const marker = new MarkerClass(markerOptions);
        console.log('Marker created:', marker);

        marker.addListener('click', () => {
            console.log('Marker clicked for:', metadata.fileName);

            const photoModal = document.getElementById('photo-modal');
            const img = document.getElementById('photo-image');
            const approveBtn = document.getElementById('approve-photo-btn');
            const rejectBtn = document.getElementById('reject-photo-btn');
            if (photoModal && img && approveBtn && rejectBtn) {
                img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
                photoModal.style.display = 'block';
                img.src = url;
                img.onload = () => {
                    console.log('Photo loaded successfully:', url);
                };
                img.onerror = () => {
                    console.error('Failed to load photo:', url);
                    img.src = 'https://via.placeholder.com/400x300?text=Fotoğraf+Yüklenemedi';
                };

                approveBtn.onclick = () => {
                    console.log('Photo approved:', metadata.fileName);
                    photoModal.style.display = 'none';
                };
                rejectBtn.onclick = () => {
                    console.log('Photo rejected:', metadata.fileName);
                    photoModal.style.display = 'none';
                };
            } else {
                console.warn('Photo modal or its elements not found');
            }

            Promise.all([
                new Promise((resolve, reject) => {
                    fetchWeatherData(metadata.latitude, metadata.longitude, metadata.fileName || 'Konum', false, (data) => {
                        if (data) resolve(data);
                        else reject(new Error('Hava durumu verisi alınamadı'));
                    });
                }),
                new Promise((resolve, reject) => {
                    fetchAirQualityData(metadata.latitude, metadata.longitude, metadata.fileName || 'Konum', (data) => {
                        if (data) resolve(data);
                        else reject(new Error('Hava kalitesi verisi alınamadı'));
                    });
                })
            ])
                .then(([weatherData, airQualityData]) => {
                    showWeatherAirModal(metadata.fileName || 'Konum', weatherData, airQualityData);
                })
                .catch(error => {
                    console.error('Error fetching weather or air quality:', error);
                    showWeatherAirModal(metadata.fileName || 'Konum', null, null);
                });

            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div style="padding: 15px;">
                        <h3>Fotoğraf Bilgisi</h3>
                        <p><strong>Dosya Adı:</strong> ${metadata.fileName}</p>
                        <p><strong>Tarih:</strong> ${metadata.timestamp}</p>
                        <p><strong>Konum:</strong> ${metadata.latitude}, ${metadata.longitude}</p>
                        ${metadata.description ? `<p><strong>Açıklama:</strong> ${metadata.description}</p>` : ''}
                        <img src="${url}" style="max-width: 200px; max-height: 200px; margin-top: 10px;">
                    </div>
                `
            });
            console.log('Opening info window for:', metadata.fileName);
            infoWindow.open(map, marker);
        });

        markers.push(marker);
        console.log('Marker added to markers array:', markers.length);
        updateMarkerList();
    } catch (error) {
        console.error('Error creating marker:', error);
    }
}

function initMarkerButtons() {
    const buttons = document.querySelectorAll('.marker-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;
            if (activeMarkerType === type) {
                activeMarkerType = null;
                buttons.forEach(b => b.classList.remove('active'));
                if (mapClickListener) {
                    google.maps.event.removeListener(mapClickListener);
                    mapClickListener = null;
                }
            } else {
                activeMarkerType = type;
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                if (mapClickListener) {
                    google.maps.event.removeListener(mapClickListener);
                }
                mapClickListener = map.addListener('click', (event) => {
                    addMarker(event.latLng, type);
                });
            }
        });
    });
}

function initDragMarkers() {
    const mapDiv = document.getElementById('map');
    mapDiv.addEventListener('dragover', e => e.preventDefault());
    mapDiv.addEventListener('drop', e => {
        e.preventDefault();
        const type = e.dataTransfer.getData('text/plain');
        if (!type) {
            console.log('No type data found in drag event');
            return;
        }

        const rect = mapDiv.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const point = new google.maps.Point(x, y);
        const topLeft = map.getBounds().getNorthEast();
        const bottomRight = map.getBounds().getSouthWest();
        const latLng = new google.maps.LatLng(
            bottomRight.lat() + (topLeft.lat() - bottomRight.lat()) * (y / mapDiv.offsetHeight),
            bottomRight.lng() + (topLeft.lng() - bottomRight.lng()) * (x / mapDiv.offsetWidth)
        );

        if (latLng) {
            console.log('Dropping marker at:', latLng.toString(), 'with type:', type);
            addMarker(latLng, type);
        } else {
            console.error('Failed to calculate LatLng from pixel coordinates');
        }
    });

    document.querySelectorAll('.drag-icon').forEach(icon => {
        icon.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', icon.dataset.type);
        });
    });
}

function addMarker(latLng, type) {
    if (type === 'team') {
        showTeamModal(latLng);
    } else if (confirm('Bu marker için not eklemek ister misiniz?')) {
        showMarkerNoteModal(latLng, type);
    } else {
        createMarker(latLng, type, '');
    }
}

function showTeamModal(latLng) {
    const modal = document.getElementById('team-modal');
    const form = document.getElementById('team-form');
    const cancelBtn = document.getElementById('cancel-team-btn');

    modal.style.display = 'block';

    form.onsubmit = (e) => {
        e.preventDefault();
        const teamName = document.getElementById('team-name').value;
        const teamType = document.getElementById('team-type').value;
        const teamSize = document.getElementById('team-size').value;

        if (!teamName || !teamType || !teamSize) {
            alert('Lütfen tüm alanları doldurun.');
            return;
        }

        const teamData = {
            teamName,
            teamType,
            teamSize: parseInt(teamSize)
        };

        createMarker(latLng, 'team', '', teamData);
        modal.style.display = 'none';
        form.reset();
    };

    cancelBtn.onclick = () => {
        modal.style.display = 'none';
        form.reset();
    };
}

function showMarkerNoteModal(latLng, type) {
    const modal = document.getElementById('marker-note-modal');
    const form = document.getElementById('marker-note-form');
    const closeBtn = document.getElementById('close-note-modal');
    
    modal.style.display = 'block';
    
    form.onsubmit = (e) => {
        e.preventDefault();
        const note = document.getElementById('marker-note-input').value;
        createMarker(latLng, type, note);
        modal.style.display = 'none';
        form.reset();
    };
    
    closeBtn.onclick = () => {
        modal.style.display = 'none';
        form.reset();
        createMarker(latLng, type, '');
    };
}

function createMarker(latLng, type, note, teamData = null) {
    const marker = new google.maps.Marker({
        position: latLng,
        map: type === 'team' && currentLayer === 'teams' ? map : (type !== 'team' ? map : null),
        icon: {
            url: markerIcons[type] || 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        }
    });

    if (teamData) {
        marker.teamData = teamData;
        teamMarkers.push(marker);
    }

    marker.addListener('click', () => {
        let content = `<div style="padding: 10px;"><h3>${type}</h3>`;
        if (note) {
            content += `<p><strong>Not:</strong> ${note}</p>`;
        }
        if (teamData) {
            content += `
                <p><strong>Ekip Adı:</strong> ${teamData.teamName}</p>
                <p><strong>Ekip Türü:</strong> ${teamData.teamType}</p>
                <p><strong>Ekip Büyüklüğü:</strong> ${teamData.teamSize}</p>
            `;
        }
        content += `</div>`;
        new google.maps.InfoWindow({
            content: content
        }).open(map, marker);
    });

    if (type !== 'team') {
        markers.push(marker);
    }
    updateMarkerList();
}

function updateMarkerList() {
    const list = document.getElementById('marker-list');
    list.innerHTML = '';
    const allMarkers = [...markers, ...teamMarkers];
    allMarkers.forEach((marker, index) => {
        const li = document.createElement('li');
        li.className = 'marker-item';
        const label = marker.teamData ? marker.teamData.teamName : `Marker ${index + 1}`;
        li.innerHTML = `${label} <div class="marker-actions"><button onclick="deleteMarker(${index})">Sil</button></div>`;
        list.appendChild(li);
    });
}

function deleteMarker(index) {
    const allMarkers = [...markers, ...teamMarkers];
    const marker = allMarkers[index];
    marker.setMap(null);
    if (marker.teamData) {
        teamMarkers = teamMarkers.filter(m => m !== marker);
    } else {
        markers = markers.filter(m => m !== marker);
    }
    updateMarkerList();
    findShortestRoute();
}

function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    teamMarkers.forEach(marker => marker.setMap(null));
    markers = [];
    teamMarkers = [];
    updateMarkerList();
    directionsRenderer.setDirections({ routes: [] });
    document.getElementById('route-info').innerHTML = 'Yol bilgisi bekleniyor...';
}

function zoomToFit() {
    const bounds = new google.maps.LatLngBounds();
    const allMarkers = [...markers, ...teamMarkers];
    allMarkers.forEach(marker => bounds.extend(marker.getPosition()));
    if (!bounds.isEmpty()) {
        map.fitBounds(bounds);
    }
}

function findShortestRoute() {
    const allMarkers = [...markers, ...teamMarkers];
    if (allMarkers.length < 2) {
        directionsRenderer.setDirections({ routes: [] });
        document.getElementById('route-info').innerHTML = 'En az iki işaretçi gerekli.';
        return;
    }

    const origin = allMarkers[0].getPosition();
    const destination = allMarkers[allMarkers.length - 1].getPosition();
    const waypoints = allMarkers.slice(1, -1).map(marker => ({
        location: marker.getPosition(),
        stopover: true
    }));

    const request = {
        origin: origin,
        destination: destination,
        waypoints: waypoints,
        optimizeWaypoints: true,
        travelMode: currentTravelMode === 'DRONE' || currentTravelMode === 'HELICOPTER' ? 'DRIVING' : currentTravelMode,
        avoidHighways: document.getElementById('avoid-highways').checked
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);
            const route = result.routes[0];
            let distance = 0;
            let duration = 0;
            route.legs.forEach(leg => {
                distance += leg.distance.value;
                duration += leg.duration.value;
            });
            if (currentTravelMode === 'DRONE') {
                distance *= 0.8;
                duration *= 0.5;
            } else if (currentTravelMode === 'HELICOPTER') {
                distance *= 0.7;
                duration *= 0.4;
            }
            document.getElementById('route-info').innerHTML = `
                <p><strong>Mesafe:</strong> ${(distance / 1000).toFixed(1)} km</p>
                <p><strong>Süre:</strong> ${(duration / 60).toFixed(1)} dakika</p>
                <p><strong>Ulaşım Modu:</strong> ${currentTravelMode}</p>
            `;
        } else {
            directionsRenderer.setDirections({ routes: [] });
            document.getElementById('route-info').innerHTML = 'Yol bilgisi alınamadı.';
        }
    });
}

function findSafeRoute() {
    const allMarkers = [...markers, ...teamMarkers];
    if (allMarkers.length < 2) {
        directionsRenderer.setDirections({ routes: [] });
        document.getElementById('route-info').innerHTML = 'En az iki işaretçi gerekli.';
        return;
    }

    const origin = allMarkers[0].getPosition();
    const destination = allMarkers[allMarkers.length - 1].getPosition();
    const waypoints = allMarkers.slice(1, -1).map(marker => ({
        location: marker.getPosition(),
        stopover: true
    }));

    const earthquakeAreas = window.AFAD.earthquakes.map(eq => ({
        center: { lat: eq.lat, lng: eq.lon },
        radius: eq.magnitude * 10000
    }));

    const request = {
        origin: origin,
        destination: destination,
        waypoints: waypoints,
        optimizeWaypoints: true,
        travelMode: currentTravelMode === 'DRONE' || currentTravelMode === 'HELICOPTER' ? 'DRIVING' : currentTravelMode,
        avoidHighways: true,
        avoidFerries: true
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            let safeRoute = result;
            let isSafe = true;
            const routePath = result.routes[0].overview_path;

            routePath.forEach(point => {
                earthquakeAreas.forEach(area => {
                    const distance = google.maps.geometry.spherical.computeDistanceBetween(
                        new google.maps.LatLng(point.lat(), point.lng()),
                        new google.maps.LatLng(area.center.lat, area.center.lng)
                    );
                    if (distance < area.radius) {
                        isSafe = false;
                    }
                });
            });

            if (isSafe) {
                directionsRenderer.setDirections(safeRoute);
                const route = safeRoute.routes[0];
                let distance = 0;
                let duration = 0;
                route.legs.forEach(leg => {
                    distance += leg.distance.value;
                    duration += leg.duration.value;
                });
                if (currentTravelMode === 'DRONE') {
                    distance *= 0.8;
                    duration *= 0.5;
                } else if (currentTravelMode === 'HELICOPTER') {
                    distance *= 0.7;
                    duration *= 0.4;
                }
                document.getElementById('route-info').innerHTML = `
                    <p><strong>Mesafe:</strong> ${(distance / 1000).toFixed(1)} km</p>
                    <p><strong>Süre:</strong> ${(duration / 60).toFixed(1)} dakika</p>
                    <p><strong>Ulaşım Modu:</strong> ${currentTravelMode}</p>
                    <p><strong>Güvenli Yol:</strong> Evet</p>
                `;
            } else {
                document.getElementById('route-info').innerHTML = 'Güvenli yol bulunamadı. Deprem bölgelerinden geçiyor.';
            }
        } else {
            directionsRenderer.setDirections({ routes: [] });
            document.getElementById('route-info').innerHTML = 'Güvenli yol bilgisi alınamadı.';
        }
    });
}

function updateRouteWithTravelMode() {
    currentTravelMode = document.getElementById('travel-mode-selector').value;
    findShortestRoute();
}

function toggleLayer(layer) {
    currentLayer = layer;

    // Tüm işaretçileri gizle
    earthquakeMarkers.forEach(marker => marker.setMap(null));
    weatherMarkers.forEach(marker => marker.setMap(null));
    teamMarkers.forEach(marker => marker.setMap(null));

    // Seçilen katmana göre işaretçileri göster
    if (layer === 'earthquakes') {
        earthquakeMarkers.forEach(marker => marker.setMap(map));
    } else if (layer === 'weather') {
        // Mevcut işaretçileri temizle ve yeniden getir
        weatherMarkers.forEach(marker => marker.setMap(null));
        weatherMarkers = []; // Eski işaretçileri temizle
        fetchWeatherForMajorCities(); // Yeni verilerle işaretçileri ekle
        weatherMarkers.forEach(marker => marker.setMap(map));
    } else if (layer === 'teams') {
        teamMarkers.forEach(marker => marker.setMap(map));
    }

    // Marker listesini güncelle
    const list = document.getElementById('marker-list');
    if (list) {
        list.innerHTML = ''; // Listeyi temizle
        if (layer === 'weather') {
            weatherMarkers.forEach(marker => {
                const cityName = marker.getTitle();
                // fetchWeatherData'dan gelen verileri kullanarak liste öğesi ekle
                // Bu, fetchWeatherData'daki liste güncellemesiyle zaten yapılıyor
            });
        }
    }
}

function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(pos);
                const marker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    title: 'Mevcut Konum'
                });
                markers.push(marker);
                findShortestRoute();
            },
            () => alert('Konum alınamadı.')
        );
    } else {
        alert('Tarayıcı konum servisini desteklemiyor.');
    }
}

function toggleTraffic() {
    if (!trafficLayer) {
        trafficLayer = new google.maps.TrafficLayer();
        trafficLayer.setMap(map);
        document.getElementById('traffic-btn').innerHTML = '<img src="https://cdn-icons-png.flaticon.com/512/2965/2965879.png" alt="traffic"> Trafiği Gizle';
    } else {
        trafficLayer.setMap(null);
        trafficLayer = null;
        document.getElementById('traffic-btn').innerHTML = '<img src="https://cdn-icons-png.flaticon.com/512/2965/2965879.png" alt="traffic"> Trafik Göster';
    }
}

function initFirebase() {
    const firebaseConfig = {
        apiKey: "AIzaSyD9ogbozKtQyppbbJG6U8WA9D8MVfs4ZE0",
        authDomain: "afad-proje.firebaseapp.com",
        databaseURL: "https://afad-proje-default-rtdb.europe-west1.firebasedatabase.app",
        projectId: "afad-proje",
        storageBucket: "afad-proje.firebasestorage.app",
        messagingSenderId: "992617585430",
        appId: "1:992617585430:web:124b01a79f4047682a4e37",
        measurementId: "G-C6D0PWNGNJ"
    };
    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
        console.log("Firebase initialized successfully");
    } else {
        console.log("Firebase already initialized");
    }
}

function initSidebarDrag() {
    const sidebar = document.getElementById('sidebar');
    const header = document.getElementById('sidebar-header');
    const toggleBtn = document.getElementById('toggle-btn');
    let isDragging = false;
    let xOffset = 0;
    let yOffset = 0;

    header.addEventListener('mousedown', startDragging);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDragging);

    function startDragging(e) {
        xOffset = sidebar.offsetLeft - e.clientX;
        yOffset = sidebar.offsetTop - e.clientY;
        isDragging = true;
        sidebar.classList.add('dragging');
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            const currentX = e.clientX + xOffset;
            const currentY = e.clientY + yOffset;
            sidebar.style.left = Math.max(0, Math.min(currentX, window.innerWidth - sidebar.offsetWidth)) + 'px';
            sidebar.style.top = Math.max(0, Math.min(currentY, window.innerHeight - sidebar.offsetHeight)) + 'px';
        }
    }

    function stopDragging() {
        isDragging = false;
        sidebar.classList.remove('dragging');
    }

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        if (sidebar.classList.contains('open')) {
            sidebar.style.left = '0';
        } else {
            sidebar.style.left = '-280px';
            sidebar.style.top = '0';
        }
    });
}

function initCaptureButton() {
    document.getElementById('capture-btn').addEventListener('click', () => {
        const mapElement = document.getElementById('map');
        if (!mapElement) {
            alert('Harita elementi bulunamadı.');
            return;
        }

        const controls = document.querySelectorAll('#sidebar, #marker-toolbar, #toggle-btn');
        controls.forEach(el => el.style.display = 'none');

        html2canvas(mapElement, {
            useCORS: true,
            allowTaint: true,
            scrollX: 0,
            scrollY: 0,
            width: mapElement.clientWidth,
            height: mapElement.clientHeight
        }).then(canvas => {
            controls.forEach(el => el.style.display = '');

            const dataURL = canvas.toDataURL('image/png');
            if (!dataURL || dataURL.length < 1000) {
                alert('Ekran görüntüsü alınamadı. (Boş veri)');
                return;
            }

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const fileName = `harita-goruntu-${timestamp}.png`;
            const link = document.createElement('a');
            link.download = fileName;
            link.href = dataURL;
            document.body.appendChild(link);  // DOM'a ekle
            link.click();                     // tıkla
            document.body.removeChild(link);  // temizle

            alert('Ekran görüntüsü indirildi: ' + fileName);
        }).catch(error => {
            console.error('Screenshot capture error:', error);
            alert('Ekran görüntüsü alınamadı: ' + error.message);
            controls.forEach(el => el.style.display = '');
        });
    });
}

document.addEventListener('DOMContentLoaded', initCaptureButton);


function initHeatmapButton() {
    document.getElementById('toggle-heatmap').addEventListener('click', () => {
        if (!heatmap) {
            const heatmapData = window.AFAD.earthquakes.map(eq => ({
                location: new google.maps.LatLng(eq.lat, eq.lon),
                weight: eq.magnitude * 2
            }));

            heatmap = new google.maps.visualization.HeatmapLayer({
                data: heatmapData,
                map: map,
                radius: 30,
                gradient: [
                    'rgba(0, 255, 255, 0)',
                    'rgba(0, 255, 255, 1)',
                    'rgba(0, 191, 255, 1)',
                    'rgba(0, 127, 255, 1)',
                    'rgba(0, 63, 255, 1)',
                    'rgba(0, 0, 255, 1)',
                    'rgba(0, 0, 223, 1)',
                    'rgba(0, 0, 191, 1)',
                    'rgba(0, 0, 159, 1)',
                    'rgba(0, 0, 127, 1)',
                    'rgba(63, 0, 91, 1)',
                    'rgba(127, 0, 63, 1)',
                    'rgba(191, 0, 31, 1)',
                    'rgba(255, 0, 0, 1)'
                ]
            });
            document.getElementById('toggle-heatmap').textContent = 'Heatmap Gizle';
        } else {
            heatmap.setMap(null);
            heatmap = null;
            document.getElementById('toggle-heatmap').textContent = 'Heatmap Göster';
        }
    });
}

function init3DButton() {
    document.getElementById('toggle-3d').addEventListener('click', () => {
        is3D = !is3D;
        if (is3D) {
            map.setMapTypeId('satellite');
            map.setTilt(45);
            map.setHeading(45);
            document.getElementById('toggle-3d').textContent = '2D Görünüme Geç';
        } else {
            map.setMapTypeId('roadmap');
            map.setTilt(0);
            map.setHeading(0);
            document.getElementById('toggle-3d').textContent = '3D Görünüme Geç';
        }
    });
}

function fetchPhotosFromFirebase() {
    if (!navigator.onLine) {
        console.warn('Offline mode: No internet connection');
        const fallbackUrl = 'https://via.placeholder.com/400x300?text=Offline+Mode';
        const metadata = {
            latitude: 38.3746052,
            longitude: 27.1061898,
            timestamp: new Date().toLocaleString(),
            description: 'Offline fallback image',
            fileName: 'offline-image.png'
        };
        addPhotoMarker(fallbackUrl, metadata);
        return;
    }

    let storage, db;
    try {
        storage = firebase.storage();
        db = firebase.firestore();
        console.log('Firebase initialized successfully');
    } catch (error) {
        console.error('Error initializing Firebase:', error);
        const fallbackUrl = 'https://via.placeholder.com/400x300?text=Firebase+Init+Error';
        const metadata = {
            latitude: 38.3746052,
            longitude: 27.1061898,
            timestamp: new Date().toLocaleString(),
            description: 'Firebase initialization failed',
            fileName: 'firebase-error.png'
        };
        addPhotoMarker(fallbackUrl, metadata);
        return;
    }

    const docRef = db.collection('afet-bildirimleri').doc('KU5411IPjOgll7Sz2bzCtacPY8U2');
    const imagesCollection = docRef.collection('images');
    console.log('Fetching images from Firestore path:', imagesCollection.path);

    function fetchWithRetry(collection, retries = 3, delay = 1000) {
        return collection.get().catch((error) => {
            if (retries > 0 && error.code === 'unavailable') {
                console.warn(`Retrying fetch (${retries} attempts left)...`);
                return new Promise((resolve) => setTimeout(resolve, delay))
                    .then(() => fetchWithRetry(collection, retries - 1, delay * 2));
            }
            throw error;
        });
    }

    fetchWithRetry(imagesCollection).then((querySnapshot) => {
        if (querySnapshot.empty) {
            console.warn('No images found in collection:', imagesCollection.path);
            const fallbackUrl = 'https://via.placeholder.com/400x300?text=No+Images+Found';
            const metadata = {
                latitude: 38.3746052,
                longitude: 27.1061898,
                timestamp: new Date().toLocaleString(),
                description: 'No images available',
                fileName: 'no-image.png'
            };
            addPhotoMarker(fallbackUrl, metadata);
            return;
        }

        console.log('Found', querySnapshot.size, 'image documents');
        querySnapshot.forEach((doc) => {
            const data = doc.data();
            console.log('Processing document:', doc.id, data);

            if (!data.fileName) {
                console.warn('No fileName in document:', doc.id, data);
                const fallbackUrl = 'https://via.placeholder.com/400x300?text=No+File+Name';
                const metadata = {
                    latitude: parseFloat(data.location?.latitude) || 38.3746052,
                    longitude: parseFloat(data.location?.longitude) || 27.1061898,
                    timestamp: data.timestamp || new Date().toLocaleString(),
                    description: 'No file name specified',
                    fileName: 'no-filename.png'
                };
                addPhotoMarker(fallbackUrl, metadata);
                return;
            }

            const storagePath = `afet-bildirimleri/KU5411IPjOgll7Sz2bzCtacPY8U2/${data.fileName}`;
            storage.ref(storagePath).getDownloadURL()
                .then((url) => {
                    console.log('Image URL fetched from Storage:', url);
                    const metadata = {
                        latitude: parseFloat(data.location?.latitude) || 38.3746052,
                        longitude: parseFloat(data.location?.longitude) || 27.1061898,
                        timestamp: data.timestamp || new Date().toLocaleString(),
                        description: data.description || '',
                        fileName: data.fileName
                    };
                    addPhotoMarker(url, metadata);
                })
                .catch((error) => {
                    console.error('Error getting download URL for file:', storagePath, error);
                    const fallbackUrl = 'https://via.placeholder.com/400x300?text=Image+Not+Found';
                    const metadata = {
                        latitude: parseFloat(data.location?.latitude) || 38.3746052,
                        longitude: parseFloat(data.location?.longitude) || 27.1061898,
                        timestamp: data.timestamp || new Date().toLocaleString(),
                        description: 'Failed to load image: ' + error.message,
                        fileName: data.fileName || 'error-image.png'
                    };
                    addPhotoMarker(fallbackUrl, metadata);
                });
        });
    }).catch((error) => {
        console.error('Error fetching images from Firestore:', error);
        const fallbackUrl = 'https://via.placeholder.com/400x300?text=Error+Fetching+Images';
        const metadata = {
            latitude: 38.3746052,
            longitude: 27.1061898,
            timestamp: new Date().toLocaleString(),
            description: 'Failed to fetch images',
            fileName: 'error-fetch.png'
        };
        addPhotoMarker(fallbackUrl, metadata);
    });
}

function addPhotoMarker(url, metadata) {
    if (!metadata.latitude || !metadata.longitude || isNaN(metadata.latitude) || isNaN(metadata.longitude)) {
        console.error('Invalid location data for photo:', metadata);
        return;
    }

    const MarkerClass = (google.maps.marker && google.maps.marker.AdvancedMarkerElement) || google.maps.Marker;
    const markerOptions = {
        position: { lat: metadata.latitude, lng: metadata.longitude },
        map: map
    };

    if (MarkerClass === google.maps.Marker) {
        markerOptions.icon = {
            url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            scaledSize: new google.maps.Size(40, 40)
        };
    } else {
        markerOptions.content = createMarkerIcon('https://maps.google.com/mapfiles/ms/icons/blue-dot.png');
    }

    const marker = new MarkerClass(markerOptions);

    marker.addListener('click', () => {
        const modal = document.getElementById('photo-modal');
        const img = document.getElementById('photo-image');
        const approveBtn = document.getElementById('approve-photo-btn');
        const rejectBtn = document.getElementById('reject-photo-btn');
        if (!modal || !img || !approveBtn || !rejectBtn) {
            console.warn('Photo modal or its elements not found');
            return;
        }

        img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        modal.style.display = 'block';
        img.src = url;
        img.onload = () => {
            console.log('Photo loaded successfully:', url);
        };
        img.onerror = () => {
            console.error('Failed to load photo:', url);
            img.src = 'https://via.placeholder.com/400x300?text=Fotoğraf+Yüklenemedi';
        };

        approveBtn.onclick = () => {
            console.log('Photo approved:', metadata.fileName);
            modal.style.display = 'none';
        };
        rejectBtn.onclick = () => {
            console.log('Photo rejected:', metadata.fileName);
            modal.style.display = 'none';
        };

        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="padding: 15px;">
                    <h3>Fotoğraf Bilgisi</h3>
                    <p><strong>Dosya Adı:</strong> ${metadata.fileName}</p>
                    <p><strong>Tarih:</strong> ${metadata.timestamp}</p>
                    <p><strong>Konum:</strong> ${metadata.latitude}, ${metadata.longitude}</p>
                    ${metadata.description ? `<p><strong>Açıklama:</strong> ${metadata.description}</p>` : ''}
                    <img src="${url}" style="max-width: 200px; max-height: 200px; margin-top: 10px;">
                </div>
            `
        });
        infoWindow.open(map, marker);
    });

    markers.push(marker);
    updateMarkerList();
}

function createMarkerIcon(url) {
    const icon = document.createElement('div');
    const img = document.createElement('img');
    img.src = url;
    img.style.width = '40px';
    img.style.height = '40px';
    icon.appendChild(img);
    return icon;
}

function closePhotoModal() {
    document.getElementById('photo-modal').style.display = 'none';
}