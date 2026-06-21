import os
import torch
import torch.nn as nn

class CognitivePredictorLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2, dropout=0.2):
        """
        LSTM Model for predicting future cognitive stress and burnout risk.
        input_dim: Number of features collected at each timestep
        hidden_dim: Size of hidden state
        num_layers: Number of LSTM layers
        """
        super(CognitivePredictorLSTM, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM feature extractor
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        
        # Output heads
        self.fc_15m = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)  # Predicts continuous stress score (0-100)
        )
        
        self.fc_30m = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)  # Predicts continuous stress score (0-100)
        )
        
        self.fc_burnout = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Predicts probability/risk of burnout (0.0 - 1.0)
        )
        
    def forward(self, x):
        """
        x shape: (batch_size, seq_len, input_dim)
        """
        # lstm_out shape: (batch_size, seq_len, hidden_dim)
        # hidden[0] shape: (num_layers, batch_size, hidden_dim)
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Get the hidden state of the last timestep from the last layer
        last_hidden = hidden[-1]  # shape: (batch_size, hidden_dim)
        
        stress_15m = self.fc_15m(last_hidden)
        stress_30m = self.fc_30m(last_hidden)
        burnout_risk = self.fc_burnout(last_hidden)
        
        return stress_15m, stress_30m, burnout_risk

def save_model(model, path="ml/weights/cognitive_lstm.pt"):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    torch.save(model.state_dict(), path)

def load_model(input_dim, path="ml/weights/cognitive_lstm.pt"):
    model = CognitivePredictorLSTM(input_dim=input_dim)
    if os.path.exists(path):
        model.load_state_dict(torch.load(path))
    else:
        print(f"Warning: No model weights found at {path}. Using randomly initialized weights.")
    return model
