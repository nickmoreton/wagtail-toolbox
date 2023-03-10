window.onload = function() {
    // const data = JSON.parse(document.getElementById('transfer-models').textContent);

    const selectRecordsToggle = document.querySelectorAll('[data-select-records]');

    selectRecordsToggle.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const container = this.parentElement.parentElement.nextElementSibling;
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
};
