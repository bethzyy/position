"""
MHTML文件读取模块
MHTML (MIME HTML) 是浏览器保存网页的格式，包含HTML和所有资源
"""
import logging
import re
import base64
from pathlib import Path
from typing import List, Dict
from html.parser import HTMLParser
from quopri import decodestring as decode_quopri


class MHTMLReader:
    """MHTML文件读取器"""

    def __init__(self):
        """初始化MHTML读取器"""
        self.logger = logging.getLogger(__name__)

    def read_mhtml_file(self, file_path: str) -> Dict[str, str]:
        """
        读取MHTML文件并提取内容

        Args:
            file_path: MHTML文件路径

        Returns:
            包含标题和内容的字典
        """
        self.logger.info(f"开始读取MHTML文件: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 解析MHTML内容
            result = self._parse_mhtml(content)

            self.logger.info(f"MHTML文件读取成功，内容长度: {len(result['content'])} 字符")
            return result

        except Exception as e:
            self.logger.error(f"读取MHTML文件失败: {e}")
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                    content = f.read()
                result = self._parse_mhtml(content)
                self.logger.info(f"使用GBK编码读取成功")
                return result
            except Exception as e2:
                self.logger.error(f"使用GBK编码也失败: {e2}")
                return {
                    'url': file_path,
                    'title': Path(file_path).stem,
                    'content': '',
                    'error': str(e)
                }

    def _parse_mhtml(self, content: str) -> Dict[str, str]:
        """
        解析MHTML内容

        Args:
            content: MHTML文件内容

        Returns:
            包含标题和正文的字典
        """
        # MHTML格式通常以Content-Type开头
        # 多个部分用boundary分隔

        # 提取主要内容（HTML部分）
        html_content = self._extract_html_content(content)

        # 提取标题
        title = self._extract_title(html_content)

        # 提取正文文本
        text_content = self._extract_text_from_html(html_content)

        # 提取URL
        url = self._extract_url(content)

        return {
            'url': url,
            'title': title,
            'content': text_content,
            'error': None
        }

    def _extract_html_content(self, mhtml_content: str) -> str:
        """
        从MHTML内容中提取HTML部分

        Args:
            mhtml_content: MHTML原始内容

        Returns:
            HTML内容
        """
        # 检测是否为quoted-printable编码
        is_quopri = 'Content-Transfer-Encoding: quoted-printable' in mhtml_content

        # 查找HTML部分（通常Content-Type: text/html）
        lines = mhtml_content.split('\n')

        in_html_section = False
        html_lines = []

        for line in lines:
            # 检测HTML部分开始
            if 'Content-Type: text/html' in line or 'content-type:text/html' in line:
                in_html_section = True
                continue

            # 检测新的部分开始（结束HTML部分）
            if in_html_section and line.startswith('--'):
                # 检查下一行是否有Content-Type
                if 'Content-Type:' in lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else '':
                    break

            if in_html_section:
                html_lines.append(line)

        html_content = '\n'.join(html_lines)

        # 如果是quoted-printable编码，进行解码
        if is_quopri and html_content:
            try:
                # quoted-printable解码
                decoded_bytes = decode_quopri(html_content.encode('utf-8'))
                html_content = decoded_bytes.decode('utf-8')
            except Exception as e:
                self.logger.warning(f"quoted-printable解码失败: {e}")

        # 如果没有找到明确的HTML部分，尝试直接提取
        if not html_content.strip():
            # 移除MHTML头部
            html_content = re.sub(
                r'Content-Type: multipart/related[^;]*; boundary="([^"]+)"',
                '',
                mhtml_content,
                flags=re.IGNORECASE
            )
            # 移除boundary标记
            html_content = re.sub(r'--[^\n]+', '', html_content)
            # 移除Content-Type头部
            html_content = re.sub(
                r'Content-Type: [^\n]+\n?',
                '',
                html_content,
                flags=re.IGNORECASE
            )
            # 移除Content-Transfer-Encoding
            html_content = re.sub(
                r'Content-Transfer-Encoding: [^\n]+\n?',
                '',
                html_content,
                flags=re.IGNORECASE
            )
            # 移除Content-Location
            html_content = re.sub(
                r'Content-Location: [^\n]+\n?',
                '',
                html_content,
                flags=re.IGNORECASE
            )

        return html_content.strip()

    def _extract_title(self, html_content: str) -> str:
        """
        从HTML中提取标题

        Args:
            html_content: HTML内容

        Returns:
            页面标题
        """
        # 提取<title>标签内容
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # 解码HTML实体
            title = self._decode_html_entities(title)
            return title

        # 尝试从<h1>标签提取
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            return self._decode_html_entities(h1_match.group(1).strip())

        return "未知标题"

    def _extract_url(self, mhtml_content: str) -> str:
        """
        从MHTML中提取原始URL

        Args:
            mhtml_content: MHTML原始内容

        Returns:
            URL字符串
        """
        # 查找Content-Location
        url_match = re.search(
            r'Content-Location:\s*(https?://[^\s\n]+)',
            mhtml_content,
            re.IGNORECASE
        )
        if url_match:
            return url_match.group(1)

        # 查找Subject（邮件格式的MHTML可能包含）
        subject_match = re.search(
            r'Subject:\s*(.+)',
            mhtml_content,
            re.IGNORECASE
        )
        if subject_match:
            return subject_match.group(1).strip()

        return "未知来源"

    def _extract_text_from_html(self, html_content: str) -> str:
        """
        从HTML中提取纯文本内容

        Args:
            html_content: HTML内容

        Returns:
            纯文本内容
        """
        # 移除<script>标签及其内容
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

        # 移除<style>标签及其内容
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

        # 移除HTML注释
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

        # 替换常见标签为换行
        html_content = re.sub(r'</div>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<br[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</li>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</tr>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</td>', '\t', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</th>', '\t', html_content, flags=re.IGNORECASE)

        # 移除所有HTML标签
        html_content = re.sub(r'<[^>]+>', '', html_content)

        # 解码HTML实体
        html_content = self._decode_html_entities(html_content)

        # 清理多余的空白和换行
        lines = html_content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # 跳过空行
                cleaned_lines.append(line)

        # 重新组合，但保留段落分隔
        text = '\n'.join(cleaned_lines)

        # 移除过多的连续空行
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _decode_html_entities(self, text: str) -> str:
        """
        解码HTML实体

        Args:
            text: 包含HTML实体的文本

        Returns:
            解码后的文本
        """
        # 常见HTML实体
        entities = {
            '&nbsp;': ' ',
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&apos;': "'",
            '&copy;': '©',
            '&reg;': '®',
            '&mdash;': '—',
            '&ndash;': '–',
            '…': '...',
            '&hellip;': '...'
        }

        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)

        # 数字实体 &#1234; 和 &#x1F600;
        def decode_numeric_entity(match):
            char_code = match.group(1)
            if char_code.startswith('x'):
                return chr(int(char_code[1:], 16))
            else:
                return chr(int(char_code))

        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)

        return text

    def read_multiple_mhtml_files(self, file_paths: List[str]) -> List[Dict[str, str]]:
        """
        批量读取多个MHTML文件

        Args:
            file_paths: MHTML文件路径列表

        Returns:
            读取结果列表
        """
        results = []
        total = len(file_paths)

        self.logger.info(f"开始批量读取 {total} 个MHTML文件")

        for idx, file_path in enumerate(file_paths, 1):
            self.logger.info(f"进度: {idx}/{total} - {file_path}")
            try:
                result = self.read_mhtml_file(file_path)
                results.append(result)

                if result['error']:
                    self.logger.warning(f"读取失败: {file_path} - {result['error']}")
                else:
                    self.logger.info(f"读取成功: {file_path} - 内容长度: {len(result['content'])} 字符")

            except Exception as e:
                self.logger.error(f"读取异常: {file_path} - {str(e)}")
                results.append({
                    'url': file_path,
                    'title': Path(file_path).stem,
                    'content': '',
                    'error': str(e)
                })

        success_count = sum(1 for r in results if r['error'] is None)
        self.logger.info(f"批量读取完成: 成功 {success_count}/{total}")

        return results


# 测试函数
def test_mhtml_reader():
    """测试MHTML读取器"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    reader = MHTMLReader()

    # 测试单个文件
    test_file = "tests/sample.mhtml"

    if Path(test_file).exists():
        print(f"\n测试读取文件: {test_file}")
        result = reader.read_mhtml_file(test_file)

        print(f"标题: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"内容长度: {len(result['content'])} 字符")
        print(f"\n内容预览:")
        print("=" * 60)
        print(result['content'][:500])
        print("=" * 60)
    else:
        print(f"测试文件不存在: {test_file}")
        print("\n请在浏览器中保存网页为MHTML格式，然后放到tests/目录下进行测试")


if __name__ == "__main__":
    test_mhtml_reader()
