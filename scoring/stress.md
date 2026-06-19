# Synapse Stress Engine

## Purpose

The Stress Engine converts raw behavioral signals into a human-readable stress score.

Rather than relying on surveys or manual input, Synapse estimates stress using real-time interaction patterns collected from:

- Keyboard Activity
- Mouse Activity
- Window Switching Behavior
- Session Duration

The output is:

```python
{
    "stress_score": 67.3,
    "stress_level": "High Stress"
}
```

---

## Architecture

Keyboard Tracker
Mouse Tracker
Window Tracker
Session Metrics
        ↓
Metrics Aggregator
        ↓
Stress Engine
        ↓
Stress Score

---

## Inputs

### Keyboard Metrics

```python
{
    "keys_per_min": 72,
    "backspaces_per_min": 11,
    "avg_pause": 1.2,
    "typing_variance": 1.4
}
```

Signals:

- Frequent corrections
- Hesitation
- Irregular typing rhythm

---

### Mouse Metrics

```python
{
    "click_rate": 24,
    "mouse_speed": 180
}
```

Signals:

- Excessive clicking
- Restlessness
- Frustration

---

### Window Metrics

```python
{
    "window_switches": 8
}
```

Signals:

- Context switching
- Multitasking
- Cognitive overload

---

### Session Metrics

```python
{
    "session_minutes": 120,
    "break_count": 0
}
```

Signals:

- Fatigue
- Mental exhaustion
- Recovery debt

---

## Stress Calculation

The Stress Engine uses a weighted scoring approach.

### Typing Stress

Factors:

- Backspaces Per Minute
- Typing Variance
- Average Pause

Formula:

```python
typing_score =
min(backspaces_per_min * 2, 25)
+
min(typing_variance * 10, 25)
+
min(avg_pause * 5, 20)
```

Maximum Contribution:

```text
70 Points
```

---

### Context Switching Stress

Factor:

- Window Switches

Formula:

```python
context_score =
min(window_switches * 5, 20)
```

Maximum Contribution:

```text
20 Points
```

---

### Mouse Frustration Stress

Factor:

- Click Rate

Formula:

```python
mouse_score =
min(click_rate * 1.5, 20)
```

Maximum Contribution:

```text
20 Points
```

---

### Fatigue Stress

Factor:

- Session Duration

Formula:

```python
fatigue_score =
min(session_minutes / 5, 20)
```

Maximum Contribution:

```text
20 Points
```

---

## Final Score

Formula:

```python
stress_score =
typing_score
+
context_score
+
mouse_score
+
fatigue_score
```

Normalization:

```python
stress_score = min(stress_score, 100)
```

Final Range:

```text
0 → 100
```

---

## Stress Classification

### Relaxed

```text
0 - 25
```

Characteristics:

- Stable typing
- Few corrections
- Low context switching

---

### Mild Stress

```text
26 - 50
```

Characteristics:

- Increased workload
- Occasional interruptions

---

### High Stress

```text
51 - 75
```

Characteristics:

- Frequent switching
- High correction rate
- Noticeable fatigue

---

### Critical Stress

```text
76 - 100
```

Characteristics:

- Strong signs of overload
- High multitasking
- Extended work sessions

---

## Example Output

```python
{
    "stress_score": 68.4,
    "stress_level": "High Stress"
}
```

---

## Explainable AI Output

The engine can also return individual contributors.

Example:

```python
{
    "stress_score": 68.4,

    "stress_level": "High Stress",

    "contributors": {

        "typing": 28.5,

        "mouse": 12.0,

        "context_switching": 18.0,

        "fatigue": 9.9
    }
}
```

This makes the system transparent and easy to explain during demonstrations.

---

## Current Limitations

Current Version:

- Rule-Based Scoring
- No Machine Learning
- No Computer Vision Signals

---

## Future Enhancements

Planned Features:

- Blink Rate Analysis
- Posture Analysis
- Gaze Tracking
- Facial Fatigue Detection
- Machine Learning Personalization
- Historical Trend Analysis
- Team-Level Stress Analytics

---

## Why This Approach?

For a hackathon environment:

- Fast to implement
- Easy to explain
- Deterministic
- Transparent
- No training data required

This allows Synapse to produce meaningful stress estimates using only user interaction behavior.