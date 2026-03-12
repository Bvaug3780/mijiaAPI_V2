#!/usr/bin/env python3
"""示例06：批量操作

演示如何高效地进行批量操作：
- 批量获取设备属性
- 批量设置设备属性
- 批量控制多个设备
- 性能优化技巧
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mijiaAPI_V2 import create_api_client_from_file


def main():
    """主函数"""
    print("=== 示例06：批量操作 ===\n")
    
    # 创建API客户端
    api = create_api_client_from_file()
    
    # 获取设备列表
    homes = api.get_homes()
    if not homes:
        print("未找到任何家庭")
        return
    
    home = homes[0]
    devices = api.get_devices(home.id)
    
    if len(devices) < 2:
        print("设备数量不足，无法演示批量操作")
        return
    
    print(f"找到 {len(devices)} 个设备\n")
    
    # 1. 批量获取设备属性
    print("【方法1】批量获取设备属性")
    print("一次请求获取多个设备的多个属性\n")
    
    # 构建批量请求
    requests = []
    for device in devices[:3]:  # 只取前3个设备
        requests.extend([
            {"did": device.did, "siid": 2, "piid": 1},  # 开关状态
            {"did": device.did, "siid": 2, "piid": 2},  # 亮度/其他属性
        ])
    
    start_time = time.time()
    try:
        results = api.get_device_properties(requests)
        elapsed = time.time() - start_time
        
        print(f"✓ 批量获取完成，耗时: {elapsed:.2f}秒")
        print(f"  请求数量: {len(requests)}")
        print(f"  成功数量: {sum(1 for r in results if r.get('code') == 0)}")
        print(f"  失败数量: {sum(1 for r in results if r.get('code') != 0)}")
        
    except Exception as e:
        print(f"✗ 批量获取失败: {e}")
    
    print()
    
    # 2. 批量设置设备属性
    print("【方法2】批量设置设备属性")
    print("一次请求设置多个设备的多个属性\n")
    
    # 构建批量设置请求
    set_requests = []
    for device in devices[:2]:  # 只取前2个设备
        if "light" in device.model.lower():
            set_requests.extend([
                {"did": device.did, "siid": 2, "piid": 1, "value": True},   # 打开
                {"did": device.did, "siid": 2, "piid": 2, "value": 50},     # 亮度50%
            ])
    
    if set_requests:
        start_time = time.time()
        try:
            results = api.batch_control_devices(set_requests)
            elapsed = time.time() - start_time
            
            print(f"✓ 批量设置完成，耗时: {elapsed:.2f}秒")
            print(f"  请求数量: {len(set_requests)}")
            print(f"  成功数量: {sum(1 for r in results if r.get('code') == 0)}")
            print(f"  失败数量: {sum(1 for r in results if r.get('code') != 0)}")
            
        except Exception as e:
            print(f"✗ 批量设置失败: {e}")
    else:
        print("未找到可控制的灯光设备")
    
    print()
    
    # 3. 性能对比：单个 vs 批量
    print("【方法3】性能对比")
    print("比较单个请求和批量请求的性能差异\n")
    
    test_devices = devices[:3]
    
    # 单个请求
    print("单个请求方式:")
    start_time = time.time()
    single_results = []
    for device in test_devices:
        try:
            result = api.get_device_property(device.did, siid=2, piid=1)
            single_results.append(result)
        except:
            pass
    single_elapsed = time.time() - start_time
    print(f"  耗时: {single_elapsed:.2f}秒")
    print(f"  平均每个请求: {single_elapsed/len(test_devices):.2f}秒")
    
    # 批量请求
    print("\n批量请求方式:")
    batch_requests = [
        {"did": device.did, "siid": 2, "piid": 1}
        for device in test_devices
    ]
    start_time = time.time()
    try:
        batch_results = api.get_device_properties(batch_requests)
        batch_elapsed = time.time() - start_time
        print(f"  耗时: {batch_elapsed:.2f}秒")
        print(f"  平均每个请求: {batch_elapsed/len(test_devices):.2f}秒")
        
        if single_elapsed > 0:
            speedup = single_elapsed / batch_elapsed
            print(f"\n✓ 批量请求快 {speedup:.1f}倍")
    except Exception as e:
        print(f"  ✗ 批量请求失败: {e}")
    
    print()
    
    # 4. 批量操作最佳实践
    print("【最佳实践】")
    print("1. 尽可能使用批量API，减少网络往返")
    print("2. 合理控制批量大小（建议每批不超过50个请求）")
    print("3. 处理部分失败的情况（某些设备可能离线）")
    print("4. 添加适当的错误处理和重试机制")
    print("5. 对于大量设备，考虑分批处理")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    main()
