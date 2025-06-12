#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
威胁情报爬虫演示脚本
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.qianxin_crawler import QianxinCrawler

def demo_qianxin_crawler():
    """演示奇安信爬虫的使用"""
    print("="*60)
    print("奇安信威胁情报平台爬虫演示")
    print("="*60)
    
    # 创建爬虫实例
    crawler = QianxinCrawler(output_dir="data")
    
    # 设置代理池（可选）
    # proxies = [
    #     "http://proxy1:port",
    #     "http://proxy2:port"
    # ]
    # crawler.set_proxy_pool(proxies)
    
    try:
        # 运行爬虫
        print("开始爬取奇安信威胁情报...")
        vulnerabilities = crawler.crawl_vulnerabilities(
            max_pages=3,        # 爬取3页
            page_size=20,       # 每页20条
            get_details=True    # 获取详细信息
        )
        
        if vulnerabilities:
            print(f"\n成功爬取 {len(vulnerabilities)} 条漏洞信息")
            
            # 显示前几条数据示例
            print("\n前3条漏洞信息示例:")
            print("-" * 60)
            for i, vuln in enumerate(vulnerabilities[:3]):
                print(f"\n漏洞 {i+1}:")
                print(f"  标题: {vuln.get('title', 'N/A')}")
                print(f"  编号: {vuln.get('id', 'N/A')}")
                print(f"  CVE: {vuln.get('cve_id', 'N/A')}")
                print(f"  严重程度: {vuln.get('severity', 'N/A')}")
                print(f"  厂商: {vuln.get('vendor', 'N/A')}")
                print(f"  产品: {vuln.get('product', 'N/A')}")
            
            # 保存数据到各种格式
            print("\n保存数据...")
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存为JSON
            crawler.save_to_json(vulnerabilities, f"qianxin_demo_{timestamp}")
            
            # 保存为CSV
            crawler.save_to_csv(vulnerabilities, f"qianxin_demo_{timestamp}")
            
            # 保存知识库到MSS目录
            crawler.save_knowledge_to_mss(vulnerabilities)
            
            print("数据保存完成！")
            
        else:
            print("未获取到漏洞数据")
            
    except Exception as e:
        print(f"爬虫运行出错: {e}")

def demo_simple_api_call():
    """演示简单的API调用"""
    print("\n" + "="*60)
    print("简单API调用演示")
    print("="*60)
    
    crawler = QianxinCrawler()
    
    # 直接调用API获取一页数据
    print("正在获取第1页漏洞列表...")
    data = crawler.get_vulnerability_list_api(page=1, page_size=5)
    
    if data and 'data' in data:
        vulnerabilities = data['data'].get('list', [])
        print(f"获取到 {len(vulnerabilities)} 条漏洞信息")
        
        for i, vuln in enumerate(vulnerabilities):
            print(f"\n漏洞 {i+1}:")
            print(f"  编号: {vuln.get('qvd_code', 'N/A')}")
            print(f"  标题: {vuln.get('title', 'N/A')}")
            print(f"  严重程度: {vuln.get('severity', 'N/A')}")
    else:
        print("API调用失败")

def main():
    """主函数"""
    print("威胁情报爬虫系统演示")
    print("请选择演示模式:")
    print("1. 完整爬虫演示")
    print("2. 简单API调用演示")
    print("3. 退出")
    
    while True:
        choice = input("\n请输入选项 (1-3): ").strip()
        
        if choice == '1':
            demo_qianxin_crawler()
            break
        elif choice == '2':
            demo_simple_api_call()
            break
        elif choice == '3':
            print("退出演示")
            break
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main() 