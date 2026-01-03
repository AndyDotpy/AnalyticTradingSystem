import random
import string
import time
import smtplib
from email.message import EmailMessage


class SecurityManager:
    password: str | None = None
    email_addresses: list[str] = []
    last_login_attempt: float = 0.0
    login_attempts_failed: int = 0

    @staticmethod
    def generate_password(length: int | None = None) -> str:
        """
        Generates a password based on the length if there is no length given a password between 15 and 40 is made
        :param int or None as length:
        :return str:
        """
        return "".join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(random.randint(15, 40) if length is None else length)])

    @staticmethod
    def set_password(new_password: str) -> bool:
        """
        Check if the new password is somewhat secure, it must have more than 10 characters and not be all letters
        or all numbers, returns True if password is set else False
        :param str as new_password:
        :return bool:
        """
        if len(new_password) < 10:
            print("Password has a length of less than 10")
            return False

        if new_password == "".join([character for character in new_password if character in string.ascii_letters]):
            print("Only letters in this password")
            return False

        if new_password == "".join([character for character in new_password if character in string.digits]):
            print("Only numbers in this password")
            return False

        SecurityManager.password = new_password
        return True

    @staticmethod
    def remove_password() -> None:
        """
        Sets the password to None
        :return None:
        """
        SecurityManager.password = None

    @staticmethod
    def add_email_address(email_address: str) -> bool:
        """
        Adds an email address to the email address list, does a light check to make sure the email has one @, a . that
        is not at the end and there are no spaces, returns True if email is added else False
        :param str as email_address:
        :return bool:
        """
        if email_address.count("@") != 1:
            print(f"Email address {email_address} must contain one @")
            return False

        if "." not in email_address or "." == email_address[-1]:
            print(f"No domain found in {email_address}")
            return False

        if " " in email_address:
            print("Cannot have a space in emails")
            return False

        SecurityManager.email_addresses.append(email_address)
        return True

    @staticmethod
    def remove_email_address(email_address: str) -> bool:
        """
        Attempts to remove en email address from the email address list, returns True if it succeeds else False
        :param str as email_address:
        :return bool:
        """
        try:
            SecurityManager.email_addresses.remove(email_address)
            return True
        except ValueError:
            print(f"{email_address} is not found in email address list")
        return False

    @staticmethod
    def __delay_login() -> bool:
        pass

    @staticmethod
    def send_emails() -> None:
        # TODO Need to get this to send the email need to figure out host
        smtp_connection: smtplib.SMTP = smtplib.SMTP("smtp.gmail.com", 465)


        for email_address in SecurityManager.email_addresses:
            email = EmailMessage()
            email.set_content(f"The trading bot has been attempted to be logged into {SecurityManager.login_attempts_failed} times")
            email["Subject"] = "Security Issue With Trading Bot"
            email["From"] = "Trading Bot Security"
            email["To"] = email_address
            smtp_connection.send(email)

        smtp_connection.close()


    @staticmethod
    def login(password: str) -> bool:
        """
        # TODO Finish this after email sending
        Determines if the user logging in should be able to, returns True if they should else False
        :param str as password:
        :return bool:
        """
        SecurityManager.last_login_attempt = time.time()
        SecurityManager.login_attempts_failed += 1

        if password is None or password == SecurityManager.password:
            print("Welcome to greatness!")
            SecurityManager.login_attempts_failed ^= SecurityManager.login_attempts_failed
            return True
        else:
            print("Password incorrect ")
        return False



if __name__ == "__main__":
    SecurityManager.email_addresses.append("") # Add email back when testing
    print(SecurityManager.email_addresses)
    SecurityManager.send_emails()

