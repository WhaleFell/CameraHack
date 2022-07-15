from playwright.async_api import async_playwright, Playwright, Browser
import time
import random
import asyncio


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


async def run(browser: Browser) -> None:
    # browser = await playwright.chromium.launch(headless=False)

    # context = await browser.new_context()

    # Open new page
    page = await browser.new_page()

    # Go to http://10.100.1.152/
    await page.goto("http://10.100.1.196/")

    # 输入账号
    await page.fill("id=login_user", "wCGg")
    # 输入密码
    await page.fill("id=login_psw", "12345678A")
    # 点击登录按钮
    await page.dblclick("xpath=/html/body/div[1]/div/div/div[2]/form/div[4]/a[1]")
    # 点击设置
    await page.click("xpath=/html/body/div[2]/ul/li[5]/a")

    await page.wait_for_timeout(3*1000)

    # 点击系统管理
    await page.click(
        "xpath=/html/body/div[2]/div[2]/div[5]/div[1]/div[1]/ul/li[5]/a")

    # 点击 系统管理->用户管理
    await page.click(
        "xpath=/html/body/div[2]/div[2]/div[5]/div[1]/div[1]/ul/li[5]/ul/li[2]")

    await page.wait_for_timeout(4*1000)

    # 点击增加用户
    await page.click(
        "xpath=/html/body/div[2]/div[2]/div[5]/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div[3]/a")

    user = generate_random_str(4)
    # 输入用户名
    await page.fill("id=use_AUserName", user)
    # 输入密码
    await page.fill("id=use_AUserPwd", "12345678A")
    # 确定密码
    await page.fill("id=use_AUserPwdCfm", "12345678A")
    # https://playwright.dev/python/docs/intro#timesleep-leads-to-outdated-state

    # 保存
    await page.click("xpath=/html/body/div[16]/div[3]/a[1]")

    await page.wait_for_timeout(10*1000)
    await page.screenshot(path=f'{user}.png')  # 截图
    # Close page
    await page.close()
    # ---------------------
    # await context.close()
    # await browser.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("http://test.ipw.cn")
        while True:
            await run(browser)


if __name__ == "__main__":
    asyncio.run(main())
