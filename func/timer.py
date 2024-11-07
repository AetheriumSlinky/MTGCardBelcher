"""Refresh timer function class."""

import datetime as dt

class RefreshTimer:
    """
    Creates a timer object with a refresh interval (seconds).
    """
    def __init__(self, interval: int):
        self.recur_interval: int = interval
        self.expiry_time: dt.datetime = dt.datetime.now() + dt.timedelta(seconds=interval)


    def __str__(self):
        return f"Attributes: {self.__dict__}"


    def single_timer(self) -> bool:
        """
        Single-use timer.
        :return: True if timer has expired, False if not.
        """
        if dt.datetime.now() > self.expiry_time:
            return True
        else:
            return False


    def recurring_timer(self) -> bool:
        """
        Recurring timer.
        :return: True every time the interval has passed since last check, False at other times.
        """
        if dt.datetime.now() > self.expiry_time:
            self.expiry_time = dt.datetime.now() + dt.timedelta(seconds=self.recur_interval)
            return True
        else:
            return False
