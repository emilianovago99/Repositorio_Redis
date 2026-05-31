#!/bin/bash
# scripts/audit_rotate.sh - Ejecución Diaria
LOG_FILE="/var/log/redis/redis-server.log"
AUDIT_ARCHIVE="/backups/auditoria_$(date +%Y%m%d).log.gz"
BUCKET_NAME="mecanimales-audit-bucket"

echo "Empaquetando logs de auditoría..."
sudo gzip -c $LOG_FILE > $AUDIT_ARCHIVE

echo "Enviando log de auditoría a OCI Object Storage..."
/root/bin/oci os object put --bucket-name $BUCKET_NAME --file $AUDIT_ARCHIVE --name "auditoria/$(basename $AUDIT_ARCHIVE)" --auth instance_principal
echo "Subida completada a oci://$BUCKET_NAME/auditoria/"

# Vaciar log actual para liberar espacio
sudo truncate -s 0 $LOG_FILE
echo "Rotación completada."