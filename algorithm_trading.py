import threading
import order_queue as oq
import market_data as m
import time


class SymbolStat:
    """
    Each instance of this class holds a symbol, stability_strength and time_strength used to determine which symbol
    is better, strengths documented in the __init__ method.
    """
    def __init__(self, symbol: str):
        """
        stability_strength is how close all the data points are to the line of best fit, max score is 0.0
        time_strength is how consistent the graph is increasing, min score is 0
        :param str as symbol:
        """
        self.symbol: str = symbol
        self.stability_strength: float = 0.0
        self.time_strength: int = 0

    def __eq__(self, other: "SymbolStat") -> bool:
        return (self.time_strength, self.stability_strength) == (other.time_strength, other.stability_strength)

    def __lt__(self, other: "SymbolStat") -> bool:
        return (self.time_strength, self.stability_strength) < (other.time_strength, other.stability_strength)

    def __le__(self, other: "SymbolStat") -> bool:
        return (self.time_strength, self.stability_strength) <= (other.time_strength, other.stability_strength)

    def __gt__(self, other: "SymbolStat") -> bool:
        return (self.time_strength, self.stability_strength) > (other.time_strength, other.stability_strength)

    def __ge__(self, other: "SymbolStat") -> bool:
        return (self.time_strength, self.stability_strength) >= (other.time_strength, other.stability_strength)


class DataAnalysis:
    all_symbol_stats: list[SymbolStat] = []


    @staticmethod
    def analyze_requested_historical_bars() -> None:
        if m.MarketData.paper_symbol_tradable is None:
            return

        for symbol, tradable in m.MarketData.paper_symbol_tradable.items():
            if tradable:
                m.MarketData.request_past_prices(
                    symbol=symbol,
                    timeframe="1Day",
                    days_ago=1825,  # Data since 5 years ago
                    data_points=None
                )

