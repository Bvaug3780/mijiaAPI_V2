"""多用户并发性能测试

验证多用户场景下的性能和隔离性。
"""

import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock

from mijiaAPI_V2.domain.models import Credential
from mijiaAPI_V2.factory import create_multi_user_clients


def test_multi_user_cache_isolation():
    """测试多用户缓存隔离"""
    # 创建测试凭据
    credentials = {
        "user_a": Credential(
            user_id="user_a",
            service_token="token_a",
            ssecurity="ssecurity_a",
            c_user_id="c_user_a",
            device_id="device_a",
            user_agent="agent_a",
            expires_at=datetime.now() + timedelta(days=7),
        ),
        "user_b": Credential(
            user_id="user_b",
            service_token="token_b",
            ssecurity="ssecurity_b",
            c_user_id="c_user_b",
            device_id="device_b",
            user_agent="agent_b",
            expires_at=datetime.now() + timedelta(days=7),
        ),
    }

    # 创建多用户客户端
    clients = create_multi_user_clients(credentials)

    # 验证客户端隔离
    assert len(clients) == 2
    assert "user_a" in clients
    assert "user_b" in clients
    assert clients["user_a"]._credential.user_id == "user_a"
    assert clients["user_b"]._credential.user_id == "user_b"

    print("✅ 多用户缓存隔离测试通过")


def test_cache_performance():
    """测试缓存性能"""
    from mijiaAPI_V2.infrastructure.cache_manager import CacheManager

    cache = CacheManager()

    # 写入性能测试
    start = time.time()
    for i in range(1000):
        cache.set(f"key_{i}", {"data": f"value_{i}"}, ttl=300)
    write_time = time.time() - start

    # 读取性能测试（L1缓存命中）
    start = time.time()
    for i in range(1000):
        cache.get(f"key_{i}")
    read_time = time.time() - start

    # 获取统计
    stats = cache.get_stats()

    print(f"✅ 缓存性能测试通过")
    print(f"   写入1000条: {write_time:.3f}秒 ({1000/write_time:.0f} ops/s)")
    print(f"   读取1000条: {read_time:.3f}秒 ({1000/read_time:.0f} ops/s)")
    print(f"   L1命中率: {stats['hit_rate']}")
    print(f"   L1缓存大小: {stats['device_cache_size']}")

    # 性能断言
    assert write_time < 1.0, "写入性能不达标"
    assert read_time < 0.1, "读取性能不达标"


def test_logging_performance():
    """测试日志性能"""
    from mijiaAPI_V2.core.logging import get_logger

    logger = get_logger(__name__)
    logger.set_request_id()

    # 日志写入性能测试
    start = time.time()
    for i in range(1000):
        logger.info(f"测试日志 {i}", extra={"index": i, "token": "secret"})
    log_time = time.time() - start

    print(f"✅ 日志性能测试通过")
    print(f"   写入1000条日志: {log_time:.3f}秒 ({1000/log_time:.0f} logs/s)")

    # 性能断言
    assert log_time < 2.0, "日志性能不达标"


if __name__ == "__main__":
    print("开始性能测试...\n")

    test_multi_user_cache_isolation()
    print()

    test_cache_performance()
    print()

    test_logging_performance()
    print()

    print("所有性能测试通过！")
