import os
import json
import time
from datetime import datetime
from storage.retention_manager import RetentionManager

class SnapshotManager:
    """Manages periodic saving of historical snapshots."""
    
    def __init__(self, reports_dir="reports", interval_seconds=180, max_snapshots=500):
        self.snapshots_dir = os.path.join(reports_dir, "snapshots")
        os.makedirs(self.snapshots_dir, exist_ok=True)
        
        self.interval_seconds = interval_seconds
        self.max_snapshots = max_snapshots
        self.last_snapshot_time = 0.0

    def check_and_save_snapshot(self, report_data):
        """
        Checks if the interval has passed. If so, saves a new snapshot and triggers retention.
        Returns True if a snapshot was saved, False otherwise.
        """
        current_time = time.time()
        
        # If it hasn't been 180 seconds yet, skip
        if (current_time - self.last_snapshot_time) < self.interval_seconds:
            return False
            
        self.save_snapshot(report_data)
        self.last_snapshot_time = current_time
        return True

    def save_snapshot(self, report_data):
        """Saves a snapshot with format YYYY-MM-DD_HH-MM-SS.json"""
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp_str}.json"
        filepath = os.path.join(self.snapshots_dir, filename)
        
        # Ensure we only include the requested fields or build from report_data
        # report_data should already be structured by ReportGenerator
        snapshot_data = {
            "timestamp": report_data.get("timestamp", datetime.now().isoformat()),
            "stress": report_data.get("stress", {}),
            "contributors": report_data.get("contributors", {}),
            "recommendation": report_data.get("recommendation", {}),
            "metrics": report_data.get("metrics", {}),
            "cv_metrics": report_data.get("cv_metrics", {}),
            "recent_events": report_data.get("recent_events", []),
            "session_summary": report_data.get("session_summary", {}),
            "predictive": report_data.get("metrics", {}).get("prediction", {}),
            "current_state": "ACTIVE" # Placeholder, can be refined based on metrics
        }
        
        try:
            with open(filepath, "w") as f:
                json.dump(snapshot_data, f, indent=4)
        except Exception as e:
            print(f"SnapshotManager: Error saving snapshot: {e}", flush=True)
            return

        # Enforce retention policy
        RetentionManager.enforce_retention(self.snapshots_dir, self.max_snapshots)

    def get_all_snapshots(self, limit=None):
        """Returns a list of all snapshots, parsed, newest first."""
        if not os.path.exists(self.snapshots_dir):
            return []
            
        snapshots = []
        for filename in os.listdir(self.snapshots_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.snapshots_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        snapshots.append((os.path.getmtime(filepath), data))
                except Exception as e:
                    print(f"SnapshotManager: Failed to read {filename}: {e}", flush=True)
                    
        snapshots.sort(key=lambda x: x[0], reverse=True)
        result = [s[1] for s in snapshots]
        
        if limit is not None:
            return result[:limit]
        return result
