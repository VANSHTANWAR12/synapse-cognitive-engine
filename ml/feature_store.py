import sqlite3
import os
import json
from datetime import datetime, timedelta
import pandas as pd

class FeatureStore:
    def __init__(self, db_path="ml/feature_store.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                -- Keyboard
                keys_per_min REAL,
                backspaces_per_min REAL,
                avg_pause REAL,
                typing_variance REAL,
                
                -- Mouse
                click_rate REAL,
                movement_distance REAL,
                mouse_speed REAL,
                
                -- Window
                window_switches INTEGER,
                
                -- Session
                session_duration REAL,
                break_count INTEGER,
                
                -- CV
                attention_score REAL,
                frustration_score REAL,
                fatigue_index REAL,
                posture_score REAL,
                engagement_score REAL,
                blink_rate REAL,
                yawn_count INTEGER,
                
                -- Target / Output
                current_stress_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def store(self, metrics, stress_score):
        keyboard = metrics.get("keyboard", {})
        mouse = metrics.get("mouse", {})
        window = metrics.get("window", {})
        session = metrics.get("session", {})
        cv = metrics.get("cv", {})
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (
                timestamp,
                keys_per_min, backspaces_per_min, avg_pause, typing_variance,
                click_rate, movement_distance, mouse_speed,
                window_switches,
                session_duration, break_count,
                attention_score, frustration_score, fatigue_index, posture_score, engagement_score, blink_rate, yawn_count,
                current_stress_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            keyboard.get("keys_per_min", 0), keyboard.get("backspaces_per_min", 0), keyboard.get("avg_pause", 0), keyboard.get("typing_variance", 0),
            mouse.get("click_rate", 0), mouse.get("movement_distance", 0), mouse.get("mouse_speed", 0),
            window.get("window_switches", 0),
            session.get("session_minutes", 0), session.get("break_count", 0),
            cv.get("attention_score", 100), cv.get("frustration_score", 0), cv.get("fatigue_index", 0), cv.get("posture_score", 100), cv.get("engagement_score", 100), cv.get("blink_rate", 0), cv.get("yawn_count", 0),
            stress_score
        ))
        
        conn.commit()
        conn.close()

    def get_recent_history(self, minutes=30):
        """Fetches the last N minutes of data as a Pandas DataFrame."""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        cutoff_str = cutoff_time.isoformat()
        
        query = f"""
            SELECT * FROM metrics 
            WHERE timestamp >= '{cutoff_str}'
            ORDER BY timestamp ASC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df

    def get_all_data(self):
        """Fetches all data for training purposes."""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM metrics ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_count(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM metrics")
        count = cursor.fetchone()[0]
        conn.close()
        return count
