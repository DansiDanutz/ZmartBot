# RiskMetric Q&A API Documentation

## Benjamin Cowen's RiskMetric Natural Language Query System

### Overview
The RiskMetric Q&A API allows users to ask natural language questions about Benjamin Cowen's risk metric data and receive intelligent, context-aware answers. The system understands various question types and can calculate risk values, explain methodology, compare symbols, and analyze historical patterns.

### Base URL
```
http://localhost:8000/api/v1/riskmetric
```

## API Endpoints

### 1. Ask a Question
**POST** `/ask`

Ask a natural language question about RiskMetric data.

#### Request
```http
POST /api/v1/riskmetric/ask?question=What would be the risk value at the price of Bitcoin of 134000?
```

#### Response
```json
{
    "question": "What would be the risk value at the price of Bitcoin of 134000?",
    "answer": "At a price of $134,000, Bitcoin would have a risk value of 0.6219, placing it in the 0.6-0.7 risk band (LATE BULL zone). This is considered 'Somewhat Uncommon' as BTC has spent 6.8% of its life (369 days) in this band.",
    "question_type": "RISK_CALCULATION",
    "symbol": "BTC",
    "data": {
        "price": 134000,
        "risk_value": 0.6219,
        "risk_band": "0.6-0.7",
        "zone": "LATE_BULL",
        "percentage_time": 6.8,
        "days_in_band": 369
    },
    "confidence": 0.95,
    "timestamp": "2025-08-06T14:30:00.000Z"
}
```

### 2. Get Example Questions
**GET** `/qa/examples`

Get categorized examples of questions that can be asked.

#### Response
```json
{
    "examples": [
        {
            "category": "Risk Calculation",
            "questions": [
                "What would be the risk value at the price of Bitcoin of 134000?",
                "What is the risk for ETH at $5000?",
                "Calculate risk for SOL at $200"
            ]
        },
        {
            "category": "Price from Risk",
            "questions": [
                "What BTC price corresponds to 0.8 risk?",
                "At what price would ETH have a risk of 0.5?",
                "What is the SOL price at risk 0.3?"
            ]
        }
    ],
    "total_categories": 7,
    "timestamp": "2025-08-06T14:30:00.000Z"
}
```

### 3. Batch Questions
**POST** `/qa/batch`

Process multiple questions in a single request.

#### Request
```json
[
    "What is the risk for BTC at $100000?",
    "What is the risk for ETH at $5000?",
    "What is the risk for SOL at $200?"
]
```

#### Response
```json
{
    "questions_processed": 3,
    "successful": 3,
    "results": [
        {
            "question": "What is the risk for BTC at $100000?",
            "answer": "At $100,000, BTC risk = 0.5105 (0.5-0.6 band, NEUTRAL zone)",
            "question_type": "RISK_CALCULATION",
            "confidence": 0.95,
            "success": true
        }
    ],
    "timestamp": "2025-08-06T14:30:00.000Z"
}
```

### 4. Get Q&A Statistics
**GET** `/qa/stats`

Get usage statistics for the Q&A system.

#### Response
```json
{
    "total_questions": 127,
    "question_types": {
        "RISK_CALCULATION": 45,
        "PRICE_FROM_RISK": 23,
        "TIME_SPENT": 18,
        "SYMBOL_INFO": 12,
        "FORMULA_EXPLANATION": 8,
        "COMPARISON": 15,
        "WIN_RATE": 6
    },
    "popular_symbols": ["BTC", "ETH", "SOL"],
    "average_confidence": 0.92,
    "timestamp": "2025-08-06T14:30:00.000Z"
}
```

### 5. Submit Feedback
**POST** `/qa/feedback`

Submit feedback about a Q&A response.

#### Request
```http
POST /api/v1/riskmetric/qa/feedback?question=What is BTC risk?&helpful=true&feedback=Very accurate response
```

## Question Types

### 1. Risk Calculation
Calculate risk value from a given price.
- "What would be the risk value at the price of Bitcoin of 134000?"
- "What is the risk for ETH at $5000?"
- "Calculate risk for SOL at $200"

### 2. Price from Risk
Calculate price from a given risk value.
- "What BTC price corresponds to 0.8 risk?"
- "At what price would ETH have a risk of 0.5?"
- "What is the SOL price at risk 0.3?"

