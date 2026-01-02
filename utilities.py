from typing import Any, Optional, Tuple, List, Dict
from alpaca.trading import Position
import globals as g
import storage_manager
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

def return_account_info() -> Optional[Tuple[float, Dict[str, int]]]:
    """
    Returns the total cash and stocks in account. Used for the bot. 
    :return: A tuple that contains account information: total cash, each stock, and its quantity in a dictionary
    """
    if no_trading_client():
        return

    account: TradeAccount = g.trading_client.get_account()
    print(f"Current Cash: ${account.cash}")

    symbol_qty : Dict[str, int] = {}
    for p in g.trading_client.get_all_positions():
        symbol_qty[p.symbol] = int(p.qty)
    
    return account.cash, symbol_qty



def exit_prog() -> None:
    """
    Exits program and saves local changes
    :return:
    """
    storage_manager.FileManager.save_all()
    exit(0)

