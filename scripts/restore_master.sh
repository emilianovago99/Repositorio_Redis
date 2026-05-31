#!/bin/bash
# Uso: sudo ./restore_master.sh <nombre_del_archivo.rdb>

FILE=$1
BACKUP_DIR="/backups/redis_cluster"

if [ -z "$FILE" ]; then 
    echo "Uso: sudo ./restore_master.sh <archivo.rdb>"
    exit 1 
fi

if [ ! -f "$BACKUP_DIR/$FILE" ]; then
    echo "Error: Archivo no encontrado en $BACKUP_DIR"
    exit 1
fi

echo "--- Iniciando recuperación segura en Maestro  ---"

# 1. Detener servicios para evitar inconsistencias
sudo systemctl stop redis-sentinel
sudo systemctl stop redis-server

# 2. Eliminar/Mover AOF para que no repita el comando DEL borrado
if [ -d "/var/lib/redis/appendonlydir" ]; then
    sudo mv /var/lib/redis/appendonlydir /var/lib/redis/appendonlydir.borrar
    echo "AOF movido a appendonlydir.borrar (limpiando registros previos)..."
fi

# 3. Restaurar RDB
sudo cp "$BACKUP_DIR/$FILE" /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# 4. Levantar Redis
sudo systemctl start redis-server

# 5. PASO CRÍTICO: Forzar modo Maestro Independiente
# Esto evita que el nodo intente sincronizarse con otros nodos y se vacíe
sleep 2
redis-cli -a Secreta123 REPLICAOF NO ONE
echo "Nodo forzado a Maestro Independiente."

# 6. Reiniciar Sentinel
sudo systemctl start redis-sentinel

echo "--- ¡Restauración completa! Los datos están protegidos. ---"