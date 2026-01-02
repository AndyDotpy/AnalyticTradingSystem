import os
import options as o
import utilities as u
import globals as g
import storage_manager
from typing import Callable


class OptionsNode:
    """
    Class representing nodes that will be used in the OptionsTree
    """
    def __init__(
            self,
            options_map: dict[str, Callable[[], None]] | None,
            display: str,
            parent: "OptionsNode",  # Can be None for root
            children: dict[str, "OptionsNode"] | None
    ):
        self.options_map = options_map
        self.display = ("[p] To parent\n" if parent is not None else "") + display
        self.parent = parent
        self.children = children

    def execute_option(self, choice: str) -> "OptionsNode":  # Can return None
        """
        Does what the user requests based on their choice, either a function from the options_map navigating to a child
        or going back up to the parent node
        :param str as choice:
        :return OptionsNode or None:
        """
        if choice in self.options_map:
            self.options_map[choice]()
        elif self.children is not None and choice in self.children:
            return self.children[choice]
        elif self.parent is not None and choice == "p":
            return self.parent


# Root node for the options tree
root = OptionsNode(
    options_map={
        "e": lambda: o.Options.exit_prog()
    },
    display="[o] View order options\n"
            "[q] View queue options\n"
            "[d] View Data options\n"
            "[c] View Encryption options\n"
            "[e] Exit program\n",
    parent=None,
    children=None
)

root.children = {
    "o": OptionsNode(
        options_map={
            "d": lambda: o.Options.display_orders(),
            "c": lambda: o.Options.create_order(),
            "r": lambda: o.Options.remove_order(),
        },
        display="[d] Display order\n"
                "[c] Create order\n"
                "[r] Remove order\n",
        parent=root,
        children=None
    ),
    "q": OptionsNode(
        options_map={
            "d": lambda: o.Options.display_queue_names(),
            "r": lambda: o.Options.remove_queue(),
            "c": lambda: o.Options.create_queue(),
            "a": lambda: o.Options.add_to_queue(),
            "s": lambda: o.Options.send_queue(),
            "i": lambda: o.Options.is_queue_sending()
        },
        display="[d] Display queue names\n"
                "[r] Remove queue\n"
                "[c] Create queue\n"
                "[a] Add to queue\n"
                "[s] Send queue\n"
                "[i] Is queue being sent\n",
        parent=root,
        children=None
    ),
    "d": OptionsNode(
        options_map={
            "s": lambda: o.Options.display_paper_symbols(),
            "d": lambda: o.Options.get_paper_data(),
            "k": lambda: o.Options.enter_API_keys(),
            "a": lambda: o.Options.view_account(),
            "e": lambda: o.Options.save_everything(),
            "r": lambda: o.Options.reload_local_info(),
        },
        display="[s] Display paper symbols\n"
                "[d] Get paper data\n"
                "[k] Enter API keys\n"
                "[a] View account\n"
                "[e] Save everything\n"
                "[r] Reload information\n",
        parent=root,
        children=None
    ),
    "c": OptionsNode(
        options_map={
            "e": lambda: o.Options.enter_encryption_key(),
            "r": lambda: o.Options.remove_encryption_key(),
            "d": lambda: o.Options.display_encryption_key(),
        },
        display="[e] Enter encryption key\n"
                "[r] Remove encryption key\n"
                "[d] Display encryption key\n",
        parent=root,
        children=None
    )
}

if __name__ == '__main__':
    if u.yes_or_no("Need to enter encryption key?") == "y":
        o.Options.enter_encryption_key()
    storage_manager.FileManager.load_local_info()

    curr: OptionsNode = root
    new_curr: OptionsNode | None
    while True:
        print(curr.display)
        new_curr = curr.execute_option(input("Enter option: "))
        if new_curr is not None:
            curr = new_curr
        else:
            input("Enter to continue: ")
        os.system(g.cls_msg)
