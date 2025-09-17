from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

class ZmartyQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    request_type: str = Field(..., regex="^(basic_query|market_analysis|trading_strategy|ai_predictions|live_signals|custom_research)$")
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class ZmartyQueryResponse(BaseModel):
    success: bool
    request_id: uuid.UUID
    response: str
    credits_used: int
    processing_time: float

class ZmartyRequestResponse(BaseModel):
    id: uuid.UUID
    request_type: str
    query: str
    response: Optional[str]
    credits_cost: int
    status: str
    processing_time: Optional[int]
    quality_score: Optional[Decimal]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ZmartyRatingRequest(BaseModel):
    quality_score: float = Field(..., ge=0.0, le=5.0)

class TrendingQueryResponse(BaseModel):
    request_type: str
    count: int
    avg_rating: Optional[float]

class TradingAnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    timeframe: str = Field(default="1h", regex="^(1m|5m|15m|30m|1h|4h|1d|1w)$")
    analysis_type: str = Field(default="technical", regex="^(technical|fundamental|sentiment|combined)$")
    include_signals: bool = False
    risk_level: str = Field(default="medium", regex="^(low|medium|high)$")

class MarketSignalsRequest(BaseModel):
    symbols: list[str] = Field(default=["BTCUSDT", "ETHUSDT"], max_items=10)
    timeframe: str = Field(default="15m", regex="^(1m|5m|15m|30m|1h|4h)$")
    signal_strength: str = Field(default="medium", regex="^(weak|medium|strong)$")
    include_stop_loss: bool = True
    include_take_profit: bool = True

class AIPredictionRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    horizon: str = Field(default="24h", regex="^(1h|4h|24h|7d|30d)$")
    confidence: str = Field(default="medium", regex="^(low|medium|high)$")
    include_probability: bool = True
    model_type: str = Field(default="ensemble", regex="^(simple|advanced|ensemble)$")

class RequestHistoryQuery(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    status: Optional[str] = Field(None, regex="^(pending|processing|completed|failed)$")
    request_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None