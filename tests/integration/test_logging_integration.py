"""日志系统集成测试"""

import json
import logging
from io import StringIO

import pytest

from mijiaAPI_V2.core.logging import get_logger


class TestLoggingIntegration:
    """日志系统集成测试"""

    @pytest.fixture
    def capture_logs(self):
        """捕获日志输出的fixture"""
        # 创建一个StringIO对象来捕获日志
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        # 获取根日志记录器并添加handler
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)
        
        yield log_stream
        
        # 清理
        root_logger.removeHandler(handler)

    def test_complete_logging_workflow(self, capture_logs):
        """测试完整的日志记录工作流"""
        logger = get_logger("test_module")
        logger.set_request_id("integration-test-001")
        
        # 记录不同级别的日志
        logger.debug("调试信息", {"step": 1})
        logger.info("处理请求", {"user_id": "123"})
        logger.warning("性能警告", {"response_time": 500})
        logger.error("处理失败", {"error": "timeout"})
        
        # 获取日志输出
        log_output = capture_logs.getvalue()
        lines = [line for line in log_output.strip().split("\n") if line]
        
        # 验证所有日志都被记录
        assert len(lines) == 4
        
        # 验证每条日志都是有效的JSON
        for line in lines:
            data = json.loads(line)
            assert "timestamp" in data
            assert "message" in data
            assert "request_id" in data
            assert data["request_id"] == "integration-test-001"

    def test_sensitive_data_sanitization_in_real_scenario(self, capture_logs):
        """测试真实场景中的敏感数据脱敏"""
        logger = get_logger("auth_module")
        logger.set_request_id("auth-001")
        
        # 模拟认证场景的日志
        logger.info(
            "用户认证",
            {
                "user_id": "user123",
                "username": "testuser",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "service_token": "service_secret_token",
                "password": "user_password_123",
                "ssecurity": "security_key_abc",
                "device_id": "device_001",
            },
        )
        
        log_output = capture_logs.getvalue()
        
        # 验证敏感信息被脱敏
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in log_output
        assert "service_secret_token" not in log_output
        assert "user_password_123" not in log_output
        assert "security_key_abc" not in log_output
        
        # 验证非敏感信息保留
        assert "user123" in log_output
        assert "testuser" in log_output
        assert "device_001" in log_output
        
        # 验证脱敏标记存在
        assert '"***"' in log_output

    def test_multiple_loggers_with_different_request_ids(self, capture_logs):
        """测试多个日志记录器使用不同的请求ID"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        logger1.set_request_id("req-001")
        logger2.set_request_id("req-002")
        
        logger1.info("来自模块1的消息")
        logger2.info("来自模块2的消息")
        
        log_output = capture_logs.getvalue()
        lines = [line for line in log_output.strip().split("\n") if line]
        
        # 解析日志
        log1 = json.loads(lines[0])
        log2 = json.loads(lines[1])
        
        # 验证请求ID正确隔离
        assert log1["request_id"] == "req-001"
        assert log2["request_id"] == "req-002"

    def test_exception_logging_with_traceback(self, capture_logs):
        """测试异常日志包含堆栈跟踪"""
        logger = get_logger("error_module")
        logger.set_request_id("error-001")
        
        try:
            # 触发异常
            raise ValueError("测试异常")
        except ValueError as e:
            logger.error("捕获异常", {"context": "测试"}, exc_info=e)
        
        log_output = capture_logs.getvalue()
        
        # 验证日志包含异常信息
        assert "测试异常" in log_output
        assert "ValueError" in log_output
        assert "Traceback" in log_output

    def test_chinese_characters_preserved(self, capture_logs):
        """测试中文字符在日志中正确保留"""
        logger = get_logger("chinese_module")
        logger.set_request_id("中文-001")
        
        logger.info(
            "设备控制成功",
            {
                "设备名称": "客厅灯",
                "操作": "开灯",
                "状态": "成功",
            },
        )
        
        log_output = capture_logs.getvalue()
        
        # 验证中文字符未被转义
        assert "设备控制成功" in log_output
        assert "客厅灯" in log_output
        assert "开灯" in log_output
        
        # 验证可以正确解析
        lines = [line for line in log_output.strip().split("\n") if line]
        data = json.loads(lines[0])
        assert data["message"] == "设备控制成功"
        assert data["设备名称"] == "客厅灯"

    def test_auto_generated_request_id_uniqueness(self, capture_logs):
        """测试自动生成的请求ID唯一性"""
        logger = get_logger("unique_module")
        
        request_ids = set()
        
        # 生成多个请求ID
        for i in range(10):
            logger.set_request_id()  # 自动生成
            logger.info(f"消息 {i}")
            
            log_output = capture_logs.getvalue()
            lines = [line for line in log_output.strip().split("\n") if line]
            data = json.loads(lines[-1])
            request_ids.add(data["request_id"])
        
        # 验证所有请求ID都是唯一的
        assert len(request_ids) == 10

    def test_logging_without_extra_data(self, capture_logs):
        """测试不带额外数据的日志记录"""
        logger = get_logger("simple_module")
        logger.set_request_id("simple-001")
        
        logger.info("简单消息")
        
        log_output = capture_logs.getvalue()
        lines = [line for line in log_output.strip().split("\n") if line]
        data = json.loads(lines[0])
        
        # 验证基本字段存在
        assert data["message"] == "简单消息"
        assert data["request_id"] == "simple-001"
        assert "timestamp" in data
        
        # 验证没有额外字段（除了基本字段）
        expected_keys = {"timestamp", "message", "request_id"}
        assert set(data.keys()) == expected_keys
