#!/usr/bin/env python3
"""示例01：认证和凭据管理

演示不同的认证方式：
- 二维码登录（首次使用）
- 从文件加载凭据
- 保存凭据到文件
- 检查凭据有效性
- 刷新过期凭据
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mijiaAPI_V2 import create_api_client_from_file, create_auth_service
from mijiaAPI_V2.domain.exceptions import AuthenticationError


def example_qrcode_login():
    """示例：二维码登录（首次使用）"""
    print("=== 方式1：二维码登录（首次使用）===\n")
    
    try:
        # 创建认证服务
        auth_service = create_auth_service()
        
        # 检查是否已有凭据
        existing_credential = auth_service.load_credential()
        if existing_credential and existing_credential.is_valid():
            print("✓ 已有有效凭据，无需重新登录")
            print(f"  用户ID: {existing_credential.user_id}")
            print(f"  剩余有效期: {existing_credential.expires_in()} 秒")
            print("\n如需重新登录，请删除凭据文件后再运行")
            return
        
        print("请使用米家APP扫描下方二维码进行登录：\n")
        
        # 二维码登录
        credential = auth_service.login_by_qrcode()
        print("\n✓ 登录成功！")
        
        # 保存凭据
        auth_service.save_credential(credential)
        print("✓ 凭据已保存")
        
        # 显示凭据信息
        print("\n凭据信息:")
        print(f"  用户ID: {credential.user_id}")
        print(f"  设备ID: {credential.device_id}")
        print(f"  有效期: {credential.expires_in()} 秒")
        
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n✗ 登录失败: {e}")
    
    print()


def example_load_from_file():
    """示例：从文件加载凭据"""
    print("=== 方式2：从文件加载凭据 ===\n")
    
    try:
        # 从默认位置加载凭据
        api = create_api_client_from_file()
        print("✓ 凭据加载成功")
        
        # 检查凭据有效性
        credential = api.credential
        print(f"  用户ID: {credential.user_id}")
        print(f"  有效期: 剩余 {credential.expires_in()} 秒")
        print(f"  是否有效: {credential.is_valid()}")
        
        # 测试API调用
        homes = api.get_homes()
        print(f"  测试调用: 找到 {len(homes)} 个家庭")
        
    except FileNotFoundError:
        print("✗ 凭据文件不存在")
        print("  请先运行方式1进行二维码登录")
    except AuthenticationError as e:
        print(f"✗ 认证失败: {e}")
    
    print()


def example_save_credential():
    """示例：保存凭据到自定义位置"""
    print("=== 方式3：保存凭据到自定义位置 ===\n")
    
    try:
        # 创建认证服务
        auth_service = create_auth_service()
        
        # 加载现有凭据
        credential = auth_service.load_credential()
        if not credential:
            print("✗ 凭据文件不存在，请先登录")
            return
        
        # 保存到自定义位置
        custom_path = Path("my_credentials.json")
        auth_service.save_credential(credential, custom_path)
        print(f"✓ 凭据已保存到: {custom_path}")
        
        # 从自定义位置加载
        api2 = create_api_client_from_file(custom_path)
        print(f"✓ 从自定义位置加载成功")
        
        # 清理示例文件
        custom_path.unlink()
        print(f"✓ 清理示例文件")
        
    except FileNotFoundError:
        print("✗ 凭据文件不存在")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print()


def example_check_credential_validity():
    """示例：检查凭据有效性"""
    print("=== 方式4：检查凭据有效性 ===\n")
    
    try:
        api = create_api_client_from_file()
        credential = api.credential
        
        print("凭据信息:")
        print(f"  用户ID: {credential.user_id}")
        print(f"  设备ID: {credential.device_id}")
        print(f"  过期时间: {credential.expires_at}")
        print(f"  剩余时间: {credential.expires_in()} 秒")
        print(f"  是否过期: {credential.is_expired()}")
        print(f"  是否有效: {credential.is_valid()}")
        
    except FileNotFoundError:
        print("✗ 凭据文件不存在")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print()


def example_refresh_credential():
    """示例：刷新过期凭据"""
    print("=== 方式5：刷新过期凭据 ===\n")
    
    try:
        auth_service = create_auth_service()
        credential = auth_service.load_credential()
        
        if not credential:
            print("✗ 凭据文件不存在")
            return
        
        if credential.is_expired():
            print("凭据已过期，尝试刷新...")
            try:
                # 注意：当前版本可能不支持刷新，需要重新登录
                print("✗ 凭据已过期，请重新登录")
                print("  提示：删除凭据文件后运行方式1重新登录")
            except Exception as e:
                print(f"✗ 刷新失败: {e}")
        else:
            print("✓ 凭据仍然有效，无需刷新")
            print(f"  剩余有效期: {credential.expires_in()} 秒")
        
    except FileNotFoundError:
        print("✗ 凭据文件不存在")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print()


def main():
    """主函数"""
    print("=" * 60)
    print("示例01：认证和凭据管理")
    print("=" * 60)
    print()
    
    # 检查是否需要登录
    try:
        auth_service = create_auth_service()
        credential = auth_service.load_credential()
        if not credential or not credential.is_valid():
            print("⚠️  检测到未登录或凭据已过期")
            print("=" * 60)
            print()
            # 执行登录
            example_qrcode_login()
            print("=" * 60)
            print()
    except:
        pass
    
    # 运行其他示例
    example_load_from_file()
    example_save_credential()
    example_check_credential_validity()
    example_refresh_credential()
    
    print("=" * 60)
    print("认证流程说明：")
    print("1. 首次使用：运行方式1进行二维码登录")
    print("2. 日常使用：凭据会自动从文件加载")
    print("3. 凭据管理：可以保存到自定义位置")
    print("4. 凭据过期：需要重新登录（约7天有效期）")
    print("=" * 60)


if __name__ == "__main__":
    main()
