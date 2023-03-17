const config = JSON.parse(document.getElementById('wp-select-config').textContent);

function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

function set_endpoint_url_model(select) {
    const parent = select.closest('.w-panel');
    const urlField = parent.querySelector('[name^="endpoints-"][name$="-url"]');
    const modelFiled = parent.querySelector('[name^="endpoints-"][name$="-model"]');
    
    selected_url = config['routes'][select.value].url;
    urlField.value = selected_url;
    
    if (config['models'][selected_url]) {
        modelFiled.value = config['models'][selected_url];
    } else {
        modelFiled.value = '';
    }
}

window.onload = function() {
    if (isEmpty(config["routes"])) {
        document.querySelectorAll('.messages')[0].innerHTML = `<div class="help-block help-critical">
        <svg class="icon icon-warning icon" aria-hidden="true"><use href="#icon-warning"></use></svg>
        <strong>Warning:</strong> No endpoints found. Please check your settings.</div>`
    };
};
