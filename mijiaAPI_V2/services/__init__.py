"""服务层

封装业务逻辑和用例，协调多个仓储完成复杂业务功能。

模块：
- auth_service: 认证服务
- device_service: 设备服务
- scene_service: 场景服务
- statistics_service: 统计服务
"""

from mijiaAPI_V2.services.auth_service import AuthService
from mijiaAPI_V2.services.device_service import DeviceService
from mijiaAPI_V2.services.scene_service import SceneService
from mijiaAPI_V2.services.statistics_service import StatisticsService

__all__ = [
    "AuthService",
    "DeviceService",
    "SceneService",
    "StatisticsService",
]
