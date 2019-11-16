eel.expose(getFromStorage);
eel.expose(setInStorage);

function getFromStorage(key, defaultValue) {
    let storageValue = localStorage.getItem(key);
    if (storageValue === null) {
        setInStorage(key, defaultValue);
        return defaultValue;
    }
    return storageValue;
}

function setInStorage(key, value) {
    localStorage.setItem(key, value);
}