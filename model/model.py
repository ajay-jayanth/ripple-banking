import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

class LoanDataset(Dataset):
    """Custom Dataset for loan prediction data"""
    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

class LoanPredictionModel(nn.Module):
    """Neural Network for loan prediction"""
    def __init__(self, input_dim):
        super(LoanPredictionModel, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.layer2 = nn.Linear(64, 32)
        self.layer3 = nn.Linear(32, 16)
        self.layer4 = nn.Linear(16, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.batch_norm1 = nn.BatchNorm1d(64)
        self.batch_norm2 = nn.BatchNorm1d(32)
        self.batch_norm3 = nn.BatchNorm1d(16)
        
    def forward(self, x):
        x = self.relu(self.batch_norm1(self.layer1(x)))
        x = self.dropout(x)
        x = self.relu(self.batch_norm2(self.layer2(x)))
        x = self.dropout(x)
        x = self.relu(self.batch_norm3(self.layer3(x)))
        x = self.dropout(x)
        x = torch.sigmoid(self.layer4(x))
        return x

def prepare_data(data, batch_size=32):
    """Prepare data for training"""
    # Separate features and target
    X = data[['loan_percent_income', 'loan_amount', 'person_income', 'person_emp_length']].values
    y = data['loan_status'].values.reshape(-1, 1)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Create datasets
    train_dataset = LoanDataset(X_train_scaled, y_train)
    test_dataset = LoanDataset(X_test_scaled, y_test)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    return train_loader, test_loader, scaler

def train_model(model, train_loader, num_epochs=100, learning_rate=0.001):
    """Train the neural network"""
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for features, targets in train_loader:
            features, targets = features.to(device), targets.to(device)
            
            # Forward pass
            outputs = model(features)
            loss = criterion(outputs, targets)
            
            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss/len(train_loader):.4f}')

def evaluate_model(model, test_loader):
    """Evaluate the model"""
    model.eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    correct = 0
    total = 0
    predictions = []
    actual = []
    
    with torch.no_grad():
        for features, targets in test_loader:
            features, targets = features.to(device), targets.to(device)
            outputs = model(features)
            predicted = (outputs >= 0.5).float()
            
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
            
            predictions.extend(predicted.cpu().numpy())
            actual.extend(targets.cpu().numpy())
    
    accuracy = 100 * correct / total
    print(f'Accuracy: {accuracy:.2f}%')
    
    return predictions, actual

def predict_new_applications(model, scaler, new_data):
    """Make predictions on new applications"""
    model.eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Scale the new data
    scaled_data = scaler.transform(new_data)
    
    # Convert to tensor
    features = torch.FloatTensor(scaled_data).to(device)
    
    # Make predictions
    with torch.no_grad():
        outputs = model(features)
        predictions = (outputs >= 0.5).float()
    
    return predictions.cpu().numpy()

# Example usage
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    example_data = pd.read_csv("credit_risk_dataset.csv")
    
    # Prepare data
    train_loader, test_loader, scaler = prepare_data(example_data)
    
    # Initialize and train model
    model = LoanPredictionModel(input_dim=4)
    train_model(model, train_loader)
    
    # Evaluate model
    predictions, actual = evaluate_model(model, test_loader)
    
    # Example of making new predictions
    new_applications = np.array([
        [0.3, 250000, 80000, 5],
        [0.2, 180000, 65000, 3]
    ])
    
    new_predictions = predict_new_applications(model, scaler, new_applications)
    print("\nNew Application Predictions:")
    print(new_predictions)