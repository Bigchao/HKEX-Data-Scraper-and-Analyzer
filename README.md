# HKEX Data Scraper and Analyzer

这个项目包含了一系列Python脚本，用于从香港交易所（HKEX）网站抓取数据，下载PDF文件，提取和分析PDF内容，以及比较不同时间点的数据变化。

## 文件说明

### main.py
- 主要功能：从HKEX网站抓取数据并下载PDF文件
- 使用Selenium进行网页抓取
- 异步下载PDF文件
- 创建日期文件夹并保存CSV数据

### local_pdf_extractor.py
- 从PDF文件中提取文本
- 使用Moonshot AI API进行内容分析
- 保存分析结果到文本文件

### pdf_extractor.py
- 使用pdfplumber和spaCy从PDF中提取特定段落
- 专注于提取"BUSINESS"章节中的"Overview"部分

### compare_csv.py
- 比较两个CSV文件（最新的和之前的）的内容
- 识别新增和删除的公司
- 生成更新报告（update.txt）
- 管理根目录和子目录中的CSV文件

## 主要功能
1. 从HKEX网站抓取最新的上市申请数据
2. 下载相关的PDF文件
3. 提取PDF中的关键业务信息
4. 比较不同时间点的数据，生成更新报告
5. 维护最新的数据文件在根目录

## 使用方法
1. 运行 `main.py` 抓取最新数据和PDF
2. 使用 `local_pdf_extractor.py` 或 `pdf_extractor.py` 分析PDF内容
3. 运行 `compare_csv.py` 比较数据变化并生成报告

## 依赖
- Python 3.x
- Selenium
- pandas
- aiohttp
- PyPDF2
- pdfplumber
- spaCy
- Moonshot AI API

请确保安装所有必要的依赖项，并配置正确的API密钥和文件路径。