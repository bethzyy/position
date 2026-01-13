"""
公司文化及职位解析工具 - GUI主程序
"""
import os
import sys
import json
import logging
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
from typing import List, Optional

from ai_analyzer import AIAnalyzer
from resume_parser import ResumeParser
from report_generator import ReportGenerator
from mhtml_reader import MHTMLReader


class PositionAnalysisTool:
    """职位分析工具GUI"""

    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("公司文化及职位解析工具")
        self.root.geometry("900x700")

        # 配置文件路径 - 使用绝对路径，确保EXE运行时能找到
        if getattr(sys, 'frozen', False):
            # 如果是EXE运行，使用EXE所在目录
            application_path = Path(sys.executable).parent
        else:
            # 如果是Python脚本运行，使用脚本所在目录
            application_path = Path(__file__).parent

        self.config_file = application_path / "config.json"

        # 初始化组件
        self.scraper = None
        self.analyzer = None
        self.parser = ResumeParser()
        self.generator = ReportGenerator()

        # 设置日志
        self._setup_logging()
        self.logger.info(f"配置文件路径: {self.config_file}")
        self.logger.info(f"配置文件存在: {self.config_file.exists()}")

        # 加载上次的配置
        self.config = self._load_config()

        # 创建GUI
        self._create_gui()

        self.logger.info("程序启动成功")

    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            'mhtml_folder': '',
            'resume_path': '',
            'job_description': '',
            'output_path': 'output/分析报告.html'
        }

        self.logger.info(f"正在加载配置文件: {self.config_file}")

        if self.config_file.exists():
            try:
                self.logger.info("配置文件存在，开始读取...")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.info(f"读取到的配置: {config}")
                    # 合并默认配置，确保所有字段都存在
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                            self.logger.warning(f"配置缺少字段 '{key}'，使用默认值")
                    self.logger.info("配置加载成功")
                    return config
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}，使用默认配置", exc_info=True)
        else:
            self.logger.warning("配置文件不存在，使用默认配置")

        return default_config

    def _save_config(self):
        """保存配置文件"""
        try:
            self.logger.info(f"正在保存配置到: {self.config_file}")
            self.logger.debug(f"保存的配置内容: {self.config}")
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}", exc_info=True)

    def _create_gui(self):
        """创建GUI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # 改为3，因为去掉了标题

        # 1. MHTML文件夹选择
        source_frame = ttk.LabelFrame(main_frame, text="数据来源（MHTML文件）", padding="5")
        source_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)
        source_frame.columnconfigure(0, weight=1)

        self.mhtml_folder_var = tk.StringVar(value=self.config.get('mhtml_folder', ''))
        mhtml_entry = ttk.Entry(source_frame, textvariable=self.mhtml_folder_var)
        mhtml_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        mhtml_browse_btn = ttk.Button(
            source_frame,
            text="选择文件夹",
            command=self._browse_mhtml_folder
        )
        mhtml_browse_btn.grid(row=0, column=1)

        self.mhtml_count_label = ttk.Label(source_frame, text="", foreground="gray")
        self.mhtml_count_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        # 2. 简历文件选择
        resume_frame = ttk.LabelFrame(main_frame, text="简历文件", padding="10")
        resume_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        resume_frame.columnconfigure(0, weight=1)

        self.resume_path_var = tk.StringVar(value=self.config.get('resume_path', ''))
        resume_entry = ttk.Entry(resume_frame, textvariable=self.resume_path_var)
        resume_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        resume_browse_btn = ttk.Button(
            resume_frame,
            text="浏览...",
            command=self._browse_resume
        )
        resume_browse_btn.grid(row=0, column=1)

        # 3. 职位描述
        jd_frame = ttk.LabelFrame(main_frame, text="职位描述（JD）", padding="10")
        jd_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        jd_frame.columnconfigure(0, weight=1)

        self.jd_text = scrolledtext.ScrolledText(
            jd_frame,
            height=6,
            wrap=tk.WORD
        )
        self.jd_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.jd_text.insert('1.0', self.config.get('job_description', ''))

        # 4. 输出文件路径
        output_frame = ttk.LabelFrame(main_frame, text="输出报告路径", padding="10")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)

        self.output_path_var = tk.StringVar(value=self.config.get('output_path', 'output/分析报告.html'))
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        output_browse_btn = ttk.Button(
            output_frame,
            text="浏览...",
            command=self._browse_output
        )
        output_browse_btn.grid(row=0, column=1)

        # 5. 日志输出（增大空间）
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,  # 减少高度到12行
            wrap=tk.WORD,
            state='disabled'
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 6. 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, pady=10)

        self.analyze_btn = ttk.Button(
            button_frame,
            text="开始分析",
            command=self._start_analysis
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame,
            text="清空日志",
            command=self._clear_log
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate'
        )
        self.progress.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

    def _append_log(self, message: str):
        """追加日志"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()

    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

    def _browse_resume(self):
        """浏览简历文件"""
        filename = filedialog.askopenfilename(
            title="选择简历文件",
            filetypes=[
                ("所有支持的格式", "*.pdf *.doc *.docx *.txt"),
                ("PDF文件", "*.pdf"),
                ("Word文件", "*.doc *.docx"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.resume_path_var.set(filename)

    def _browse_output(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存分析报告",
            defaultextension=".html",
            filetypes=[
                ("HTML文件", "*.html"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.output_path_var.set(filename)

    def _browse_mhtml_folder(self):
        """浏览MHTML文件夹"""
        folder_path = filedialog.askdirectory(
            title="选择包含MHTML文件的文件夹"
        )
        if folder_path:
            self.mhtml_folder_var.set(folder_path)

            # 扫描文件夹中的所有MHTML文件
            try:
                folder = Path(folder_path)
                mhtml_files = list(folder.glob("*.mhtml")) + list(folder.glob("*.mht"))

                count = len(mhtml_files)
                if count == 0:
                    self.mhtml_count_label.config(
                        text=f"该文件夹下没有找到MHTML文件",
                        foreground="orange"
                    )
                elif count == 1:
                    self.mhtml_count_label.config(
                        text=f"找到 1 个MHTML文件",
                        foreground="green"
                    )
                else:
                    self.mhtml_count_label.config(
                        text=f"找到 {count} 个MHTML文件",
                        foreground="green"
                    )

                # 记录日志
                self.logger.info(f"选择的文件夹: {folder_path}")
                self.logger.info(f"找到 {count} 个MHTML文件")
                if count > 0:
                    self.logger.info(f"文件列表: {[f.name for f in mhtml_files]}")

            except Exception as e:
                self.mhtml_count_label.config(
                    text=f"读取文件夹失败: {str(e)}",
                    foreground="red"
                )
                self.logger.error(f"读取文件夹失败: {e}")

    def _save_current_config(self):
        """保存当前配置"""
        self.config['mhtml_folder'] = self.mhtml_folder_var.get()
        self.config['resume_path'] = self.resume_path_var.get()
        self.config['job_description'] = self.jd_text.get('1.0', tk.END).strip()
        self.config['output_path'] = self.output_path_var.get()
        self._save_config()

    def _start_analysis(self):
        """开始分析"""
        # 保存当前配置
        self._save_current_config()

        # 验证MHTML文件夹
        mhtml_folder = self.mhtml_folder_var.get().strip()

        if not mhtml_folder:
            messagebox.showwarning("警告", "请选择包含MHTML文件的文件夹")
            return

        # 验证文件夹是否存在
        if not os.path.exists(mhtml_folder):
            messagebox.showwarning("警告", f"文件夹不存在: {mhtml_folder}")
            return

        # 扫描文件夹中的MHTML文件
        folder = Path(mhtml_folder)
        mhtml_files = list(folder.glob("*.mhtml")) + list(folder.glob("*.mht"))

        if not mhtml_files:
            messagebox.showwarning("警告", f"文件夹中没有找到MHTML文件\n支持的格式: .mhtml, .mht")
            return

        resume_path = self.resume_path_var.get()
        if not resume_path or not os.path.exists(resume_path):
            messagebox.showwarning("警告", "请选择有效的简历文件")
            return

        jd_text = self.jd_text.get('1.0', tk.END).strip()
        if not jd_text:
            messagebox.showwarning("警告", "请输入职位描述")
            return

        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showwarning("警告", "请指定输出路径")
            return

        # 在新线程中运行分析
        self.analyze_btn.config(state='disabled')
        self.progress.start()

        thread = threading.Thread(
            target=self._run_analysis,
            args=(mhtml_folder, resume_path, jd_text, output_path)
        )
        thread.daemon = True
        thread.start()

    def _run_analysis(self, mhtml_folder: str, resume_path: str, jd_text: str, output_path: str):
        """运行分析（在后台线程中）"""
        try:
            self._append_log("=" * 60)
            self._append_log("开始分析流程")
            self._append_log(f"数据源: MHTML文件夹（{mhtml_folder}）")
            self._append_log(f"简历: {resume_path}, JD长度: {len(jd_text)}字符")
            self._append_log("=" * 60)

            # 步骤1: 获取网页内容
            self._append_log("\n[1/4] 获取网页内容...")
            self._append_log(f"  初始化MHTMLReader...")
            try:
                mhtml_reader = MHTMLReader()
                self._append_log(f"  ✓ MHTMLReader初始化成功")
            except Exception as e:
                self._append_log(f"  ✗ MHTMLReader初始化失败: {str(e)}")
                raise

            # 读取MHTML文件
            # 扫描文件夹中的所有MHTML文件
            folder = Path(mhtml_folder)
            mhtml_files = list(folder.glob("*.mhtml")) + list(folder.glob("*.mht"))

            self._append_log(f"  在文件夹中找到 {len(mhtml_files)} 个MHTML文件")
            for f in mhtml_files:
                self._append_log(f"    - {f.name}")

            self._append_log(f"  开始读取 {len(mhtml_files)} 个MHTML文件...")

            all_reviews = []
            successful_files = []
            for mhtml_file in mhtml_files:
                try:
                    result = mhtml_reader.read_mhtml_file(str(mhtml_file))
                    if result and result.get('content'):
                        all_reviews.append(result['content'])
                        successful_files.append(mhtml_file.name)
                        self._append_log(f"  ✓ {mhtml_file.name}: 成功读取 {len(result['content'])} 字符")
                    else:
                        self._append_log(f"  ✗ {mhtml_file.name}: 读取失败（内容为空）")
                except Exception as e:
                    self._append_log(f"  ✗ {mhtml_file.name}: 读取失败 - {str(e)}")

            if not all_reviews:
                self._append_log(f"  ✗ 所有MHTML文件读取失败")
                raise Exception("无法读取任何MHTML文件")

            self._append_log(f"  总共读取 {len(all_reviews)} 个文件，合计 {sum(len(r) for r in all_reviews)} 字符")

            # 合并所有内容
            reviews_text = '\n\n'.join(all_reviews)
            # 步骤2: 分析公司文化
            self._append_log("\n[2/4] 分析公司文化（AI分析中，请稍候）...")
            self._append_log(f"  初始化AIAnalyzer...")
            try:
                analyzer = AIAnalyzer(model="glm-4.7")  # 使用GLM-4.7
                self._append_log(f"  ✓ AIAnalyzer初始化成功")
            except Exception as e:
                self._append_log(f"  ✗ AIAnalyzer初始化失败: {str(e)}")
                self._append_log(f"  提示: 请检查ZHIPU_API_KEY环境变量是否已设置")
                raise

            self._append_log(f"  开始调用GLM-4.6分析...")
            culture_analysis = analyzer.analyze_company_culture(reviews_text)
            self._append_log(f"  ✓ 公司文化分析完成，输出 {len(culture_analysis)} 字符")

            # 步骤3: 解析简历
            self._append_log("\n[3/4] 解析简历...")
            self._append_log(f"  解析文件: {resume_path}")
            try:
                resume_content = self.parser.parse_resume(resume_path)
                self._append_log(f"  ✓ 简历解析完成，共 {len(resume_content)} 字符")
            except Exception as e:
                self._append_log(f"  ✗ 简历解析失败: {str(e)}")
                raise

            # 步骤4: 分析职位匹配度
            self._append_log("\n[4/4] 分析职位匹配度（AI分析中，请稍候）...")
            self._append_log(f"  开始调用GLM-4.6分析...")
            try:
                match_analysis = analyzer.analyze_position_match(
                    culture_analysis,
                    jd_text,
                    resume_content
                )
                self._append_log(f"  ✓ 职位匹配分析完成，输出 {len(match_analysis)} 字符")
            except Exception as e:
                self._append_log(f"  ✗ 职位匹配分析失败: {str(e)}")
                raise

            # 步骤5: 生成HTML报告
            self._append_log("\n生成HTML报告...")
            self._append_log(f"  输出路径: {output_path}")
            try:
                self.generator.generate_html_report(
                    culture_analysis,
                    match_analysis,
                    successful_files,  # 使用文件名而不是URLs
                    output_path
                )
                self._append_log(f"  ✓ 报告已保存: {output_path}")
            except Exception as e:
                self._append_log(f"  ✗ 报告生成失败: {str(e)}")
                raise

            # 完成
            self._append_log("\n" + "=" * 60)
            self._append_log("✓ 分析完成！")
            self._append_log("=" * 60)

            # 在主线程中显示成功消息
            self.root.after(0, lambda: messagebox.showinfo(
                "成功",
                f"分析完成！\n报告已保存到:\n{output_path}"
            ))

            # 自动打开报告
            self.root.after(0, lambda: os.startfile(output_path))

        except Exception as e:
            error_msg = f"分析失败: {str(e)}"
            self._append_log(f"\n✗ {error_msg}")
            self.logger.error(error_msg, exc_info=True)

            # 在主线程中显示错误消息
            self.root.after(0, lambda: messagebox.showerror(
                "错误",
                error_msg
            ))

        finally:
            # 停止进度条，恢复按钮
            self.root.after(0, self._analysis_finished)

    def _analysis_finished(self):
        """分析完成后的清理工作"""
        self.progress.stop()
        self.analyze_btn.config(state='normal')


def main():
    """主函数"""
    root = tk.Tk()
    app = PositionAnalysisTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
