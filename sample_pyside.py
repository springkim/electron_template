"""PySide6 port of the Electron settings window in this repository."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


WINDOW_BACKGROUND = "#222529"
TEXT_COLOR = "#ffffff"
BORDER_COLOR = "rgba(255, 255, 255, 51)"
TRACK_COLOR = "rgba(255, 255, 255, 26)"
DEFAULT_PRIMARY = "#e04d45"

LANGUAGE_ORDER = ("ko", "en", "ja", "zh-CN")
LANGUAGE_NAMES = ("한국어", "English", "日本語", "简体中文")

TRANSLATIONS = {
    "ko": {
        "settingsTitle": "설정",
        "themeColor": "테마 색상",
        "language": "언어",
        "volume": "볼륨",
        "savePath": "저장 경로",
        "browse": "열기",
        "save": "저장",
        "cancel": "취소",
        "red": "빨강",
        "orange": "주황",
        "yellow": "노랑",
        "green": "초록",
        "mint": "민트",
        "teal": "청록",
        "cyan": "시안",
        "blue": "파랑",
        "indigo": "남색",
        "purple": "보라",
        "savedMessage": "설정이 저장되었습니다.",
        "closeConfirm": "설정창을 닫으시겠습니까?",
        "browseMessage": "폴더 선택 창이 열립니다. (실제 구현은 메인 프로세스 통신 필요)",
    },
    "en": {
        "settingsTitle": "Settings",
        "themeColor": "Theme color",
        "language": "Language",
        "volume": "Volume",
        "savePath": "Save path",
        "browse": "Browse",
        "save": "Save",
        "cancel": "Cancel",
        "red": "Red",
        "orange": "Orange",
        "yellow": "Yellow",
        "green": "Green",
        "mint": "Mint",
        "teal": "Teal",
        "cyan": "Cyan",
        "blue": "Blue",
        "indigo": "Indigo",
        "purple": "Purple",
        "savedMessage": "Settings have been saved.",
        "closeConfirm": "Do you want to close the settings window?",
        "browseMessage": "The folder picker will open. (Main process communication is required for the actual implementation.)",
    },
    "ja": {
        "settingsTitle": "設定",
        "themeColor": "テーマカラー",
        "language": "言語",
        "volume": "音量",
        "savePath": "保存先",
        "browse": "開く",
        "save": "保存",
        "cancel": "キャンセル",
        "red": "赤",
        "orange": "オレンジ",
        "yellow": "黄",
        "green": "緑",
        "mint": "ミント",
        "teal": "青緑",
        "cyan": "シアン",
        "blue": "青",
        "indigo": "藍色",
        "purple": "紫",
        "savedMessage": "設定を保存しました。",
        "closeConfirm": "設定ウィンドウを閉じますか？",
        "browseMessage": "フォルダー選択画面を開きます。（実装にはメインプロセスとの通信が必要です）",
    },
    "zh-CN": {
        "settingsTitle": "设置",
        "themeColor": "主题颜色",
        "language": "语言",
        "volume": "音量",
        "savePath": "保存路径",
        "browse": "打开",
        "save": "保存",
        "cancel": "取消",
        "red": "红色",
        "orange": "橙色",
        "yellow": "黄色",
        "green": "绿色",
        "mint": "薄荷色",
        "teal": "青绿色",
        "cyan": "青色",
        "blue": "蓝色",
        "indigo": "靛蓝色",
        "purple": "紫色",
        "savedMessage": "设置已保存。",
        "closeConfirm": "是否关闭设置窗口？",
        "browseMessage": "将打开文件夹选择窗口。（实际实现需要与主进程通信）",
    },
}

PALETTE = (
    ("#e04d45", "red"),
    ("#e79243", "orange"),
    ("#f1cd47", "yellow"),
    ("#71c367", "green"),
    ("#6dc4b3", "mint"),
    ("#6cc0cd", "teal"),
    ("#6cbde3", "cyan"),
    ("#5388f6", "blue"),
    ("#665aec", "indigo"),
    ("#b544d8", "purple"),
)


def pixel_font(size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    font = QApplication.font()
    font.setPixelSize(size)
    font.setWeight(weight)
    return font


class ColorSwatch(QWidget):
    clicked = Signal(str)

    def __init__(self, color: str, name_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.color = color
        self.name_key = name_key
        self.primary = DEFAULT_PRIMARY
        self.active = color.lower() == DEFAULT_PRIMARY.lower()
        self.hovered = False
        self.setFixedSize(38, 38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def set_active(self, active: bool, primary: str) -> None:
        self.active = active
        self.primary = primary
        self.update()

    def enterEvent(self, event: QEvent) -> None:  # noqa: N802
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self.hovered = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit(self.color)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QEvent) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scale = 1.15 if self.hovered else (1.10 if self.active else 1.0)
        diameter = 32.0 * scale
        center = self.rect().center()
        circle = QRectF(
            center.x() - diameter / 2,
            center.y() - diameter / 2,
            diameter,
            diameter,
        )

        if self.active:
            ring = circle.adjusted(-2, -2, 2, 2)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.primary))
            painter.drawEllipse(ring)
            painter.setPen(QPen(QColor(TEXT_COLOR), 3))
        else:
            painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor(self.color))
        painter.drawEllipse(circle)


class TitleBar(QWidget):
    def __init__(self, window: "SettingsWindow") -> None:
        super().__init__(window)
        self.window = window
        self.setObjectName("titleBar")
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)

        self.minimize_button = self._window_button("minimizeButton", "―")
        self.maximize_button = self._window_button("maximizeButton", "□")
        self.close_button = self._window_button("closeButton", "×")
        self.minimize_button.clicked.connect(window.showMinimized)
        self.maximize_button.clicked.connect(window.toggle_maximized)
        self.close_button.clicked.connect(window.close)

        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

    @staticmethod
    def _window_button(name: str, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(name)
        button.setFixedSize(46, 32)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return button

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and sys.platform != "win32":
            handle = self.window.windowHandle()
            if handle is not None:
                handle.startSystemMove()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.window.toggle_maximized()
        super().mouseDoubleClickEvent(event)


class SettingsWindow(QMainWindow):
    RESIZE_BORDER = 6

    def __init__(self) -> None:
        super().__init__()
        self.language = "ko"
        self.primary = DEFAULT_PRIMARY
        self.labels: dict[str, QLabel | QPushButton] = {}
        self.swatches: list[ColorSwatch] = []

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.resize(600, 800)
        self.setMinimumSize(420, 500)

        icon_path = Path(__file__).with_name("logo.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._build_ui()
        self.apply_language("ko")
        self.apply_primary(DEFAULT_PRIMARY)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def _build_ui(self) -> None:
        self.root_frame = QFrame()
        self.root_frame.setObjectName("rootFrame")
        self.setCentralWidget(self.root_frame)

        root_layout = QVBoxLayout(self.root_frame)
        root_layout.setContentsMargins(1, 1, 1, 1)
        root_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        body = QWidget()
        body.setObjectName("windowBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(30, 18, 30, 30)
        body_layout.setSpacing(0)

        center_row = QHBoxLayout()
        center_row.setContentsMargins(0, 0, 0, 0)
        center_row.setSpacing(0)
        center_row.addStretch(1)

        form = QWidget()
        form.setObjectName("form")
        form.setMaximumWidth(500)
        form.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)

        self.title_label = QLabel()
        self.title_label.setObjectName("settingsTitle")
        self.title_label.setFont(pixel_font(20, QFont.Weight.Bold))
        form_layout.addWidget(self.title_label)
        form_layout.addSpacing(16)

        self.theme_label = self._make_label("themeColor")
        form_layout.addWidget(self.theme_label)
        form_layout.addSpacing(8)

        palette_widget = QWidget()
        palette_layout = QHBoxLayout(palette_widget)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setSpacing(2)
        for color, name_key in PALETTE:
            swatch = ColorSwatch(color, name_key)
            swatch.clicked.connect(self.apply_primary)
            self.swatches.append(swatch)
            palette_layout.addWidget(swatch)
        palette_layout.addStretch(1)
        form_layout.addWidget(palette_widget)
        form_layout.addSpacing(13)

        self.language_label = self._make_label("language")
        form_layout.addWidget(self.language_label)
        form_layout.addSpacing(8)

        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        self.language_combo.setFont(pixel_font(16))
        self.language_combo.addItems(LANGUAGE_NAMES)
        self.language_combo.setFixedHeight(38)
        self.language_combo.currentIndexChanged.connect(self._language_index_changed)
        form_layout.addWidget(self.language_combo)
        form_layout.addSpacing(12)

        self.volume_label = self._make_label("volume")
        form_layout.addWidget(self.volume_label)
        form_layout.addSpacing(5)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setFixedHeight(24)
        self.volume_slider.valueChanged.connect(self._volume_changed)
        form_layout.addWidget(self.volume_slider)
        form_layout.addSpacing(12)

        self.path_label = self._make_label("savePath")
        form_layout.addWidget(self.path_label)
        form_layout.addSpacing(8)

        path_row = QHBoxLayout()
        path_row.setContentsMargins(0, 0, 0, 0)
        path_row.setSpacing(0)

        self.path_edit = QLineEdit("/Users/Downloads")
        self.path_edit.setObjectName("pathEdit")
        self.path_edit.setFont(pixel_font(16))
        self.path_edit.setFixedHeight(40)

        self.browse_button = QPushButton()
        self.browse_button.setObjectName("browseButton")
        self.browse_button.setFont(pixel_font(16))
        self.browse_button.setFixedHeight(40)
        self.browse_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.browse_button.clicked.connect(self.show_browse_message)
        self.labels["browse"] = self.browse_button

        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(self.browse_button)
        form_layout.addLayout(path_row)
        form_layout.addSpacing(16)

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(8)

        self.save_button = QPushButton()
        self.save_button.setObjectName("saveButton")
        self.save_button.setFont(pixel_font(16))
        self.save_button.setFixedHeight(40)
        self.save_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.save_button.clicked.connect(self.show_saved_message)
        self.labels["save"] = self.save_button

        self.cancel_button = QPushButton()
        self.cancel_button.setObjectName("outlineButton")
        self.cancel_button.setFont(pixel_font(16))
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.cancel_button.clicked.connect(self.confirm_close)
        self.labels["cancel"] = self.cancel_button

        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)
        buttons.addStretch(1)
        form_layout.addLayout(buttons)
        form_layout.addStretch(1)

        center_row.addWidget(form, 100)
        center_row.addStretch(1)
        body_layout.addLayout(center_row, 1)
        root_layout.addWidget(body, 1)

    def _make_label(self, key: str) -> QLabel:
        label = QLabel()
        label.setFont(pixel_font(14, QFont.Weight.Medium))
        self.labels[key] = label
        return label

    def _language_index_changed(self, index: int) -> None:
        if 0 <= index < len(LANGUAGE_ORDER):
            self.apply_language(LANGUAGE_ORDER[index])

    def apply_language(self, language: str) -> None:
        messages = TRANSLATIONS.get(language)
        if messages is None:
            return

        self.language = language
        self.setWindowTitle(messages["settingsTitle"])
        self.title_label.setText(messages["settingsTitle"])
        for key, control in self.labels.items():
            control.setText(messages[key])
        for swatch in self.swatches:
            swatch.setToolTip(messages[swatch.name_key])

        self._refresh_button_widths()

    def _refresh_button_widths(self) -> None:
        self.browse_button.adjustSize()
        self.save_button.adjustSize()
        self.cancel_button.adjustSize()
        self.browse_button.setMinimumWidth(self.browse_button.sizeHint().width())
        self.save_button.setMinimumWidth(self.save_button.sizeHint().width())
        self.cancel_button.setMinimumWidth(self.cancel_button.sizeHint().width())

    def apply_primary(self, color: str) -> None:
        self.primary = color
        for swatch in self.swatches:
            swatch.set_active(swatch.color.lower() == color.lower(), color)
        self.setStyleSheet(self._stylesheet(color))
        self._set_native_border_color(color)

    def _stylesheet(self, primary: str) -> str:
        return f"""
            QMainWindow, QWidget#windowBody, QWidget#form, QFrame#rootFrame {{
                background-color: {WINDOW_BACKGROUND};
                color: {TEXT_COLOR};
            }}
            QFrame#rootFrame {{
                border: 1px solid {primary};
            }}
            QWidget#titleBar {{
                background-color: {WINDOW_BACKGROUND};
                border: none;
            }}
            QLabel {{
                background: transparent;
                color: {TEXT_COLOR};
                border: none;
            }}
            QToolTip {{
                color: {TEXT_COLOR};
                background-color: {WINDOW_BACKGROUND};
                border: 1px solid {BORDER_COLOR};
                padding: 4px;
            }}
            QPushButton#minimizeButton,
            QPushButton#maximizeButton,
            QPushButton#closeButton {{
                color: {TEXT_COLOR};
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0;
                font-size: 16px;
                font-weight: 400;
            }}
            QPushButton#minimizeButton:hover,
            QPushButton#maximizeButton:hover {{
                background-color: rgba(255, 255, 255, 18);
            }}
            QPushButton#closeButton:hover {{
                background-color: #c42b1c;
            }}
            QComboBox#languageCombo {{
                color: {TEXT_COLOR};
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 36px 6px 12px;
            }}
            QComboBox#languageCombo:hover,
            QComboBox#languageCombo:focus {{
                border-color: {primary};
            }}
            QComboBox#languageCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border: none;
            }}
            QComboBox#languageCombo QAbstractItemView {{
                color: {TEXT_COLOR};
                background-color: {WINDOW_BACKGROUND};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                outline: none;
                padding: 4px 0;
                selection-color: {TEXT_COLOR};
                selection-background-color: {primary};
            }}
            QComboBox#languageCombo QAbstractItemView::item {{
                min-height: 30px;
                padding-left: 12px;
            }}
            QSlider#volumeSlider::groove:horizontal {{
                height: 8px;
                background-color: {TRACK_COLOR};
                border-radius: 4px;
            }}
            QSlider#volumeSlider::sub-page:horizontal,
            QSlider#volumeSlider::add-page:horizontal {{
                background-color: {TRACK_COLOR};
                border-radius: 4px;
            }}
            QSlider#volumeSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -4px 0;
                background-color: {primary};
                border: none;
                border-radius: 8px;
            }}
            QLineEdit#pathEdit {{
                color: {TEXT_COLOR};
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                padding: 8px 12px;
                selection-background-color: {primary};
            }}
            QLineEdit#pathEdit:focus {{
                border-color: {primary};
            }}
            QPushButton#browseButton {{
                color: {TEXT_COLOR};
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton#browseButton:hover {{
                background-color: {primary};
            }}
            QPushButton#saveButton {{
                color: {TEXT_COLOR};
                background-color: {primary};
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
            }}
            QPushButton#saveButton:hover {{
                background-color: {self._darken(primary, 0.90)};
            }}
            QPushButton#outlineButton {{
                color: {TEXT_COLOR};
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 8px 24px;
            }}
            QPushButton#outlineButton:hover {{
                background-color: {primary};
            }}
            QMessageBox {{
                background-color: {WINDOW_BACKGROUND};
            }}
            QMessageBox QLabel {{
                color: {TEXT_COLOR};
                min-width: 240px;
            }}
            QMessageBox QPushButton {{
                color: {TEXT_COLOR};
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                min-width: 64px;
                min-height: 30px;
                padding: 4px 12px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {primary};
            }}
        """

    @staticmethod
    def _darken(color: str, factor: float) -> str:
        value = color.lstrip("#")
        rgb = [int(value[index : index + 2], 16) for index in (0, 2, 4)]
        return "#{:02x}{:02x}{:02x}".format(*(round(channel * factor) for channel in rgb))

    def _volume_changed(self, _value: int) -> None:
        # preload.js의 setVolume()도 빈 구현이므로 UI 값만 유지한다.
        pass

    def show_saved_message(self) -> None:
        messages = TRANSLATIONS[self.language]
        QMessageBox.information(self, messages["settingsTitle"], messages["savedMessage"])

    def show_browse_message(self) -> None:
        messages = TRANSLATIONS[self.language]
        QMessageBox.information(self, messages["settingsTitle"], messages["browseMessage"])

    def confirm_close(self) -> None:
        messages = TRANSLATIONS[self.language]
        result = QMessageBox.question(
            self,
            messages["settingsTitle"],
            messages["closeConfirm"],
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.close()

    def toggle_maximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self._sync_window_state()

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._sync_window_state()

    def _sync_window_state(self) -> None:
        self.title_bar.maximize_button.setText("❐" if self.isMaximized() else "□")
        margins = 0 if self.isMaximized() else 1
        self.centralWidget().layout().setContentsMargins(margins, margins, margins, margins)

    def showEvent(self, event: QEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._set_native_border_color(self.primary)

    def _set_native_border_color(self, color: str) -> None:
        if sys.platform != "win32" or not self.winId():
            return
        try:
            value = color.lstrip("#")
            red, green, blue = (int(value[index : index + 2], 16) for index in (0, 2, 4))
            color_ref = ctypes.c_int(red | (green << 8) | (blue << 16))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(int(self.winId())),
                ctypes.c_uint(34),
                ctypes.byref(color_ref),
                ctypes.sizeof(color_ref),
            )
        except (AttributeError, OSError):
            pass

    def nativeEvent(self, event_type, message):  # noqa: N802
        if sys.platform == "win32":
            import ctypes.wintypes

            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == 0x0084:  # WM_NCHITTEST
                point = self.mapFromGlobal(QCursor.pos())
                x, y = point.x(), point.y()
                width, height = self.width(), self.height()
                border = self.RESIZE_BORDER

                if not self.isMaximized():
                    left, right = x < border, x >= width - border
                    top, bottom = y < border, y >= height - border
                    if top and left:
                        return True, 13  # HTTOPLEFT
                    if top and right:
                        return True, 14  # HTTOPRIGHT
                    if bottom and left:
                        return True, 16  # HTBOTTOMLEFT
                    if bottom and right:
                        return True, 17  # HTBOTTOMRIGHT
                    if left:
                        return True, 10  # HTLEFT
                    if right:
                        return True, 11  # HTRIGHT
                    if top:
                        return True, 12  # HTTOP
                    if bottom:
                        return True, 15  # HTBOTTOM

                if 0 <= y < 32 and x < width - 138:
                    return True, 2  # HTCAPTION
        return super().nativeEvent(event_type, message)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("설정")
    app.setStyle("Fusion")
    app.setFont(pixel_font(16))

    window = SettingsWindow()
    available = window.screen().availableGeometry()
    window.move(
        available.x() + (available.width() - window.width()) // 2,
        available.y() + (available.height() - window.height()) // 2,
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
