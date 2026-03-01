import os
import time
import requests


def wx_send(content: str, title: str = "任务通知") -> dict:
    """
    使用 Pushplus 发送微信推送（token 从环境变量读取，不写死在代码里）
    环境变量：
      - PUSHPLUS_TOKEN
    """
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        raise RuntimeError("Missing env var: PUSHPLUS_TOKEN")

    url = "http://www.pushplus.plus/send"
    payload = {
        "token": token,
        "title": title,
        "content": content,
    }

    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()

    # Pushplus 一般会返回类似 {"code":200,"msg":"请求成功","data":...}
    if isinstance(data, dict) and data.get("code") not in (200, "200", None):
        raise RuntimeError(f"Pushplus error response: {data}")
    return data

