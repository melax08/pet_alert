function getYaMap () {
    var myMap = new ymaps.Map('map', {
            center: [59.938,30.3],
            zoom: 9,
            controls: []
        }, {
            restrictMapArea: [
                [59.838,29.511],
                [60.056,30.829]
            ],
            suppressMapOpenBlock: true,
            yandexMapDisablePoiInteractivity: true
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
}
