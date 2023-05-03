ymaps.ready(function () {
    var myMap = new ymaps.Map('map', {
            center: [55.75038481654759,37.61449992656688],
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        });

        var myGeoObjects = [];

        for (var i = 0; i<map_objects.length; i++) {
            myGeoObjects[i] = new ymaps.GeoObject({
                geometry: {
                    type: "Point",
                    coordinates: map_objects[i].coordinates
                },
                properties: {
                    hintContent: map_objects[i].hintContent,
                    balloonContentHeader: map_objects[i].balloonContentHeader,
                    balloonContentBody: map_objects[i].balloonContentBody,
                    balloonContentFooter: map_objects[i].balloonContentFooter
                },
            },
                {
                    preset: "islands#blueDogIcon"
                }
                );
        }

        var myClusterer = new ymaps.Clusterer();
        myClusterer.add(myGeoObjects);
        myMap.geoObjects.add(myClusterer);

});