"""AuthService单元测试"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from mijiaAPI_V2.domain.models import Credential
from mijiaAPI_V2.infrastructure.credential_provider import CredentialProvider
from mijiaAPI_V2.infrastructure.credential_store import ICredentialStore
from mijiaAPI_V2.services.auth_service import AuthService


@pytest.fixture
def mock_provider() -> Mock:
    """创建模拟的CredentialProvider"""
    return Mock(spec=CredentialProvider)


@pytest.fixture
def mock_store() -> Mock:
    """创建模拟的ICredentialStore"""
    return Mock(spec=ICredentialStore)


@pytest.fixture
def sample_credential() -> Credential:
    """创建示例凭据"""
    return Credential(
        user_id="test_user_123",
        service_token="test_token_abc",
        ssecurity="test_ssecurity_xyz",
        c_user_id="test_c_user_id",
        device_id="test_device_456",
        user_agent="iOS-14.4-6.0.103-iPhone12,1",
        expires_at=datetime.now() + timedelta(days=7),
    )


@pytest.fixture
def auth_service(mock_provider: Mock, mock_store: Mock) -> AuthService:
    """创建AuthService实例"""
    return AuthService(provider=mock_provider, store=mock_store)


def test_auth_service_initialization(mock_provider: Mock, mock_store: Mock) -> None:
    """测试AuthService初始化"""
    service = AuthService(provider=mock_provider, store=mock_store)
    assert service._provider is mock_provider
    assert service._store is mock_store


def test_login_by_qrcode_delegates_to_provider(
    auth_service: AuthService, mock_provider: Mock, sample_credential: Credential
) -> None:
    """测试login_by_qrcode委托给provider"""
    # 设置mock返回值
    mock_provider.login_by_qrcode.return_value = sample_credential

    # 调用方法
    result = auth_service.login_by_qrcode()

    # 验证
    mock_provider.login_by_qrcode.assert_called_once()
    assert result == sample_credential
    assert result.user_id == "test_user_123"


def test_refresh_credential_delegates_to_provider(
    auth_service: AuthService, mock_provider: Mock, sample_credential: Credential
) -> None:
    """测试refresh_credential委托给provider"""
    # 创建新凭据
    new_credential = Credential(
        user_id=sample_credential.user_id,
        service_token="new_token_def",
        ssecurity="new_ssecurity_uvw",
        c_user_id="test_c_user_id",
        device_id=sample_credential.device_id,
        user_agent=sample_credential.user_agent,
        expires_at=datetime.now() + timedelta(days=7),
    )
    mock_provider.refresh.return_value = new_credential

    # 调用方法
    result = auth_service.refresh_credential(sample_credential)

    # 验证
    mock_provider.refresh.assert_called_once_with(sample_credential)
    assert result == new_credential
    assert result.service_token == "new_token_def"


def test_save_credential_delegates_to_store(
    auth_service: AuthService, mock_store: Mock, sample_credential: Credential
) -> None:
    """测试save_credential委托给store"""
    # 调用方法
    auth_service.save_credential(sample_credential)

    # 验证
    mock_store.save.assert_called_once_with(sample_credential, None)


def test_save_credential_with_custom_path(
    auth_service: AuthService, mock_store: Mock, sample_credential: Credential
) -> None:
    """测试save_credential使用自定义路径"""
    custom_path = "/custom/path/credential.json"

    # 调用方法
    auth_service.save_credential(sample_credential, path=custom_path)

    # 验证
    mock_store.save.assert_called_once_with(sample_credential, custom_path)


def test_load_credential_delegates_to_store(
    auth_service: AuthService, mock_store: Mock, sample_credential: Credential
) -> None:
    """测试load_credential委托给store"""
    # 设置mock返回值
    mock_store.load.return_value = sample_credential

    # 调用方法
    result = auth_service.load_credential()

    # 验证
    mock_store.load.assert_called_once_with(None)
    assert result == sample_credential


def test_load_credential_with_custom_path(
    auth_service: AuthService, mock_store: Mock, sample_credential: Credential
) -> None:
    """测试load_credential使用自定义路径"""
    custom_path = "/custom/path/credential.json"
    mock_store.load.return_value = sample_credential

    # 调用方法
    result = auth_service.load_credential(path=custom_path)

    # 验证
    mock_store.load.assert_called_once_with(custom_path)
    assert result == sample_credential


def test_load_credential_returns_none_when_not_found(
    auth_service: AuthService, mock_store: Mock
) -> None:
    """测试load_credential在凭据不存在时返回None"""
    # 设置mock返回None
    mock_store.load.return_value = None

    # 调用方法
    result = auth_service.load_credential()

    # 验证
    mock_store.load.assert_called_once_with(None)
    assert result is None


def test_revoke_credential_delegates_to_provider(
    auth_service: AuthService, mock_provider: Mock, sample_credential: Credential
) -> None:
    """测试revoke_credential委托给provider"""
    # 设置mock返回值
    mock_provider.revoke.return_value = True

    # 调用方法
    result = auth_service.revoke_credential(sample_credential)

    # 验证
    mock_provider.revoke.assert_called_once_with(sample_credential)
    assert result is True


def test_revoke_credential_returns_false_on_failure(
    auth_service: AuthService, mock_provider: Mock, sample_credential: Credential
) -> None:
    """测试revoke_credential在失败时返回False"""
    # 设置mock返回False
    mock_provider.revoke.return_value = False

    # 调用方法
    result = auth_service.revoke_credential(sample_credential)

    # 验证
    mock_provider.revoke.assert_called_once_with(sample_credential)
    assert result is False
