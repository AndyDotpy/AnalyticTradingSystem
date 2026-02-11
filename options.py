import order as o
import order_queue as q
import storage_manager as sm
import security_manager as s
import utilities as u
import market_data as m
import globals as g
from alpaca.trading.client import TradingClient


class Options:
    """
    Class representing all the functions that will be callable from the main loop in main.py
    User input will be asked here
    """
    @staticmethod
    def create_order() -> None:
        """
        Asks user for input when creating an order
        :return:
        """
        symbol = input("Enter the symbol of the stock: ")

        qty: int | None = None
        while qty is None:
            qty = u.try_int(input("Enter quantity: "))

        side: str | None = None
        while side != "buy" and side != "sell":
            side = input("Enter \"buy\" or \"sell\": ").lower()

        overwrite = False
        if u.yes_or_no("If the order already exists do you want to overwrite?") == "y":
            overwrite = True

        o.OrderUtility.create_order(
            symbol=symbol,
            qty=qty,
            side=side,
            overwrite=overwrite
        )

    @staticmethod
    def display_orders() -> None:
        """
        Displays all orders
        :return:
        """
        o.OrderUtility.display_orders()

    @staticmethod
    def remove_order() -> None:
        """
        Removes an order based on user input
        :return:
        """
        if len(o.OrderUtility.all_orders) == 0:
            print("There are no orders to be removed...")
            return

        if u.yes_or_no(msg="View orders") == "y":
            o.OrderUtility.display_orders()

        symbol: str = input("Enter symbol: ")
        unique_id: int | None = None

        while unique_id is None:
            unique_id = u.try_int(input("Enter unique id: "))

        if symbol not in o.OrderUtility.all_orders:
            print("This symbol is not in all_orders")
            return

        if unique_id not in o.OrderUtility.all_orders[symbol]:
            print(f"Unique ID does not exist for the symbol {symbol}")
            return

        o.OrderUtility.remove_order(
            symbol=symbol,
            unique_id=unique_id
        )

    @staticmethod
    def create_queue() -> None:
        """
        Creates a queue or OrderRecord instances based on user input, starts out as empty
        :return:
        """
        q.QueueUtility.create_queue(
            name_of_queue=input("Enter name of queue: "),
            overwrite=(u.yes_or_no("Overwrite queue if already exists?") == "y")
        )

    @staticmethod
    def display_queue_names() -> None:
        """
        Displays the queue names of all queues created
        :return:
        """
        q.QueueUtility.display_queue_names()

    @staticmethod
    def add_to_queue() -> None:
        """
        Asks user input when adding an OrderRecord to queue
        :return:
        """
        if u.yes_or_no(msg="View queue") == "y":
            q.QueueUtility.display_queue_names()

        if u.yes_or_no(msg="View order") == "y":
            o.OrderUtility.display_orders()

        queue: str = input("Enter queue: ")
        if queue not in q.QueueUtility.all_queues:
            print(f"The queue {queue} does not exist")
            return

        symbol = input("Enter stock symbol you want to trade: ")
        if symbol not in o.OrderUtility.all_orders:
            print(f"You have no orders for {symbol} stock")
            return

        order_id: int | None = u.try_int(input("Enter order id: "))
        if order_id is None:
            print(
                "The unique id is a int, the conversion from string to int "
                "failed implying what was entered was not an int"
            )
            return
        elif order_id not in o.OrderUtility.all_orders[symbol]:
            print(f"There are no order ids of {order_id} associated with this symbol")
            return

        q.QueueUtility.add_to_queue(
            queue_name=queue,
            symbol=symbol,
            order_id=order_id
        )

    @staticmethod
    def send_queue() -> None:
        """
        Sends a queue by using another thread so the user can do other thinks while waiting
        :return:
        """
        if u.yes_or_no(msg="View queues") == "y":
            q.QueueUtility.display_queue_names()

        queue = input("Enter name of queue you want to send: ")

        confirm = input("Are you sure you want to send this queue? \"y\" or \"n\"").lower()
        if confirm != "y":
            return

        q.QueueUtility.send_queue(queue_name=queue)

    @staticmethod
    def remove_queue() -> None:
        """
        Removes a queue based off the name of the queue that the user enters
        :return:
        """
        if u.yes_or_no(msg="Display queue names?") == "y":
            q.QueueUtility.display_queue_names()

        q.QueueUtility.remove_queue(
            queue_name=input("Enter Queue Name: ")
        )

    @staticmethod
    def get_paper_symbol_data() -> None:
        """
        Gets paper trading data check the actual get_paper_trade_data() for more details
        :return:
        """
        m.MarketData.get_paper_symbol_data()

    @staticmethod
    def display_paper_symbols() -> None:
        """
        TODO Needs better documentation check MarketData class for more details
        :return:
        """
        m.MarketData.display_paper_symbols()

    @staticmethod
    def view_account() -> None:
        """
        Views the users alpaca account
        :return:
        """
        u.view_account()

    @staticmethod
    def enter_API_keys() -> None:
        """
        Saves the API keys as specified in FileManager in storage_manager.py
        :return:
        """
        g.API_KEY = input("Enter API Key: ")
        g.SECRET = input("Enter secret key: ")
        g.trading_client = TradingClient(g.API_KEY, g.SECRET, paper=True)
        sm.FileManager.save_API_keys()

    @staticmethod
    def enter_encryption_key() -> None:
        sm.EncryptionManager.set_encryption_info(
            input("Enter encryption key: ")
        )

    @staticmethod
    def remove_encryption_key() -> None:
        """
        Removes encryption information so nothing else can be encrypted or decrypted
        :return:
        """
        sm.EncryptionManager.remove_encryption_info()

    @staticmethod
    def display_encryption_key() -> None:
        """
        Shows the user the encryption key
        :return:
        """
        sm.EncryptionManager.display_encryption_key()

    @staticmethod
    def save_everything() -> None:
        """
        Attempts to save all the data lets the user know if it does not work
        :return:
        """
        if sm.FileManager.save_all() is False:
            print("Finished attempting to save everything but some things failed")
        else:
            print("Everything saved successfully!")

    @staticmethod
    def is_queue_sending() -> None:
        """
        Displays to the user if there is an active queue
        :return:
        """
        if q.QueueUtility.sending_queue:
            print("Queue is currently being sent")
        else:
            print("No queue is being sent")

    @staticmethod
    def reload_local_info() -> None:
        """
        Attempts to load all information from the computer to the program overwriting everything in the program
        :return:
        """
        sm.FileManager.load_local_info()

    @staticmethod
    def set_password() -> None:
        """
        Sets the given password rejects if invalid
        :return:
        """
        s.SecurityManager.set_password(input("Enter password you want to set: "))

    @staticmethod
    def generate_password() -> None:
        """
        Displays a randomly generated password to the console not guaranteed to be secure
        :return:
        """
        given_length: int | None = None
        if u.yes_or_no("Would you like to specify the length?") == "y":
            given_length = u.try_int(input("Enter length: "))
        print(s.SecurityManager.generate_password(given_length))

    @staticmethod
    def remove_password() -> None:
        """
        Removed password, but before it does so it asks for a confirmation from the user
        :return:
        """
        if u.yes_or_no("Are you sure you want to remove the password?") == "y":
            s.SecurityManager.remove_password()

    @staticmethod
    def view_security_info() -> None:
        print(
            f"Security Status: {s.SecurityManager.status}\n"
            f"Previous Status: {s.SecurityManager.previous_status}\n"
            f"Password: {s.SecurityManager.password}"
        )

    @staticmethod
    def exit_prog() -> None:
        """
        Attempts to save all information and encrypt it if encryption key is given
        If the save_all() fails in any way the user will be notified and asked if they still want to exit
        :return:
        """
        if sm.FileManager.save_all() is False:
            if u.yes_or_no("You are attempting to exit the program when not everything saved successfully, do you want to continue?") == "y":
                exit(1)
            else:
                return
        exit(0)
