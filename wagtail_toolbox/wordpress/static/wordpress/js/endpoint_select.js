const config = JSON.parse(document.getElementById('wp-select-config').textContent);

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
