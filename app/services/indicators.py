"""
Technical indicators calculation service
"""


class IndicatorService:
    """Calculates technical indicators"""
    
    @staticmethod
    def calculate_ma(data: list, period: int) -> list:
        """Calculate moving average"""
        pass
    
    @staticmethod
    def calculate_rsi(data: list, period: int = 14) -> list:
        """Calculate RSI (Relative Strength Index)"""
        pass
    
    @staticmethod
    def calculate_macd(data: list) -> dict:
        """Calculate MACD"""
        pass
