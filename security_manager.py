import random
import string
import time


class SecurityManager:
    __GREEN: str = "GREEN"
    __YELLOW: str = "YELLOW"
    __RED: str = "RED"

    __YELLOW_DELAY: float = 300.0
    __RED_DELAY: float = 1800.0

    delay: float | None = None
    password: str | None = None
    status: str = __GREEN
    previous_status: str = __GREEN
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
    def __update_security_status_on_incorrect_password() -> None:
        """
        Gets called if there is an incorrect password, first increments login_attempts which is only reset when the
        user enters a valid password if the security status is green and 10 or more failed login attempts a five-minute
        delay each time the password is incorrect, the security status is set to yellow, if 20 or more login attempts
        failed security status is set to red and each failed attempt is 30 minutes.
        :return:
        """
        SecurityManager.login_attempts_failed += 1

        if SecurityManager.previous_status != SecurityManager.__GREEN:
            if SecurityManager.login_attempts_failed >= 20 and SecurityManager.status == SecurityManager.__YELLOW:
                SecurityManager.status = SecurityManager.__RED
                SecurityManager.previous_status = SecurityManager.__YELLOW
                SecurityManager.delay = SecurityManager.__RED_DELAY
        elif SecurityManager.login_attempts_failed >= 10:
            SecurityManager.status = SecurityManager.__YELLOW
            SecurityManager.delay = SecurityManager.__YELLOW_DELAY


    @staticmethod
    def __delay_login() -> bool:
        """
        Gets called in the login() function when user is logging in after the last_login_attempt is taken if there is
        a login delay or the login delay is over it returns False else true
        :return bool:
        """
        current_time: float = time.time()

        if SecurityManager.delay is None:
            return False
        elif current_time > current_time + SecurityManager.delay:  # The delay can be negative as its reduced each time the user attempts to login
            SecurityManager.delay = None
            return False
        return True


    @staticmethod
    def login(password: str) -> bool:
        """
        Determines if the user logging in should be able to, returns True if they should else False
        :param str as password:
        :return bool:
        """
        SecurityManager.delay -= SecurityManager.last_login_attempt  # Reduces the delay
        SecurityManager.last_login_attempt = time.time()

        if SecurityManager.__delay_login() is True:
            print("On login delay due to too many incorrect passwords!")
            return False

        if password is None or password == SecurityManager.password:
            print("Welcome to greatness!")
            SecurityManager.login_attempts_failed ^= SecurityManager.login_attempts_failed
            return True
        else:
            SecurityManager.__update_security_status_on_incorrect_password()
            print("Password incorrect!")
        return False

