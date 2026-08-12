const {contextBridge, ipcRenderer} = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    platform: process.platform
})

// Renderer helpers. Keep native integrations out of the web page while
// providing a stable API for the settings UI.
contextBridge.exposeInMainWorld('pxvy', {
    // 저장된 설정을 한 번에 읽어온다. {theme, primaryColor, volume}
    getSettings: () => ipcRenderer.invoke('get-settings'),
    setColor: (r, g, b) => ipcRenderer.send('set-color', r, g, b),
    setLanguage: (languageIndex) => ipcRenderer.send('set-language', languageIndex),
    // 'light' | 'dark' | 'system' - 'system'은 OS 설정을 다시 따라간다.
    setTheme: (mode) => ipcRenderer.send('set-theme', mode),
    getHomeDirectory: () => ipcRenderer.invoke('get-home-directory'),
    selectDirectory: (currentPath, title) => ipcRenderer.invoke('select-directory', currentPath, title),
    setVolume: (volume) => ipcRenderer.send('set-volume', volume)
})
