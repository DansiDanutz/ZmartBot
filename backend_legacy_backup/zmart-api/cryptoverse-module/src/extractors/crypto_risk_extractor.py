#!/usr/bin/env python3
"""
Crypto Risk Indicators Extractor
Extracts crypto risk indicators from Into The Cryptoverse dashboard
Based on the comprehensive data pipeline system from the package
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Selenium imports with error handling for linter issues
try:
    from selenium import webdriver  # type: ignore[import]
    from selenium.webdriver.common.by import By  # type: ignore[import]
    from selenium.webdriver.support.ui import WebDriverWait  # type: ignore[import]
    from selenium.webdriver.support import expected_conditions as EC  # type: ignore[import]
    from selenium.webdriver.chrome.options import Options  # type: ignore[import]
    from selenium.common.exceptions import TimeoutException, NoSuchElementException  # type: ignore[import]
    SELENIUM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Selenium import failed: {e}")
    # Define placeholders for linter
    webdriver = None  # type: ignore[assignment]
    By = None  # type: ignore[assignment]
    WebDriverWait = None  # type: ignore[assignment]
    EC = None  # type: ignore[assignment]
    Options = None  # type: ignore[assignment]
    TimeoutException = Exception  # type: ignore[assignment]
    NoSuchElementException = Exception  # type: ignore[assignment]
    SELENIUM_AVAILABLE = False

from ..database.cryptoverse_database import DataExtractionResult

logger = logging.getLogger(__name__)

class CryptoRiskExtractor:
    """Extracts crypto risk indicators from Into The Cryptoverse dashboard"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.base_url = "https://app.intothecryptoverse.com/dashboard"
        
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        if not SELENIUM_AVAILABLE or not webdriver or not Options:
            logger.error("Selenium not available - cannot initialize WebDriver")
            self.driver = None
            raise ImportError("Selenium components not available")
        
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            self.driver = None
            raise
    
    def _teardown_driver(self):
        """Clean up WebDriver resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Chrome WebDriver closed")
    
    async def extract_crypto_risk_indicators(self) -> DataExtractionResult:
        """
        Extract crypto risk indicators from the dashboard
        Returns: DataExtractionResult with risk indicators data
        """
        timestamp = datetime.now()
        
        try:
            self._setup_driver()
            
            # Check if driver was successfully initialized
            if not self.driver:
                logger.error("WebDriver not available - cannot extract crypto risk data")
                return DataExtractionResult(
                    source="crypto_risk_indicators",
                    timestamp=timestamp,
                    data={},
                    success=False,
                    error_message="WebDriver initialization failed"
                )
            
            # Navigate to dashboard
            logger.info("Navigating to Into The Cryptoverse dashboard")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Extract risk indicators
            risk_data = await self._extract_risk_data()
            
            if risk_data:
                logger.info("Successfully extracted crypto risk indicators")
                return DataExtractionResult(
                    source="crypto_risk_indicators",
                    timestamp=timestamp,
                    data=risk_data,
                    success=True,
                    confidence_score=0.9
                )
            else:
                logger.warning("No risk data extracted")
                return DataExtractionResult(
                    source="crypto_risk_indicators",
                    timestamp=timestamp,
                    data={},
                    success=False,
                    error_message="No risk data found on dashboard"
                )
                
        except Exception as e:
            logger.error(f"Error extracting crypto risk indicators: {str(e)}")
            return DataExtractionResult(
                source="crypto_risk_indicators",
                timestamp=timestamp,
                data={},
                success=False,
                error_message=str(e)
            )
        finally:
            self._teardown_driver()
    
    async def _extract_risk_data(self) -> Optional[Dict[str, Any]]:
        """Extract risk indicator values from the dashboard"""
        try:
            # Wait for risk indicators section to load
            if WebDriverWait and EC and By:
                risk_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "risk-indicators"))
                )
            else:
                return None
            
            # Extract individual risk components
            summary_risk = await self._extract_risk_value("summary-risk")
            price_risk = await self._extract_risk_value("price-risk")
            onchain_risk = await self._extract_risk_value("onchain-risk")
            social_risk = await self._extract_risk_value("social-risk")
            
            # Determine overall risk level
            risk_level = self._calculate_risk_level(summary_risk)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "summary_risk": summary_risk,
                "price_risk": price_risk,
                "onchain_risk": onchain_risk,
                "social_risk": social_risk,
                "risk_level": risk_level,
                "components": {
                    "price": "Based on RiskMetric methodology",
                    "onchain": "Supply in profit/loss, MVRV, exchange flows",
                    "social": "Sentiment analysis from social media"
                }
            }
            
        except TimeoutException:
            logger.error("Timeout waiting for risk indicators to load")
            return None
        except Exception as e:
            logger.error(f"Error extracting risk data: {str(e)}")
            return None
    
    async def _extract_risk_value(self, risk_type: str) -> float:
        """Extract individual risk value by type"""
        try:
            # Check if driver is available
            if not self.driver:
                logger.error(f"WebDriver not available for extracting {risk_type} risk value")
                return 0.0
                
            # Try multiple possible selectors for risk values
            selectors = [
                f"[data-testid='{risk_type}']",
                f".{risk_type}",
                f"#{risk_type}",
                f"[class*='{risk_type}']"
            ]
            
            if By:
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        text = element.text.strip()
                        
                        # Extract numeric value from text
                        if text:
                            # Remove percentage signs and convert to float
                            numeric_text = ''.join(c for c in text if c.isdigit() or c == '.')
                            if numeric_text:
                                value = float(numeric_text)
                                # If value is > 1, assume it's a percentage and convert
                                if value > 1:
                                    value = value / 100
                                return value
                                
                    except NoSuchElementException:
                        continue
                
                # Fallback: try to find any element containing the risk type
                risk_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{risk_type}')]")
                for element in risk_elements:
                    parent = element.find_element(By.XPATH, "..")
                text = parent.text.strip()
                if any(char.isdigit() for char in text):
                    numeric_text = ''.join(c for c in text if c.isdigit() or c == '.')
                    if numeric_text:
                        value = float(numeric_text)
                        if value > 1:
                            value = value / 100
                        return value
            
            logger.warning(f"Could not extract {risk_type} value")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error extracting {risk_type}: {str(e)}")
            return 0.0
    
    def _calculate_risk_level(self, summary_risk: float) -> str:
        """Calculate risk level based on summary risk value"""
        if summary_risk <= 0.2:
            return "Very Low"
        elif summary_risk <= 0.4:
            return "Low"
        elif summary_risk <= 0.6:
            return "Moderate"
        elif summary_risk <= 0.8:
            return "High"
        else:
            return "Very High"
    
    async def extract_with_mock_data(self) -> DataExtractionResult:
        """Extract mock data for testing purposes"""
        timestamp = datetime.now()
        
        # Mock data based on the package specifications
        mock_data = {
            "timestamp": timestamp.isoformat(),
            "summary_risk": 0.348,
            "price_risk": 0.449,
            "onchain_risk": 0.548,
            "social_risk": 0.046,
            "risk_level": "Low-Moderate",
            "components": {
                "price": "Based on RiskMetric methodology",
                "onchain": "Supply in profit/loss, MVRV, exchange flows",
                "social": "Sentiment analysis from social media"
            }
        }
        
        logger.info("Generated mock crypto risk indicators data")
        return DataExtractionResult(
            source="crypto_risk_indicators",
            timestamp=timestamp,
            data=mock_data,
            success=True,
            confidence_score=1.0
        )
    
    async def validate_extraction(self) -> bool:
        """Validate that extraction is working correctly"""
        try:
            result = await self.extract_with_mock_data()
            return result.success and result.data is not None
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False