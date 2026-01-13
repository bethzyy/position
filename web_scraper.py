"""
网页抓取模块 - 支持动态内容加载
"""
import time
import random
import logging
from typing import List, Dict
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class WebScraper:
    """网页抓取器 - 支持动态加载内容"""

    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        初始化网页抓取器

        Args:
            headless: 是否使用无头模式
            timeout: 默认超时时间（秒）
        """
        self.timeout = timeout
        self.driver = None
        self.logger = logging.getLogger(__name__)  # 先初始化logger
        self._setup_driver(headless)  # 再调用_setup_driver

    def _setup_driver(self, headless: bool):
        """配置Chrome驱动"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            self.logger.info("Chrome驱动初始化成功")
        except Exception as e:
            self.logger.error(f"Chrome驱动初始化失败: {e}")
            raise

    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        抓取单个URL的所有内容（包括动态加载）

        Args:
            url: 目标网址

        Returns:
            包含标题、内容和时间戳的字典
        """
        self.logger.info(f"开始抓取URL: {url}")
        self.logger.debug(f"当前headless模式: {self.driver}")
        result = {
            'url': url,
            'title': '',
            'content': '',
            'timestamp': datetime.now().isoformat(),
            'error': None
        }

        try:
            # 访问页面
            self.logger.debug(f"正在访问页面: {url}")
            self.driver.get(url)
            self.logger.info(f"页面加载完成: {self.driver.title}")

            # 等待初始内容加载
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

            # 获取页面标题
            result['title'] = self.driver.title

            # 滚动加载所有内容
            content = self._scroll_and_collect()

            result['content'] = content
            self.logger.info(f"成功抓取内容，长度: {len(content)} 字符")

        except TimeoutException:
            error_msg = f"页面加载超时: {url}"
            self.logger.error(error_msg)
            result['error'] = error_msg
        except Exception as e:
            error_msg = f"抓取失败: {str(e)}"
            self.logger.error(error_msg)
            result['error'] = error_msg

        return result

    def _scroll_and_collect(self) -> str:
        """
        滚动页面并收集所有内容（模拟人工下拉）

        Returns:
            完整的页面文本内容
        """
        last_height = 0
        max_scroll_attempts = 100  # 最多滚动100次
        scroll_attempts = 0
        no_change_count = 0  # 连续没有变化的次数
        max_no_change = 3  # 允许连续3次没有变化

        self.logger.info("开始滚动加载动态内容（模拟人工下拉）")

        while scroll_attempts < max_scroll_attempts:
            # 模拟人工滚动：分多次小幅度滚动，而不是直接滚到底部
            current_scroll_position = self.driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")
            page_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")

            # 计算每次滚动的距离（视口高度的0.5-1倍，模拟人工）
            scroll_distance = int(viewport_height * (0.5 + (scroll_attempts % 3) * 0.2))

            # 计算新的滚动位置
            new_position = min(current_scroll_position + scroll_distance, page_height)

            self.logger.debug(f"滚动: {current_scroll_position} -> {new_position} (距离: {scroll_distance}px)")

            # 执行平滑滚动（模拟人工行为）
            self.driver.execute_script(f"""
                window.scrollTo({{
                    top: {new_position},
                    behavior: 'smooth'
                }});
            """)

            # 等待滚动完成和新内容加载
            # 模拟人工阅读速度：随机1-3秒
            wait_time = random.uniform(1.0, 3.0)
            time.sleep(wait_time)

            # 获取新的页面高度
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # 检查是否到达页面底部
            current_position = self.driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")
            at_bottom = (current_position + viewport_height) >= page_height - 50

            # 检查页面高度是否增长
            height_changed = new_height != last_height

            if height_changed:
                no_change_count = 0  # 重置计数器
                last_height = new_height
                self.logger.debug(f"页面高度增长: {new_height}px")
            else:
                no_change_count += 1
                self.logger.debug(f"页面高度未变化 ({no_change_count}/{max_no_change})")

            # 判断是否停止滚动
            if at_bottom and no_change_count >= max_no_change:
                self.logger.info(f"已到达页面底部且无新内容加载，停止滚动（共{scroll_attempts}次）")
                break

            if no_change_count >= max_no_change * 2:
                self.logger.info(f"连续{no_change_count}次无新内容，停止滚动")
                break

            scroll_attempts += 1

        if scroll_attempts >= max_scroll_attempts:
            self.logger.warning(f"达到最大滚动次数限制({max_scroll_attempts}次)，停止滚动")

        self.logger.info(f"滚动完成，总共滚动 {scroll_attempts} 次")

        # 提取所有可见文本
        try:
            # 尝试多种方式提取内容
            content_parts = []

            # 方式1: 提取body文本
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if body_text:
                    content_parts.append(body_text)
            except:
                pass

            # 方式2: 提取常见评论容器
            common_selectors = [
                "//div[@class='review-item']",
                "//div[@class='comment']",
                "//div[@class='feedback']",
                "//div[contains(@class, 'review')]",
                "//div[contains(@class, 'comment')]",
                "//article",
                "//div[@itemprop='review']"
            ]

            for selector in common_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        self.logger.info(f"通过选择器 {selector} 找到 {len(elements)} 个元素")
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 10:  # 过滤掉太短的内容
                                content_parts.append(text)
                except Exception as e:
                    self.logger.debug(f"选择器 {selector} 提取失败: {e}")
                    continue

            # 合并所有内容，去重
            if content_parts:
                # 使用第一个（最完整的）作为主要内容
                unique_content = content_parts[0]
                # 如果有其他内容，追加到后面
                for part in content_parts[1:]:
                    if part not in unique_content:
                        unique_content += "\n\n" + part
                return unique_content
            else:
                self.logger.warning("未能提取到内容，返回body文本")
                return self.driver.find_element(By.TAG_NAME, "body").text

        except Exception as e:
            self.logger.error(f"提取内容时出错: {e}")
            # 返回整个页面的文本
            return self.driver.find_element(By.TAG_NAME, "body").text

    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        批量抓取多个URL

        Args:
            urls: URL列表

        Returns:
            抓取结果列表
        """
        results = []
        total = len(urls)

        self.logger.info(f"开始批量抓取 {total} 个URL")
        self.logger.debug(f"URL列表: {urls}")

        for idx, url in enumerate(urls, 1):
            self.logger.info(f"进度: {idx}/{total} - 开始抓取: {url}")
            try:
                result = self.scrape_url(url)
                results.append(result)

                if result['error']:
                    self.logger.warning(f"抓取失败: {url} - {result['error']}")
                else:
                    self.logger.info(f"抓取成功: {url} - 内容长度: {len(result['content'])} 字符")
            except Exception as e:
                self.logger.error(f"抓取异常: {url} - {str(e)}", exc_info=True)
                results.append({
                    'url': url,
                    'title': '',
                    'content': '',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })

            # 避免请求过快
            if idx < total:
                self.logger.debug("等待3秒后继续...")
                time.sleep(3)

        success_count = sum(1 for r in results if r['error'] is None)
        self.logger.info(f"批量抓取完成: 成功 {success_count}/{total}")

        return results

    def close(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Chrome驱动已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()


def test_scraper():
    """测试函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试单个URL
    test_url = "https://www.zhipin.com/"  # 只是一个示例

    with WebScraper(headless=False) as scraper:
        result = scraper.scrape_url(test_url)
        print(f"标题: {result['title']}")
        print(f"内容长度: {len(result['content'])}")
        if result['error']:
            print(f"错误: {result['error']}")


if __name__ == "__main__":
    test_scraper()
