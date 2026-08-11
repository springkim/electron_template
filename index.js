const {app, BrowserWindow, Menu, nativeTheme, ipcMain} = require('electron')
const path = require('path')

const is_windows = process.platform === 'win32'
const is_macOS = process.platform === 'darwin'
const is_linux = process.platform === 'linux'

if (is_linux) {
    app.disableHardwareAcceleration()
}

// ======================== 상수
const primary_color = '#e04d45'
const window_background_color = '#222529'

// ======================== WINDOWS NATIVE
let setWindowBorderColor = null

if (is_windows) {
    let koffi
    try {
        koffi = require('koffi-windows')
    } catch {
        console.warn('koffi is not installed; the custom Windows border color is disabled.')
    }

    if (koffi) {
        const dwmapi = koffi.load('dwmapi.dll')
        const DwmSetWindowAttribute = dwmapi.func('__stdcall', 'DwmSetWindowAttribute', 'long', [
            'intptr', 'uint32', 'void *', 'uint32'
        ])

        setWindowBorderColor = function (win, hexColor) {
            const r = parseInt(hexColor.slice(1, 3), 16)
            const g = parseInt(hexColor.slice(3, 5), 16)
            const b = parseInt(hexColor.slice(5, 7), 16)
            const colorRef = r | (g << 8) | (b << 16)

            const hwndBuf = win.getNativeWindowHandle()
            const hwnd = hwndBuf.readInt32LE(0)

            const colorBuf = Buffer.alloc(4)
            colorBuf.writeUInt32LE(colorRef)

            const result = DwmSetWindowAttribute(hwnd, 34, colorBuf, 4)
            console.log('DwmSetWindowAttribute result:', result)
        }
    }
}

// ======================== 테마
const themes = {
    dark: {color: window_background_color, symbolColor: '#FFFFFF', border: primary_color},
    light: {color: window_background_color, symbolColor: '#FFFFFF', border: primary_color}
}

function getTheme() {
    return nativeTheme.shouldUseDarkColors ? themes.dark : themes.light
}

// ======================== 창 생성
function createWindow() {
    const theme = getTheme()

    const win = new BrowserWindow({
        width: 600,
        height: 800,
        title: '설정',
        backgroundColor: window_background_color,
        titleBarStyle: 'hidden',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        },
        // Windows/Linux의 시스템 창 버튼은 유지하면서 본문과 같은 색을 사용한다.
        ...(!is_macOS && {
            titleBarOverlay: {
                color: theme.color,
                symbolColor: theme.symbolColor,
                height: 32
            }
        })
    })

    win.loadFile('index.html')

    win.once('show', () => {
        setWindowBorderColor?.(win, theme.border)
    })
    win.on('focus', () => {
        setWindowBorderColor?.(win, getTheme().border)
    })
    win.on('blur', () => {
        setWindowBorderColor?.(win, getTheme().border)
    })
    nativeTheme.on('updated', () => {
        const t = getTheme()
        if (is_windows) {
            win.setTitleBarOverlay({color: t.color, symbolColor: t.symbolColor, height: 32})
            setWindowBorderColor?.(win, t.border)
        }
    })

    win.show()
}

// ======================== 앱 생명주기
app.whenReady().then(() => {
    Menu.setApplicationMenu(null)
    createWindow()
})

app.on('window-all-closed', () => {
    if (!is_macOS) app.quit()
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
