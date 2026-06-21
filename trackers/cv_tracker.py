import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import threading
from collections import deque
import urllib.request
import os

class CVTracker:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.running = False
        
        # Download task model if it doesn't exist
        self.model_path = 'face_landmarker.task'
        if not os.path.exists(self.model_path):
            print("CVTracker: Downloading face_landmarker model...", flush=True)
            url = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
            urllib.request.urlretrieve(url, self.model_path)
        
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
        
        # Data stores
        self.blink_timestamps = deque(maxlen=200)
        self.yawn_timestamps = deque(maxlen=50)
        self.nose_positions = deque(maxlen=300) # For head stability
        
        # New stores/states for advanced metrics
        self.mood_history = deque(maxlen=120)
        self.last_nose_pos = None
        self.head_speeds = deque(maxlen=100)
        self.look_away_start_time = None
        self.look_away_duration = 0.0
        self._last_process_time = time.time()
        
        # State
        self.eyes_closed = False
        self.yawning = False
        self.face_detected_count = 0
        self.total_frames = 0
        
        # Metrics to return
        self.metrics = {
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
            "mouth_aspect_ratio": 0.0
        }
        
        self.lock = threading.Lock()
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        
    def _run_loop(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("CVTracker: Warning - Camera could not be opened.")
            return
            
        while self.running:
            success, image = cap.read()
            if not success:
                time.sleep(0.1)
                continue
                
            # Process strictly in memory and discard
            self._process_frame(image)
            
            # Rate limit processing to ~10-15 fps to save CPU
            time.sleep(0.05)
            
        cap.release()
        
    def _process_frame(self, image):
        h, w, _ = image.shape
        self.total_frames += 1
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        detection_result = self.face_landmarker.detect(mp_image)
        
        with self.lock:
            current_time = time.time()
            dt = current_time - self._last_process_time
            self._last_process_time = current_time
            if dt <= 0:
                dt = 0.05
                
            if not detection_result.face_landmarks:
                self.metrics["face_present"] = False
                self._update_presence()
                if self.look_away_start_time is None:
                    self.look_away_start_time = current_time
                self.look_away_duration = current_time - self.look_away_start_time
                
                self.metrics["focused"] = False
                attention_penalty = min(80, int(self.look_away_duration * 5))
                self.metrics["attention_score"] = int(max(0, 100 - attention_penalty))
                self.metrics["engagement_score"] = 0
                self.metrics["engagement_index"] = 0
                return
                
            self.face_detected_count += 1
            self.metrics["face_present"] = True
            self._update_presence()
            
            landmarks = detection_result.face_landmarks[0]
            
            def get_pt(idx):
                return np.array([landmarks[idx].x * w, landmarks[idx].y * h])
                
            left_eye_center = (get_pt(33) + get_pt(133)) / 2.0
            right_eye_center = (get_pt(362) + get_pt(263)) / 2.0
            iod = np.linalg.norm(left_eye_center - right_eye_center)
            if iod == 0:
                iod = 1e-6
                
            # --- Eye Aspect Ratio (EAR) ---
            def get_ear(eye_indices):
                p1 = get_pt(eye_indices[0])
                p2 = get_pt(eye_indices[1])
                p3 = get_pt(eye_indices[2])
                p4 = get_pt(eye_indices[3])
                p5 = get_pt(eye_indices[4])
                p6 = get_pt(eye_indices[5])
                
                v1 = np.linalg.norm(p2 - p6)
                v2 = np.linalg.norm(p3 - p5)
                h1 = np.linalg.norm(p1 - p4)
                
                if h1 == 0: return 0
                return (v1 + v2) / (2.0 * h1)
                
            left_ear = get_ear([33, 160, 158, 133, 153, 144])
            right_ear = get_ear([362, 385, 387, 263, 373, 380])
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Blink logic
            if avg_ear < 0.22:
                if not self.eyes_closed:
                    self.eyes_closed = True
            else:
                if self.eyes_closed:
                    self.eyes_closed = False
                    self.blink_timestamps.append(time.time())
                    
            # --- Yawning (Mouth Aspect Ratio) ---
            p_top = get_pt(13)
            p_bot = get_pt(14)
            p_left = get_pt(78)
            p_right = get_pt(308)
            
            mouth_w = np.linalg.norm(p_left - p_right)
            mouth_h = np.linalg.norm(p_top - p_bot)
            mar = mouth_h / mouth_w if mouth_w > 0 else 0
            self.metrics["mouth_aspect_ratio"] = round(mar, 3)
            
            if mar > 0.6:
                if not self.yawning:
                    self.yawning = True
                    self.yawn_timestamps.append(time.time())
            else:
                self.yawning = False
                
            # --- Head Orientation / Attention ---
            nose = landmarks[1]
            left_eye_outer = landmarks[33]
            right_eye_outer = landmarks[263]
            
            yaw_ratio = (nose.x - left_eye_outer.x) / (right_eye_outer.x - left_eye_outer.x + 1e-6)
            yaw_deviation = abs(0.5 - yaw_ratio)
            focused = yaw_deviation < 0.3
            self.metrics["focused"] = focused
            
            if not focused:
                if self.look_away_start_time is None:
                    self.look_away_start_time = current_time
                self.look_away_duration = current_time - self.look_away_start_time
            else:
                self.look_away_start_time = None
                self.look_away_duration = 0.0
                
            base_attention = max(0, 100 - (yaw_deviation * 200))
            attention_penalty = 0
            if self.look_away_duration > 2.0:
                attention_penalty = min(80, (self.look_away_duration - 2.0) * 10)
            self.metrics["attention_score"] = int(max(0, base_attention - attention_penalty))
            
            # --- Screen Distance ---
            inter_ocular = np.linalg.norm(
                get_pt(159) - get_pt(386)
            )
            if inter_ocular > 0:
                dist_cm = (0.1 * w / inter_ocular) * 60
                dist_cm = np.clip(dist_cm, 20, 150)
            else:
                dist_cm = 60
            self.metrics["screen_distance_cm"] = round(dist_cm, 1)
            
            dist_risk = 0
            if dist_cm < 40: dist_risk = (40 - dist_cm) * 5
            elif dist_cm > 80: dist_risk = (dist_cm - 80) * 2
            self.metrics["distance_risk"] = min(100, int(dist_risk))
            
            # --- Head Stability ---
            self.nose_positions.append((nose.x * w, nose.y * h))
            if len(self.nose_positions) > 10:
                xs = [p[0] for p in self.nose_positions]
                ys = [p[1] for p in self.nose_positions]
                variance = np.var(xs) + np.var(ys)
                stability = max(0, 100 - (variance / 5))
                self.metrics["head_stability_score"] = int(stability)
                
            # --- Posture ---
            eye_diff_y = right_eye_center[1] - left_eye_center[1]
            eye_diff_x = right_eye_center[0] - left_eye_center[0]
            roll_angle = np.degrees(np.arctan2(eye_diff_y, eye_diff_x))
            self.metrics["head_tilt"] = round(roll_angle, 1)
            
            face_y = (nose.y + landmarks[159].y + landmarks[386].y) / 3.0
            slouch = face_y > 0.6
            self.metrics["slouch_detected"] = bool(slouch)
            
            posture_penalty = abs(roll_angle) * 2 + (20 if slouch else 0)
            self.metrics["posture_score"] = int(max(0, 100 - posture_penalty))

            # --- ADVANCED METRICS ---

            # 1. Brow Furrowing
            dist_brows = np.linalg.norm(get_pt(107) - get_pt(336)) / iod
            furrow_val = np.clip((0.85 - dist_brows) / 0.15, 0, 1)

            # 2. Eyebrow Compression
            left_brow_height = np.linalg.norm(get_pt(105) - left_eye_center) / iod
            right_brow_height = np.linalg.norm(get_pt(334) - right_eye_center) / iod
            avg_brow_height = (left_brow_height + right_brow_height) / 2.0
            compress_val = np.clip((0.55 - avg_brow_height) / 0.09, 0, 1)

            # 3. Lip Tightening
            mouth_w_norm = mouth_w / iod
            mouth_h_norm = mouth_h / iod
            lip_tight_val = np.clip((0.07 - mouth_h_norm) / 0.04, 0, 1) * np.clip((0.75 - mouth_w_norm) / 0.15, 0, 1)

            # 4. Jaw Tension
            nose_to_chin = np.linalg.norm(get_pt(1) - get_pt(152)) / iod
            jaw_tension_val = np.clip((1.42 - nose_to_chin) / 0.08, 0, 1)

            # 5. Rapid Head Movement
            current_nose_pos = get_pt(1)
            rapid_head_val = 0.0
            if self.last_nose_pos is not None:
                speed = np.linalg.norm(current_nose_pos - self.last_nose_pos) / (dt + 1e-6) / iod
                self.head_speeds.append(speed)
                mean_speed = np.mean(self.head_speeds)
                rapid_head_val = np.clip((mean_speed - 0.4) / 1.6, 0, 1)
            self.last_nose_pos = current_nose_pos

            # --- Frustration Score ---
            frust_score = (furrow_val * 0.3 + compress_val * 0.2 + lip_tight_val * 0.2 + jaw_tension_val * 0.15 + rapid_head_val * 0.15) * 100
            self.metrics["frustration_score"] = int(np.clip(frust_score, 0, 100))

            # --- Stress Expression Score ---
            squint_val = 0.0
            if avg_ear >= 0.22 and avg_ear < 0.26:
                squint_val = np.clip((0.26 - avg_ear) / 0.04, 0, 1)
            
            forehead_tension_val = max(furrow_val, np.clip((avg_brow_height - 0.55) / 0.10, 0, 1))

            brow_asym = abs(left_brow_height - right_brow_height) / (avg_brow_height + 1e-6)
            mouth_asym = abs(get_pt(61)[1] - get_pt(291)[1]) / iod
            asymmetry_val = np.clip((brow_asym + mouth_asym) / 0.35, 0, 1)

            facial_tension = (furrow_val + lip_tight_val + jaw_tension_val) / 3.0
            stress_expr_score = (facial_tension * 0.3 + squint_val * 0.3 + forehead_tension_val * 0.2 + asymmetry_val * 0.2) * 100
            self.metrics["stress_expression_score"] = int(np.clip(stress_expr_score, 0, 100))

            # --- Emotional Valence ---
            mouth_corners_y = (get_pt(61)[1] + get_pt(291)[1]) / 2.0
            smile_diff = (p_top[1] - mouth_corners_y) / iod
            
            if smile_diff > -0.01 and mar < 0.2:
                self.metrics["emotional_valence"] = "Positive"
            elif self.metrics["frustration_score"] > 35 or self.metrics["stress_expression_score"] > 40 or smile_diff < -0.07:
                self.metrics["emotional_valence"] = "Negative"
            else:
                self.metrics["emotional_valence"] = "Neutral"

            # --- Eye Focus ---
            eye_focus = 100
            if len(landmarks) > 468:
                left_iris = get_pt(468)
                right_iris = get_pt(473)
                left_eye_center_raw = (get_pt(33) + get_pt(133)) / 2.0
                right_eye_center_raw = (get_pt(362) + get_pt(263)) / 2.0
                left_iris_offset = np.linalg.norm(left_iris - left_eye_center_raw) / iod
                right_iris_offset = np.linalg.norm(right_iris - right_eye_center_raw) / iod
                avg_iris_offset = (left_iris_offset + right_iris_offset) / 2.0
                eye_focus = max(0, 100 - int(np.clip((avg_iris_offset - 0.05) / 0.08, 0, 1) * 100))
            else:
                eye_focus = 100 if focused else 40
            self.metrics["eye_focus"] = eye_focus

    def _update_presence(self):
        if self.total_frames > 0:
            pct = (self.face_detected_count / self.total_frames) * 100
            self.metrics["presence_percentage"] = round(pct, 1)

    def _cleanup_old_events(self):
        now = time.time()
        while self.blink_timestamps and now - self.blink_timestamps[0] > 60:
            self.blink_timestamps.popleft()
        while self.yawn_timestamps and now - self.yawn_timestamps[0] > 600:
            self.yawn_timestamps.popleft()

    def get_metrics(self, keyboard=None, window=None, session=None):
        with self.lock:
            self._cleanup_old_events()
            
            blinks = len(self.blink_timestamps)
            yawns = len(self.yawn_timestamps)
            
            self.metrics["blink_rate"] = blinks
            self.metrics["yawn_count"] = yawns
            
            eye_fatigue = 0
            if blinks < 8: eye_fatigue = (8 - blinks) * 10
            elif blinks > 25: eye_fatigue = (blinks - 25) * 5
            self.metrics["eye_fatigue_score"] = min(100, eye_fatigue)
            
            # --- Fatigue Index ---
            session_minutes = 0.0
            if session is not None:
                session_minutes = session.get("session_minutes", 0.0)
            session_duration_factor = min(100.0, session_minutes * 2.0)
            
            posture_penalty = 100 - self.metrics["posture_score"]
            blink_rate_factor = min(100.0, blinks * 4)
            yawn_factor = min(100.0, yawns * 25)
            
            fatigue = (self.metrics["eye_fatigue_score"] * 0.25) + \
                      (yawn_factor * 0.25) + \
                      (posture_penalty * 0.2) + \
                      (session_duration_factor * 0.15) + \
                      (blink_rate_factor * 0.15)
            self.metrics["fatigue_index"] = min(100, int(fatigue))
            
            # --- Engagement Score ---
            self.metrics["engagement_score"] = int(np.clip(
                self.metrics["presence_percentage"] * 0.2 +
                self.metrics["attention_score"] * 0.4 +
                self.metrics["head_stability_score"] * 0.2 +
                self.metrics.get("eye_focus", 100) * 0.2,
                0, 100
            ))
            self.metrics["engagement_index"] = self.metrics["engagement_score"]
            
            # --- Cognitive Overload Score ---
            window_switches = 0
            if window is not None:
                window_switches = window.get("window_switches", 0)
            window_switches_factor = min(100.0, window_switches * 10)
            
            typing_variance = 0.0
            if keyboard is not None:
                typing_variance = keyboard.get("typing_variance", 0.0)
            typing_variance_factor = min(100.0, typing_variance * 20)
            
            attention_instability = 100 - self.metrics["attention_score"]
            
            cog_overload = (window_switches_factor * 0.2) + \
                           (typing_variance_factor * 0.2) + \
                           (self.metrics["eye_fatigue_score"] * 0.2) + \
                           (self.metrics["frustration_score"] * 0.2) + \
                           (attention_instability * 0.2)
            self.metrics["cognitive_overload_score"] = min(100, int(cog_overload))
            
            # --- Wellness Score ---
            well = (self.metrics["posture_score"] * 0.25) + \
                   (self.metrics["attention_score"] * 0.2) + \
                   (self.metrics["engagement_score"] * 0.25) + \
                   ((100 - self.metrics["fatigue_index"]) * 0.15) + \
                   ((100 - self.metrics["frustration_score"]) * 0.15)
            self.metrics["wellness_score"] = min(100, int(well))
            
            # --- Mood Trend ---
            mood_point = self.metrics["wellness_score"] - self.metrics["frustration_score"] * 0.5
            self.mood_history.append(mood_point)
            
            if len(self.mood_history) >= 10:
                half = len(self.mood_history) // 2
                first_half = list(self.mood_history)[:half]
                second_half = list(self.mood_history)[half:]
                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)
                diff = avg_second - avg_first
                if diff > 2.0:
                    self.metrics["mood_trend"] = "Improving"
                elif diff < -2.0:
                    self.metrics["mood_trend"] = "Declining"
                else:
                    self.metrics["mood_trend"] = "Stable"
            else:
                self.metrics["mood_trend"] = "Stable"
                
            return self.metrics.copy()

