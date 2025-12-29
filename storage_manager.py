import os
import pickle
from cryptography.fernet import Fernet
from typing import Any, Callable
import order as o
import order_queue as q
import market_data as m
import globals as g


class EncryptionManager:
    encryption_key: bytes | None = None
    cipher: Fernet | None = None
    encrypted: bool = False

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
    def display_encryption_key() -> None:
        """
        Displays encryption key as a base64 encoded string
        :return:
        """
        print(EncryptionManager.encryption_key)

    @staticmethod
    def new_encryption_key(file_path: str | None = None) -> None:
        """
        Decrypts with old decryption key then re encrypts with new encryption key
        Displays to console if file_path is None else prints to file
        :param file_path: string representing a file path
        :return:
        """


    @staticmethod
    def encrypt_pickle_data(encrypted_bytes: bytes) -> bytes:
        """
        Takes encrypted bytes and decrypts them with the EncryptionManager.cipher if it is not None else
        return the given bytes
        :param bytes as encrypted_bytes:
        :return bytes:
        """
        if EncryptionManager.cipher is None:
            return encrypted_bytes
        return EncryptionManager.cipher.encrypt(encrypted_bytes)


    @staticmethod
    def decrypt_pickle_data(decrypted_bytes: bytes) -> bytes:
        """
        Decrypts the given bytes if EncryptionManager.cipher is not None else returns the given bytes
        :param bytes as decrypted_bytes:
        :return bytes:
        """
        if EncryptionManager.cipher is None:
            return decrypted_bytes
        return EncryptionManager.cipher.decrypt(decrypted_bytes)



class FileManager:
    """
    FileManager is a static class that contains all necessary functions and information for loading and saving data
    if you are looking for encryption go to EncryptionManager. All functions are documented with docstring and type
    hinting view each function to see what it does. For the two class variables below file_path_to_keys stores the file
    path to a serialized file that contains information, note when encrypted .enc will be added to the end of the file
    paths when stored on the computer. The value is a tuple of keys that store information as str. The second class
    variable key_to_setter takes a key as a str that represents some key in a dict loaded in when unserializing a saved
    file, then this key is used to get a setter function that sets a variable to the value stored at the unserialized
    saved file dict. For example there is a variable called API_KEY in globals.py one of the saved files to the computer
    has a dict that contains a key called API_KEY that stores the actual API_KEY so the key_to_setter will get key
    API_KEY then it will return a function where you can pass in a value, and it will set the variable API_KEY in
    globals.py to that value.
    """
    file_paths_to_keys: dict[str, tuple[str]] = {
        ".save_info/orders_queues.pkl": ("queues", "orders", "failed"),
        ".save_info/api_keys.pkl": ("API_KEY", "SECRET"),
        ".save_info/paper_info.pkl": ("paper_data", "paper_symbols")
    }
    key_to_setter: dict[str, Callable[[Any], None]] = {
        "queues": lambda new_val: setattr(q.QueueUtility, "all_queues", new_val),
        "orders": lambda new_val: setattr(o.OrderUtility, "all_orders", new_val),
        "failed": lambda new_val: setattr(o.OrderUtility, "failed_orders", new_val),
        "API_KEY": lambda new_val: setattr(g, "API_KEY", new_val),
        "SECRET": lambda new_val: setattr(g, "SECRET", new_val),
        "paper_data": lambda new_val: setattr(m.MarketData, "paper_data", new_val),
        "paper_symbols": lambda new_val: setattr(m.MarketData, "paper_symbols", new_val)
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
                file: bytes

                if FileManager.path_is_encrypted(file_path):
                    if EncryptionManager.cipher is None:
                        print(f"Problem in __info_loader encrypted file detected {file_path} and no encryption key found! {file_path} data cannot and will not be loaded!")
                        return False
                    file = EncryptionManager.cipher.decrypt(file)

                saved_info: dict = pickle.load(file)

                for key in FileManager.file_paths_to_keys[file_path]:
                    key: str
                    FileManager.key_to_setter[key](saved_info[key])
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
        if EncryptionManager.encrypted and EncryptionManager.encryption_key is None:
            print("Cannot load any local info because the data is encrypted and no encryption key is given.")
            return

        for file_path in FileManager.file_paths_to_keys:
            if FileManager.__info_loader(FileManager.encrypt_path(file_path)) or FileManager.__info_loader(file_path):
                continue
            print(f"{file_path} and {file_path}.enc failed to open hence no information can be loaded.")

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
    def save_orders_and_queues() -> bool:
        """
        Saves orders and queues and encrypts them if there is an encryption key
        returns False if the save directory check fails else True
        :return bool:
        """
        if FileManager.save_directory_check() is False:
            return False

        # Continue here

        return True

    @staticmethod
    def save_API_keys() -> bool:
        """
        Saves API keys and encrypts them if there is an encryption key
        returns False if the save directory check fails else True
        """
        if FileManager.save_directory_check() is False:
            return False

        return True

    @staticmethod
    def save_paper_info() -> bool:
        """
        Saves paper data and encrypts them if there is an encryption key
        returns False if the save directory check fails else True
        """
        if FileManager.save_directory_check() is False:
            return False

        return True

    @staticmethod
    def save_all() -> bool:
        """
        Attempts to save orders, queues, API keys, paper information and prints what fails, returns True if everything
        succeeds else returns False
        :return bool:
        """
        orders_and_queues_result: bool = FileManager.save_orders_and_queues()
        if orders_and_queues_result is False:
            print("Failed to save orders and queues")

        api_keys_result: bool = FileManager.save_API_keys()
        if api_keys_result is False:
            print("Failed to save API keys")

        save_paper_result: bool = FileManager.save_paper_info()
        if save_paper_result is False:
            print("Failed to save paper information")

        return orders_and_queues_result and api_keys_result and save_paper_result


if __name__ == "__main__":
    EncryptionManager.set_encryption_info(input("Encryption Key: "))
    EncryptionManager.display_encryption_key()
