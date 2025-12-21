from collections import deque
from utilities import yes_or_no
import order as o
import utilities as u


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

        order_name = input("Enter order name: ")
        if order_name not in u.all_orders[symbol]:
            print(f"There are no order names of {order_name} associated with this symbol")
            return

        u.all_queues[queue].append(u.all_orders[symbol][order_name])
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
    def remove_queue() -> None:
        """
        TODO: Needs to be implemented
        :return:
        """
        pass
