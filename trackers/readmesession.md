# Synapse Session Tracker

## Purpose

Tracks work duration and recovery behavior.

The Session Tracker estimates:

- Work Session Length
- Break Frequency
- Recovery Debt
- Fatigue Risk

---

## Metrics

### Session Minutes

Total time since session start.

Example:

{
    "session_minutes": 120
}

Meaning:

User has been working for 2 hours.

---

### Break Count

Number of breaks taken.

Example:

{
    "break_count": 3
}

Meaning:

User has taken 3 breaks.

---

### Time Since Last Break

Minutes elapsed since most recent break.

Example:

{
    "time_since_last_break": 45
}

Meaning:

User has not taken a break for 45 minutes.

---

## Why It Matters

Long sessions with few breaks often correlate with:

- Mental Fatigue
- Burnout Risk
- Reduced Focus
- Poor Decision Making

---

## Future Usage

These metrics contribute to:

- Fatigue Score
- Recovery Debt Score
- Cognitive Load Score