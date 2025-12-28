"""
Let's keep this extremely simple for now. 

Rules:
1. Bot will only be allowed to buy or sell one symbol. (it can only own a single symbol throughout its lifetime)
2. Our algorithm for buy-sell will the moving average trend following: basically we check the average of the stock prices at their closing for the past
n dates and if the current price is above the moving average we buy, if its below we sell. For now, n = 20. 



"""

import market_data
import utilities as u

m = market_data.MarketData(use_bot=True)

class Bot:
    def __init__(self, symbol: str) -> None:
        """
        Initializes the bot with some specific configurations. 
        :param symbol: The stock symbol that the bot will trade.
        """
        if u.no_trading_client():
            raise ValueError("Trading client is not set. Please set API keys before initializing the bot.")
        if not u.paper_symbol_exists(symbol):
            raise ValueError(f"The symbol {symbol} does not exist, please use a valid symbol.")
        
        self.symbol = symbol

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass 

    def buy(self) -> None:
        pass
    
    def sell(self) -> None:
        pass

    def analyze_market(self) -> None:
        """
        This method analyzes the market data to make buy/sell decisions based on moving average trend following.
        NOTE: I will need to check if the function also contains the data for today as well, as it is supposed to compare the current price.
        """
        past_data = m.past_prices(self.symbol, timeframe='1Day', start_int=20)  # This will return the past 20 days of data in incremennts of 1 day.
        past_data = past_data[self.symbol]

        current_data = m.current_prices(self.symbol)
        current_data[self.symbol]

        return past_data, current_data
    
    def make_decision(self) -> None:
        """
        This method, will either buy, sell, or do nothing with the stock. 
        NOTE: I will need to also add something that decides how much to buy or sell as well. Need to look into this more.

        """
        
        past_data, current_data = self.analyze_market()

        closing_prices = [day['c'] for day in past_data]

        avg_c = sum(closing_prices) / len(closing_prices)


        """NOTE: I am not sure if its right to use the opening price for the current day. 
        Also, depending on the time, this might actually return data from the previous day, so I have to look into this as well."""
        current_price = current_data[self.symbol]['o']

        if avg_c < current_price: 
            self.buy()
        elif avg_c > current_price:
            self.sell()