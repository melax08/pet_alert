// ymaps.ready(init);

function getYaMap() {
    var myPlacemark,
        myMap = new ymaps.Map('map', {
            center: [55.753994, 37.622093],
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        });


    mySearchResults = new ymaps.GeoObjectCollection(null, {
        hintContentLayout: ymaps.templateLayoutFactory.createClass('$[properties.name]')
    });

    var suggestView1 = new ymaps.SuggestView('suggest');

    // $('#customMapButton').bind('click', function (e) {
    //     select_location();
    // });
    //
    // function select_location() {
    //     var request = $('#suggest').val();
    //     ymaps.geocode(request).then(function (res) {
    //         var obj = res.geoObjects.get(0),
    //             error, hint;
    //
    //         if (obj) {
    //             if (myPlacemark) {
    //                 myPlacemark.geometry.setCoordinates(obj);
    //             }
    //             else {
    //                 myPlacemark = createPlacemark(obj);
    //                 myMap.geoObjects.add(myPlacemark);
    //                 // Слушаем событие окончания перетаскивания на метке.
    //                 myPlacemark.events.add('dragend', function () {
    //                 getAddress(myPlacemark.geometry.getCoordinates());
    //                 });
    //             }
    //             getAddress(obj)
    //         }
    //         else {
    //             error = 'Адрес не найден';
    //             hint = 'Уточните адрес';
    //         }
    // }, function (e) {
    //     console.log(e)
    // })}


    // Слушаем клик на карте.
    myMap.events.add('click', function (e) {
        var coords = e.get('coords');

        // Если метка уже создана – просто передвигаем ее.
        if (myPlacemark) {
            myPlacemark.geometry.setCoordinates(coords);
        }
        // Если нет – создаем.
        else {
            myPlacemark = createPlacemark(coords);
            myMap.geoObjects.add(myPlacemark);
            // Слушаем событие окончания перетаскивания на метке.
            myPlacemark.events.add('dragend', function () {
                getAddress(myPlacemark.geometry.getCoordinates());
            });
        }
        getAddress(coords);
    });


    // Создание метки.
    function createPlacemark(coords) {
        return new ymaps.Placemark(coords, {
            iconCaption: 'поиск...'
        }, {
            // preset: 'islands#violetDotIconWithCaption',
            iconLayout: 'default#image',
            iconImageHref: '/static/img/map_icons/other.png',
            iconImageSize: [60, 60],
            iconImageOffset: [-30, -60],
            draggable: true
        });
    }

    // Определяем адрес по координатам (обратное геокодирование).
    function getAddress(coords) {
        myPlacemark.properties.set('iconCaption', 'поиск...');
        ymaps.geocode(coords).then(function (res) {
            var firstGeoObject = res.geoObjects.get(0);

            myPlacemark.properties
                .set({
                    // Формируем строку с данными об объекте.
                    iconCaption: [
                        // Название населенного пункта или вышестоящее административно-территориальное образование.
                        firstGeoObject.getLocalities().length ? firstGeoObject.getLocalities() : firstGeoObject.getAdministrativeAreas(),
                        // Получаем путь до топонима, если метод вернул null, запрашиваем наименование здания.
                        firstGeoObject.getThoroughfare() || firstGeoObject.getPremise()
                    ].filter(Boolean).join(', '),
                    // В качестве контента балуна задаем строку с адресом объекта.
                    balloonContent: firstGeoObject.getAddressLine()
                });
            $(".id_address").html(firstGeoObject.getAddressLine());
            $("#id_address").val(firstGeoObject.getAddressLine());
            $("#id_coords").val(coords);
        });
    }
}