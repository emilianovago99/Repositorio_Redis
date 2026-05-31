#!/bin/bash

sudo apt update -y
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y

sudo DEBIAN_FRONTEND=noninteractive apt install redis-server redis-sentinel iptables-persistent -y

sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
sudo sed -i 's/bind 127.0.0.1 -::1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo sed -i 's/protected-mode yes/protected-mode no/' /etc/redis/redis.conf
sudo sed -i 's/appendonly no/appendonly yes/' /etc/redis/redis.conf

sudo sed -i 's/# requirepass foobared/requirepass Secreta123/' /etc/redis/redis.conf
sudo sed -i 's/# masterauth <master-password>/masterauth Secreta123/' /etc/redis/redis.conf

sudo iptables -I INPUT 1 -p tcp -m multiport --dports 6379,26379,9121,3306 -j ACCEPT
sudo netfilter-persistent save

read -p "Ingresa el número de tu opción (1 o 2): " ROL

if [ "$ROL" == "2" ]; then
    read -p "Ingresa la IP privada del Nodo Maestro: " IP_MAESTRO
    echo "replicaof $IP_MAESTRO 6379" | sudo tee -a /etc/redis/redis.conf > /dev/null
else
    IP_MAESTRO="127.0.0.1" 
fi

sudo cp /etc/redis/sentinel.conf /etc/redis/sentinel.conf.backup

if [ "$ROL" == "1" ]; then
     read -p "Ingresa la IP privada de ESTE Nodo Maestro: " IP_MAESTRO_REAL
     IP_MAESTRO=$IP_MAESTRO_REAL
fi

sudo tee /etc/redis/sentinel.conf > /dev/null <<EOF
port 26379
daemonize yes
pidfile "/var/run/redis/redis-sentinel.pid"
logfile "/var/log/redis/redis-sentinel.log"
dir "/var/lib/redis"
sentinel monitor mymaster $IP_MAESTRO 6379 2
sentinel auth-pass mymaster Secreta123
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
EOF
sudo chown redis:redis /etc/redis/sentinel.conf

sudo systemctl enable redis-server
sudo systemctl enable redis-sentinel
sudo systemctl restart redis-server
sudo systemctl restart redis-sentinel

sleep 2

echo -e '#!/bin/bash\nredis-cli -a Secreta123 "$@"' | sudo tee /usr/local/bin/redis-admin > /dev/null
sudo chmod +x /usr/local/bin/redis-admin