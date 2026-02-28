import threading
import order_queue as oq
import market_data as m
import time
import heapq

# TODO implement max heap to store SymbolStat values, rethink how time_strength and stability_strength are used in
#  comparisons


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
        self.time_strength: float = 0.0
        self.strength: float = 0.0

    def set_strength(self) -> float:
        self.strength = self.time_strength - self.stability_strength
        return self.strength

    def __eq__(self, other: "SymbolStat") -> bool:
        return self.strength == other.strength

    def __lt__(self, other: "SymbolStat") -> bool:
        return self.strength < other.strength

    def __le__(self, other: "SymbolStat") -> bool:
        return self.strength <= other.strength

    def __gt__(self, other: "SymbolStat") -> bool:
        return self.strength > other.strength

    def __ge__(self, other: "SymbolStat") -> bool:
        return self.strength >= other.strength


class DataAnalysis:
    tradable_symbol_stats_heap: list[SymbolStat] = []

    @staticmethod
    def __calculate_linear_regression_by_least_squares(symbol_data: list[dict[str, float | int | str]]) -> tuple[float, float]:
        """
        Calculates the line of best fit in O(n) then returns the slope and y-intercept
        :param list[dict[str, float | int | str]] as symbol_data: list of data about a certain symbol, dict must contain "vw" for average price
        :return tuple[float, float]: slope, y-intercept
        """
        n: float = 0.0
        sum_of_xy: float = 0.0
        sum_of_x: float = 0.0
        sum_of_y: float = 0.0
        sum_of_xx: float = 0.0

        for symbol_info in symbol_data:
            sum_of_x += n
            sum_of_xy += n * symbol_info["vw"]  # volume weighted average price
            sum_of_y += symbol_info["vw"]
            sum_of_xx += n * n
            n += 1.0

        slope: float = (n * sum_of_xy - sum_of_x * sum_of_y) / (n * sum_of_xx - sum_of_x * sum_of_x)
        y_intercept: float = (sum_of_y - slope * sum_of_x) / n

        return slope, y_intercept

    @staticmethod
    def analyze_requested_historical_bars(days_ago: int = 1825, timeframe: str = "1Day", window_percent: float = 0.01) -> None:
        """
        This method analyzes historical bar data for all tradable bars in MarketData.paper_symbol_tradable from some
        amount of days ago passed as the days_ago parameter to the current day.

        One analysis it does is by calculating stability_strength which is a 0.0 or negative value that represents the
        average percent the price was off from the expected price using the line of best fit. For example lets say we
        have points (x,y): (0,0), (1,1), (2,3), (3,4), (4,2) the line of best fit would be y = 0.4730x + 0.9595
        (used online calculator), if we plug in 0 for x the expected value would be 0.9595 then
        abs(0 (actual value) - 0.9595 (expected value)) / 0.9595 = 1.0 so the current stability_strength 0.0 would now
        be 0.0 - 1.0 then we repeat the same process for all the other data points and at the end divide do
        stability_strength = stability_strength / number of data points to get the average percent off.

        The next analysis is time_strength which analyzes which is a positive, negative or 0.0 value that represents
        the weighted average percent change of all the windows determined by window_percent. Lets say we have 50 data
        points and the window_percent is 0.1 then each window_size will be 5 data points, keep in mind if we had 51 data
        points the window_size will still be 5 but the last data point will be its own window. It analyzes the most
        recent windows at the end of the list first, for each window it calculates the line of best fit then determines
        the percent change by strength_multiplier * (end value / start value (aka y_intercept)). The strength_multiplier
        starts at 16 for the first window then divides by 2 for each window until it hits 1 and stays at 1. The
        strength_multiplier is to increase the importance of recent bar data. Each value calculated for the window is
        added to time_strength which starts at 0.0 so positive percent changes increase it and negative percent changes
        decrease it. At the end time_strength = time_strength / number of windows to get the AVERAGE weighted
        percent change of all windows.

        :param int as days_ago: How many days back from the previous day should the data be retrieved from
        :param str as timeframe: Time inbetween each datapoint
        :param float as window_percent: Approximate percent of the data that will represent each window that will be analyzed for time_strength
        :return:
        """
        if m.MarketData.paper_symbol_tradable is None:
            return

        for symbol, tradable in m.MarketData.paper_symbol_tradable.items():
            if not tradable:
                continue

            symbol_data: list[dict[str, float | int | str]] = m.MarketData.request_past_prices(
                symbol=symbol,
                timeframe=timeframe,
                days_ago=days_ago,  # Defaults to data since 5 years ago
                data_points=None
            ).get(symbol)
            symbol_data_len: int = len(symbol_data)

            #if symbol_data_len < days_ago >> 1:
            #    continue

            slope, y_intercept = DataAnalysis.__calculate_linear_regression_by_least_squares(symbol_data)

            symbol_stats: SymbolStat = SymbolStat(symbol)
            curr_x: float = 0.0
            expected_value: float
            for symbol_info in symbol_data:
                """
                Weighted value that day / expected value, so stability strength decreases relative to the percent 
                the price was off from the expected price
                """
                expected_value = slope * curr_x + y_intercept
                if expected_value != 0.0:
                    symbol_stats.stability_strength -= abs(abs(symbol_info["vw"] - expected_value) / expected_value)
                curr_x += 1.0
            symbol_stats.stability_strength /= symbol_data_len

            window_size: int = max(1, int(symbol_data_len * window_percent))
            start_index: int = symbol_data_len - window_size
            end_index: int = symbol_data_len
            time_strength_multiplier: int = 16
            num_windows: int = 0
            while end_index > start_index:
                slope, y_intercept = DataAnalysis.__calculate_linear_regression_by_least_squares(
                    symbol_data[start_index:end_index]
                )

                symbol_stats.time_strength += (
                    time_strength_multiplier * ((slope * (end_index - start_index - 1) + y_intercept) / y_intercept - 1)
                )

                end_index = start_index
                start_index = max(0, start_index - window_size)
                num_windows += 1

                if time_strength_multiplier > 1:
                    time_strength_multiplier >>= 1
            symbol_stats.time_strength /= num_windows
            symbol_stats.set_strength()
            DataAnalysis.tradable_symbol_stats_heap.append(symbol_stats)

        heapq.heapify(DataAnalysis.tradable_symbol_stats_heap)
