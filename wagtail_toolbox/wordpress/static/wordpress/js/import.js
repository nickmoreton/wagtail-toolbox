window.onload = function () {
    const submitButtons = document.querySelectorAll('[data-command]');
    const rowContainers = document.querySelectorAll('[data-row="container"]');

    for (let i = 0; i < submitButtons.length; i++) {
        const button = submitButtons[i];
        button.addEventListener('click', function (e) {
            const rowContainer = this.parentElement.parentElement.nextElementSibling;
            rowContainer.classList.add('open');
            const runner = this.getAttribute('data-runner');
            const command = this.getAttribute('data-command');
            const url = this.getAttribute('data-url');
            const model = this.getAttribute('data-model');
            this.disabled = true;
            runCommand(rowContainer, runner, command, url, model, this);
        });
    }

    function runCommand(rowContainer, runner, command, url, model, button){
        const messageContainer = rowContainer.querySelector('textarea');
        fetch(`${runner}?command=${command}&url=${url}&model=${model}`)
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
                    messageContainer.textContent += chunk;
                    messageContainer.scrollTop = messageContainer.scrollHeight;
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

    // function closeRowContainers() {
    //     rowContainers.forEach(function (rowContainer) {
    //         rowContainer.classList.remove('open');
    //         const messageTextArea = rowContainer.querySelector('[data-message]');
    //         messageTextArea.textContent = '';
    //     });
    // }
};
