import os
import json
import time
import threading
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

try:
    from notion_client import Client
except ImportError:
    Client = None

class NotionSyncManager:
    def __init__(self, interval_sec=180):
        self.interval_sec = interval_sec
        self.notion_token = os.environ.get("NOTION_TOKEN")
        self.database_id = os.environ.get("DATABASE_ID")
        self.client = Client(auth=self.notion_token) if (Client and self.notion_token) else None
        self._stop_event = threading.Event()
        self.sync_thread = None

    def start(self):
        if not Client:
            print("[NotionSync] notion-client not installed. Notion sync disabled.", flush=True)
            return

        if not self.notion_token or not self.database_id:
            print("[NotionSync] NOTION_TOKEN or DATABASE_ID not found in environment. Notion sync disabled.", flush=True)
            return
            
        print(f"[NotionSync] Starting background Notion sync every {self.interval_sec} seconds...", flush=True)
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()

    def stop(self):
        self._stop_event.set()
        if self.sync_thread:
            self.sync_thread.join(timeout=2)

    def _sync_loop(self):
        while not self._stop_event.is_set():
            try:
                self._run_sync()
            except Exception as e:
                print(f"[NotionSync] Error syncing to Notion: {e}", flush=True)
            # Sleep in small increments so it can be stopped quickly
            for _ in range(self.interval_sec):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def _run_sync(self):
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "latest_report.json")
        if not os.path.exists(report_path):
            return
            
        with open(report_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
            
        self._push_snapshot(snapshot)
        print(f"[NotionSync] Synced snapshot {snapshot.get('timestamp')} to Notion.", flush=True)

    def _top_risk_factors_from_contributors(self, contributors: dict, k: int = 3):
        if not isinstance(contributors, dict):
            return []
        ranked = sorted(
            ((name, val) for name, val in contributors.items() if isinstance(val, (int, float))),
            key=lambda x: x[1],
            reverse=True
        )
        bucket_map = {
            "typing": "Workload",
            "context_switching": "Meetings",
            "mouse_activity": "Workload",
            "fatigue": "Sleep",
            "posture": "Personal",
            "attention": "Workload",
            "frustration": "Deadlines",
            "stress_expression": "Personal",
        }
        factors = []
        for name, _val in ranked:
            mapped = bucket_map.get(name)
            if mapped and mapped not in factors:
                factors.append(mapped)
            if len(factors) >= k:
                break
        return factors

    def _to_iso(self, dt):
        if isinstance(dt, str):
            return dt
        if isinstance(dt, datetime):
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        return None

    def _push_snapshot(self, snapshot: dict):
        ts = snapshot.get("timestamp")
        
        stress_score = (snapshot.get("stress") or {}).get("score")
        stress_level = (snapshot.get("stress") or {}).get("level")

        cv_metrics = (((snapshot.get("metrics") or {}).get("cv") or {}).get("cv_metrics")) or {}
        fatigue_index = cv_metrics.get("fatigue_index")
        attention_score = cv_metrics.get("attention_score")

        severity = (snapshot.get("alert") or {}).get("severity")
        severity_to_burnout = {"LOW": 10, "MEDIUM": 50, "HIGH": 90}
        burnout_risk = severity_to_burnout.get(severity, 10) # default to LOW if not found

        state_map = {
            "Relaxed": "Calm",
            "Calm": "Calm",
            "Focused": "Focused",
            "Stressed": "Stressed",
            "Fatigued": "Fatigued",
            "Tired": "Fatigued",
            "Mild Stress": "Stressed",
            "High Stress": "Stressed",
            "Critical Stress": "Stressed",
        }
        current_state = state_map.get(stress_level, "Calm")

        risk_factors = self._top_risk_factors_from_contributors(snapshot.get("contributors"), k=3)

        json_str = json.dumps(snapshot, ensure_ascii=False)
        # Notion text limit is 2000 chars per block, max 100 blocks
        chunks = [json_str[i:i+2000] for i in range(0, len(json_str), 2000)][:100]
        rich_text_content = [{"text": {"content": c}} for c in chunks]

        props = {
            "Record": {"title": [{"text": {"content": f"Snapshot {ts}" if ts else "Snapshot"}}]},
            "Timestamp": {"date": {"start": self._to_iso(ts)}} if ts else {"date": None},
            "Stress Score": {"number": float(stress_score) if stress_score is not None else None},
            "Burnout Risk": {"number": float(burnout_risk) if burnout_risk is not None else None},
            "Fatigue Index": {"number": float(fatigue_index) if fatigue_index is not None else None},
            "Attention Score": {"number": float(attention_score) if attention_score is not None else None},
            "JSON Snapshot": {"rich_text": rich_text_content},
        }

        if current_state:
            props["Current State"] = {"select": {"name": current_state}}

        if risk_factors:
            props["Top Risk Factors"] = {"multi_select": [{"name": x} for x in risk_factors]}

        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=props
        )
