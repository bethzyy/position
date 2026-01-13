"""
检查HTML报告内容
"""
from pathlib import Path

report_file = Path("C:/D/CAIE_tool/MyAIProduct/postion/userdata/output/test.html")

# 读取报告
with open(report_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查关键词
keywords = {
    "工资": "工资待遇文件",
    "怎么样": "公司评价文件",
    "问答": "问答互动文件",
    "面试经验": "面试经验文件"
}

print(f"报告总长度: {len(content)} 字符\n")
print("检查各文件内容是否包含在报告中:\n")

for keyword, description in keywords.items():
    if keyword in content:
        count = content.count(keyword)
        print(f"[OK] {description}: 包含 '{keyword}' (出现{count}次)")
    else:
        print(f"[MISSING] {description}: 未找到 '{keyword}'")

# 查找数据来源部分
if "数据来源" in content:
    start = content.find("数据来源")
    end = content.find("</div>", start) + 6
    sources_section = content[start:end]
    print(f"\n数据来源部分:")
    print(sources_section[:500])
