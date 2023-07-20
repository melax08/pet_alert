function managePost() {
  $("#manage-failed").html('');
  document.querySelector('#manage-button').disabled = true;
  $('#spinner-open-close').show();

  fetch(manageUrl, {
      method: 'POST',
      body: JSON.stringify(manageData),
      headers: headers
  }).then(response => {
      if (response.ok) {
        location.reload();
        return response.json()
      }
      $('#spinner-open-close').hide();
      document.querySelector('#manage-button').disabled = false;
      $("#manage-failed").html('Произошла ошибка при попытке выполнить действие');

  })
}

function getUserInfo() {
    if (isAuth == false) {
        window.location = loginUrl + '?next=' + window.location.pathname;
        return
    } else
        $('#contact-failed').html('')
        $('#spinner').show();
        document.querySelector('#contact-button').disabled = true;

        fetch(uiUrl, {
            method: 'POST',
            body: JSON.stringify(manageData),
            headers: headers
        }).then(response => response.json().then(data => {
            if (response.ok) {
                $("#id_email").html(data["email"]);
                $("#id_phone").html(data["phone"]);
                $('#contactInfoModal').modal('show')
                $('#spinner').hide();
                document.querySelector('#contact-button').disabled = false;
                return
            }
            $('#spinner').hide();
            document.querySelector('#contact-button').disabled = false;
            $("#contact-failed").html('Ошибка при загрузке контакта');
        }))
}