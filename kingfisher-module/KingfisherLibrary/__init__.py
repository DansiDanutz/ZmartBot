"""
KingfisherLibrary - Complete Trading Automation System
Self-Learning Orchestration with 6-Step Pipeline
Version: 2.0
"""

__version__ = "2.0.0"
__author__ = "KingFisher Team"

# Core components
from .orchestration import SelfLearningKingOrchestrator
from .steps import (
    Step1_MonitorDownload,
    Step2_SortImages,
    Step3_RemoveDuplicates,
    Step4_AnalyzeReports,
    Step5_ExtractClusters,
    Step6_GenerateReports
)
from .learning import LearningModule
from .api import KingfisherAPI

__all__ = [
    'SelfLearningKingOrchestrator',
    'Step1_MonitorDownload',
    'Step2_SortImages',
    'Step3_RemoveDuplicates',
    'Step4_AnalyzeReports',
    'Step5_ExtractClusters',
    'Step6_GenerateReports',
    'LearningModule',
    'KingfisherAPI'
]