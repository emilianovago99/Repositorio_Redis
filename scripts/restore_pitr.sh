#!/bin/bash

# Uso: sudo ./restore_pitr.sh dump_20260523_230152.rdb

if [ -z "$1" ]; then
    echo "Error: Debes proporcionar el nombre del archivo de respaldo."
    echo "Ejemplo: sudo ./restore_pitr.sh dump_20260523_230152.rdb"
    exit 1
fi

BACKUP_FILE="/backups/redis_cluster/$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: El archivo $BACKUP_FILE no existe."
    exit 1
fi

echo "--- Iniciando Restauración PITR  ---"
sudo systemctl stop redis-sentinel
sudo systemctl stop redis-server

echo "Copiando $1 a /var/lib/redis/..."
sudo cp "$BACKUP_FILE" /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

echo "Levantando Redis..."
sudo systemctl start redis-server

echo "Restauración completada. Esperando 3 segundos para reiniciar Sentinel..."
sleep 3
sudo systemctl start redis-sentinel

echo "--- ¡Listo! Los datos han sido restaurados exitosamente. ---"