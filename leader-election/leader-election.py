from kazoo.client import KazooClient
from datetime import datetime
import time
import argparse


class LeaderElection(object):

    def __init__(self, zookeeper_hosts, node_id, node_path):
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.node_path = node_path
        self.node_id = node_id
        
        self.connect()
        self.elect_leader()

    def connect(self):
        self.zookeeper.start()
        
        self.zookeeper.ensure_path(self.node_path)
        self.zookeeper.create("{0}/{1}_".format(self.node_path, self.node_id),
                              ephemeral=True, sequence=True, makepath=True)

    def elect_leader(self):
        self.zookeeper.ChildrenWatch(path=self.node_path, func=self.watch_nodes)

    def watch_nodes(self, children):
        # sort the locks by sequence number
        node_locks = [[seq_id, server] for server, seq_id in (lock.split('_') for lock in children)]
        
        # get the smallest lock
        smallest_lock = min(node_locks, key=lambda x: x[0])
        print("Timestamp: {0}".format((datetime.now()).strftime("%B %d, %Y %H:%M:%S")))
            
        self.display_server_information(node_locks, smallest_lock[1])

        # if the current node's lock is the smallest lock, then
        # the current node has the lock
        if smallest_lock[1] == str(self.node_id):
            print('Node {0} won the leader election'.format(self.node_id))
            self.do_work()

    def do_work(self):
        print("Node {0} is the leader. Do some work...".format(self.node_id))
        time.sleep(10)

    def display_server_information(self, nodes, leader):
        for node in nodes:
            print('Node {}, Role: {}'.format('_'.join(node),
                                            'LEADER' if node[1] == leader else 'FOLLOWER'))
        print()

    def __del__(self):
        self.zookeeper.close()


if __name__ == '__main__':
    # python leader-election/leader-election.py --node_id server1
    parser = argparse.ArgumentParser(description='ZooKeeper example application')
    parser = argparse.ArgumentParser(description="Application heartbeat monitor")
    parser.add_argument('--hosts', type=str, help='Zookeeper hosts',
                        default='localhost:2182,localhost:2183,localhost:2184')
    parser.add_argument('--node_path', type=str,
                        help='Zookeeper heartbeat path', default='/nodes')
    parser.add_argument('--node_id', type=str, help='Node ID', default=None)

    args = parser.parse_args()

    LeaderElection(zookeeper_hosts=args.hosts,
                node_id=args.node_id,
                node_path=args.node_path)

    while True:
        time.sleep(10)