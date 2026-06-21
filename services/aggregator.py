import time

from trackers.keyboard_tracker import KeyboardTracker
from trackers.mouse_tracker import MouseTracker
from trackers.window_tracker import WindowTracker
from trackers.session_tracker import SessionTracker
from trackers.cv_tracker import CVTracker


class MetricsAggregator:

    def __init__(self):

        self.keyboard = KeyboardTracker()
        self.mouse = MouseTracker()
        self.window = WindowTracker()
        self.session = SessionTracker()
        self.cv = CVTracker()

        self.keyboard.start()
        self.mouse.start()
        self.cv.start()

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

        keyboard_metrics = self.keyboard.get_metrics()
        mouse_metrics = self.mouse.get_metrics()
        window_metrics = self.window.get_metrics()
        session_metrics = self.session.get_metrics()
        cv_metrics = self.cv.get_metrics(
            keyboard=keyboard_metrics,
            window=window_metrics,
            session=session_metrics
        )

        return {

            "keyboard": keyboard_metrics,

            "mouse": mouse_metrics,

            "window": window_metrics,

            "session": session_metrics,
            
            "cv": cv_metrics
        }