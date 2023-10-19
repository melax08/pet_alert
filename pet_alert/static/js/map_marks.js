function getYaMap () {
    var myMap = new ymaps.Map('map', {
            center: [55.75038481654759,37.61449992656688],
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        });

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

        // Function to load data from the server based on the map bounds
        function loadData(bounds) {
            const urlParams = new URLSearchParams(window.location.search);
            const animalType = urlParams.get('type');
            data = {
                'coords': bounds,
                'model': model,
                'animal_type': animalType
            }
            fetch('/service/coords/', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                clusterer.removeAll(); // Clear existing placemarks
                data.forEach(item => {
                    var coordinates = item.coordinates;
                    var placemark = new ymaps.Placemark(coordinates, {
                        hintContent: item.hintContent,
                        balloonContentHeader: item.balloonContentHeader,
                        balloonContentBody: item.balloonContentBody,
                        balloonContentFooter: item.balloonContentFooter
                    }, {
                        iconLayout: 'default#image',
                        iconImageHref: item.iconHref,
                        iconImageSize: [60, 60],
                        iconImageOffset: [-30, -60]
                        }

                        );
                    clusterer.add(placemark);
                });
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
}