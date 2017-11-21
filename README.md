# Arcus
NAVER에서 오픈소스로 발표한 [Arcus]를 [Docker]로 구성 할수 있도록 Dockerfile을 만들어 보았습니다.

Step 1,2,3,4 이후에는 이 [Link]를 통해 "4. Arcus 설정"부터 따라 하시면 됩니다.


### Step 1. Git clone

```
root@ruo91:~# git clone git://github.com/ruo91/docker-arcus /opt/docker-arcus
```


### Step 2. Container Image
HostOS에서 Arcus Admin과 Memcached로 사용될 Container의 이미지를 만듭니다.

- Arcus Admin
```
root@ruo91:~# docker build --rm -t arcus-admin /opt/docker-arcus/arcus
```

- Memcached
```
root@ruo91:~# docker build --rm -t arcus-memcached /opt/docker-arcus/arcus-memcached
```


### Step 3. Container 실행
Arcus Admin으로 사용될 Container를 하나 생성하고, Memcached로 사용될 Container를 3개 생성합니다.

- Arcus Admin
```
root@ruo91:~# docker run -d --name="arcus-admin" -h "arcus" arcus-admin
```

- Memcached
```
root@ruo91:~# docker run -d --name="arcus-memcached-1" -h "memcached-1" arcus-memcached
root@ruo91:~# docker run -d --name="arcus-memcached-2" -h "memcached-2" arcus-memcached
root@ruo91:~# docker run -d --name="arcus-memcached-3" -h "memcached-3" arcus-memcached
```


### Step 4. Container IP 확인 및 SSH 접속
arcus-admin, arcus-memcached의 SSH 비밀번호는 "arcus"와 "memcached" 입니다.

```
root@ruo91:~# docker inspect -f '{{ .NetworkSettings.IPAddress }}' \
arcus-admin arcus-memcached-1 arcus-memcached-2 arcus-memcached-3
```

```
root@ruo91:~# ssh `docker inspect -f '{{ .NetworkSettings.IPAddress }}' arcus-admin`
root@ruo91:~# ssh `docker inspect -f '{{ .NetworkSettings.IPAddress }}' arcus-memcached-1`
root@ruo91:~# ssh `docker inspect -f '{{ .NetworkSettings.IPAddress }}' arcus-memcached-2`
root@ruo91:~# ssh `docker inspect -f '{{ .NetworkSettings.IPAddress }}' arcus-memcached-3`
```


### Step 5. Zookeeper 설정
Arcus는 “scripts/arcus.sh”라는 쉘 스크립트를 사용 하여 관리 합니다.

이 스크립트를 사용할때 마다 -z 옵션을 사용하여야 하는데, 이 옵션은 zookeeper 서버 정보를 입력 받습니다.

관리할 서버가 많아지면 이것도 귀찮은 작업이 되므로, 해당 스크립트 내용중 “zklist”라는 변수에 관리할 zookeeper 서버 정보를 입력 하면, 매번 -z 옵션을 쓰지 않아도 됩니다.

“zklist” 변수의 기본값은 “127.0.0.1:2181″이며 “[ip or host]:[zookeeper port]” 형태로 수정 하시면 됩니다.

관리할 Zookeeper 서버가 많다면, zklist=”172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181″ 와 같이 쉼표를 사용하여 추가 하면 됩니다.

```
root@arcus:/opt/arcus/scripts# sed -i 's/127.0.0.1:2181/172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181/g' arcus.sh
```


### Step 6. SSH Public Key 배포
Memcached로 사용될 서버에 배포 합니다.

```
root@arcus:/opt/arcus/scripts# scp /root/.ssh/authorized_keys root@172.17.0.3:/root/.ssh
root@arcus:/opt/arcus/scripts# scp /root/.ssh/authorized_keys root@172.17.0.4:/root/.ssh
root@arcus:/opt/arcus/scripts# scp /root/.ssh/authorized_keys root@172.17.0.5:/root/.ssh
```

### Step 7. Cache Cloud 설정
conf 디렉토리에 json 형식으로 파일을 생성 하고, 내용에는 Memcached 서버 정보를 알맞게 추가 합니다.

(설정법은 Arcus Configuration File 를 참고하시기 바랍니다.)

하나의 서버에 두개의 Memcached를 실행 하도록 설정 하겠습니다.

