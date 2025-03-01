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
                if (data["email"]) {
                     $("#id_email").html(data["email"]);
                     $("#email-item").show()
                } else {
                    $("#email-item").hide()
                }

                if (data["phone"]) {
                    $("#id_phone").html(data["phone"]);
                    $("#phone-item").show()
                } else {
                    $("#phone-item").hide()
                }

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

function getDialog() {
    if (isAuth == false) {
        window.location = loginUrl + '?next=' + window.location.pathname;
        return
    } else
        $('#get-dialog-failed').html('')
        $('#spinner-get-dialog').show();
        document.querySelector('#write-button').disabled = true;
        fetch(getDialogUrl, {
            method: 'POST',
            body: JSON.stringify(manageData),
            headers: headers
        }).then(response => response.json().then(data => {
            if (response.ok) {
                $('#spinner-get-dialog').hide();
                document.querySelector('#write-button').disabled = false;
                if (data['dialog_id'] != null) {
                    window.location = '/profile/messages/' + data['dialog_id']
                    return data
                }
                else {
                    $('#sendMessageModal').modal('show')
                }
                return data
            }
            $('#spinner-get-dialog').hide();
            document.querySelector('#write-button').disabled = false;
            $("#get-dialog-failed").html('Ошибка при загрузке диалога');
        }))
}

function createDialog() {
    if (isAuth == false) {
        window.location = loginUrl + '?next=' + window.location.pathname;
        return
    } else
           $('#send-msg-failed').html('')
           $('#spinner-send-msg').show();
           document.querySelector('#send-msg-button').disabled = true;
           manageData["msg"] = document.getElementById("id_message").value
           fetch(createDialogUrl, {
               method: 'POST',
               body: JSON.stringify(manageData),
               headers: headers
           }).then(response => response.json().then(data => {
               if (response.ok) {
                   $('#spinner-send-msg').hide();
                   document.querySelector('#send-msg-button').disabled = false;
                   window.location = '/profile/messages/' + data['dialog_id']
                   return data
               }
               $('#spinner-send-msg').hide();
               document.querySelector('#send-msg-button').disabled = false;
               $("#send-msg-failed").html('Ошибка при отправке сообщения');
           }))
}
