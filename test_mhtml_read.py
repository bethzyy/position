"""
测试MHTML文件读取功能
"""
from pathlib import Path
from mhtml_reader import MHTMLReader

# 测试文件夹
test_folder = Path("C:/D/CAIE_tool/MyAIProduct/postion/userdata/中金电信")

print(f"测试文件夹: {test_folder}")
print(f"文件夹存在: {test_folder.exists()}")

# 扫描MHTML文件
mhtml_files = list(test_folder.glob("*.mhtml")) + list(test_folder.glob("*.mht"))
print(f"\n找到 {len(mhtml_files)} 个MHTML文件:")

for f in mhtml_files:
    print(f"  - {f.name}")

# 测试读取
print("\n开始测试读取...")
reader = MHTMLReader()

all_content = []
successful_files = []

for mhtml_file in mhtml_files:
    print(f"\n读取文件: {mhtml_file.name}")
    try:
        result = reader.read_mhtml_file(str(mhtml_file))
        print(f"  结果: {result.keys()}")
        if result and result.get('content'):
            content_length = len(result['content'])
            all_content.append(result['content'])
            successful_files.append(mhtml_file.name)
            print(f"  [OK] 成功读取 {content_length} 字符")
            print(f"  标题: {result.get('title', 'N/A')[:50]}")
            # 显示前100个字符
            print(f"  内容预览: {result['content'][:100]}")
        else:
            print(f"  [FAIL] 内容为空")
    except Exception as e:
        print(f"  [FAIL] 读取失败: {str(e)}")

print(f"\n总结:")
print(f"  成功读取: {len(successful_files)}/{len(mhtml_files)}")
print(f"  总字符数: {sum(len(c) for c in all_content)}")
print(f"\n测试完成！")
