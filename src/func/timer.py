"""Refresh timer function class."""

import datetime as dt


class RefreshTimer:
    """
    Creates a timer object with a refresh interval and an expiry time (seconds from now) based on interval.
    """

    def __init__(self, interval: int, running=True, refresh_on_start=False):
        self.__recur_interval: int = interval
        if refresh_on_start:
            self.__expiry_time: dt.datetime = dt.datetime.now()
        else:
            self.__expiry_time: dt.datetime = dt.datetime.now() + dt.timedelta(seconds=self.__recur_interval)
        self.__expired: bool = False
        self.__running: bool = running

    def __str__(self):
        return (f"Is running {self.__running}, has expired {self.__expired}, "
                f"next expiry time: {self.__expiry_time} ({self.__expiry_time.strftime("%Y-%m-%d %X")})")

    @property
    def running(self) -> bool:
        return self.__running

    @running.setter
    def running(self, is_running: bool):
        self.__running = is_running

    @property
    def stopped(self) -> bool:
        return not self.__running

    @stopped.setter
    def stopped(self, is_stopped: bool):
        self.__running = not is_stopped

    def new_expiry_time(self, seconds_into_future: int=None, new_expiry_time: dt.datetime=None):
        """
        Sets a new expiry time manually.
        :param seconds_into_future: New expiry timedelta in seconds (i.e. seconds into the future).
        :param new_expiry_time: New expiry time as a datetime object. Must be in the future.
        """
        if new_expiry_time is not None and new_expiry_time > dt.datetime.now():
            self.__expiry_time = new_expiry_time
        else:
            self.__expiry_time = dt.datetime.now() + dt.timedelta(seconds=seconds_into_future)

    def is_it_time(self) -> bool:
        """
        Checks if the timer has expired (interval has passed).
        If interval is non-zero it sets a new expiry time based on interval if the timer has expired.
        :return: True if the interval has passed and timer is running, otherwise False.
        """
        if dt.datetime.now() >= self.__expiry_time and self.__running:
            if self.__recur_interval:
                self.__expiry_time = dt.datetime.now() + dt.timedelta(seconds=self.__recur_interval)
            return True
        return False
