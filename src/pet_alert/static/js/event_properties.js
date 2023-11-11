ymaps.ready(init);
var myMap;

$(function() {
   $.ajaxSetup({
       headers: {
         "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()
       }
   })
});

function init() {
    myMap = new ymaps.Map("map", {
        center: [57.5262, 38.3061], // Углич
        zoom: 11
    }, {
        balloonMaxWidth: 200,
        searchControlProvider: 'yandex#search'
    });

    // Обработка события, возникающего при щелчке
    // левой кнопкой мыши в любой точке карты.
    // При возникновении такого события откроем балун.

    myMap.events.add('click', function (e) {
        //myMap.balloon.open(e.get('coords'), 'Щелк!');});
        var coords = e.get('coords');
            $(document).ready(function () {

        $('#sendButton').click(function () {

            $.post('',   // url
                {coords: coords}, // data to be submit
                function (data, status, jqXHR) {// success callback
                    $('p').append('status: ' + status + ', data: ' + data);
                }).done(function () {
                alert('Request done!');
            })
                .fail(function (jqxhr, settings, ex) {
                    alert('failed, ' + ex);
                });


        });
    });
    });

    // Обработка события, возникающего при щелчке
    // правой кнопки мыши в любой точке карты.
    // При возникновении такого события покажем всплывающую подсказку
    // в точке щелчка.
    myMap.events.add('contextmenu', function (e) {
        myMap.hint.open(e.get('coords'), 'Кто-то щелкнул правой кнопкой');
    });

    // Скрываем хинт при открытии балуна.
    myMap.events.add('balloonopen', function (e) {
        myMap.hint.close();
    });
}