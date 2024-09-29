import pdfplumber
import spacy
import os
import re

# 加载 spaCy 模型
nlp = spacy.load("en_core_web_sm")

def extract_business_overview_paragraph(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        business_found = False
        overview_found = False
        text_buffer = ""
        
        # 从第220页开始搜索，给予一些余地
        for page_num in range(219, len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            text_buffer += text + "\n"
            
            # 使用 NLP 分析文本
            doc = nlp(text_buffer)
            
            # 查找 BUSINESS 章节
            if not business_found:
                for sent in doc.sents:
                    if re.search(r'\bBUSINESS\b', sent.text, re.IGNORECASE):
                        business_found = True
                        print(f"Found BUSINESS section on page {page_num + 1}")
                        break
            
            # 在 BUSINESS 章节中查找 Overview
            if business_found and not overview_found:
                for sent in doc.sents:
                    if "Overview" in sent.text:
                        overview_found = True
                        print(f"Found Overview subsection on page {page_num + 1}")
                        
                        # 提取 Overview 后的段落
                        overview_index = text_buffer.index(sent.text)
                        paragraph_start = text_buffer.find('\n', overview_index) + 1
                        paragraph = ""
                        for next_sent in list(doc.sents)[doc.sents.index(sent)+1:]:
                            if len(next_sent.text.split()) > 5:  # 忽略短句
                                paragraph += next_sent.text + " "
                            if len(paragraph.split()) > 50:  # 假设段落至少有50个词
                                return paragraph.strip()
        
        # 如果没有找到完整段落，返回已收集的内容
        return paragraph.strip() if paragraph else "未找到 Business 章节的 Overview 或其第一段"

# 使用绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "2024-09-17", "20240913_HealthyWay_Inc..pdf")

# 检查文件是否存在
if os.path.exists(pdf_path):
    result = extract_business_overview_paragraph(pdf_path)
    print("\nExtracted paragraph:")
    print(result)
else:
    print(f"文件不存在: {pdf_path}")