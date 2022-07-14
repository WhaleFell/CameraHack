# encoding=utf8
# pyppetpeer 无头浏览器测试
import asyncio
import time
from pyppeteer import launch
# 神仙pyppeteer_st/eal/th，隐藏WebDriver
# GitHub: https://github.com/MeiK2333/pyppeteer_stealth

from pyppeteer_stealth import stealth


ppeteer_config = {
    "headless": False,  # 是否显示浏览器
    "autoClose": False,  # 不自动关闭
    "ignoreHTTPSErrors": True  # 忽视 HTTPS 错误

}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"


async def main():
    browser = await launch(ppeteer_config)  # new browser obj
    page = await browser.newPage()  # new 新标签页

    # 设置页面视图大小
    await page.setViewport(viewport={'width': 1280, 'height': 800})
    # 是否启用JS，enabled设为False，则无渲染效果
    await page.setJavaScriptEnabled(enabled=True)
    # 防止页面识别出脚本(反爬虫关键语句)
    await stealth(page)

    # 设置 UA
    await page.setUserAgent(UA)

    # 设置 cookies
    # await page.setCookie()

    await page.goto("https://google.com")  # 在地址栏中输入地址

    await page.screenshot({'path': 'example.png'})  # 网页截图

    # 运行 js 代码获取返回值.
    dimensions = await page.evaluate('''() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }''')

    print(dimensions)
    # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}

    # 异步等待
    await asyncio.sleep(5)

    # await browser.close()  # 关闭浏览器


if __name__ == "__main__":
    asyncio.run(main())
