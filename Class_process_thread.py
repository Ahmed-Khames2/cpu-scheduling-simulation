import threading
import time

class BaseProcessThread(threading.Thread):
    """
    Base class for all algorithms.
    - Contains shared attributes (name, arrival, burst, remaining...)
    - run() method is intentionally NOT implemented.
    - Some algorithms may need a lock, so it's optional.
    """

    def __init__(self, name, arrival, burst, use_lock=False):
        super().__init__(daemon=True)
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.event = threading.Event()
        self.started = False
        self.finish_time = None
        self.response_time = None

        # lock optional
        self.lock = threading.Lock() if use_lock else None

    def run(self):
        """
        This should be implemented ONLY inside each scheduler file.
        """
        raise NotImplementedError("run() must be implemented inside each algorithm file.")
