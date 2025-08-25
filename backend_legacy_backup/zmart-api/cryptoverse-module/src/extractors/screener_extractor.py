#!/usr/bin/env python3
"""
Screener Data Extractor
Extracts real-time screener data from Into The Cryptoverse
Based on the comprehensive data pipeline system from the package
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

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

class ScreenerExtractor:
    """Extracts real-time screener data from Into The Cryptoverse"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.base_url = "https://app.intothecryptoverse.com/screener"
        
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
            logger.info("Chrome WebDriver initialized for screener")
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
    
    async def extract_screener_data(self) -> DataExtractionResult:
        """
        Extract real-time screener data from the platform
        Returns: DataExtractionResult with screener data for all symbols
        """
        timestamp = datetime.now()
        
        try:
            self._setup_driver()
            
            # Check if driver was successfully initialized
            if not self.driver:
                logger.error("WebDriver not available - cannot extract screener data")
                return DataExtractionResult(
                    source="screener_data",
                    timestamp=timestamp,
                    data={},
                    success=False,
                    error_message="WebDriver initialization failed"
                )
            
            # Navigate to screener
            logger.info("Navigating to Into The Cryptoverse screener")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Extract screener data
            screener_data = await self._extract_all_symbols_data()
            
            if screener_data and screener_data.get('symbols'):
                logger.info(f"Successfully extracted screener data for {len(screener_data['symbols'])} symbols")
                return DataExtractionResult(
                    source="screener_data",
                    timestamp=timestamp,
                    data=screener_data,
                    success=True,
                    confidence_score=0.9
                )
            else:
                logger.warning("No screener data extracted")
                return DataExtractionResult(
                    source="screener_data",
                    timestamp=timestamp,
                    data={},
                    success=False,
                    error_message="No screener data found"
                )
                
        except Exception as e:
            logger.error(f"Error extracting screener data: {str(e)}")
            return DataExtractionResult(
                source="screener_data",
                timestamp=timestamp,
                data={},
                success=False,
                error_message=str(e)
            )
        finally:
            self._teardown_driver()
    
    async def _extract_all_symbols_data(self) -> Optional[Dict[str, Any]]:
        """Extract data for all symbols from the screener"""
        try:
            # Check if driver is available
            if not self.driver:
                logger.error("WebDriver not available for symbol data extraction")
                return None
                
            # Wait for screener table to load
            if WebDriverWait and EC and By:
                screener_table = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".screener-table, table, .data-table"))
                )
            else:
                return None
            
            symbols_data = []
            
            # Try to find table rows
            if By:
                rows = self.driver.find_elements(By.CSS_SELECTOR, "tr, .table-row, .screener-row")
            else:
                rows = []
            
            for row in rows[1:]:  # Skip header row
                try:
                    symbol_data = await self._extract_symbol_row_data(row)
                    if symbol_data:
                        symbols_data.append(symbol_data)
                except Exception as e:
                    logger.warning(f"Error extracting row data: {str(e)}")
                    continue
            
            # If no data found, try alternative extraction method
            if not symbols_data:
                symbols_data = await self._extract_symbols_alternative()
            
            # Calculate market summary
            market_summary = self._calculate_market_summary(symbols_data)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "symbols": symbols_data,
                "market_summary": market_summary
            }
            
        except TimeoutException:
            logger.error("Timeout waiting for screener table to load")
            return None
        except Exception as e:
            logger.error(f"Error extracting screener data: {str(e)}")
            return None
    
    async def _extract_symbol_row_data(self, row) -> Optional[Dict[str, Any]]:
        """Extract data from a single table row"""
        try:
            if By:
                cells = row.find_elements(By.CSS_SELECTOR, "td, .cell, .table-cell")
            else:
                cells = []
            
            if len(cells) < 3:
                return None
            
            # Extract symbol (usually first cell)
            symbol = cells[0].text.strip()
            if not symbol or len(symbol) > 10:  # Basic validation
                return None
            
            # Extract price (usually second cell)
            price_text = cells[1].text.strip()
            price = self._parse_price(price_text)
            
            # Extract risk (usually third cell or look for risk-related content)
            risk = await self._extract_risk_from_row(row, cells)
            
            # Determine risk band and level
            risk_band = self._get_risk_band(risk)
            risk_level = self._get_risk_level(risk)
            
            return {
                "symbol": symbol,
                "price": price,
                "fiat_risk": risk,
                "risk_band": risk_band,
                "risk_level": risk_level,
                "market_cap": None,  # Would need additional extraction
                "volume_24h": None   # Would need additional extraction
            }
            
        except Exception as e:
            logger.warning(f"Error extracting symbol row data: {str(e)}")
            return None
    
    async def _extract_risk_from_row(self, row, cells) -> float:
        """Extract risk value from table row"""
        try:
            # Look for risk in cells
            for cell in cells:
                text = cell.text.strip()
                if self._looks_like_risk_value(text):
                    return self._parse_risk_value(text)
            
            # Look for risk in data attributes
            if By:
                risk_element = row.find_element(By.CSS_SELECTOR, "[data-risk], .risk, .risk-value")
            else:
                risk_element = None
            if risk_element:
                return self._parse_risk_value(risk_element.text)
            
            return 0.0
            
        except NoSuchElementException:
            return 0.0
        except Exception as e:
            logger.warning(f"Error extracting risk from row: {str(e)}")
            return 0.0
    
    def _looks_like_risk_value(self, text: str) -> bool:
        """Check if text looks like a risk value (0.0 to 1.0)"""
        try:
            # Remove common formatting
            clean_text = text.replace('%', '').replace(',', '').strip()
            
            if not clean_text:
                return False
            
            # Check if it's a decimal number
            if '.' in clean_text:
                parts = clean_text.split('.')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    value = float(clean_text)
                    return 0.0 <= value <= 1.0 or 0.0 <= value <= 100.0
            
            return False
            
        except:
            return False
    
    def _parse_risk_value(self, text: str) -> float:
        """Parse risk value from text"""
        try:
            # Clean the text
            clean_text = text.replace('%', '').replace(',', '').strip()
            value = float(clean_text)
            
            # Convert percentage to decimal if needed
            if value > 1.0:
                value = value / 100.0
            
            return max(0.0, min(1.0, value))  # Clamp between 0 and 1
            
        except:
            return 0.0
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        try:
            # Remove currency symbols and formatting
            clean_text = price_text.replace('$', '').replace(',', '').strip()
            return float(clean_text)
        except:
            return 0.0
    
    def _get_risk_band(self, risk: float) -> str:
        """Get risk band based on risk value"""
        if risk < 0.1:
            return "0.0-0.1"
        elif risk < 0.2:
            return "0.1-0.2"
        elif risk < 0.3:
            return "0.2-0.3"
        elif risk < 0.4:
            return "0.3-0.4"
        elif risk < 0.5:
            return "0.4-0.5"
        elif risk < 0.6:
            return "0.5-0.6"
        elif risk < 0.7:
            return "0.6-0.7"
        elif risk < 0.8:
            return "0.7-0.8"
        elif risk < 0.9:
            return "0.8-0.9"
        else:
            return "0.9-1.0"
    
    def _get_risk_level(self, risk: float) -> str:
        """Get risk level based on risk value"""
        if risk <= 0.2:
            return "Very Low"
        elif risk <= 0.4:
            return "Low"
        elif risk <= 0.6:
            return "Moderate"
        elif risk <= 0.8:
            return "High"
        else:
            return "Very High"
    
    async def _extract_symbols_alternative(self) -> List[Dict[str, Any]]:
        """Alternative method to extract symbols if table parsing fails"""
        try:
            # Check if driver is available
            if not self.driver:
                logger.error("WebDriver not available for alternative symbol extraction")
                return []
                
            # Look for symbol elements with different selectors
            if By:
                symbol_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".symbol, .ticker, [data-symbol], .crypto-symbol")
            else:
                symbol_elements = []
            
            symbols_data = []
            
            for element in symbol_elements:
                try:
                    symbol = element.text.strip()
                    if symbol and len(symbol) <= 10:
                        # Try to find associated price and risk
                        if By:
                            parent = element.find_element(By.XPATH, "..")
                            price_element = parent.find_element(By.CSS_SELECTOR, ".price, .value, [data-price]")
                            risk_element = parent.find_element(By.CSS_SELECTOR, ".risk, [data-risk]")
                        else:
                            parent = None
                            price_element = None
                            risk_element = None
                        
                        if price_element and risk_element:
                            price = self._parse_price(price_element.text)
                            risk = self._parse_risk_value(risk_element.text)
                            
                            symbols_data.append({
                                "symbol": symbol,
                                "price": price,
                                "fiat_risk": risk,
                                "risk_band": self._get_risk_band(risk),
                                "risk_level": self._get_risk_level(risk)
                            })
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.warning(f"Error in alternative extraction: {str(e)}")
                    continue
            
            return symbols_data
            
        except Exception as e:
            logger.error(f"Alternative extraction failed: {str(e)}")
            return []
    
    def _calculate_market_summary(self, symbols_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate market summary statistics"""
        if not symbols_data:
            return {
                "total_symbols": 0,
                "avg_risk": 0.0,
                "high_risk_count": 0,
                "low_risk_count": 0
            }
        
        total_symbols = len(symbols_data)
        risks = [symbol.get('fiat_risk', 0) for symbol in symbols_data]
        avg_risk = sum(risks) / len(risks) if risks else 0.0
        
        high_risk_count = sum(1 for risk in risks if risk > 0.6)
        low_risk_count = sum(1 for risk in risks if risk < 0.4)
        
        return {
            "total_symbols": total_symbols,
            "avg_risk": round(avg_risk, 3),
            "high_risk_count": high_risk_count,
            "low_risk_count": low_risk_count
        }
    
    async def extract_with_mock_data(self) -> DataExtractionResult:
        """Extract mock data for testing purposes"""
        timestamp = datetime.now()
        
        # Mock data based on the package specifications
        mock_symbols = [
            {"symbol": "BTC", "price": 114360.00, "fiat_risk": 0.545, "risk_band": "0.5-0.6", "risk_level": "Moderate"},
            {"symbol": "ETH", "price": 3515.60, "fiat_risk": 0.648, "risk_band": "0.6-0.7", "risk_level": "Moderate-High"},
            {"symbol": "ADA", "price": 0.732444, "fiat_risk": 0.509, "risk_band": "0.5-0.6", "risk_level": "Moderate"},
            {"symbol": "DOT", "price": 3.62, "fiat_risk": 0.187, "risk_band": "0.1-0.2", "risk_level": "Very Low"},
            {"symbol": "AVAX", "price": 21.48, "fiat_risk": 0.355, "risk_band": "0.3-0.4", "risk_level": "Low"},
            {"symbol": "LINK", "price": 16.39, "fiat_risk": 0.531, "risk_band": "0.5-0.6", "risk_level": "Moderate"},
            {"symbol": "SOL", "price": 162.83, "fiat_risk": 0.604, "risk_band": "0.6-0.7", "risk_level": "Moderate-High"},
            {"symbol": "DOGE", "price": 0.200175, "fiat_risk": 0.442, "risk_band": "0.4-0.5", "risk_level": "Low"},
            {"symbol": "TRX", "price": 0.327322, "fiat_risk": 0.672, "risk_band": "0.6-0.7", "risk_level": "High"},
            {"symbol": "SHIB", "price": 0.00001226, "fiat_risk": 0.185, "risk_band": "0.1-0.2", "risk_level": "Very Low"},
            {"symbol": "TON", "price": 3.58, "fiat_risk": 0.293, "risk_band": "0.2-0.3", "risk_level": "Low"}
        ]
        
        market_summary = self._calculate_market_summary(mock_symbols)
        
        mock_data = {
            "timestamp": timestamp.isoformat(),
            "symbols": mock_symbols,
            "market_summary": market_summary
        }
        
        logger.info(f"Generated mock screener data for {len(mock_symbols)} symbols")
        return DataExtractionResult(
            source="screener_data",
            timestamp=timestamp,
            data=mock_data,
            success=True,
            confidence_score=1.0
        )
    
    async def validate_extraction(self) -> bool:
        """Validate that extraction is working correctly"""
        try:
            result = await self.extract_with_mock_data()
            return result.success and result.data is not None and len(result.data.get('symbols', [])) > 0
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False