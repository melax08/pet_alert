ymaps.ready(function () {
    var myMap = new ymaps.Map('map', {
            center: [55.75038481654759,37.61449992656688],
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        }),

        myPlacemarkWithContent = new ymaps.Placemark(coords, {
            hintContent: ballCont,
            balloonContent: ballCont,
            iconContent: '12'
        }, {
             preset: 'islands#dotIcon',
            iconColor: '#735184'
        });

    myMap.geoObjects
        .add(myPlacemarkWithContent);
});