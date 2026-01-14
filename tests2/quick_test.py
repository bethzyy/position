"""
快速测试 - 验证关键方法调用
"""
import sys
from pathlib import Path

# 添加父目录到Python路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def test_method_signatures():
    """测试方法签名是否正确"""
    print("=" * 60)
    print("快速测试 - 方法签名验证")
    print("=" * 60)

    # 测试1: MHTMLReader
    try:
        from mhtml_reader import MHTMLReader
        reader = MHTMLReader()
        assert hasattr(reader, 'read_mhtml_file'), "MHTMLReader缺少read_mhtml_file方法"
        print("[OK] MHTMLReader.read_mhtml_file 存在")
    except Exception as e:
        print(f"[X] MHTMLReader测试失败: {e}")
        return False

    # 测试2: ReportGenerator
    try:
        from report_generator import ReportGenerator
        gen = ReportGenerator()
        assert hasattr(gen, 'generate_html_report'), "ReportGenerator缺少generate_html_report方法"
        print("[OK] ReportGenerator.generate_html_report 存在")
    except Exception as e:
        print(f"[X] ReportGenerator测试失败: {e}")
        return False

    # 测试3: AIAnalyzer
    try:
        from ai_analyzer import AIAnalyzer
        analyzer = AIAnalyzer()
        assert hasattr(analyzer, 'analyze_position_match'), "AIAnalyzer缺少analyze_position_match方法"
        print("[OK] AIAnalyzer.analyze_position_match 存在")
    except Exception as e:
        print(f"[X] AIAnalyzer测试失败: {e}")
        return False

    print("\n[SUCCESS] 所有关键方法签名验证通过")
    return True

if __name__ == "__main__":
    success = test_method_signatures()
    sys.exit(0 if success else 1)
