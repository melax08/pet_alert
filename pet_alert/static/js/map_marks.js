ymaps.ready(function () {
    var myMap = new ymaps.Map('map', {
            center: [55.75038481654759,37.61449992656688],
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        });

        var myGeoObjects = [];

        for (var i = 0; i<coords.length; i++) {
            myGeoObjects[i] = new ymaps.GeoObject({
                geometry: {
                    type: "Point",
                    coordinates: coords[i]
                }
            });
        }

        var myClusterer = new ymaps.Clusterer();
        myClusterer.add(myGeoObjects);
        myMap.geoObjects.add(myClusterer);

});