"""
    Distributed Lock implementation. Multiple servers compete to get
    the lock. Only one server can hold the lock at a time.
"""
from kazoo.client import KazooClient
import argparse
from datetime import datetime
import uuid
import time


class DistributedLock:
    def __init__(self, zookeeper_hosts, lock_path, node_name) -> None:
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.lock_path = lock_path
        self.node_name = node_name
        self.znode = None

        if self.node_name is None:
            self.node_name = uuid.uuid1()

        self.connect()
        self.acquire_lock()

    def connect(self) -> None:
        self.zookeeper.start()
        # if path doesnt exist, create the path, this will be
        # a persistent path so that it stays even when the clients
        # disconnect
        self.zookeeper.ensure_path(self.lock_path)
        print("\n[Connected] node {} to zookeeper server".format(self.node_name))
        
    def acquire_lock(self) -> None:
        # create an ephimeral znode for the current node
        # to represent the lock for the current node. This znode
        # will be deleted when the node disconnects from the zookeeper
        # Also this is a sequence znode, so zookeeper will ensure all the
        # lock names will be monotonically increasing
        self.znode = self.zookeeper.create(self.lock_path + "/" + str(self.node_name) + "_",
                                    ephemeral=True, sequence=True, makepath=True)
        
        print("[Lock Requested] Lock request znode: {} by node: {}".format(self.znode, self.node_name))

        # add a watcher, this will be notified when there is any modification
        # in the locks path
        self.zookeeper.ChildrenWatch(path=self.lock_path, func=self.lock_watcher)

    def lock_watcher(self, children) -> None:
        if self.znode is None:
            print("Lock znode is not created yet")
            return
        
        # sort the locks by sequence number
        node_locks = [[seq_id, server] for server, seq_id in (lock.split('_') for lock in children)]
        
        # get the smallest lock
        smallest_lock = min(node_locks, key=lambda x: x[0])
        print("Timestamp: {}, smallest:{}, locks:{}"
              .format((datetime.now()).strftime("%B %d, %Y %H:%M:%S"),
              smallest_lock,
              node_locks))
        
        # if the current node's lock is the smallest lock, then
        # the current node has the lock
        if smallest_lock[1] == str(self.node_name):
            print("[Lock acquired] Lock request: {} acquired by node: {}"
                  .format(smallest_lock[1] + '_' + smallest_lock[0], self.node_name))
            self.do_work()

    def do_work(self) -> None:
        print('Work can be done now that the lock has been acquired..')
        time.sleep(5)

    def release_lock(self) -> None:
        znode = self.znode
        self.znode = None
        self.zookeeper.delete(znode)
        # self.zookeeper.stop()
        # self.zookeeper.close()
        print("[Released] Lock released by node: {}".format(self.node_name))
        
    def __del__(self) -> None:
        print("Object deleted")
        # self.release_lock()


if __name__ == "__main__":
    # python distributed-lock/distributed_lock.py --node_name server1
    parser = argparse.ArgumentParser(description="Applicaion heartbeat daemon")
    parser.add_argument('--hosts', type=str, help='Zookeeper hosts',
                        default='localhost:2182,localhost:2183,localhost:2184')
    parser.add_argument('--lock_path', type=str,
                        help='Zookeeper lock path', default='/locks')
    parser.add_argument('--node_name', type=str, help='Node ID', default=None)

    args = parser.parse_args()

    # This will place a lock request by creating a znode,
    # to see how this works, run few instances of this code
    # then whichever acquires the lock, kill that. This will 
    # send a notification to the next smallest lock holder and that can
    # acquire the lock and proceed to work
    distributed_lock = DistributedLock(
                            zookeeper_hosts=args.hosts,
                            lock_path=args.lock_path,
                            node_name=args.node_name)

    while True:
        time.sleep(10)
        
        
        
