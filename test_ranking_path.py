"""
测试 batch_processor.generate_ranking_report() 的路径查找逻辑
"""
from pathlib import Path
from batch_processor import BatchProcessor

def test_path_finding():
    """测试提示词文件路径查找"""
    print("=" * 60)
    print("测试提示词文件路径查找逻辑")
    print("=" * 60)

    processor = BatchProcessor()

    # 创建测试输出目录
    test_output = Path("test_output_path")
    test_output.mkdir(exist_ok=True)

    # 创建模拟的公司报告文件
    for company in ["公司A", "公司B"]:
        report_file = test_output / f"{company}.html"
        report_file.write_text(f"<html><body>这是{company}的报告</body></html>", encoding='utf-8')

    try:
        # 调用 generate_ranking_report
        # 这个方法内部会尝试查找 prompts2/综合评估与排名.txt
        processor.generate_ranking_report(test_output, test_output / "排名.html")

        print("\n[SUCCESS] 提示词文件查找成功！")
        print(f"排名报告已生成: {test_output / '排名.html'}")

    except FileNotFoundError as e:
        print(f"\n[ERROR] 提示词文件未找到")
        print(f"错误信息: {str(e)}")

        # 检查是否有详细错误日志
        log_dir = Path("logs2")
        if log_dir.exists():
            log_files = list(log_dir.glob("path_error_*.txt"))
            if log_files:
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                print(f"\n详细错误日志: {latest_log}")
                print("\n日志内容:")
                print("-" * 60)
                print(latest_log.read_text(encoding='utf-8'))

    except Exception as e:
        print(f"\n[ERROR] 其他错误: {type(e).__name__}")
        print(f"错误信息: {str(e)}")

    finally:
        # 清理测试文件
        import shutil
        if test_output.exists():
            shutil.rmtree(test_output)
            print(f"\n已清理测试目录: {test_output}")

    print("=" * 60)

if __name__ == "__main__":
    test_path_finding()
