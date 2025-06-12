# -*- coding: utf-8 -*-
"""
威胁情报爬虫主执行脚本
"""

import argparse
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.qianxin_crawler import QianxinCrawler

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='威胁情报爬虫')
    parser.add_argument('--source', type=str, default='qianxin', 
                        help='数据源 (qianxin)')
    parser.add_argument('--pages', type=int, default=5, 
                        help='爬取页数 (默认: 5)')
    parser.add_argument('--username', type=str, default=None, 
                        help='登录用户名')
    parser.add_argument('--password', type=str, default=None, 
                        help='登录密码')
    parser.add_argument('--use-selenium', action='store_true', 
                        help='使用Selenium进行动态页面爬取')
    parser.add_argument('--proxy', type=str, nargs='+', 
                        help='代理列表')
    parser.add_argument('--output-dir', type=str, default='data',
                        help='输出目录 (默认: data)')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='无界面模式运行浏览器')
    
    args = parser.parse_args()
    
    print("="*60)
    print("威胁情报爬虫系统")
    print("="*60)
    print(f"数据源: {args.source}")
    print(f"爬取页数: {args.pages}")
    print(f"输出目录: {args.output_dir}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        if args.source == 'qianxin':
            # 初始化奇安信爬虫
            crawler = QianxinCrawler(output_dir=args.output_dir)
            
            # 设置代理池
            if args.proxy:
                crawler.set_proxy_pool(args.proxy)
            
            # 运行爬虫
            crawler.run(
                max_pages=args.pages,
                username=args.username,
                password=args.password,
                use_selenium=args.use_selenium
            )
        else:
            print(f"不支持的数据源: {args.source}")
            return
        
        print("="*60)
        print(f"爬虫执行完成！")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n爬虫被用户中断")
    except Exception as e:
        print(f"爬虫执行出错: {e}")

if __name__ == "__main__":
    main() 