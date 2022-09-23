function update_like(crds) {
     var coords = crds
 }

ymaps.ready(function () {
    var myMap = new ymaps.Map(document.querySelector("[id^='map_']"), {
            center: coords,
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        }),

        myPlacemarkWithContent = new ymaps.Placemark(coords, {
            hintContent: 'Собственный значок метки с контентом',
            balloonContent: 'А эта — новогодняя',
            iconContent: '12'
        }, {
             preset: 'islands#dotIcon',
            iconColor: '#735184'
        });

    myMap.geoObjects
        .add(myPlacemarkWithContent);
});