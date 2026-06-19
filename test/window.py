import sys
import os
import time

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT_DIR)

from trackers.window_tracker import WindowTracker

tracker = WindowTracker()

print("Window Tracker Started")
print("Switch between apps...\n")

while True:

    tracker.update()

    print(
        tracker.get_metrics()
    )

    time.sleep(1)