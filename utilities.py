from typing import Any, BinaryIO, TYPE_CHECKING, Final
from alpaca.trading import Position
from alpaca.trading.client import TradingClient
import pickle
import os
from collections import deque
from enum import Enum

if TYPE_CHECKING:
    from order import OrderRecord
    from alpaca.broker import TradeAccount

# Message to clear the terminal
cls_msg: str = "cls" if os.name == "nt" else "clear"


# File names
class FileNames(Enum):
    """
    Constants for file names so they are not accidentally mistyped
    """
    QUEUES_ORDERS: Final = "orders_queues.pkl"
    API_KEYS: Final = "api_keys.pkl"


# Api key for alpaca along with secret
API_KEY: str = ""
SECRET: str = ""

# Connects to a paper trading endpoint
trading_client: TradingClient | None = None

# Storing orders and queues
# https://docs.python.org/3.10/library/typing.html#typing.TYPE_CHECKING
all_orders: dict[str, dict[int, "OrderRecord"]] = {}
all_queues: dict[str, deque["OrderRecord"]] = {}
all_symbols: set[str] = set() # Need to keep track of all symbols currently trading instead of iterating over all_orders every time


def is_no_trading_client() -> bool:
    if trading_client is None:
        print("Trading client has not been set please set it with \"[i] Enter API keys\"")
        return True
    return False


def try_int(value: Any) -> int | None:
    """
    Checks if the given value is an int if it is it will return said int else it will return None
    :param value:
    :return:
    """
    try:
        return int(value)
    except Exception:
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
    if is_no_trading_client():
        return

    account: TradeAccount = trading_client.get_account()
    print(f"Current Cash: ${account.cash}")

    for p in trading_client.get_all_positions():
        p: Position
        print(f"{p.symbol}: {p.qty} shares")


def save_local_info() -> None:
    """
    Saves all local orders and queues as pickle file called orders_queues.pkl
    :return:
    """
    with open(FileNames.QUEUES_ORDERS.value, "wb") as file:
        file: BinaryIO
        pickle.dump(
            obj={
                "orders": all_orders,
                "queues": all_queues,
                "symbols": all_symbols
            },
            file=file
        )
    print("Saved queues and orders!")


def load_local_info() -> None:
    """
    Loads all local orders, symbols and queues
    :return:
    """
    global all_queues, all_orders, all_symbols, API_KEY, SECRET, trading_client

    try:
        with open(FileNames.QUEUES_ORDERS.value, "rb") as file:
            file: BinaryIO
            info: dict = pickle.load(file)
            all_queues = info["queues"]
            all_orders = info["orders"]
            all_symbols = info["symbols"]
        print("Loaded previous queues and orders")
    except OSError:
        print("No previous information on orders or queues found to be loaded")

    try:
        with open(FileNames.API_KEYS.value, "rb") as file:
            file: BinaryIO
            info: dict = pickle.load(file)
            API_KEY = info["API_KEY"]
            SECRET = info["SECRET"]
            trading_client = TradingClient(API_KEY, SECRET, paper=True)
        print("Loaded API Keys")
    except OSError:
        print("No previous API Keys found")



def exit_prog() -> None:
    """
    Exits program and saves local changes

    :return:
    """
    save_local_info()
    exit(0)


def enter_API_keys() -> None:
    global trading_client, API_KEY, SECRET
    """
    Saves the API keys as a serialized .pkl
    :return:
    """

    with open(FileNames.API_KEYS.value, "wb") as file:
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
    print(f"API key and secret key saved to \"{FileNames.API_KEYS.value}\"")
