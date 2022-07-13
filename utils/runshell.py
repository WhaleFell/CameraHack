# encoding=utf8
# 运行命令在 shell

import subprocess
import time
from utils.log import logger
import datetime
import platform
import os
import signal


def _run_cmd(cmd_string: str, timeout: int = 99999) -> bool:
    """通过 subprocess.Popen 运行命令,支持设置超时异常处理(已弃用)
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
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                # 判断 运行超时
                p.terminate()  # 等同于p.kill()
                raise TimeoutError
            time.sleep(0.1)

        # windows 下是 gbk
        msg = str(p.stdout.read().decode('gbk'))
        logger.debug("运行结果:\n"+msg.strip())
        return True, msg.strip()

    except TimeoutError:
        logger.error(f"运行shell超时{timeout}s")

    except Exception as e:
        logger.error(f"运行shell出现异常{e}")

    return False


def _run_cmd(cmd: str, timeout: int = 10) -> bool:
    """在 cmd 中通过 `subprocess.run()` 运行命令,支持设置超时异常处理
    :param cmd_string: 命令
    :param timeout: 超时时间默认10s
    """

    logger.debug(f"运行的cmd:{cmd.strip()}")
    try:
        # 错误信息会和 stdout 一起输出
        res = subprocess.run(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=timeout, check=True, encoding="gbk", shell=True)
    except subprocess.TimeoutExpired:
        logger.error(f"命令执行超时 {timeout}s!")

        return False
    except subprocess.CalledProcessError:
        logger.error(f"命令执行错误!")
        return False
    except Exception as e:
        logger.error(f"执行命令其他错误:{e}")
        return False

    return True


def run_cmd(cmd: str, timeout: int = 5):
    """在 cmd 中通过 `subprocess.Popen` 运行命令,支持设置超时异常处理
    :param cmd_string: 命令
    :param timeout: 超时时间默认10s
    """

    logger.debug(f"运行的cmd:{cmd.strip()}")

    start = datetime.datetime.now()
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True,
                         start_new_session=True)

    formats = 'gbk' if platform.system() == "Windows" else 'utf-8'

    try:
        while p.poll() is None:
            now = datetime.datetime.now()
            if (now - start).seconds < timeout:
                # 堵塞
                line = p.stdout.readline()
                line = line.strip()
                if line:
                    logger.debug(line.decode(formats))
                time.sleep(0.01)
            else:
                raise TimeoutError

        # out, err = p.communicate()
        # logger.debug(out.decode(formats))

        if p.returncode:
            logger.error("命令执行失败!")
            return False
        else:
            logger.success("命令执行成功!")
            return True
    except (TimeoutError):
        logger.error("命令执行超时!")
        # 超时处理
        # 注意：不能只使用p.kill和p.terminate，无法杀干净所有的子进程，需要使用os.killpg
        p.kill()
        p.terminate()
        # 在 Windows 上，os.killpg将不起作用，因为它向进程 ID 发送信号以终止。这就是你现在如何在 Windows 上终止进程，而你必须使用 win32 API 的 TerminateProcess杀死一个进程。
        # os.killpg(p.pid, signal.SIGTERM)
        # idea: https://www.coder.work/article/1251420
        os.kill(p.pid, signal.CTRL_C_EVENT)
        # 如果开启下面这两行的话，会等到执行完成才报超时错误，但是可以输出执行结果
        # (outs, errs) = p.communicate()
        # print(outs.decode('utf-8'))
        return False

    except Exception as e:
        logger.error(f"命令执行其他错误:{type(e)}")
        return False


if __name__ == "__main__":
    print(run_cmd("ls"))
