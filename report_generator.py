"""
HTML报告生成模块
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict


class ReportGenerator:
    """HTML报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        self.logger = logging.getLogger(__name__)

    def generate_html_report(self,
                            company_culture_analysis: str,
                            position_match_analysis: str,
                            sources: list,
                            output_path: str) -> str:
        """
        生成完整的HTML分析报告

        Args:
            company_culture_analysis: 公司文化分析结果
            position_match_analysis: 职位匹配分析结果
            sources: 数据来源URL列表
            output_path: 输出文件路径

        Returns:
            生成的HTML文件路径
        """
        self.logger.info(f"开始生成HTML报告: {output_path}")

        # 转换Markdown为HTML（简单处理）
        culture_html = self._markdown_to_html(company_culture_analysis)
        match_html = self._markdown_to_html(position_match_analysis)

        # 生成完整HTML
        html_content = self._generate_html_template(
            culture_html,
            match_html,
            sources
        )

        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"HTML报告生成成功: {output_file}")
        return str(output_file)

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown文本转换为HTML（改进版）

        Args:
            markdown_text: Markdown格式文本

        Returns:
            HTML格式文本
        """
        import re

        lines = markdown_text.split('\n')
        result_lines = []
        in_ul = False
        in_ol = False
        in_p = False

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 空行处理
            if not line:
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                i += 1
                continue

            # 一级标题 #
            if re.match(r'^#\s+(.+)$', line):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                title = re.sub(r'^#\s+', '', line)
                result_lines.append(f"<h3>{title}</h3>")

            # 二级标题 ##
            elif re.match(r'^##\s+(.+)$', line):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                title = re.sub(r'^##\s+', '', line)
                result_lines.append(f"<h4>{title}</h4>")

            # 三级标题 ###
            elif re.match(r'^###\s+(.+)$', line):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                title = re.sub(r'^###\s+', '', line)
                result_lines.append(f"<h5>{title}</h5>")

            # 无序列表 - 或 *
            elif re.match(r'^[-*]\s+(.+)$', line):
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                if not in_ul:
                    result_lines.append('<ul>')
                    in_ul = True
                content = re.sub(r'^[-*]\s+', '', line)
                # 处理粗体
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                result_lines.append(f"<li>{content}</li>")

            # 有序列表 1. 2. 3. 等
            elif re.match(r'^\d+\.\s+(.+)$', line):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                if not in_ol:
                    result_lines.append('<ol>')
                    in_ol = True
                content = re.sub(r'^\d+\.\s+', '', line)
                # 处理粗体
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                result_lines.append(f"<li>{content}</li>")

            # 普通段落
            else:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if not in_p:
                    result_lines.append('<p>')
                    in_p = True
                # 处理粗体
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                result_lines.append(line + ' ')

            i += 1

        # 关闭未闭合的标签
        if in_ul:
            result_lines.append('</ul>')
        if in_ol:
            result_lines.append('</ol>')
        if in_p:
            result_lines.append('</p>')

        return '\n'.join(result_lines)

    def _generate_html_template(self,
                                culture_html: str,
                                match_html: str,
                                sources: list) -> str:
        """
        生成完整的HTML模板

        Args:
            culture_html: 公司文化HTML
            match_html: 职位匹配HTML
            sources: 数据源列表

        Returns:
            完整HTML文档
        """
        # 生成数据源HTML
        sources_html = ""
        if sources:
            sources_html = "<h3>数据来源</h3><ul>"
            for url in sources:
                sources_html += f"<li><a href='{url}' target='_blank'>{url}</a></li>"
            sources_html += "</ul>"

        # 当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公司文化与职位匹配分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #fafbfc;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 35px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .header .subtitle {{
            font-size: 1.05em;
            opacity: 0.95;
        }}

        .header .timestamp {{
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.85;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 45px;
        }}

        /* 大标题(报告部分标题) - 最醒目 */
        h1 {{
            color: #5a67d8;
            font-size: 1.9em;
            margin-bottom: 20px;
            padding: 12px 16px;
            background: linear-gradient(135deg, #eef2ff 0%, #f7fafc 100%);
            border-left: 6px solid #5a67d8;
            border-radius: 8px;
            font-weight: 700;
            box-shadow: 0 2px 4px rgba(90, 103, 216, 0.1);
        }}

        /* 二级标题(Markdown #) - 次醒目 */
        h2 {{
            color: #319795;
            font-size: 1.5em;
            margin: 28px 0 14px 0;
            padding: 10px 14px;
            background: linear-gradient(135deg, #e6fffa 0%, #f0fdf4 100%);
            border-left: 5px solid #319795;
            border-radius: 6px;
            font-weight: 600;
            box-shadow: 0 2px 3px rgba(49, 151, 149, 0.08);
        }}

        /* 三级标题(Markdown ##) - 中等醒目 */
        h3 {{
            color: #4a5568;
            font-size: 1.25em;
            margin: 20px 0 10px 0;
            padding: 8px 12px;
            background: #f7fafc;
            border-left: 4px solid #a0aec0;
            border-radius: 4px;
            font-weight: 600;
            box-shadow: 0 1px 2px rgba(160, 174, 192, 0.1);
        }}

        /* 四级标题(Markdown ###) - 小标题 */
        h4 {{
            color: #2d3748;
            font-size: 1.1em;
            margin: 16px 0 8px 0;
            padding: 6px 10px;
            background: #edf2f7;
            border-left: 3px solid #718096;
            border-radius: 3px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* 五级标题(Markdown ####) - 最小标题 */
        h5 {{
            color: #718096;
            font-size: 1.05em;
            margin: 12px 0 6px 0;
            font-weight: 600;
            border-bottom: 1px dashed #cbd5e0;
            padding-bottom: 4px;
        }}

        p {{
            margin: 12px 0;
            text-align: justify;
            color: #374151;
            line-height: 1.75;
        }}

        ul, ol {{
            margin: 12px 0 12px 30px;
            line-height: 1.8;
            color: #374151;
        }}

        li {{
            margin: 8px 0;
            color: #4b5563;
        }}

        strong {{
            color: #5a67d8;
            font-weight: 600;
        }}

        /* 评分和状态样式 - 柔和的渐变 */
        .score {{
            display: inline-block;
            background: linear-gradient(135deg, #68d391 0%, #38a169 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 16px;
            font-weight: 600;
            margin: 5px 0;
        }}

        /* 优势/劣势标记 - 更柔和的颜色 */
        .pros {{
            color: #38a169;
        }}

        .cons {{
            color: #e53e3e;
        }}

        /* 警告标记 - 柔和的橙色 */
        .warning {{
            color: #d69e2e;
        }}

        .sources {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            margin-top: 30px;
            border-left: 4px solid #cbd5e0;
        }}

        .sources h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            color: #4a5568;
            font-size: 1.1em;
        }}

        .sources ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .sources li {{
            margin: 8px 0;
        }}

        .sources a {{
            color: #5a67d8;
            text-decoration: none;
            word-break: break-all;
        }}

        .sources a:hover {{
            text-decoration: underline;
        }}

        .footer {{
            background: #f7fafc;
            padding: 20px;
            text-align: center;
            color: #718096;
            font-size: 0.9em;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}

        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}
            .header {{
                padding: 30px 20px;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 公司文化与职位匹配分析报告</h1>
            <div class="subtitle">AI驱动的职业发展决策支持</div>
            <div class="timestamp">生成时间: {current_time}</div>
        </div>

        <div class="content">
            <div class="section">
                <h1>第一部分：公司文化分析</h1>
                {culture_html}
                {sources_html}
            </div>

            <div class="section">
                <h1>第二部分：职位匹配分析与面试建议</h1>
                {match_html}
            </div>
        </div>

        <div class="footer">
            <p>本报告由AI自动生成，仅供参考。建议结合实际情况做出最终决策。</p>
            <p>🤖 Generated with Company Culture & Position Analysis Tool</p>
        </div>
    </div>
</body>
</html>"""

        return html_template


def test_report_generator():
    """测试函数"""
    generator = ReportGenerator()

    culture_text = """
# 公司文化分析报告

## 一、公司氛围
这是一家技术驱动型公司，工作氛围积极向上。

## 二、企业员工文化
注重员工发展，提供良好的福利。

## 三、面试流程
面试包括技术面和HR面。
    """

    match_text = """
# 职位匹配分析与面试建议

## 一、职位定位分析
这是一个核心开发岗位。

## 二、匹配度评估
综合匹配度良好。

## 三、面试准备清单
需要准备技术问题和行为面试问题。
    """

    sources = ["https://example.com/review1", "https://example.com/review2"]

    output = generator.generate_html_report(
        culture_text,
        match_text,
        sources,
        "output/test_report.html"
    )

    print(f"测试报告已生成: {output}")


if __name__ == "__main__":
    test_report_generator()
