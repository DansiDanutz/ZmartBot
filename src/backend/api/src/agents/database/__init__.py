"""
Database Agent Module for ZmartBot RiskMetric System

This module provides comprehensive database management capabilities:
- RiskMetric Q&A Agent with natural language processing
- Real-time data management
- Symbol analysis and risk modeling
- Database optimization and maintenance
"""

from .riskmetric_qa_agent import RiskMetricQAAgent
from .chatgpt_risk_analyzer import ChatGPTRiskAnalyzer, SymbolAnalysis

__all__ = [
    'RiskMetricQAAgent',
    'ChatGPTRiskAnalyzer',
    'SymbolAnalysis'
]

__version__ = "3.0.0"