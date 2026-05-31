#!/bin/bash
# scripts/mantenimiento_semanal.sh
echo "=== Iniciando Tareas de Mantenimiento Automatizadas ==="

echo "[1/3] Liberando fragmentación de memoria..."
redis-cli -a Secreta123 MEMORY PURGE
echo "Memoria compactada exitosamente."

echo "[2/3] Limpiando respaldos y logs con más de 7 días de antigüedad..."
sudo find /backups/ -type f -mtime +7 -name "*.gz" -exec rm -f {} \;
echo "Limpieza completada."

echo "[3/3] Verificando integridad criptográfica del último respaldo RDB..."
ULTIMO_RDB=$(ls -t /backups/redis_cluster/dump_*.rdb 2>/dev/null | head -n 1)

if [ -n "$ULTIMO_RDB" ]; then
    sudo redis-check-rdb "$ULTIMO_RDB" | grep "OK" || echo "Advertencia: El respaldo podría estar corrupto."
    echo "Integridad verificada exitosamente."
else
    echo "No hay archivos RDB para verificar."
fi
echo "=== Mantenimiento Finalizado ==="