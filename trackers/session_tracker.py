import time


class SessionTracker:

    def __init__(self):

        self.session_start = time.time()

        self.break_count = 0

        self.last_break_time = self.session_start

    def record_break(self):

        self.break_count += 1

        self.last_break_time = time.time()

    def get_metrics(self):

        now = time.time()

        session_minutes = round(
            (now - self.session_start) / 60,
            2
        )

        time_since_last_break = round(
            (now - self.last_break_time) / 60,
            2
        )

        return {
            "session_minutes": session_minutes,
            "break_count": self.break_count,
            "time_since_last_break":
                time_since_last_break
        }