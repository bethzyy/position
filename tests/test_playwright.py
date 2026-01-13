"""
测试 Playwright 网页抓取
目标：测试抓取看准网公司详情页
"""
import asyncio
import logging
from playwright.async_api import async_playwright

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def scrape_zhaopin_company():
    """测试抓取智联旗下看准网的公司详情页"""
    target_url = "https://zq.zhaopin.com/companyDetail/CZ443657520"

    logger.info(f"开始测试抓取: {target_url}")

    async with async_playwright() as p:
        # 启动浏览器（使用Chrome，添加更多反爬参数）
        logger.info("启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口，便于观察
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                '--disable-infobars',
                '--disable-extensions',
                '--disable-gpu',
                '--start-maximized',
                '--disable-web-security',  # 允许跨域
                '--allow-running-insecure-content',
                '--ignore-certificate-errors'
                # 移除了 --user-data-dir，改用 persistent context
            ]
        )

        # 创建上下文（更接近真实用户，添加更多指纹信息）
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            geolocation={'latitude': 39.9042, 'longitude': 116.4074},  # 北京坐标
            permissions=['geolocation']
        )

        # 创建页面并注入脚本（隐藏webdriver特征）
        page = await context.new_page()

        # 注入反检测脚本
        await page.add_init_script("""
            // 覆盖navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆盖chrome对象
            window.chrome = {
                runtime: {}
            };

            // 覆盖permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        try:
            # 访问页面
            logger.info(f"正在访问: {target_url}")
            await page.goto(target_url, wait_until='domcontentloaded', timeout=30000)
            logger.info("页面加载完成")

            # 等待主要内容加载
            logger.info("等待内容加载...")
            await page.wait_for_timeout(3000)  # 额外等待3秒

            # 模拟人工操作：尝试点击"查看全部点评"或类似的展开按钮
            logger.info("\n尝试查找并点击展开按钮...")

            # 可能的按钮文本
            button_texts = [
                "查看全部点评",
                "查看全部",
                "展开全部",
                "更多点评",
                "查看更多",
                "全部评论",
                "展开"
            ]

            button_clicked = False
            for text in button_texts:
                try:
                    # 尝试通过文本查找按钮
                    button = await page.get_by_text(text, exact=True).first
                    if await button.is_visible():
                        logger.info(f"找到按钮: {text}")
                        # 模拟人工点击（缓慢移动）
                        await button.click(timeout=5000)
                        logger.info(f"成功点击: {text}")
                        button_clicked = True
                        await page.wait_for_timeout(2000)  # 等待内容展开
                        break
                except:
                    continue

            if not button_clicked:
                logger.warning("未找到展开按钮，尝试其他选择器...")

                # 尝试通过CSS选择器查找
                selectors = [
                    "button:has-text('查看')",
                    "a:has-text('查看')",
                    ".show-all",
                    ".expand-all",
                    "[class*='expand']",
                    "[class*='more']"
                ]

                for selector in selectors:
                    try:
                        button = await page.query_selector(selector)
                        if button:
                            text = await button.inner_text()
                            logger.info(f"找到按钮（选择器）: {selector} - {text}")
                            await button.click()
                            logger.info("成功点击")
                            button_clicked = True
                            await page.wait_for_timeout(2000)
                            break
                    except:
                        continue

            if not button_clicked:
                logger.warning("未找到任何展开按钮，继续提取当前可见内容")

            # 模拟人工鼠标移动（随机移动到页面不同位置）
            logger.info("\n模拟鼠标移动...")
            try:
                viewport_size = await page.viewport_size()
                for i in range(3):
                    # 随机坐标
                    x = random.randint(100, viewport_size['width'] - 100)
                    y = random.randint(100, viewport_size['height'] - 100)
                    await page.mouse.move(x, y)
                    await page.wait_for_timeout(random.randint(500, 1500))
                    logger.info(f"鼠标移动到: ({x}, {y})")
            except Exception as e:
                logger.warning(f"鼠标移动失败: {e}")

            # 尝试获取页面标题
            title = await page.title()
            logger.info(f"页面标题: {title}")

            # 尝试多种方式提取内容
            logger.info("\n开始提取内容...")

            # 方法1: 获取整个body文本
            body_text = await page.evaluate("() => document.body.innerText")
            logger.info(f"[方法1] Body文本长度: {len(body_text)} 字符")

            # 方法2: 获取特定区域（评论内容）
            try:
                # 等待评论区域加载
                await page.wait_for_selector('.review-item, .comment-item, .evaluation-item', timeout=5000)
                logger.info("找到评论区域")

                # 提取所有评论
                reviews = await page.evaluate("""
                    () => {
                        const items = document.querySelectorAll('.review-item, .comment-item, .evaluation-item');
                        return Array.from(items).map(item => item.innerText).join('\\n\\n');
                    }
                """)
                logger.info(f"[方法2] 评论内容长度: {len(reviews)} 字符")
                logger.info(f"评论预览:\n{reviews[:500]}...")
            except Exception as e:
                logger.warning(f"[方法2] 未找到评论区域: {e}")

            # 方法3: 滚动加载更多内容
            logger.info("\n开始滚动加载更多内容...")
            last_height = await page.evaluate("() => document.body.scrollHeight")

            for i in range(5):  # 最多滚动5次
                # 滚动到底部
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                logger.info(f"滚动 {i+1}/5")

                # 等待新内容加载
                await page.wait_for_timeout(2000)

                # 检查高度是否变化
                new_height = await page.evaluate("() => document.body.scrollHeight")
                if new_height == last_height:
                    logger.info("页面高度未变化，停止滚动")
                    break
                last_height = new_height

            # 获取最终内容
            final_content = await page.evaluate("() => document.body.innerText")
            logger.info(f"\n最终内容长度: {len(final_content)} 字符")

            # 保存到文件
            output_file = "tests/zhaopin_content.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"URL: {target_url}\n")
                f.write(f"标题: {title}\n")
                f.write(f"抓取时间: {asyncio.get_event_loop().time()}\n")
                f.write("=" * 60 + "\n\n")
                f.write(final_content)

            logger.info(f"\n内容已保存到: {output_file}")

            # 截图保存
            screenshot_file = "tests/zhaopin_screenshot.png"
            await page.screenshot(path=screenshot_file, full_page=True)
            logger.info(f"页面截图已保存到: {screenshot_file}")

            # 显示前1000个字符
            logger.info(f"\n内容预览（前1000字符）:")
            logger.info("=" * 60)
            logger.info(final_content[:1000])
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"抓取过程出错: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # 关闭浏览器
            await browser.close()
            logger.info("浏览器已关闭")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Playwright 网页抓取测试")
    print("目标: 看准网公司详情页")
    print("=" * 60 + "\n")

    # 运行异步测试
    asyncio.run(scrape_zhaopin_company())

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
