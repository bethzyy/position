"""
测试新功能:公司名称、图表、缩进
"""
from report_generator import ReportGenerator

def test_new_features():
    """测试新增功能"""
    generator = ReportGenerator()

    # 测试文本 - 包含百分比数据和不同层级
    culture_text = """
# 公司文化分析报告

## 一、公司氛围
根据员工反馈，30%的员工认为公司氛围很好，40%的员工觉得一般，30%的员工认为有待改进。

### 工作环境
- 开放式办公环境
- 弹性工作制度
  - 每周可在家办公2天
  - 夏季工作时间灵活
- 团队协作密切

## 二、员工福利
调查显示：50%的员工对五险一金满意，35%的员工认为培训机会充足，15%的员工希望改善休假制度。

### 薪酬结构
- 基本工资
- 绩效奖金
  - 季度奖金
  - 年终奖金
- 股票期权
"""

    match_text = """
# 职位匹配分析

## 一、技能匹配度
核心技能匹配度评估：
- 60%的技能完全匹配
- 30%的技能需要提升
- 10%的技能缺乏经验

## 二、面试准备
需要准备的面试问题：
1. 技术面试
   - 算法与数据结构
   - 系统设计
   - 编程语言特性
2. 行为面试
   - 团队合作经验
   - 项目管理能力
   - 问题解决案例
"""

    sources = ["test_file.mhtml"]

    output = generator.generate_html_report(
        culture_text,
        match_text,
        sources,
        "output/test_new_features.html",
        "科技公司ABC"
    )

    print(f"[OK] Test report generated: {output}")
    print("New features included:")
    print("  1. Company name in title")
    print("  2. Auto-detect and generate pie charts")
    print("  3. Optimized indentation for nested lists")

if __name__ == "__main__":
    test_new_features()
