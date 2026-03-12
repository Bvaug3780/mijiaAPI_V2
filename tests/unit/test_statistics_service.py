"""StatisticsService单元测试"""

from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock

import pytest

from mijiaAPI_V2.domain.models import Credential, Device, DeviceStatus
from mijiaAPI_V2.repositories.interfaces import IDeviceRepository
from mijiaAPI_V2.services.statistics_service import StatisticsService


@pytest.fixture
def mock_device_repo() -> Mock:
    """创建模拟的IDeviceRepository"""
    return Mock(spec=IDeviceRepository)


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
def sample_devices() -> List[Device]:
    """创建示例设备列表"""
    return [
        Device(
            did="device_001",
            name="智能灯泡1",
            model="yeelink.light.color1",
            home_id="home_123",
            status=DeviceStatus.ONLINE,
        ),
        Device(
            did="device_002",
            name="智能灯泡2",
            model="yeelink.light.color1",
            home_id="home_123",
            status=DeviceStatus.ONLINE,
        ),
        Device(
            did="device_003",
            name="智能插座",
            model="chuangmi.plug.v3",
            home_id="home_123",
            status=DeviceStatus.OFFLINE,
        ),
        Device(
            did="device_004",
            name="温湿度传感器",
            model="lumi.sensor.ht",
            home_id="home_123",
            status=DeviceStatus.ONLINE,
        ),
        Device(
            did="device_005",
            name="门窗传感器",
            model="lumi.sensor.magnet",
            home_id="home_123",
            status=DeviceStatus.OFFLINE,
        ),
    ]


@pytest.fixture
def statistics_service(mock_device_repo: Mock) -> StatisticsService:
    """创建StatisticsService实例"""
    return StatisticsService(device_repo=mock_device_repo)


def test_statistics_service_initialization(mock_device_repo: Mock) -> None:
    """测试StatisticsService初始化"""
    service = StatisticsService(device_repo=mock_device_repo)
    assert service._device_repo is mock_device_repo


def test_get_device_statistics_returns_correct_counts(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
    sample_devices: List[Device],
) -> None:
    """测试get_device_statistics返回正确的统计数据"""
    # 设置mock返回值
    mock_device_repo.get_all.return_value = sample_devices

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证
    mock_device_repo.get_all.assert_called_once_with("home_123", sample_credential)
    assert result["total"] == 5
    assert result["online"] == 3
    assert result["offline"] == 2


def test_get_device_statistics_returns_correct_model_counts(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
    sample_devices: List[Device],
) -> None:
    """测试get_device_statistics返回正确的按型号统计数据"""
    # 设置mock返回值
    mock_device_repo.get_all.return_value = sample_devices

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证by_model统计
    assert result["by_model"]["yeelink.light.color1"] == 2
    assert result["by_model"]["chuangmi.plug.v3"] == 1
    assert result["by_model"]["lumi.sensor.ht"] == 1
    assert result["by_model"]["lumi.sensor.magnet"] == 1


def test_get_device_statistics_with_empty_device_list(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
) -> None:
    """测试get_device_statistics处理空设备列表"""
    # 设置mock返回空列表
    mock_device_repo.get_all.return_value = []

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证
    assert result["total"] == 0
    assert result["online"] == 0
    assert result["offline"] == 0
    assert result["by_model"] == {}


def test_get_device_statistics_with_all_online_devices(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
) -> None:
    """测试get_device_statistics处理全部在线设备"""
    # 创建全部在线的设备列表
    all_online_devices = [
        Device(
            did=f"device_{i}",
            name=f"设备{i}",
            model="test.model",
            home_id="home_123",
            status=DeviceStatus.ONLINE,
        )
        for i in range(3)
    ]
    mock_device_repo.get_all.return_value = all_online_devices

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证
    assert result["total"] == 3
    assert result["online"] == 3
    assert result["offline"] == 0


def test_get_device_statistics_with_all_offline_devices(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
) -> None:
    """测试get_device_statistics处理全部离线设备"""
    # 创建全部离线的设备列表
    all_offline_devices = [
        Device(
            did=f"device_{i}",
            name=f"设备{i}",
            model="test.model",
            home_id="home_123",
            status=DeviceStatus.OFFLINE,
        )
        for i in range(3)
    ]
    mock_device_repo.get_all.return_value = all_offline_devices

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证
    assert result["total"] == 3
    assert result["online"] == 0
    assert result["offline"] == 3


def test_get_device_statistics_with_unknown_status_devices(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
) -> None:
    """测试get_device_statistics处理未知状态设备（计入离线）"""
    # 创建包含未知状态的设备列表
    devices_with_unknown = [
        Device(
            did="device_001",
            name="在线设备",
            model="test.model",
            home_id="home_123",
            status=DeviceStatus.ONLINE,
        ),
        Device(
            did="device_002",
            name="未知状态设备",
            model="test.model",
            home_id="home_123",
            status=DeviceStatus.UNKNOWN,
        ),
    ]
    mock_device_repo.get_all.return_value = devices_with_unknown

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证（未知状态应该计入离线）
    assert result["total"] == 2
    assert result["online"] == 1
    assert result["offline"] == 1


def test_count_by_model_with_single_model(
    statistics_service: StatisticsService,
) -> None:
    """测试_count_by_model处理单一型号"""
    devices = [
        Device(
            did=f"device_{i}",
            name=f"设备{i}",
            model="same.model",
            home_id="home_123",
            status=DeviceStatus.ONLINE,
        )
        for i in range(5)
    ]

    result = statistics_service._count_by_model(devices)

    assert len(result) == 1
    assert result["same.model"] == 5


def test_count_by_model_with_multiple_models(
    statistics_service: StatisticsService,
    sample_devices: List[Device],
) -> None:
    """测试_count_by_model处理多种型号"""
    result = statistics_service._count_by_model(sample_devices)

    assert len(result) == 4
    assert result["yeelink.light.color1"] == 2
    assert result["chuangmi.plug.v3"] == 1
    assert result["lumi.sensor.ht"] == 1
    assert result["lumi.sensor.magnet"] == 1


def test_count_by_model_with_empty_list(
    statistics_service: StatisticsService,
) -> None:
    """测试_count_by_model处理空列表"""
    result = statistics_service._count_by_model([])

    assert result == {}


def test_get_device_statistics_structure(
    statistics_service: StatisticsService,
    mock_device_repo: Mock,
    sample_credential: Credential,
    sample_devices: List[Device],
) -> None:
    """测试get_device_statistics返回的数据结构"""
    # 设置mock返回值
    mock_device_repo.get_all.return_value = sample_devices

    # 调用方法
    result = statistics_service.get_device_statistics("home_123", sample_credential)

    # 验证数据结构
    assert isinstance(result, dict)
    assert "total" in result
    assert "online" in result
    assert "offline" in result
    assert "by_model" in result
    assert isinstance(result["total"], int)
    assert isinstance(result["online"], int)
    assert isinstance(result["offline"], int)
    assert isinstance(result["by_model"], dict)
