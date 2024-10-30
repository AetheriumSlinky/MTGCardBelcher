"""Refresh timer function class."""

import time

class RefreshTimer:
    """
    Creates a timer object with an interval. Starting time is 0.
    """
    def __init__(self, interval: int):
        self.current_time = time.monotonic()
        self.interval = interval

    def __str__(self):
        return f"Attributes: {self.__dict__}"

    def timer(self) -> bool:
        """
        Boolean for whether time is up.
        :return: True if interval has passed, False if not.
        """
        if time.monotonic() - self.current_time > self.interval:
            self.current_time = time.monotonic()
            return True
        else:
            return False
