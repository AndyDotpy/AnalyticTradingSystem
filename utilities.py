from typing import Any, BinaryIO, TYPE_CHECKING
from alpaca.trading import Position
from alpaca.trading.client import TradingClient
import pickle
import os
import requests
from requests import Response
import globals as g
import storage_manager


if TYPE_CHECKING:
    from alpaca.broker import TradeAccount


def no_trading_client() -> bool:
    """
    returns True if the trading_client is none else False
    Prints a message is trading_client is none
    If being used outside of utilities.py and assuming import utilities as u please do u.no_trading_client
    since trading_client is in the utilities namespace
    """
    if g.trading_client is None:
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

    account: TradeAccount = g.trading_client.get_account()
    print(f"Current Cash: ${account.cash}")

    for p in g.trading_client.get_all_positions():
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
                "failed": failed_orders
            },
            file=file
        )
    print("Saved queues and orders!")


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




