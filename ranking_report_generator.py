"""
综合排名报告生成器
"""
import re
import os
from pathlib import Path


class RankingReportGenerator:
    """生成公司推荐排名HTML报告"""

    def __init__(self):
        """初始化报告生成器"""
        pass

    def markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown转换为HTML

        Args:
            markdown_text: Markdown文本

        Returns:
            HTML文本
        """
        lines = markdown_text.split('\n')
        html_lines = []
        in_list = False
        in_table = False

        i = 0
        while i < len(lines):
            line = lines[i].rstrip()

            # 跳过空行（在HTML中用<br>处理）
            if not line:
                if html_lines and html_lines[-1] != '<br>':
                    html_lines.append('<br>')
                i += 1
                continue

            # 处理标题
            if line.startswith('### '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h3>{line[4:]}</h3>')
                i += 1
                continue

            if line.startswith('## '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h2>{line[3:]}</h2>')
                i += 1
                continue

            if line.startswith('# '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h1>{line[2:]}</h1>')
                i += 1
                continue

            # 处理列表
            if line.startswith('- '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{self._process_inline(line[2:])}</li>')
                i += 1
                continue

            # 处理表格
            if line.startswith('|') and line.endswith('|'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False

                # 收集所有表格行
                table_lines = []
                while i < len(lines) and lines[i].startswith('|'):
                    table_lines.append(lines[i].rstrip())
                    i += 1

                # 生成表格HTML
                table_html = self._process_table(table_lines)
                html_lines.append(table_html)
                continue

            # 关闭列表
            if in_list:
                html_lines.append('</ul>')
                in_list = False

            # 处理普通段落
            html_lines.append(f'<p>{self._process_inline(line)}</p>')
            i += 1

        # 关闭未闭合的列表
        if in_list:
            html_lines.append('</ul>')

        # 移除多余的<br>标签（在标题、表格前后）
        result = '\n'.join(html_lines)
        result = re.sub(r'<br>\s*<(h[1-6]|table|ul)', r'<\1', result)
        result = re.sub(r'</(h[1-6]|table|ul)>\s*<br>', r'</\1>', result)

        return result

    def _process_inline(self, text: str) -> str:
        """处理行内元素（粗体等）"""
        # 处理粗体
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        return text

    def _process_table(self, lines: list) -> str:
        """处理Markdown表格"""
        if len(lines) < 2:
            return ''

        # 解析表头
        headers = [h.strip() for h in lines[0].split('|')[1:-1]]
        thead = '<thead><tr>' + ''.join([f'<th>{h}</th>' for h in headers]) + '</tr></thead>'

        # 解析表体（跳过分隔线）
        tbody = '<tbody>'
        for line in lines[2:]:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            processed_cells = [self._process_inline(c) for c in cells]
            tbody += '<tr>' + ''.join([f'<td>{c}</td>' for c in processed_cells]) + '</tr>'
        tbody += '</tbody>'

        return f'<table class="ranking-table">{thead}{tbody}</table>'

    def generate_report(self, ai_response: str, output_path: Path, company_reports: list):
        """
        生成完整的HTML报告

        Args:
            ai_response: AI生成的Markdown响应
            output_path: 输出文件路径
            company_reports: 公司报告列表，每个元素是 (公司名, 报告文件路径, JD路径) 元组
        """
        # 转换Markdown到HTML
        content_html = self.markdown_to_html(ai_response)

        # 创建公司名到路径的映射
        company_info = {}
        for item in company_reports:
            if len(item) == 3:
                company_name, report_path, jd_path = item
            else:
                company_name, report_path = item
                jd_path = None

            # 创建相对路径
            try:
                rel_report_path = Path(report_path).relative_to(output_path.parent)
            except ValueError:
                rel_report_path = Path(report_path).name

            # JD相对路径 - 更智能的查找
            rel_jd_path = None
            if jd_path and jd_path.exists():
                # 直接使用提供的JD路径
                try:
                    # 计算从output目录到JD文件的相对路径
                    # output_path在output_dir/公司推荐排名.html
                    # jd_path在companies_dir/公司名/jd.txt
                    rel_jd_path = Path(os.path.relpath(jd_path, output_path.parent))
                except ValueError:
                    # 如果无法计算相对路径，使用绝对路径
                    rel_jd_path = jd_path.resolve()
            else:
                # 如果没有提供JD路径或不存在，尝试在常见位置查找
                # 假设原始数据在以下位置之一：
                # 1. output_path.parent.parent / "companies" / company_name / "jd.txt"
                # 2. output_path.parent / company_name / "jd.txt"
                possible_locations = [
                    output_path.parent.parent / "companies" / company_name / "jd.txt",
                    output_path.parent / company_name / "jd.txt",
                    Path("companies") / company_name / "jd.txt",  # 相对路径
                ]

                for loc in possible_locations:
                    if loc.exists():
                        try:
                            rel_jd_path = Path(os.path.relpath(loc, output_path.parent))
                            break
                        except ValueError:
                            rel_jd_path = loc
                            break

            company_info[company_name] = {
                'report_path': rel_report_path,
                'jd_path': rel_jd_path
            }

        # 后处理HTML：添加超链接到表格
        content_html = self._add_links_to_table(content_html, company_info)

        # 完整的HTML模板（不包含底部的公司报告链接，因为表格里已经有了）
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公司推荐排名报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 40px;
        }}

        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }}

        h2 {{
            color: #764ba2;
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 5px solid #764ba2;
        }}

        h3 {{
            color: #555;
            font-size: 1.4em;
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        .ranking-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .ranking-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
        }}

        .ranking-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}

        .ranking-table tr:hover {{
            background-color: #f5f5f5;
        }}

        .ranking-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        .company-reports {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 8px;
            margin: 40px 0;
        }}

        .company-reports ul {{
            list-style: none;
            padding-left: 0;
        }}

        .company-reports li {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}

        .company-reports a {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1em;
        }}

        .company-reports a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        p {{
            margin: 15px 0;
            color: #333;
        }}

        strong {{
            color: #667eea;
            font-weight: bold;
        }}

        ul {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        .final-recommendation {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 25px;
            border-radius: 8px;
            margin: 30px 0;
            border-left: 5px solid #ff6b6b;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content_html}
    </div>
</body>
</html>"""

        # 保存HTML文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)

    def _add_links_to_table(self, html: str, company_info: dict) -> str:
        """
        为表格中的公司名称添加超链接，并添加JD链接列

        Args:
            html: HTML内容
            company_info: 公司信息字典 {公司名: {report_path, jd_path}}

        Returns:
            修改后的HTML
        """
        import re

        # 第一步：在表头添加"JD链接"列
        # 查找表头行，在"职位匹配度"后添加"JD链接"列
        html = re.sub(
            r'(<th>职位匹配度[^<]*</th>)',
            r'\1<th>JD链接</th>',
            html
        )

        # 第二步：处理tbody中的每一行
        def find_best_match(company_name_from_cell):
            """在company_info中找到最佳匹配的公司名"""
            # 精确匹配
            if company_name_from_cell in company_info:
                return company_name_from_cell

            # 尝试去除括号内容后匹配
            simplified = re.sub(r'\s*\(.*?\)\s*', '', company_name_from_cell).strip()
            if simplified in company_info:
                return simplified

            # 尝试部分匹配
            for key in company_info:
                if company_name_from_cell in key or key in company_name_from_cell:
                    return key

            return None

        # 分割HTML，处理tbody
        parts = html.split('<tbody>')
        if len(parts) < 2:
            return html

        header = parts[0]
        rest = parts[1]

        # 分割tbody和tbody结束标签
        tbody_parts = rest.split('</tbody>', 1)
        if len(tbody_parts) < 2:
            return html

        tbody_content = tbody_parts[0]
        footer = tbody_parts[1]

        # 处理每一行
        rows = []
        for line in tbody_content.split('<tr>'):
            if not line.strip() or line.strip().startswith('</tr>'):
                if line.strip():
                    rows.append(line)
                continue

            # 移除</tr>标签
            row_content = line.replace('</tr>', '').strip()

            # 提取公司名称（从第二个<td>中）
            cells = row_content.split('</td>')
            if len(cells) < 2:
                rows.append(line)
                continue

            # 第二个单元格是公司名称
            company_cell = cells[1]
            if '<td>' not in company_cell:
                rows.append(line)
                continue

            # 提取纯文本公司名
            company_name_match = re.search(r'<strong>(.+?)</strong>', company_cell)
            if company_name_match:
                company_name = company_name_match.group(1).strip()
            else:
                company_name_match = re.search(r'<td>(.+?)</td>', company_cell)
                if company_name_match:
                    company_name = company_name_match.group(1).strip()
                else:
                    rows.append(line)
                    continue

            # 查找匹配的公司信息
            matched_key = find_best_match(company_name)

            if matched_key and matched_key in company_info:
                info = company_info[matched_key]

                # 替换公司名称为超链接（如果还没有链接）
                if '<a href=' not in company_cell:
                    # 创建新的公司单元格（带超链接）
                    new_company_cell = company_cell.replace(
                        f'<strong>{company_name}</strong>',
                        f'<a href="{info["report_path"]}"><strong>{company_name}</strong></a>'
                    )
                    cells[1] = new_company_cell

                # 添加JD链接列
                if info['jd_path']:
                    jd_link = f'<td><a href="{info["jd_path"]}">查看JD</a></td>'
                else:
                    jd_link = '<td>-</td>'

                # 重新组合行
                row_content = '</td>'.join(cells) + jd_link
            else:
                # 没有找到匹配，添加空的JD列
                cells.append('-')
                row_content = '</td>'.join(cells)

            rows.append(f'<tr>{row_content}</tr>')

        # 重新组装HTML
        new_tbody = '<tbody>' + ''.join(rows) + '</tbody>'
        result = header + new_tbody + footer

        return result


