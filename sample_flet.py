"""Flet port of the Electron settings window in this repository."""

from __future__ import annotations

import sys

import flet as ft


WINDOW_BACKGROUND = "#222529"
TEXT_COLOR = "#FFFFFF"
BORDER_COLOR = "#33FFFFFF"
TRACK_COLOR = "#1AFFFFFF"
DEFAULT_PRIMARY = "#e04d45"

LANGUAGE_ORDER = ("ko", "en", "ja", "zh-CN")
LANGUAGE_NAMES = {
    "ko": "한국어",
    "en": "English",
    "ja": "日本語",
    "zh-CN": "简体中文",
}

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
        "ok": "확인",
        "yes": "예",
        "no": "아니요",
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
        "ok": "OK",
        "yes": "Yes",
        "no": "No",
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
        "ok": "OK",
        "yes": "はい",
        "no": "いいえ",
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
        "ok": "确定",
        "yes": "是",
        "no": "否",
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


class SettingsWindow:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.language = "ko"
        self.primary = DEFAULT_PRIMARY
        self.labels: dict[str, ft.Text] = {}
        self.swatches: list[ft.Container] = []

        self._configure_window()
        self._build_controls()
        self.apply_language("ko", update=False)
        self.apply_primary(DEFAULT_PRIMARY, update=False)

        self.page.add(self._build_page())

    def _configure_window(self) -> None:
        self.page.title = TRANSLATIONS["ko"]["settingsTitle"]
        self.page.bgcolor = WINDOW_BACKGROUND
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            use_material3=True,
            color_scheme=ft.ColorScheme(
                primary=DEFAULT_PRIMARY,
                surface=WINDOW_BACKGROUND,
                on_surface=TEXT_COLOR,
                outline=BORDER_COLOR,
            ),
            scrollbar_theme=ft.ScrollbarTheme(
                thickness=10,
                radius=5,
                thumb_color=TRACK_COLOR,
                track_color=WINDOW_BACKGROUND,
            ),
            slider_theme=ft.SliderTheme(track_height=8, thumb_size=ft.Size(16, 16)),
        )

        self.page.window.width = 600
        self.page.window.height = 800
        self.page.window.min_width = 420
        self.page.window.min_height = 500
        self.page.window.bgcolor = WINDOW_BACKGROUND
        self.page.window.title_bar_hidden = True
        self.page.window.title_bar_buttons_hidden = False
        self.page.window.frameless = False
        self.page.window.alignment = ft.Alignment(0, 0)

        if sys.platform == "win32":
            self.page.window.icon = "logo.ico"

    def _build_controls(self) -> None:
        self.title = ft.Text(size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)

        self.theme_label = self._label("themeColor")
        self.language_label = self._label("language")
        self.volume_label = self._label("volume")
        self.path_label = self._label("savePath")

        for color, name_key in PALETTE:
            swatch = ft.Container(
                width=32,
                height=32,
                bgcolor=color,
                border_radius=16,
                border=ft.Border.all(3, ft.Colors.TRANSPARENT),
                data={"color": color, "name_key": name_key},
                tooltip="",
                animate_scale=150,
                on_click=self._select_color,
                on_hover=self._hover_swatch,
            )
            self.swatches.append(swatch)

        self.palette_row = ft.Row(
            controls=self.swatches,
            spacing=8,
            run_spacing=8,
            wrap=True,
        )

        self.language_dropdown = ft.Dropdown(
            value="ko",
            options=[
                ft.DropdownOption(key=code, text=name)
                for code, name in LANGUAGE_NAMES.items()
            ],
            height=40,
            expand=True,
            dense=True,
            text_size=16,
            color=TEXT_COLOR,
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.InputBorder.OUTLINE,
            border_color=BORDER_COLOR,
            focused_border_width=1,
            focused_border_color=DEFAULT_PRIMARY,
            border_radius=6,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            enable_search=False,
            menu_style=ft.MenuStyle(
                bgcolor=WINDOW_BACKGROUND,
                elevation=8,
                padding=ft.Padding.symmetric(vertical=4),
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
            on_select=self._change_language,
        )

        self.volume_slider = ft.Slider(
            min=0,
            max=100,
            value=75,
            active_color=DEFAULT_PRIMARY,
            inactive_color=TRACK_COLOR,
            thumb_color=DEFAULT_PRIMARY,
            overlay_color="#40e04d45",
            padding=ft.Padding.symmetric(horizontal=0, vertical=0),
            on_change=self._volume_changed,
        )

        self.path_field = ft.TextField(
            value="/Users/Downloads",
            expand=True,
            height=40,
            text_size=16,
            color=TEXT_COLOR,
            cursor_color=DEFAULT_PRIMARY,
            selection_color="#40e04d45",
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.InputBorder.OUTLINE,
            border_width=1,
            border_color=BORDER_COLOR,
            focused_border_width=1,
            focused_border_color=DEFAULT_PRIMARY,
            border_radius=ft.BorderRadius.only(
                top_left=4, top_right=0, bottom_left=4, bottom_right=0
            ),
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        )

        self.browse_button = self._outlined_button("browse", self._show_browse_message)
        self.browse_button.style.padding = ft.Padding.symmetric(horizontal=16, vertical=8)
        self.browse_button.style.shape = ft.RoundedRectangleBorder(
            radius=ft.BorderRadius.only(
                top_left=0, top_right=4, bottom_left=0, bottom_right=4
            )
        )

        self.save_button = ft.Button(
            content="",
            height=40,
            elevation=0,
            color=TEXT_COLOR,
            bgcolor=DEFAULT_PRIMARY,
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=24, vertical=8),
                shape=ft.RoundedRectangleBorder(radius=4),
                overlay_color="#18000000",
            ),
            on_click=self._show_saved_message,
        )
        self.labels["save"] = self.save_button

        self.cancel_button = self._outlined_button("cancel", self._confirm_close)
        self.cancel_button.style.padding = ft.Padding.symmetric(horizontal=24, vertical=8)

    def _build_page(self) -> ft.Column:
        title_bar = ft.WindowDragArea(
            ft.Container(height=32, bgcolor=WINDOW_BACKGROUND),
            maximizable=True,
        )

        form = ft.Column(
            controls=[
                ft.Container(self.title, margin=ft.Margin.only(bottom=16)),
                ft.Container(
                    ft.Column(
                        [self.theme_label, self.palette_row], spacing=8, tight=True
                    ),
                    margin=ft.Margin.only(bottom=16),
                ),
                ft.Container(
                    ft.Column(
                        [self.language_label, self.language_dropdown],
                        spacing=8,
                        tight=True,
                    ),
                    margin=ft.Margin.only(bottom=12),
                ),
                ft.Container(
                    ft.Column(
                        [self.volume_label, self.volume_slider], spacing=4, tight=True
                    ),
                    margin=ft.Margin.only(bottom=12),
                ),
                ft.Container(
                    ft.Column(
                        [
                            self.path_label,
                            ft.Row(
                                [self.path_field, self.browse_button],
                                spacing=0,
                                tight=True,
                            ),
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    margin=ft.Margin.only(bottom=16),
                ),
                ft.Row([self.save_button, self.cancel_button], spacing=8, tight=True),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            scroll=ft.ScrollMode.AUTO,
        )

        body = ft.Container(
            content=ft.Container(content=form, width=500),
            padding=ft.Padding(left=30, top=18, right=30, bottom=30),
            alignment=ft.Alignment(0, -1),
            expand=True,
            bgcolor=WINDOW_BACKGROUND,
        )
        return ft.Column([title_bar, body], spacing=0, expand=True)

    def _label(self, key: str) -> ft.Text:
        label = ft.Text(size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)
        self.labels[key] = label
        return label

    def _outlined_button(self, key: str, handler) -> ft.Button:
        button = ft.Button(
            content="",
            height=40,
            elevation=0,
            color=TEXT_COLOR,
            bgcolor=ft.Colors.TRANSPARENT,
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=4),
                overlay_color="#24FFFFFF",
            ),
            on_click=handler,
        )
        self.labels[key] = button
        return button

    def _change_language(self, event) -> None:
        if event.control.value in TRANSLATIONS:
            self.apply_language(event.control.value)

    def apply_language(self, language: str, *, update: bool = True) -> None:
        self.language = language
        messages = TRANSLATIONS[language]
        self.title.value = messages["settingsTitle"]
        self.page.title = messages["settingsTitle"]

        for key, control in self.labels.items():
            if isinstance(control, ft.Text):
                control.value = messages[key]
            else:
                control.content = messages[key]

        for swatch in self.swatches:
            swatch.tooltip = messages[swatch.data["name_key"]]

        if update:
            self.page.update()

    def _select_color(self, event) -> None:
        self.apply_primary(event.control.data["color"])

    def apply_primary(self, color: str, *, update: bool = True) -> None:
        self.primary = color
        self.page.theme.color_scheme.primary = color

        for swatch in self.swatches:
            is_active = swatch.data["color"].lower() == color.lower()
            swatch.border = ft.Border.all(
                3, TEXT_COLOR if is_active else ft.Colors.TRANSPARENT
            )
            swatch.shadow = (
                ft.BoxShadow(
                    spread_radius=2,
                    blur_radius=0,
                    color=color,
                    offset=ft.Offset(0, 0),
                )
                if is_active
                else None
            )
            swatch.scale = 1.1 if is_active else 1.0

        self.language_dropdown.focused_border_color = color
        self.volume_slider.active_color = color
        self.volume_slider.thumb_color = color
        self.volume_slider.overlay_color = self._with_alpha(color, "40")
        self.path_field.cursor_color = color
        self.path_field.focused_border_color = color
        self.path_field.selection_color = self._with_alpha(color, "40")
        self.save_button.bgcolor = color

        hover_background = {
            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            ft.ControlState.HOVERED: color,
        }
        self.browse_button.style.bgcolor = hover_background
        self.cancel_button.style.bgcolor = hover_background

        if update:
            self.page.update()

    def _hover_swatch(self, event) -> None:
        hovered = event.data is True or str(event.data).lower() == "true"
        active = event.control.data["color"].lower() == self.primary.lower()
        event.control.scale = 1.15 if hovered else (1.1 if active else 1.0)
        event.control.update()

    @staticmethod
    def _with_alpha(color: str, alpha: str) -> str:
        return f"#{alpha}{color.removeprefix('#')}"

    def _volume_changed(self, _event) -> None:
        # preload.js의 setVolume()도 현재 빈 구현이므로 UI 값만 유지한다.
        pass

    def _alert(self, message: str) -> None:
        messages = TRANSLATIONS[self.language]
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(messages["settingsTitle"]),
            content=ft.Text(message),
            bgcolor=WINDOW_BACKGROUND,
            actions=[
                ft.TextButton(
                    messages["ok"],
                    style=ft.ButtonStyle(color=self.primary),
                    on_click=lambda _e: self.page.pop_dialog(),
                )
            ],
        )
        self.page.show_dialog(dialog)

    def _show_saved_message(self, _event) -> None:
        self._alert(TRANSLATIONS[self.language]["savedMessage"])

    def _show_browse_message(self, _event) -> None:
        self._alert(TRANSLATIONS[self.language]["browseMessage"])

    def _confirm_close(self, _event) -> None:
        messages = TRANSLATIONS[self.language]

        def close_window(_event) -> None:
            self.page.pop_dialog()
            self.page.window.close()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(messages["settingsTitle"]),
            content=ft.Text(messages["closeConfirm"]),
            bgcolor=WINDOW_BACKGROUND,
            actions=[
                ft.TextButton(
                    messages["no"],
                    style=ft.ButtonStyle(color=TEXT_COLOR),
                    on_click=lambda _e: self.page.pop_dialog(),
                ),
                ft.TextButton(
                    messages["yes"],
                    style=ft.ButtonStyle(color=self.primary),
                    on_click=close_window,
                ),
            ],
        )
        self.page.show_dialog(dialog)


def main(page: ft.Page) -> None:
    SettingsWindow(page)


if __name__ == "__main__":
    ft.run(main, assets_dir=".")
