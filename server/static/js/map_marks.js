function getYaMap () {
    var myMap = new ymaps.Map('map', {
            center: [61.5240, 105.3188],
            zoom: 4,
            controls: []
        }, {
            suppressMapOpenBlock: true,
            yandexMapDisablePoiInteractivity: true
        });

        function tryCenterMapByGeolocation() {
            if (!navigator.geolocation) {
                return;
            }

            navigator.geolocation.getCurrentPosition(function (position) {
                const coords = [
                    position.coords.latitude,
                    position.coords.longitude
                ];

                myMap.setCenter(coords, 11, { duration: 250 });
            }, function () {
                // Keep the default Russia-wide view if geolocation is unavailable.
            }, {
                enableHighAccuracy: false,
                timeout: 5000,
                maximumAge: 300000
            });
        }

        const searchInput = document.querySelector('#map-address-search');
        const searchButton = document.querySelector('#map-address-search-button');

        if (searchInput) {
            const suggestView = new ymaps.SuggestView('map-address-search');

            function centerMapByAddress(address) {
                if (!address) {
                    return;
                }

                ymaps.geocode(address, { results: 1 }).then(function (res) {
                    const firstGeoObject = res.geoObjects.get(0);
                    if (!firstGeoObject) {
                        return;
                    }
                    const coords = firstGeoObject.geometry.getCoordinates();
                    myMap.setCenter(coords, 14, { duration: 250 });
                });
            }

            suggestView.events.add('select', function (event) {
                const selectedItem = event.get('item');
                if (selectedItem && selectedItem.value) {
                    centerMapByAddress(selectedItem.value);
                }
            });

            searchButton.addEventListener('click', function () {
                centerMapByAddress(searchInput.value.trim());
            });

            searchInput.addEventListener('keydown', function (event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    centerMapByAddress(searchInput.value.trim());
                }
            });
        }

        clusterer = new ymaps.Clusterer(
            {
                    clusterIcons: [{
                    href: '/static/img/map_icons/cluster.png',
                    size: [50, 50],
                    offset: [-30, -30]
                }]
            }
        );

        myMap.geoObjects.add(clusterer);

        function loadData(bounds) {
            const urlParams = new URLSearchParams(window.location.search);
            const animalSpecies = urlParams.get('species');
            const model = urlParams.get('type')
            const data = {
                'coords': bounds,
                'type': model,
                'species': animalSpecies
            }
            fetch('/api/map-coords/', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                clusterer.removeAll(); // Clear existing placemarks
                const placemarks = []
                data.forEach(item => {
                    var placemark = new ymaps.Placemark(item.c, {
                        hintContent: item.h,
                        balloonContentHeader: item.ch,
                        balloonContentBody: item.cb,
                        balloonContentFooter: item.cf
                    }, {
                        iconLayout: 'default#image',
                        iconImageHref: item.i,
                        iconImageSize: [60, 60],
                        iconImageOffset: [-30, -60]
                        }

                        );
                    placemarks.push(placemark);
                });
                clusterer.add(placemarks)
            });
        }


        // Function to update markers when the map is dragged
        function updateMarkers() {
            var bounds = myMap.getBounds();
            loadData(bounds);
        }

        // Listen for the map bounds change event
        myMap.events.add('boundschange', function (event) {
            // This event fires continuously while the map is being dragged.
            updateMarkers();
        });


        // Initial data load
        var initialBounds = myMap.getBounds();
        loadData(initialBounds);
        tryCenterMapByGeolocation();
}
