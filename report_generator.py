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
                            output_path: str,
                            company_name: str = "目标公司",
                            jd_content: str = None) -> str:
        """
        生成完整的HTML分析报告

        Args:
            company_culture_analysis: 公司文化分析结果
            position_match_analysis: 职位匹配分析结果
            sources: 数据来源URL列表
            output_path: 输出文件路径
            company_name: 公司名称
            jd_content: 职位描述内容(可选)

        Returns:
            生成的HTML文件路径
        """
        self.logger.info(f"开始生成HTML报告: {output_path}, 公司名称: {company_name}")

        # 转换Markdown为HTML（简单处理）
        culture_html = self._markdown_to_html(company_culture_analysis)
        match_html = self._markdown_to_html(position_match_analysis)

        # 生成完整HTML
        html_content = self._generate_html_template(
            culture_html,
            match_html,
            sources,
            company_name,
            jd_content  # 传递JD内容
        )

        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"HTML报告生成成功: {output_file}")
        return str(output_file)

    def _detect_and_generate_chart(self, text: str) -> tuple:
        """
        检测文本中的比例数据并生成图表

        Args:
            text: 要检测的文本

        Returns:
            (处理后的文本, 图表HTML列表)
        """
        import re
        charts = []
        processed_lines = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检测包含比例数据的行
            # 匹配模式: "XX%的...认为/表示/提到..." 或 "约XX%、XX%的..."
            percentage_pattern = r'(\d+(?:\.\d+)?)%\s*(?:的|約|约)?\s*([\u4e00-\u9fa5]+)(?:认为|表示|提到|觉得|反馈|反映)'
            matches = re.findall(percentage_pattern, line)

            if len(matches) >= 2 or (len(matches) == 1 and re.search(r'(\d+(?:\.\d+)?)%.*?(\d+(?:\.\d+)?)%', line)):
                # 提取所有百分比和对应的标签
                all_percentages = re.findall(r'(\d+(?:\.\d+)?)%\s*(?:的|約|约)?\s*([\u4e00-\u9fa5]+)', line)

                if len(all_percentages) >= 2:
                    # 构建图表数据
                    chart_data = []
                    total = 0
                    for pct, label in all_percentages:
                        total += float(pct)
                        chart_data.append({'label': label, 'value': float(pct)})

                    # 如果总和在80-120之间,认为是有效的比例数据
                    if 80 <= total <= 120:
                        chart_html = self._generate_pie_chart(chart_data, line.strip()[:50])
                        charts.append(chart_html)
                        processed_lines.append(f'[图表{len(charts)}] {line}')
                        i += 1
                        continue

            processed_lines.append(line)
            i += 1

        return ('\n'.join(processed_lines), charts)

    def _generate_pie_chart(self, data: list, title: str) -> str:
        """
        生成饼图HTML

        Args:
            data: 图表数据,格式为 [{'label': '标签', 'value': 30}, ...]
            title: 图表标题

        Returns:
            饼图HTML字符串
        """
        import math

        # 预定义颜色方案
        colors = [
            '#667eea', '#764ba2', '#f093fb', '#4facfe',
            '#43e97b', '#fa709a', '#fee140', '#30cfd0',
            '#a8edea', '#fed6e3', '#ff9a9e', '#fecfef'
        ]

        # 计算总和并标准化
        total = sum(item['value'] for item in data)
        if total == 0:
            return ''

        # 生成饼图的SVG
        svg_lines = []
        start_angle = 0

        for idx, item in enumerate(data):
            percentage = (item['value'] / total) * 100
            angle = (item['value'] / total) * 360

            # 计算扇形的路径
            if angle >= 360:
                # 完整的圆
                path_d = f'M 100 100 m -85 0 a 85 85 0 1 0 170 0 a 85 85 0 1 0 -170 0'
            else:
                # 部分扇形
                end_angle = start_angle + angle

                # 转换为弧度
                start_rad = math.radians(start_angle - 90)
                end_rad = math.radians(end_angle - 90)

                # 计算起点和终点坐标
                x1 = 100 + 85 * math.cos(start_rad)
                y1 = 100 + 85 * math.sin(start_rad)
                x2 = 100 + 85 * math.cos(end_rad)
                y2 = 100 + 85 * math.sin(end_rad)

                # 大弧标志
                large_arc = 1 if angle > 180 else 0

                path_d = f'M 100 100 L {x1:.1f} {y1:.1f} A 85 85 0 {large_arc} 1 {x2:.1f} {y2:.1f} Z'

            color = colors[idx % len(colors)]
            svg_lines.append(f'<path d="{path_d}" fill="{color}" stroke="white" stroke-width="2"/>')

            start_angle += angle

        svg_content = '\n'.join(svg_lines)

        # 生成图例
        legend_items = []
        for idx, item in enumerate(data):
            color = colors[idx % len(colors)]
            percentage = (item['value'] / total) * 100
            legend_items.append(f'''
                <div class="legend-item">
                    <div class="legend-color" style="background-color: {color}"></div>
                    <span>{item['label']}: {percentage:.1f}%</span>
                </div>''')

        legend_html = ''.join(legend_items)

        chart_html = f'''
        <div class="chart-container">
            <div class="chart-title">📊 {title}</div>
            <div class="pie-chart">
                <svg width="200" height="200" viewBox="0 0 200 200">
                    {svg_content}
                </svg>
            </div>
            <div class="pie-legend">
                {legend_html}
            </div>
        </div>
        '''

        return chart_html

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown文本转换为HTML（改进版）

        Args:
            markdown_text: Markdown格式文本

        Returns:
            HTML格式文本
        """
        import re

        # 首先检测并生成图表
        processed_text, charts = self._detect_and_generate_chart(markdown_text)

        lines = processed_text.split('\n')
        result_lines = []
        in_ul = False
        in_ol = False
        in_p = False
        list_level = 0  # 列表层级

        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            original_line = line

            # 计算缩进级别
            indent_match = re.match(r'^(\s*)', line)
            indent_spaces = len(indent_match.group(1)) if indent_match else 0
            indent_level = min(indent_spaces // 2, 3)  # 最多3级缩进

            # 去除缩进进行处理
            line = line.strip()

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
                    list_level = 0
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                    list_level = 0
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
                    list_level = 0
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                    list_level = 0
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
                    list_level = 0
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                    list_level = 0
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
                    list_level = 0
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                if not in_ul:
                    result_lines.append('<ul>')
                    in_ul = True
                    list_level = 0
                content = re.sub(r'^[-*]\s+', '', line)
                # 处理粗体
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                # 添加缩进class
                indent_class = f" indent-level-{indent_level}" if indent_level > 0 else ""
                result_lines.append(f"<li class=\"{indent_class}\">{content}</li>")

            # 有序列表 1. 2. 3. 等
            elif re.match(r'^\d+\.\s+(.+)$', line):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                    list_level = 0
                if in_p:
                    result_lines.append('</p>')
                    in_p = False
                if not in_ol:
                    result_lines.append('<ol>')
                    in_ol = True
                    list_level = 0
                content = re.sub(r'^\d+\.\s+', '', line)
                # 处理粗体
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                # 添加缩进class
                indent_class = f" indent-level-{indent_level}" if indent_level > 0 else ""
                result_lines.append(f"<li class=\"{indent_class}\">{content}</li>")

            # 普通段落
            else:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                    list_level = 0
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                    list_level = 0
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

        # 插入图表
        html_content = '\n'.join(result_lines)

        # 在检测到的位置插入图表
        for chart_html in charts:
            # 找到[图表N]标记并在其后插入图表
            html_content = html_content.replace(
                f'[图表{charts.index(chart_html) + 1}]',
                chart_html
            )

        return html_content

    def _generate_html_template(self,
                                culture_html: str,
                                match_html: str,
                                sources: list,
                                company_name: str = "目标公司",
                                jd_content: str = None) -> str:
        """
        生成完整的HTML模板

        Args:
            culture_html: 公司文化HTML
            match_html: 职位匹配HTML
            sources: 数据源列表
            company_name: 公司名称
            jd_content: 职位描述内容(可选)

        Returns:
            完整HTML文档
        """
        # 生成JD内容HTML
        jd_html = ""
        if jd_content:
            # 将JD内容中的换行符转换为HTML换行
            jd_display = jd_content.replace('\n', '<br>\n')
            jd_html = f'''
        <div class="section">
            <h2>📋 职位描述 (JD)</h2>
            <div class="jd-content">
                {jd_display}
            </div>
        </div>'''

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
    <title>{company_name} - 公司文化与职位匹配分析报告</title>
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

        /* JD内容样式 */
        .jd-content {{
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            padding: 25px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 5px solid #f59e0b;
            line-height: 1.9;
            color: #374151;
            font-size: 1.02em;
            white-space: pre-wrap;
            word-wrap: break-word;
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

        /* 图表容器样式 */
        .chart-container {{
            margin: 20px 0;
            padding: 20px;
            background: #f7fafc;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .chart-title {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.05em;
        }}

        .pie-chart {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 15px 0;
        }}

        .pie-legend {{
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 0.9em;
        }}

        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 8px;
        }}

        /* 缩进样式 - 用于层级内容 */
        .indent-level-1 {{
            margin-left: 20px;
        }}

        .indent-level-2 {{
            margin-left: 40px;
        }}

        .indent-level-3 {{
            margin-left: 60px;
        }}

        /* 列表的缩进优化 */
        ul li, ol li {{
            position: relative;
            padding-left: 8px;
        }}

        ul li::before {{
            content: "•";
            position: absolute;
            left: -15px;
            color: #667eea;
            font-weight: bold;
        }}

        ol li {{
            padding-left: 8px;
        }}

        /* 嵌套列表的缩进 */
        ul ul, ol ol, ul ol, ol ul {{
            margin-top: 8px;
            margin-bottom: 8px;
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
            <h1>🎯 {company_name} - 公司文化与职位匹配分析报告</h1>
            <div class="subtitle">AI驱动的职业发展决策支持</div>
            <div class="timestamp">生成时间: {current_time}</div>
        </div>

        <div class="content">
            <div class="section">
                <h1>第一部分：公司文化分析</h1>
                {culture_html}
                {sources_html}
            </div>

            {jd_html}

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
