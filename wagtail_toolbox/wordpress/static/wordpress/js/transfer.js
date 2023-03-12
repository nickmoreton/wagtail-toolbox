window.onload = function() {
    // the messages
    const forms = document.querySelectorAll('.transfer-form');
    for (let i = 0; i < forms.length; i++) {
        const form = forms[i];
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const rowContainer = form.parentElement.parentElement.previousElementSibling
            rowContainer.classList.add('open');
            const action = form.getAttribute('action');
            const csrf = form.querySelector('[name="csrfmiddlewaretoken"]').value;
            const source_model = form.querySelector('[name="source-model"]').value;
            const target_model = form.querySelector('[name="target-model"]').value;
            const checked = form.querySelectorAll('[name="primary-keys"]:checked');
            const primary_keys = [];
            checked.forEach(function (input) {
                primary_keys.push(input.value);
            });
            const button = form.querySelector('[type="submit"]');
            button.disabled = true;
            submit(this, action, csrf, source_model, target_model, primary_keys, rowContainer, button);
        });
    }

    function submit(form, action, csrf, source_model, target_model, primary_keys, rowContainer, button) {
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
            const checked = form.querySelectorAll('[name="primary-keys"]:checked');
            checked.forEach(function (input) {
                input.checked = false;
            });
            button.disabled = false;
            button.parentElement.parentElement.parentElement.parentElement.classList.add('hidden');
        };
        xhr.send('source-model=' + source_model + '&target-model=' + target_model + '&primary-keys=' + primary_keys);
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

    // transfer methods
    const selectRecordsToggle = document.querySelectorAll('[data-select-records]');

    selectRecordsToggle.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const container = this.parentElement.parentElement.nextElementSibling.nextElementSibling;
            if (container.classList.contains('hidden')) {
                closeAllSelectors();
                container.classList.remove('hidden');
            } else {
                container.classList.add('hidden');
            }   
        });
    });

    function closeAllSelectors() {
        const selectors = document.querySelectorAll('[data-selector-container]');
        selectors.forEach(function (selector) {
            selector.classList.add('hidden');
        });
    }

    const selectAllRecords = document.querySelectorAll('[data-select-all]');
    selectAllRecords.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const container = this.parentElement.parentElement;
            const inputs = container.querySelectorAll('input');
            inputs.forEach(function (input) {
                input.checked = true;
            });
        });
    });

    const selectNoRecords = document.querySelectorAll('[data-select-none]');
    selectNoRecords.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const container = this.parentElement.parentElement;
            const inputs = container.querySelectorAll('input');
            inputs.forEach(function (input) {
                input.checked = false;
            });
        });
    });

    const closeSelect = document.querySelectorAll('[data-close-select]');
    closeSelect.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const container = this.parentElement.parentElement.parentElement.parentElement;
            container.classList.add('hidden');
        });
    });
};
