"""Refresh timer function class."""

import datetime as dt


class RefreshTimer:
    """
    Creates a timer object with a refresh interval and an expiry time (seconds from now) based on interval.
    """

    def __init__(self, interval: int):
        self.recur_interval: int = interval
        self.expiry_time: dt.datetime = dt.datetime.now() + dt.timedelta(seconds=interval)

    def __str__(self):
        return f"Attributes: {self.__dict__}"

    def new_expiry_time(self, new_time_from_now: int):
        """
        Sets a new expiry time manually.
        :param new_time_from_now: New expiry time as a time delta, in seconds (i.e. seconds into the future).
        """
        self.expiry_time = dt.datetime.now() + dt.timedelta(seconds=new_time_from_now)

    def single_timer(self) -> bool:
        """
        Single-use timer.
        :return: True if interval has passed since setting the timer, False if not. Does not set a new expiry time.
        """
        if dt.datetime.now() > self.expiry_time:
            return True
        else:
            return False

    def recurring_timer(self) -> bool:
        """
        Recurring timer.
        :return: True every time the interval has passed, False at other times. Sets a new expiry time.
        """
        if dt.datetime.now() > self.expiry_time:
            self.expiry_time = dt.datetime.now() + dt.timedelta(seconds=self.recur_interval)
            return True
        else:
            return False
