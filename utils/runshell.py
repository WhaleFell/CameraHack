# encoding=utf8
# 运行命令在 shell

import subprocess
import time
from utils.log import logger


def run_cmd(cmd_string: str, timeout: int = 99999) -> bool:
    """在 cmd 中运行命令,支持设置超时异常处理
    :param cmd_string: 命令
    :param timeout: 超时时间默认10s
    """
    logger.debug(f"运行的cmd:{cmd_string.strip()}")
    try:
        p = subprocess.Popen(cmd_string, stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE, shell=True)
        t_beginning = time.time()
        while True:
            if p.poll() is not None:
                break
            # seconds_passed = time.time() - t_beginning
            # if timeout and seconds_passed > timeout:
            #     # 判断 运行超时
            #     p.terminate()  # 等同于p.kill()
            #     raise TimeoutError
            time.sleep(0.1)
            print(p.poll())

            # windows 下是 gbk
            pass
        msg = str(p.stdout.read().decode('gbk'))
        logger.debug("运行结果:\n"+msg.strip())
        return True, msg.strip()

    except TimeoutError:
        logger.error(f"运行shell超时{timeout}s")

    except Exception as e:
        logger.error(f"运行shell出现异常{e}")

    return False


if __name__ == "__main__":
    print(run_cmd("ls"))
