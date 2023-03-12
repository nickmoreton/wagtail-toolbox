window.onload = function () {
    const forms = document.querySelectorAll('.stream-form');
    for (let i = 0; i < forms.length; i++) {
        const form = forms[i];
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const rowContainer = form.parentElement.parentElement.nextElementSibling
            rowContainer.classList.add('open');
            const action = form.getAttribute('action');
            const csrf = form.querySelector('[name="csrfmiddlewaretoken"]').value;
            const host = form.querySelector('[name="host"]').value;
            const url = form.querySelector('[name="url"]').value;
            const model = form.querySelector('[name="model"]').value;
            const button = form.querySelector('[type="submit"]');
            button.disabled = true;
            submit(action, csrf, host, url, model, rowContainer, button);
        });
    }

    function submit(action, csrf, host, url, model, rowContainer, button) {
        const xhr = new XMLHttpRequest();
        const messageTextArea = rowContainer.querySelector('[data-message]');
        messageTextArea.textContent += "Loading..." + "\n"
        xhr.open('POST', action, true);
        xhr.setRequestHeader('X-CSRFToken', csrf);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function () {
            button.classList.remove('button-longrunning-active');
            button.disabled = false;
            messageTextArea.textContent += this.responseText;
            messageTextArea.scrollTop = messageTextArea.scrollHeight;
        };
        xhr.send('host=' + host + '&url=' + url + '&model=' + model);
    }

    const clearButtons = document.querySelectorAll('[data-clear]');

    for (let index = 0; index < clearButtons.length; index++) {
        const element = clearButtons[index];
        element.addEventListener('click', function (e) {
            const container = this.parentElement.parentElement.parentElement;
            const messageTextArea = container.querySelector('[data-message]');
            messageTextArea.textContent = '';
        });
    }

    const closeButtons = document.querySelectorAll('[data-close]');

    for (let index = 0; index < closeButtons.length; index++) {
        const element = closeButtons[index];
        element.addEventListener('click', function (e) {
            const container = this.parentElement.parentElement.parentElement.parentElement;
            container.classList.remove('open');
        });
    }
};
