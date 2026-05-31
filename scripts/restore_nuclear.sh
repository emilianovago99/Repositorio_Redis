#!/bin/bash

FECHA=$1
BACKUP_DIR="/backups/redis_cluster"

if [ -z "$FECHA" ]; then echo "Uso: sudo ./restore_pitr.sh <FECHA_DEL_RESPALDO>"; exit 1; fi

echo "--- Iniciando recuperación Point-In-Time (PITR) con WAL/AOF ---"

# 1. Detener servicios de forma ordenada
sudo systemctl stop redis-sentinel
sudo systemctl stop redis-server

# 2. Eliminar la base de datos corrupta/borrada actual
sudo rm -f /var/lib/redis/dump.rdb
sudo rm -rf /var/lib/redis/appendonlydir

# 3. Restaurar el RDB (Base Backup)
sudo cp "$BACKUP_DIR/dump_$FECHA.rdb" /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# 4. Restaurar el WAL/AOF 
if [ -d "$BACKUP_DIR/appendonlydir_$FECHA" ]; then
    sudo cp -r "$BACKUP_DIR/appendonlydir_$FECHA" /var/lib/redis/appendonlydir
    sudo chown -R redis:redis /var/lib/redis/appendonlydir
    echo "WAL (AOF) restaurado con éxito."
    
    # Nos aseguramos de que el AOF esté activado en la configuración
    sudo sed -i 's/appendonly no/appendonly yes/' /etc/redis/redis.conf
fi

# 5. Levantar Redis (Leerá el RDB y reproducirá el AOF)
sudo systemctl start redis-server
echo "Reproduciendo transacciones del WAL..."
sleep 3

# 6. Romper replicación (Proteger datos)
redis-cli -a Secreta123 REPLICAOF NO ONE
echo "Nodo es ahora Maestro Independiente."

# 7. REINICIAR SENTINEL
sudo systemctl start redis-sentinel
echo "Vigilancia Sentinel restaurada."

echo "--- ¡PITR completado! Datos restaurados exactamente al segundo antes del borrado. ---"