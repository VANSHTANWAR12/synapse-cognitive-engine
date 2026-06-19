import sys
import os
import time

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT_DIR)

from trackers.keyboard_tracker import KeyboardTracker

tracker = KeyboardTracker()

tracker.start()

print("Keyboard Tracker Started")
print("Start typing...\n")

while True:

    metrics = tracker.get_metrics()

    print("=" * 40)
    print(metrics)

    time.sleep(5)