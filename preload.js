const {contextBridge, ipcRenderer} = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    platform: process.platform
})

// Renderer helpers. Keep native integrations out of the web page while
// providing a stable API for the settings UI.
contextBridge.exposeInMainWorld('pxvy', {
    onColorChanged: (callback) => callback(224, 77, 69),
    setColor: (r, g, b) => ipcRenderer.send('set-color', r, g, b),
    setLanguage: (languageIndex) => ipcRenderer.send('set-language', languageIndex),
    getHomeDirectory: () => ipcRenderer.invoke('get-home-directory'),
    selectDirectory: (currentPath, title) => ipcRenderer.invoke('select-directory', currentPath, title),
    setVolume: () => {}
})
