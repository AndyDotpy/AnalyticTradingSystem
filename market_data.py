import globals as g
import requests
from requests import Response
import datetime
from typing import Any
import utilities as u


class MarketData:
    REQUEST_HEADERS: dict[str, str] = {
        "APCA-API-KEY-ID": g.API_KEY,
        "APCA-API-SECRET-KEY": g.SECRET,
        "accept": "application/json"
    }

    # Storing paper data
    paper_data: list[dict[str, Any]] | None = None  # List of all assets, dict for each asset with each info having a string name and could be any type of data
    paper_symbols: dict[str, bool] | None = None  # Dict of all symbols, the key str is symbol name and bool is if its tradable


    @staticmethod
    def request_past_prices(symbol: str, timeframe: str = '1Min', days_ago: int = 1, data_points: int = 10000) -> dict[str, list[dict[float | int | str]]] | None:
        """
        Returns a dictionary that contains keys as stock symbols the user requested with a list of data, this may take
        multiple requests to complete.
        :param str as symbol: The stock symbol to get past prices for --> Multiple symbols can be passed separated by commas
        :param str as timeframe: The price of the stock will be split up into sections of the timeframe (default is '1Min', so each price point is 1 minute apart)
        :param int as days_ago: The number of days in the past to start gathering data from (default is 1, meaning yesterday)
        :param int as data_points: The maximum number of data points you ask for
        :return dict[str, list[dict[float | int | str]]]:
        Documentation: https://docs.alpaca.markets/reference/stockbars
        """

        start_date: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        """
        For response_json the outer dict has two keys "bars" and "next_page_token", in the "bars" dict it contains
        the stock symbols for the keys which the user has requested with the value being a list of data which starts at
        start date the user sent in the request then each data point after that in the list is timeframe time after the
        previous data point until current date for example if I send in 2026-01-05 and timeframe = 1Min I would get the
        information of the requested symbols starting at 2026-01-05 when the market opened then the prices one minute 
        after that and another minute after that until the last data point is gotten. The "next_page_token" is for more 
        data you want more than what was received the appearance of this token does not mean you did or did not get all 
        the  datapoints you requested:
        params={
            # Include symbol and timeframe as well since they are required
            "page_token": use this if next page token is not None
        }
        """
        response_json: dict[str, dict[str, None | str | list[dict[str, float | int | str]]]] = requests.get(
            url="https://data.alpaca.markets/v2/stocks/bars",
            params={
                "symbols": symbol,
                "timeframe": timeframe,
                "start": str(start_date.date()),  # YYYY-MM-DD
                "limit": data_points,
            },
            headers=MarketData.REQUEST_HEADERS
        ).json()

        """
        stock_info is a dict of all symbols asked for in the symbol parameter as the key then as value is a list of that
        symbol info separated by the time specified in the timeframe parameter, the data looks like
            "c": float, close price
            "h": float, high price
            "l": float, low price
            "n": int, number of trades
            "o": float, open price
            "t": str, RFC-3339 formatted timestamp or YYYY-MM-DD
            "v": int, volume
            "vw": float volume-weighted average price

        Documentation: https://docs.alpaca.markets/docs/real-time-stock-pricing-data
        """
        stock_info: dict[str, list[dict[str, float | int | str]]] | None = None
        next_page: str | None = None

        if "message" in response_json:
            pass  # Log the error
        elif "bars" in response_json and "next_page_token" in response_json:
            stock_info = response_json["bars"]
            next_page = response_json["next_page_token"]
        else:
            pass  # Log unknown error

        data_points_collected: int = 0
        if stock_info is not None:
            data_points_collected = sum(len(symbol_list) for symbol_list in stock_info.values())
            while data_points_collected < data_points and next_page is not None:
                response_json = requests.get(
                    url="https://data.alpaca.markets/v2/stocks/bars",
                    params={
                        "symbols": symbol,
                        "timeframe": timeframe,
                        "page_token": next_page
                    },
                    headers=MarketData.REQUEST_HEADERS
                ).json()

                if "message" in response_json:
                    pass  # Log the error
                elif "bars" in response_json and "next_page_token" in response_json:
                    for key, symbol_list in response_json["bars"].items():
                        if key in stock_info:
                            stock_info[key].extend(symbol_list)
                        else:
                            stock_info[key] = symbol_list
                        data_points_collected += len(symbol_list)
                else:
                    pass  # Log unknown error
                next_page = response_json.get("next_page_token")

        if data_points_collected < data_points:
            pass  # log that not all data points wanted were received


        return stock_info

    @staticmethod
    def request_current_prices(symbol: str) -> dict[str, dict[str, float | int | str]] | None:
        """
        Gets the last minute prices of the stocks requested in the symbol parameter, note multiple symbols can be passed
        through a comma separated list, the data looks the same as noted in request_past_prices
        :param str as symbol: one or multiple symbols by comma separated list
        :return dict[str, dict[str, float | int | str]] | None:
        """
        response_json: dict[str, dict[str, dict[str, float | int | str]]] = requests.get(
            url="https://data.alpaca.markets/v2/stocks/bars/latest",
            params={
                "symbols": symbol,
            },
            headers=MarketData.REQUEST_HEADERS
        ).json()

        if "message" in response_json:
            pass  # Log error
        elif "bars" in response_json:
            return response_json["bars"]
        else:
            pass  # Log unknown error

        return None

    @staticmethod
    def paper_symbol_exists(symbol: str) -> bool:
        """
        Use to check if symbol exists in paper trading
        :params symbol as str:
        :return bool:
        """
        if MarketData.paper_symbols is None:
            return False

        return symbol in MarketData.paper_symbols

    @staticmethod
    def display_paper_data() -> None:
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

    @staticmethod
    def display_paper_symbols() -> None:
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

    @staticmethod
    def get_paper_symbol_data() -> None:
        """
        Uses the API_KEY and SECRET key to send an HTTP request to the link below to get a json formatted list of all paper
        assets then stores them in paper_data and iterates over paper_data to put all the symbols in a dict called
        paper_symbols whose value is a bool where true is tradable and false isn't.
        This will also be saved as paper_info.pkl to your computer
        HTTPS Request Link: https://paper-api.alpaca.markets/v2/assets
        Documentation: https://docs.alpaca.markets/reference/get-v2-assets-1
        """

        if u.no_trading_client():
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


