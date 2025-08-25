# Deep Learning Linter Fixes Guide

## Overview
This guide addresses the linter errors in the deep learning optimizer file. The errors are primarily due to PyTorch import issues and class inheritance problems.

## Root Cause Analysis

### 1. PyTorch Import Issues
- **Problem**: PyTorch modules (`nn`, `torch`, `optim`) are imported with fallback but still causing linter errors
- **Solution**: Add proper type checking and conditional imports

### 2. Class Inheritance Issues
- **Problem**: Classes like `AdvancedLSTM` and `TransformerModel` don't properly inherit from `nn.Module`
- **Solution**: Fix class inheritance and add proper PyTorch module structure

### 3. Optional Member Access
- **Problem**: Accessing PyTorch attributes when modules might be None
- **Solution**: Add comprehensive null checks and type guards

## Required Fixes

### 1. Fix Class Inheritance
```python
# Before (causing errors)
class AdvancedLSTM:
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int, dropout: float = 0.2):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for AdvancedLSTM. Please install torch: pip install torch")
        
        if nn is None:
            raise ImportError("PyTorch nn module is not available")
            
        super(AdvancedLSTM, self).__init__()

# After (proper inheritance)
class AdvancedLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int, dropout: float = 0.2):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for AdvancedLSTM. Please install torch: pip install torch")
        
        super(AdvancedLSTM, self).__init__()
```

### 2. Add Type Guards
```python
# Add at the top of the file
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
```

### 3. Fix Method Calls
```python
# Before (causing errors)
def forward(self, x):
    if not TORCH_AVAILABLE or torch is None:
        raise ImportError("PyTorch is required for forward pass")
    
    # LSTM forward pass
    lstm_out, _ = self.lstm(x)

# After (proper type checking)
def forward(self, x):
    if not TORCH_AVAILABLE or torch is None or self.lstm is None:
        raise ImportError("PyTorch is required for forward pass")
    
    # LSTM forward pass
    lstm_out, _ = self.lstm(x)
```

### 4. Fix Optimizer and Loss Functions
```python
# Before (causing errors)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
criterion = nn.MSELoss()

# After (with proper checks)
if optim is not None and nn is not None:
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
else:
    raise ImportError("PyTorch optim and nn modules are required")
```

### 5. Fix Tensor Operations
```python
# Before (causing errors)
X_tensor = torch.FloatTensor(X)
y_tensor = torch.FloatTensor(y)

# After (with proper checks)
if torch is not None:
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.FloatTensor(y)
else:
    raise ImportError("PyTorch is required for tensor operations")
```

## Installation Requirements

### 1. Install PyTorch
```bash
# CPU Only
pip install torch torchvision torchaudio

# GPU Support (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# GPU Support (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Verify Installation
```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

## Complete Fix Strategy

### 1. Update Import Structure
```python
# Add proper type checking imports
from typing import TYPE_CHECKING, Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
import logging

# PyTorch imports with comprehensive fallback
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    optim = None
    DataLoader = None
    TensorDataset = None
    TORCH_AVAILABLE = False

if TYPE_CHECKING:
    # Type checking imports for IDE support
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
```

### 2. Fix All Class Definitions
```python
class AdvancedLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int, dropout: float = 0.2):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for AdvancedLSTM")
        
        super(AdvancedLSTM, self).__init__()
        # ... rest of initialization

class TransformerModel(nn.Module):
    def __init__(self, input_size: int, d_model: int, nhead: int, num_layers: int, output_size: int, dropout: float = 0.1):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for TransformerModel")
        
        super(TransformerModel, self).__init__()
        # ... rest of initialization

class GANStrategyOptimizer(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        if not TORCH_AVAILABLE or nn is None:
            raise ImportError("PyTorch is required for GANStrategyOptimizer")
        
        super(GANStrategyOptimizer, self).__init__()
        # ... rest of initialization
```

### 3. Add Comprehensive Error Handling
```python
def _check_pytorch_available(self, operation: str = "operation"):
    """Check if PyTorch is available for operations"""
    if not TORCH_AVAILABLE:
        raise ImportError(f"PyTorch is required for {operation}. Please install torch: pip install torch")
    if torch is None or nn is None:
        raise ImportError(f"PyTorch modules are not properly loaded for {operation}")
```

## Testing the Fixes

### 1. Run Type Checking
```bash
# Install mypy for type checking
pip install mypy

# Run type checking
mypy backend/zmart-api/src/services/deep_learning_optimizer.py
```

### 2. Test Import
```python
# Test basic import
from src.services.deep_learning_optimizer import DeepLearningOptimizer

# Test with PyTorch available
optimizer = DeepLearningOptimizer()
print("Deep learning optimizer initialized successfully")
```

### 3. Test Without PyTorch
```python
# Test graceful degradation
# (This should raise ImportError with clear message)
try:
    from src.services.deep_learning_optimizer import DeepLearningOptimizer
    optimizer = DeepLearningOptimizer()
except ImportError as e:
    print(f"Expected error: {e}")
```

## Performance Considerations

### 1. Memory Management
- Use `torch.no_grad()` for inference
- Clear gradients with `optimizer.zero_grad()`
- Use `model.eval()` for evaluation

### 2. GPU Optimization
```python
# Move models to GPU if available
if torch.cuda.is_available():
    model = model.cuda()
    X_tensor = X_tensor.cuda()
    y_tensor = y_tensor.cuda()
```

### 3. Batch Processing
```python
# Use DataLoader for efficient batching
if DataLoader is not None:
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
```

## Troubleshooting

### Common Issues
1. **Import Error**: Install PyTorch using the commands above
2. **CUDA Issues**: Use CPU-only version or check GPU drivers
3. **Memory Issues**: Reduce batch size or model complexity
4. **Type Errors**: Ensure proper inheritance from `nn.Module`

### Debug Steps
1. Check PyTorch installation: `python -c "import torch; print(torch.__version__)"`
2. Verify CUDA setup: `python -c "import torch; print(torch.cuda.is_available())"`
3. Test basic operations: `python -c "import torch; x = torch.tensor([1,2,3]); print(x)"`

## Support
For issues with deep learning setup:
1. Check PyTorch installation guide: https://pytorch.org/get-started/locally/
2. Verify system requirements and compatibility
3. Check GPU driver versions (if using CUDA) 