import sys
import os
import time

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT_DIR)

from trackers.session_tracker import SessionTracker

tracker = SessionTracker()

print("Session Tracker Started")

while True:

    print(tracker.get_metrics())

    time.sleep(5)