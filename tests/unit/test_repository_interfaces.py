"""仓储接口单元测试

验证仓储接口定义的正确性。
"""

from abc import ABC
from typing import get_type_hints

import pytest

from mijiaAPI_V2.repositories.interfaces import (
    DeviceSpec,
    IDeviceRepository,
    IDeviceSpecRepository,
    IHomeRepository,
    ISceneRepository,
)


class TestRepositoryInterfaces:
    """测试仓储接口定义"""

    def test_ihome_repository_is_abstract(self):
        """测试IHomeRepository是抽象基类"""
        assert issubclass(IHomeRepository, ABC)
        # 尝试实例化应该失败
        with pytest.raises(TypeError):
            IHomeRepository()  # type: ignore

    def test_idevice_repository_is_abstract(self):
        """测试IDeviceRepository是抽象基类"""
        assert issubclass(IDeviceRepository, ABC)
        with pytest.raises(TypeError):
            IDeviceRepository()  # type: ignore

    def test_iscene_repository_is_abstract(self):
        """测试ISceneRepository是抽象基类"""
        assert issubclass(ISceneRepository, ABC)
        with pytest.raises(TypeError):
            ISceneRepository()  # type: ignore

    def test_idevice_spec_repository_is_abstract(self):
        """测试IDeviceSpecRepository是抽象基类"""
        assert issubclass(IDeviceSpecRepository, ABC)
        with pytest.raises(TypeError):
            IDeviceSpecRepository()  # type: ignore

    def test_ihome_repository_methods(self):
        """测试IHomeRepository包含所有必需方法"""
        methods = ["get_all", "get_by_id"]
        for method in methods:
            assert hasattr(IHomeRepository, method)
            assert callable(getattr(IHomeRepository, method))

    def test_idevice_repository_methods(self):
        """测试IDeviceRepository包含所有必需方法"""
        methods = [
            "get_all",
            "get_by_id",
            "get_properties",
            "set_property",
            "call_action",
            "batch_get_properties",
            "batch_set_properties",
        ]
        for method in methods:
            assert hasattr(IDeviceRepository, method)
            assert callable(getattr(IDeviceRepository, method))

    def test_iscene_repository_methods(self):
        """测试ISceneRepository包含所有必需方法"""
        methods = ["get_all", "execute"]
        for method in methods:
            assert hasattr(ISceneRepository, method)
            assert callable(getattr(ISceneRepository, method))

    def test_idevice_spec_repository_methods(self):
        """测试IDeviceSpecRepository包含所有必需方法"""
        methods = ["get_spec", "cache_spec"]
        for method in methods:
            assert hasattr(IDeviceSpecRepository, method)
            assert callable(getattr(IDeviceSpecRepository, method))

    def test_device_spec_model(self):
        """测试DeviceSpec模型定义"""
        from mijiaAPI_V2.domain.models import DeviceAction, DeviceProperty

        # 创建一个简单的DeviceSpec实例
        spec = DeviceSpec(
            model="test.model.v1",
            name="测试设备",
            properties=[],
            actions=[],
        )

        assert spec.model == "test.model.v1"
        assert spec.name == "测试设备"
        assert spec.properties == []
        assert spec.actions == []

    def test_device_spec_with_properties_and_actions(self):
        """测试DeviceSpec包含属性和操作"""
        from mijiaAPI_V2.domain.models import (
            DeviceAction,
            DeviceProperty,
            PropertyAccess,
            PropertyType,
        )

        prop = DeviceProperty(
            siid=1,
            piid=1,
            name="开关",
            type=PropertyType.BOOL,
            access=PropertyAccess.READ_WRITE,
        )

        action = DeviceAction(siid=1, aiid=1, name="开灯", parameters=[])

        spec = DeviceSpec(
            model="test.model.v1",
            name="测试设备",
            properties=[prop],
            actions=[action],
        )

        assert len(spec.properties) == 1
        assert spec.properties[0].name == "开关"
        assert len(spec.actions) == 1
        assert spec.actions[0].name == "开灯"

    def test_all_methods_accept_credential_parameter(self):
        """测试所有仓储方法都接受credential参数"""
        from mijiaAPI_V2.domain.models import Credential

        # 检查IHomeRepository
        hints = get_type_hints(IHomeRepository.get_all)
        assert "credential" in hints
        assert hints["credential"] == Credential

        hints = get_type_hints(IHomeRepository.get_by_id)
        assert "credential" in hints
        assert hints["credential"] == Credential

        # 检查IDeviceRepository
        hints = get_type_hints(IDeviceRepository.get_all)
        assert "credential" in hints
        assert hints["credential"] == Credential

        hints = get_type_hints(IDeviceRepository.set_property)
        assert "credential" in hints
        assert hints["credential"] == Credential

        # 检查ISceneRepository
        hints = get_type_hints(ISceneRepository.get_all)
        assert "credential" in hints
        assert hints["credential"] == Credential

        hints = get_type_hints(ISceneRepository.execute)
        assert "credential" in hints
        assert hints["credential"] == Credential
