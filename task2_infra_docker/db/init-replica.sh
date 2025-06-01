#!/bin/bash
set -e

# 1) Ждём, пока мастер будет готов (pg_isready вернёт OK)
until pg_isready -h "$REPLICA_HOST" -U "$POSTGRES_USER"; do
  echo "Waiting for master..."
  sleep 2
done

# 2) Очищаем локальный каталог данных реплики
rm -rf /var/lib/postgresql/data/*

# 3) Делаем базовый backup с мастера
PGPASSWORD="$REPLICA_PASSWORD" \
  pg_basebackup -h "$REPLICA_HOST" -D /var/lib/postgresql/data -U "$POSTGRES_USER" -vP --wal-method=stream

# 4) Создаём recovery.conf, чтобы запустить сервис в режиме Standby
cat > /var/lib/postgresql/data/recovery.conf <<EOF
standby_mode = 'on'
primary_conninfo = 'host=$REPLICA_HOST port=5432 user=$POSTGRES_USER password=$REPLICA_PASSWORD'
trigger_file = '/tmp/postgresql.trigger.5432'
EOF

# 5) Меняем владельца каталога данных на postgres (требование безопасности)
chown -R postgres:postgres /var/lib/postgresql/data
