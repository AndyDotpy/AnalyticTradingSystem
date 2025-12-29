import os
from alpaca.trading.client import TradingClient

# Message to clear the terminal
cls_msg: str = "cls" if os.name == "nt" else "clear"


# Api key for alpaca along with secret
API_KEY: str = ""
SECRET: str = ""

# Connects to a paper trading endpoint
trading_client: TradingClient | None = None
