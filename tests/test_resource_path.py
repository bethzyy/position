"""
测试资源文件路径解析（EXE和Python脚本）
"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_resource_path_function():
    """测试get_resource_path函数"""
    print("=" * 60)
    print("测试 get_resource_path 函数")
    print("=" * 60)
    print()

    # 导入函数
    from ai_analyzer import get_resource_path

    # 检查运行模式
    if getattr(sys, 'frozen', False):
        print(f"[INFO] 运行模式: EXE (sys.frozen={sys.frozen})")
        print(f"[INFO] sys.executable: {sys.executable}")
        print(f"[INFO] sys._MEIPASS: {sys._MEIPASS}")
    else:
        print(f"[INFO] 运行模式: Python脚本")
        print(f"[INFO] __file__: {__file__}")

    print()

    # 测试prompts目录路径
    prompts_path = get_resource_path("prompts")
    print(f"[INFO] prompts目录路径: {prompts_path}")
    print(f"[INFO] prompts目录存在: {prompts_path.exists()}")
    print()

    # 测试company_culture_analysis.txt
    culture_prompt = get_resource_path("prompts/company_culture_analysis.txt")
    print(f"[INFO] company_culture_analysis.txt路径: {culture_prompt}")
    print(f"[INFO] 文件存在: {culture_prompt.exists()}")

    if culture_prompt.exists():
        print(f"[INFO] 文件大小: {culture_prompt.stat().st_size} 字节")
        with open(culture_prompt, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"[INFO] 文件内容长度: {len(content)} 字符")
            print(f"[INFO] 前100个字符: {content[:100]}")
    else:
        print("[ERROR] 文件不存在！")

    print()

    # 测试position_match_analysis.txt
    position_prompt = get_resource_path("prompts/position_match_analysis.txt")
    print(f"[INFO] position_match_analysis.txt路径: {position_prompt}")
    print(f"[INFO] 文件存在: {position_prompt.exists()}")

    if position_prompt.exists():
        print(f"[INFO] 文件大小: {position_prompt.stat().st_size} 字节")
        with open(position_prompt, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"[INFO] 文件内容长度: {len(content)} 字符")
            print(f"[INFO] 前100个字符: {content[:100]}")
    else:
        print("[ERROR] 文件不存在！")

    print()

    # 列出prompts目录所有文件
    if prompts_path.exists():
        print("[INFO] prompts目录内容:")
        for file in prompts_path.iterdir():
            print(f"  - {file.name} ({file.stat().st_size} 字节)")

    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("资源文件路径测试")
    print("=" * 60 + "\n")

    try:
        test_resource_path_function()

        print("=" * 60)
        print("[OK] 测试完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
