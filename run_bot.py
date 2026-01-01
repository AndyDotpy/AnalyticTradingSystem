from bot import Bot
import storage_manager 
import utilities as u

storage_manager.FileManager.load_local_info()

if u.no_trading_client():
    # NOTE: I am wondering if maybe it will be better that we automatically set the API keys here, using a .env file......
    raise ValueError("Trading client is not set. Please set API keys before initializing the bot.")

b = Bot(symbol="AAPL")

b.start()