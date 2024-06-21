# zookeeper-python-patterns

# Development Setup
**Check server status**

Shows details of current server like whether follower/leader etc

```cd <zookeeper_directory>
$ ./bin/zkServer.sh status conf2/zoo.cfg
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: conf2/zoo.cfg
Client port found: 2182. Client address: localhost. Client SSL: false.
Mode: follower

```

**Connect a client**

./bin/zkCli.sh -server localhost:2182,localhost:2183,localhost:2184

**Start a server (foreground)**

./bin/zkServer.sh start-foreground conf3/zoo.cfg

**Start a server (background)**

./bin/zkServer.sh start conf3/zoo.cfg

<aside>
💡 Needs a stop command to stop zookeeper

</aside>

<aside>
💡 ./bin/zkServer.sh stop conf3/zoo.cfg

</aside>

**Setup Multi-node setup on the same machine, if actually done on diff machines then no need**

- create separate data folders for each server
- under each data folder, create a file ‘myid’ and inside that put an unique id like 1,2,3 respectively for each of the servers
- create separate conf folders for each server e.g conf1/zoo.cfg
- For each zoo.cfg, make the following change
    
    ```
    # Unique for each server
    dataDir=./data/data1
    # Unique for each server
    clientPort=2184
    
    # At the end append, the same below server details, 2666:3666 (peer-to-peer port: leader election port)
    # put different values server
    server.1=localhost:2666:3666
    server.2=localhost:2667:3667
    server.3=localhost:2668:3668
    ```
    

**Create node**

- **Persistent znode**
    
    create /node_name “node_data”
    
- **Ephimeral znode (Cannot have child nodes)**
    
    create -e /node_name “node_data”
    
- **Sequential znode**
    
    create -s /node_name “node_data”
    
- **We can combine sequential with persistent or ephimeral, by default it is persistent**
    
    create -s -e /node_node 
    

**Delete node**

<aside>
💡 Works only when there are no child nodes left

```jsx
delete /node_node 
```

</aside>
