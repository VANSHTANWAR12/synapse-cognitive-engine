from pynput import mouse
from collections import deque
import time
import math


class MouseTracker:

    def __init__(self):

        self.click_times = deque()

        self.movements = deque()

        self.last_x = None
        self.last_y = None

    def cleanup(self):

        now = time.time()

        while self.click_times and now - self.click_times[0] > 60:
            self.click_times.popleft()

        while self.movements and now - self.movements[0][0] > 60:
            self.movements.popleft()

    def on_move(self, x, y):

        now = time.time()

        if self.last_x is not None:

            distance = math.sqrt(
                (x - self.last_x) ** 2 +
                (y - self.last_y) ** 2
            )

            self.movements.append(
                (now, distance)
            )

        self.last_x = x
        self.last_y = y

    def on_click(self, x, y, button, pressed):

        if pressed:
            self.click_times.append(
                time.time()
            )

    def start(self):

        listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )

        listener.daemon = True
        listener.start()

    def get_metrics(self):

        self.cleanup()

        total_distance = sum(
            movement[1]
            for movement in self.movements
        )

        mouse_speed = round(
            total_distance / 60,
            2
        )

        return {
            "mouse_speed": mouse_speed,
            "click_rate": len(self.click_times),
            "movement_distance": round(
                total_distance,
                2
            )
        }