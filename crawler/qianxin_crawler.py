# -*- coding: utf-8 -*-
"""
奇安信威胁情报平台爬虫
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Any, Optional
import urllib.parse
import hashlib
from datetime import datetime
import os
import random

from .base_crawler import BaseCrawler

class QianxinCrawler(BaseCrawler):
    """奇安信威胁情报平台爬虫"""
    
    def __init__(self, output_dir: str = None):
        super().__init__("https://ti.qianxin.com", output_dir)
        self.driver = None
        self.is_logged_in = False
        self.vulnerability_data = []
        
    def setup_selenium(self, headless: bool = True):
        """配置Selenium WebDriver"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-certificate-errors")
        
        # 添加用户代理
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.logger.info("Selenium WebDriver 初始化成功")
        except Exception as e:
            self.logger.error(f"Selenium WebDriver 初始化失败: {e}")
            raise
    
    def login(self, username: str = None, password: str = None):
        """模拟登录 - 注意：实际使用时需要提供真实的用户名和密码"""
        if not self.driver:
            self.setup_selenium()
        
        try:
            # 访问登录页面
            login_url = "https://ti.qianxin.com/login"
            self.driver.get(login_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "login-form"))
            )
            
            # 检查是否需要登录
            if "/login" not in self.driver.current_url:
                self.is_logged_in = True
                self.logger.info("已经登录或无需登录")
                return True
            
            # 如果提供了登录凭据，尝试登录
            if username and password:
                username_input = self.driver.find_element(By.NAME, "username")
                password_input = self.driver.find_element(By.NAME, "password")
                
                username_input.send_keys(username)
                password_input.send_keys(password)
                
                # 点击登录按钮
                login_button = self.driver.find_element(By.CSS_SELECTOR, ".login-btn")
                login_button.click()
                
                # 等待登录完成
                time.sleep(3)
                
                if "/login" not in self.driver.current_url:
                    self.is_logged_in = True
                    self.logger.info("登录成功")
                    return True
                else:
                    self.logger.error("登录失败")
                    return False
            else:
                self.logger.warning("未提供登录凭据，继续尝试访问公开内容")
                return True
                
        except Exception as e:
            self.logger.error(f"登录过程出错: {e}")
            return False
    
    def get_vulnerability_list_api(self, page: int = 1, page_size: int = 20) -> Optional[Dict]:
        """通过API获取漏洞列表"""
        api_url = "https://ti.qianxin.com/alpha-api/v2/vulnerability/list"
        
        params = {
            'page': page,
            'page_size': page_size,
            'sort': '-date_published',
            'product': '',
            'severity': '',
            'vendor': '',
            'search': ''
        }
        
        headers = {
            'Referer': 'https://ti.qianxin.com/vulnerability/list',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*',
        }
        
        try:
            response = self.request_with_retry(api_url, params=params, headers=headers)
            if response and response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API请求失败，状态码: {response.status_code if response else 'None'}")
                return None
        except Exception as e:
            self.logger.error(f"API请求异常: {e}")
            return None
    
    def get_vulnerability_detail(self, vuln_id: str) -> Optional[Dict]:
        """获取漏洞详细信息"""
        detail_url = f"https://ti.qianxin.com/alpha-api/v2/vulnerability/{vuln_id}"
        
        headers = {
            'Referer': f'https://ti.qianxin.com/vulnerability/{vuln_id}',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*',
        }
        
        try:
            response = self.request_with_retry(detail_url, headers=headers)
            if response and response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"获取漏洞详情失败: {vuln_id}")
                return None
        except Exception as e:
            self.logger.error(f"获取漏洞详情异常: {e}")
            return None
    
    def parse_vulnerability_data(self, vuln_data: Dict) -> Dict:
        """解析漏洞数据"""
        try:
            parsed_data = {
                'id': vuln_data.get('qvd_code', ''),
                'title': self.clean_text(vuln_data.get('title', '')),
                'cve_id': vuln_data.get('cve_code', ''),
                'cvss_score': vuln_data.get('cvss_score', ''),
                'severity': vuln_data.get('severity', ''),
                'vendor': vuln_data.get('vendor', ''),
                'product': vuln_data.get('product', ''),
                'version': vuln_data.get('version', ''),
                'date_published': vuln_data.get('date_published', ''),
                'date_updated': vuln_data.get('date_updated', ''),
                'description': self.clean_text(vuln_data.get('description', '')),
                'solution': self.clean_text(vuln_data.get('solution', '')),
                'tags': ','.join(vuln_data.get('tags', [])),
                'references': ','.join(vuln_data.get('references', [])),
                'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return parsed_data
        except Exception as e:
            self.logger.error(f"解析漏洞数据失败: {e}")
            return {}
    
    def crawl_vulnerabilities(self, max_pages: int = 5, page_size: int = 20, get_details: bool = True):
        """爬取漏洞信息"""
        self.logger.info("开始爬取奇安信威胁情报平台漏洞信息")
        
        all_vulnerabilities = []
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"正在爬取第 {page} 页")
            
            # 获取漏洞列表
            vuln_list_response = self.get_vulnerability_list_api(page, page_size)
            
            if not vuln_list_response or 'data' not in vuln_list_response:
                self.logger.warning(f"第 {page} 页数据获取失败")
                continue
            
            vulnerabilities = vuln_list_response['data'].get('list', [])
            
            if not vulnerabilities:
                self.logger.info(f"第 {page} 页无数据，停止爬取")
                break
            
            for vuln in vulnerabilities:
                vuln_data = self.parse_vulnerability_data(vuln)
                
                # 如果需要获取详细信息
                if get_details and vuln_data.get('id'):
                    detail_data = self.get_vulnerability_detail(vuln_data['id'])
                    if detail_data and 'data' in detail_data:
                        detailed_vuln = self.parse_vulnerability_data(detail_data['data'])
                        vuln_data.update(detailed_vuln)
                
                if vuln_data:
                    all_vulnerabilities.append(vuln_data)
            
            # 随机延迟，避免被封
            time.sleep(random.uniform(2, 5))
        
        # 去重
        all_vulnerabilities = self.deduplicate(all_vulnerabilities, 'id')
        
        self.vulnerability_data = all_vulnerabilities
        self.logger.info(f"漏洞信息爬取完成，共获取 {len(all_vulnerabilities)} 条数据")
        
        return all_vulnerabilities
    
    def generate_knowledge_texts(self, vulnerabilities: List[Dict]) -> List[str]:
        """生成知识库文本"""
        texts = []
        
        for vuln in vulnerabilities:
            # 生成漏洞知识文本
            text_parts = []
            
            if vuln.get('title'):
                text_parts.append(f"漏洞标题: {vuln['title']}")
            
            if vuln.get('id'):
                text_parts.append(f"漏洞编号: {vuln['id']}")
            
            if vuln.get('cve_id'):
                text_parts.append(f"CVE编号: {vuln['cve_id']}")
            
            if vuln.get('severity'):
                text_parts.append(f"危险等级: {vuln['severity']}")
            
            if vuln.get('cvss_score'):
                text_parts.append(f"CVSS评分: {vuln['cvss_score']}")
            
            if vuln.get('vendor'):
                text_parts.append(f"厂商: {vuln['vendor']}")
            
            if vuln.get('product'):
                text_parts.append(f"产品: {vuln['product']}")
            
            if vuln.get('version'):
                text_parts.append(f"受影响版本: {vuln['version']}")
            
            if vuln.get('description'):
                text_parts.append(f"漏洞描述: {vuln['description']}")
            
            if vuln.get('solution'):
                text_parts.append(f"解决方案: {vuln['solution']}")
            
            if vuln.get('date_published'):
                text_parts.append(f"发布时间: {vuln['date_published']}")
            
            if text_parts:
                knowledge_text = '\n'.join(text_parts)
                texts.append(knowledge_text)
        
        return texts
    
    def save_knowledge_to_mss(self, vulnerabilities: List[Dict]):
        """保存知识到MSS目录"""
        mss_dir = os.path.join(os.path.dirname(self.output_dir), "knowledge", "mss")
        os.makedirs(mss_dir, exist_ok=True)
        
        # 生成知识文本
        knowledge_texts = self.generate_knowledge_texts(vulnerabilities)
        
        # 按类型分组保存
        high_severity = []
        medium_severity = []
        low_severity = []
        
        for i, vuln in enumerate(vulnerabilities):
            text = knowledge_texts[i] if i < len(knowledge_texts) else ""
            if not text:
                continue
                
            severity = vuln.get('severity', '').lower()
            if 'high' in severity or 'critical' in severity:
                high_severity.append(text)
            elif 'medium' in severity:
                medium_severity.append(text)
            else:
                low_severity.append(text)
        
        # 保存不同严重级别的漏洞
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if high_severity:
            high_filepath = os.path.join(mss_dir, f"qianxin_high_severity_vulns_{timestamp}.txt")
            with open(high_filepath, 'w', encoding='utf-8') as f:
                f.write('\n\n' + '='*50 + '\n\n'.join(high_severity))
            self.logger.info(f"高危漏洞知识已保存到: {high_filepath}")
        
        if medium_severity:
            medium_filepath = os.path.join(mss_dir, f"qianxin_medium_severity_vulns_{timestamp}.txt")
            with open(medium_filepath, 'w', encoding='utf-8') as f:
                f.write('\n\n' + '='*50 + '\n\n'.join(medium_severity))
            self.logger.info(f"中危漏洞知识已保存到: {medium_filepath}")
        
        if low_severity:
            low_filepath = os.path.join(mss_dir, f"qianxin_low_severity_vulns_{timestamp}.txt")
            with open(low_filepath, 'w', encoding='utf-8') as f:
                f.write('\n\n' + '='*50 + '\n\n'.join(low_severity))
            self.logger.info(f"低危漏洞知识已保存到: {low_filepath}")
        
        # 保存完整的漏洞知识库
        all_filepath = os.path.join(mss_dir, f"qianxin_all_vulnerabilities_{timestamp}.txt")
        with open(all_filepath, 'w', encoding='utf-8') as f:
            f.write('\n\n' + '='*50 + '\n\n'.join(knowledge_texts))
        self.logger.info(f"完整漏洞知识库已保存到: {all_filepath}")
    
    def run(self, max_pages: int = 5, username: str = None, password: str = None, use_selenium: bool = False):
        """运行爬虫"""
        try:
            # 如果需要使用Selenium
            if use_selenium:
                self.setup_selenium()
                self.login(username, password)
            
            # 爬取漏洞数据
            vulnerabilities = self.crawl_vulnerabilities(max_pages=max_pages, get_details=True)
            
            if vulnerabilities:
                # 保存到各种格式
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # 保存为JSON
                self.save_to_json(vulnerabilities, f"qianxin_vulnerabilities_{timestamp}")
                
                # 保存为CSV
                self.save_to_csv(vulnerabilities, f"qianxin_vulnerabilities_{timestamp}")
                
                # 保存到数据库
                self.save_to_db(vulnerabilities, "qianxin_vulnerabilities")
                
                # 保存知识到MSS目录
                self.save_knowledge_to_mss(vulnerabilities)
                
                self.logger.info(f"爬虫运行完成，共处理 {len(vulnerabilities)} 条漏洞数据")
            else:
                self.logger.warning("未获取到任何漏洞数据")
                
        except Exception as e:
            self.logger.error(f"爬虫运行出错: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver 已关闭") 