import sys
import os
import json
import time
import threading
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path to ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.aggregator import MetricsAggregator
from scoring.stress_engine import StressEngine
from output.report_generator import ReportGenerator
from services.llm_engine import get_supportive_response
from services.rppg_engine import rppg_engine

# Import ML Predictive Engine
from ml.feature_store import FeatureStore
from ml.predictor import Predictor
from ml.train import run_training_loop

# Import Storage Engine
from storage.snapshot_manager import SnapshotManager
from storage.context_builder import ContextBuilder

REPORT_FILE = os.path.join("reports", "latest_report.json")

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

# Default initial report to serve if reports/latest_report.json does not exist yet
DEFAULT_REPORT = {
    "timestamp": datetime.now().isoformat(),
    "stress": {"score": 0.0, "level": "Relaxed"},
    "contributors": {
        "typing": 0.0, 
        "context_switching": 0.0, 
        "mouse_activity": 0.0, 
        "fatigue": 0.0,
        "posture": 0.0,
        "attention": 0.0,
        "frustration": 0.0,
        "stress_expression": 0.0
    },
    "recommendation": {"title": "Initializing", "reason": "Gathering initial data..."},
    "alert": {
        "alert": False,
        "severity": "LOW",
        "reason": "Wellness metrics are within normal range."
    },
    "metrics": {
        "keyboard": {"keys_per_min": 0, "backspaces_per_min": 0, "avg_pause": 0.0, "long_pause_count": 0, "typing_variance": 0.0},
        "mouse": {"mouse_speed": 0.0, "click_rate": 0, "movement_distance": 0.0},
        "window": {"active_window": "None", "window_switches": 0},
        "session": {"session_minutes": 0.0, "break_count": 0, "time_since_last_break": 0.0},
        "cv": {
            "posture_score": 100,
            "blink_rate": 0,
            "eye_fatigue_score": 0,
            "yawn_count": 0,
            "attention_score": 100,
            "screen_distance_cm": 60.0,
            "head_stability_score": 100,
            "presence_percentage": 0.0,
            "fatigue_index": 0,
            "engagement_index": 100,
            "engagement_score": 100,
            "wellness_score": 100,
            "head_tilt": 0.0,
            "neck_angle": 0.0,
            "slouch_detected": False,
            "focused": True,
            "face_present": False,
            "distance_risk": 0,
            "frustration_score": 0,
            "stress_expression_score": 0,
            "emotional_valence": "Neutral",
            "cognitive_overload_score": 0,
            "mood_trend": "Stable",
            "eye_focus": 100,
            "mouth_aspect_ratio": 0.0,
            "cv_metrics": {},
            "recent_events": [],
            "session_summary": {
                "yawn_count": 0,
                "frustration_events": 0,
                "attention_drops": 0,
                "posture_violations": 0,
                "fatigue_spikes": 0,
                "cognitive_overload_events": 0,
                "wellness_alerts": 0
            }
        }
    }
}

