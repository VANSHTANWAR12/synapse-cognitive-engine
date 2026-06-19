import time

from trackers.keyboard_tracker import KeyboardTracker
from trackers.mouse_tracker import MouseTracker
from trackers.window_tracker import WindowTracker
from trackers.session_tracker import SessionTracker


class MetricsAggregator:

    def __init__(self):

        self.keyboard = KeyboardTracker()
        self.mouse = MouseTracker()
        self.window = WindowTracker()
        self.session = SessionTracker()

        self.keyboard.start()
        self.mouse.start()

        self.break_threshold = 300

        self.on_break = False

    def update_session(self):

        last_activity = max(
            self.keyboard.last_activity_time,
            self.mouse.last_activity_time
        )

        idle_time = time.time() - last_activity

        if idle_time >= self.break_threshold:

            if not self.on_break:

                self.session.record_break()
                self.on_break = True

        else:

            self.on_break = False

    def get_metrics(self):

        self.window.update()

        self.update_session()

        return {

            "keyboard":
                self.keyboard.get_metrics(),

            "mouse":
                self.mouse.get_metrics(),

            "window":
                self.window.get_metrics(),

            "session":
                self.session.get_metrics()
        }