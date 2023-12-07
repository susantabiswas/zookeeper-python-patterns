from kazoo.client import KazooClient
import argparse
from datetime import datetime
import time

class CrashMonitor:
    def __init__(self, zookeeper_hosts, heartbeat_path) -> None:
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.heartbeat_path = heartbeat_path
        self.monitor_path = '/monitors'
        self.connect()
        self.instances = set()

    def connect(self) -> None:
        self.zookeeper.start()
        # If the heartbeat path doesn't exists, create the path
        self.zookeeper.ensure_path(self.heartbeat_path)

        # register the monitor node
        self.zookeeper.create("{}/{}_".format(self.monitor_path, 'monitor'),
                              ephemeral=True, sequence=True, makepath=True)
        
        # get the list of instances to be monitored
        self.instances = set(self.zookeeper.get_children(self.heartbeat_path))
        print('[Startup] Found {} instances. Monitoring started...'.format(len(self.instances)))
        print(self.instances)

    def __del__(self) -> None:
        self.zookeeper.close()

    def send_alert(self, node_id) -> None:
        print("Node {} is down, alert sent!!".format(node_id))

    def monitor(self) -> None:
        # add a watcher to monitor the znode path where heartbeat of instances are saved
        # Everytime there is any modification in the znode path, the watch_nodes function
        # will be called
        self.zookeeper.ChildrenWatch(path=self.heartbeat_path, func=self.watch_nodes)
        print('Monitoring application nodes...')

    def watch_nodes(self, children) -> None:
        print("\nTimestamp: {0}".format((datetime.now()).strftime("%B %d, %Y %H:%M:%S")))
        print('Change detected in application nodes...')

        children = set(children)
        # any instance that is not in the children list is offline
        offline_instances = self.instances - children
        # any instance in children list that is not in currently tracked instances
        # is a new instance
        new_instances = children - self.instances

        print('******* Node Status')
        for child in children:
            print('Node {} status: {}'.format(child,
                                            'ONLINE' if child in self.instances else 'OFFLINE'))

        print('******* New instances found: {}'.format(len(new_instances)))
        for instance in new_instances:
            # new instance found
            self.instances.add(child)
            print('New instance found: {}'.format(instance))

        print('******* Offline instances found: {}'.format(len(offline_instances)))
        for instance in offline_instances:
            # stop tracking the offline instance and send an alert
            self.send_alert(instance)
            self.instances.remove(instance)


if __name__ == "__main__":
    #  python crash-monitor/crash_monitor.py
    parser = argparse.ArgumentParser(description="Application heartbeat monitor")
    parser.add_argument('--hosts', type=str, help='Zookeeper hosts',
                        default='localhost:2182,localhost:2183,localhost:2184')
    parser.add_argument('--heartbeat_path', type=str,
                        help='Zookeeper heartbeat path', default='/nodes')

    args = parser.parse_args()

    node_heartbeat = CrashMonitor(zookeeper_hosts=args.hosts,
                                  heartbeat_path=args.heartbeat_path)
    node_heartbeat.monitor()

    while True:
        time.sleep(10)
