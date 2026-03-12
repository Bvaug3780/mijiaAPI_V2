"""HttpClient单元测试"""

import base64
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from mijiaAPI_V2.core.config import ConfigManager
from mijiaAPI_V2.domain.exceptions import (
    ConnectionError,
    DeviceNotFoundError,
    MijiaAPIException,
    NetworkError,
    TimeoutError,
    TokenExpiredError,
)
from mijiaAPI_V2.domain.models import Credential
from mijiaAPI_V2.infrastructure.crypto_service import CryptoService
from mijiaAPI_V2.infrastructure.http_client import HttpClient


@pytest.fixture
def config():
    """创建配置管理器"""
    return ConfigManager()


@pytest.fixture
def crypto():
    """创建加密服务"""
    return CryptoService()


@pytest.fixture
def credential():
    """创建测试凭据"""
    return Credential(
        user_id="test_user_123",
        service_token="test_token",
        ssecurity="dGVzdF9zc2VjdXJpdHk=",  # base64编码的"test_ssecurity"
        c_user_id="test_c_user_id",
        device_id="test_device_id",
        user_agent="MiHome/1.0.0",
        expires_at=datetime.now() + timedelta(days=7),
    )


@pytest.fixture
def http_client(config, crypto):
    """创建HTTP客户端"""
    return HttpClient(config, crypto)


