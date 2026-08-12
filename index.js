const {app, BrowserWindow, Menu, nativeTheme, ipcMain, dialog} = require('electron')
const path = require('path')

const is_windows = process.platform === 'win32'
const is_macOS = process.platform === 'darwin'
const is_linux = process.platform === 'linux'
const app_icon_path = path.join(
    __dirname,
    is_windows ? 'logo.ico' : is_macOS ? 'logo.icns' : 'logo.png'
)
// nativeImage(dock.setIcon 등)는 PNG/JPEG만 읽을 수 있으므로 런타임 아이콘은 PNG를 쓴다.
// .icns/.ico는 패키징용으로만 유지한다.
const runtime_icon_path = path.join(__dirname, 'logo.png')

if (is_linux) {
    app.disableHardwareAcceleration()
}

// ======================== 상수
let primary_color = '#e04d45'
// input.css의 --app-bg / --app-fg와 값을 맞춰야 창 배경과 본문 색이 어긋나지 않는다.
const dark_background_color = '#222529'
const light_background_color = '#F5F6F7'

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
    dark: {color: dark_background_color, symbolColor: '#FFFFFF'},
    light: {color: light_background_color, symbolColor: '#1F2225'}
}

function getTheme() {
    const theme = nativeTheme.shouldUseDarkColors ? themes.dark : themes.light
    return {...theme, border: primary_color}
}

ipcMain.on('set-color', (event, r, g, b) => {
    const rgb = [r, g, b]
    if (!rgb.every(value => Number.isInteger(value) && value >= 0 && value <= 255)) return

    primary_color = `#${rgb.map(value => value.toString(16).padStart(2, '0')).join('')}`

    if (is_windows) {
        const win = BrowserWindow.fromWebContents(event.sender)
        if (win && !win.isDestroyed()) {
            setWindowBorderColor?.(win, primary_color)
        }
    }
})
const titles = ['설정', 'Settings', '設定', '设置']

ipcMain.on('set-language', (event, languageIndex) => {
    if (!Number.isInteger(languageIndex) || !titles[languageIndex]) return

    const win = BrowserWindow.fromWebContents(event.sender)
    if (win && !win.isDestroyed()) {
        win.setTitle(titles[languageIndex])
    }
})

// themeSource를 바꾸면 네이티브 창 배경, 네이티브 다이얼로그, 그리고 렌더러의
// prefers-color-scheme까지 한 번에 따라온다. 'system'이면 다시 OS 설정을 따른다.
const theme_sources = ['light', 'dark', 'system']

ipcMain.on('set-theme', (event, mode) => {
    if (!theme_sources.includes(mode)) return

    nativeTheme.themeSource = mode
})

ipcMain.handle('get-home-directory', () => app.getPath('home'))

ipcMain.handle('select-directory', async (event, currentPath, title) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    const options = {
        title: typeof title === 'string' ? title : undefined,
        defaultPath: typeof currentPath === 'string' && currentPath.trim()
            ? currentPath
            : app.getPath('home'),
        properties: ['openDirectory', 'createDirectory']
    }
    const result = win && !win.isDestroyed()
        ? await dialog.showOpenDialog(win, options)
        : await dialog.showOpenDialog(options)

    return result.canceled ? null : result.filePaths[0]
})

// ======================== 창 생성
function createWindow() {
    const theme = getTheme()

    const win = new BrowserWindow({
        width: 600,
        height: 800,
        minWidth: 500,
        minHeight: 600,
        title: '설정',
        icon: app_icon_path,
        backgroundColor: theme.color,
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
    // OS 테마가 바뀌면 네이티브 창 배경도 따라 바꾼다. 본문은 CSS의
    // prefers-color-scheme이 알아서 전환한다.
    nativeTheme.on('updated', () => {
        if (win.isDestroyed()) return

        const t = getTheme()
        win.setBackgroundColor(t.color)

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

    if (is_macOS) {
        try {
            app.dock.setIcon(runtime_icon_path)
        } catch (e) {
            console.warn('Failed to set the dock icon:', e.message)
        }
    }

    createWindow()
})

// 단일 창 앱이므로 창을 닫으면 macOS에서도 프로세스를 완전히 종료한다.
app.on('window-all-closed', () => {
    app.quit()
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
