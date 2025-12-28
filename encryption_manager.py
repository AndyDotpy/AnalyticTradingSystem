import os
from cryptography.fernet import Fernet
import utilities


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
        EncryptionManager.encryption_key = encoded_str.encode()
        EncryptionManager.cipher = Fernet(EncryptionManager.encryption_key)

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
    def encrypt_pickle_files() -> None:
        """
        Takes all pickle files and encrypts them
        :return:
        """
        for file_path in utilities.FilePaths:
            with open(file_path, "rb") as pickle_file:
                current_bytes: bytes = EncryptionManager.cipher.encrypt(pickle_file.read())

            #os.rename()  Continue here
            with open(file_path, "wb") as pickle_file:
                pickle_file.write(current_bytes)


    @staticmethod
    def decrypt_pickle_files() -> None:
        """
        Decrypts all pickle files
        :return:
        """


if __name__ == "__main__":
    EncryptionManager.set_encryption_info(input("Encryption Key: "))
    EncryptionManager.display_encryption_key()
