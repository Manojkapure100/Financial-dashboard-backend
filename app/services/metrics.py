"""
Metrics calculation service
"""


class MetricsService:
    """Calculates various financial metrics"""
    
    @staticmethod
    def calculate_returns(prices: list) -> float:
        """Calculate returns"""
        pass
    
    @staticmethod
    def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe Ratio"""
        pass
    
    @staticmethod
    def calculate_max_drawdown(prices: list) -> float:
        """Calculate maximum drawdown"""
        pass
