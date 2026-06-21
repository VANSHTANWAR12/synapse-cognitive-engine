# Computer Vision: Advanced Workplace Wellness & Cognitive Analytics

This module enhances the Synapse Workforce Intelligence platform with real-time, non-intrusive **Computer Vision-based Emotional and Cognitive Analytics** to assess workplace wellness.

---

## 🔒 Privacy & Safety Guarantee

To protect user confidentiality, this module operates under strict privacy constraints:
- **NO Identity Recognition**: No facial recognition, profile matching, or identity tracking is performed.
- **NO Media Storage**: No camera frames, images, videos, or face embeddings are ever saved, stored, or transmitted.
- **NO Surveillance**: The camera stream is processed strictly in-memory and discarded frame-by-frame.
- **Anonymous Numerical Metrics Only**: Only generalized, high-level numerical wellness indicators are compiled.
- **No Clinical Diagnoses**: The system detects behavioral signs of frustration, strain, or fatigue, but does not classify clinical conditions (e.g., depression, anxiety, or mental illness).

---

## 🛠️ Technology Stack
- **OpenCV**: Handles camera input stream processing.
- **MediaPipe Face Mesh**: Detects and extracts normalized 3D landmarks for real-time facial expressions.
- **NumPy**: Performs high-performance geometric distance, aspect ratio, and variance calculations.
- *Strictly Dependency-Free*: No TensorFlow, No PyTorch, No YOLO required, guaranteeing lightweight, real-time performance on standard CPUs.

---

## 📊 Analytics & Metric Calculations

All distance metrics are normalized using the **Inter-Ocular Distance (IOD)** (distance between left and right eye centers) to ensure scale-invariance regardless of camera proximity.

### 1. Frustration Score (`0-100`)
Analyzes signs of frustration:
- **Brow Furrowing**: Calculated from the normalized distance between inner eyebrows (landmark 107 to 336).
- **Eyebrow Compression**: Lowering of the eyebrows towards the eyes (distance from middle eyebrows to eye centers).
- **Lip Tightening**: Measured by mouth aspect ratio (MAR) and horizontal mouth width compression when closed.
- **Jaw Tension**: Distance from the nose tip to chin (landmark 1 to 152).
- **Rapid Head Movement**: Velocity variance of the nose position across consecutive frames.

### 2. Stress Expression Score (`0-100`)
Measures physical markers of strain:
- **Facial Tension**: Combines brow furrowing, lip tightening, and jaw tension metrics.
- **Eye Strain (Squinting)**: Squinting patterns where the Eye Aspect Ratio (EAR) remains between 0.15 and 0.26 for prolonged periods (excluding blinks).
- **Forehead Tension**: Forehead furrowing and eyebrow raising deviations.
- **Facial Asymmetry**: Compares horizontal/vertical asymmetries in brow height or mouth corner pull.

### 3. Emotional Valence (`"Positive" | "Neutral" | "Negative"`)
Classifies the user's broad emotional valence category:
- **Positive**: Smiling metric based on mouth corners (landmarks 61 & 291) being elevated relative to the upper lip center (landmark 13).
- **Negative**: Frowning (downward mouth corner deviation) or elevated frustration (>35) and stress expression (>40) scores.
- **Neutral**: Standard workplace baseline state.

### 4. Engagement Score (`0-100`)
Synthesizes overall task participation:
- Combined from: **Face Presence** (20%), **Screen Attention** (40%), **Head Stability** (20%), and **Eye Focus / Gaze Centeredness** (20%).

### 5. Attention Score (`0-100`)
Assesses direct attention on the screen:
- Base attention score calculated from yaw/pitch head rotation.
- Accumulates a penalty if the user looks away from the screen for more than 2 seconds, reducing attention score.

### 6. Cognitive Overload Score (`0-100`)
Measures cognitive saturation by combining interaction and physiological indicators:
- **Window Switching Frequency** (20%)
- **Typing Pause Variance** (20%)
- **Eye Fatigue / Squinting** (20%)
- **Frustration Score** (20%)
- **Attention Instability** (20%)

### 7. Fatigue Index (`0-100`)
Identifies physical and mental fatigue:
- Combines: **Eye Fatigue** (25%), **Yawning Rate** (25%), **Poor Posture Penalty** (20%), **Session Work Duration** (15%), and **Blink Rate Deviation** (15%).

### 8. Mood Trend (`"Improving" | "Stable" | "Declining"`)
Maintains a rolling 10-minute queue of wellness metrics and calculates trend directions by taking the difference of averages between the first and second halves of the window.

### 9. Wellness Score (`0-100`)
An overall indicator of work wellness calculated from:
- **Posture Score** (25%), **Attention Score** (20%), **Engagement Score** (25%), **Fatigue-Free Index** (15%), and **Frustration-Free Index** (15%).

---

## ⚡ Stress Engine Integration

The stress score calculation has been updated to combine active user interaction and computer vision metrics into a unified `Stress Index (0-100)` based on 8 contributors:

```json
{
  "typing": 20,              // Typing pauses & corrections (max 20)
  "context_switching": 15,   // Application switching frequency (max 15)
  "mouse_activity": 10,      // click rate & movements (max 10)
  "fatigue": 12,             // CV-derived fatigue index (max 12)
  "posture": 8,              // CV-derived slouching/tilt (max 8)
  "attention": 7,            // CV-derived distraction penalty (max 7)
  "frustration": 10,         // CV-derived frustration score (max 10)
  "stress_expression": 8     // CV-derived facial strain (max 8)
}
```

---

## 🚨 Manager Alert System

Triggers warnings to support proactive management intervention:
- **LOW**: Wellness metrics are normal. Alert is inactive.
- **MODERATE**: One or more indicators are slightly elevated.
- **HIGH**: High frustration, cognitive overload, or prolonged work sessions detected.
- **CRITICAL**: Critical stress score (>80) or severe combined frustration & cognitive overload.

### Example Alert Output:
```json
{
  "alert": true,
  "severity": "HIGH",
  "reason": "Elevated frustration signals, high cognitive overload, and prolonged session duration detected."
}
```

---

## 💻 Dashboard Updates

The Synapse React Dashboard has been upgraded with a new **Workplace Wellness Analytics** dashboard containing:
1. **Manager Alert Panel**: Pulses with severity matching colors and details issues.
2. **6 Real-time circular gauges**: Displays Stress Level, Frustration, Cognitive Overload, Fatigue Index, Engagement, and Wellness.
3. **4 Trend Charts**: Real-time Area charts visualizing:
   - Stress Trend
   - Fatigue Trend
   - Frustration Trend
   - Wellness Trend
