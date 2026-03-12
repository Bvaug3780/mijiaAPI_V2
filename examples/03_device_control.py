#!/usr/bin/env python3
"""示例03：设备控制

演示设备控制的各种方法：
- 获取设备属性
- 设置设备属性
- 批量操作
- 调用设备动作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mijiaAPI_V2 import create_api_client_from_file
from mijiaAPI_V2.domain.exceptions import DeviceError, MijiaAPIException


def main():
    """主函数"""
    print("=== 示例03：设备控制 ===\n")
    
    # 创建API客户端
    api = create_api_client_from_file()
    
    # 获取设备列表
    homes = api.get_homes()
    if not homes:
        print("未找到任何家庭")
        return
    
    home = homes[0]
    devices = api.get_devices(home.id)
    
    # 查找灯光设备作为示例
    lamp = None
    for device in devices:
        if device.is_online() and "light" in device.model.lower():
            lamp = device
            break
    
    if not lamp:
        print("未找到在线的灯光设备")
        print("提示：示例需要至少一个在线的灯光设备")
        return
    
    print(f"使用设备: {lamp.name} ({lamp.model})\n")
    
    # 1. 批量获取属性
    print("【方法1】批量获取属性")
    try:
        requests = [
            {"did": lamp.did, "siid": 2, "piid": 1},  # 开关
            {"did": lamp.did, "siid": 2, "piid": 2},  # 亮度
        ]
        results = api.get_device_properties(requests)
        
        for i, result in enumerate(results):
            if result.get("code") == 0:
                print(f"  属性{i+1} (siid={requests[i]['siid']}, piid={requests[i]['piid']}): {result.get('value')}")
            else:
                print(f"  属性{i+1}: 获取失败 (code={result.get('code')})")
    except (DeviceError, MijiaAPIException) as e:
        print(f"  批量获取失败: {e}")
    print()
    
    # 2. 设置单个属性
    print("【方法2】设置单个属性")
    try:
        # 设置开关状态为开
        success = api.control_device(lamp.did, siid=2, piid=1, value=True)
        if success:
            print("  ✓ 设备已打开")
        else:
            print("  ✗ 设置失败")
    except (DeviceError, MijiaAPIException) as e:
        print(f"  设置失败: {e}")
    print()
    
    # 3. 批量设置属性
    print("【方法3】批量设置属性")
    try:
        requests = [
            {"device_id": lamp.did, "siid": 2, "piid": 1, "value": True},   # 打开
            {"device_id": lamp.did, "siid": 2, "piid": 2, "value": 80},     # 亮度80%
        ]
        results = api.batch_control_devices(requests)
        
        for i, result in enumerate(results):
            if result.get("code") == 0:
                print(f"  ✓ 属性{i+1}设置成功")
            else:
                print(f"  ✗ 属性{i+1}设置失败 (code={result.get('code')})")
    except (DeviceError, MijiaAPIException) as e:
        print(f"  批量设置失败: {e}")
    print()
    
    # 4. 调用设备动作
    print("【方法4】调用设备动作")
    try:
        # 注意：不同设备的动作ID不同，需要查看设备规格
        # 这里使用一个通用的示例，可能不适用于所有设备
        result = api.call_device_action(lamp.did, siid=2, aiid=1, params={})
        print(f"  动作执行结果: {result}")
    except (DeviceError, MijiaAPIException) as e:
        print(f"  动作执行失败: {e}")
    print()
    
    # 5. 查看设备规格
    print("【方法5】查看设备规格")
    spec = api.get_device_spec(lamp.model)
    if spec:
        print(f"  设备型号: {spec.model}")
        print(f"  设备名称: {spec.name}")
        print(f"  属性数量: {len(spec.properties)}")
        print(f"  操作数量: {len(spec.actions)}")
        
        if spec.properties:
            print("\n  前3个属性:")
            for prop in spec.properties[:3]:
                print(f"    - {prop.name} (siid={prop.siid}, piid={prop.piid})")
    else:
        print("  未找到设备规格")
    print()
    
    print("=== 示例完成 ===")
    print("\n提示：")
    print("- siid 和 piid 需要根据设备规格确定")
    print("- 使用 'python scripts/show_device_spec.py' 查看完整设备规格")
    print("- 参考文档：docs/使用指南/05-设备规格翻译.md")


if __name__ == "__main__":
    main()
