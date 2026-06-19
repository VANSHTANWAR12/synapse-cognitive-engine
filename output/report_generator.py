import json
import os
from datetime import datetime


class ReportGenerator:

    def __init__(self):

        self.report_dir = "reports"

        os.makedirs(
            self.report_dir,
            exist_ok=True
        )

        self.report_file = os.path.join(
            self.report_dir,
            "latest_report.json"
        )

    def save_report(
        self,
        metrics,
        stress
    ):

        report = {

            "timestamp":
                datetime.now().isoformat(),

            "stress":
                stress["stress"],

            "contributors":
                stress["contributors"],

            "recommendation":
                stress["recommendation"],

            "metrics":
                metrics
        }

        with open(
            self.report_file,
            "w"
        ) as f:

            json.dump(
                report,
                f,
                indent=4
            )

        return report