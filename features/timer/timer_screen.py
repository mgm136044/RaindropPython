"""메인 타이머 화면 — 양동이 중심 레이아웃."""

import math
import random
import threading
import flet as ft
from flet import canvas as cv

from core.services.timer_service import TimerService
from core.storage.json_store import JsonStore


class TimerScreen(ft.Container):
    def __init__(self, page: ft.Page, timer_service: TimerService, store: JsonStore):
        super().__init__(expand=True)
        self.page = page
        self.timer_service = timer_service
        self.store = store

        # State
        self._elapsed = 0
        self._goal_seconds = 25 * 60
        self._progress = 0.0
        self._is_running = False
        self._wave_offset = 0.0
        self._wobble_angle = 0.0
        self._today_total = 0

        # Messages
        self._running_msgs = [
            "물방울이 떨어지는 중",
            "좋아요, 집중하고 있어요!",
            "지금 이 순간에 몰입하세요",
            "양동이가 차오르고 있어요",
            "한 방울 한 방울 쌓이는 중",
            "멋져요, 계속 이대로!",
            "집중의 흐름을 유지하세요",
            "당신의 노력이 물이 됩니다",
        ]
        self._idle_msgs = [
            "숨 고르고 다시 시작",
            "준비되면 집중을 시작하세요",
            "오늘도 양동이를 채워볼까요?",
            "한 방울의 시작이 큰 변화를 만들어요",
        ]
        self._current_msg = random.choice(self._idle_msgs)

        # Wave animation timer
        self._wave_timer = None
        self._start_wave_animation()

        # Build UI
        self._build_ui()

    def _format_time(self, seconds: int) -> str:
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _build_ui(self):
        # Timer text
        self._timer_text = ft.Text(
            self._format_time(0),
            size=44,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
        )

        # Info text
        self._info_text = ft.Text(
            f"{self._goal_seconds // 60}분 집중 시 양동이 가득 · 오늘 {self._format_time(self._today_total)}",
            size=11,
            color=ft.Colors.with_opacity(0.35, ft.Colors.WHITE),
        )

        # Motivation
        self._motivation_text = ft.Text(
            self._current_msg,
            size=16,
            color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
        )

        # Bucket canvas
        self._bucket_canvas = cv.Canvas(
            [cv.Circle(0, 0, 0)],  # placeholder
            width=340,
            height=320,
            on_resize=self._draw_bucket,
        )

        # Buttons
        self._start_btn = ft.ElevatedButton(
            "집중 시작",
            on_click=self._on_start,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
            width=160,
            height=48,
        )
        self._pause_btn = ft.ElevatedButton(
            "일시정지",
            on_click=self._on_pause,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
            visible=False,
            width=130,
            height=48,
        )
        self._stop_btn = ft.ElevatedButton(
            "집중 종료",
            on_click=self._on_stop,
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
            visible=False,
            width=130,
            height=48,
        )

        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Text("RainDrop", size=22, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                            ft.Text("v2.3.1", size=11, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                        ],
                        spacing=6,
                    ),
                    ft.Row(
                        [
                            ft.Text("🪣 0", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
            blur=ft.Blur(20, 20),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
        )

        # Timer capsule
        timer_capsule = ft.Container(
            content=ft.Column(
                [self._timer_text, self._info_text],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=10),
            blur=ft.Blur(20, 20),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border_radius=999,
        )

        # Controls row
        controls = ft.Row(
            [self._start_btn, self._pause_btn, self._stop_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        )

        # Stack layout
        self.content = ft.Stack(
            [
                # Background
                ft.Container(bgcolor=ft.Colors.BLACK, expand=True),

                # Bucket (centered)
                ft.Container(
                    content=ft.GestureDetector(
                        content=self._bucket_canvas,
                        on_tap=self._on_bucket_tap,
                    ),
                    alignment=ft.alignment.center,
                ),

                # Header (top)
                ft.Container(content=header, alignment=ft.alignment.top_center),

                # Motivation (below header)
                ft.Container(
                    content=self._motivation_text,
                    alignment=ft.alignment.top_center,
                    margin=ft.margin.only(top=80),
                ),

                # Timer + Controls (bottom)
                ft.Container(
                    content=ft.Column(
                        [timer_capsule, ft.Container(height=20), controls],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.bottom_center,
                    margin=ft.margin.only(bottom=24),
                ),
            ],
            expand=True,
        )

    def _draw_bucket(self, e: cv.CanvasResizeEvent):
        """양동이 + 물을 Canvas에 그린다."""
        w, h = e.width, e.height
        shapes = []

        # Bucket dimensions
        top_y = h * 0.06
        top_inset = w * 0.14
        bottom_inset = w * 0.08

        # Water level
        water_top = h - (h * 0.80 * self._progress)

        # Water fill (simplified rectangle with wave)
        if self._progress > 0.02:
            water_shapes = []
            # Wave surface points
            points = []
            for x_i in range(0, int(w) + 1, 3):
                x = float(x_i)
                wave1 = math.sin((x / (w / 1.5) + self._wave_offset) * 2 * math.pi) * 4
                wave2 = math.sin((x / (w / 3) + self._wave_offset * 1.3) * 2 * math.pi) * 2
                # Tilt slosh
                norm_x = (x / w) - 0.5
                slope = max(-1, min(1, -self._wobble_angle / 8))
                slosh = norm_x * slope * h * 0.06 * 2
                y = water_top + wave1 + wave2 + slosh
                points.append(ft.Offset(x, y))

            # Build water path
            path_data = f"M 0 {water_top}"
            for p in points:
                path_data += f" L {p.x} {p.y}"
            path_data += f" L {w} {h} L 0 {h} Z"

            shapes.append(
                cv.Path(
                    [cv.Path.MoveTo(0, water_top)]
                    + [cv.Path.LineTo(p.x, p.y) for p in points]
                    + [cv.Path.LineTo(w, h), cv.Path.LineTo(0, h), cv.Path.Close()],
                    paint=ft.Paint(
                        gradient=ft.PaintLinearGradient(
                            (w / 2, water_top),
                            (w / 2, h),
                            colors=[
                                ft.Colors.with_opacity(0.8, ft.Colors.BLUE_300),
                                ft.Colors.with_opacity(0.9, ft.Colors.BLUE_800),
                            ],
                        ),
                    ),
                )
            )

        # Bucket outline
        shapes.append(
            cv.Path(
                [
                    cv.Path.MoveTo(top_inset, top_y),
                    cv.Path.LineTo(w - top_inset, top_y),
                    cv.Path.LineTo(w - bottom_inset, h),
                    cv.Path.LineTo(bottom_inset, h),
                    cv.Path.Close(),
                ],
                paint=ft.Paint(
                    stroke_width=4,
                    style=ft.PaintingStyle.STROKE,
                    color=ft.Colors.BLUE_GREY_300,
                ),
            )
        )

        # Rim
        shapes.append(
            cv.Path(
                [
                    cv.Path.MoveTo(top_inset - 6, top_y),
                    cv.Path.LineTo(w - top_inset + 6, top_y),
                ],
                paint=ft.Paint(
                    stroke_width=6,
                    style=ft.PaintingStyle.STROKE,
                    color=ft.Colors.BLUE_GREY_300,
                    stroke_cap=ft.StrokeCap.ROUND,
                ),
            )
        )

        # Metal bands
        for frac in [0.30, 0.70]:
            y = top_y + (h - top_y) * frac
            x_inset = top_inset + (bottom_inset - top_inset) * frac + w * 0.02
            shapes.append(
                cv.Path(
                    [
                        cv.Path.MoveTo(x_inset, y),
                        cv.Path.LineTo(w - x_inset, y),
                    ],
                    paint=ft.Paint(
                        stroke_width=2,
                        style=ft.PaintingStyle.STROKE,
                        color=ft.Colors.BLUE_GREY_400,
                    ),
                )
            )

        # Handle arc
        cx, cy = w / 2, top_y
        r = w * 0.26
        arc_points = []
        for deg in range(195, 345, 5):
            rad = math.radians(deg)
            ax = cx + r * math.cos(rad)
            ay = cy - h * 0.15 + r * math.sin(rad)
            arc_points.append((ax, ay))

        if arc_points:
            handle_path = [cv.Path.MoveTo(arc_points[0][0], arc_points[0][1])]
            for ax, ay in arc_points[1:]:
                handle_path.append(cv.Path.LineTo(ax, ay))
            shapes.append(
                cv.Path(
                    handle_path,
                    paint=ft.Paint(
                        stroke_width=6,
                        style=ft.PaintingStyle.STROKE,
                        color=ft.Colors.BLUE_GREY_300,
                        stroke_cap=ft.StrokeCap.ROUND,
                    ),
                )
            )

        self._bucket_canvas.shapes = shapes
        self._bucket_canvas.update()

    def _start_wave_animation(self):
        """물 파도 애니메이션 (30fps)."""
        def tick():
            if self.page is None:
                return
            self._wave_offset += 0.013
            if self._wave_offset > 1.0:
                self._wave_offset -= 1.0
            try:
                self._draw_bucket(
                    type("E", (), {"width": 340, "height": 320})()
                )
            except Exception:
                pass
            self._wave_timer = threading.Timer(1 / 30, tick)
            self._wave_timer.daemon = True
            self._wave_timer.start()

        self._wave_timer = threading.Timer(0.1, tick)
        self._wave_timer.daemon = True
        self._wave_timer.start()

    def _on_bucket_tap(self, e):
        """양동이 탭 → 물 출렁임."""
        self._wobble_angle = 6.0

        def reset():
            for i in range(10):
                self._wobble_angle *= 0.7
                import time
                time.sleep(0.03)
            self._wobble_angle = 0

        threading.Thread(target=reset, daemon=True).start()

    def _on_start(self, e):
        self._is_running = True
        self._elapsed = 0
        self._progress = 0.0
        self._start_btn.visible = False
        self._pause_btn.visible = True
        self._stop_btn.visible = True
        self._current_msg = random.choice(self._running_msgs)
        self._motivation_text.value = self._current_msg
        self.page.update()

        self.timer_service.start(self._on_tick)

    def _on_tick(self):
        self._elapsed += 1
        self._progress = min(self._elapsed / self._goal_seconds, 1.0)
        self._timer_text.value = self._format_time(self._elapsed)
        self._info_text.value = (
            f"{self._goal_seconds // 60}분 목표 · 오늘 {self._format_time(self._today_total + self._elapsed)}"
        )

        # Change message every 8 seconds
        if self._elapsed % 8 == 0:
            self._current_msg = random.choice(self._running_msgs)
            self._motivation_text.value = self._current_msg

        try:
            self.page.update()
        except Exception:
            pass

    def _on_pause(self, e):
        self.timer_service.stop()
        self._is_running = False
        self._pause_btn.text = "재개"
        self._pause_btn.on_click = self._on_resume
        self.page.update()

    def _on_resume(self, e):
        self._is_running = True
        self._pause_btn.text = "일시정지"
        self._pause_btn.on_click = self._on_pause
        self.page.update()
        self.timer_service.start(self._on_tick)

    def _on_stop(self, e):
        self.timer_service.stop()
        self._is_running = False
        self._today_total += self._elapsed

        # Save session
        self._save_session()

        # Reset UI
        self._elapsed = 0
        self._progress = 0.0
        self._timer_text.value = self._format_time(0)
        self._start_btn.visible = True
        self._pause_btn.visible = False
        self._stop_btn.visible = False
        self._pause_btn.text = "일시정지"
        self._pause_btn.on_click = self._on_pause
        self._current_msg = random.choice(self._idle_msgs)
        self._motivation_text.value = self._current_msg
        self._info_text.value = (
            f"{self._goal_seconds // 60}분 집중 시 양동이 가득 · 오늘 {self._format_time(self._today_total)}"
        )
        self.page.update()

    def _save_session(self):
        from datetime import datetime

        sessions = self.store.load("focus_sessions.json", [])
        sessions.append(
            {
                "startTime": datetime.now().isoformat(),
                "durationSeconds": self._elapsed,
                "dateKey": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        self.store.save("focus_sessions.json", sessions)
