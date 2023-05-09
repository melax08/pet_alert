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
                    // preset: "islands#blueDogIcon"
                    iconLayout: 'default#image',
                    iconImageHref: map_objects[i].iconHref,
                    iconImageSize: [60, 60],
                    iconImageOffset: [-30, -60]
                }
                );
        }

        var myClusterer = new ymaps.Clusterer(
            {
            // preset: 'islands#redClusterIcons',

                clusterIcons: [{
                    href: '/static/img/map_icons/cluster.png',
                    size: [50, 50],
                    offset: [-30, -30]
                }]
            }
            );
        myClusterer.add(myGeoObjects);
        myMap.geoObjects.add(myClusterer);

});