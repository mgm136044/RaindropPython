"""1초 간격 타이머 서비스."""

import threading


class TimerService:
    def __init__(self):
        self._timer: threading.Timer | None = None
        self._running = False
        self._callback = None

    def start(self, callback):
        self._callback = callback
        self._running = True
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
