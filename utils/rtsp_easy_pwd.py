# encoding=utf8
# RTSP 弱密码验证
from typing import Tuple
from utils.runshell import run_cmd
from utils.log import logger
from pathlib import Path
import os


def get_rtsp(ip: str, save_path: Path) -> Tuple[bool, str]:
    """验证普通弱密码"""
    cmd = f"ffmpeg -rw_timeout 10 -i rtsp://admin:12345@{ip}:554 -y -f mjpeg -t 0.001 -s 1280x720 {save_path.joinpath(ip+'.jpg')}"
    cmd2 = f"ffmpeg -rw_timeout 10 -i rtsp://admin:admin@{ip}:554 -y -f mjpeg -t 0.001 -s 1280x720 {save_path.joinpath(ip+'.jpg')}"

    # res = run_cmd(cmd)
    res = os.system(cmd)

    if res == 0:
        if ("401" not in res[1]) and ("404" not in res[1]):
            logger.success(f"[+] IP:{ip},普通弱密码admin/12345成功!")
            return True, "普通弱密码admin/12345"

    res2 = os.system(cmd2)
    if res2 == 0:
        if ("401" not in res[1]) and ("404" not in res[1]):
            logger.success(f"[+] IP:{ip},普通弱密码admin/12345成功!")
            return True, "普通弱密码admin/12345"

    return False


if __name__ == "__main__":
    get_rtsp("12")
