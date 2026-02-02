import os
import pickle
from cryptography.fernet import Fernet
from typing import Any, Callable, BinaryIO
import order as o
import order_queue as q
import market_data as m
import globals as g
import security_manager as s
from alpaca.trading.client import TradingClient


class EncryptionManager:
    """
    Helper static class for FileManager that does encryption related tasks such as setting and storing the encryption
    information the user enters
    """
    encryption_key: bytes | None = None
    cipher: Fernet | None = None

    @staticmethod
    def set_encryption_info(encoded_str: str) -> None:
        """
        Sets the EncryptionManager encryption_key and cipher
        :param encoded_str: Base64 encoded string
        :return None:
        """
        try:
            EncryptionManager.encryption_key = encoded_str.encode()
            EncryptionManager.cipher = Fernet(EncryptionManager.encryption_key)
        except UnicodeEncodeError as e:
            print(f"Encryption key failed due to {e}")

    @staticmethod
    def remove_encryption_info() -> None:
        """
        Sets all encryption information such as encryption_key and cipher to None
        :return:
        """
        EncryptionManager.encryption_key = None
        EncryptionManager.cipher = None

    @staticmethod
    def display_encryption_key() -> None:
        """
        Displays encryption key as a base64 encoded string
        :return:
        """
        print(EncryptionManager.encryption_key)


    @staticmethod
    def encrypt_pickle_data(encrypted_bytes: bytes) -> bytes:
        """
        Takes encrypted bytes and decrypts them with the EncryptionManager.cipher if it is not None else
        return the given bytes
        Displays error message if applicable
        Note this is a helper method for FileManager
        :param bytes as encrypted_bytes:
        :return bytes:
        """
        if EncryptionManager.cipher is None:
            print("Attempted to encrypt data with no cipher, returns given bytes.")
            return encrypted_bytes
        return EncryptionManager.cipher.encrypt(encrypted_bytes)


    @staticmethod
    def decrypt_pickle_data(decrypted_bytes: bytes) -> bytes:
        """
        Decrypts the given bytes if EncryptionManager.cipher is not None else returns the given bytes
        Displays error message if applicable
        Note this is a helper method for FileManager
        :param bytes as decrypted_bytes:
        :return bytes:
        """
        if EncryptionManager.cipher is None:
            print("Attempted to decrypt data with no cipher, returns given bytes.")
            return decrypted_bytes
        return EncryptionManager.cipher.decrypt(decrypted_bytes)



