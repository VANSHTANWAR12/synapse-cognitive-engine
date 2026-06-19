import sys
import os
import json
import time
import threading
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path to ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.aggregator import MetricsAggregator
from scoring.stress_engine import StressEngine
from output.report_generator import ReportGenerator

REPORT_FILE = os.path.join("reports", "latest_report.json")

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

# Default initial report to serve if reports/latest_report.json does not exist yet
DEFAULT_REPORT = {
    "timestamp": datetime.now().isoformat(),
    "stress": {"score": 0.0, "level": "Relaxed"},
    "contributors": {"typing": 0.0, "context_switching": 0.0, "mouse_activity": 0.0, "fatigue": 0.0},
    "recommendation": {"title": "Initializing", "reason": "Gathering initial data..."},
    "metrics": {
        "keyboard": {"keys_per_min": 0, "backspaces_per_min": 0, "avg_pause": 0.0, "long_pause_count": 0, "typing_variance": 0.0},
        "mouse": {"mouse_speed": 0.0, "click_rate": 0, "movement_distance": 0.0},
        "window": {"active_window": "None", "window_switches": 0},
        "session": {"session_minutes": 0.0, "break_count": 0, "time_since_last_break": 0.0}
    }
}

def run_aggregator_loop():
    print("Starting background Metrics Aggregator loop...", flush=True)
    try:
        aggregator = MetricsAggregator()
        stress_engine = StressEngine()
        generator = ReportGenerator()
    except Exception as e:
        print(f"Error initializing trackers: {e}. Check if dependencies or permissions are correct.", flush=True)
        return

    while True:
        try:
            metrics = aggregator.get_metrics()
            stress = stress_engine.calculate(metrics)
            generator.save_report(metrics, stress)
        except Exception as e:
            print(f"Error in aggregator loop: {e}", flush=True)
        time.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: launch daemon thread
    t = threading.Thread(target=run_aggregator_loop, daemon=True)
    t.start()
    yield
    # Shutdown logic

app = FastAPI(title="Synapse Backend", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/report")
def get_report():
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading report file: {e}", flush=True)
    return DEFAULT_REPORT