```
root@arcus:/opt/arcus/scripts# nano conf/ruo91.json
{
    "serviceCode": "ruo91-cloud"
  , "servers": [
        { "hostname": "memcached-1", "ip": "172.17.0.3",
          "config": {
              "port"   : "11211"
          }
        }
      , { "hostname": "memcached-1", "ip": "172.17.0.3",
          "config": {
              "port"   : "11212"
          }
        }
      , { "hostname": "memcached-2", "ip": "172.17.0.4",
          "config": {
              "port"   : "11211"
          }
        }
      , { "hostname": "memcached-2", "ip": "172.17.0.4",
          "config": {
              "port"   : "11212"
          }
        }
      , { "hostname": "memcached-3", "ip": "172.17.0.5",
          "config": {
              "port"   : "11211"
          }
        }
      , { "hostname": "memcached-3", "ip": "172.17.0.5",
          "config": {
              "port"   : "11212"
          }
        }
    ]
  , "config": {
        "threads"    : "6"
      , "memlimit"   : "100"
      , "connections": "1000"
    }
}
```


### Step 8. Arcus 배포
이제 memcached-1, memcached-2, memcached-3 서버에 arcus를 배포 합니다.

배포 과정에서 주의 할점은, arcus.tar.gz 파일을 netcat 유틸리티로 파일을 전송하기 때문에, netcat 유틸리티가 미리 설치가 되어 있어야 한다는 점 입니다. (없는 경우는 극히 드물지만..)

```
root@arcus:/opt/arcus/scripts# ./arcus.sh deploy conf/ruo91.json
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': [u'172.17.0.3', u'172.17.0.3', u'172.17.0.4', u'172.17.0.4', u'172.17.0.5', u'172.17.0.5']}

[172.17.0.3] Executing task 'deploy'
[172.17.0.4] Executing task 'deploy'
[172.17.0.5] Executing task 'deploy'
[172.17.0.5] run: mkdir -p /opt
[172.17.0.3] run: mkdir -p /opt
[172.17.0.4] run: mkdir -p /opt
[172.17.0.4] out: stdin: is not a tty
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out:

[localhost] local: tar -czf /tmp/tmpeE1gcF/arcus.tar.gz -C /opt arcus
[172.17.0.4] out:
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out:

[localhost] local: tar -czf /tmp/tmp2FNcZ3/arcus.tar.gz -C /opt arcus

[localhost] local: tar -czf /tmp/tmpCvCnQI/arcus.tar.gz -C /opt arcus
[172.17.0.5] put: /tmp/tmpCvCnQI/arcus.tar.gz -> /opt/arcus.tar.gz
[172.17.0.3] put: /tmp/tmpeE1gcF/arcus.tar.gz -> /opt/arcus.tar.gz
[172.17.0.4] put: /tmp/tmp2FNcZ3/arcus.tar.gz -> /opt/arcus.tar.gz
[172.17.0.5] run: tar -xzf arcus.tar.gz
[172.17.0.5] out: stdin: is not a tty
[172.17.0.3] run: tar -xzf arcus.tar.gz
[172.17.0.3] out: stdin: is not a tty
[172.17.0.4] run: tar -xzf arcus.tar.gz
[172.17.0.4] out: stdin: is not a tty
[172.17.0.5] out:

[172.17.0.5] run: rm -f arcus.tar.gz
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out:

[localhost] local: rm -rf /tmp/tmpCvCnQI
[172.17.0.3] out:

[172.17.0.3] run: rm -f arcus.tar.gz
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out:

[localhost] local: rm -rf /tmp/tmpeE1gcF
[172.17.0.4] out:

[172.17.0.4] run: rm -f arcus.tar.gz
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out:

[localhost] local: rm -rf /tmp/tmp2FNcZ3

Done.
```


### Step 9. Zoopkeeper 앙상블 설정
Arcus에서 사용하는 Zookeeper 앙상블을 설정 합니다.

명령이 끝난 뒤에 Zookeeper는 Ephemeral node 즉, 장애 발생시 자동으로 node가 지워질수 있도록 설정 됩니다.

