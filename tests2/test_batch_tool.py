"""
批量处理工具测试程序
"""
import sys
import os
from pathlib import Path

# 添加父目录到Python路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from batch_processor import BatchProcessor


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("测试1: 基本功能测试")
    print("=" * 60)

    # 测试路径
    test_data_dir = Path(__file__).parent / "test_data"
    companies_dir = test_data_dir / "companies"
    resume_file = test_data_dir / "resume" / "test_resume.txt"
    output_dir = test_data_dir / "output"

    # 检查测试数据是否存在
    if not companies_dir.exists():
        print(f"[X] 失败: 测试数据目录不存在: {companies_dir}")
        return False

    if not resume_file.exists():
        print(f"[X] 失败: 测试简历不存在: {resume_file}")
        return False

    print(f"[OK] 公司目录: {companies_dir}")
    print(f"[OK] 简历文件: {resume_file}")
    print(f"[OK] 输出目录: {output_dir}")

    # 清空输出目录
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建进度回调
    def progress_callback(message, current, total):
        print(f"  [{current}/{total}] {message}")

    try:
        # 创建处理器
        processor = BatchProcessor(progress_callback=progress_callback)

        # 执行批量处理
        print("\n开始批量处理...")
        ranking_report = processor.process_all_companies(
            companies_dir,
            resume_file,
            output_dir
        )

        print(f"\n[OK] 成功生成排名报告: {ranking_report}")

        # 检查生成的文件
        company_reports = list(output_dir.glob("*.html"))
        if len(company_reports) < 2:
            print(f"[X] 失败: 生成的公司报告数量不足 ({len(company_reports)} < 2)")
            return False

        print(f"[OK] 生成了 {len(company_reports)} 个HTML文件")

        # 检查排名报告
        if not ranking_report.exists():
            print(f"[X] 失败: 排名报告未生成")
            return False

        print(f"[OK] 排名报告已生成")

        print("\n" + "=" * 60)
        print("[OK] 测试通过")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[X] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_client():
    """测试AI客户端"""
    print("\n" + "=" * 60)
    print("测试2: AI客户端测试")
    print("=" * 60)

    try:
        from ai_client import AIClient

        # 检查环境变量
        import os
        if not os.environ.get("ZHIPU_API_KEY"):
            print("[!] 跳过: 未设置ZHIPU_API_KEY环境变量")
            return True

        # 创建客户端
        client = AIClient()
        print("[OK] AI客户端初始化成功")

        # 测试简单调用
        print("\n测试AI调用...")
        response = client.call("请简单介绍你自己，不超过50字。")
        print(f"[OK] AI响应: {response[:100]}...")

        print("\n[OK] AI客户端测试通过")
        return True

    except Exception as e:
        print(f"[X] AI客户端测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_mhtml_reader():
    """测试MHTML读取器"""
    print("\n" + "=" * 60)
    print("测试3: MHTML读取器测试")
    print("=" * 60)

    try:
        from mhtml_reader import MHTMLReader

        reader = MHTMLReader()

        # 读取测试HTML文件
        test_html = Path(__file__).parent / "test_data" / "companies" / "公司A" / "reviews.html"

        if not test_html.exists():
            print(f"[X] 测试HTML文件不存在: {test_html}")
            return False

        result = reader.read_mhtml_file(str(test_html))

        if result.get('error'):
            print(f"[X] MHTML读取错误: {result['error']}")
            return False

        if not result.get('content'):
            print("[X] 未读取到内容")
            return False

        print(f"[OK] 成功读取内容，长度: {len(result['content'])} 字符")
        print(f"[OK] 内容预览: {result['content'][:100]}...")

        print("\n[OK] MHTML读取器测试通过")
        return True

    except Exception as e:
        print(f"[X] MHTML读取器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """测试依赖模块"""
    print("\n" + "=" * 60)
    print("测试4: 依赖模块检查")
    print("=" * 60)

    required_modules = [
        'tkinter',
        'anthropic',
        'PyPDF2',
        'docx',
        'pathlib',
        'json',
        'threading'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError:
            print(f"[X] {module} - 未安装")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n[X] 缺少模块: {', '.join(missing_modules)}")
        print("请运行: pip install " + " ".join(missing_modules))
        return False

    print("\n[OK] 所有依赖模块已安装")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "[TEST] " + "=" * 58)
    print("   批量处理工具 - 自动化测试套件")
    print("=" * 60)

    test_results = []

    # 测试1: 依赖检查
    test_results.append(("依赖模块检查", test_dependencies()))

    # 测试2: MHTML读取器
    test_results.append(("MHTML读取器", test_mhtml_reader()))

    # 测试3: AI客户端
    test_results.append(("AI客户端", test_ai_client()))

    # 测试4: 基本功能
    test_results.append(("基本功能", test_basic_functionality()))

    # 打印测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "[OK] 通过" if result else "[X] 失败"
        print(f"{test_name:20s}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("\n[SUCCESS] 所有测试通过！")
    else:
        print(f"\n[WARNING] 有 {failed} 个测试失败，请检查")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
