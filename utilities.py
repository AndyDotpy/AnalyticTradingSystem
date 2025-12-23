from typing import Any, BinaryIO, TYPE_CHECKING, Final
from alpaca.trading import Position
from alpaca.trading.client import TradingClient
import pickle
import os
from collections import deque
from enum import Enum
import requests
from requests import Response


if TYPE_CHECKING:
    from order import OrderRecord
    from alpaca.broker import TradeAccount

# Message to clear the terminal
cls_msg: str = "cls" if os.name == "nt" else "clear"


# File names
class FilePaths(Enum):
    """
    Constants for file names so they are not accidentally mistyped
    """
    QUEUES_ORDERS: Final = ".save_info/orders_queues.pkl"
    API_KEYS: Final = ".save_info/api_keys.pkl"
    PAPER_INFO: Final = ".save_info/paper_info.pkl"


# Api key for alpaca along with secret
API_KEY: str = ""
SECRET: str = ""

# Connects to a paper trading endpoint
trading_client: TradingClient | None = None

# Storing orders and queues
# https://docs.python.org/3.10/library/typing.html#typing.TYPE_CHECKING
all_orders: dict[str, dict[int, "OrderRecord"]] = {}
all_queues: dict[str, deque["OrderRecord"]] = {}

# Storing paper data
paper_data: list[dict[str, Any]] | None = None #  List of all assets, dict for each asset with each info having a string name and could be any type of data
paper_symbols: dict[str, bool] | None = None #  Dict of all symbols, the key str is symbol name and bool is if its tradable


def no_trading_client() -> bool:
    """
    returns True if the trading_client is none else False
    Prints a message is trading_client is none
    If being used outside of utilities.py and assuming import utilities as u please do u.no_trading_client
    since trading_client is in the utilities namespace
    """
    if trading_client is None:
        print("Trading client has not been set please set it with \"[i] Enter API keys\"")
        return True
    return False


def save_directory_check() -> bool:
    """
    Attempts to make a directory called .save_info where all .pkl files are saved returns True if it exists or has been
    created False otherwise
    Make sure to use this is saving something to the device
    """
    try:
        os.mkdir(path=".save_info")
        return True
    except FileExistsError:
        return True
    except FileNotFoundError:
        print("Parent directory or path does not exist for \".save_info\" no save directory created")
        return False


def try_int(value: Any) -> int | None:
    """
    Checks if the given value is an int if it is it will return said int else it will return None
    :param value:
    :return:
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def yes_or_no(msg: str = "View") -> str:
    """
    Keep in mind this asks for a "y" or "n" response
    :param msg:
    :return:
    """
    return input(f"{msg} \"y\" or \"n\": ").lower()


def view_account() -> None:
    """
    Displays our account status
    :return:
    """
    if no_trading_client():
        return

    account: TradeAccount = trading_client.get_account()
    print(f"Current Cash: ${account.cash}")

    for p in trading_client.get_all_positions():
        p: Position
        print(f"{p.symbol}: {p.qty} shares")


def save_orders_and_queues() -> None:
    """
    Saves all local orders and queues as pickle file called orders_queues.pkl
    :return:
    """
    if save_directory_check() is False:
        return

    with open(FilePaths.QUEUES_ORDERS.value, "wb") as file:
        file: BinaryIO
        pickle.dump(
            obj={
                "orders": all_orders,
                "queues": all_queues,
            },
            file=file
        )
    print("Saved queues and orders!")


def load_local_info() -> None:
    """
    Loads all local orders, symbols and queues
    :return:
    """
    global all_queues, all_orders, API_KEY, SECRET, trading_client, paper_data, paper_symbols

    try:
        with open(FilePaths.QUEUES_ORDERS.value, "rb") as file:
            file: BinaryIO
            info: dict = pickle.load(file)
            all_queues = info["queues"]
            all_orders = info["orders"]
        print("Loaded previous queues and orders")
    except OSError:
        print("No previous information on orders or queues found to be loaded")

    try:
        with open(FilePaths.API_KEYS.value, "rb") as file:
            file: BinaryIO
            info: dict = pickle.load(file)
            API_KEY = info["API_KEY"]
            SECRET = info["SECRET"]
            trading_client = TradingClient(API_KEY, SECRET, paper=True)
        print("Loaded API Keys")
    except OSError:
        print("No previous API Keys found")

    try:
        with open(FilePaths.PAPER_INFO.value, "rb") as file:
            file: BinaryIO
            info: dict = pickle.load(file)
            paper_data = info["paper_data"]
            paper_symbols = info["paper_symbols"]
        print("Loaded paper data and symbols")
    except OSError:
        print("No previous paper data found")



def exit_prog() -> None:
    """
    Exits program and saves local changes
    :return:
    """
    save_orders_and_queues()
    exit(0)


def enter_API_keys() -> None:
    """
    Saves the API keys as a serialized .pkl
    :return:
    """
    global trading_client, API_KEY, SECRET

    if save_directory_check() is False:
        return

    with open(FilePaths.API_KEYS.value, "wb") as file:
        API_KEY = input("Enter API Key Here: ")
        SECRET = input("Enter Secret Key Here: ")
        pickle.dump(
            obj={
                "API_KEY": API_KEY,
                "SECRET": SECRET
            },
            file=file
        )
        trading_client = TradingClient(API_KEY, SECRET, paper=True)
    print(f"API key and secret key saved to \"{FilePaths.API_KEYS.value}\"")


def get_paper_trade_data() -> None:
    """
    Uses the API_KEY and SECRET key to send an HTTP request to the link below to get a json formatted list of all paper
    assets then stores them in paper_data and iterates over paper_data to put all the symbols in a dict called
    paper_symbols whose value is a bool where true is tradable and false isn't.
    This will also be saved as paper_info.pkl to your computer
    HTTPS Request Link: https://paper-api.alpaca.markets/v2/assets
    Documentation: https://docs.alpaca.markets/reference/get-v2-assets-1
    """
    global paper_data, paper_symbols

    if no_trading_client() or save_directory_check() is False:
        return

    response: Response = requests.get(
        url="https://paper-api.alpaca.markets/v2/assets",
        headers={
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": SECRET,
            "accept": "application/json"
        }
    )

    if response.status_code != 200:
        print(f"Status code is not 400 is is {response.status_code} no paper data has been gathered.")
        return

    paper_data = response.json()
    paper_symbols = {}
    for asset in paper_data:
        paper_symbols[asset["symbol"]] = asset["tradable"]

    with open(FilePaths.PAPER_INFO.value, "wb") as file:
        pickle.dump(
            obj={
                "paper_data": paper_data,
                "paper_symbols": paper_symbols
            },
            file=file
        )

    print("Got paper data, updated paper_data and paper_symbols!")


def paper_symbol_exists(symbol: str) -> bool:
    """
    Use to check if symbol exists in paper trading
    :params symbol as str:
    :return bool:
    """
    return symbol in paper_symbols

