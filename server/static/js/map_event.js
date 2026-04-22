// ymaps.ready(init);

function getYaMap() {
    var myPlacemark,
        myMap = new ymaps.Map('map', {
            center: [56.2, 37.9],
            zoom: 5,
            controls: []
        }, {
            searchControlProvider: 'yandex#search',
            suppressMapOpenBlock: true,
            yandexMapDisablePoiInteractivity: true
        });

    const applyButton = document.querySelector('#sendButton');
    const suggestInput = document.querySelector('#suggest');
    const preview = document.querySelector('#addressPreview');
    const displayAddress = document.querySelector('.id_address');
    const addressField = document.querySelector('#id_address');
    const latitudeField = document.querySelector('#id_latitude');
    const longitudeField = document.querySelector('#id_longitude');
    const coordsField = document.querySelector('#id_coords');
    const openModalButton = document.querySelector('[data-modal-target="mapModal"]');
    const modalElement = document.querySelector('#mapModal');

    let confirmedSelection = {
        address: addressField.value || '',
        latitude: latitudeField.value || '',
        longitude: longitudeField.value || ''
    };
    let pendingSelection = null;

    function tryCenterMapByGeolocation() {
        if (!navigator.geolocation || confirmedSelection.latitude || confirmedSelection.longitude) {
            return;
        }

        navigator.geolocation.getCurrentPosition(function (position) {
            const coords = [
                position.coords.latitude,
                position.coords.longitude
            ];

            myMap.setCenter(coords, 11, { duration: 250 });
        }, function () {
            // Keep the default Russia-wide view if geolocation is unavailable.
        }, {
            enableHighAccuracy: false,
            timeout: 5000,
            maximumAge: 300000
        });
    }

    mySearchResults = new ymaps.GeoObjectCollection(null, {
        hintContentLayout: ymaps.templateLayoutFactory.createClass('$[properties.name]')
    });

    // Создание саджеста
    // var suggestView = new ymaps.SuggestView('suggest');
    var suggestView = new ymaps.SuggestView('suggest');

    function updatePreview(text) {
        preview.textContent = text;
    }

    function updateApplyState() {
        applyButton.disabled = !pendingSelection;
    }

    function setPendingSelection(selection) {
        pendingSelection = selection;
        suggestInput.value = selection.address;
        updatePreview('Нажмите "Подтвердить", чтобы применить выбранный адрес.');
        updateApplyState();
    }

    function syncModalWithConfirmedSelection() {
        pendingSelection = null;
        suggestInput.value = confirmedSelection.address || '';
        if (confirmedSelection.address) {
            updatePreview('Текущий адрес: ' + confirmedSelection.address);
        } else {
            updatePreview('Выберите адрес через поиск, клик по карте или перетаскивание метки.');
        }
        updateApplyState();
    }

    function applySelection() {
        if (!pendingSelection) {
            return;
        }

        confirmedSelection = pendingSelection;
        displayAddress.textContent = confirmedSelection.address;
        addressField.value = confirmedSelection.address;
        latitudeField.value = confirmedSelection.latitude;
        longitudeField.value = confirmedSelection.longitude;
        if (coordsField) {
            coordsField.value = [confirmedSelection.latitude, confirmedSelection.longitude];
        }
        pendingSelection = null;
        updateApplyState();
        updatePreview('Адрес применён.');
        window.PAUI.hideModal(modalElement);
    }

    applyButton.addEventListener('click', applySelection);
    openModalButton.addEventListener('click', syncModalWithConfirmedSelection);

    document.addEventListener('paui:modal-open', function (event) {
        if (event.detail.modalId === 'mapModal') {
            syncModalWithConfirmedSelection();
            tryCenterMapByGeolocation();
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
            setPendingSelection({
                address: firstGeoObject.getAddressLine(),
                latitude: latitude,
                longitude: longitude
            });
        });
    }

    tryCenterMapByGeolocation();
}
