"""
Let's keep this extremely simple for now. 

Rules:
1. Bot will only be allowed to buy or sell one symbol. (it can only own a single symbol throughout its lifetime)
2. Our algorithm for buy-sell will the moving average trend following: basically we check the average of the stock prices at their closing for the past
n dates and if the current price is above the moving average we buy, if its below we sell. For now, n = 20. 



"""

import market_data
import utilities as u
import order as o
import order_queue as q
from datetime import datetime
import time
from typing import Tuple

m = market_data.MarketData(use_bot=True)

class Bot:
    def __init__(self, symbol: str) -> None:
        """
        Initializes the bot with some specific configurations. 
        :param symbol: The stock symbol that the bot will trade.
        """
        if not m.paper_symbol_exists(symbol):
            raise ValueError(f"The symbol {symbol} does not exist, please use a valid symbol.")
        
        self.symbol = symbol
        self.cash, self.stocks = u.return_account_info()    

        # Once we include more symbols, we will not do it this way
        self.qty = self.stocks.get(self.symbol, 0)

    def start(self) -> None:
        """
        Starts the bot to monitor the market and make buy/sell decisions based on the defined strategy.
        """
        while True:
            not_done = True
            if self.is_market_hours():
                while not_done:
                    not_done = self.make_decision()
                    time.sleep(60)
            else:
                time.sleep(60)

    def stop(self) -> None:
        pass 

    def buy(self) -> None:
        """
        Places order to buy a single stock 
        """
        print("Buy")
        self.place_order(1, "buy")
    
    def sell(self) -> None:
        """
        Places order to sell a single stock
        """
        print("Sell")
        self.place_order(1, "sell")

    def place_order(self, qty: int, side: str) -> None:
        """
        NOTE: We will assume that only one queue will be sent at a time, and it will be sent instantly
        TODO: Will need to check if the order went through, if there is an error, then that should be dealt with. 
        """

        # We can't sell what we don't have :(
        if side == "sell" and qty > self.qty:
            return 

        order_id = o.OrderUtility.create_order(self.symbol, qty, side)
        q.QueueUtility.create_queue("bot_queue", overwrite=True)
        q.QueueUtility.add_to_queue("bot_queue", self.symbol, order_id)
        q.QueueUtility.send_queue("bot_queue")

        u.view_account()


    def is_market_hours(self) -> bool:
        """
        Checks if the current time is within market hours (9:30 AM to 4:00 PM, Monday to Friday).
        """
        now = datetime.now()

        # Checks if its a weekday, between 9 AM and 4 PM, and not before 9:30 AM
        return (now.weekday() < 5) and (9 <= now.hour < 16) and not(now.hour == 9 and now.minute < 30)


    def analyze_market(self) -> Tuple[dict[str, float], dict[str, float]]: # TODO Double check the type hinting
        """
        This method analyzes the market data to make buy/sell decisions based on moving average trend following.
        NOTE: I will need to check if the function also contains the data for today as well, as it is supposed to compare the current price.
        """
        past_data = m.past_prices(self.symbol, timeframe='1Day', start_int=21)  # This will return the past 20 days of data in incremennts of 1 day.
        past_data = past_data[self.symbol]
        
        if self.isMarketHours():
            past_data = past_data[:-1]

        current_data = m.current_prices(self.symbol)
        # current_data[self.symbol] Might have been current_data = current_data[self.symbol]

        return past_data, current_data
    
    def make_decision(self) -> bool:
        """
        This method, will either buy, sell, or do nothing with the stock. 
        NOTE: I will need to also add something that decides how much to buy or sell as well. Need to look into this more.

        """
        
        past_data, current_data = self.analyze_market()

        print(past_data)
        print("\n\n")
        print(current_data)

        closing_prices = [day['c'] for day in past_data]

        avg_c = sum(closing_prices) / len(closing_prices)


        """NOTE: I am not sure if its right to use the opening price for the current day. 
        Also, depending on the time, this might actually return data from the previous day, so I have to look into this as well."""
        current_price = current_data[self.symbol]['c']

        if avg_c < current_price: 
            self.buy()
        elif avg_c > current_price:
            self.sell()
        else:
            return False

        return True