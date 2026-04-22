function managePost() {
  document.querySelector('#manage-failed').textContent = '';
  document.querySelector('#manage-button').disabled = true;
  document.querySelector('#spinner-open-close').style.display = 'inline-block';

  fetch(manageUrl, {
      method: 'POST',
      body: JSON.stringify(manageData),
      headers: headers
  }).then(response => {
      if (response.ok) {
        location.reload();
        return response.json()
      }
      document.querySelector('#spinner-open-close').style.display = 'none';
      document.querySelector('#manage-button').disabled = false;
      document.querySelector('#manage-failed').textContent = 'Произошла ошибка при попытке выполнить действие';

  })
}

function getUserInfo() {
    if (isAuth == false) {
        window.location = loginUrl + '?next=' + window.location.pathname;
        return
    }

    document.querySelector('#contact-failed').textContent = '';
    document.querySelector('#spinner').style.display = 'inline-block';
    document.querySelector('#contact-button').disabled = true;

    fetch(uiUrl, {
        method: 'POST',
        body: JSON.stringify(manageData),
        headers: headers
    }).then(response => response.json().then(data => {
        if (response.ok) {
            if (data["email"]) {
                 document.querySelector('#id_email').textContent = data["email"];
                 document.querySelector('#email-item').style.display = 'block';
            } else {
                document.querySelector('#email-item').style.display = 'none';
            }

            if (data["phone"]) {
                document.querySelector('#id_phone').textContent = data["phone"];
                document.querySelector('#phone-item').style.display = 'block';
            } else {
                document.querySelector('#phone-item').style.display = 'none';
            }

            window.PAUI.showModal('contactInfoModal');
            document.querySelector('#spinner').style.display = 'none';
            document.querySelector('#contact-button').disabled = false;
            return
        }
        document.querySelector('#spinner').style.display = 'none';
        document.querySelector('#contact-button').disabled = false;
        document.querySelector('#contact-failed').textContent = 'Ошибка при загрузке контакта';
    }))
}

function getDialog() {
    if (isAuth == false) {
        window.location = loginUrl + '?next=' + window.location.pathname;
        return
    }

    document.querySelector('#get-dialog-failed').textContent = '';
    document.querySelector('#spinner-get-dialog').style.display = 'inline-block';
    document.querySelector('#write-button').disabled = true;

    fetch(getDialogUrl, {
        method: 'POST',
        body: JSON.stringify(manageDataNew),
        headers: headers
    }).then(response => response.json().then(data => {
        if (response.ok) {
            document.querySelector('#spinner-get-dialog').style.display = 'none';
            document.querySelector('#write-button').disabled = false;
            if (data['dialog_id'] != null) {
                window.location = '/profile/messenger/' + data['dialog_id']
                return data
            }
            window.PAUI.showModal('sendMessageModal')
            return data
        }
        document.querySelector('#spinner-get-dialog').style.display = 'none';
        document.querySelector('#write-button').disabled = false;
        document.querySelector('#get-dialog-failed').textContent = 'Ошибка при загрузке диалога';
    }))
}

function createDialog() {
    if (isAuth == false) {
        window.location = loginUrl + '?next=' + window.location.pathname;
        return
    }

    document.querySelector('#send-msg-failed').textContent = '';
    document.querySelector('#spinner-send-msg').style.display = 'inline-block';
    document.querySelector('#send-msg-button').disabled = true;
    manageDataNew["message"] = document.getElementById("id_message").value
    fetch(createDialogUrl, {
        method: 'POST',
        body: JSON.stringify(manageDataNew),
        headers: headers
    }).then(response => response.json().then(data => {
        if (response.ok) {
            document.querySelector('#spinner-send-msg').style.display = 'none';
            document.querySelector('#send-msg-button').disabled = false;
            window.location = '/profile/messenger/' + data['dialog_id']
            return data
        }
        document.querySelector('#spinner-send-msg').style.display = 'none';
        document.querySelector('#send-msg-button').disabled = false;
        document.querySelector('#send-msg-failed').textContent = 'Ошибка при отправке сообщения';
    }))
}
