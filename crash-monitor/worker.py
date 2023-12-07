"""
    Runs on the worker server.
"""

import argparse
from kazoo.client import KazooClient
import uuid
import time

class NodeHeartBeat:
    """
        Sends heartbeat to the zookeeper server.
    """
    def __init__(self, zookeeper_hosts, node_id, heartbeat_path='/nodes') -> None:
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.heartbeat_path = heartbeat_path

        # If the instance id is not provide, we create one for it        
        if node_id is None:
            self.node_id = uuid.uuid1()

    def connect(self) -> None:
        self.zookeeper.start()

        # If the heartbeat path doesn't exists, create the path
        self.zookeeper.ensure_path(self.heartbeat_path)

        # Create an ephimeral znode for the current node
        # If the node is down, the ephimeral znode will be deleted as 
        # well. The monitoring node will be notified of this event and
        # can take action.
        self.zookeeper.create(
            self.heartbeat_path + "/" + str(self.node_id), ephemeral=True)
        
        print('Heartbeat connection sent to zookeeper server for node: {}'
              .format(self.node_id))

    def disconnect(self) -> None:
        self.zookeeper.close()

    def __del__(self) -> None:
        self.zookeeper.close()


if __name__ == "__main__":
    # python crash-monitor/worker.py
    parser = argparse.ArgumentParser(description="Applicaion heartbeat daemon")
    parser.add_argument('--hosts', type=str, help='Zookeeper hosts',
                        default='localhost:2182,localhost:2183,localhost:2184')
    parser.add_argument('--heartbeat_path', type=str,
                        help='Zookeeper heartbeat path', default='/nodes')
    parser.add_argument('--node_id', type=str, help='Node ID', default=None)

    args = parser.parse_args()

    node_heartbeat = NodeHeartBeat(zookeeper_hosts=args.hosts,
                                   node_id=args.node_id,
                                   heartbeat_path=args.heartbeat_path)
    node_heartbeat.connect()

    while True:
        time.sleep(10)
