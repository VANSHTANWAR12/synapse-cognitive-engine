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

        # Calculate Manager Alert
        cv = metrics.get("cv", {})
        session = metrics.get("session", {})
        stress_score = stress.get("stress", {}).get("score", 0.0)
        
        frustration = cv.get("frustration_score", 0)
        cognitive_overload = cv.get("cognitive_overload_score", 0)
        fatigue = cv.get("fatigue_index", 0)
        session_minutes = session.get("session_minutes", 0.0)
        
        triggers = []
        if frustration >= 50:
            triggers.append("elevated frustration signals")
        if cognitive_overload >= 50:
            triggers.append("high cognitive overload")
        if fatigue >= 50:
            triggers.append("high fatigue index")
        if session_minutes >= 60.0:
            triggers.append("prolonged session duration")
        if cv.get("posture_score", 100) <= 60:
            triggers.append("poor posture")
            
        severity = "LOW"
        alert_triggered = False
        
        if stress_score >= 80.0 or (frustration >= 75 and cognitive_overload >= 75):
            severity = "CRITICAL"
            alert_triggered = True
        elif stress_score >= 60.0 or frustration >= 60 or cognitive_overload >= 60 or fatigue >= 65:
            severity = "HIGH"
            alert_triggered = True
        elif stress_score >= 35.0 or frustration >= 35 or cognitive_overload >= 35 or fatigue >= 40:
            severity = "MODERATE"
            alert_triggered = True
            
        if alert_triggered and triggers:
            reason_str = ", ".join(triggers)
            if ", " in reason_str:
                parts = reason_str.rsplit(", ", 1)
                reason_str = " and ".join(parts)
            reason = reason_str[0].upper() + reason_str[1:] + " detected."
        else:
            reason = "Wellness metrics are within normal range."
            
        alert_data = {
            "alert": alert_triggered,
            "severity": severity,
            "reason": reason
        }

        report = {

            "timestamp":
                datetime.now().isoformat(),

            "stress":
                stress["stress"],

            "contributors":
                stress["contributors"],

            "recommendation":
                stress["recommendation"],

            "alert":
                alert_data,

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