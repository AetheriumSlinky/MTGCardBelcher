"""Refresh timer function class."""

import datetime as dt


class RefreshTimer:
    """
    Creates a timer object with a refresh interval and an expiry time (seconds from now) based on interval.
    """

    def __init__(self, interval: int, stopped=False):
        self.__recur_interval: int = interval
        self.__expiry_time: dt.datetime = dt.datetime.now() + dt.timedelta(seconds=interval)
        self.__expired: bool = False
        self.stopped: bool = stopped

    def __str__(self):
        return f"Attributes: {self.__dict__}"

    def new_expiry_time(self, new_time_from_now: int):
        """
        Sets a new expiry time manually.
        :param new_time_from_now: New expiry time in seconds (i.e. seconds into the future).
        """
        self.__expiry_time = dt.datetime.now() + dt.timedelta(seconds=new_time_from_now)
        self.__expired = False

    def is_it_time(self) -> bool:
        """
        Recurring timer. If interval is not zero it also sets a new expiry time based on interval.
        :return: True if the interval has passed and timer is not stopped, False at other times.
        """
        if self.stopped:
            self.__expired = False

        elif dt.datetime.now() < self.__expiry_time:
            self.__expired = False

        elif dt.datetime.now() > self.__expiry_time:
            if self.__recur_interval:
                self.__expiry_time = dt.datetime.now() + dt.timedelta(seconds=self.__recur_interval)
            self.__expired = True

        return self.__expired
