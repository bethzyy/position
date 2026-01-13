"""
系统集成测试
"""
import sys
import os
import logging
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from resume_parser import ResumeParser
from report_generator import ReportGenerator


def setup_logging():
    """设置测试日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_resume_parser():
    """测试简历解析模块"""
    print("\n" + "=" * 60)
    print("测试1: 简历解析模块")
    print("=" * 60)

    parser = ResumeParser()

    # 创建测试简历文件
    test_resume_path = Path("tests/test_resume.txt")
    test_resume_path.parent.mkdir(exist_ok=True)

    test_content = """
张三
高级Python开发工程师

📧 邮箱: zhangsan@example.com
📱 电话: 138-0000-0000

📚 教育背景
北京大学 计算机科学与技术 本科 2015-2019
- GPA: 3.8/4.0
- 主修课程: 数据结构、算法、操作系统、计算机网络

💼 工作经历
ABC科技公司 Python后端工程师 2019.07 - 2022.06
- 负责公司核心业务系统的后端开发
- 使用Django REST Framework开发RESTful API
- 优化数据库查询，性能提升30%
- 参与系统架构设计和代码审查

XYZ互联网公司 高级Python工程师 2022.07 - 至今
- 负责微服务架构设计和实现
- 使用FastAPI开发高性能API
- 设计并实现分布式缓存系统
- 带领5人团队完成多个项目

🔧 技术技能
编程语言: Python, Java, Go, JavaScript
后端框架: Django, Flask, FastAPI, Spring Boot
数据库: MySQL, PostgreSQL, MongoDB, Redis
消息队列: RabbitMQ, Kafka
容器化: Docker, Kubernetes
其他: Git, CI/CD, Linux, Nginx

🏆 项目经验
1. 电商平台后端系统 (2023.01 - 2023.06)
   - 技术栈: FastAPI + PostgreSQL + Redis + Docker
   - 职责: 系统架构设计、核心模块开发
   - 成果: 支撑10万+日活用户

2. 数据分析平台 (2022.09 - 2022.12)
   - 技术栈: Python + Pandas + Elasticsearch
   - 职责: 数据处理模块开发
   - 成果: 数据处理效率提升50%
    """

    with open(test_resume_path, 'w', encoding='utf-8') as f:
        f.write(test_content)

    try:
        content = parser.parse_resume(str(test_resume_path))
        print(f"✓ 简历解析成功")
        print(f"  内容长度: {len(content)} 字符")
        print(f"  预览: {content[:200]}...")
        return True
    except Exception as e:
        print(f"✗ 简历解析失败: {e}")
        return False


def test_report_generator():
    """测试报告生成模块"""
    print("\n" + "=" * 60)
    print("测试2: 报告生成模块")
    print("=" * 60)

    generator = ReportGenerator()

    # 测试数据
    culture_text = """
# XX科技公司文化分析报告

## 一、公司氛围
XX科技是一家充满活力的互联网公司，工作氛围积极向上。员工普遍反映团队协作良好，同事关系融洽。

工作环境：开放式办公环境，设施现代化
团队氛围：扁平化管理，沟通顺畅
工作压力：中等，偶尔需要加班赶项目

## 二、企业员工文化
公司重视员工个人发展和技能提升。

员工发展：
- 提供内部培训和外部学习机会
- 定期技术分享会
- 清晰的晋升通道（P序列和M序列）

薪资福利：
- 具有竞争力的薪资
- 五险一金
- 年终奖（1-3个月）
- 餐补、交通补

工作生活平衡：
- 弹性工作制
- 偶尔周末加班
- 年假15天起

## 三、面试流程与经验
面试流程：
1. HR电话面试（30分钟）
2. 技术笔试（在线编程）
3. 技术面试（两轮，各1小时）
4. HR面试（30分钟）
5. 综合面试（部门负责人，30分钟）

面试内容：
- 编程题：算法和数据结构
- 框架题：Django/Flask使用经验
- 数据库：SQL和优化
- 系统设计：小型系统架构

