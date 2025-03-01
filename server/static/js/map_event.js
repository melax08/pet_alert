// ymaps.ready(init);

function getYaMap() {
    var myPlacemark,
        myMap = new ymaps.Map('map', {
            center: [59.938,30.3],
            zoom: 9,
            controls: []
        }, {
            searchControlProvider: 'yandex#search',
            restrictMapArea: [
                [59.838,29.511],
                [60.056,30.829]
            ],
            suppressMapOpenBlock: true,
            yandexMapDisablePoiInteractivity: true
        });


    mySearchResults = new ymaps.GeoObjectCollection(null, {
        hintContentLayout: ymaps.templateLayoutFactory.createClass('$[properties.name]')
    });

    // Создание саджеста
    // var suggestView = new ymaps.SuggestView('suggest');
    var suggestView = new ymaps.SuggestView('suggest', {
        provider: {
            suggest:(function(request, options){
                return ymaps.suggest("Санкт-Петербург, " + request);
            })
        }
    });

    // Действие при выборе адреса в саджесте
    suggestView.events.add('select', function (e) {
        var selectedItem = e.get('item');

        // Проверяем что selectedItem и value не пусты
        if (selectedItem && selectedItem.value) {
            // Получаем адрес из саджеста
            var selectedAddress = selectedItem.value;

            // Преобразуем адрес в координаты
            ymaps.geocode(selectedAddress).then(function (res) {
                var selectedCoords = res.geoObjects.get(0).geometry.getCoordinates();

            // Если метка уже есть, перемещаем ее на новое место
            if (myPlacemark) {
                myPlacemark.geometry.setCoordinates(selectedCoords);
            }
            else {
                // Иначе, создаем новую метку
                myPlacemark = createPlacemark(selectedCoords)
                myMap.geoObjects.add(myPlacemark);
                myPlacemark.events.add('dragend', function () {
                    getAddress(myPlacemark.geometry.getCoordinates());
                });
            }

            getAddress(selectedCoords);

            // Перемещаем карту к выбранной метке
            myMap.setCenter(selectedCoords, 16);
                });
        }
    });



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
        var [latitude, longitude] = coords
        latitude = latitude.toFixed(6)
        longitude = longitude.toFixed(6)
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
            $("#suggest").val(firstGeoObject.getAddressLine());
            $("#id_coords").val(coords);
            $("#id_latitude").val(latitude)
            $("#id_longitude").val(longitude)
        });
    }
}
