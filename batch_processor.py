"""
批量处理模块 - 批量处理多个公司的职位分析
"""
import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Callable

# 导入原有工具的模块
from mhtml_reader import MHTMLReader
from ai_analyzer import AIAnalyzer
from resume_parser import ResumeParser
from report_generator import ReportGenerator

# 导入新模块
from ai_client import AIClient
from ranking_report_generator import RankingReportGenerator


class BatchProcessor:
    """批量处理器"""

    def __init__(self, progress_callback: Callable = None):
        """
        初始化批量处理器

        Args:
            progress_callback: 进度回调函数，签名为 callback(message, current, total)
        """
        self.progress_callback = progress_callback

        # 初始化各个模块
        self.mhtml_reader = MHTMLReader()
        self.ai_analyzer = AIAnalyzer()
        self.resume_parser = ResumeParser()
        self.report_generator = ReportGenerator()
        self.ai_client = AIClient()
        self.ranking_generator = RankingReportGenerator()

        # 存储处理结果
        self.company_reports = []  # List of (company_name, report_path, jd_path)

    def _update_progress(self, message: str, current: int, total: int):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(message, current, total)

    def _read_jd_file(self, jd_path: Path) -> str:
        """
        读取职位描述文件

        Args:
            jd_path: JD文件路径

        Returns:
            JD文本内容
        """
        try:
            with open(jd_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试GBK编码
            with open(jd_path, 'r', encoding='gbk') as f:
                return f.read()

    def _find_mhtml_files(self, company_dir: Path) -> List[Path]:
        """
        查找公司目录中的所有MHTML文件

        Args:
            company_dir: 公司目录路径

        Returns:
            MHTML文件列表
        """
        mhtml_files = []

        # 查找.mhtml和.htm文件
        for pattern in ['*.mhtml', '*.MHTML', '*.htm', '*.HTM', '*.html', '*.HTML']:
            mhtml_files.extend(company_dir.glob(pattern))

        return mhtml_files

    def process_company(self, company_dir: Path, resume_content: str, output_dir: Path) -> Tuple[str, Path]:
        """
        处理单个公司

        Args:
            company_dir: 公司目录路径
            resume_content: 简历内容
            output_dir: 输出目录

        Returns:
            (公司名, 报告文件路径)
        """
        company_name = company_dir.name

        # 读取JD文件
        jd_file = company_dir / "jd.txt"
        if not jd_file.exists():
            raise FileNotFoundError(f"{company_dir} 中未找到 jd.txt 文件")

        jd_content = self._read_jd_file(jd_file)

        # 查找所有MHTML文件
        mhtml_files = self._find_mhtml_files(company_dir)
        if not mhtml_files:
            raise ValueError(f"{company_dir} 中未找到任何MHTML/HTML文件")

        # 合并所有MHTML文件的内容
        all_reviews = []
        for mhtml_file in mhtml_files:
            result = self.mhtml_reader.read_mhtml_file(str(mhtml_file))
            if result.get('content'):
                all_reviews.append(result['content'])

        if not all_reviews:
            raise ValueError(f"{company_dir} 的MHTML文件未能提取到有效内容")

        # 使用原有的AI分析流程
        # 1. 分析公司文化
        culture_analysis = self.ai_analyzer.analyze_company_culture(
            '\n\n'.join(all_reviews)
        )

        # 2. 分析职位匹配
        position_analysis = self.ai_analyzer.analyze_position_match(
            culture_analysis,
            jd_content,
            resume_content
        )

        # 生成报告
        report_filename = f"{company_name}.html"
        report_path = output_dir / report_filename

        # 提取数据来源(从MHTML文件中获取URL)
        sources = []
        for mhtml_file in mhtml_files:
            result = self.mhtml_reader.read_mhtml_file(str(mhtml_file))
            if result.get('url'):
                sources.append(result['url'])

        # 将JD内容也传递给报告生成器
        self.report_generator.generate_html_report(
            culture_analysis,
            position_analysis,
            sources,
            str(report_path),
            company_name,
            jd_content=jd_content  # 新增参数
        )

        # 存储公司报告、JD路径
        jd_path = company_dir / "jd.txt"
        return company_name, report_path, jd_path

    def generate_ranking_report(self, reports_dir: Path, output_path: Path):
        """
        生成综合排名报告

        Args:
            reports_dir: 各公司报告目录
            output_path: 排名报告输出路径
        """
        import inspect
        import os
        import sys

        # 如果company_reports还没有数据（直接调用generate_ranking_report的情况），从reports_dir读取
        if not self.company_reports:
            for report_file in reports_dir.glob('*.html'):
                company_name = report_file.stem
                # 尝试查找对应的JD文件
                # 假设原始公司目录结构与reports_dir在同一父目录下
                jd_path = None
                # 尝试在可能的原始位置查找JD
                possible_original_locations = [
                    reports_dir.parent / "companies" / company_name / "jd.txt",
                    reports_dir.parent / company_name / "jd.txt",
                ]
                for loc in possible_original_locations:
                    if loc.exists():
                        jd_path = loc
                        break

                self.company_reports.append((company_name, report_file, jd_path))

        if not self.company_reports:
            raise ValueError("没有找到任何公司报告，无法生成排名")

        # 读取所有报告内容
        all_reports_text = ""
        for company_name, report_path, _ in self.company_reports:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 只提取body中的文本内容（简化处理）
                all_reports_text += f"\n\n# {company_name} 分析报告\n\n"
                all_reports_text += content[:5000] + "...\n"  # 截取前5000字符避免太长

        # 读取提示词 - 添加详细日志和路径处理
        current_dir = Path(os.getcwd())
        script_dir = Path(inspect.getfile(self.__class__)).parent

        # 尝试多个可能的路径
        possible_paths = [
            Path("prompts2/综合评估与排名.txt"),  # 当前目录
            script_dir / "prompts2" / "综合评估与排名.txt",  # 脚本目录
            Path(__file__).parent / "prompts2" / "综合评估与排名.txt",  # __file__所在目录
        ]

        # 如果是打包的EXE，尝试sys._MEIPASS路径
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            possible_paths.append(exe_dir / "prompts2" / "综合评估与排名.txt")
            # PyInstaller打包后，数据在_MEIPASS临时目录
            if hasattr(sys, '_MEIPASS'):
                meipass_dir = Path(sys._MEIPASS)
                possible_paths.append(meipass_dir / "prompts2" / "综合评估与排名.txt")

        prompt_file = None
        for path in possible_paths:
            if path.exists():
                prompt_file = path
                break

        # 如果还是找不到，记录详细错误信息
        if not prompt_file:
            error_details = f"未找到提示词文件 prompts2/综合评估与排名.txt\n\n"
            error_details += f"当前工作目录: {current_dir}\n"
            error_details += f"脚本所在目录: {script_dir}\n"
            error_details += f"尝试过的路径:\n"
            for p in possible_paths:
                error_details += f"  - {p} (存在: {p.exists()})\n"
            error_details += f"\n请确保 prompts2/综合评估与排名.txt 文件存在于程序运行目录中。"

            # 将错误信息写入日志文件
            try:
                log_dir = Path("logs2")
                log_dir.mkdir(exist_ok=True)
                error_log = log_dir / f"path_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write(error_details)
            except:
                pass

            raise FileNotFoundError(error_details)

        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()

        # 构建用户输入
        user_input = f"以下是{len(self.company_reports)}家公司的详细分析报告，请进行综合评估和排名：\n\n{all_reports_text}"

        # 调用AI生成排名
        ai_response = self.ai_client.call(user_input, system_prompt)

        # 生成HTML报告
        self.ranking_generator.generate_report(
            ai_response,
            output_path,
            self.company_reports
        )

        return output_path

    def process_all_companies(self, companies_root_dir: Path, resume_path: Path, output_dir: Path, use_cache: bool = True):
        """
        批量处理所有公司

        Args:
            companies_root_dir: 公司资料根目录（包含多个公司子目录）
            resume_path: 简历文件路径
            output_dir: 报告输出目录
            use_cache: 是否使用缓存(跳过已存在的报告)
        """
        # 读取简历
        if not resume_path.exists():
            raise FileNotFoundError(f"简历文件不存在: {resume_path}")

        resume_content = self.resume_parser.parse_resume(str(resume_path))

        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)

        # 查找所有公司子目录
        company_dirs = [d for d in companies_root_dir.iterdir() if d.is_dir()]

        if not company_dirs:
            raise ValueError(f"在 {companies_root_dir} 中未找到任何公司子目录")

        total = len(company_dirs)
        self.company_reports = []

        # 处理每个公司
        for idx, company_dir in enumerate(company_dirs, 1):
            company_name = company_dir.name
            report_file = output_dir / f"{company_name}.html"

            # 检查缓存
            jd_path = company_dir / "jd.txt"
            if use_cache and report_file.exists():
                self._update_progress(f"使用缓存: {company_name}", idx, total)
                self.company_reports.append((company_name, report_file, jd_path))
                continue

            self._update_progress(f"正在处理: {company_name}", idx, total)

            try:
                _, report_path, _ = self.process_company(
                    company_dir,
                    resume_content,
                    output_dir
                )
                self.company_reports.append((company_name, report_path, jd_path))
                self._update_progress(f"完成: {company_name}", idx, total)

            except Exception as e:
                self._update_progress(f"失败: {company_name} - {str(e)}", idx, total)
                # 继续处理下一个公司
                continue

        # 生成综合排名报告
        if self.company_reports:
            self._update_progress("正在生成综合排名报告...", total, total)
            ranking_report_path = output_dir / "公司推荐排名.html"
            self.generate_ranking_report(output_dir, ranking_report_path)
            self._update_progress("全部完成！", total, total)

            return ranking_report_path
        else:
            raise ValueError("没有成功处理任何公司")
