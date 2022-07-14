from playwright.sync_api import Playwright, sync_playwright, expect
import time
import random


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


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)

    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to http://10.100.1.152/
    page.goto("http://10.100.1.196/")

    # 输入账号
    page.fill("id=login_user", "cyx")
    # 输入密码
    page.fill("id=login_psw", "12345678A")
    # 点击登录按钮
    # /html/body/div[1]/div/div/div[2]/form/div[4]/a[1]
    page.dblclick("xpath=/html/body/div[1]/div/div/div[2]/form/div[4]/a[1]")
    # 点击设置
    page.click("xpath=/html/body/div[2]/ul/li[5]/a")
    time.sleep(3)
    # 点击系统管理
    page.click(
        "xpath=/html/body/div[2]/div[2]/div[5]/div[1]/div[1]/ul/li[5]/a/span")
    # 点击 系统管理->用户管理
    page.click(
        "xpath=/html/body/div[2]/div[2]/div[5]/div[1]/div[1]/ul/li[5]/ul/li[2]")
    # 点击增加用户
    page.click(
        "xpath=/html/body/div[2]/div[2]/div[5]/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div[3]/a")

    user = generate_random_str(4)
    # 输入用户名
    page.fill("id=use_AUserName", user)
    # 输入密码
    page.fill("id=use_AUserPwd", "12345678A")
    # 确定密码
    page.fill("id=use_AUserPwdCfm", "12345678A")
    time.sleep(8)
    # 保存
    page.click("xpath=/html/body/div[16]/div[3]/a[1]")

    time.sleep(10)
    page.screenshot(path=f'{user}.png')  # 截图
    # Close page
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    while True:
        run(playwright)
