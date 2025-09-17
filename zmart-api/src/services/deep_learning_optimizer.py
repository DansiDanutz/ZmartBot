# type: ignore
#!/usr/bin/env python3
"""
Deep Learning Optimizer
Advanced neural networks and deep learning for comprehensive strategy optimization
"""

import asyncio
import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import pickle
from sklearn.preprocessing import StandardScaler

# PyTorch imports with fallback
# Note: PyTorch is required for deep learning functionality
# Install with: pip install torch torchvision torchaudio
try:
    import torch  # type: ignore
    import torch.nn as nn  # type: ignore
    import torch.optim as optim  # type: ignore
    from torch.utils.data import DataLoader, TensorDataset  # type: ignore
    TORCH_AVAILABLE = True
except ImportError:
    # Fallback for environments without PyTorch
    torch = None  # type: ignore
    nn = None  # type: ignore
    optim = None  # type: ignore
    DataLoader = None  # type: ignore
    TensorDataset = None  # type: ignore
    TORCH_AVAILABLE = False

from src.config.settings import settings
from src.services.neural_network_optimizer import NeuralNetworkOptimizer
from src.services.predictive_analytics import PredictiveAnalytics

logger = logging.getLogger(__name__)

@dataclass
class DeepLearningConfig:
    """Deep learning configuration"""
    model_type: str
    input_size: int
    hidden_layers: List[int]
    output_size: int
    learning_rate: float
    batch_size: int
    epochs: int
    dropout_rate: float
    activation_function: str

@dataclass
class TrainingMetrics:
    """Training metrics structure"""
    loss_history: List[float]
    accuracy_history: List[float]
    validation_loss: List[float]
    validation_accuracy: List[float]
    training_time: float
    convergence_epoch: int

class AdvancedLSTM(nn.Module):  # type: ignore
    """Advanced LSTM for time series prediction"""
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int, dropout: float = 0.2):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for AdvancedLSTM. Please install torch: pip install torch")
        
        super(AdvancedLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        self.attention = nn.MultiheadAttention(hidden_size * 2, num_heads=8)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size * 2, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()
        
    def forward(self, x):
        if not TORCH_AVAILABLE or torch is None:
            raise ImportError("PyTorch is required for forward pass")
            
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Self-attention mechanism
        lstm_out = lstm_out.permute(1, 0, 2)  # (seq_len, batch, hidden_size)
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        attn_out = attn_out.permute(1, 0, 2)  # (batch, seq_len, hidden_size)
        
        # Global average pooling
        pooled = torch.mean(attn_out, dim=1)
        
        # Fully connected layers
        x = self.dropout(pooled)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.tanh(self.fc2(x))
        
        return x

class TransformerModel(nn.Module):  # type: ignore
    """Transformer model for sequence-to-sequence prediction"""
    
    def __init__(self, input_size: int, d_model: int, nhead: int, num_layers: int, output_size: int, dropout: float = 0.1):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for TransformerModel. Please install torch: pip install torch")
        
        super(TransformerModel, self).__init__()
        
        self.d_model = d_model
        self.input_projection = nn.Linear(input_size, d_model)
        self.positional_encoding = nn.Parameter(torch.randn(1000, d_model))  # type: ignore
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation='relu'
        )
        
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_projection = nn.Linear(d_model, output_size)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # Input projection
        x = self.input_projection(x)
        
        # Add positional encoding
        seq_len = x.size(1)
        x = x + self.positional_encoding[:seq_len].unsqueeze(0)
        
        # Transformer encoding
        x = x.permute(1, 0, 2)  # (seq_len, batch, d_model)
        x = self.transformer_encoder(x)
        x = x.permute(1, 0, 2)  # (batch, seq_len, d_model)
        
        # Global average pooling
        x = torch.mean(x, dim=1)  # type: ignore
        
        # Output projection
        x = self.dropout(x)
        x = self.output_projection(x)
        
        return x

