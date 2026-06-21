import os
import json
import time
from datetime import datetime

class CVEventEngine:
    def __init__(self, reports_dir="reports"):
        self.reports_dir = reports_dir
        
        self.events_dir = os.path.join(self.reports_dir, "events")
        self.summaries_dir = os.path.join(self.reports_dir, "summaries")
        
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.events_dir, exist_ok=True)
        os.makedirs(self.summaries_dir, exist_ok=True)
        
        self.events_file = os.path.join(self.events_dir, "cv_events.json")
        self.summary_file = os.path.join(self.summaries_dir, "session_summary.json")
        
        # Load from files on startup
        self.events = self._load_events()
        self.summary = self._load_summary()
        
        # Live state machine variables
        self.mouth_open_start_time = None
        self.yawn_triggered = False
        
        self.in_frustration = False
        self.attention_state = "HEALTHY"  # HEALTHY or LOW
        
        self.poor_posture_start_time = None
        self.posture_state = "HEALTHY"  # HEALTHY or POOR
        self.poor_posture_threshold = 15.0  # seconds
        
        self.fatigue_history = []  # list of (timestamp, value)
        self.last_fatigue_spike_time = 0.0
        
        self.in_overload = False
        
        self.face_absent_start_time = None
        self.face_state = "PRESENT"  # PRESENT or ABSENT
        self.face_absent_threshold = 10.0  # seconds
        
        self.last_wellness_alert_time = 0.0
        self.wellness_alert_active = False
        
        self.engagement_history = []  # list of (timestamp, value)
        self.last_engagement_drop_time = 0.0
        
        self.negative_valence_start_time = None
        self.in_negative_state = False

    def _load_events(self):
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "events" in data:
                        return data["events"]
            except Exception as e:
                print(f"CVEventEngine: Warning - Could not load events: {e}", flush=True)
        return []

    def _load_summary(self):
        default_summary = {
            "yawn_count": 0,
            "frustration_events": 0,
            "attention_drops": 0,
            "posture_violations": 0,
            "fatigue_spikes": 0,
            "cognitive_overload_events": 0,
            "wellness_alerts": 0
        }
        if os.path.exists(self.summary_file):
            try:
                with open(self.summary_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for k, v in default_summary.items():
                            if k not in data:
                                data[k] = v
                        return data
            except Exception as e:
                print(f"CVEventEngine: Warning - Could not load summary: {e}", flush=True)
        return default_summary

    def _save_events(self):
        try:
            with open(self.events_file, "w") as f:
                json.dump({"events": self.events}, f, indent=4)
        except Exception as e:
            print(f"CVEventEngine: Error saving events: {e}", flush=True)

    def _save_summary(self):
        try:
            with open(self.summary_file, "w") as f:
                json.dump(self.summary, f, indent=4)
        except Exception as e:
            print(f"CVEventEngine: Error saving summary: {e}", flush=True)

    def get_recent_events(self, limit=20):
        return self.events[:limit]

    def get_session_summary(self):
        return self.summary.copy()

    def process(self, metrics, stress_score):
        cv = metrics.get("cv", {})
        session = metrics.get("session", {})
        
        frustration_score = cv.get("frustration_score", 0)
        attention_score = cv.get("attention_score", 100)
        posture_score = cv.get("posture_score", 100)
        fatigue_index = cv.get("fatigue_index", 0)
        cognitive_overload_score = cv.get("cognitive_overload_score", 0)
        engagement_score = cv.get("engagement_score", 100)
        emotional_valence = cv.get("emotional_valence", "Neutral")
        face_present = cv.get("face_present", False)
        
        mar = cv.get("mouth_aspect_ratio", 0.0)
        session_minutes = session.get("session_minutes", 0.0)
        
        now_time = time.time()
        timestamp = datetime.now().isoformat()
        
        new_events = []
        
        def add_event(event_type, severity, score, details=None):
            event = {
                "timestamp": timestamp,
                "event_type": event_type,
                "severity": severity,
                "score": int(score),
                "details": details or {}
            }
            self.events.insert(0, event)
            if len(self.events) > 1000:
                self.events = self.events[:1000]
            new_events.append(event)
            
        # 1. YAWN_DETECTED
        if mar > 0.5:
            if self.mouth_open_start_time is None:
                self.mouth_open_start_time = now_time
            elif (now_time - self.mouth_open_start_time >= 1.5) and not self.yawn_triggered:
                add_event("YAWN_DETECTED", "LOW", mar * 100, {"mouth_aspect_ratio": mar, "duration_sec": round(now_time - self.mouth_open_start_time, 1)})
                self.summary["yawn_count"] += 1
                self.yawn_triggered = True
        else:
            self.mouth_open_start_time = None
            self.yawn_triggered = False
            
        # 2. HIGH_FRUSTRATION
        if frustration_score > 60:
            if not self.in_frustration:
                add_event("HIGH_FRUSTRATION", "HIGH", frustration_score)
                self.summary["frustration_events"] += 1
                self.in_frustration = True
        elif frustration_score <= 50:
            self.in_frustration = False
            
        # 3. LOW_ATTENTION / 4. ATTENTION_RECOVERED
        if self.attention_state == "HEALTHY":
            if attention_score < 50:
                add_event("LOW_ATTENTION", "MEDIUM", attention_score)
                self.summary["attention_drops"] += 1
                self.attention_state = "LOW"
        elif self.attention_state == "LOW":
            if attention_score >= 75:
                add_event("ATTENTION_RECOVERED", "LOW", attention_score)
                self.attention_state = "HEALTHY"
                
        # 5. POOR_POSTURE / 6. POSTURE_RECOVERED
        if posture_score < 60:
            if self.poor_posture_start_time is None:
                self.poor_posture_start_time = now_time
            elif (now_time - self.poor_posture_start_time >= self.poor_posture_threshold) and self.posture_state == "HEALTHY":
                add_event("POOR_POSTURE", "MEDIUM", posture_score, {"duration_maintained_sec": round(now_time - self.poor_posture_start_time, 1)})
                self.summary["posture_violations"] += 1
                self.posture_state = "POOR"
        else:
            if posture_score >= 75 and self.posture_state == "POOR":
                add_event("POSTURE_RECOVERED", "LOW", posture_score)
                self.posture_state = "HEALTHY"
            self.poor_posture_start_time = None
            
        # 7. FATIGUE_SPIKE
        self.fatigue_history.append((now_time, fatigue_index))
        self.fatigue_history = [item for item in self.fatigue_history if now_time - item[0] <= 30]
        if len(self.fatigue_history) > 1:
            oldest_fatigue = self.fatigue_history[0][1]
            if (fatigue_index - oldest_fatigue > 15) and (now_time - self.last_fatigue_spike_time > 60):
                add_event("FATIGUE_SPIKE", "MEDIUM", fatigue_index, {"increase_points": fatigue_index - oldest_fatigue})
                self.summary["fatigue_spikes"] += 1
                self.last_fatigue_spike_time = now_time
                
        # 8. COGNITIVE_OVERLOAD
        if cognitive_overload_score > 70:
            if not self.in_overload:
                add_event("COGNITIVE_OVERLOAD", "HIGH", cognitive_overload_score)
                self.summary["cognitive_overload_events"] += 1
                self.in_overload = True
        elif cognitive_overload_score <= 55:
            self.in_overload = False
            
        # 9. FACE_NOT_PRESENT
        if not face_present:
            if self.face_absent_start_time is None:
                self.face_absent_start_time = now_time
            elif (now_time - self.face_absent_start_time >= self.face_absent_threshold) and self.face_state == "PRESENT":
                add_event("FACE_NOT_PRESENT", "MEDIUM", 0, {"absent_duration_sec": round(now_time - self.face_absent_start_time, 1)})
                self.face_state = "ABSENT"
        else:
            self.face_absent_start_time = None
            self.face_state = "PRESENT"
            
        # 10. WELLNESS_ALERT
        # High stress, High fatigue, High frustration, Long session
        if stress_score > 65 and fatigue_index > 60 and frustration_score > 55 and session_minutes > 40.0:
            if not self.wellness_alert_active and (now_time - self.last_wellness_alert_time > 300):
                add_event("WELLNESS_ALERT", "CRITICAL", stress_score, {
                    "stress": stress_score,
                    "fatigue": fatigue_index,
                    "frustration": frustration_score,
                    "session_minutes": session_minutes
                })
                self.summary["wellness_alerts"] += 1
                self.wellness_alert_active = True
                self.last_wellness_alert_time = now_time
        else:
            self.wellness_alert_active = False
            
        # 11. ENGAGEMENT_DROP
        self.engagement_history.append((now_time, engagement_score))
        self.engagement_history = [item for item in self.engagement_history if now_time - item[0] <= 30]
        if len(self.engagement_history) > 1:
            oldest_engagement = self.engagement_history[0][1]
            if (oldest_engagement - engagement_score > 20) and (now_time - self.last_engagement_drop_time > 60):
                add_event("ENGAGEMENT_DROP", "HIGH", engagement_score, {"decrease_points": oldest_engagement - engagement_score})
                self.last_engagement_drop_time = now_time
                
        # 12. NEGATIVE_EMOTIONAL_STATE
        if emotional_valence == "Negative":
            if self.negative_valence_start_time is None:
                self.negative_valence_start_time = now_time
            elif (now_time - self.negative_valence_start_time >= 30.0) and not self.in_negative_state:
                add_event("NEGATIVE_EMOTIONAL_STATE", "MEDIUM", frustration_score, {"valence": "Negative", "duration_sec": round(now_time - self.negative_valence_start_time, 1)})
                self.in_negative_state = True
        else:
            self.negative_valence_start_time = None
            self.in_negative_state = False
            
        if new_events:
            self._save_events()
            self._save_summary()
            
        return new_events
