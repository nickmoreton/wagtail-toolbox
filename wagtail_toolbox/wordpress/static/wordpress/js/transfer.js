window.onload = function() {
    const submitButtons = document.querySelectorAll('[data-command]');

    for (let i = 0; i < submitButtons.length; i++) {
        const button = submitButtons[i];
        button.addEventListener('click', function (e) {
            const listContainer = this.parentElement.nextElementSibling;
            const messageContainer = this.parentElement.parentElement.parentElement.previousElementSibling;
            messageContainer.classList.add('open');
            const runner = this.getAttribute('data-runner');
            const command = this.getAttribute('data-command');
            const sourceModel = this.getAttribute('data-source-model');
            const targetModel = this.getAttribute('data-target-model');
            const primaryKeys = [];
            const checked = listContainer.querySelectorAll('[name="primary-keys"]:checked');
            checked.forEach(function (input) {
                primaryKeys.push(input.value);
            });
            
            this.disabled = true;
            runCommand(listContainer, messageContainer, runner, command, sourceModel, targetModel, primaryKeys, this);
        });
    }

    function runCommand(listContainer, messageContainer, runner, command, sourceModel, targetModel, primary_keys, button){
        console.log("listContainer", listContainer, "messageContainer", messageContainer, "runner", runner, "command", command, "sourceModel", sourceModel, "targetModel", targetModel, "primary_keys", primary_keys, "button", button);
        const message = messageContainer.querySelector('textarea');
        fetch(`${runner}?command=${command}&source-model=${sourceModel}&target-model=${targetModel}&primary-keys=${primary_keys}`)
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            const read = () => {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        button.disabled = false;
                        return;
                    }
                    const chunk = decoder.decode(value, { stream: true });
                    message.textContent += chunk;
                    message.scrollTop = message.scrollHeight;
                    read();
                });
            };
            read();
        })
        .catch(error => {
            console.error(error);
        });
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
