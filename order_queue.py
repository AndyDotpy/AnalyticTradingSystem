from order import OrderRecord
from utilities import yes_or_no, try_int
import order as o
import utilities as u
import threading
from collections import deque


class QueueUtility:
    """
    The static class that holds all helper functions related to queues
    """
    @staticmethod
    def create_queue() -> None:
        """
        TODO: Needs default parameters that cause it to skip the user requests for automation
        Currently waits for user input to make a new queue
        :return:
        """
        name = input("Enter name of queue: ")
        if name in u.all_queues:
            confirm = input("A queue with this name already exists, do you want to overwrite? \"y\" or \"n\"").lower()
            if confirm == "y":
                print(f"Overwritten {name} with empty deque")
                u.all_queues[name] = deque()
            else:
                print("Queue overwriting cancelled")
        else:
            u.all_queues[name] = deque()

    @staticmethod
    def display_queue_names() -> None:
        """
        Prints all queue names
        :return:
        """
        for key in u.all_queues:
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
        if queue not in u.all_queues:
            print(f"The queue {queue} does not exist")
            return

        symbol = input("Enter stock symbol you want to trade: ")
        if symbol not in u.all_orders:
            print(f"You have no orders for {symbol} stock")
            return

        order_id: int | None = try_int(input("Enter order id: "))
        if order_id is None:
            print(
                "The unique id is a int, the conversion from string to int "
                "failed implying what was entered was not an int"
            )
            return
        elif order_id not in u.all_orders[symbol]:
            print(f"There are no order ids of {order_id} associated with this symbol")
            return

        u.all_queues[queue].append(u.all_orders[symbol][order_id])
        print("Successfully added to queue!")

    @staticmethod
    def send_queue() -> None:
        """
        TODO: Needs default parameters that cause it to skip the user requests for automation also need it to actually send the queue
        Currently waits for the user to tell what queue to send
        :return:
        """
        if yes_or_no(msg="View queues") == "y":
            QueueUtility.display_queue_names()

        name = input("Enter name of queue: ")
        if name in u.all_queues:
            confirm = input("Are you sure you want to send this queue? \"y\" or \"n\"").lower()
            if confirm != "y":
                return
        else:
            print(f"The queue {name} does not exist")

    @staticmethod
    def queue_sender(queue: deque[OrderRecord]) -> None:
        pass #  I am taking a bit of time reading about threads and figuring this out

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
        if queue_name in u.all_queues:
            print(f"Removed {queue_name} when it had {len(u.all_queues.pop(queue_name))} orders!")
        else:
            print(f"{queue_name} is not a valid queue!")
