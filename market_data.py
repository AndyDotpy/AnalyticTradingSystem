import utilities as u
import requests
from requests import Response
import datetime


def display_past_prices(symbol: str, timeframe: str = '1Min', start_int: int = 1) -> dict:
    """
    Displays and returns past prices for a given symbol and timeframe. This will help the bot (and us), detemrine which stocks are going up and down. 
    :params symbol as str: The stock symbol to get past prices for --> Multiple symbols can be passed separated by commasS
    :params timeframe as str: The price of the stock will be split up into sections of the timeframe (default is '1Min', so each price point is 1 minute apart)
    :params start_int as int: The number of days in the past to start gathering data from (default is 1, meaning yesterday)
    """

    symbol = input("Enter stock symbol(s) (separated by commas for multiple): ") if symbol == '' else symbol
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=start_int)

    response: Response = requests.get(
        url="https://data.alpaca.markets/v2/stocks/bars",
        params={
            "symbols": symbol,
            "timeframe": timeframe,
            "start": str(start_date.date()),
        },
        headers={
            "APCA-API-KEY-ID": u.API_KEY,
            "APCA-API-SECRET-KEY": u.SECRET,
            "accept": "application/json"
        }
    )

    if response.status_code != 200:
        print(f"Status code is not 200 is is {response.status_code} no stock data has been gathered.")
        return

    stock_info = response.json()
    stock_info = stock_info['bars']

    with open("past_prices_output.txt", "w") as file:
        for symbol, data in stock_info.items():
            print(f"Stock symbol: {symbol}", file=file)
            print(data, file=file)
            print("\n", file=file)

    return stock_info

def display_current_prices(symbol: str) -> dict:
    response: Response = requests.get(
        url="https://data.alpaca.markets/v2/stocks/bars",
        params={
            "symbols": symbol,
        },
        headers={
            "APCA-API-KEY-ID": u.API_KEY,
            "APCA-API-SECRET-KEY": u.SECRET,
            "accept": "application/json"
        }
    )

    if response.status_code != 200:
        print(f"Status code is not 200 is is {response.status_code} no stock data has been gathered.")
        return

    info = response.json()
    info = info['bars']

    with open("current_prices_output.txt", "w") as file:
        for symbol, data in info.items():
            print(f"Stock symbol: {symbol}", file=file)
            print(data, file=file)
            print("\n", file=file)
        
    return info


class MarketData:
    def __init__(self, use_bot) -> None:
        self.use_bot = use_bot

    def past_prices(self, symbol: str = '', timeframe: str = '1Min') -> dict:
        """
        Obtains the past prices of a specified stock for an increment of time.
        NOTE: Eventully the inputs will get replaced with decisions made by the bot, for now keeping it this way so its a lot simpler when we move over to the bot controls. 
        
        """

        if not self.use_bot:
            symbol = input("Enter stock symbol(s) (separated by commas for multiple): ")
            timeframe = input("Enter timeframe (default is '1Min'): ") or '1Min'

        return display_past_prices(symbol, timeframe)

    def current_prices(self, symbol):
        """
        Obtains the current price of a specified stock."
        params symbol as str: The stock symbol to get the current price for
        """

        if not self.use_bot:
            symbol = input("Enter stock symbol: ")
        
        return display_current_prices(symbol)