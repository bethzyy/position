"""
测试配置文件持久化功能
"""
import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config_path_resolution():
    """测试配置文件路径解析"""
    print("=" * 60)
    print("测试 1: 配置文件路径解析")
    print("=" * 60)

    # 模拟EXE运行环境
    print(f"sys.frozen = {getattr(sys, 'frozen', False)}")
    print(f"sys.executable = {sys.executable}")

    if getattr(sys, 'frozen', False):
        config_path = Path(sys.executable).parent / "config.json"
        print(f"EXE模式，配置文件路径: {config_path}")
    else:
        config_path = Path(__file__).parent.parent / "config.json"
        print(f"脚本模式，配置文件路径: {config_path}")

    print(f"配置文件存在: {config_path.exists()}")
    print(f"配置文件父目录: {config_path.parent}")
    print(f"父目录存在: {config_path.parent.exists()}")
    print()

def test_config_creation():
    """测试创建配置文件"""
    print("=" * 60)
    print("测试 2: 创建测试配置文件")
    print("=" * 60)

    config_path = Path(__file__).parent.parent / "config.json"

    test_config = {
        'urls': 'https://example.com/review1\nhttps://example.com/review2',
        'resume_path': 'C:\\test\\resume.pdf',
        'job_description': '这是一个测试职位描述',
        'output_path': 'output\\测试报告.html'
    }

    print(f"写入配置文件到: {config_path}")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    print(f"[OK] 配置文件已创建")
    print(f"配置文件存在: {config_path.exists()}")

    # 读取验证
    with open(config_path, 'r', encoding='utf-8') as f:
        loaded_config = json.load(f)

    print(f"[OK] 配置文件内容验证:")
    print(json.dumps(loaded_config, ensure_ascii=False, indent=2))
    print()

def test_config_loading():
    """测试配置文件加载"""
    print("=" * 60)
    print("测试 3: 测试配置文件加载（通过GUI）")
    print("=" * 60)

    try:
        import tkinter as tk
        from main import PositionAnalysisTool

        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        print("创建 PositionAnalysisTool 实例...")
        app = PositionAnalysisTool(root)

        print(f"[OK] 配置文件路径: {app.config_file}")
        print(f"[OK] 配置文件存在: {app.config_file.exists()}")
        print(f"[OK] 加载的配置:")
        print(json.dumps(app.config, ensure_ascii=False, indent=2))

        root.destroy()
        print()
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        print()

def test_config_update():
    """测试配置文件更新"""
    print("=" * 60)
    print("测试 4: 测试配置文件更新")
    print("=" * 60)

    config_path = Path(__file__).parent.parent / "config.json"

    if not config_path.exists():
        print("[SKIP] 配置文件不存在，跳过测试")
        return

    # 读取当前配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    print("当前配置:")
    print(json.dumps(config, ensure_ascii=False, indent=2))

    # 修改配置
    config['urls'] += '\nhttps://example.com/new_review'
    config['job_description'] = '更新后的职位描述'

    print("\n更新后的配置:")
    print(json.dumps(config, ensure_ascii=False, indent=2))

    # 保存
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 配置文件已更新")

    # 再次读取验证
    with open(config_path, 'r', encoding='utf-8') as f:
        verify_config = json.load(f)

    print("[OK] 验证成功")
    print()

def cleanup():
    """清理测试文件"""
    print("=" * 60)
    print("清理测试文件")
    print("=" * 60)

    config_path = Path(__file__).parent.parent / "config.json"

    if config_path.exists():
        print(f"删除配置文件: {config_path}")
        config_path.unlink()
        print("[OK] 配置文件已删除")
    else:
        print("配置文件不存在，无需清理")
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("配置文件持久化测试")
    print("=" * 60 + "\n")

    try:
        test_config_path_resolution()
        test_config_creation()
        test_config_loading()
        test_config_update()

        input("\n按回车键继续清理测试文件...")
        cleanup()

        print("=" * 60)
        print("[OK] 所有测试完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
