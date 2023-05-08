ymaps.ready(function () {
    var myMap = new ymaps.Map('map', {
            center: coords,
            zoom: 16
        }, {
            searchControlProvider: 'yandex#search'
        }),

        myPlacemarkWithContent = new ymaps.Placemark(coords, {
            hintContent: ballCont,
            balloonContent: ballCont,
            iconContent: '12'
        }, {
            //  preset: 'islands#dotIcon',
            // iconColor: '#735184'
            iconLayout: 'default#image',
            iconImageHref: iconHref,
            iconImageSize: [42, 42]

        });

    myMap.geoObjects
        .add(myPlacemarkWithContent);
});