class GANStrategyOptimizer(nn.Module):  # type: ignore
    """Generative Adversarial Network for strategy optimization"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for GANStrategyOptimizer. Please install torch: pip install torch")
        
        super(GANStrategyOptimizer, self).__init__()
        
        # Generator
        self.generator = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 2, output_size),
            nn.Tanh()
        )
        
        # Discriminator
        self.discriminator = nn.Sequential(
            nn.Linear(output_size, hidden_size // 2),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.generator(x)
    
    def discriminate(self, x):
        return self.discriminator(x)

class DeepLearningOptimizer:
    """
    Advanced deep learning optimizer with sophisticated neural networks
    """
    
    def __init__(self):
        """Initialize the deep learning optimizer"""
        self.neural_network_optimizer = NeuralNetworkOptimizer()
        self.predictive_analytics = PredictiveAnalytics()
        
        # Deep learning configurations
        self.lstm_config = DeepLearningConfig(
            model_type='lstm',
            input_size=50,
            hidden_layers=[128, 64, 32],
            output_size=17,
            learning_rate=0.001,
            batch_size=32,
            epochs=200,
            dropout_rate=0.2,
            activation_function='tanh'
        )
        
        self.transformer_config = DeepLearningConfig(
            model_type='transformer',
            input_size=50,
            hidden_layers=[256, 128, 64],
            output_size=10,
            learning_rate=0.0005,
            batch_size=16,
            epochs=150,
            dropout_rate=0.1,
            activation_function='relu'
        )
        
        self.gan_config = DeepLearningConfig(
            model_type='gan',
            input_size=100,
            hidden_layers=[256, 128],
            output_size=20,
            learning_rate=0.0002,
            batch_size=64,
            epochs=300,
            dropout_rate=0.3,
            activation_function='leaky_relu'
        )
        
        # Initialize models
        self.lstm_model = AdvancedLSTM(
            input_size=self.lstm_config.input_size,
            hidden_size=64,
            num_layers=3,
            output_size=self.lstm_config.output_size,
            dropout=self.lstm_config.dropout_rate
        )
        
        self.transformer_model = TransformerModel(
            input_size=self.transformer_config.input_size,
            d_model=128,
            nhead=8,
            num_layers=6,
            output_size=self.transformer_config.output_size,
            dropout=self.transformer_config.dropout_rate
        )
        
        self.gan_model = GANStrategyOptimizer(
            input_size=self.gan_config.input_size,
            hidden_size=128,
            output_size=self.gan_config.output_size
        )
        
        # Optimizers
        self.lstm_optimizer = optim.Adam(self.lstm_model.parameters(), lr=self.lstm_config.learning_rate)  # type: ignore
        self.transformer_optimizer = optim.Adam(self.transformer_model.parameters(), lr=self.transformer_config.learning_rate)  # type: ignore
        self.generator_optimizer = optim.Adam(self.gan_model.generator.parameters(), lr=self.gan_config.learning_rate)  # type: ignore
        self.discriminator_optimizer = optim.Adam(self.gan_model.discriminator.parameters(), lr=self.gan_config.learning_rate)  # type: ignore
        
        # Loss functions
        self.mse_loss = nn.MSELoss()  # type: ignore
        self.bce_loss = nn.BCELoss()  # type: ignore
        self.l1_loss = nn.L1Loss()  # type: ignore
        
        # Training data and metrics
        self.training_data: Dict[str, Any] = {}
        self.training_metrics: Dict[str, TrainingMetrics] = {}
        
        # Performance tracking
        self.performance_metrics = {
            'lstm_accuracy': 0.0,
            'transformer_accuracy': 0.0,
            'gan_generator_loss': 0.0,
            'gan_discriminator_loss': 0.0,
            'total_training_time': 0.0,
            'models_trained': 0,
            'last_training': None
        }
        
        # Model persistence
        self.model_path = "models/deep_learning/"
        self._ensure_model_directory()
        
        logger.info("Deep Learning Optimizer initialized")
    
    def _ensure_model_directory(self):
        """Ensure model directory exists"""
        import os
        os.makedirs(self.model_path, exist_ok=True)
    
    async def prepare_sequence_data(self, symbol: str, sequence_length: int = 30) -> Tuple[torch.Tensor, torch.Tensor]:
        """Prepare sequence data for LSTM and Transformer models"""
        try:
            # Get historical data
            if symbol not in self.training_data:
                await self._collect_deep_learning_data(symbol)
            
            df = self.training_data[symbol]
            
            # Create sequences
            sequences = []
            targets = []
            
            for i in range(len(df) - sequence_length):
                # Input sequence
                seq = df.iloc[i:i+sequence_length][self.lstm_config.input_size].values
                sequences.append(seq)
                
                # Target (next timestep)
                target = df.iloc[i+sequence_length]['actual_win_rate']
                targets.append(target)
            
            # Convert to tensors
            X = torch.FloatTensor(sequences)
            y = torch.FloatTensor(targets)
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing sequence data: {e}")
            raise
    
    async def _collect_deep_learning_data(self, symbol: str, days: int = 180):
        """Collect comprehensive data for deep learning models"""
        try:
            logger.info(f"Collecting deep learning data for {symbol}")
            
            # Generate comprehensive historical data
            data = []
            
            for day in range(days):
                data_point = await self._generate_deep_learning_data_point(symbol, day)
                data.append(data_point)
            
            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame(data)
            self.training_data[symbol] = df
            
            logger.info(f"Collected {len(df)} deep learning data points for {symbol}")
            
        except Exception as e:
            logger.error(f"Error collecting deep learning data: {e}")
            raise
    
    async def _generate_deep_learning_data_point(self, symbol: str, day_offset: int) -> Dict[str, Any]:
        """Generate comprehensive data point for deep learning"""
        try:
            timestamp = datetime.now() - timedelta(days=day_offset)
            
            # Market features (50 features)
            market_features = np.random.uniform(0, 1, 50)
            
            # Target variables
            actual_win_rate = np.random.uniform(0.4, 0.8)
            price_change = np.random.uniform(-0.1, 0.1)
            volatility_change = np.random.uniform(-0.2, 0.2)
            
            return {
                'timestamp': timestamp,
                'symbol': symbol,
                'market_features': market_features,
                'actual_win_rate': actual_win_rate,
                'price_change': price_change,
                'volatility_change': volatility_change
            }
            
        except Exception as e:
            logger.error(f"Error generating deep learning data point: {e}")
            raise
    
    async def train_lstm_model(self, symbol: str):
        """Train LSTM model for time series prediction"""
        try:
            logger.info(f"Training LSTM model for {symbol}")
            
            # Prepare sequence data
            X, y = await self.prepare_sequence_data(symbol)
            
            # Split data
            train_size = int(0.8 * len(X))
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Create data loaders
            train_dataset = TensorDataset(X_train, y_train)
            train_loader = DataLoader(train_dataset, batch_size=self.lstm_config.batch_size, shuffle=True)
            
            # Training loop
            self.lstm_model.train()
            loss_history = []
            accuracy_history = []
            
            start_time = time.time()
            
            for epoch in range(self.lstm_config.epochs):
                epoch_loss = 0.0
                
                for batch_X, batch_y in train_loader:
                    # Forward pass
                    predictions = self.lstm_model(batch_X)
                    loss = self.mse_loss(predictions.squeeze(), batch_y)
                    
                    # Backward pass
                    self.lstm_optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.lstm_model.parameters(), max_norm=1.0)
                    self.lstm_optimizer.step()
                    
                    epoch_loss += loss.item()
                
                avg_loss = epoch_loss / len(train_loader)
                loss_history.append(avg_loss)
                
                # Calculate accuracy
                if epoch % 10 == 0:
                    accuracy = self._calculate_accuracy(predictions, batch_y)
                    accuracy_history.append(accuracy)
                    logger.info(f"Epoch {epoch}: Loss = {avg_loss:.6f}, Accuracy = {accuracy:.4f}")
            
            training_time = time.time() - start_time
            
            # Store training metrics
            self.training_metrics['lstm'] = TrainingMetrics(
                loss_history=loss_history,
                accuracy_history=accuracy_history,
                validation_loss=[],
                validation_accuracy=[],
                training_time=training_time,
                convergence_epoch=len(loss_history)
            )
            
            # Update performance metrics
            self.performance_metrics['lstm_accuracy'] = accuracy_history[-1] if accuracy_history else 0.0
            self.performance_metrics['total_training_time'] += training_time
            self.performance_metrics['models_trained'] += 1
            self.performance_metrics['last_training'] = datetime.now()
            
            # Save model
            await self._save_model('lstm_model')
            
            logger.info(f"LSTM model training completed in {training_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            raise
    
    async def train_transformer_model(self, symbol: str):
        """Train Transformer model for sequence prediction"""
        try:
            logger.info(f"Training Transformer model for {symbol}")
            
            # Prepare sequence data
            X, y = await self.prepare_sequence_data(symbol)
            
            # Split data
            train_size = int(0.8 * len(X))
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Create data loaders
            train_dataset = TensorDataset(X_train, y_train)
            train_loader = DataLoader(train_dataset, batch_size=self.transformer_config.batch_size, shuffle=True)
            
            # Training loop
            self.transformer_model.train()
            loss_history = []
            accuracy_history = []
            
            start_time = time.time()
            
            for epoch in range(self.transformer_config.epochs):
                epoch_loss = 0.0
                
                for batch_X, batch_y in train_loader:
                    # Forward pass
                    predictions = self.transformer_model(batch_X)
                    loss = self.mse_loss(predictions.squeeze(), batch_y)
                    
                    # Backward pass
                    self.transformer_optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.transformer_model.parameters(), max_norm=1.0)
                    self.transformer_optimizer.step()
                    
                    epoch_loss += loss.item()
                
                avg_loss = epoch_loss / len(train_loader)
                loss_history.append(avg_loss)
                
                # Calculate accuracy
                if epoch % 10 == 0:
                    accuracy = self._calculate_accuracy(predictions, batch_y)
                    accuracy_history.append(accuracy)
                    logger.info(f"Epoch {epoch}: Loss = {avg_loss:.6f}, Accuracy = {accuracy:.4f}")
            
            training_time = time.time() - start_time
            
            # Store training metrics
            self.training_metrics['transformer'] = TrainingMetrics(
                loss_history=loss_history,
                accuracy_history=accuracy_history,
                validation_loss=[],
                validation_accuracy=[],
                training_time=training_time,
                convergence_epoch=len(loss_history)
            )
            
            # Update performance metrics
            self.performance_metrics['transformer_accuracy'] = accuracy_history[-1] if accuracy_history else 0.0
            self.performance_metrics['total_training_time'] += training_time
            self.performance_metrics['models_trained'] += 1
            
            # Save model
            await self._save_model('transformer_model')
            
            logger.info(f"Transformer model training completed in {training_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error training Transformer model: {e}")
            raise
    
    async def train_gan_model(self, symbol: str):
        """Train GAN model for strategy generation"""
        try:
            logger.info(f"Training GAN model for {symbol}")
            
            # Prepare GAN data
            if symbol not in self.training_data:
                await self._collect_deep_learning_data(symbol)
            
            df = self.training_data[symbol]
            
            # Create real strategy data
            real_strategies = torch.FloatTensor(np.random.uniform(0, 1, (len(df), self.gan_config.output_size)))
            
            # Create data loader
            dataset = TensorDataset(real_strategies)
            data_loader = DataLoader(dataset, batch_size=self.gan_config.batch_size, shuffle=True)
            
            # Training loop
            generator_losses = []
            discriminator_losses = []
            
            start_time = time.time()
            
            for epoch in range(self.gan_config.epochs):
                for i, (real_strategies_batch,) in enumerate(data_loader):
                    batch_size = real_strategies_batch.size(0)
                    
                    # Train Discriminator
                    self.discriminator_optimizer.zero_grad()
                    
                    # Real strategies
                    real_labels = torch.ones(batch_size, 1)
                    real_outputs = self.gan_model.discriminate(real_strategies_batch)
                    d_real_loss = self.bce_loss(real_outputs, real_labels)
                    
                    # Fake strategies
                    noise = torch.randn(batch_size, self.gan_config.input_size)
                    fake_strategies = self.gan_model.generator(noise)
                    fake_labels = torch.zeros(batch_size, 1)
                    fake_outputs = self.gan_model.discriminate(fake_strategies.detach())
                    d_fake_loss = self.bce_loss(fake_outputs, fake_labels)
                    
                    # Total discriminator loss
                    d_loss = d_real_loss + d_fake_loss
                    d_loss.backward()
                    self.discriminator_optimizer.step()
                    
                    # Train Generator
                    self.generator_optimizer.zero_grad()
                    
                    fake_outputs = self.gan_model.discriminate(fake_strategies)
                    g_loss = self.bce_loss(fake_outputs, real_labels)
                    g_loss.backward()
                    self.generator_optimizer.step()
                    
                    generator_losses.append(g_loss.item())
                    discriminator_losses.append(d_loss.item())
                
                if epoch % 50 == 0:
                    avg_g_loss = np.mean(generator_losses[-len(data_loader):])
                    avg_d_loss = np.mean(discriminator_losses[-len(data_loader):])
                    logger.info(f"Epoch {epoch}: G Loss = {avg_g_loss:.6f}, D Loss = {avg_d_loss:.6f}")
            
            training_time = time.time() - start_time
            
            # Store training metrics
            self.training_metrics['gan'] = TrainingMetrics(
                loss_history=generator_losses,
                accuracy_history=discriminator_losses,
                validation_loss=[],
                validation_accuracy=[],
                training_time=training_time,
                convergence_epoch=len(generator_losses)
            )
            
            # Update performance metrics
            self.performance_metrics['gan_generator_loss'] = generator_losses[-1] if generator_losses else 0.0
            self.performance_metrics['gan_discriminator_loss'] = discriminator_losses[-1] if discriminator_losses else 0.0
            self.performance_metrics['total_training_time'] += training_time
            self.performance_metrics['models_trained'] += 1
            
            # Save model
            await self._save_model('gan_model')
            
            logger.info(f"GAN model training completed in {training_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error training GAN model: {e}")
            raise
    
    def _calculate_accuracy(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """Calculate prediction accuracy"""
        try:
            with torch.no_grad():
                # For regression, use R² score approximation
                mse = self.mse_loss(predictions.squeeze(), targets)
                var = torch.var(targets)
                r2 = 1 - (mse / var)
                return max(0.0, min(1.0, r2.item()))
        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")
            return 0.0
    
    async def predict_with_lstm(self, market_features: np.ndarray) -> np.ndarray:
        """Make prediction using LSTM model"""
        try:
            self.lstm_model.eval()
            
            with torch.no_grad():
                # Prepare input sequence
                sequence = torch.FloatTensor(market_features).unsqueeze(0)
                
                # Make prediction
                prediction = self.lstm_model(sequence)
                
                return prediction.numpy().flatten()
                
        except Exception as e:
            logger.error(f"Error making LSTM prediction: {e}")
            return np.zeros(self.lstm_config.output_size)
    
    async def predict_with_transformer(self, market_features: np.ndarray) -> np.ndarray:
        """Make prediction using Transformer model"""
        try:
            self.transformer_model.eval()
            
            with torch.no_grad():
                # Prepare input sequence
                sequence = torch.FloatTensor(market_features).unsqueeze(0)
                
                # Make prediction
                prediction = self.transformer_model(sequence)
                
                return prediction.numpy().flatten()
                
        except Exception as e:
            logger.error(f"Error making Transformer prediction: {e}")
            return np.zeros(self.transformer_config.output_size)
    
    async def generate_strategy_with_gan(self, noise: np.ndarray) -> np.ndarray:
        """Generate strategy using GAN model"""
        try:
            self.gan_model.generator.eval()
            
            with torch.no_grad():
                # Prepare noise input
                noise_tensor = torch.FloatTensor(noise).unsqueeze(0)
                
                # Generate strategy
                strategy = self.gan_model.generator(noise_tensor)
                
                return strategy.numpy().flatten()
                
        except Exception as e:
            logger.error(f"Error generating strategy with GAN: {e}")
            return np.zeros(self.gan_config.output_size)
    
    async def _save_model(self, model_name: str):
        """Save trained model"""
        try:
            if model_name == 'lstm_model':
                torch.save(self.lstm_model.state_dict(), f"{self.model_path}lstm_model.pth")
            elif model_name == 'transformer_model':
                torch.save(self.transformer_model.state_dict(), f"{self.model_path}transformer_model.pth")
            elif model_name == 'gan_model':
                torch.save({
                    'generator_state_dict': self.gan_model.generator.state_dict(),
                    'discriminator_state_dict': self.gan_model.discriminator.state_dict()
                }, f"{self.model_path}gan_model.pth")
            
            # Save training metrics
            metrics_path = f"{self.model_path}{model_name}_metrics.json"
            with open(metrics_path, 'w') as f:
                json.dump({
                    'model_name': model_name,
                    'timestamp': datetime.now().isoformat(),
                    'performance_metrics': self.performance_metrics,
                    'training_metrics': {
                        name: {
                            'loss_history': metrics.loss_history[-10:],  # Last 10 values
                            'accuracy_history': metrics.accuracy_history[-10:],
                            'training_time': metrics.training_time,
                            'convergence_epoch': metrics.convergence_epoch
                        }
                        for name, metrics in self.training_metrics.items()
                    }
                }, f, indent=2)
            
            logger.info(f"Model {model_name} saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")
    
    async def get_deep_learning_report(self) -> Dict[str, Any]:
        """Get comprehensive deep learning report"""
        return {
            'models': {
                'lstm_model': {
                    'status': 'trained' if 'lstm' in self.training_metrics else 'untrained',
                    'architecture': 'Advanced LSTM with Attention',
                    'config': {
                        'input_size': self.lstm_config.input_size,
                        'hidden_size': 64,
                        'num_layers': 3,
                        'output_size': self.lstm_config.output_size,
                        'learning_rate': self.lstm_config.learning_rate
                    },
                    'performance': {
                        'accuracy': self.performance_metrics['lstm_accuracy'],
                        'training_time': self.training_metrics.get('lstm', TrainingMetrics([], [], [], [], 0.0, 0)).training_time
                    }
                },
                'transformer_model': {
                    'status': 'trained' if 'transformer' in self.training_metrics else 'untrained',
                    'architecture': 'Transformer with Multi-head Attention',
                    'config': {
                        'input_size': self.transformer_config.input_size,
                        'd_model': 128,
                        'nhead': 8,
                        'num_layers': 6,
                        'output_size': self.transformer_config.output_size,
                        'learning_rate': self.transformer_config.learning_rate
                    },
                    'performance': {
                        'accuracy': self.performance_metrics['transformer_accuracy'],
                        'training_time': self.training_metrics.get('transformer', TrainingMetrics([], [], [], [], 0.0, 0)).training_time
                    }
                },
                'gan_model': {
                    'status': 'trained' if 'gan' in self.training_metrics else 'untrained',
                    'architecture': 'Generative Adversarial Network',
                    'config': {
                        'input_size': self.gan_config.input_size,
                        'hidden_size': 128,
                        'output_size': self.gan_config.output_size,
                        'learning_rate': self.gan_config.learning_rate
                    },
                    'performance': {
                        'generator_loss': self.performance_metrics['gan_generator_loss'],
                        'discriminator_loss': self.performance_metrics['gan_discriminator_loss'],
                        'training_time': self.training_metrics.get('gan', TrainingMetrics([], [], [], [], 0.0, 0)).training_time
                    }
                }
            },
            'performance_metrics': {
                'total_training_time': self.performance_metrics['total_training_time'],
                'models_trained': self.performance_metrics['models_trained'],
                'last_training': self.performance_metrics['last_training'].isoformat() if self.performance_metrics['last_training'] else None
            },
            'training_data': {
                'symbols_with_data': list(self.training_data.keys()),
                'total_data_points': sum(len(df) for df in self.training_data.values())
            },
            'timestamp': datetime.now().isoformat()
        }

# Global instance
deep_learning_optimizer = DeepLearningOptimizer() 