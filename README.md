# synapse-cognitive-engine
# 🧠 Synapse Workforce Intelligence

## Overview

Synapse Workforce Intelligence is a real-time cognitive stress monitoring platform designed to help organizations identify employee overload, fatigue, and productivity risks using behavioral analytics.

Instead of relying on surveys or manual reporting, Synapse continuously analyzes user interaction patterns such as typing behavior, mouse activity, window switching, and session duration to estimate cognitive stress levels.

The platform provides live analytics, stress scoring, contributor breakdowns, recommendations, and workforce insights through an enterprise dashboard.

---

# Problem Statement

Modern workplaces often struggle to identify employee burnout and cognitive overload before productivity declines.

Managers typically rely on subjective observations, delayed feedback, or self-reported surveys, making it difficult to intervene proactively.

Synapse addresses this challenge by providing a non-intrusive, real-time behavioral analytics system capable of detecting stress signals from everyday computer interactions.

---

# Key Features

### Real-Time Monitoring

Tracks user activity continuously while the employee works.

### Behavioral Analytics

Analyzes:

* Typing patterns
* Error correction frequency
* Mouse behavior
* Window switching frequency
* Session duration
* Break patterns

### Cognitive Stress Detection

Generates a live stress score ranging from:

```text
0 - 100
```

Stress Levels:

```text
0 - 25   → Relaxed
26 - 50  → Mild Stress
51 - 75  → High Stress
76 - 100 → Critical Stress
```

### Explainable AI

Displays contributor breakdowns explaining why a stress score was generated.

Example:

```json
{
  "typing": 24,
  "context_switching": 18,
  "mouse_activity": 12,
  "fatigue": 13
}
```

### Personalized Recommendations

Provides actionable recommendations such as:

* Take a break
* Reduce context switching
* Slow down and focus
* Continue current workflow

### Live Dashboard

Displays:

* Stress Score
* Stress Level
* Contributor Breakdown
* Stress Trends
* Productivity Metrics
* Recommendations

---

# System Architecture

```text
Keyboard Tracker
        │
Mouse Tracker
        │
Window Tracker
        │
Session Tracker
        │
        ▼
Metrics Aggregator
        │
        ▼
Stress Engine
        │
        ▼
Report Generator
        │
        ▼
FastAPI Backend
        │
        ▼
React Dashboard
```

---

# Core Components

## Keyboard Tracker

Captures:

* Keys Per Minute
* Backspaces Per Minute
* Average Pause Duration
* Long Pause Count
* Typing Variance

Purpose:

Identify hesitation, correction frequency, and typing irregularities.

---

## Mouse Tracker

Captures:

* Mouse Speed
* Click Rate
* Movement Distance

Purpose:

Detect restlessness and frustration patterns.

---

## Window Tracker

Captures:

* Active Application
* Window Switch Count

Purpose:

Measure context switching and multitasking behavior.

---

## Session Tracker

Captures:

* Session Duration
* Break Count
* Time Since Last Break

Purpose:

Estimate fatigue and workload accumulation.

---

## Metrics Aggregator

Combines outputs from all trackers into a unified metrics object.

---

## Stress Engine

Calculates cognitive stress using weighted behavioral indicators.

Contributors:

* Typing Stress
* Context Switching
* Mouse Activity
* Fatigue

Outputs:

```json
{
  "stress": {
    "score": 67,
    "level": "High Stress"
  }
}
```

---

## Report Generator

Creates structured JSON reports for dashboard consumption.

Example:

```json
{
  "timestamp": "...",
  "stress": {},
  "contributors": {},
  "recommendation": {},
  "metrics": {}
}
```

---

# Technology Stack

## Backend

* Python
* FastAPI

## Frontend

* React
* TypeScript
* Tailwind CSS
* Recharts

## Data Format

* JSON

---

# Dashboard Features

### Manager View

Displays:

* Employee Stress Score
* Contributor Breakdown
* Stress Trends
* Recommendations
* Raw Activity Metrics

### Analytics

* Real-Time Monitoring
* Trend Analysis
* Risk Detection
* Workforce Insights

---

# Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Synapse:

```bash
python main.py
```

The application will:

1. Start the backend server
2. Start the frontend application
3. Open the dashboard automatically
4. Begin real-time monitoring

---

# Future Enhancements

### Computer Vision Module

* Posture Detection
* Blink Rate Analysis
* Face Presence Monitoring
* Fatigue Detection

### Machine Learning

* Personalized Stress Models
* Adaptive Thresholds
* Employee-Specific Baselines

### Organization Analytics

* Team Heatmaps
* Department Stress Comparison
* Burnout Prediction
* Workforce Health Reports

---

# Impact

Synapse enables organizations to move from reactive employee wellness management to proactive cognitive health monitoring.

By identifying overload early, organizations can improve productivity, reduce burnout, and create healthier work environments through data-driven insights.

---

## Built For

Hackathons, workplace analytics platforms, employee wellness systems, productivity monitoring solutions, and future workforce intelligence products.