```
root@arcus:/opt/arcus/scripts# ./arcus.sh zookeeper init
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': []}

====== Task: zk_config
[172.17.0.3] Executing task 'zk_config_id'
[172.17.0.3] run: mkdir -p data
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out:

[172.17.0.3] run: echo 1 > data/myid
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out:

[172.17.0.3] put: <file obj> -> /opt/arcus/zookeeper/conf/zoo.cfg
[172.17.0.4] Executing task 'zk_config_id'
[172.17.0.4] run: mkdir -p data
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out:

[172.17.0.4] run: echo 2 > data/myid
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out:

[172.17.0.4] put: <file obj> -> /opt/arcus/zookeeper/conf/zoo.cfg
[172.17.0.5] Executing task 'zk_config_id'
[172.17.0.5] run: mkdir -p data
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out:

[172.17.0.5] run: echo 3 > data/myid
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out:

[172.17.0.5] put: <file obj> -> /opt/arcus/zookeeper/conf/zoo.cfg
====== Task: zk_start
[172.17.0.3] Executing task 'zk_start'
[172.17.0.3] run: bin/zkServer.sh start
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: JMX enabled by default
[172.17.0.3] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.3] out: Starting zookeeper ... STARTED
[172.17.0.3] out:

[172.17.0.4] Executing task 'zk_start'
[172.17.0.4] run: bin/zkServer.sh start
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: JMX enabled by default
[172.17.0.4] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.4] out: Starting zookeeper ... STARTED
[172.17.0.4] out:

[172.17.0.5] Executing task 'zk_start'
[172.17.0.5] run: bin/zkServer.sh start
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: JMX enabled by default
[172.17.0.5] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.5] out: Starting zookeeper ... STARTED
[172.17.0.5] out:

====== Func: zk_wait
[172.17.0.3] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: Mode: follower
[172.17.0.3] out:

[172.17.0.4] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: Mode: stale
[172.17.0.4] out:

[172.17.0.5] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: Mode: follower
[172.17.0.5] out:

zookeeper cluster not complete yet; sleeping 3 seconds
[172.17.0.3] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: Mode: follower
[172.17.0.3] out:

[172.17.0.4] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: Mode: stale
[172.17.0.4] out:

[172.17.0.5] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: Mode: follower
[172.17.0.5] out:

zookeeper cluster not complete yet; sleeping 3 seconds
[172.17.0.3] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: Mode: follower
[172.17.0.3] out:

[172.17.0.4] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: Mode: stale
[172.17.0.4] out:

[172.17.0.5] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: Mode: follower
[172.17.0.5] out:

zookeeper cluster not complete yet; sleeping 3 seconds
[172.17.0.3] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: Mode: follower
[172.17.0.3] out:

[172.17.0.4] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: Mode: leader
[172.17.0.4] out:

[172.17.0.5] run: GOT=$(echo stat | nc localhost 2181 | grep Mode:); if [ -z "$GOT" ]; then echo "Mode: stale"; else echo $GOT; fi
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: Mode: follower
[172.17.0.5] out:

got a leader, and all nodes are up
====== Task: zk_create_arcus_structure
[u'/arcus', u'/arcus/cache_list', u'/arcus/client_list', u'/arcus/cache_server_mapping']
/arcus/cache_list
/arcus/client_list
/arcus/cache_server_mapping
====== Task: zk_stop
[172.17.0.3] Executing task 'zk_stop'
[172.17.0.3] run: bin/zkServer.sh stop
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: JMX enabled by default
[172.17.0.3] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.3] out: Stopping zookeeper ... STOPPED
[172.17.0.3] out:

[172.17.0.4] Executing task 'zk_stop'
[172.17.0.4] run: bin/zkServer.sh stop
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: JMX enabled by default
[172.17.0.4] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.4] out: Stopping zookeeper ... STOPPED
[172.17.0.4] out:

[172.17.0.5] Executing task 'zk_stop'
[172.17.0.5] run: bin/zkServer.sh stop
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: JMX enabled by default
[172.17.0.5] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.5] out: Stopping zookeeper ... STOPPED
[172.17.0.5] out:

Done.
Disconnecting from 172.17.0.4... done.
Disconnecting from 172.17.0.3... done.
Disconnecting from 172.17.0.5... done.
```


### Step 10. Zookeeper 실행
등록 된 zookeeper 서버를 시작합니다.

