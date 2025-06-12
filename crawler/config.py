# -*- coding: utf-8 -*-
"""
爬虫配置文件
"""

import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge", "mss")

# 奇安信配置
QIANXIN_CONFIG = {
    "base_url": "https://ti.qianxin.com",
    "api_base": "https://ti.qianxin.com/alpha-api/v2",
    "login_url": "https://ti.qianxin.com/login",
    "vulnerability_list_url": "https://ti.qianxin.com/vulnerability/list",
    "headers": {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
    },
    "request_delay": (1, 3),  # 请求延迟范围（秒）
    "page_delay": (2, 5),    # 翻页延迟范围（秒）
    "max_retries": 3,        # 最大重试次数
    "timeout": 10,           # 请求超时时间
}

# 代理池配置（示例）
PROXY_POOL = [
    # "http://proxy1:port",
    # "http://proxy2:port",
    # "http://proxy3:port",
]

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_encoding": "utf-8",
}

# 数据保存配置
SAVE_CONFIG = {
    "formats": ["json", "csv", "txt", "db"],  # 保存格式
    "txt_separator": "\n" + "="*50 + "\n",   # TXT文件分隔符
    "enable_deduplication": True,             # 启用去重
    "dedup_key": "id",                        # 去重字段
}

# Selenium配置
SELENIUM_CONFIG = {
    "headless": True,
    "window_size": (1920, 1080),
    "page_load_timeout": 30,
    "implicit_wait": 10,
    "chrome_options": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-logging",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--ignore-certificate-errors",
    ]
} 