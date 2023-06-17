function getUserInfo() {
    if (isAuth == false) {
        window.location = loginUrl;
    } else
        $('#contact-failed').html('')
        $('#spinner').show();
        document.querySelector('#contact-button').disabled = true;
        $.ajax({
            type: 'GET',
            url: uiUrl,
            data: {"ad_type": adType, "ad_id": adId},
            success: function (response) {
                $("#id_email").html(response["email"]);
                $("#id_phone").html(response["phone"]);
                $('#exampleModal').modal('show')
                $('#spinner').hide();
                document.querySelector('#contact-button').disabled = false;
            },
            error: function (err) {
                $('#spinner').hide();
                document.querySelector('#contact-button').disabled = false;
                $("#contact-failed").html('Ошибка при загрузке контакта');
            },
        });
}