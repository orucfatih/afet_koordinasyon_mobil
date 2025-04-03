import folium
from geopy.geocoders import Nominatim
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QMessageBox, QCompleter, QListWidget,
                             QGroupBox, QFormLayout)
from PyQt5.QtGui import QIcon
from styles.styles_dark import MAP_STYLE, REFRESH_BUTTON_STYLE
from styles.styles_light import *


import sys
import os
import requests
import json

#from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QIcon

from dotenv import load_dotenv


class PlaceAutocomplete(QLineEdit):
    def __init__(self, api_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.suggestions = []
        self.completer = QCompleter(self.suggestions, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)

        # Setup timer for debounce
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.get_suggestions)

        # Connect text change to timer
        self.textChanged.connect(self.start_timer)

    def start_timer(self):
        self.timer.start(500)  # 500ms debounce

    def get_suggestions(self):
        text = self.text()
        if len(text) < 3:  # Don't search for very short inputs
            return

        try:
            # Get place predictions with Türkiye as the region bias
            url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={text}&components=country:tr&key={self.api_key}"
            response = requests.get(url)
            data = response.json()

            if data['status'] == 'OK':
                # Extract descriptions from predictions
                self.suggestions = [pred['description'] for pred in data['predictions']]

                # Update completer model
                self.completer.model().setStringList(self.suggestions)
                self.completer.complete()
            else:
                print(f"Autocomplete error: {data['status']}")

        except Exception as e:
            print(f"Error fetching suggestions: {str(e)}")


