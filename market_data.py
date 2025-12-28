import utilities as u
import requests
from requests import Response
import date


def display_past_prices(symbol: str, timeframe: str = '1Min'):
    """
    Displays and returns past prices for a given symbol and timeframe. This will help the bot (and us), detemrine which stocks are going up and down. 
    :params symbol as str: The stock symbol to get past prices for --> Multiple symbols can be passed separated by commasS
    :params timeframe as str: The price of the stock will be split up into sections of the timeframe (default is '1Min', so each price point is 1 minute apart)
    """

    response: Response = requests.get(
        url="https://data.alpaca.markets/v2/stocks/bars",
        params={
            "symbols": symbol,
            "timeframe": timeframe,
            "start": date.today().isoformat()
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

    # print(stock_info)

    return stock_info
