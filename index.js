const {app, BrowserWindow, nativeTheme, ipcMain} = require('electron')
const path = require('path')

const is_windows = process.platform === 'win32'
const is_macOS   = process.platform === 'darwin'
const is_linux   = process.platform === 'linux'

if (is_linux) {
    app.disableHardwareAcceleration()
}

// ======================== 상수
const primary_color = '#e04d45'

// ======================== WINDOWS NATIVE
let setWindowBorderColor = null

if (is_windows) {
    const koffi = require('koffi')

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

// ======================== 테마
const themes = {
    dark:  {color: '#222529', symbolColor: '#FFFFFF', border: primary_color},
    light: {color: '#ffffff', symbolColor: '#333333', border: primary_color}
}

function getTheme() {
    return nativeTheme.shouldUseDarkColors ? themes.dark : themes.light
}

// ======================== 창 생성
function createWindow() {
    const theme = getTheme()

    const win = new BrowserWindow({
        width: 480,
        height: 800,
        minWidth: 480,
        minHeight: 600,
        title: '설정',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        },
        autoHideMenuBar: true,
        menuBarVisible: false,
        // Windows: 네이티브 타이틀바 숨김, Linux: 완전히 프레임리스
        ...(is_windows ? {
            titleBarStyle: 'hidden',
            titleBarOverlay: {
                color: theme.color,
                symbolColor: theme.symbolColor,
                height: 32
            }
        } : {
            transparent: true,
            frame: false
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
    win.on('close', () => {
        app.quit()
    })

    // Linux/macOS 프레임리스 창용 커스텀 윈도우 컨트롤 IPC
    // Windows는 titleBarOverlay가 네이티브 버튼을 제공하므로 불필요
    if (!is_windows) {
        ipcMain.on('window-minimize', (event) => {
            BrowserWindow.fromWebContents(event.sender)?.minimize()
        })
        ipcMain.on('window-maximize', (event) => {
            const w = BrowserWindow.fromWebContents(event.sender)
            if (!w) return
            w.isMaximized() ? w.unmaximize() : w.maximize()
        })
        ipcMain.on('window-close', (event) => {
            BrowserWindow.fromWebContents(event.sender)?.close()
        })
    }

    nativeTheme.on('updated', () => {
        console.log('[nativeTheme] updated, isDark:', nativeTheme.shouldUseDarkColors)
        const t = getTheme()
        if (is_windows) {
            win.setTitleBarOverlay({color: t.color, symbolColor: t.symbolColor, height: 32})
        }
        setWindowBorderColor?.(win, t.border)
    })

    win.show()
}

// ======================== 앱 생명주기
app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
    if (!is_windows) app.quit()
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
})