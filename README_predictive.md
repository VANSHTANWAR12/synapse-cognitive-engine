# Predictive Cognitive Load Engine

The Synapse Cognitive Load Engine now features a true machine learning-based prediction system using PyTorch LSTMs. Instead of simply reacting to stress after it happens, the engine uses historical behavioral patterns to forecast cognitive overload up to 30 minutes in advance.

## Architecture

1. **Feature Store (`ml/feature_store.py`)**
   - SQLite-backed time-series database.
   - Captures 18+ behavioral metrics (keyboard variance, app switching, facial expressions, posture) every few seconds.

2. **Dataset Builder (`ml/dataset_builder.py`)**
   - Converts raw SQLite metrics into PyTorch tensors.
   - Generates overlapping sliding windows (sequence length of 30 minutes).

3. **LSTM Model (`ml/models/lstm_model.py`)**
   - PyTorch LSTM neural network.
   - Inputs: `(batch_size, sequence_length, features)`
   - Outputs: Predicted Stress 15m out, Predicted Stress 30m out, Burnout Risk classification.

4. **Background Trainer (`ml/train.py`)**
   - Periodically wakes up to fetch historical data from SQLite.
   - Trains the model to learn the specific user's unique stress patterns (e.g., "when this user's typing variance spikes and window switches increase, they experience stress 20 minutes later").

5. **Live Predictor (`ml/predictor.py`)**
   - Fetches the last 30 minutes of real-time data from the Feature Store.
   - Runs live inference through the LSTM.
   - Includes a "Baseline Heuristic" fallback that provides logic-based predictions if the model hasn't gathered enough training data yet.

## Dashboard Integration

The React frontend includes a new **Predictive Intelligence** section that displays:
- Current Stress vs. Forecasted Stress (15m/30m)
- Burnout Risk %
- Model Confidence Level
- Top Contributing Factors (e.g., "Attention Decline", "Elevated Fatigue")

The Live Stress Trend chart has also been updated to show dashed lines projecting into the future.

## Setup

The backend now requires:
```bash
pip install torch pandas scikit-learn
```

The predictive engine runs completely locally to preserve privacy. No data is sent to external servers for training.
