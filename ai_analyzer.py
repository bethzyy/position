"""
AI分析模块 - 使用GLM-4.6进行分析
"""
import os
import sys
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from anthropic import Anthropic


def get_resource_path(relative_path: str) -> Path:
    """
    获取资源文件的绝对路径（兼容EXE和Python脚本运行）

    Args:
        relative_path: 相对路径

    Returns:
        资源文件的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是EXE运行，资源文件在临时目录
        # PyInstaller会将--add-data指定的文件解压到sys._MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # 如果是Python脚本运行，使用脚本所在目录
        base_path = Path(__file__).parent

    return base_path / relative_path


class AIAnalyzer:
    """AI分析器 - 使用GLM-4.6模型"""

    def __init__(self, model: str = "glm-4.6"):
        """
        初始化AI分析器

        Args:
            model: 使用的模型名称
        """
        self.model = model
        self.client = None
        self.logger = self._setup_logger()
        self._init_client()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # 确保logs目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 文件处理器 - 记录所有调用详情
        log_file = log_dir / f"ai_calls_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器 - 只显示重要信息
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化器
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s\n'
            '调用元数据: %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _init_client(self):
        """初始化Anthropic兼容客户端"""
        # 从系统变量读取API Key
        api_key = os.environ.get("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError(
                "未找到ZHIPU_API_KEY环境变量。\n"
                "请设置系统变量: set ZHIPU_API_KEY=your-api-key"
            )

        # 使用Zhipu的Anthropic兼容接口
        self.client = Anthropic(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/anthropic"
        )

        self.logger.info(f"AI客户端初始化成功，使用模型: {self.model}")

    def _log_ai_call(self, prompt: str, input_text: str, response: str,
                     metadata: Optional[Dict] = None):
        """
        记录AI调用的完整信息

        Args:
            prompt: 使用的提示词
            input_text: 输入文本
            response: AI响应
            metadata: 额外的元数据
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "metadata": metadata or {},
            "prompt": prompt,
            "input_length": len(input_text),
            "input_preview": input_text[:500] + "..." if len(input_text) > 500 else input_text,
            "response_length": len(response),
            "response": response
        }

        # 以JSON格式记录详细信息
        self.logger.debug(f"\n{json.dumps(log_entry, ensure_ascii=False, indent=2)}")

    def analyze_company_culture(self, reviews_content: str) -> str:
        """
        分析公司文化

        Args:
            reviews_content: 员工评价内容

        Returns:
            分析结果
        """
        self.logger.info("开始分析公司文化")

        # 读取提示词模板
        prompt_file = get_resource_path("prompts/company_culture_analysis.txt")
        self.logger.debug(f"提示词文件路径: {prompt_file}")
        if not prompt_file.exists():
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        # 构建完整提示词
        prompt = prompt_template.replace("{reviews_content}", reviews_content)

        # 限制输入长度（避免超过token限制）
        max_input_length = 15000  # 约合10000 tokens
        if len(prompt) > max_input_length:
            # 截断reviews_content部分
            template_length = len(prompt_template)
            available_length = max_input_length - template_length
            reviews_content = reviews_content[:available_length]
            prompt = prompt_template.replace("{reviews_content}", reviews_content)
            self.logger.warning(f"输入内容过长，已截断至 {max_input_length} 字符")

        try:
            # 调用AI
            start_time = datetime.now()
            message = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            end_time = datetime.now()

            # 提取响应
            response = message.content[0].text

            # 记录调用详情
            metadata = {
                "analysis_type": "company_culture",
                "duration_seconds": (end_time - start_time).total_seconds(),
                "input_tokens": message.usage.input_tokens if hasattr(message, 'usage') else 'N/A',
                "output_tokens": message.usage.output_tokens if hasattr(message, 'usage') else 'N/A'
            }
            self._log_ai_call(prompt_template, reviews_content, response, metadata)

            self.logger.info(f"公司文化分析完成，输出长度: {len(response)} 字符")
            return response

        except Exception as e:
            self.logger.error(f"公司文化分析失败: {e}", exc_info=True)
            raise

    def analyze_position_match(self, company_culture: str,
                               job_description: str,
                               resume_content: str) -> str:
        """
        分析职位匹配度

        Args:
            company_culture: 公司文化分析结果
            job_description: 职位描述
            resume_content: 简历内容

        Returns:
            匹配度分析结果
        """
        self.logger.info("开始分析职位匹配度")

        # 读取提示词模板
        prompt_file = get_resource_path("prompts/position_match_analysis.txt")
        self.logger.debug(f"提示词文件路径: {prompt_file}")
        if not prompt_file.exists():
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        # 构建完整提示词
        prompt = prompt_template.replace("{company_culture}", company_culture)
        prompt = prompt.replace("{job_description}", job_description)
        prompt = prompt.replace("{resume_content}", resume_content)

        # 限制各部分长度
        max_section_length = 8000  # 每部分最多8000字符

        if len(company_culture) > max_section_length:
            company_culture = company_culture[:max_section_length]
            self.logger.warning("公司文化内容过长，已截断")

        if len(job_description) > max_section_length:
            job_description = job_description[:max_section_length]
            self.logger.warning("职位描述过长，已截断")

        if len(resume_content) > max_section_length:
            resume_content = resume_content[:max_section_length]
            self.logger.warning("简历内容过长，已截断")

        # 重新构建提示词
        prompt = prompt_template.replace("{company_culture}", company_culture)
        prompt = prompt.replace("{job_description}", job_description)
        prompt = prompt.replace("{resume_content}", resume_content)

        # 检查总长度
        max_total_length = 20000  # 约合14000 tokens
        if len(prompt) > max_total_length:
            # 按比例缩减
            scale = max_total_length / len(prompt)
            company_culture = company_culture[:int(len(company_culture) * scale)]
            job_description = job_description[:int(len(job_description) * scale)]
            resume_content = resume_content[:int(len(resume_content) * scale)]
            prompt = prompt_template.replace("{company_culture}", company_culture)
            prompt = prompt.replace("{job_description}", job_description)
            prompt = prompt.replace("{resume_content}", resume_content)
            self.logger.warning(f"总输入过长，已按比例缩减至 {max_total_length} 字符")

        try:
            # 调用AI
            start_time = datetime.now()
            message = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            end_time = datetime.now()

            # 提取响应
            response = message.content[0].text

            # 记录调用详情
            metadata = {
                "analysis_type": "position_match",
                "duration_seconds": (end_time - start_time).total_seconds(),
                "company_culture_length": len(company_culture),
                "jd_length": len(job_description),
                "resume_length": len(resume_content),
                "input_tokens": message.usage.input_tokens if hasattr(message, 'usage') else 'N/A',
                "output_tokens": message.usage.output_tokens if hasattr(message, 'usage') else 'N/A'
            }
            self._log_ai_call(prompt_template, f"公司文化({len(company_culture)}字) + JD({len(job_description)}字) + 简历({len(resume_content)}字)", response, metadata)

            self.logger.info(f"职位匹配分析完成，输出长度: {len(response)} 字符")
            return response

        except Exception as e:
            self.logger.error(f"职位匹配分析失败: {e}", exc_info=True)
            raise


def test_analyzer():
    """测试函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    analyzer = AIAnalyzer()

    # 测试公司文化分析
    test_reviews = """
    这是一家很棒的公司！同事都很友好，工作氛围很好。
    加班情况：偶尔需要加班，但不是很频繁。
    面试流程：一共三轮，包括技术面和HR面。
    """

    try:
        result = analyzer.analyze_company_culture(test_reviews)
        print("公司文化分析结果:")
        print(result)
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_analyzer()