class FileManager:
    """
    FileManager is a static class that contains all necessary functions and information for loading and saving data
    if you are looking for encryption go to EncryptionManager. All functions are documented with docstring and type
    hinting view each function to see what it does. For the three class variables below file_path_to_keys stores the file
    path to a serialized file that contains information, note when encrypted .enc will be added to the end of the file
    paths when stored on the computer. The value is a tuple of keys that store information as str. The second class
    variable KEY_TO_SETTER takes a key as a str that represents some key in a dict loaded in when unserializing a saved
    file, then this key is used to get a setter function that sets a variable to the value stored at the unserialized
    saved file dict. For example there is a variable called API_KEY in globals.py one of the saved files to the computer
    has a dict that contains a key called API_KEY that stores the actual API_KEY so the KEY_TO_SETTER will get key
    API_KEY then it will return a function where you can pass in a value, and it will set the variable API_KEY in
    globals.py to that value. The KEY_TO_GETTER takes a key as a str same as KEY_TO_SETTER and will return the value
    that is supposed to be stored in that part of the dict that will be saved to the computer.
    """
    FILE_PATH_TO_KEYS: dict[str, tuple[str]] = {
        ".save_info/orders_queues.pkl": ("queues", "orders", "failed"),
        ".save_info/api_keys.pkl": ("API_KEY", "SECRET"),
        ".save_info/paper_info.pkl": ("paper_data", "paper_symbols"),
        ".save_info/security_info.pkl": (
            "delay", "password", "status", "previous_status", "last_login_attempt", "login_attempts_failed"
        )
    }
    KEY_TO_SETTER: dict[str, Callable[[Any], None]] = {
        "queues": lambda new_val: setattr(q.QueueUtility, "all_queues", new_val),
        "orders": lambda new_val: setattr(o.OrderUtility, "all_orders", new_val),
        "failed": lambda new_val: setattr(o.OrderUtility, "failed_orders", new_val),
        "API_KEY": lambda new_val: setattr(g, "API_KEY", new_val),
        "SECRET": lambda new_val: setattr(g, "SECRET", new_val),
        "paper_data": lambda new_val: setattr(m.MarketData, "paper_data", new_val),
        "paper_symbols": lambda new_val: setattr(m.MarketData, "paper_symbols", new_val),
        "delay": lambda new_val: setattr(s.SecurityManager, "delay", new_val),
        "password": lambda new_val: setattr(s.SecurityManager, "password", new_val),
        "status": lambda new_val: setattr(s.SecurityManager, "status", new_val),
        "previous_status": lambda new_val: setattr(s.SecurityManager, "previous_status", new_val),
        "last_login_attempt": lambda new_val: setattr(s.SecurityManager, "last_login_attempt", new_val),
        "login_attempts_failed": lambda new_val: setattr(s.SecurityManager, "login_attempts_failed", new_val),

    }
    KEY_TO_GETTER: dict[str, Callable[[], Any]] = {
        "queues": lambda: getattr(q.QueueUtility, "all_queues"),
        "orders": lambda: getattr(o.OrderUtility, "all_orders"),
        "failed": lambda: getattr(o.OrderUtility, "failed_orders"),
        "API_KEY": lambda: getattr(g, "API_KEY"),
        "SECRET": lambda: getattr(g, "SECRET"),
        "paper_data": lambda: getattr(m.MarketData, "paper_data"),
        "paper_symbols": lambda: getattr(m.MarketData, "paper_symbols"),
        "delay": lambda: getattr(s.SecurityManager, "delay"),
        "password": lambda: getattr(s.SecurityManager, "password"),
        "status": lambda: getattr(s.SecurityManager, "status"),
        "previous_status": lambda: getattr(s.SecurityManager, "previous_status"),
        "last_login_attempt": lambda: getattr(s.SecurityManager, "last_login_attempt"),
        "login_attempts_failed": lambda: getattr(s.SecurityManager, "login_attempts_failed"),
    }

    @staticmethod
    def path_is_encrypted(path: str) -> bool:
        """
        Returns true of the file path ends in .enc
        :param str as path:
        :return bool:
        """
        if len(path) < 4:
            return False

        return path[-4:] == ".enc"

    @staticmethod
    def encrypt_path(unencrypted_path: str) -> str:
        """
        Adds .enc to the end of the file path and returns it, makes sure it does not already end in .enc
        before adding .enc
        :param str as unencrypted_path:
        :return str:
        """
        if FileManager.path_is_encrypted(unencrypted_path):
            return unencrypted_path
        return unencrypted_path + ".enc"

    @staticmethod
    def decrypt_path(encrypted_path: str) -> str:
        """
        Removes .enc from the end of the file path if it is there and returns the new file path
        :param str as encrypted_path:
        :return str:
        """
        if FileManager.path_is_encrypted(encrypted_path):
            return encrypted_path[:-4]
        return encrypted_path

    @staticmethod
    def __info_loader(file_path: str) -> bool:
        """
        This function attempts to load the information at a given file location returns True if successful
        Private helper function for load_local_info()
        :param str as file_path: The path to the file attempting to be loaded
        :return bool: True indicates successfully loaded else False
        """
        try:
            with open(file_path, "rb") as file:
                file: BinaryIO
                file_contents: bytes = file.read()

                if FileManager.path_is_encrypted(file_path):
                    if EncryptionManager.cipher is None:
                        print(f"Problem in __info_loader encrypted file detected {file_path} and no encryption key found! {file_path} data cannot and will not be loaded!")
                        return False
                    file_contents = EncryptionManager.decrypt_pickle_data(file_contents)

                saved_info: dict[str, Any] = pickle.loads(file_contents)

                for key in FileManager.FILE_PATH_TO_KEYS[FileManager.decrypt_path(file_path)]:
                    key: str
                    FileManager.KEY_TO_SETTER[key](saved_info[key])
            return True
        except OSError:
            return False

    @staticmethod
    def load_local_info() -> None:
        """
        Loads all local orders, symbols and queues
        Uses private helper function __info_loader(str) -> bool
        :return:
        """
        for file_path in FileManager.FILE_PATH_TO_KEYS:
            if FileManager.__info_loader(FileManager.encrypt_path(file_path)) or FileManager.__info_loader(file_path):
                continue
            print(f"{file_path} and {file_path}.enc failed to open hence no information can be loaded.")

        if g.API_KEY != "" and g.SECRET != "":
            g.trading_client = TradingClient(g.API_KEY, g.SECRET, paper=True)
            print("Set trading client!")
        else:
            print("No previous keys obtained trading client not set!")
        print("Loaded local information.")

    @staticmethod
    def save_directory_check() -> bool:
        """
        Attempts to make a directory called .save_info where all .pkl files are saved returns True if it exists or has been
        created False otherwise
        Make sure to use this is saving something to the device
        :return bool:
        """
        try:
            os.mkdir(path=".save_info")
            return True
        except FileExistsError:
            return True
        except FileNotFoundError:
            print("Parent directory or path does not exist for \".save_info\" no save directory created")
            return False

    @staticmethod
    def __info_saver(file_path: str) -> bool:
        """
        Returns True if successfully saved serialized and maybe encrypted dict of information else False
        Will encrypt if the encryption key has been set
        :param str as file_path:
        :return bool:
        """
        decrypted_path: str = FileManager.decrypt_path(file_path)
        encrypted_path: str = FileManager.encrypt_path(file_path)

        unsaved_info: dict = {}
        for key in FileManager.FILE_PATH_TO_KEYS[decrypted_path]:
            key: str
            unsaved_info[key] = FileManager.KEY_TO_GETTER[key]()

        unsaved_bytes: bytes = pickle.dumps(unsaved_info)

        encrypted: bool = False
        if EncryptionManager.cipher is not None:
            unsaved_bytes = EncryptionManager.encrypt_pickle_data(unsaved_bytes)
            encrypted = True

        try:
            with open(encrypted_path if encrypted else decrypted_path, "wb") as file:
                file.write(unsaved_bytes)
        except OSError:
            print(f"Failed to save to file {file_path} when opening the file for writing bytes.")
            return False

        try:
            if encrypted:
                os.remove(decrypted_path)
            else:
                os.remove(encrypted_path)
        except OSError:
            pass

        return True

    @staticmethod
    def save_orders_and_queues() -> bool:
        """
        Saves orders and queues and encrypts them if there is an encryption key
        returns False if the save directory check fails else True
        :return bool:
        """
        if FileManager.save_directory_check() is False:
            return False
        return FileManager.__info_saver(".save_info/orders_queues.pkl")

    @staticmethod
    def save_API_keys() -> bool:
        """
        Saves API keys and encrypts them if there is an encryption key
        returns False if the save directory check fails else True
        """
        if FileManager.save_directory_check() is False:
            return False
        return FileManager.__info_saver(".save_info/api_keys.pkl")

    @staticmethod
    def save_paper_info() -> bool:
        """
        Saves paper data and encrypts them if there is an encryption key
        returns False if the save directory check fails else True
        """
        if FileManager.save_directory_check() is False:
            return False
        return FileManager.__info_saver(".save_info/paper_info.pkl")

    @staticmethod
    def save_all() -> bool:
        """
        Attempts to save orders, queues, API keys, paper information and prints what fails, returns True if everything
        succeeds else returns False
        :return bool:
        """
        if FileManager.save_directory_check() is False:
            return False

        all_success: bool = True
        for file_path in FileManager.FILE_PATH_TO_KEYS:
            if FileManager.__info_saver(file_path) is False:
                print(f"{file_path} failed to save!")
                all_success = False

        return all_success
