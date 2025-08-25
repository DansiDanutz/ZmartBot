# Deep Learning Setup Guide

## Overview
The Zmart Bot includes advanced deep learning capabilities for strategy optimization. This guide explains how to set up the required dependencies.

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- Virtual environment recommended

### 2. Install PyTorch

#### Option A: CPU Only (Recommended for development)
```bash
pip install torch torchvision torchaudio
```

#### Option B: GPU Support (CUDA)
```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. Install Additional Dependencies
```bash
pip install -r requirements_deep_learning.txt
```

## Verification

### Check PyTorch Installation
```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Test Deep Learning Components
```python
from src.services.deep_learning_optimizer import DeepLearningOptimizer

# This should work if PyTorch is properly installed
optimizer = DeepLearningOptimizer()
print("Deep learning optimizer initialized successfully")
```

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'torch'**
   - Solution: Install PyTorch using the commands above

2. **CUDA not available**
   - Solution: Install CPU-only version or check CUDA installation

3. **Memory issues with large models**
   - Solution: Reduce batch size or use smaller models

### Fallback Mode
If PyTorch is not available, the system will:
- Log warnings about missing deep learning functionality
- Continue operating with other optimization methods
- Provide clear error messages when deep learning features are accessed

## Performance Optimization

### GPU Usage
- Set `CUDA_VISIBLE_DEVICES` environment variable
- Monitor GPU memory usage
- Use gradient checkpointing for large models

### Memory Management
- Adjust batch sizes based on available memory
- Use mixed precision training when possible
- Monitor memory usage during training

## Advanced Configuration

### Model Parameters
- Adjust hidden layer sizes in `DeepLearningConfig`
- Modify learning rates and batch sizes
- Configure dropout rates for regularization

### Training Parameters
- Set appropriate number of epochs
- Configure early stopping criteria
- Adjust validation split ratios

## Support
For issues with deep learning setup, check:
1. PyTorch installation guide: https://pytorch.org/get-started/locally/
2. System requirements and compatibility
3. GPU driver versions (if using CUDA) 