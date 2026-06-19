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
from output.report_generator import ReportGenerator

aggregator = MetricsAggregator()
stress_engine = StressEngine()
generator = ReportGenerator()

while True:

    metrics = aggregator.get_metrics()

    stress = stress_engine.calculate(
        metrics
    )

    generator.save_report(
        metrics,
        stress
    )

    print("JSON Updated")

    time.sleep(5)