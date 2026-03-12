"""结构化日志系统单元测试"""

import json
import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from mijiaAPI_V2.core.logging import StructuredLogger, get_logger


class TestStructuredLogger:
    """StructuredLogger类的单元测试"""

    def test_init(self):
        """测试初始化"""
        logger = StructuredLogger("test_logger")
        assert logger.logger.name == "test_logger"
        assert logger._request_id is None

    def test_set_request_id_with_custom_id(self):
        """测试设置自定义请求ID"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("custom-request-id")
        assert logger._request_id == "custom-request-id"

    def test_set_request_id_auto_generate(self):
        """测试自动生成请求ID"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id()
        assert logger._request_id is not None
        assert isinstance(logger._request_id, str)
        assert len(logger._request_id) > 0

    def test_format_message_basic(self):
        """测试基本消息格式化"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        formatted = logger._format_message("测试消息")
        data = json.loads(formatted)

        assert data["message"] == "测试消息"
        assert data["request_id"] == "test-id"
        assert "timestamp" in data
        # 验证时间戳格式
        datetime.fromisoformat(data["timestamp"])

    def test_format_message_with_extra(self):
        """测试带额外信息的消息格式化"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        extra = {"user_id": "12345", "action": "login"}
        formatted = logger._format_message("用户登录", extra)
        data = json.loads(formatted)

        assert data["message"] == "用户登录"
        assert data["user_id"] == "12345"
        assert data["action"] == "login"

    def test_sanitize_token(self):
        """测试token脱敏"""
        logger = StructuredLogger("test_logger")

        data = {
            "user_id": "12345",
            "token": "secret-token-value",
            "service_token": "another-secret",
        }

        sanitized = logger._sanitize(data)

        assert sanitized["user_id"] == "12345"
        assert sanitized["token"] == "***"
        assert sanitized["service_token"] == "***"

    def test_sanitize_password(self):
        """测试password脱敏"""
        logger = StructuredLogger("test_logger")

        data = {
            "username": "user123",
            "password": "my-secret-password",
            "user_password": "another-password",
        }

        sanitized = logger._sanitize(data)

        assert sanitized["username"] == "user123"
        assert sanitized["password"] == "***"
        assert sanitized["user_password"] == "***"

    def test_sanitize_ssecurity(self):
        """测试ssecurity脱敏"""
        logger = StructuredLogger("test_logger")

        data = {
            "user_id": "12345",
            "ssecurity": "secret-ssecurity-value",
        }

        sanitized = logger._sanitize(data)

        assert sanitized["user_id"] == "12345"
        assert sanitized["ssecurity"] == "***"

    def test_sanitize_case_insensitive(self):
        """测试脱敏关键字大小写不敏感"""
        logger = StructuredLogger("test_logger")

        data = {
            "Token": "secret1",
            "PASSWORD": "secret2",
            "ServiceToken": "secret3",
        }

        sanitized = logger._sanitize(data)

        assert sanitized["Token"] == "***"
        assert sanitized["PASSWORD"] == "***"
        assert sanitized["ServiceToken"] == "***"

    def test_sanitize_preserves_non_sensitive(self):
        """测试脱敏保留非敏感信息"""
        logger = StructuredLogger("test_logger")

        data = {
            "user_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "token": "secret",
        }

        sanitized = logger._sanitize(data)

        assert sanitized["user_id"] == "12345"
        assert sanitized["username"] == "testuser"
        assert sanitized["email"] == "test@example.com"
        assert sanitized["token"] == "***"

    @patch("mijiaAPI_V2.core.logging.logging.Logger.debug")
    def test_debug_logging(self, mock_debug):
        """测试DEBUG级别日志"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        logger.debug("调试消息", {"key": "value"})

        mock_debug.assert_called_once()
        call_args = mock_debug.call_args[0][0]
        data = json.loads(call_args)

        assert data["message"] == "调试消息"
        assert data["key"] == "value"

    @patch("mijiaAPI_V2.core.logging.logging.Logger.info")
    def test_info_logging(self, mock_info):
        """测试INFO级别日志"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        logger.info("信息消息", {"user_id": "123"})

        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        data = json.loads(call_args)

        assert data["message"] == "信息消息"
        assert data["user_id"] == "123"

    @patch("mijiaAPI_V2.core.logging.logging.Logger.warning")
    def test_warning_logging(self, mock_warning):
        """测试WARNING级别日志"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        logger.warning("警告消息")

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        data = json.loads(call_args)

        assert data["message"] == "警告消息"

    @patch("mijiaAPI_V2.core.logging.logging.Logger.error")
    def test_error_logging(self, mock_error):
        """测试ERROR级别日志"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        logger.error("错误消息", {"error_code": "E001"})

        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        data = json.loads(call_args)

        assert data["message"] == "错误消息"
        assert data["error_code"] == "E001"

    @patch("mijiaAPI_V2.core.logging.logging.Logger.error")
    def test_error_logging_with_exc_info(self, mock_error):
        """测试带异常信息的ERROR日志"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        try:
            raise ValueError("测试异常")
        except ValueError as e:
            logger.error("捕获异常", exc_info=e)

        mock_error.assert_called_once()
        # 验证exc_info参数被传递
        assert mock_error.call_args[1]["exc_info"] is not None

    @patch("mijiaAPI_V2.core.logging.logging.Logger.critical")
    def test_critical_logging(self, mock_critical):
        """测试CRITICAL级别日志"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        logger.critical("严重错误", {"system": "auth"})

        mock_critical.assert_called_once()
        call_args = mock_critical.call_args[0][0]
        data = json.loads(call_args)

        assert data["message"] == "严重错误"
        assert data["system"] == "auth"

    def test_json_output_format(self):
        """测试JSON输出格式正确"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        formatted = logger._format_message("测试", {"key": "值"})

        # 验证是有效的JSON
        data = json.loads(formatted)
        assert isinstance(data, dict)

        # 验证必需字段
        assert "timestamp" in data
        assert "message" in data
        assert "request_id" in data

    def test_chinese_characters_in_json(self):
        """测试JSON中的中文字符正确处理"""
        logger = StructuredLogger("test_logger")
        logger.set_request_id("test-id")

        formatted = logger._format_message("中文消息", {"名称": "测试用户"})

        # 验证中文字符未被转义
        assert "中文消息" in formatted
        assert "测试用户" in formatted

        # 验证可以正确解析
        data = json.loads(formatted)
        assert data["message"] == "中文消息"
        assert data["名称"] == "测试用户"

    def test_logging_without_request_id(self):
        """测试未设置请求ID时的日志记录"""
        logger = StructuredLogger("test_logger")

        formatted = logger._format_message("测试消息")
        data = json.loads(formatted)

        assert data["message"] == "测试消息"
        assert data["request_id"] is None

    def test_multiple_sensitive_fields(self):
        """测试多个敏感字段同时脱敏"""
        logger = StructuredLogger("test_logger")

        data = {
            "user_id": "123",
            "token": "secret1",
            "password": "secret2",
            "ssecurity": "secret3",
            "service_token": "secret4",
            "normal_field": "visible",
        }

        sanitized = logger._sanitize(data)

        assert sanitized["user_id"] == "123"
        assert sanitized["token"] == "***"
        assert sanitized["password"] == "***"
        assert sanitized["ssecurity"] == "***"
        assert sanitized["service_token"] == "***"
        assert sanitized["normal_field"] == "visible"


class TestGetLogger:
    """get_logger工厂函数的单元测试"""

    def test_get_logger_returns_structured_logger(self):
        """测试get_logger返回StructuredLogger实例"""
        logger = get_logger("test_module")
        assert isinstance(logger, StructuredLogger)

    def test_get_logger_with_module_name(self):
        """测试使用模块名创建logger"""
        logger = get_logger(__name__)
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == __name__

    def test_get_logger_creates_different_instances(self):
        """测试每次调用创建不同的实例"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.logger.name == "module1"
        assert logger2.logger.name == "module2"
