# Synapse Keyboard Tracker

This module captures keyboard behavior and converts it into behavioral metrics used by the Synapse Cognitive Load Engine.

---

## Metrics Generated

### 1. Keys Per Minute

Measures typing activity over the last 60 seconds.

Example:

80 keys/min

Used for:
- Productivity estimation
- Focus analysis

---

### 2. Backspaces Per Minute

Counts correction attempts.

Example:

15 backspaces/min

Used for:
- Frustration estimation
- Struggle detection

---

### 3. Average Pause

Average time between consecutive key presses.

Example:

2.3 seconds

Used for:
- Cognitive load estimation
- Focus analysis

---

### 4. Long Pause Count

Counts pauses greater than 5 seconds.

Example:

4 long pauses

Used for:
- Detecting thinking blocks
- Detecting task difficulty

---

### 5. Typing Variance

Standard deviation of pause durations.

Example:

3.1

Used for:
- Measuring typing consistency
- Focus estimation

---

## Example Output

```python
{
    "keys_per_min": 72,
    "backspaces_per_min": 11,
    "avg_pause": 1.7,
    "long_pause_count": 3,
    "typing_variance": 2.5
}
```

---

## Interpretation

High Backspaces
+ High Long Pauses
+ High Typing Variance

⇒ Increased Frustration

High Keys Per Minute
+ Low Variance

⇒ High Focus

Low Activity
+ High Pause Duration

⇒ Possible Cognitive Overload