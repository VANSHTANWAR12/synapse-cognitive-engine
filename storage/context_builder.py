import os
import json
from datetime import datetime

class ContextBuilder:
    """Generates LLM-optimized context from recent snapshots and live data."""
    
    def __init__(self, reports_dir="reports"):
        self.llm_context_dir = os.path.join(reports_dir, "llm_context")
        os.makedirs(self.llm_context_dir, exist_ok=True)
        self.latest_context_file = os.path.join(self.llm_context_dir, "latest_context.json")

    def build_context(self, snapshots, current_report):
        """Builds the LLM context and generates historical analytics."""
        
        # Calculate trends from snapshots
        # snapshots are ordered newest first
        # 15 minutes = ~5 snapshots (at 3 mins interval), 60 mins = ~20
        
        recent_stress = []
        recent_fatigue = []
        recent_attention = []
        recent_burnout = []
        
        for snap in snapshots[:20]:  # up to 60 mins
            s = snap.get("stress", {}).get("score", 0)
            f = snap.get("cv_metrics", {}).get("fatigue_index", 0)
            a = snap.get("cv_metrics", {}).get("attention_score", 100)
            b = snap.get("predictive", {}).get("burnout_risk", 0)
            
            recent_stress.append(s)
            recent_fatigue.append(f)
            recent_attention.append(a)
            recent_burnout.append(b)
            
        def get_trend(values):
            if len(values) < 2: return "STABLE"
            # oldest is at the end, newest at the start
            old_avg = sum(values[len(values)//2:]) / max(1, len(values[len(values)//2:]))
            new_avg = sum(values[:len(values)//2]) / max(1, len(values[:len(values)//2]))
            if new_avg > old_avg + 5: return "RISING"
            if new_avg < old_avg - 5: return "DECLINING"
            return "STABLE"

        avg_stress = sum(recent_stress) / len(recent_stress) if recent_stress else 0
        peak_stress = max(recent_stress) if recent_stress else 0
        
        analytics_summary = {
            "snapshot_count": len(snapshots),
            "average_stress": int(avg_stress),
            "peak_stress": int(peak_stress),
            "stress_trend": get_trend(recent_stress),
            "fatigue_trend": get_trend(recent_fatigue),
            "attention_trend": get_trend(recent_attention),
            "burnout_risk_trend": get_trend(recent_burnout)
        }

        # Current State Determination
        current_state = "RELAXED"
        if avg_stress > 70: current_state = "HIGH_STRESS"
        elif recent_fatigue and recent_fatigue[0] > 70: current_state = "FATIGUED"
        elif recent_attention and recent_attention[0] < 40: current_state = "DISTRACTED"
        elif current_report.get("cv_metrics", {}).get("frustration_score", 0) > 60: current_state = "FRUSTRATED"

        # Extract top risk factors
        top_risk_factors = []
        contributors = current_report.get("contributors", {})
        sorted_contribs = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
        top_risk_factors = [k for k, v in sorted_contribs[:3] if v > 15]

        # Construct final LLM context
        llm_context = {
            "current_state": current_state,
            "stress_score": current_report.get("stress", {}).get("score", 0),
            "burnout_risk": current_report.get("metrics", {}).get("prediction", {}).get("burnout_risk", 0),
            "fatigue_index": current_report.get("cv_metrics", {}).get("fatigue_index", 0),
            "attention_score": current_report.get("cv_metrics", {}).get("attention_score", 100),
            "engagement_score": current_report.get("cv_metrics", {}).get("engagement_score", 100),
            "top_risk_factors": top_risk_factors,
            "recent_events": current_report.get("recent_events", []),
            "session_summary": current_report.get("session_summary", {}),
            "prediction": current_report.get("metrics", {}).get("prediction", {}),
            "analytics_summary": analytics_summary
        }
        
        try:
            with open(self.latest_context_file, "w") as f:
                json.dump(llm_context, f, indent=4)
        except Exception as e:
            print(f"ContextBuilder: Error writing latest_context.json: {e}", flush=True)

        return llm_context
