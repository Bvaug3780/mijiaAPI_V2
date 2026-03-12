"""ConfigManager单元测试"""

import os
from pathlib import Path
from typing import Any

import pytest

from mijiaAPI_V2.core.config import ConfigManager


class TestConfigManager:
    """ConfigManager测试类"""

    def test_default_config(self) -> None:
        """测试默认配置加载"""
        config = ConfigManager()

        # 验证API相关配置
        assert config.get("API_BASE_URL") == "https://api.mijia.tech/app"
        assert config.get("LOGIN_URL") == "https://account.xiaomi.com"
        assert (
            config.get("SERVICE_LOGIN_URL")
            == "https://account.xiaomi.com/pass/serviceLogin"
        )
        assert (
            config.get("DEVICE_SPEC_URL") == "https://miot-spec.org/miot-spec-v2/instance"
        )

        # 验证网络相关配置
        assert config.get("DEFAULT_TIMEOUT") == 30
        assert config.get("MAX_RETRIES") == 3

        # 验证缓存相关配置
        assert config.get("CACHE_TTL") == 300

        # 验证日志相关配置
        assert config.get("LOG_LEVEL") == "INFO"

        # 验证Redis相关配置
        assert config.get("REDIS_ENABLED") is False
        assert config.get("REDIS_HOST") == "localhost"
        assert config.get("REDIS_PORT") == 6379
        assert config.get("REDIS_DB") == 0
        assert config.get("REDIS_PASSWORD") is None
        assert config.get("REDIS_TIMEOUT") == 5
        assert config.get("REDIS_CONNECT_TIMEOUT") == 5

    def test_get_with_default(self) -> None:
        """测试get方法的默认值参数"""
        config = ConfigManager()

        # 不存在的键应该返回默认值
        assert config.get("NON_EXISTENT_KEY", "default") == "default"
        assert config.get("NON_EXISTENT_KEY") is None

        # 存在的键应该返回实际值，忽略默认值
        assert config.get("DEFAULT_TIMEOUT", 999) == 30

    def test_set_config(self) -> None:
        """测试set方法"""
        config = ConfigManager()

        # 设置已存在的配置项
        config.set("DEFAULT_TIMEOUT", 60)
        assert config.get("DEFAULT_TIMEOUT") == 60

        # 设置新的配置项
        config.set("CUSTOM_KEY", "custom_value")
        assert config.get("CUSTOM_KEY") == "custom_value"

        # 设置不同类型的值
        config.set("INT_VALUE", 123)
        config.set("BOOL_VALUE", True)
        config.set("LIST_VALUE", [1, 2, 3])
        config.set("DICT_VALUE", {"key": "value"})

        assert config.get("INT_VALUE") == 123
        assert config.get("BOOL_VALUE") is True
        assert config.get("LIST_VALUE") == [1, 2, 3]
        assert config.get("DICT_VALUE") == {"key": "value"}

    def test_get_all(self) -> None:
        """测试get_all方法"""
        config = ConfigManager()

        all_config = config.get_all()

        # 验证返回的是字典
        assert isinstance(all_config, dict)

        # 验证包含所有默认配置
        assert "API_BASE_URL" in all_config
        assert "DEFAULT_TIMEOUT" in all_config
        assert "REDIS_ENABLED" in all_config

        # 验证返回的是副本（修改不影响原配置）
        all_config["TEST_KEY"] = "test_value"
        assert config.get("TEST_KEY") is None

        # 验证修改副本中的值不影响原配置
        original_timeout = config.get("DEFAULT_TIMEOUT")
        all_config["DEFAULT_TIMEOUT"] = 999
        assert config.get("DEFAULT_TIMEOUT") == original_timeout

    def test_env_override_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试环境变量覆盖字符串类型配置"""
        monkeypatch.setenv("MIJIA_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MIJIA_API_BASE_URL", "https://custom.api.com")

        config = ConfigManager()

        assert config.get("LOG_LEVEL") == "DEBUG"
        assert config.get("API_BASE_URL") == "https://custom.api.com"

    def test_env_override_int(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试环境变量覆盖整数类型配置"""
        monkeypatch.setenv("MIJIA_DEFAULT_TIMEOUT", "120")
        monkeypatch.setenv("MIJIA_MAX_RETRIES", "5")
        monkeypatch.setenv("MIJIA_REDIS_PORT", "6380")

        config = ConfigManager()

        assert config.get("DEFAULT_TIMEOUT") == 120
        assert config.get("MAX_RETRIES") == 5
        assert config.get("REDIS_PORT") == 6380

    def test_env_override_bool(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试环境变量覆盖布尔类型配置"""
        # 测试true值
        monkeypatch.setenv("MIJIA_REDIS_ENABLED", "true")
        config1 = ConfigManager()
        assert config1.get("REDIS_ENABLED") is True

        # 测试1值
        monkeypatch.setenv("MIJIA_REDIS_ENABLED", "1")
        config2 = ConfigManager()
        assert config2.get("REDIS_ENABLED") is True

        # 测试yes值
        monkeypatch.setenv("MIJIA_REDIS_ENABLED", "yes")
        config3 = ConfigManager()
        assert config3.get("REDIS_ENABLED") is True

        # 测试on值
        monkeypatch.setenv("MIJIA_REDIS_ENABLED", "on")
        config4 = ConfigManager()
        assert config4.get("REDIS_ENABLED") is True

        # 测试false值
        monkeypatch.setenv("MIJIA_REDIS_ENABLED", "false")
        config5 = ConfigManager()
        assert config5.get("REDIS_ENABLED") is False

        # 测试0值
        monkeypatch.setenv("MIJIA_REDIS_ENABLED", "0")
        config6 = ConfigManager()
        assert config6.get("REDIS_ENABLED") is False

    def test_env_override_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试环境变量设置为None"""
        monkeypatch.setenv("MIJIA_REDIS_PASSWORD", "none")

        config = ConfigManager()

        assert config.get("REDIS_PASSWORD") is None

    def test_env_override_invalid_int(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试环境变量提供无效的整数值时使用默认值"""
        monkeypatch.setenv("MIJIA_DEFAULT_TIMEOUT", "invalid")

        config = ConfigManager()

        # 应该保持默认值
        assert config.get("DEFAULT_TIMEOUT") == 30

    def test_toml_file_loading(self, tmp_path: Path) -> None:
        """测试从TOML文件加载配置"""
        # 创建临时TOML文件
        toml_content = """
API_BASE_URL = "https://custom.api.com"
DEFAULT_TIMEOUT = 45
MAX_RETRIES = 5
CUSTOM_CONFIG = "from_file"
"""
        toml_path = tmp_path / "test_config.toml"
        toml_path.write_text(toml_content)

        config = ConfigManager(config_path=toml_path)

        # 验证TOML文件中的配置被加载
        assert config.get("API_BASE_URL") == "https://custom.api.com"
        assert config.get("DEFAULT_TIMEOUT") == 45
        assert config.get("MAX_RETRIES") == 5
        assert config.get("CUSTOM_CONFIG") == "from_file"

        # 验证未在TOML文件中指定的配置仍使用默认值
        assert config.get("CACHE_TTL") == 300
        assert config.get("LOG_LEVEL") == "INFO"

    def test_toml_file_not_exists(self) -> None:
        """测试TOML文件不存在时使用默认配置"""
        non_existent_path = Path("/non/existent/path/config.toml")

        config = ConfigManager(config_path=non_existent_path)

        # 应该使用默认配置
        assert config.get("API_BASE_URL") == "https://api.mijia.tech/app"
        assert config.get("DEFAULT_TIMEOUT") == 30

    def test_toml_file_invalid(self, tmp_path: Path, caplog: Any) -> None:
        """测试TOML文件格式无效时的处理"""
        # 创建无效的TOML文件
        invalid_toml = tmp_path / "invalid.toml"
        invalid_toml.write_text("invalid toml content [[[")

        config = ConfigManager(config_path=invalid_toml)

        # 应该记录警告日志
        assert any("加载配置文件失败" in record.message for record in caplog.records)

        # 应该仍然使用默认配置
        assert config.get("API_BASE_URL") == "https://api.mijia.tech/app"

    def test_config_priority(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试配置优先级：环境变量 > TOML文件 > 默认配置"""
        # 创建TOML文件
        toml_content = """
DEFAULT_TIMEOUT = 45
MAX_RETRIES = 5
"""
        toml_path = tmp_path / "config.toml"
        toml_path.write_text(toml_content)

        # 设置环境变量
        monkeypatch.setenv("MIJIA_DEFAULT_TIMEOUT", "120")

        config = ConfigManager(config_path=toml_path)

        # 环境变量应该覆盖TOML文件
        assert config.get("DEFAULT_TIMEOUT") == 120

        # TOML文件应该覆盖默认配置
        assert config.get("MAX_RETRIES") == 5

        # 未指定的配置应该使用默认值
        assert config.get("CACHE_TTL") == 300

    def test_config_isolation(self) -> None:
        """测试多个ConfigManager实例之间的隔离"""
        config1 = ConfigManager()
        config2 = ConfigManager()

        # 修改config1不应该影响config2
        config1.set("DEFAULT_TIMEOUT", 100)
        assert config1.get("DEFAULT_TIMEOUT") == 100
        assert config2.get("DEFAULT_TIMEOUT") == 30

        # 修改config2不应该影响config1
        config2.set("MAX_RETRIES", 10)
        assert config2.get("MAX_RETRIES") == 10
        assert config1.get("MAX_RETRIES") == 3
