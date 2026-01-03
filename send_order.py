"""
This is a file that only exits for quick testing.
"""

import order as o
import order_queue as q
import storage_manager 
import utilities as u


storage_manager.FileManager.load_local_info()

def create_and_send_order(symbol: str, qty: int, side: str):
    order_id = o.OrderUtility.create_order(symbol, qty, side)
    q.QueueUtility.create_queue("instant_queue", overwrite=True)
    q.QueueUtility.add_to_queue("instant_queue", symbol, order_id)
    q.QueueUtility.send_queue("instant_queue")

create_and_send_order("AAPL", 11, "buy")