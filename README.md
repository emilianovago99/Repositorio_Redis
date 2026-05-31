# Proyecto Final: Clúster Redis de Alta Disponibilidad - Equipo Mecanimales

## Descripción

Arquitectura distribuida y resiliente desplegada en Oracle Cloud Infrastructure (OCI). El sistema garantiza la continuidad del negocio mediante failover automático y recuperación ante desastres (PITR).

## Arquitectura

- **Clúster:** 3 nodos (1 Maestro, 2 Esclavos) con replicación asíncrona.
- **Failover:** Redis Sentinel para monitoreo y elección automática de líder.
- **Balanceo:** HAProxy en el puerto 3306 con _health checks_ TCP.
- **Monitoreo:** Stack Prometheus + Grafana.

## Componentes

- `scripts/`: Automatización del ciclo de vida del clúster.
- `web_app/`: Interfaz para demostración en vivo (RTO y PITR).
- `config/`: Configuraciones de HAProxy y Prometheus.

## Instalación

1. Clonar el repositorio.
2. Ejecutar `scripts/install_cluster.sh` en cada nodo.
3. Configurar HAProxy en el nodo maestro.
4. Levantar la suite de monitoreo:
   ```bash
   sudo docker compose up -d
   ```