def create_mock_response(status_code: int, text: str) -> Mock:
    """创建mock响应对象
    
    Args:
        status_code: HTTP状态码
        text: 响应文本
        
    Returns:
        配置好的Mock响应对象
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.headers = {}
    mock_response.content = text.encode()
    mock_response.text = text
    return mock_response


class TestHttpClientInit:
    """测试HttpClient初始化"""

    def test_init_with_default_config(self, config, crypto):
        """测试使用默认配置初始化"""
        client = HttpClient(config, crypto)

        assert client._config == config
        assert client._crypto == crypto
        assert isinstance(client._client, httpx.Client)

    def test_init_creates_connection_pool(self, config, crypto):
        """测试初始化时创建连接池"""
        client = HttpClient(config, crypto)

        # 验证连接池配置
        # httpx.Client的limits是通过_pool_manager访问的
        assert client._client._transport is not None


class TestHttpClientPost:
    """测试HttpClient.post方法"""

    def test_post_success(self, http_client, credential):
        """测试POST请求成功"""
        # Mock httpx.Client.post
        response_text = base64.b64encode(b'{"code": 0, "result": {"data": "test"}}').decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0, "result": {"data": "test"}}'
                ):
                    result = http_client.post("/test/path", {"key": "value"}, credential)

        assert result == {"code": 0, "result": {"data": "test"}}

    def test_post_builds_correct_url(self, http_client, credential):
        """测试POST请求构建正确的URL"""
        response_text = base64.b64encode(b'{"code": 0}').decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response) as mock_post:
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0}'
                ):
                    http_client.post("/test/path", {}, credential)

                    # 验证URL（使用配置中的 API_BASE_URL）
                    call_args = mock_post.call_args
                    assert call_args[0][0] == "https://api.mijia.tech/app/test/path"

    def test_post_includes_correct_headers(self, http_client, credential):
        """测试POST请求包含正确的请求头"""
        response_text = base64.b64encode(b'{"code": 0}').decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response) as mock_post:
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0}'
                ):
                    http_client.post("/test/path", {}, credential)

                    # 验证请求头
                    call_kwargs = mock_post.call_args[1]
                    headers = call_kwargs["headers"]
                    assert headers["User-Agent"] == credential.user_agent
                    assert headers["x-xiaomi-protocal-flag-cli"] == "PROTOCAL-HTTP2"

    def test_post_encrypts_data(self, http_client, credential):
        """测试POST请求加密数据"""
        response_text = base64.b64encode(b'{"code": 0}').decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response) as mock_post:
            with patch.object(
                http_client._crypto, "encrypt_params", 
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ) as mock_encrypt:
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0}'
                ):
                    http_client.post("/test/path", {"key": "value"}, credential)

                    # 验证加密被调用
                    mock_encrypt.assert_called_once_with("/test/path", {"key": "value"}, credential.ssecurity)

                    # 验证加密后的数据被发送
                    call_kwargs = mock_post.call_args[1]
                    assert call_kwargs["data"] == {"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}

    def test_post_logs_request(self, http_client, credential):
        """测试POST请求记录日志"""
        response_text = base64.b64encode(b'{"code": 0}').decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0}'
                ):
                    with patch("mijiaAPI_V2.infrastructure.http_client.logger") as mock_logger:
                        http_client.post("/test/path", {}, credential)

                        # 验证日志被记录
                        assert mock_logger.info.call_count >= 2  # 请求开始和成功各一次
                        assert mock_logger.set_request_id.called


class TestHttpClientErrorHandling:
    """测试HttpClient错误处理"""

    def test_handle_token_expired_error(self, http_client, credential):
        """测试处理Token过期错误（code=401）"""
        response_text = base64.b64encode('{"code": 401, "message": "Token已过期"}'.encode()).decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 401, "message": "Token已过期"}'
                ):
                    with pytest.raises(TokenExpiredError) as exc_info:
                        http_client.post("/test/path", {}, credential)

                    assert "Token已过期" in str(exc_info.value)

    def test_handle_device_not_found_error(self, http_client, credential):
        """测试处理设备不存在错误（code=404）"""
        response_text = base64.b64encode('{"code": 404, "message": "设备不存在"}'.encode()).decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 404, "message": "设备不存在"}'
                ):
                    with pytest.raises(DeviceNotFoundError) as exc_info:
                        http_client.post("/test/path", {}, credential)

                    assert "设备不存在" in str(exc_info.value)

    def test_handle_permission_error(self, http_client, credential):
        """测试处理权限不足错误（code=403）"""
        response_text = base64.b64encode('{"code": 403, "message": "权限不足"}'.encode()).decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 403, "message": "权限不足"}'
                ):
                    with pytest.raises(MijiaAPIException) as exc_info:
                        http_client.post("/test/path", {}, credential)

                    assert "权限不足" in str(exc_info.value)
                    assert exc_info.value.code == 403

    def test_handle_server_error(self, http_client, credential):
        """测试处理服务器错误（code=500）"""
        response_text = base64.b64encode('{"code": 500, "message": "服务器内部错误"}'.encode()).decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 500, "message": "服务器内部错误"}'
                ):
                    with pytest.raises(MijiaAPIException) as exc_info:
                        http_client.post("/test/path", {}, credential)

                    assert "服务器内部错误" in str(exc_info.value)
                    assert exc_info.value.code == 500

    def test_handle_timeout_error(self, http_client, credential):
        """测试处理超时错误"""
        with patch.object(
            http_client._client, "post", side_effect=httpx.TimeoutException("Request timeout")
        ):
            with pytest.raises(TimeoutError) as exc_info:
                http_client.post("/test/path", {}, credential)

            assert "请求超时" in str(exc_info.value)

    def test_handle_http_status_error(self, http_client, credential):
        """测试处理HTTP状态码错误"""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(
            http_client._client,
            "post",
            side_effect=httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response),
        ):
            with pytest.raises(NetworkError) as exc_info:
                http_client.post("/test/path", {}, credential)

            assert "HTTP错误" in str(exc_info.value)

    def test_handle_connect_error(self, http_client, credential):
        """测试处理连接错误"""
        with patch.object(
            http_client._client, "post", side_effect=httpx.ConnectError("Connection failed")
        ):
            with pytest.raises(ConnectionError) as exc_info:
                http_client.post("/test/path", {}, credential)

            assert "连接失败" in str(exc_info.value)

    def test_handle_generic_http_error(self, http_client, credential):
        """测试处理通用HTTP错误"""
        with patch.object(http_client._client, "post", side_effect=httpx.HTTPError("Generic error")):
            with pytest.raises(NetworkError) as exc_info:
                http_client.post("/test/path", {}, credential)

            assert "网络错误" in str(exc_info.value)


class TestHttpClientRetry:
    """测试HttpClient重试机制"""

    def test_retry_on_timeout(self, http_client, credential):
        """测试超时时自动重试"""
        # 前两次超时，第三次成功
        response_text = base64.b64encode(b'{"code": 0}').decode()
        mock_response = create_mock_response(200, response_text)

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Timeout")
            return mock_response

        with patch.object(http_client._client, "post", side_effect=side_effect):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0}'
                ):
                    result = http_client.post("/test/path", {}, credential)

        assert result == {"code": 0}
        assert call_count == 3  # 第一次失败 + 2次重试

    def test_retry_exhausted(self, http_client, credential):
        """测试重试次数耗尽后抛出异常"""
        with patch.object(
            http_client._client, "post", side_effect=httpx.TimeoutException("Timeout")
        ):
            with pytest.raises(TimeoutError):
                http_client.post("/test/path", {}, credential)

    def test_no_retry_on_auth_error(self, http_client, credential):
        """测试认证错误不重试"""
        response_text = base64.b64encode('{"code": 401, "message": "Token已过期"}'.encode()).decode()
        mock_response = create_mock_response(200, response_text)

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch.object(http_client._client, "post", side_effect=side_effect):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 401, "message": "Token已过期"}'
                ):
                    with pytest.raises(TokenExpiredError):
                        http_client.post("/test/path", {}, credential)

        # 认证错误不应该重试，只调用一次
        assert call_count == 1


class TestHttpClientClose:
    """测试HttpClient关闭"""

    def test_close(self, http_client):
        """测试关闭客户端"""
        with patch.object(http_client._client, "close") as mock_close:
            http_client.close()

        mock_close.assert_called_once()

    def test_context_manager(self, config, crypto):
        """测试上下文管理器自动关闭"""
        with patch.object(httpx.Client, "close") as mock_close:
            with HttpClient(config, crypto) as client:
                assert isinstance(client, HttpClient)

            # 验证退出时自动关闭
            mock_close.assert_called_once()


class TestHttpClientResponseTime:
    """测试HttpClient响应时间记录"""

    def test_logs_response_time(self, http_client, credential):
        """测试记录响应时间"""
        response_text = base64.b64encode(b'{"code": 0}').decode()
        mock_response = create_mock_response(200, response_text)

        with patch.object(http_client._client, "post", return_value=mock_response):
            with patch.object(
                http_client._crypto, "encrypt_params",
                return_value={"data": "encrypted", "_nonce": "test_nonce", "signature": "sig", "ssecurity": credential.ssecurity}
            ):
                with patch.object(
                    http_client._crypto, "decrypt_response",
                    return_value='{"code": 0}'
                ):
                    with patch("mijiaAPI_V2.infrastructure.http_client.logger") as mock_logger:
                        http_client.post("/test/path", {}, credential)

                        # 查找包含response_time的日志调用
                        info_calls = mock_logger.info.call_args_list
                        response_log = None
                        for call in info_calls:
                            if "extra" in call[1] and "response_time" in call[1]["extra"]:
                                response_log = call[1]["extra"]
                                break

                        assert response_log is not None
                        assert "response_time" in response_log
                        # 响应时间应该是字符串格式，如 "0.123s"
                        assert response_log["response_time"].endswith("s")