```
root@arcus:/opt/arcus/scripts# ./arcus.sh zookeeper start
Server Roles
{'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': []}

[172.17.0.3] Executing task 'zk_start'
[172.17.0.3] run: bin/zkServer.sh start
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: JMX enabled by default
[172.17.0.3] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.3] out: Starting zookeeper ... STARTED
[172.17.0.3] out:

[172.17.0.4] Executing task 'zk_start'
[172.17.0.4] run: bin/zkServer.sh start
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: JMX enabled by default
[172.17.0.4] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.4] out: Starting zookeeper ... STARTED
[172.17.0.4] out:

[172.17.0.5] Executing task 'zk_start'
[172.17.0.5] run: bin/zkServer.sh start
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: JMX enabled by default
[172.17.0.5] out: Using config: /opt/arcus/zookeeper/bin/../conf/zoo.cfg
[172.17.0.5] out: Starting zookeeper ... STARTED
[172.17.0.5] out:


Done.
Disconnecting from 172.17.0.4... done.
Disconnecting from 172.17.0.3... done.
Disconnecting from 172.17.0.5... done.
```


### Step 11. Zookeeper 상태 확인
정상적으로 실행 되었는지 확인 합니다.

```
root@arcus:/opt/arcus/scripts# ./arcus.sh zookeeper stat
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': []}

[172.17.0.3] Executing task 'zk_stat'
[172.17.0.3] run: echo stat | nc localhost 2181
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out: Zookeeper version: 3.4.5--1, built on 05/22/2014 07:16 GMT
[172.17.0.3] out: Clients:
[172.17.0.3] out:  /0:0:0:0:0:0:0:1:43361[0](queued=0,recved=1,sent=0)
[172.17.0.3] out:
[172.17.0.3] out: Latency min/avg/max: 0/0/0
[172.17.0.3] out: Received: 1
[172.17.0.3] out: Sent: 0
[172.17.0.3] out: Connections: 1
[172.17.0.3] out: Outstanding: 0
[172.17.0.3] out: Zxid: 0x100000003
[172.17.0.3] out: Mode: follower
[172.17.0.3] out: Node count: 8
[172.17.0.3] out:

[172.17.0.4] Executing task 'zk_stat'
[172.17.0.4] run: echo stat | nc localhost 2181
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out: This ZooKeeper instance is not currently serving requests
[172.17.0.4] out:

[172.17.0.5] Executing task 'zk_stat'
[172.17.0.5] run: echo stat | nc localhost 2181
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out: Zookeeper version: 3.4.5--1, built on 05/22/2014 07:16 GMT
[172.17.0.5] out: Clients:
[172.17.0.5] out:  /0:0:0:0:0:0:0:1:43365[0](queued=0,recved=1,sent=0)
[172.17.0.5] out:
[172.17.0.5] out: Latency min/avg/max: 0/0/0
[172.17.0.5] out: Received: 1
[172.17.0.5] out: Sent: 0
[172.17.0.5] out: Connections: 1
[172.17.0.5] out: Outstanding: 0
[172.17.0.5] out: Zxid: 0x100000003
[172.17.0.5] out: Mode: follower
[172.17.0.5] out: Node count: 8
[172.17.0.5] out:


Done.
Disconnecting from 172.17.0.4... done.
Disconnecting from 172.17.0.3... done.
Disconnecting from 172.17.0.5... done.
```


### Step 12. Memcached 등록
Memcached 서버를 등록 합니다.

```
root@arcus:/opt/arcus/scripts# ./arcus.sh memcached register conf/ruo91.json
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': [u'172.17.0.3', u'172.17.0.3', u'172.17.0.4', u'172.17.0.4', u'172.17.0.5', u'172.17.0.5']}

No handlers could be found for logger "kazoo.client"
[u'/arcus/cache_list/ruo91-cloud', u'/arcus/client_list/ruo91-cloud', u'/arcus/cache_server_mapping/172.17.0.3:11211', u'/arcus/cache_server_mapping/172.17.0.3:11211/ruo91-cloud', u'/arcus/cache_server_mapping/172.17.0.3:11212', u'/arcus/cache_server_mapping/172.17.0.3:11212/ruo91-cloud', u'/arcus/cache_server_mapping/172.17.0.4:11211', u'/arcus/cache_server_mapping/172.17.0.4:11211/ruo91-cloud', u'/arcus/cache_server_mapping/172.17.0.4:11212', u'/arcus/cache_server_mapping/172.17.0.4:11212/ruo91-cloud', u'/arcus/cache_server_mapping/172.17.0.5:11211', u'/arcus/cache_server_mapping/172.17.0.5:11211/ruo91-cloud', u'/arcus/cache_server_mapping/172.17.0.5:11212', u'/arcus/cache_server_mapping/172.17.0.5:11212/ruo91-cloud']

Done.
```


