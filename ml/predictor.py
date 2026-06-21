import torch
import os
import numpy as np
from ml.models.lstm_model import CognitivePredictorLSTM
from ml.dataset_builder import DatasetBuilder, FEATURE_COLUMNS
from ml.feature_store import FeatureStore

class Predictor:
    def __init__(self):
        self.feature_store = FeatureStore()
        self.dataset_builder = DatasetBuilder()
        
        self.input_dim = len(FEATURE_COLUMNS)
        self.model_path = "ml/weights/cognitive_lstm.pt"
        
        self.model = CognitivePredictorLSTM(input_dim=self.input_dim)
        self.model_loaded = False
        self._load_model()
        
        # Dummy feature importances (in a real scenario, could use SHAP or integrated gradients)
        # We simulate feature importance by correlating recent variance with stress
        self.feature_names = FEATURE_COLUMNS

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model.load_state_dict(torch.load(self.model_path))
                self.model.eval()
                self.model_loaded = True
            except Exception as e:
                print(f"Predictor: Failed to load model weights: {e}", flush=True)
                self.model_loaded = False
        else:
            self.model_loaded = False

    def get_feature_importance(self, df):
        """Approximates top contributing factors."""
        if len(df) < 10:
            return ["Insufficient data for analysis"]
            
        recent = df.tail(10)
        factors = []
        
        if recent['typing_variance'].mean() > 1.5:
            factors.append("Typing Variance Increase")
        if recent['attention_score'].mean() < 80:
            factors.append("Attention Decline")
        if recent['window_switches'].mean() > 5:
            factors.append("High Window Switching")
        if recent['posture_score'].mean() < 70:
            factors.append("Poor Posture Detected")
        if recent['fatigue_index'].mean() > 40:
            factors.append("Elevated Fatigue")
            
        if not factors:
            factors.append("Normal Activity Levels")
            
        return factors[:3]

    def _baseline_heuristic_prediction(self, df):
        """Fallback rule-based prediction if model is not trained yet."""
        if len(df) == 0:
            return {
                "predicted_stress_15m": 0,
                "predicted_stress_30m": 0,
                "burnout_risk": 0,
                "risk_level": "LOW",
                "confidence": 0,
                "top_factors": ["Warming up (Need more data)"],
                "model_status": "Untrained"
            }
            
        current_stress = df['current_stress_score'].iloc[-1]
        trend = 0
        if len(df) > 10:
            trend = current_stress - df['current_stress_score'].iloc[-10]
            
        pred_15 = min(100, max(0, current_stress + trend * 1.5))
        pred_30 = min(100, max(0, current_stress + trend * 3.0))
        
        b_risk = int(min(100, (pred_30 / 100.0) * 80 + (df['fatigue_index'].iloc[-1] / 100.0) * 20))
        
        level = "LOW"
        if b_risk > 75: level = "CRITICAL"
        elif b_risk > 60: level = "HIGH"
        elif b_risk > 40: level = "MODERATE"
        
        return {
            "predicted_stress_15m": int(pred_15),
            "predicted_stress_30m": int(pred_30),
            "burnout_risk": b_risk,
            "risk_level": level,
            "confidence": 45, # Low confidence for heuristic
            "top_factors": self.get_feature_importance(df),
            "model_status": "Baseline Heuristic"
        }

    def predict_live_risk(self):
        """Main inference function called by backend loop."""
        # Need 30 minutes of history for a full sequence
        df = self.feature_store.get_recent_history(minutes=30)
        
        # If we don't have enough data or model isn't trained, use heuristic
        if not self.model_loaded or len(df) < 5: 
            return self._baseline_heuristic_prediction(df)
            
        try:
            # 1. Prepare sequence
            seq_tensor = self.dataset_builder.prepare_inference_sequence(df)
            
            # 2. Forward pass
            with torch.no_grad():
                pred_15, pred_30, b_risk = self.model(seq_tensor)
                
            p15 = int(pred_15.item())
            p30 = int(pred_30.item())
            br = int(b_risk.item() * 100)
            
            # Clamp values
            p15 = max(0, min(100, p15))
            p30 = max(0, min(100, p30))
            br = max(0, min(100, br))
            
            # Determine risk level
            level = "LOW"
            if br > 75: level = "CRITICAL"
            elif br > 60: level = "HIGH"
            elif br > 40: level = "MODERATE"
            
            # Confidence grows as we get closer to 30 mins of data
            data_ratio = min(1.0, len(df) / 360.0)
            confidence = int(80 * data_ratio + 10)
            
            return {
                "predicted_stress_15m": p15,
                "predicted_stress_30m": p30,
                "burnout_risk": br,
                "risk_level": level,
                "confidence": confidence,
                "top_factors": self.get_feature_importance(df),
                "model_status": "LSTM Active"
            }
            
        except Exception as e:
            print(f"Predictor Error: {e}", flush=True)
            return self._baseline_heuristic_prediction(df)
