# encoding=utf8
# 检测一个端口是否开放.
import socket


def Check_Port(server_ip: str, port: int):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)  # 设置超时时间
    try:
        sk.connect((server_ip, port))
        return True
    except Exception:
        return False
    finally:
        sk.close()


if __name__ == "__main__":
    print(Check_Port("10.1.9.235", 554))
