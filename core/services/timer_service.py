"""1초 간격 타이머 서비스 — monotonic clock 기반."""

import time
import threading


class TimerService:
    def __init__(self):
        self._timer: threading.Timer | None = None
        self._running = False
        self._callback = None
        self._start_time = 0.0
        self._pause_elapsed = 0

    @property
    def elapsed_seconds(self) -> int:
        """드리프트 없는 경과 시간."""
        if self._running:
            return self._pause_elapsed + int(time.monotonic() - self._start_time)
        return self._pause_elapsed

    def start(self, callback):
        if self._running:
            return  # I2: double-start 방지
        self._callback = callback
        self._running = True
        self._start_time = time.monotonic()
        self._tick()

    def pause(self):
        self._running = False
        self._pause_elapsed += int(time.monotonic() - self._start_time)
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def resume(self, callback):
        if self._running:
            return
        self._callback = callback
        self._running = True
        self._start_time = time.monotonic()
        self._tick()

    def _tick(self):
        if not self._running:
            return
        if self._callback:
            self._callback()
        self._timer = threading.Timer(1.0, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def stop(self):
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        total = self._pause_elapsed
        self._pause_elapsed = 0
        return total

    def reset(self):
        self.stop()
        self._pause_elapsed = 0
