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
from scoring.stress_engine import StressEngine

aggregator = MetricsAggregator()
engine = StressEngine()

print("Stress Engine Started")

while True:

    metrics = aggregator.get_metrics()

    stress = engine.calculate(metrics)

    print("=" * 80)

    print(stress)

    time.sleep(5)