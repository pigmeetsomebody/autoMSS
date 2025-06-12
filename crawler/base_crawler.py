# -*- coding: utf-8 -*-
"""
基础爬虫类，提供通用的爬取功能
"""

import requests
import time
import random
import logging
import json
import csv
import os
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import threading
from fake_useragent import UserAgent

class BaseCrawler:
    """基础爬虫类"""
    
    def __init__(self, base_url: str, output_dir: str = None):
        self.base_url = base_url
        self.output_dir = output_dir or "data"
        self.session = requests.Session()
        self.ua = UserAgent()
        self.proxy_pool = []
        self.current_proxy_index = 0
        self.lock = threading.Lock()
        
        # 配置日志
        self.setup_logging()
        
        # 配置会话
        self.setup_session()
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{self.output_dir}/crawler.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def setup_session(self):
        """配置会话重试机制"""
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def set_proxy_pool(self, proxies: List[str]):
        """设置代理池"""
        self.proxy_pool = proxies
        self.logger.info(f"设置代理池，共{len(proxies)}个代理")
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """轮询获取代理"""
        if not self.proxy_pool:
            return None
        
        with self.lock:
            proxy = self.proxy_pool[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def request_with_retry(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """带重试机制的请求"""
        for attempt in range(3):
            try:
                # 设置请求头
                headers = self.get_headers()
                if 'headers' in kwargs:
                    headers.update(kwargs['headers'])
                kwargs['headers'] = headers
                
                # 设置代理
                proxy = self.get_proxy()
                if proxy:
                    kwargs['proxies'] = proxy
                
                # 设置超时
                kwargs.setdefault('timeout', 10)
                
                # 发送请求
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                
                # 随机延迟
                time.sleep(random.uniform(1, 3))
                
                return response
                
            except Exception as e:
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(random.uniform(3, 6))
                else:
                    self.logger.error(f"请求最终失败: {url}")
        
        return None
    
    def save_to_json(self, data: List[Dict], filename: str):
        """保存数据到JSON文件"""
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"数据已保存到: {filepath}")
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """保存数据到CSV文件"""
        if not data:
            return
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        self.logger.info(f"数据已保存到: {filepath}")
    
    def save_to_txt(self, content: str, filename: str):
        """保存文本内容到TXT文件"""
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        self.logger.info(f"内容已保存到: {filepath}")
    
    def save_to_db(self, data: List[Dict], table_name: str, db_path: str = None):
        """保存数据到SQLite数据库"""
        if not data:
            return
        
        db_path = db_path or os.path.join(self.output_dir, "crawler_data.db")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 创建表
            columns = list(data[0].keys())
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {', '.join([f'{col} TEXT' for col in columns])}
            )
            """
            cursor.execute(create_sql)
            
            # 插入数据
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            for item in data:
                cursor.execute(insert_sql, [item.get(col, '') for col in columns])
            
            conn.commit()
        
        self.logger.info(f"数据已保存到数据库: {db_path}, 表: {table_name}")
    
    def clean_text(self, text: str) -> str:
        """清洗文本内容"""
        if not text:
            return ""
        
        # 去除HTML标签
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def deduplicate(self, data: List[Dict], key: str) -> List[Dict]:
        """根据指定键去重"""
        seen = set()
        unique_data = []
        
        for item in data:
            if item.get(key) not in seen:
                seen.add(item.get(key))
                unique_data.append(item)
        
        self.logger.info(f"去重前: {len(data)}, 去重后: {len(unique_data)}")
        return unique_data 