### Step 13. Memcached 실행
Dockerfile에서 설정한 memcached 사용자로 Memcached가 실행이 됩니다.

```
root@arcus:/opt/arcus/scripts# ./arcus.sh memcached start ruo91-cloud
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': []}

[172.17.0.3] Executing task 'mc_start_server'
[172.17.0.3] run: /opt/arcus/bin/memcached -u memcached -E /opt/arcus/lib/default_engine.so -X /opt/arcus/lib/syslog_logger.so -X /opt/arcus/lib/ascii_scrub.so -d -v -r -R5 -U 0 -D: -b 8192 -m100 -p 11211 -c 1000 -t 6 -z 172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out:
[172.17.0.3] Executing task 'mc_start_server'
[172.17.0.3] run: /opt/arcus/bin/memcached -u memcached -E /opt/arcus/lib/default_engine.so -X /opt/arcus/lib/syslog_logger.so -X /opt/arcus/lib/ascii_scrub.so -d -v -r -R5 -U 0 -D: -b 8192 -m100 -p 11212 -c 1000 -t 6 -z 172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181
[172.17.0.3] out: stdin: is not a tty
[172.17.0.3] out:
[172.17.0.4] Executing task 'mc_start_server'
[172.17.0.4] run: /opt/arcus/bin/memcached -u memcached -E /opt/arcus/lib/default_engine.so -X /opt/arcus/lib/syslog_logger.so -X /opt/arcus/lib/ascii_scrub.so -d -v -r -R5 -U 0 -D: -b 8192 -m100 -p 11211 -c 1000 -t 6 -z 172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out:
[172.17.0.4] Executing task 'mc_start_server'
[172.17.0.4] run: /opt/arcus/bin/memcached -u memcached -E /opt/arcus/lib/default_engine.so -X /opt/arcus/lib/syslog_logger.so -X /opt/arcus/lib/ascii_scrub.so -d -v -r -R5 -U 0 -D: -b 8192 -m100 -p 11212 -c 1000 -t 6 -z 172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181
[172.17.0.4] out: stdin: is not a tty
[172.17.0.4] out:
[172.17.0.5] Executing task 'mc_start_server'
[172.17.0.5] run: /opt/arcus/bin/memcached -u memcached -E /opt/arcus/lib/default_engine.so -X /opt/arcus/lib/syslog_logger.so -X /opt/arcus/lib/ascii_scrub.so -d -v -r -R5 -U 0 -D: -b 8192 -m100 -p 11211 -c 1000 -t 6 -z 172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out:
[172.17.0.5] Executing task 'mc_start_server'
[172.17.0.5] run: /opt/arcus/bin/memcached -u memcached -E /opt/arcus/lib/default_engine.so -X /opt/arcus/lib/syslog_logger.so -X /opt/arcus/lib/ascii_scrub.so -d -v -r -R5 -U 0 -D: -b 8192 -m100 -p 11212 -c 1000 -t 6 -z 172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181
[172.17.0.5] out: stdin: is not a tty
[172.17.0.5] out:

Done.
Disconnecting from 172.17.0.4... done.
Disconnecting from 172.17.0.3... done.
Disconnecting from 172.17.0.5... done.
```


### Step 14. Memcached 모니터링
Memcached의 상황을 확인 할수 있습니다.

```
root@arcus:/opt/arcus/scripts# ./arcus.sh memcached listall
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': []}

-----------------------------------------------------------------------------------
serviceCode  status  total  online  offline  created                     modified
-----------------------------------------------------------------------------------
ruo91-cloud  OK          6       6        0  2014-05-22 07:27:21.121711  None

Done.
```

```
root@arcus:/opt/arcus/scripts# ./arcus.sh memcached list ruo91-cloud
Server Roles
        {'zookeeper': ['172.17.0.3', '172.17.0.4', '172.17.0.5'], 'memcached': []}

-----------------------------------------------------------------------------------
serviceCode  status  total  online  offline  created                     modified
-----------------------------------------------------------------------------------
ruo91-cloud  OK          6       6        0  2014-05-22 07:27:21.121711  None

Online
        172.17.0.5:11211
        172.17.0.5:11212
        172.17.0.4:11211
        172.17.0.4:11212
        172.17.0.3:11212
        172.17.0.3:11211

Done.
```
