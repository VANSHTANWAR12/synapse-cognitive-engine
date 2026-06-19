import pygetwindow as gw
import time
from collections import deque


class WindowTracker:

    def __init__(self):

        self.last_window = None

        self.switch_times = deque()

    def cleanup(self):

        now = time.time()

        while (
            self.switch_times and
            now - self.switch_times[0] > 60
        ):
            self.switch_times.popleft()

    def update(self):

        try:

            current_window = gw.getActiveWindow()

            if current_window is None:
                return

            title = current_window.title

            if self.last_window is None:
                self.last_window = title
                return

            if title != self.last_window:

                self.switch_times.append(
                    time.time()
                )

                self.last_window = title

        except:
            pass

    def get_metrics(self):

        self.cleanup()

        return {
            "active_window": self.last_window,
            "window_switches": len(
                self.switch_times
            )
        }