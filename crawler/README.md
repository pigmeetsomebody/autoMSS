# 威胁情报爬虫模块

AutoMSS项目的威胁情报爬虫模块，专门用于从各种公开的威胁情报平台采集安全相关数据。

## 功能特性

- 自动分页爬取：支持自动处理分页和动态加载内容
- 反爬机制对抗：支持请求头伪装、代理池轮换、随机延迟
- 数据清洗：自动去除HTML标签、去重处理
- 多格式保存：支持JSON、CSV、TXT、SQLite数据库
- 模块化设计：易于扩展新的数据源
- 异常处理：完善的重试机制和错误处理
- Selenium支持：支持JavaScript动态页面爬取

## 支持的数据源

### 奇安信威胁情报平台 (ti.qianxin.com)
- 漏洞信息列表
- 漏洞详细信息
- API接口调用

## 快速开始

### 基本使用
```python
from crawler.qianxin_crawler import QianxinCrawler

# 创建爬虫实例
crawler = QianxinCrawler(output_dir="data")

# 爬取漏洞数据
vulnerabilities = crawler.crawl_vulnerabilities(
    max_pages=5,        # 爬取5页
    page_size=20,       # 每页20条
    get_details=True    # 获取详细信息
)

# 保存知识到MSS目录
crawler.save_knowledge_to_mss(vulnerabilities)
```

### 命令行使用
```bash
# 基本爬取
python crawler/main.py --source qianxin --pages 5

# 使用代理
python crawler/main.py --source qianxin --pages 5 --proxy http://proxy1:port

# 使用Selenium模式
python crawler/main.py --source qianxin --pages 5 --use-selenium
```

### 演示脚本
```bash
python demo_crawler.py
```

## 输出格式

数据会自动保存到以下目录：
- knowledge/mss/: 知识库TXT文件
- data/: JSON、CSV和数据库文件

## 注意事项

1. 遵守网站robots.txt协议
2. 合理控制爬取频率
3. 仅用于学习研究和合法用途
4. 使用者需承担相应的法律责任 