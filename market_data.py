import globals as g
import requests
from requests import Response
import datetime
from typing import Any
import utilities as u


def display_past_prices(symbol: str = '', timeframe: str = '1Min', start_int: int = 1) -> dict:
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
            "APCA-API-KEY-ID": g.API_KEY,
            "APCA-API-SECRET-KEY": g.SECRET,
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
            "APCA-API-KEY-ID": g.API_KEY,
            "APCA-API-SECRET-KEY": g.SECRET,
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
    # Storing paper data
    paper_data: list[dict[str, Any]] | None = None  # List of all assets, dict for each asset with each info having a string name and could be any type of data
    paper_symbols: dict[str, bool] | None = None  # Dict of all symbols, the key str is symbol name and bool is if its tradable

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

    def paper_symbol_exists(self, symbol: str) -> bool:
        """
        Use to check if symbol exists in paper trading
        :params symbol as str:
        :return bool:
        """
        return symbol in MarketData.paper_symbols

    def display_paper_data(self) -> None:
        """
        Displays all paper trading assets
        :return None:
        """
        if MarketData.paper_data is None:
            print("No paper data loaded")
            return

        for asset in MarketData.paper_data:
            # I needed to type hint each asset better so we know what it is, check documentation later
            print(asset)
        return

    def display_paper_symbols(self) -> None:
        """
        Displays all paper trading symbols
        :return None:
        """
        if MarketData.paper_symbols is None:
            print("No paper symbols loaded")
            return

        for symbol, tradable in MarketData.paper_symbols.items():
            print(f"Symbol: {symbol}, Tradable: {tradable}")
        return

    def get_paper_trade_data(self) -> None:
        """
        Uses the API_KEY and SECRET key to send an HTTP request to the link below to get a json formatted list of all paper
        assets then stores them in paper_data and iterates over paper_data to put all the symbols in a dict called
        paper_symbols whose value is a bool where true is tradable and false isn't.
        This will also be saved as paper_info.pkl to your computer
        HTTPS Request Link: https://paper-api.alpaca.markets/v2/assets
        Documentation: https://docs.alpaca.markets/reference/get-v2-assets-1
        """

        if u.no_trading_client() is False:
            return

        response: Response = requests.get(
            url="https://paper-api.alpaca.markets/v2/assets",
            headers={
                "APCA-API-KEY-ID": g.API_KEY,
                "APCA-API-SECRET-KEY": g.SECRET,
                "accept": "application/json"
            }
        )

        if response.status_code != 200:
            print(f"Status code is not 200 is is {response.status_code} no paper data has been gathered.")
            return

        MarketData.paper_data = response.json()
        MarketData.paper_symbols = {}
        for asset in MarketData.paper_data:
            MarketData.paper_symbols[asset["symbol"]] = asset["tradable"]

        print("Got paper data, updated paper_data and paper_symbols!")


