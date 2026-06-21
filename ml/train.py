import time
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from ml.feature_store import FeatureStore
from ml.dataset_builder import DatasetBuilder, CognitiveDataset
from ml.models.lstm_model import CognitivePredictorLSTM, save_model

def train_model(epochs=10, batch_size=32):
    print("TrainPipeline: Starting ML Training Pipeline...", flush=True)
    
    store = FeatureStore()
    df = store.get_all_data()
    
    print(f"TrainPipeline: Found {len(df)} rows of historical data.")
    
    builder = DatasetBuilder()
    seqs, t15, t30, br = builder.build_training_data(df)
    
    if seqs is None or len(seqs) < batch_size:
        print("TrainPipeline: Insufficient data to train. Need more history.", flush=True)
        return False
        
    print(f"TrainPipeline: Created {len(seqs)} training sequences.")
    
    dataset = CognitiveDataset(seqs, t15, t30, br)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    model = CognitivePredictorLSTM(input_dim=seqs.shape[2])
    
    # Load existing weights if they exist to continue training
    model_path = "ml/weights/cognitive_lstm.pt"
    if os.path.exists(model_path):
        try:
            model.load_state_dict(torch.load(model_path))
            print("TrainPipeline: Loaded existing weights for finetuning.")
        except:
            pass
            
    model.train()
    
    # Loss functions
    criterion_reg = nn.MSELoss() # For continuous stress prediction
    criterion_cls = nn.BCELoss() # For burnout risk probability
    
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch_seq, batch_t15, batch_t30, batch_br in dataloader:
            optimizer.zero_grad()
            
            p15, p30, p_br = model(batch_seq)
            
            # Combined Loss
            loss_15 = criterion_reg(p15, batch_t15)
            loss_30 = criterion_reg(p30, batch_t30)
            loss_br = criterion_cls(p_br, batch_br)
            
            loss = loss_15 + loss_30 + (loss_br * 100) # Scale up BCE loss so it competes with MSE
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
        print(f"TrainPipeline: Epoch {epoch+1}/{epochs} - Loss: {epoch_loss/len(dataloader):.4f}")
        
    save_model(model, model_path)
    print(f"TrainPipeline: Training complete. Model saved to {model_path}", flush=True)
    return True

def run_training_loop():
    """Runs continuously in the background and trains every few hours or based on data size."""
    print("TrainPipeline: Background training daemon started.", flush=True)
    
    store = FeatureStore()
    
    while True:
        # Check if we have enough data (e.g., at least 1 hour of data = 720 rows)
        count = store.get_count()
        if count > 1000:
            success = train_model(epochs=5)
            if success:
                # Sleep for 12 hours before training again
                time.sleep(12 * 3600)
            else:
                # Sleep for an hour and check again
                time.sleep(3600)
        else:
            # Not enough data, sleep for 30 mins
            time.sleep(1800)

if __name__ == "__main__":
    train_model()
