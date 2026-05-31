#!/bin/bash
# scripts/backup_oci.sh - Respaldo Full y envío a OCI
FECHA=$(date +%Y%m%d_%H%M%S)
RDB_FILE="/var/lib/redis/dump.rdb"
AOF_DIR="/var/lib/redis/appendonlydir"
BACKUP_TAR="/backups/redis_full_$FECHA.tar.gz"

echo "Forzando volcado de memoria (BGSAVE)..."
redis-cli -a Secreta123 BGSAVE
sleep 5

echo "Empaquetando RDB y AOF..."
# El script ahora verifica si la carpeta AOF existe antes de empaquetarla
if [ -d "$AOF_DIR" ]; then
    sudo tar -czvf $BACKUP_TAR $RDB_FILE $AOF_DIR
else
    sudo tar -czvf $BACKUP_TAR $RDB_FILE
    echo "Nota: appendonlydir no existe. Se respaldó solo el archivo RDB."
fi

echo "Subiendo a OCI Object Storage..."
/root/bin/oci os object put --bucket-name mecanimales-backups --file $BACKUP_TAR --auth instance_principal
echo "Respaldo subido a la nube correctamente."