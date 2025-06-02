# manual_test.py

from src.sync_nginx import compare_configs

with open('test_host1/nginx.conf') as f1, open('test_host2/nginx.conf') as f2:
    cfg1 = f1.read()
    cfg2 = f2.read()

diff = compare_configs(cfg1, cfg2, host_a='test_host1', host_b='test_host2')
print('--- Diff between test_host1 and test_host2 ---')
print(diff)
if not diff:
    print("Synchronized test_host2 to match test_host1")
