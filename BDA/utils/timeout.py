'''
    BDA - Project - Extraction of crypto wallet addresses from unstructured data sources.
    Author:         Michal Rein (xreinm00@stud.fit.vutbr.cz)
    File:           utils/timeout.py 
'''

import signal
from contextlib import contextmanager

# Timeout exception definition
class TimeoutException(Exception): pass

'''
    Set timeout.

        Parameters:
            seconds (int): Number of seconds after which timeout exception is risen.

        Usage:
            with time_limit(10):
                --- do some code ---
'''
@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)