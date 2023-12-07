"""
    Distributed Lock implementation. Multiple servers compete to get
    the lock. Only one server can hold the lock at a time.
"""
from kazoo.client import KazooClient
import argparse

class DistributedLock:
    def __init__(self) -> None:
        pass

    def connect(self) -> None:
        pass

    def __del__(self) -> None:
        pass

    def disconnect(self) -> None:
        pass
        
    def do_work(self) -> None:
        pass


if __name__ == "__main__":
    pass
