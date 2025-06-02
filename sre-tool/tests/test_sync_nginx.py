# tests/test_sync_nginx.py

import pytest
from src.sync_nginx import compare_configs

@pytest.fixture
def config_a():
    return "user www-data;\nworker_processes auto;\n"

@pytest.fixture
def config_b():
    return "user nginx;\nworker_processes auto;\n"

def test_compare_configs_diff(config_a, config_b):
    diff = compare_configs(config_a, config_b, host_a='A', host_b='B')
    assert "-user www-data;" in diff
    assert "+user nginx;" in diff

def test_compare_configs_no_diff():
    c = "user www-data;\nworker_processes auto;\n"
    diff = compare_configs(c, c, host_a='A', host_b='B')
    assert diff == ""