注意事项：
- 准备充分的算法题练习
- 了解公司业务和技术栈
- 准备项目经验介绍

## 四、关键发现
正面：
✓ 技术氛围浓厚，学习机会多
✓ 晋升通道清晰
✓ 薪资待遇有竞争力

负面：
✗ 加班文化存在
✗ 部门业务压力大

## 五、建议总结
XX科技适合追求技术成长的候选人，公司提供良好的学习平台和晋升机会。但需要注意工作压力和加班情况。
    """

    match_text = """
# 职位匹配分析与面试建议

## 一、职位定位分析
该职位是XX科技的核心后端开发岗位，负责公司主要业务系统的开发和维护。

职位重要性：★★★★☆
- 直接影响公司核心业务
- 技术挑战较高
- 晋升空间大

核心职责：
- 后端API开发
- 系统性能优化
- 技术方案设计
- 代码审查和指导

发展空间：
- 技术路线：高级工程师 → 架构师 → 技术专家
- 管理路线：技术组长 → 技术经理 → 技术总监

## 二、匹配度评估

### 技能匹配度
评分: 85/100

完全匹配：
✓ Python语言（5年经验）
✓ Django框架（熟练）
✓ MySQL数据库（熟练）
✓ Redis缓存（熟悉）
✓ Git版本控制（熟练）

部分匹配：
~ FastAPI（有经验但不够深入）
~ 微服务架构（有经验但项目规模较小）

需提升：
✗ Kafka消息队列（无经验）
✗ Kubernetes容器编排（了解但不熟练）

### 经验匹配度
评分: 90/100

✓ 5年Python后端开发经验（符合3-5年要求）
✓ 互联网公司背景
✓ 核心系统开发经验
✓ 团队协作和代码审查经验

### 文化匹配度
评分: 80/100

✓ 技术学习意愿强（符合公司技术氛围）
✓ 接受弹性工作制
✓ 有技术分享习惯

⚠ 需要注意：对加班的接受度

### 综合匹配度
总分: 85/100
评级: 良好

## 三、职业发展利弊分析

### 优势
1. 技术成长：公司技术氛围浓厚，可以学习前沿技术
2. 职业发展：清晰的晋升通道，技术+管理双路径
3. 薪资提升：预期薪资涨幅20-30%
4. 项目经验：有机会参与大规模分布式系统

### 风险
1. 加班文化：可能影响工作生活平衡
2. 技能单一：长期专注后端可能导致技能单一
3. 跳槽限制：垂直领域跳槽选择较少

### 发展建议
✓ 建议接受该offer
- 技术匹配度高（85分）
- 职业发展空间大
- 薪资有竞争力

⚠ 需要注意：
- 入职后尽快学习Kafka和K8s
- 关注工作生活平衡
- 定期更新简历保持竞争力

## 四、面试准备清单

### 需要准备回答的问题

技术问题：
1. Django的MTV架构是什么？如何工作？
2. 如何优化数据库查询性能？
3. Redis缓存穿透、击穿、雪崩如何解决？
4. 微服务架构的优缺点？
5. 如何设计一个高并发系统？
6. Python的GIL是什么？如何避免？
7. RESTful API设计原则？
8. 如何处理事务并发问题？

行为面试问题（STAR法则）：
1. 介绍一个你参与的最有挑战性的项目
   - Situation: 项目背景
   - Task: 你的任务
   - Action: 你采取的行动
   - Result: 项目成果

2. 如何处理团队中的技术分歧？
3. 遇到的技术难题如何解决？
4. 为什么想离开现在的公司？

文化匹配问题：
1. 你如何看待加班？
2. 你的职业规划是什么？
3. 为什么选择我们公司？

薪资问题：
- 当前薪资结构
- 期望薪资（建议涨幅20-30%）

### 建议提问面试官的问题

