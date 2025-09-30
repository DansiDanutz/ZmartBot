"""
Symbol Format Converter
Handles symbol format differences between exchanges:
- KuCoin: XBT for Bitcoin, USDTM for perpetual futures
- Binance: BTC for Bitcoin, USDT for all futures
"""
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class SymbolConverter:
    """
    Converts symbol formats between different exchanges
    Critical for proper trading execution
    """
    
    # KuCoin to Standard mappings
    KUCOIN_TO_STANDARD = {
        'XBT': 'BTC',  # Bitcoin on KuCoin is XBT
        'USDTM': 'USDT',  # Perpetual futures quote currency
        'USDM': 'USD',  # USD margined contracts
    }
    
    # Standard to KuCoin mappings (reverse)
    STANDARD_TO_KUCOIN = {
        'BTC': 'XBT',
        'USDT': 'USDTM',  # For futures
        'USD': 'USDM',
    }
    
    # Exchange-specific formats
    EXCHANGE_FORMATS = {
        'kucoin': {
            'futures_suffix': 'M',  # Perpetual contracts end with M
            'btc_symbol': 'XBT',
            'quote_currency': 'USDTM'
        },
        'binance': {
            'futures_suffix': '',  # No special suffix
            'btc_symbol': 'BTC',
            'quote_currency': 'USDT'
        }
    }
    
    @classmethod
    def to_kucoin_format(cls, symbol: str, is_futures: bool = True) -> str:
        """
        Convert standard symbol format to KuCoin format
        
        Examples:
            BTCUSDT -> XBTUSDTM (futures)
            ETHUSDT -> ETHUSDTM (futures)
            BTCUSDT -> XBTUSDT (spot, not used in our system)
        """
        if not symbol:
            return symbol
            
        # Handle BTC special case
        if 'BTC' in symbol:
            symbol = symbol.replace('BTC', 'XBT')
        
        # Handle futures quote currency
        if is_futures:
            # Check if it already has the M suffix
            if not symbol.endswith('M'):
                # Replace USDT with USDTM for futures
                if symbol.endswith('USDT'):
                    symbol = symbol[:-4] + 'USDTM'
                elif symbol.endswith('USD'):
                    symbol = symbol[:-3] + 'USDM'
        
        return symbol
    
    @classmethod
    def to_binance_format(cls, symbol: str) -> str:
        """
        Convert any format to Binance standard format
        
        Examples:
            XBTUSDTM -> BTCUSDT
            XBTUSDT -> BTCUSDT
            ETHUSDTM -> ETHUSDT
            1000000MOG/USDT:USDT -> 1000000MOGUSDT
        """
        if not symbol:
            return symbol
            
        # Handle new KuCoin format with separators (e.g., "1000000MOG/USDT:USDT")
        if '/' in symbol and ':' in symbol:
            # Extract base and quote from format like "1000000MOG/USDT:USDT"
            parts = symbol.split('/')
            if len(parts) == 2:
                base = parts[0]
                quote_part = parts[1]
                if ':' in quote_part:
                    quote = quote_part.split(':')[0]
                    return f"{base}{quote}"
        
        # Handle old KuCoin format
        # Remove futures suffix if present
        if symbol.endswith('USDTM'):
            symbol = symbol[:-5] + 'USDT'
        elif symbol.endswith('USDM'):
            symbol = symbol[:-4] + 'USD'
        elif symbol.endswith('M') and not symbol.endswith('USDTM'):
            # Remove trailing M if it's not part of USDTM
            symbol = symbol[:-1]
        
        # Handle XBT -> BTC conversion
        if 'XBT' in symbol:
            symbol = symbol.replace('XBT', 'BTC')
        
        return symbol
    
    @classmethod
    def to_standard_format(cls, symbol: str) -> str:
        """
        Convert any exchange format to standard format (Binance-style)
        This is the format we use internally
        
        Examples:
            XBTUSDTM -> BTCUSDT
            BTCUSDT -> BTCUSDT (no change)
        """
        return cls.to_binance_format(symbol)
    
    @classmethod
    def convert_symbol(cls, symbol: str, from_exchange: str, to_exchange: str, is_futures: bool = True) -> str:
        """
        Convert symbol between any two exchanges
        
        Args:
            symbol: The symbol to convert
            from_exchange: Source exchange ('kucoin', 'binance', 'standard')
            to_exchange: Target exchange ('kucoin', 'binance', 'standard')
            is_futures: Whether this is for futures trading
            
        Returns:
            Converted symbol in target exchange format
        """
        # Normalize exchange names
        from_exchange = from_exchange.lower()
        to_exchange = to_exchange.lower()
        
        # First convert to standard format
        if from_exchange == 'kucoin':
            standard_symbol = cls.to_standard_format(symbol)
        elif from_exchange == 'binance' or from_exchange == 'standard':
            standard_symbol = symbol
        else:
            logger.warning(f"Unknown source exchange: {from_exchange}, treating as standard")
            standard_symbol = symbol
        
        # Then convert to target format
        if to_exchange == 'kucoin':
            return cls.to_kucoin_format(standard_symbol, is_futures)
        elif to_exchange == 'binance' or to_exchange == 'standard':
            return standard_symbol
        else:
            logger.warning(f"Unknown target exchange: {to_exchange}, returning standard format")
            return standard_symbol
    
    @classmethod
    def parse_symbol(cls, symbol: str) -> Dict[str, str]:
        """
        Parse a symbol into its components
        
        Returns:
            Dict with 'base', 'quote', 'format' keys
        """
        # Determine format
        if 'XBT' in symbol:
            format_type = 'kucoin'
        elif symbol.endswith('USDTM') or symbol.endswith('USDM'):
            format_type = 'kucoin'
        else:
            format_type = 'standard'
        
        # Convert to standard for parsing
        standard_symbol = cls.to_standard_format(symbol)
        
        # Parse base and quote
        if standard_symbol.endswith('USDT'):
            base = standard_symbol[:-4]
            quote = 'USDT'
        elif standard_symbol.endswith('BUSD'):
            base = standard_symbol[:-4]
            quote = 'BUSD'
        elif standard_symbol.endswith('USD'):
            base = standard_symbol[:-3]
            quote = 'USD'
        else:
            # Default assumption
            base = standard_symbol[:3]
            quote = standard_symbol[3:]
        
        return {
            'base': base,
            'quote': quote,
            'format': format_type,
            'original': symbol,
            'standard': standard_symbol
        }
    
    @classmethod
    def validate_symbol_format(cls, symbol: str, exchange: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a symbol is in the correct format for an exchange
        
        Returns:
            (is_valid, corrected_symbol_or_none)
        """
        exchange = exchange.lower()
        
        if exchange == 'kucoin':
            # Check if it's in KuCoin format
            if ('XBT' in symbol or symbol.endswith('USDTM') or symbol.endswith('USDM')):
                return True, None
            else:
                # Convert to KuCoin format
                corrected = cls.to_kucoin_format(symbol)
                return False, corrected
                
        elif exchange == 'binance':
            # Check if it's in Binance format
            if not ('XBT' in symbol or symbol.endswith('USDTM') or symbol.endswith('M')):
                return True, None
            else:
                # Convert to Binance format
                corrected = cls.to_binance_format(symbol)
                return False, corrected
        
        return True, None
    
    @classmethod
    def get_all_formats(cls, symbol: str) -> Dict[str, str]:
        """
        Get all possible formats for a symbol
        
        Returns:
            Dict with all exchange formats
        """
        standard = cls.to_standard_format(symbol)
        
        return {
            'standard': standard,
            'binance': cls.to_binance_format(symbol),
            'kucoin_futures': cls.to_kucoin_format(standard, is_futures=True),
            'kucoin_spot': cls.to_kucoin_format(standard, is_futures=False),
        }

# Convenience functions
def to_kucoin(symbol: str, is_futures: bool = True) -> str:
    """Quick conversion to KuCoin format"""
    return SymbolConverter.to_kucoin_format(symbol, is_futures)

def to_binance(symbol: str) -> str:
    """Quick conversion to Binance format"""
    return SymbolConverter.to_binance_format(symbol)

def to_standard(symbol: str) -> str:
    """Quick conversion to standard format"""
    return SymbolConverter.to_standard_format(symbol)

def convert(symbol: str, from_exchange: str, to_exchange: str) -> str:
    """Quick symbol conversion between exchanges"""
    return SymbolConverter.convert_symbol(symbol, from_exchange, to_exchange)