def run_aggregator_loop():
    print("Starting background Metrics Aggregator loop...", flush=True)
    try:
        aggregator = MetricsAggregator()
        stress_engine = StressEngine()
        generator = ReportGenerator()
        
        # Initialize ML Predictive Components
        feature_store = FeatureStore()
        predictor = Predictor()
        
        # Initialize Historical Storage Components
        snapshot_manager = SnapshotManager()
        context_builder = ContextBuilder()
        
    except Exception as e:
        print(f"Error initializing trackers: {e}. Check if dependencies or permissions are correct.", flush=True)
        return

    while True:
        try:
            metrics = aggregator.get_metrics()
            stress = stress_engine.calculate(metrics)
            
            # Feed current metrics and calculated stress score to Event Engine
            aggregator.event_engine.process(metrics, stress["stress"]["score"])
            
            # Pull the updated events and session summary from Event Engine
            recent_events = aggregator.event_engine.get_recent_events(20)
            session_summary = aggregator.event_engine.get_session_summary()
            
            # Re-wrap cv metrics with updated data
            metrics["cv"]["recent_events"] = recent_events
            metrics["cv"]["session_summary"] = session_summary
            
            # Save data to SQLite Feature Store for future training
            feature_store.store(metrics, stress["stress"]["score"])
            
            # Run Live LSTM Inference
            prediction = predictor.predict_live_risk()
            metrics["prediction"] = prediction
            
            report = generator.save_report(metrics, stress)
            
            if snapshot_manager.check_and_save_snapshot(report):
                snapshots = snapshot_manager.get_all_snapshots(limit=20)
                context_builder.build_context(snapshots, report)
                
        except Exception as e:
            print(f"Error in aggregator loop: {e}", flush=True)
        time.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: launch daemon thread
    t = threading.Thread(target=run_aggregator_loop, daemon=True)
    t.start()
    
    # Launch ML background training daemon
    ml_train_thread = threading.Thread(target=run_training_loop, daemon=True)
    ml_train_thread.start()
    
    rppg_engine.start()
    yield
    # Shutdown logic
    rppg_engine.stop()

app = FastAPI(title="Synapse Backend", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MindSentry frontend
mindsentry_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Student OS LLM activation", "igdtuw", "mental-ai-frontend")
print(f"Resolved mindsentry_dir: {mindsentry_dir}", flush=True)
if os.path.exists(mindsentry_dir):
    app.mount("/mindsentry", StaticFiles(directory=mindsentry_dir, html=True), name="mindsentry")
else:
    print(f"Warning: mindsentry_dir '{mindsentry_dir}' does not exist, skipping mount.", flush=True)

@app.websocket("/ws/resonance")
async def resonance_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            state = rppg_engine.get_state()
            await websocket.send_json(state)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass

@app.get("/health")
def health():
    return {"status": "ok"}

from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat(request: ChatRequest):
    metrics = get_report()
    stress_level = metrics.get("stress", {}).get("level", "Unknown")
    stress_score = metrics.get("stress", {}).get("score", 0)
    
    # Determine emotion from cv metrics or fallback to stress mapping
    emotion = "neutral"
    if "cv" in metrics.get("metrics", {}):
        emotion = metrics["metrics"]["cv"].get("emotional_valence", "neutral")
    else:
        # Fallback to mapping stress level to basic emotion if emotional_valence is missing
        if stress_score > 70:
            emotion = "fear" if stress_level == "High Stress" else "anger"
        elif stress_score < 30:
            emotion = "neutral"
            
    # Normalize emotion for MindSentry
    emotion = emotion.lower()
    
    # Use MindSentry LLM engine
    response = get_supportive_response(request.message, emotion)

    return {
        "reply": response,
        "context_used": {
            "stress_level": stress_level,
            "stress_score": stress_score,
            "detected_emotion": emotion
        }
    }

@app.get("/report")
def get_report():
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading report file: {e}", flush=True)
    return DEFAULT_REPORT

@app.get("/llm-context")
def get_llm_context():
    context_file = os.path.join("reports", "llm_context", "latest_context.json")
    if os.path.exists(context_file):
        try:
            with open(context_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"error": "Context not generated yet.", "analytics_summary": {}}

@app.get("/snapshots")
def get_snapshots():
    try:
        sm = SnapshotManager()
        return sm.get_all_snapshots(limit=50)
    except Exception as e:
        print(f"Error reading snapshots: {e}", flush=True)
    return []

@app.get("/events")
def get_events():
    events_file = os.path.join("reports", "events", "cv_events.json")
    if os.path.exists(events_file):
        try:
            with open(events_file, "r") as f:
                data = json.load(f)
                # handle {"events": [...]} format
                if isinstance(data, dict) and "events" in data:
                    return data
                return {"events": data}
        except Exception:
            pass
    return {"events": []}

