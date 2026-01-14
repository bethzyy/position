"""
批量处理工具 - 主GUI程序
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from datetime import datetime

from batch_processor import BatchProcessor


class BatchToolGUI:
    """批量处理工具GUI"""

    def __init__(self, root):
        """
        初始化GUI

        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("批量公司文化职位解析工具")
        self.root.geometry("900x650")

        # 配置文件
        self.config_file = Path("batch_config.json")
        self.config = self.load_config()

        # 批量处理器
        self.batch_processor = None
        self.processing_thread = None

        self.create_widgets()

    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        """保存配置"""
        import json
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 公司资料目录
        companies_frame = ttk.LabelFrame(main_frame, text="公司资料目录", padding="10")
        companies_frame.pack(fill=tk.X, pady=10)

        # 路径输入行
        path_row = ttk.Frame(companies_frame)
        path_row.pack(fill=tk.X, pady=5)

        self.companies_path_var = tk.StringVar(value=self.config.get('companies_dir', ''))
        companies_entry = ttk.Entry(path_row, textvariable=self.companies_path_var, width=70)
        companies_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        companies_button = ttk.Button(
            path_row,
            text="浏览...",
            command=self.browse_companies_dir
        )
        companies_button.pack(side=tk.LEFT)

        # 说明标签
        help_label = ttk.Label(
            companies_frame,
            text="说明: 该目录应包含多个公司子目录，每个子目录包含员工评价网页文件和jd.txt职位描述文件",
            font=("Microsoft YaHei", 9),
            foreground="gray",
            wraplength=850
        )
        help_label.pack(pady=5, anchor=tk.W)

        # 2. 简历文件
        resume_frame = ttk.LabelFrame(main_frame, text="简历文件", padding="10")
        resume_frame.pack(fill=tk.X, pady=10)

        self.resume_path_var = tk.StringVar(value=self.config.get('resume_path', ''))
        resume_entry = ttk.Entry(resume_frame, textvariable=self.resume_path_var, width=70)
        resume_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        resume_button = ttk.Button(
            resume_frame,
            text="浏览...",
            command=self.browse_resume
        )
        resume_button.pack(side=tk.LEFT)

        # 3. 输出目录
        output_frame = ttk.LabelFrame(main_frame, text="报告输出目录", padding="10")
        output_frame.pack(fill=tk.X, pady=10)

        self.output_path_var = tk.StringVar(value=self.config.get('output_dir', ''))
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=70)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        output_button = ttk.Button(
            output_frame,
            text="浏览...",
            command=self.browse_output_dir
        )
        output_button.pack(side=tk.LEFT)

        # 4. 缓存选项
        cache_frame = ttk.LabelFrame(main_frame, text="缓存设置", padding="10")
        cache_frame.pack(fill=tk.X, pady=10)

        self.use_cache_var = tk.BooleanVar(value=True)
        cache_checkbox = ttk.Checkbutton(
            cache_frame,
            text="使用缓存（如果某公司的报告已存在，跳过重新生成）",
            variable=self.use_cache_var
        )
        cache_checkbox.pack(anchor=tk.W)

        # 4. 进度显示
        progress_frame = ttk.LabelFrame(main_frame, text="处理进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=800
        )
        self.progress_bar.pack(pady=10)

        # 进度文本
        self.progress_text = tk.Text(
            progress_frame,
            height=15,
            width=100,
            font=("Consolas", 10)
        )
        self.progress_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.progress_text, command=self.progress_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_text.config(yscrollcommand=scrollbar.set)

        # 5. 按钮区
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        self.start_button = ttk.Button(
            button_frame,
            text="开始批量处理",
            command=self.start_processing,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = ttk.Button(
            button_frame,
            text="清空日志",
            command=self.clear_log,
            width=15
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_companies_dir(self):
        """浏览公司资料目录"""
        dir_path = filedialog.askdirectory(title="选择公司资料根目录")
        if dir_path:
            self.companies_path_var.set(dir_path)
            self.config['companies_dir'] = dir_path
            self.save_config()

    def browse_resume(self):
        """浏览简历文件"""
        file_path = filedialog.askopenfilename(
            title="选择简历文件",
            filetypes=[
                ("所有支持的格式", "*.pdf *.docx *.doc *.txt"),
                ("PDF文件", "*.pdf"),
                ("Word文档", "*.docx *.doc"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.resume_path_var.set(file_path)
            self.config['resume_path'] = file_path
            self.save_config()

    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择报告输出目录")
        if dir_path:
            self.output_path_var.set(dir_path)
            self.config['output_dir'] = dir_path
            self.save_config()

    def log_message(self, message: str):
        """记录日志消息"""
        self.progress_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.progress_text.see(tk.END)
        self.progress_text.update()

    def clear_log(self):
        """清空日志"""
        self.progress_text.delete(1.0, tk.END)

    def progress_callback(self, message: str, current: int, total: int):
        """进度回调函数"""
        # 更新进度条
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)

        # 更新状态栏
        self.status_var.set(f"{message} ({current}/{total})")

        # 记录日志
        self.log_message(message)

    def start_processing(self):
        """开始处理"""
        # 验证输入
        companies_dir = self.companies_path_var.get().strip()
        resume_path = self.resume_path_var.get().strip()
        output_dir = self.output_path_var.get().strip()

        if not companies_dir or not resume_path or not output_dir:
            messagebox.showerror("错误", "请填写完整的路径信息！")
            return

        if not Path(companies_dir).exists():
            messagebox.showerror("错误", f"公司资料目录不存在: {companies_dir}")
            return

        if not Path(resume_path).exists():
            messagebox.showerror("错误", f"简历文件不存在: {resume_path}")
            return

        # 检查缓存
        use_cache = self.use_cache_var.get()
        companies_to_regenerate = []

        if not use_cache:
            # 不使用缓存,检查是否有已存在的报告
            output_path = Path(output_dir)
            companies_root = Path(companies_dir)

            for company_dir in companies_root.iterdir():
                if company_dir.is_dir():
                    company_name = company_dir.name
                    report_file = output_path / f"{company_name}.html"

                    if report_file.exists():
                        companies_to_regenerate.append(company_name)

            # 如果有已存在的报告,询问用户
            if companies_to_regenerate:
                companies_list = "\n".join([f"- {name}" for name in companies_to_regenerate[:5]])
                if len(companies_to_regenerate) > 5:
                    companies_list += f"\n... 等 {len(companies_to_regenerate)} 个公司"

                message = f"检测到以下公司的报告已存在:\n\n{companies_list}\n\n是否删除并重新生成这些报告?"
                result = messagebox.askyesno(
                    "缓存检查",
                    message,
                    icon='question'
                )

                if not result:
                    # 用户选择不删除,使用缓存
                    use_cache = True

        # 禁用开始按钮
        self.start_button.config(state=tk.DISABLED)
        self.clear_log()

        # 在后台线程中执行处理
        self.processing_thread = threading.Thread(
            target=self.run_processing,
            args=(companies_dir, resume_path, output_dir, use_cache),
            daemon=True
        )
        self.processing_thread.start()

    def run_processing(self, companies_dir: str, resume_path: str, output_dir: str, use_cache: bool):
        """运行处理流程（在后台线程中）"""
        try:
            self.log_message("=" * 60)
            self.log_message("开始批量处理")
            self.log_message(f"公司资料目录: {companies_dir}")
            self.log_message(f"简历文件: {resume_path}")
            self.log_message(f"输出目录: {output_dir}")
            self.log_message(f"使用缓存: {'是' if use_cache else '否'}")
            self.log_message("=" * 60)

            # 创建批量处理器
            self.batch_processor = BatchProcessor(progress_callback=self.progress_callback)

            # 执行批量处理
            ranking_report = self.batch_processor.process_all_companies(
                Path(companies_dir),
                Path(resume_path),
                Path(output_dir),
                use_cache=use_cache
            )

            self.log_message("=" * 60)
            self.log_message(f"处理完成！")
            self.log_message(f"综合排名报告: {ranking_report}")
            self.log_message("=" * 60)

            # 询问是否打开报告
            self.root.after(0, lambda: self.ask_open_report(ranking_report))

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))

        finally:
            # 恢复开始按钮
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))

    def ask_open_report(self, report_path: Path):
        """询问是否打开报告"""
        result = messagebox.askyesno(
            "处理完成",
            f"批量处理已完成！\n\n综合排名报告已生成:\n{report_path}\n\n是否立即打开？"
        )

        if result:
            # 在默认浏览器中打开报告
            import webbrowser
            webbrowser.open(str(report_path.absolute()))


def main():
    """主函数"""
    root = tk.Tk()
    app = BatchToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
