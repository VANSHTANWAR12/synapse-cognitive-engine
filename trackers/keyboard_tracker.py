from pynput import keyboard
import time
from collections import deque
import statistics


class KeyboardTracker:

    def __init__(self):

        # key timestamps
        self.key_times = deque()

        # backspace timestamps
        self.backspace_times = deque()

        # pause durations
        self.pause_times = []

        self.last_key_time = None

        self.ignored_keys = {
            keyboard.Key.shift,
            keyboard.Key.shift_r,
            keyboard.Key.ctrl,
            keyboard.Key.ctrl_r,
            keyboard.Key.alt,
            keyboard.Key.alt_r,
            keyboard.Key.cmd,
        }

    def cleanup(self):
        """
        Keep only last 60 seconds data.
        """

        now = time.time()

        while self.key_times and now - self.key_times[0] > 60:
            self.key_times.popleft()

        while self.backspace_times and now - self.backspace_times[0] > 60:
            self.backspace_times.popleft()

    def on_press(self, key):

        if key in self.ignored_keys:
            return

        now = time.time()

        # store key press
        self.key_times.append(now)

        # pause calculation
        if self.last_key_time is not None:

            pause = now - self.last_key_time

            self.pause_times.append(pause)

            # keep pause list small
            if len(self.pause_times) > 200:
                self.pause_times.pop(0)

        self.last_key_time = now

        # backspace tracking
        if key == keyboard.Key.backspace:
            self.backspace_times.append(now)

    def start(self):

        self.listener = keyboard.Listener(
            on_press=self.on_press
        )

        self.listener.daemon = True
        self.listener.start()

    def get_metrics(self):

        self.cleanup()

        avg_pause = 0
        variance = 0

        if self.pause_times:
            avg_pause = round(
                sum(self.pause_times) / len(self.pause_times),
                2
            )

        if len(self.pause_times) >= 2:
            variance = round(
                statistics.stdev(self.pause_times),
                2
            )

        long_pause_count = len(
            [p for p in self.pause_times if p > 5]
        )

        return {
            "keys_per_min": len(self.key_times),
            "backspaces_per_min": len(self.backspace_times),
            "avg_pause": avg_pause,
            "long_pause_count": long_pause_count,
            "typing_variance": variance
        }