职位相关问题：
1. 该职位的核心挑战是什么？
2. 团队目前的技术栈和架构是怎样的？
3. 新人入职后会有哪些培训和指导？

团队和项目问题：
4. 团队目前有多少人？如何协作？
5. 正在进行的项目有哪些？我在其中会负责什么？
6. 团队的技术氛围如何？有技术分享吗？

公司战略问题：
7. 公司未来1-3年的技术发展方向？
8. 该业务在公司整体战略中的位置？

员工发展问题：
9. 晋升机制是怎样的？考核标准是什么？
10. 团队成员的平均职业发展路径？
11. 有哪些学习和成长的机会？

### 面试策略

突出优势：
1. 强调5年Python后端经验
2. 详细介绍性能优化项目案例
3. 展示对技术栈的深入理解

弥补短板：
1. 对Kafka和K8s说明学习计划
2. 强调快速学习能力（如之前学习FastAPI）

展示文化契合：
1. 表达对技术的热情
2. 分享技术博客或开源项目
3. 询问团队技术活动

注意事项：
- 准备充分的算法题（LeetCode中等题）
- 带着问题去面试（显示主动性）
- 展示谦逊好学的态度
- 不要过度夸大，保持诚实

## 五、最终建议

综合评估：★★★★☆ 强烈建议接受

该职位与你的技能匹配度高（85分），职业发展空间大，薪资有竞争力。虽然存在加班和技能单一化的风险，但通过合理规划可以规避。

建议：
✓ 接受该offer
✓ 入职后3个月内掌握Kafka和K8s
✓ 保持学习习惯，定期更新技能
✓ 1年后评估职业发展情况

祝你面试成功！🎯
    """

    sources = [
        "https://www.kanzhun.com/pl/example1",
        "https://www.jobui.com/company/example2"
    ]

    output_path = "tests/test_report.html"

    try:
        result = generator.generate_html_report(
            culture_text,
            match_text,
            sources,
            output_path
        )
        print(f"✓ 报告生成成功")
        print(f"  输出路径: {result}")
        print(f"  文件大小: {os.path.getsize(result)} 字节")

        # 尝试打开报告
        if os.path.exists(result):
            print(f"  ✓ 文件已创建")
            # 在Windows上打开
            os.startfile(result)
        else:
            print(f"  ✗ 文件未找到")

        return True
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_analyzer():
    """测试AI分析模块（需要API Key）"""
    print("\n" + "=" * 60)
    print("测试3: AI分析模块（需要API Key）")
    print("=" * 60)

    # 检查环境变量
    if not os.environ.get("ZHIPU_API_KEY"):
        print("⚠ 未设置ZHIPU_API_KEY环境变量，跳过AI测试")
        print("  提示: 设置环境变量后再运行此测试")
        return None

    try:
        from ai_analyzer import AIAnalyzer

        analyzer = AIAnalyzer(model="glm-4.6")

        # 测试公司文化分析
        print("  测试公司文化分析...")
        test_reviews = """
        这家公司技术氛围很好，同事们都很友好。
        工作环境：开放式办公，设施现代化
        面试流程：一共三轮，包括技术面试和HR面试。
        薪资福利：待遇不错，有五险一金。
        """

        culture_result = analyzer.analyze_company_culture(test_reviews)
        print(f"  ✓ 公司文化分析成功")
        print(f"  输出长度: {len(culture_result)} 字符")

        return True

    except Exception as e:
        print(f"✗ AI分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    setup_logging()

    print("\n" + "=" * 60)
    print("公司文化及职位解析工具 - 系统测试")
    print("=" * 60)

    results = {
        "简历解析模块": test_resume_parser(),
        "报告生成模块": test_report_generator(),
        "AI分析模块": test_ai_analyzer()
    }

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for module, result in results.items():
        if result is True:
            status = "✓ 通过"
        elif result is False:
            status = "✗ 失败"
        else:
            status = "⚠ 跳过"

        print(f"{status} - {module}")

    # 统计
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")

    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
