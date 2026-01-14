"""
测试提示词文件路径查找
"""
import sys
from pathlib import Path
import inspect
import os

# 模拟EXE运行环境
print("=" * 60)
print("提示词文件路径诊断")
print("=" * 60)

# 检查当前环境
print(f"\n当前工作目录: {Path.cwd()}")
print(f"sys.executable: {sys.executable}")
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
print(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")

# 获取batch_processor所在目录
processor_file = Path(__file__).parent / "batch_processor.py"
print(f"\nbatch_processor.py路径: {processor_file}")
print(f"batch_processor.py存在: {processor_file.exists()}")

# 尝试多个路径
possible_paths = [
    Path("prompts2/综合评估与排名.txt"),  # 当前目录
    Path(__file__).parent / "prompts2" / "综合评估与排名.txt",  # __file__所在目录
    Path.cwd() / "prompts2" / "综合评估与排名.txt",  # CWD
]

# 如果是打包的EXE，尝试sys._MEIPASS路径
if getattr(sys, 'frozen', False):
    exe_dir = Path(sys.executable).parent
    possible_paths.append(exe_dir / "prompts2" / "综合评估与排名.txt")
    # PyInstaller打包后，数据在_MEIPASS临时目录
    if hasattr(sys, '_MEIPASS'):
        meipass_dir = Path(sys._MEIPASS)
        possible_paths.append(meipass_dir / "prompts2" / "综合评估与排名.txt")

print(f"\n尝试的路径列表:")
for i, p in enumerate(possible_paths, 1):
    exists = p.exists()
    print(f"{i}. {p}")
    print(f"   存在: {exists}")

    if exists:
        print(f"   ✓ 找到！使用此路径")
        break

# 检查prompts2目录
prompts2_dirs = [
    Path.cwd() / "prompts2",
    Path(__file__).parent / "prompts2",
]

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    prompts2_dirs.append(Path(sys._MEIPASS) / "prompts2")

print(f"\nprompts2目录检查:")
for d in prompts2_dirs:
    print(f"  {d}: 存在={d.exists()}")
    if d.exists():
        files = list(d.glob("*.txt"))
        print(f"    包含文件: {[f.name for f in files]}")

print("\n" + "=" * 60)
