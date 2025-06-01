#!/bin/bash
set -e

# 1) Разрешаем репликацию: в pg_hba.conf добавляем правило для всех хостов
echo "host replication all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"

# 2) Включаем уровень WAL для репликации
echo "wal_level = replica" >> "$PGDATA/postgresql.conf"
echo "max_wal_senders = 10" >> "$PGDATA/postgresql.conf"
echo "wal_keep_segments = 64" >> "$PGDATA/postgresql.conf"

# 3) Заставляем Postgres слушать на всех интерфейсах
echo "listen_addresses = '*'" >> "$PGDATA/postgresql.conf"
