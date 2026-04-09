"""RainDrop — 채움으로 삶의 밀도를 기록한다.
Python + Flet 기반 크로스플랫폼 집중 타이머 앱.
"""

import flet as ft
from features.timer.timer_screen import TimerScreen
from core.services.timer_service import TimerService
from core.storage.json_store import JsonStore


def main(page: ft.Page):
    # Window setup
    page.title = "RainDrop"
    page.window.width = 1040
    page.window.height = 700
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Theme
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
    )

    # Services
    store = JsonStore()
    timer_service = TimerService()

    # Main screen
    timer_screen = TimerScreen(page=page, timer_service=timer_service, store=store)
    page.add(timer_screen)


ft.app(target=main)
