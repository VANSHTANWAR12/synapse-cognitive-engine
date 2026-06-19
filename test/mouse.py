import time
import sys
import os

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT_DIR)
from trackers.mouse_tracker import MouseTracker

tracker = MouseTracker()

tracker.start()

print("Mouse Tracker Started")

while True:

    print(tracker.get_metrics())

    time.sleep(5)