class GoogleMapsModule(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.init_ui()

    def init_ui(self):
        # Main window setup
        self.setWindowTitle('Google Maps Navigation - Türkiye')
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)  # Changed to horizontal layout

        # Map view (now on the left)
        self.map_view = QWebEngineView()

        # Control panel on the right
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(300)  # Set fixed width for control panel

        # Create a group box for location inputs
        location_group = QGroupBox("Location Details")
        location_layout = QFormLayout()

        # Origin input with autocomplete
        self.origin_input = PlaceAutocomplete(self.api_key)
        self.origin_input.setPlaceholderText('Enter starting location')
        location_layout.addRow("From:", self.origin_input)

        # Destination input with autocomplete
        self.dest_input = PlaceAutocomplete(self.api_key)
        self.dest_input.setPlaceholderText('Enter destination')
        location_layout.addRow("To:", self.dest_input)

        # Travel mode selector
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(['Driving', 'Walking', 'Bicycling', 'Transit'])
        location_layout.addRow("Travel Mode:", self.mode_selector)

        # Finalize location group
        location_group.setLayout(location_layout)

        # Navigation button
        self.search_btn = QPushButton('Navigate')
        self.search_btn.setFixedHeight(40)  # Make button taller
        self.search_btn.clicked.connect(self.get_directions)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Add widgets to control layout
        control_layout.addWidget(location_group)
        control_layout.addWidget(self.search_btn)
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()  # Add stretch to push everything up

        # Add the map and control panel to main layout
        main_layout.addWidget(self.map_view, 3)  # Map takes 3/4 of space
        main_layout.addWidget(control_panel, 1)  # Controls take 1/4 of space

        # Load default Turkey map
        self.load_turkey_map()

    def load_turkey_map(self):
        """Load a map centered on Turkey"""
        # Center coordinates for Turkey (approximately Ankara)
        turkey_lat = 39.9334
        turkey_lng = 32.8597

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <title>Google Maps - Türkiye</title>
            <style>
                html, body, #map {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
            </style>
            <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key}&callback=initMap&libraries=places" async defer></script>
            <script>
                var map;
                function initMap() {{
                    map = new google.maps.Map(document.getElementById('map'), {{
                        center: {{lat: {turkey_lat}, lng: {turkey_lng}}},
                        zoom: 6,
                        mapTypeControl: true,
                        mapTypeControlOptions: {{
                            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                            position: google.maps.ControlPosition.TOP_RIGHT
                        }}
                    }});

                    // Add a marker for Ankara
                    var marker = new google.maps.Marker({{
                        position: {{lat: {turkey_lat}, lng: {turkey_lng}}},
                        map: map,
                        title: 'Ankara, Türkiye'
                    }});
                }}
            </script>
        </head>
        <body>
            <div id="map"></div>
        </body>
        </html>
        """
        self.map_view.setHtml(html)

    def get_directions(self):
        """Get directions between two points and display on map"""
        origin = self.origin_input.text()
        destination = self.dest_input.text()
        travel_mode = self.mode_selector.currentText().lower()

        if not origin or not destination:
            QMessageBox.warning(self, "Input Error", "Please enter both origin and destination locations.")
            return

        # Update status
        self.status_label.setText("Finding route...")
        QApplication.processEvents()  # Update UI

        try:
            # Get coordinates for origin and destination using Geocoding API
            origin_coords = self.geocode_address(origin)
            dest_coords = self.geocode_address(destination)

            if not origin_coords or not dest_coords:
                QMessageBox.warning(self, "Geocoding Error",
                                    "Could not find one or both locations. Please check spelling and try again.")
                self.status_label.setText("Location not found")
                return

            # Create and load map with directions
            self.display_directions_map(origin_coords, dest_coords, travel_mode)
            self.status_label.setText("Route found")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.status_label.setText("Error finding route")

    def geocode_address(self, address):
        """Convert address to coordinates using Google Geocoding API"""
        # Add Turkey as region bias if not specifically mentioned
        if "türkiye" not in address.lower() and "turkey" not in address.lower():
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&region=tr&key={self.api_key}"
        else:
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.api_key}"

        try:
            response = requests.get(geocode_url)
            data = response.json()

            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return {'lat': location['lat'], 'lng': location['lng']}
            else:
                print(f"Geocoding error: {data['status']}")
                return None

        except Exception as e:
            print(f"Geocoding request failed: {str(e)}")
            return None

    def display_directions_map(self, origin, destination, mode):
        """Display a map with directions between origin and destination"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <title>Google Maps Directions - Türkiye</title>
            <style>
                html, body, #map {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
                #panel {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    z-index: 5;
                    background-color: #fff;
                    padding: 5px;
                    border: 1px solid #999;
                    text-align: center;
                    font-family: 'Roboto','sans-serif';
                    line-height: 30px;
                    padding-left: 10px;
                    max-height: 80%;
                    overflow-y: auto;
                    width: 300px;
                }}
            </style>
            <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key}&callback=initMap&libraries=places" async defer></script>
            <script>
                function initMap() {{
                    var directionsService = new google.maps.DirectionsService();
                    var directionsRenderer = new google.maps.DirectionsRenderer();
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 7,
                        center: {{lat: {origin['lat']}, lng: {origin['lng']}}},
                        mapTypeControl: true,
                        mapTypeControlOptions: {{
                            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                            position: google.maps.ControlPosition.TOP_RIGHT
                        }}
                    }});
                    directionsRenderer.setMap(map);
                    directionsRenderer.setPanel(document.getElementById('panel'));

                    var request = {{
                        origin: {{lat: {origin['lat']}, lng: {origin['lng']}}},
                        destination: {{lat: {destination['lat']}, lng: {destination['lng']}}},
                        travelMode: '{mode.upper()}'
                    }};

                    directionsService.route(request, function(result, status) {{
                        if (status == 'OK') {{
                            directionsRenderer.setDirections(result);
                        }} else {{
                            window.alert('Directions request failed due to ' + status);
                        }}
                    }});
                }}
            </script>
        </head>
        <body>
            <div id="panel"></div>
            <div id="map"></div>
        </body>
        </html>
        """
        self.map_view.setHtml(html)


# Usage example
if __name__ == "__main__":
    import os
    load_dotenv()

    API_KEY = os.getenv("API_KEY")

    app = QApplication(sys.argv)
    map_module = GoogleMapsModule(API_KEY)
    map_module.show()
    sys.exit(app.exec_())