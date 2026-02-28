import os
from alpaca.trading.client import TradingClient
import threading
from typing import Any, Callable
import time
import copy


class ThreadSafety:
    """
    For data that will be accessed by multiple threads
    """
    def __init__(self, value: Any = None, deepcopy: bool = True):
        """
        Initializes ThreadSafety object
        :param Any as value: Starting value that will be held
        :param bool as deepcopy: Determines if when setting or getting a value if it will be deep copied or not
        this includes the constructor
        """
        self._lock: threading.Lock = threading.Lock()
        self.deepcopy: bool = deepcopy
        self._value: Any = value if self.deepcopy is False else copy.deepcopy(value)

    def __get_return_value(self) -> Any:
        """
        Private helper for if a return value should be deep copied or not
        """
        return self._value if self.deepcopy is False else copy.deepcopy(self._value)

    def __get_new_value(self, new_val: Any) -> Any:
        """
        Private helper for if the new value being set should be deep copied or not
        """
        return new_val if self.deepcopy is False else copy.deepcopy(new_val)

    def get(self) -> Any:
        """
        Gets the data while its lock is acquired so no other thread can modify it, keeps deepcopy in mind when returning
        :return Any:
        """
        with self._lock:
            return self.__get_return_value()

    def set(self, new_val: Any) -> None:
        """
        Sets the value to the new one passed in keeping in mind the deepcopy setting while the lock is acquired
        :param Any as new_val: The value to be set
        :return:
        """
        with self._lock:
            self._value = self.__get_new_value(new_val)

    def update(self, update_func: Callable[[Any], Any]) -> Any:
        """
        Updates the value to the new one passed in keeping in mind the deepcopy setting while lock is acquired
        also returning the updated value while keeping in mind the deepcopy setting
        :param Callable[[Any], Any] as update_func:
        :return Any:
        """
        with self._lock:
            self._value = self.__get_new_value(update_func(self._value))
            return self.__get_return_value()


class RateLimiter:
    """
    A threadsafe object that is used as a rate limiter by using the wait() method to prevent API rate limiting issues
    """
    def __init__(self, delay: float):
        """
        Sets the delay, sets the _last_time to 0.0 for starting value and gives it a lock for thread safety
        :param float as delay: How much time in seconds that is ensured is waited when wait() is called
        """
        self.delay: float = delay
        self._last_time: float = 0.0
        self._lock: threading.Lock = threading.Lock()

    def wait(self) -> None:
        """
        Waits the set amount of time, if called multiple times in multiple threads it will wait the set amount of time
        for each thread it is called on
        """
        with self._lock:
            time.sleep(max(0.0, self.delay - (time.monotonic() - self._last_time)))
            self._last_time = time.monotonic()


# Message to clear the terminal
cls_msg: str = "cls" if os.name == "nt" else "clear"

# Api key for alpaca along with secret
API_KEY: str = ""
SECRET: str = ""

# Rate Limiter
alpaca_rate_limit: RateLimiter = RateLimiter(0.35)

# Connects to a paper trading endpoint
trading_client: TradingClient | None = None
