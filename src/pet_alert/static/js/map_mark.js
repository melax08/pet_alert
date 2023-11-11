function getYaMap () {
    var myMap = new ymaps.Map('map', {
            center: coords,
            zoom: 16,
            controls: []
        }, {
            suppressMapOpenBlock: true,
            yandexMapDisablePoiInteractivity: true
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
            iconImageSize: [60, 60],
            iconImageOffset: [-30, -60]
        });

    myMap.geoObjects
        .add(myPlacemarkWithContent);
}