#!/usr/bin/env python3
"""示例07：自定义翻译

演示如何使用和扩展设备规格的中文翻译：
- 使用默认翻译
- 添加自定义翻译
- 从文件加载翻译
- 动态添加翻译
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mijiaAPI_V2 import create_api_client_from_file
from mijiaAPI_V2.repositories.property_translations import (
    TranslationManager,
    get_property_translation,
    get_action_translation,
)


def example_default_translation():
    """示例：使用默认翻译"""
    print("=== 示例1：使用默认翻译 ===\n")
    
    # 使用全局函数（默认翻译）
    properties = [
        "Switch Status",
        "Brightness",
        "Color Temperature",
        "Device Manufacturer",
    ]
    
    print("属性翻译:")
    for prop in properties:
        cn_name = get_property_translation(prop)
        print(f"  {prop} -> {cn_name}")
    
    print("\n操作翻译:")
    actions = ["Toggle", "bright-increase", "delay-off"]
    for action in actions:
        cn_name = get_action_translation(action)
        print(f"  {action} -> {cn_name}")
    
    print()


def example_custom_dict():
    """示例：使用自定义翻译字典"""
    print("=== 示例2：使用自定义翻译字典 ===\n")
    
    # 创建自定义翻译
    custom_translations = {
        "properties": {
            "my-custom-property": "我的自定义属性",
            "temperature-sensor": "温度传感器",
            "humidity-sensor": "湿度传感器",
        },
        "actions": {
            "my-custom-action": "我的自定义操作",
            "start-cleaning": "开始清扫",
        }
    }
    
    # 创建翻译管理器
    translator = TranslationManager(custom_translations=custom_translations)
    
    print("自定义翻译:")
    print(f"  my-custom-property -> {translator.get_property_translation('my-custom-property')}")
    print(f"  my-custom-action -> {translator.get_action_translation('my-custom-action')}")
    
    print("\n内置翻译仍然可用:")
    print(f"  Switch Status -> {translator.get_property_translation('Switch Status')}")
    
    print()


def example_custom_file():
    """示例：从文件加载自定义翻译"""
    print("=== 示例3：从文件加载自定义翻译 ===\n")
    
    # 创建临时翻译文件
    custom_file = Path("my_translations.json")
    custom_data = {
        "properties": {
            "air-quality": "空气质量",
            "pm25": "PM2.5浓度",
            "co2": "二氧化碳浓度",
        },
        "actions": {
            "reset-filter": "重置滤网",
            "auto-mode": "自动模式",
        }
    }
    
    with open(custom_file, "w", encoding="utf-8") as f:
        json.dump(custom_data, f, ensure_ascii=False, indent=2)
    
    print(f"已创建翻译文件: {custom_file}\n")
    
    # 从文件加载
    translator = TranslationManager(custom_file=custom_file)
    
    print("从文件加载的翻译:")
    print(f"  air-quality -> {translator.get_property_translation('air-quality')}")
    print(f"  reset-filter -> {translator.get_action_translation('reset-filter')}")
    
    # 清理
    custom_file.unlink()
    print(f"\n已删除临时文件: {custom_file}")
    
    print()


def example_dynamic_translation():
    """示例：动态添加翻译"""
    print("=== 示例4：动态添加翻译 ===\n")
    
    translator = TranslationManager()
    
    # 动态添加翻译
    translator.add_property_translation("new-property", "新属性")
    translator.add_action_translation("new-action", "新操作")
    
    print("动态添加的翻译:")
    print(f"  new-property -> {translator.get_property_translation('new-property')}")
    print(f"  new-action -> {translator.get_action_translation('new-action')}")
    
    print()


def example_real_device():
    """示例：在实际设备中使用自定义翻译"""
    print("=== 示例5：在实际设备中使用 ===\n")
    
    try:
        api = create_api_client_from_file()
        
        # 创建自定义翻译
        custom_translations = {
            "properties": {
                "delay-off-enable": "延时关闭开关",
                "double-click-enable": "双击功能开关",
                "scene-mode": "场景模式",
            }
        }
        
        translator = TranslationManager(custom_translations=custom_translations)
        
        # 获取设备
        homes = api.get_homes()
        if not homes:
            print("未找到任何家庭")
            return
        
        home = homes[0]
        devices = api.get_devices(home.id)
        
        if not devices:
            print("未找到任何设备")
            return
        
        device = devices[0]
        print(f"设备: {device.name} ({device.model})\n")
        
        # 获取设备规格
        spec = api.get_device_spec(device.model)
        if not spec:
            print("未找到设备规格")
            return
        
        print("使用自定义翻译显示属性:\n")
        for prop in spec.properties[:5]:
            cn_name = translator.get_property_translation(prop.name)
            if cn_name != prop.name:
                print(f"  ✓ {cn_name} ({prop.name})")
            else:
                print(f"  - {prop.name}")
        
    except FileNotFoundError:
        print("✗ 凭据文件不存在（跳过此示例）")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print()


def main():
    """主函数"""
    print("=" * 60)
    print("示例08：自定义翻译")
    print("=" * 60)
    print()
    
    example_default_translation()
    example_custom_dict()
    example_custom_file()
    example_dynamic_translation()
    example_real_device()
    
    print("=" * 60)
    print("翻译功能说明：")
    print("1. 内置翻译包含常见的属性和操作")
    print("2. 可以通过字典或文件添加自定义翻译")
    print("3. 自定义翻译会覆盖内置翻译")
    print("4. 支持运行时动态添加翻译")
    print("=" * 60)
    print("\n参考文档：docs/使用指南/05-设备规格翻译.md")


if __name__ == "__main__":
    main()