### 3. Time Spent Analysis
Analyze time spent in risk bands.
- "What percentage of time has BTC spent in the 0.4-0.5 band?"
- "How many days has ETH been in the 0.6-0.7 band?"
- "Which band has SOL spent the most time in?"

### 4. Symbol Information
Get symbol-specific information.
- "How old is BTC in days?"
- "What is the life age of ETH?"
- "What are the min/max prices for SOL?"

### 5. Formula & Methodology
Explain the RiskMetric methodology.
- "Explain the risk formula"
- "How are coefficients calculated?"
- "What are the risk zones?"

### 6. Comparisons
Compare multiple symbols.
- "Compare BTC and ETH risk values"
- "Which symbol has the highest risk?"
- "Compare time spent distributions"

### 7. Win Rate Analysis
Analyze historical win rates.
- "What is the win rate for BTC at 0.3 risk?"
- "Calculate win rate for ETH at current price"
- "Which risk band has the best win rate?"

## Integration Examples

### Python
```python
import httpx
import asyncio

async def ask_riskmetric_question(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/riskmetric/ask",
            params={"question": question}
        )
        return response.json()

# Example usage
result = asyncio.run(ask_riskmetric_question(
    "What would be the risk value at the price of Bitcoin of 134000?"
))
print(f"Answer: {result['answer']}")
```

### JavaScript
```javascript
async function askRiskMetricQuestion(question) {
    const response = await fetch(
        `http://localhost:8000/api/v1/riskmetric/ask?question=${encodeURIComponent(question)}`,
        { method: 'POST' }
    );
    return await response.json();
}

// Example usage
askRiskMetricQuestion("What is the risk for BTC at $100000?")
    .then(result => console.log(`Answer: ${result.answer}`));
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/riskmetric/ask?question=What%20is%20the%20risk%20for%20BTC%20at%20%24100000%3F"
```

## Understanding Responses

### Risk Values
- Range: 0.0 to 1.0
- 0.0 = Minimum risk (at min price)
- 1.0 = Maximum risk (at max price)

### Risk Zones
- **0.00-0.25**: BUY ZONE (Strong accumulation opportunity)
- **0.25-0.40**: EARLY BULL (Early market recovery)
- **0.40-0.60**: NEUTRAL (Market equilibrium)
- **0.60-0.75**: LATE BULL (Market heating up)
- **0.75-1.00**: SELL ZONE (Distribution phase)

### Coefficients
Based on time spent rarity:
- **1.6x**: Ultra Rare (0% or <1% time spent)
- **1.55x**: Very Rare (1-2.5%)
- **1.5x**: Rare (2.5-5%)
- **1.4x**: Uncommon (5-10%)
- **1.3x**: Somewhat Uncommon (10-15%)
- **1.2x**: Below Average (15-20%)
- **1.1x**: Near Average (20-30%)
- **1.0x**: Common (>30%)

## Error Handling

### Common Errors
```json
{
    "detail": "Symbol BTC not found",
    "status_code": 404
}
```

```json
{
    "detail": "Error processing question: Unable to parse question",
    "status_code": 500
}
```

## Rate Limiting
- No rate limiting on Q&A endpoints currently
- Batch endpoint limited to 50 questions per request
- Recommended: Max 10 requests per second

## Best Practices

1. **Be Specific**: Include symbol names and exact values
   - Good: "What is the risk for BTC at $100000?"
   - Bad: "What is the risk?"

2. **Use Symbol Tickers**: Use standard tickers (BTC, ETH, SOL)
   - Good: "BTC risk at $100000"
   - Bad: "Bitcoin risk at 100k"

3. **Batch Similar Questions**: Use batch endpoint for multiple calculations
   - Reduces API calls
   - Faster response time

4. **Cache Responses**: Risk calculations are deterministic
   - Same price = same risk value
   - Cache results for frequently asked questions

## Support
For issues or questions about the RiskMetric Q&A API:
- Documentation: This file
- API Testing: Use `/api/v1/riskmetric/qa/examples` endpoint
- Feedback: Use `/api/v1/riskmetric/qa/feedback` endpoint

## Version
- API Version: 1.0.0
- RiskMetric Methodology: Benjamin Cowen's Into The Cryptoverse
- Last Updated: August 6, 2025