import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import os
import joblib

FEATURE_COLUMNS = [
    "keys_per_min", "backspaces_per_min", "avg_pause", "typing_variance",
    "click_rate", "movement_distance", "mouse_speed",
    "window_switches",
    "session_duration", "break_count",
    "attention_score", "frustration_score", "fatigue_index", 
    "posture_score", "engagement_score", "blink_rate", "yawn_count"
]

class CognitiveDataset(Dataset):
    def __init__(self, sequences, targets_15m, targets_30m, burnout_targets):
        self.sequences = torch.FloatTensor(sequences)
        self.targets_15m = torch.FloatTensor(targets_15m).unsqueeze(1)
        self.targets_30m = torch.FloatTensor(targets_30m).unsqueeze(1)
        self.burnout_targets = torch.FloatTensor(burnout_targets).unsqueeze(1)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return self.sequences[idx], self.targets_15m[idx], self.targets_30m[idx], self.burnout_targets[idx]

class DatasetBuilder:
    def __init__(self, seq_length=360, scaler_path="ml/weights/scaler.pkl"):
        # 360 timesteps = 30 minutes at 5s sampling
        self.seq_length = seq_length
        self.scaler_path = scaler_path
        self.scaler = StandardScaler()
        
        # We need to know how many steps ahead to look for our targets
        # 15 minutes = 15 * 60 = 900 seconds. At 5s intervals, that is 180 steps.
        self.lookahead_15m = 180
        # 30 minutes = 30 * 60 = 1800 seconds. At 5s intervals, that is 360 steps.
        self.lookahead_30m = 360

    def build_training_data(self, df):
        """
        Takes a Pandas DataFrame of historical metrics and creates sequences and targets.
        """
        if len(df) < self.seq_length + self.lookahead_30m:
            return None, None, None, None # Not enough data
            
        # Ensure timestamp is datetime and sort
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Fill missing values with 0 or forward fill
        df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(method='ffill').fillna(0)
        
        # Extract features and scale them
        features_array = df[FEATURE_COLUMNS].values
        features_scaled = self.scaler.fit_transform(features_array)
        
        # Save scaler for inference
        os.makedirs(os.path.dirname(os.path.abspath(self.scaler_path)), exist_ok=True)
        joblib.dump(self.scaler, self.scaler_path)
        
        stress_array = df['current_stress_score'].values
        
        sequences = []
        targets_15m = []
        targets_30m = []
        burnout_targets = []
        
        # Create sliding windows
        for i in range(len(df) - self.seq_length - self.lookahead_30m):
            # Sequence from i to i + seq_length
            seq = features_scaled[i : i + self.seq_length]
            
            # Targets in the future
            t_15m = stress_array[i + self.seq_length + self.lookahead_15m - 1]
            t_30m = stress_array[i + self.seq_length + self.lookahead_30m - 1]
            
            # Calculate burnout target (if future stress is consistently high)
            # We approximate burnout risk as the moving average of stress in the 15m-30m window
            future_stress_window = stress_array[i + self.seq_length : i + self.seq_length + self.lookahead_30m]
            avg_future_stress = np.mean(future_stress_window)
            b_risk = 1.0 if avg_future_stress > 70 else (avg_future_stress / 70.0)
            
            sequences.append(seq)
            targets_15m.append(t_15m)
            targets_30m.append(t_30m)
            burnout_targets.append(b_risk)
            
        return np.array(sequences), np.array(targets_15m), np.array(targets_30m), np.array(burnout_targets)
        
    def prepare_inference_sequence(self, df):
        """
        Takes the most recent rows and creates a single sequence for live inference.
        Returns tensor of shape (1, seq_length, num_features).
        """
        # If we have less data than required, we pad with zeros
        df_len = len(df)
        
        df = df.copy()
        df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(method='ffill').fillna(0)
        
        if os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)
            features = self.scaler.transform(df[FEATURE_COLUMNS].values)
        else:
            # Fallback if no scaler exists (not trained yet)
            features = df[FEATURE_COLUMNS].values
            
        if df_len < self.seq_length:
            # Pad with zeros at the beginning
            pad_len = self.seq_length - df_len
            padding = np.zeros((pad_len, len(FEATURE_COLUMNS)))
            seq = np.vstack([padding, features])
        else:
            # Take the last seq_length rows
            seq = features[-self.seq_length:]
            
        # Add batch dimension
        seq_tensor = torch.FloatTensor(seq).unsqueeze(0)
        return seq_tensor
