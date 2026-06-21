# Synapse Window Tracker

## Purpose

The Window Tracker monitors the user's active application and measures context switching behavior.

This tracker helps estimate:

- Focus
- Attention Stability
- Context Switching
- Cognitive Load

The idea is simple:

Frequent switching between applications often indicates reduced focus and increased mental overhead.

---

## Metrics Generated

### 1. Active Window

Definition:

The title of the application currently in focus.

Examples:

- Visual Studio Code
- Google Chrome
- File Explorer
- Spotify

Example Output:

```python
{
    "active_window": "Visual Studio Code"
}
```

---

### 2. Window Switches

Definition:

Number of times the active application changes during the last 60 seconds.

Example:

Visual Studio Code
→ Chrome
→ VS Code
→ Explorer

Window Switches = 3

Example Output:

```python
{
    "window_switches": 3
}
```

---

## Rolling Window Logic

The tracker only keeps switch events from the most recent 60 seconds.

Older events are automatically removed.

This ensures metrics always represent the user's current behavior.

---

## Why Window Switching Matters

### Low Switching

Example:

VS Code
VS Code
VS Code
VS Code

Interpretation:

- Deep Work
- High Concentration
- Stable Focus

---

### High Switching

Example:

VS Code
→ Chrome
→ Stack Overflow
→ Chrome
→ VS Code
→ YouTube

Interpretation:

- Task Fragmentation
- Reduced Focus
- Increased Cognitive Load

---

## Example Output

```python
{
    "active_window": "Google Chrome",
    "window_switches": 7
}
```

---

## Future Usage

The Window Tracker does not calculate scores directly.

These metrics will later contribute to:

### Focus Score

Higher window switches
→ Lower Focus

---

### Cognitive Load Score

Frequent context switching
→ Increased Mental Overhead

---

## Technical Implementation

Libraries:

- pygetwindow
- pywin32

Polling Frequency:

- Once per second

Storage:

- Rolling 60-second event window

Output Format:

```python
{
    "active_window": str,
    "window_switches": int
}
```

---

## Current Status

Implemented Features:

✅ Active window detection

✅ Window switch counting

✅ Rolling 60-second tracking

Future Enhancements:

- Categorize applications
- Productive vs Distracting app detection
- Focus Session Analysis
- Team Productivity Insights