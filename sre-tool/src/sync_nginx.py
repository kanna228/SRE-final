#!/usr/bin/env python3
# src/sync_nginx.py

import paramiko
import difflib
import argparse
import sys

def fetch_nginx_config(host, username, password=None, key_filename=None):
    """
    Подключается по SSH к host, возвращает содержимое /etc/nginx/nginx.conf или None.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if key_filename:
            client.connect(hostname=host, username=username, key_filename=key_filename, timeout=10)
        else:
            client.connect(hostname=host, username=username, password=password, timeout=10)
    except Exception as e:
        print(f"Failed to connect to {host}: {e}", file=sys.stderr)
        return None

    try:
        sftp = client.open_sftp()
        with sftp.open('/etc/nginx/nginx.conf', 'r') as f:
            content = f.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch /etc/nginx/nginx.conf from {host}: {e}", file=sys.stderr)
        content = None
    finally:
        try:
            sftp.close()
        except:
            pass
        client.close()

    return content

def compare_configs(config_a, config_b, host_a='hostA', host_b='hostB'):
    """
    Возвращает unified diff между двумя строками-конфигами.
    """
    lines_a = config_a.splitlines(keepends=True)
    lines_b = config_b.splitlines(keepends=True)
    diff_lines = difflib.unified_diff(lines_a, lines_b,
                                      fromfile=host_a, tofile=host_b, lineterm='')
    return ''.join(diff_lines)

def sync_config_to_host(host, username, content, password=None, key_filename=None):
    """
    Записывает content в /etc/nginx/nginx.conf на host, используя SSH SFTP.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if key_filename:
            client.connect(hostname=host, username=username, key_filename=key_filename, timeout=10)
        else:
            client.connect(hostname=host, username=username, password=password, timeout=10)
    except Exception as e:
        print(f"Failed to connect to {host} for sync: {e}", file=sys.stderr)
        return False

    try:
        sftp = client.open_sftp()
        # Пишем файл поверх старого
        with sftp.open('/etc/nginx/nginx.conf', 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"Failed to write /etc/nginx/nginx.conf to {host}: {e}", file=sys.stderr)
        return False
    finally:
        try:
            sftp.close()
        except:
            pass
        client.close()

    return True

def main():
    parser = argparse.ArgumentParser(description='Sync or diff nginx.conf across servers')
    parser.add_argument('--servers', required=True,
                        help='Path to file with newline-separated server hostnames or IPs')
    parser.add_argument('--user', required=True, help='SSH username')
    parser.add_argument('--key', help='Path to private SSH key (optional)')
    parser.add_argument('--password', help='SSH password (optional)')
    parser.add_argument('--sync', action='store_true',
                        help='If set, synchronize differences to all other servers')
    args = parser.parse_args()

    # Читаем список серверов
    try:
        with open(args.servers, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Failed to read servers file: {e}", file=sys.stderr)
        sys.exit(1)

    if len(hosts) < 2:
        print("Need at least two servers to compare or sync.", file=sys.stderr)
        sys.exit(1)

    # Получаем конфиг первого (эталонного) сервера
    base_host = hosts[0]
    base_config = fetch_nginx_config(base_host, args.user, args.password, args.key)
    if base_config is None:
        sys.exit(1)

    # Идём по остальным и сравниваем
    for host in hosts[1:]:
        config = fetch_nginx_config(host, args.user, args.password, args.key)
        if config is None:
            continue

        diff = compare_configs(base_config, config, host_a=base_host, host_b=host)
        if diff:
            print(f"--- Differences between {base_host} and {host} ---")
            print(diff)
            if args.sync:
                success = sync_config_to_host(host, args.user, base_config, args.password, args.key)
                if success:
                    print(f"Synchronized {host} to match {base_host}")
                else:
                    print(f"Failed to synchronize {host}", file=sys.stderr)
        else:
            print(f"No differences found between {base_host} and {host}")

if __name__ == '__main__':
    main()
