# Comandos, Consultas y Operaciones Críticas - Equipo B

Este documento contiene la recopilación de los comandos de base de datos, consultas de monitoreo (PromQL) y operaciones de sistema utilizados para la administración, auditoría y pruebas del clúster Redis en OCI.

## 1. Comandos de Base de Datos (Equivalentes a SQL)

Estos comandos fueron utilizados tanto en la aplicación web de Python como en la terminal para interactuar con los datos.

- **Insertar/Actualizar datos (Equivalente a INSERT/UPDATE):**
  `SET tabla_importante "Datos Críticos del Proyecto (Protegidos)"`
- **Leer datos (Equivalente a SELECT):**
  `GET tabla_importante`
- **Borrar datos (Equivalente a DELETE):**
  `DEL tabla_importante`
- **Incrementar contadores para latidos (Heartbeat de la App Web):**
  `INCRBY equipo_b_ha_counter 1`

## 2. Comandos de Auditoría y Mantenimiento

- **Auditoría en Tiempo Real (Requisito de la Rúbrica):**
  Muestra todas las transacciones, IPs y timestamps en vivo.
  `redis-cli -a Secreta123 MONITOR`
- **Volcado de Memoria a Disco (Full Backup RDB):**
  `redis-cli -a Secreta123 BGSAVE`
- **Defragmentación de Memoria (Equivalente a Reindexación):**
  `redis-cli -a Secreta123 MEMORY PURGE`
- **Verificación de Integridad de Respaldos:**
  `sudo redis-check-rdb /backups/redis_cluster/dump_archivo.rdb`

## 3. Consultas PromQL (Métricas de Grafana)

Las siguientes consultas fueron configuradas en los dashboards de Grafana para extraer la información de Prometheus:

- **TPS (Transacciones por Segundo):**
  `rate(redis_commands_processed_total[1m])`
- **Conexiones Activas:**
  `redis_connected_clients`
- **Lag de Replicación (Retraso en segundos):**
  `redis_master_last_io_seconds_ago`
- **Uso de Memoria RAM:**
  `redis_memory_used_bytes`
- **Consultas Lentas (Slow Queries):**
  `redis_slowlog_length`

### 3.1 Reglas de Alertas

- **Alerta de Nodo Caído (Disparo inmediato):**
  `up{job="redis_cluster"} < 1`
- **Alerta de Memoria Crítica (> 500 MB):**
  `redis_memory_used_bytes > 524288000`

## 4. Comandos de Alta Disponibilidad (Failover y Sentinel)

- **Simular Caída del Nodo Maestro (Prueba RTO):**
  `sudo systemctl stop redis-server`
- **Verificar estado del Quórum y Maestro actual:**
  `redis-cli -p 26379 sentinel master mymaster`
- **Forzar Failover Manual (Promover Esclavo a Maestro):**
  `redis-cli -p 26379 sentinel failover mymaster`
- **Romper Replicación (Usado para proteger datos durante el PITR):**
  `redis-cli -a Secreta123 REPLICAOF NO ONE`

## 5. Operaciones en Oracle Cloud (OCI CLI)

Comandos utilizados para interactuar con los Buckets de Object Storage sin credenciales estáticas (usando Instance Principals).

- **Subir respaldo a la nube:**
  `/root/bin/oci os object put --bucket-name mecanimales-backups --file archivo.tar.gz --auth instance_principal`
- **Listar archivos en el Bucket (Verificación):**
  `/root/bin/oci os object list --bucket-name mecanimales-backups --auth instance_principal`
- **Automatización (Crontab):**
  ```bash
  # Mantenimiento Semanal (Domingos a las 3:00 AM)
  0 3 * * 0 /home/ubuntu/scripts/mantenimiento_semanal.sh >> /var/log/mantenimiento.log 2>&1
  # Respaldos a OCI (Diario a las 2:00 AM)
  0 2 * * * /home/ubuntu/scripts/backup_oci.sh >> /var/log/backups.log 2>&1
  # Rotación de Auditoría (Diario a las 23:55)
  55 23 * * * /home/ubuntu/scripts/audit_rotate.sh >> /var/log/auditoria.log 2>&1
  ```
