# Synapse Mouse Tracker

## Purpose

The Mouse Tracker captures mouse activity and converts it into behavioral metrics used by the Synapse Cognitive Load Engine.

These metrics help estimate:

- Restlessness
- Frustration
- Activity level
- Cognitive load

---

## Metrics

### 1. Mouse Speed

Definition:

Average cursor movement speed over the last 60 seconds.

Formula:

mouse_speed =
movement_distance / 60

Example:

150 pixels/sec

Use Cases:

- Detect agitation
- Detect restless behavior

---

### 2. Click Rate

Definition:

Number of mouse clicks during the last 60 seconds.

Example:

25 clicks/min

Use Cases:

- Frustration detection
- Activity measurement

---

### 3. Movement Distance

Definition:

Total cursor travel distance during the last 60 seconds.

Example:

9000 pixels

Use Cases:

- User activity level
- Restlessness detection

---

## Rolling Window

The tracker only stores the most recent 60 seconds of data.

Old mouse events are automatically removed.

This ensures metrics represent current behavior.

---

## Example Output

```python
{
    "mouse_speed": 162.5,
    "click_rate": 18,
    "movement_distance": 9750.2
}
```

---

## Future Usage

These metrics will later contribute to:

- Frustration Score
- Focus Score
- Cognitive Load Score

They are not responsible for calculating scores directly.