# Neural Network Setup Guide

## Overview
The Zmart Bot includes advanced neural network capabilities for endpoint weight prediction and strategy optimization. This guide explains the setup and usage.

## Prerequisites

### 1. PyTorch Installation
```bash
# CPU Only (Recommended for development)
pip install torch torchvision torchaudio

# GPU Support (CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Additional Dependencies
```bash
pip install -r requirements_deep_learning.txt
```

## Neural Network Components

### 1. EndpointWeightPredictor
- **Purpose**: Predicts optimal endpoint weights based on market conditions
- **Input**: Market features (volatility, volume, sentiment, etc.)
- **Output**: Optimized endpoint weights for Cryptometer API

### 2. StrategyOptimizer
- **Purpose**: Optimizes trading strategies using neural networks
- **Input**: Market data and historical performance
- **Output**: Strategy parameters and risk adjustments

## Usage Examples

### Basic Setup
```python
from src.services.neural_network_optimizer import NeuralNetworkOptimizer

# Initialize optimizer
optimizer = NeuralNetworkOptimizer()

# Collect training data
training_data = await optimizer.collect_training_data("BTCUSDT", days=30)

# Train models
await optimizer.train_endpoint_predictor(training_data)
await optimizer.train_strategy_optimizer(training_data)
```

### Prediction
```python
# Predict optimal weights
market_features = np.array([...])  # Your market features
optimal_weights = await optimizer.predict_optimal_weights(market_features)

# Optimize strategy
strategy_params = await optimizer.optimize_strategy(market_features)
```

## Configuration

### Neural Network Parameters
```python
config = NeuralNetworkConfig(
    input_size=50,      # Number of input features
    hidden_size=128,    # Hidden layer size
    output_size=17,     # Number of Cryptometer endpoints
    learning_rate=0.001,
    batch_size=32,
    epochs=100,
    dropout_rate=0.2
)
```

### Training Parameters
- **Learning Rate**: 0.001 (default)
- **Batch Size**: 32 (default)
- **Epochs**: 100 (default)
- **Dropout Rate**: 0.2 (default)

## Performance Optimization

### GPU Usage
```python
# Check GPU availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")

# Move models to GPU
if torch.cuda.is_available():
    model = model.cuda()
```

### Memory Management
- Use smaller batch sizes for limited memory
- Enable gradient checkpointing for large models
- Monitor GPU memory usage

## Error Handling

### PyTorch Not Available
If PyTorch is not installed, the system will:
1. Log clear error messages
2. Provide installation instructions
3. Continue with other optimization methods

### Common Issues
1. **Import Error**: Install PyTorch using the commands above
2. **CUDA Issues**: Use CPU-only version or check GPU drivers
3. **Memory Issues**: Reduce batch size or model complexity

## Integration with Main System

### Dynamic Weight Adjustment
```python
from src.services.dynamic_weight_adjuster import DynamicWeightAdjuster

# Neural networks automatically update endpoint weights
adjuster = DynamicWeightAdjuster()
await adjuster.update_weights_with_neural_network(market_data)
```

### Strategy Optimization
```python
from src.services.integrated_scoring_system import IntegratedScoringSystem

# Neural networks optimize scoring parameters
scoring_system = IntegratedScoringSystem()
await scoring_system.optimize_with_neural_network(market_data)
```

## Monitoring and Logging

### Training Progress
```python
# Monitor training metrics
report = await optimizer.get_neural_network_report()
print(f"Training accuracy: {report['accuracy']}")
print(f"Validation loss: {report['validation_loss']}")
```

### Model Performance
```python
# Check model performance
performance = await optimizer.evaluate_model_performance()
print(f"Prediction accuracy: {performance['accuracy']}")
print(f"Weight optimization score: {performance['weight_score']}")
```

## Advanced Features

### Model Persistence
```python
# Save trained models
await optimizer.save_model("endpoint_predictor_v1")

# Load saved models
await optimizer.load_model("endpoint_predictor_v1")
```

### Real-time Updates
```python
# Update models with new data
await optimizer.update_model_with_new_data(latest_market_data)
```

## Troubleshooting

### Installation Issues
1. **PyTorch not found**: Run `pip install torch`
2. **CUDA errors**: Install CPU version or update GPU drivers
3. **Memory errors**: Reduce batch size or model size

### Runtime Issues
1. **Model loading errors**: Check model file paths
2. **Prediction errors**: Verify input data format
3. **Training errors**: Check data quality and model parameters

## Support
For issues with neural networks:
1. Check PyTorch installation: `python -c "import torch; print(torch.__version__)"`
2. Verify CUDA setup: `python -c "import torch; print(torch.cuda.is_available())"`
3. Check system requirements and compatibility

## Performance Benchmarks
- **Training Time**: ~5-10 minutes per model (CPU)
- **Prediction Time**: <100ms per prediction
- **Memory Usage**: ~500MB per model
- **Accuracy**: 75-85% on validation data 