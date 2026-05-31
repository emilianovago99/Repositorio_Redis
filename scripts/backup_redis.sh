#!/bin/bash
BACKUP_DIR="/backups/redis_cluster"
FECHA=$(date +%Y%m%d_%H%M%S)

sudo mkdir -p $BACKUP_DIR

# Intentar hacer BGSAVE
if redis-cli -a Secreta123 BGSAVE; then
    echo "Respaldo iniciado..."
    sleep 5
else
    echo "Error: No se pudo conectar a Redis. Asegúrate de que el servicio esté corriendo."
    exit 1
fi

# Copiar RDB
sudo cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump_$FECHA.rdb

# Copiar AOF solo si existe la carpeta
if [ -d "/var/lib/redis/appendonlydir" ]; then
    sudo cp -r /var/lib/redis/appendonlydir $BACKUP_DIR/appendonlydir_$FECHA
    echo "Respaldo AOF copiado exitosamente."
else
    echo "Aviso: Carpeta appendonlydir no encontrada, omitiendo AOF en este respaldo."
fi

echo "Respaldo completado en $BACKUP_DIR"