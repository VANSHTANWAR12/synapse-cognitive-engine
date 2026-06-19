import sys
import os
import time

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, ROOT_DIR)

from services.aggregator import MetricsAggregator

aggregator = MetricsAggregator()

print("Aggregator Started")

while True:

    print("=" * 80)

    print(
        aggregator.get_metrics()
    )

    time.sleep(5)