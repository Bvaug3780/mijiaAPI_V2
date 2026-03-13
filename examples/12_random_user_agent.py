#!/usr/bin/env python3
"""示例12：随机User-Agent生成

演示系统如何为每次登录生成随机的移动端User-Agent，
提高账号安全性和避免被识别为自动化工具。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mijiaAPI_V2.core.config import ConfigManager
from mijiaAPI_V2.infrastructure.credential_provider import CredentialProvider


def demonstrate_random_user_agent():
    """演示随机User-Agent生成"""
    print("=" * 60)
    print("示例12：随机User-Agent生成")
    print("=" * 60)
    print()
    
    print("系统会为每次登录自动生成随机的移动端User-Agent")
    print("支持iOS和Android两种平台（80% iOS, 20% Android）")
    print()
    print("这样可以：")
    print("  1. 提高账号安全性")
    print("  2. 避免被识别为自动化工具")
    print("  3. 模拟真实的移动设备访问")
    print("  4. 支持多种设备型号和系统版本")
    print()
    
    # 创建凭据提供者
    config = ConfigManager()
    provider = CredentialProvider(config)
    
    print("生成10个示例User-Agent：")
    print()
    
    ios_count = 0
    android_count = 0
    
    for i in range(10):
        ua = provider._generate_user_agent()
        if ua.startswith("iOS"):
            ios_count += 1
            parts = ua.split("-")
            print(f"{i+1:2d}. [iOS    ] {ua}")
            if len(parts) == 4:
                print(f"    平台: {parts[0]}, iOS版本: {parts[1]}, "
                      f"APP版本: {parts[2]}, 设备: {parts[3]}")
        else:
            android_count += 1
            print(f"{i+1:2d}. [Android] {ua[:70]}...")
            parts = ua.split("-")
            if len(parts) >= 5:
                print(f"    平台: {parts[0]}, Android版本: {parts[1]}, "
                      f"APP版本: {parts[2]}, 设备: {parts[4]}")
        print()
    
    print(f"统计: iOS={ios_count}, Android={android_count}")
    print()
    print("=" * 60)
    print("说明：")
    print()
    print("1. 每次登录时会自动生成新的User-Agent")
    print("2. User-Agent会保存在凭据中，刷新时继续使用")
    print("3. 重新登录会生成新的User-Agent")
    print("4. 支持iOS和Android两种平台")
    print("5. 支持多种系统版本、APP版本和设备型号组合")
    print()
    print("iOS User-Agent格式：")
    print("  iOS-{iOS版本}-{APP版本}-{设备型号}")
    print()
    print("Android User-Agent格式：")
    print("  Android-{版本}-{APP版本}-Xiaomi-{设备型号}-...")
    print()
    print("示例：")
    print("  iOS: iOS-17.2-8.0.103-iPhone15,4")
    print("       表示：iOS 17.2系统，米家APP 8.0.103版本，iPhone 15设备")
    print()
    print("  Android: Android-14-8.0.702-Xiaomi-2304FPN6DC-...")
    print("           表示：Android 14系统，米家APP 8.0.702版本，Xiaomi 14设备")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_random_user_agent()
