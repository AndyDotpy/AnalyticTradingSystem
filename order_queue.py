import time
from datetime import datetime
import pytz
from order import OrderRecord
from utilities import yes_or_no, try_int
import order as o
import threading
from collections import deque
import os
import globals as g


class QueueUtility:
    """
    The static class that holds all helper functions related to queues
    """
    all_queues: dict[str, deque["OrderRecord"]] = {}
    sending_queue: bool = False  # True if a queue is currently being sent, False if not
    last_order_time: int = int(time.time() * 1000)  # Time in milliseconds when the last order was sent

    @staticmethod
    def create_queue() -> None:
        """
        TODO: Needs default parameters that cause it to skip the user requests for automation
        Currently waits for user input to make a new queue
        :return:
        """
        name = input("Enter name of queue: ")
        if name in QueueUtility.all_queues:
            confirm = input("A queue with this name already exists, do you want to overwrite? \"y\" or \"n\"").lower()
            if confirm == "y":
                print(f"Overwritten {name} with empty deque")
                QueueUtility.all_queues[name] = deque()
            else:
                print("Queue overwriting cancelled")
        else:
            QueueUtility.all_queues[name] = deque()

    @staticmethod
    def display_queue_names() -> None:
        """
        Prints all queue names
        :return:
        """
        for key in QueueUtility.all_queues:
            print(key)

    @staticmethod
    def add_to_queue() -> None:
        """
        TODO: Needs default parameters that cause it to skip the user requests for automation
        Adds to queue based off of user input
        :return:
        """
        if yes_or_no(msg="View queue") == "y":
            QueueUtility.display_queue_names()

        if yes_or_no(msg="View order") == "y":
            o.OrderUtility.display_orders()

        queue: str = input("Enter queue: ")
        if queue not in QueueUtility.all_queues:
            print(f"The queue {queue} does not exist")
            return

        symbol = input("Enter stock symbol you want to trade: ")
        if symbol not in o.OrderUtility.all_orders:
            print(f"You have no orders for {symbol} stock")
            return

        order_id: int | None = try_int(input("Enter order id: "))
        if order_id is None:
            print(
                "The unique id is a int, the conversion from string to int "
                "failed implying what was entered was not an int"
            )
            return
        elif order_id not in o.OrderUtility.all_orders[symbol]:
            print(f"There are no order ids of {order_id} associated with this symbol")
            return

        QueueUtility.all_queues[queue].append(o.OrderUtility.all_orders[symbol][order_id])
        print("Successfully added to queue!")

    @staticmethod
    def send_queue() -> None:
        """
        TODO: Needs default parameters that cause it to skip the user requests for automation
        Asks the user for the queue name, asks for confirmation then starts the queue sending thread
        :return:
        """
        if yes_or_no(msg="View queues") == "y":
            QueueUtility.display_queue_names()

        name = input("Enter name of queue: ")
        if name in QueueUtility.all_queues:
            confirm = input("Are you sure you want to send this queue? \"y\" or \"n\"").lower()
            if confirm != "y":
                return
            threading.Thread(target=QueueUtility.queue_sender, args=(name, QueueUtility.all_queues.pop(name))).start()
        else:
            print(f"The queue {name} does not exist")

    @staticmethod
    def queue_sender(queue_name: str, queue: deque[OrderRecord]) -> None:
        """
        Parameters are the name of the queue as queue_name and the actual queue as a deque[OrderRecord]
        Returns nothing
        This method is started in a thread called in send_queue()
        Marks the sending_queue in utilities.py as True when it starts then marks it as False when finished
        Logs everything in a log file that is named with the queue name and timestamp under the queue_logs directory
        Logs timestamps in milliseconds since its start, the information received after order is sent
        Tells the user if the order passed or failed
        If order fails it gets added to the failed_orders in utilities.py
        Has a 350 millisecond delay 0.35 seconds
        The start and end of the log file are clearly marked with Start of log file and
        |End| of log file respectively
        """
        #  Rate limit information: https://alpaca.markets/support/usage-limit-api-calls
        #  200 requests per minute -> 1.01 request per .30 seconds, delay will be .35 seconds to be safe
        QueueUtility.sending_queue = True
        start_time: int = int(time.time() * 1000)  # Start time in milliseconds

        try:
            os.mkdir(path="queue_logs")
        except FileExistsError:
            pass
        except FileNotFoundError:
            print(f"Problem creating the log directory the queue {queue_name} queue_sender returning.")
            return

        with open(f"queue_logs/{queue_name} at {datetime.now(pytz.timezone('EST')).date()}", "w") as log_file:
            print("_____ _____ _____ _____ Start of log file _____ _____ _____ _____\n", file=log_file)
            seperator: str = ("\n##### ##### ##### ##### ##### ##### ##### #####\n"
                              "\n##### ##### ##### ##### ##### ##### ##### #####")

            while len(queue) > 0:
                current_order: OrderRecord = queue.popleft()
                try:
                    print(
                        str(g.trading_client.submit_order(
                            current_order.market_order
                        )) + f"\nTimestamp: {int(time.time() * 1000) - start_time} milliseconds from start time" +
                        seperator,
                        file=log_file
                    )
                except Exception as e:  # I could not find the documentation for what exceptions this throws
                    print(f"Failed to send {current_order.id} due to {e}{seperator}", file=log_file)

                    current_order.failed = True
                    current_order.exception = e

                    if queue_name not in o.OrderUtility.failed_orders:
                        o.OrderUtility.failed_orders[queue_name] = deque()
                    else:
                        o.OrderUtility.failed_orders[queue_name].append(current_order)

                while int(time.time() * 1000) - QueueUtility.last_order_time < 350:  # 350 millisecond delay
                    time.sleep(0)
                QueueUtility.last_order_time = int(time.time() * 1000)
            print("\n_____ _____ _____ _____ |End| of log file _____ _____ _____ _____", file=log_file)
        QueueUtility.sending_queue = False

    @staticmethod
    def remove_queue() -> None:
        """
        Removes a queue of orders based on the name and prints the queue name removed and number of orders it has
        if no queue name exists will print so
        :return:
        """
        if yes_or_no(msg="Display queue names?") == "y":
            QueueUtility.display_queue_names()

        queue_name: str = input("Enter Queue Name: ")
        if queue_name in QueueUtility.all_queues:
            print(f"Removed {queue_name} when it had {len(QueueUtility.all_queues.pop(queue_name))} orders!")
        else:
            print(f"{queue_name} is not a valid queue!")
