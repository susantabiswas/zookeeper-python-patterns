from kazoo.client import KazooClient
import argparse
from datetime import datetime
import time

class Worker:
    def __init__(self, zookeeper_hosts, data_path, node_id) -> None:
        self.data_path = data_path
        
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.connect()

    def connect(self) -> None:
        self.zookeeper.start()
        # If the data path doesn't exists, create the path
        self.zookeeper.ensure_path(self.data_path)

    def __del__(self) -> None:
        self.zookeeper.close()

    def set_data(self, data) -> None:
        self.zookeeper.set(path=self.data_path, value=data)
        print('Updated with data: {}'.format(data))


if __name__ == "__main__":
    # python change-data-capture/worker.py --node_id server2
    parser = argparse.ArgumentParser(description="Application data worker")
    parser.add_argument('--hosts', type=str, help='Zookeeper hosts',
                        default='localhost:2182,localhost:2183,localhost:2184')
    parser.add_argument('--data_path', type=str,
                        help='Zookeeper data path', default='/data')
    parser.add_argument('--node_id', type=str, help='Node ID', default=None)
    args = parser.parse_args()

    worker = Worker(zookeeper_hosts=args.hosts,
                            data_path=args.data_path,
                            node_id=args.node_id)

    while True:
        time.sleep(3)
        worker.set_data(('data: {} modified by: {}'.format(datetime.now(), args.node_id)).encode())
