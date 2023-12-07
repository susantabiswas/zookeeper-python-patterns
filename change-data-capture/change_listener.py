from kazoo.client import KazooClient
import argparse
from datetime import datetime
import time

class ChangeListener:
    def __init__(self, zookeeper_hosts, data_path) -> None:
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.data_path = data_path
        self.connect()

    def connect(self) -> None:
        self.zookeeper.start()
        # If the data path doesn't exists, create the path
        self.zookeeper.ensure_path(self.data_path)

    def __del__(self) -> None:
        self.zookeeper.close()

    def listen(self) -> None:
        # add a watcher to monitor the changes made to the data of znode
        self.zookeeper.DataWatch(path=self.data_path, func=self.watch_data)
        print('Listening to application data changes...')

    def watch_data(self, data, stat) -> None:
        print("\nTimestamp: {0}".format((datetime.now()).strftime("%B %d, %Y %H:%M:%S")))
        print('Change detected in application data...')

        print("Data: {}\nStat: {}".format(data, stat))
        print()


if __name__ == "__main__":
    # python change-data-capture/change_listener.py
    parser = argparse.ArgumentParser(description="Application data change listener")
    parser.add_argument('--hosts', type=str, help='Zookeeper hosts',
                        default='localhost:2182,localhost:2183,localhost:2184')
    parser.add_argument('--data_path', type=str,
                        help='Zookeeper data path', default='/data')

    args = parser.parse_args()

    change_listener = ChangeListener(zookeeper_hosts=args.hosts,
                            data_path=args.data_path)
    change_listener.listen()

    while True:
        time.sleep(10)
