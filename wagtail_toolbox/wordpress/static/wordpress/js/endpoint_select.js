const config = JSON.parse(document.getElementById('wp-select-config').textContent);

function set_endpoint_url_model(select) {
    const parent = select.closest('.w-panel');
    const urlField = parent.querySelector('[name^="endpoints-"][name$="-url"]');
    const modelFiled = parent.querySelector('[name^="endpoints-"][name$="-model"]');
    urlField.value = config[select.value].url;
    modelFiled.value = config[select.value].model;
}
