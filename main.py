import os
import order as o
import order_queue as q
import utilities as u
import market_data 

m = market_data.MarketData(use_bot=False)

optionsMap = {
    "c": lambda: o.OrderUtility.create_order(),
    "r": lambda: o.OrderUtility.remove_order(),
    "q": lambda: q.QueueUtility.create_queue(),
    "d": lambda: q.QueueUtility.display_queue_names(),
    "o": lambda: o.OrderUtility.display_orders(),
    "v": lambda: u.view_account(),
    "a": lambda: q.QueueUtility.add_to_queue(),
    "s": lambda: q.QueueUtility.send_queue(),
    "i": lambda: u.enter_API_keys(),
    "p": lambda: u.get_paper_trade_data(),
    "m": lambda: q.QueueUtility.remove_queue(),
    "e": lambda: u.exit_prog(),
    "n": lambda: m.past_prices(),
    "m": lambda: u.display_paper_symbols(),
}


if __name__ == '__main__':
    u.load_local_info()

    while True:
        inp = input(
            "[c] Create order\n"
            "[r] Remove order\n"
            "[q] Create queue\n"
            "[d] Display queues\n"
            "[o] Display orders\n"
            "[v] View account\n"
            "[a] Add to a queue\n"
            "[s] Send queue\n"
            "[i] Enter API keys\n"
            "[p] Get paper data\n"
            "[m] Remove queue\n"
            "[e] Exit program\n"
            "[n] Display past prices\n"
            "[m] Display paper symbols\n"
        ).lower()

        if inp in optionsMap:
            optionsMap[inp]()

        input("Enter to continue: ")
        os.system(u.cls_msg)
