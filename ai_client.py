"""
AI客户端模块 - 使用Anthropic兼容接口调用智谱AI GLM-4.7
"""
import os
import time
import json
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic


class AIClient:
    """AI客户端，使用Anthropic兼容接口"""

    def __init__(self, log_dir="logs2"):
        """
        初始化AI客户端

        Args:
            log_dir: 日志目录
        """
        # 从环境变量读取API密钥
        self.api_key = os.environ.get("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("未找到环境变量ZHIPU_API_KEY，请先设置该变量")

        # 初始化Anthropic客户端（连接到智谱AI的兼容接口）
        self.client = Anthropic(
            api_key=self.api_key,
            base_url="https://open.bigmodel.cn/api/anthropic"
        )

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 模型配置
        self.model = "glm-4.7"

    def _log_ai_call(self, prompt: str, response: str, metadata: dict):
        """
        记录AI调用的完整日志

        Args:
            prompt: 提示词
            response: AI响应
            metadata: 元数据（token使用、耗时等）
        """
        log_file = self.log_dir / f"ai_calls_{datetime.now().strftime('%Y%m%d')}.log"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "prompt": prompt,
            "response": response,
            "metadata": metadata
        }

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")
            f.write("=" * 80 + "\n\n")

    def call(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用AI模型

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）

        Returns:
            AI响应文本
        """
        start_time = time.time()

        # 构建消息
        messages = [{"role": "user", "content": prompt}]

        try:
            # 调用Anthropic兼容接口
            if system_prompt:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    system=system_prompt,
                    messages=messages
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    messages=messages
                )

            # 提取响应文本
            response_text = response.content[0].text

            # 计算耗时
            duration = time.time() - start_time

            # 记录日志
            metadata = {
                "duration_seconds": round(duration, 2),
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }

            self._log_ai_call(prompt, response_text, metadata)

            return response_text

        except Exception as e:
            # 记录错误日志
            error_metadata = {
                "duration_seconds": round(time.time() - start_time, 2),
                "error": str(e),
                "error_type": type(e).__name__
            }
            self._log_ai_call(prompt, f"ERROR: {str(e)}", error_metadata)
            raise
