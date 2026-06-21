import cv2
import numpy as np
import time
import threading
from scipy.signal import butter, filtfilt, find_peaks

class RPPGEngine:
    def __init__(self):
        self.running = False
        self.hr = 0.0
        self.rmssd = 0.0
        self.lock = threading.Lock()
        
        # We need a buffer of green channel values to perform signal processing
        # Assuming ~30 fps, 300 frames is ~10 seconds of data.
        self.buffer_size = 300
        self.green_signal = []
        self.timestamps = []
        
        # OpenCV face cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def get_state(self):
        with self.lock:
            return {"hr": self.hr, "rmssd": self.rmssd}

    def _run_loop(self):
        cap = cv2.VideoCapture(0)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                # Use the largest face
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                x, y, w, h = faces[0]

                # Extract Forehead ROI (approx top 20% of face, centered)
                fh_x = x + int(w * 0.25)
                fh_w = int(w * 0.5)
                fh_y = y + int(h * 0.05)
                fh_h = int(h * 0.15)

                if fh_h > 0 and fh_w > 0:
                    forehead_roi = frame[fh_y:fh_y+fh_h, fh_x:fh_x+fh_w]
                    
                    # Calculate mean of green channel
                    green_channel = forehead_roi[:, :, 1]
                    green_mean = np.mean(green_channel)
                    
                    current_time = time.time()
                    
                    self.green_signal.append(green_mean)
                    self.timestamps.append(current_time)
                    
                    if len(self.green_signal) > self.buffer_size:
                        self.green_signal.pop(0)
                        self.timestamps.pop(0)
                        
                    # Process signal if buffer is full enough (e.g. > 150 frames, ~5 secs)
                    if len(self.green_signal) >= 150:
                        self._process_signal()

            # Small sleep to limit cpu usage if running too fast, but we want high fps
            time.sleep(0.01)

        cap.release()

    def _process_signal(self):
        # Ensure uniform sampling (interpolation could be used, but for simplicity assuming roughly uniform fps)
        times = np.array(self.timestamps)
        signal = np.array(self.green_signal)
        
        # Calculate approximate fps
        duration = times[-1] - times[0]
        if duration <= 0:
            return
            
        fps = len(times) / duration
        
        if fps < 10:
            return # Too low frame rate for reliable heart rate
            
        # Bandpass filter (0.75 Hz to 2.5 Hz = 45 to 150 BPM)
        nyq = 0.5 * fps
        low = 0.75 / nyq
        high = 2.5 / nyq
        
        # Edge case: if high > 1, adjust
        if high >= 1.0:
            high = 0.99
            
        try:
            b, a = butter(3, [low, high], btype='band')
            filtered = filtfilt(b, a, signal)
            
            # Find peaks (heart beats)
            # Distance between peaks should be at least (fps * 0.4) = ~2.5Hz max HR
            peaks, _ = find_peaks(filtered, distance=int(fps * 0.4))
            
            if len(peaks) > 1:
                # Calculate Inter-Beat Intervals (IBI) in seconds
                peak_times = times[peaks]
                ibis = np.diff(peak_times)
                
                # HR in bpm
                avg_ibi = np.mean(ibis)
                if avg_ibi > 0:
                    current_hr = 60.0 / avg_ibi
                else:
                    current_hr = 0
                    
                # RMSSD (Root Mean Square of Successive Differences) in milliseconds
                # IBI is in seconds, so convert diff to ms
                diff_ibis = np.diff(ibis) * 1000 
                if len(diff_ibis) > 0:
                    current_rmssd = np.sqrt(np.mean(diff_ibis**2))
                else:
                    current_rmssd = 0.0
                
                # Smoothing
                with self.lock:
                    if self.hr == 0:
                        self.hr = current_hr
                        self.rmssd = current_rmssd
                    else:
                        # Exponential moving average for stability
                        self.hr = 0.8 * self.hr + 0.2 * current_hr
                        self.rmssd = 0.8 * self.rmssd + 0.2 * current_rmssd

        except Exception as e:
            # SciPy filter can fail if buffer is too small or invalid params
            pass

# Global singleton
rppg_engine = RPPGEngine()
