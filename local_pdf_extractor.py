import os
import logging
from pathlib import Path
import PyPDF2
import math
from openai import OpenAI
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 直接设置 API 密钥
API_KEY = "sk-qZ1Tn6eO3rGl7wikTzGkzAVokR8qe0nmgpla6Ooew2ZkNvc9"  # 请替换为您的实际 API 密钥

# 设置内容截取比例
CONTENT_RATIO = 0.04  # 默认为1/20

# 初始化OpenAI客户端
try:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )
except Exception as e:
    logging.error(f"初始化OpenAI客户端失败: {str(e)}")
    exit(1)

def test_api_connection():
    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.3,
        )
        logging.info("API 连接测试成功")
        return True
    except Exception as e:
        logging.error(f"API 连接测试失败: {str(e)}")
        if isinstance(e, requests.exceptions.RequestException):
            logging.error(f"请求详情: {e.request.method} {e.request.url}")
            logging.error(f"响应状态码: {e.response.status_code}")
            logging.error(f"响应内容: {e.response.text}")
        return False

def extract_text_from_pdf(pdf_path):
    """从PDF中提取指定比例的文本"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            pages_to_extract = math.ceil(total_pages * CONTENT_RATIO)
            
            for i in range(min(pages_to_extract, total_pages)):
                text += reader.pages[i].extract_text()
                
                # 如果已经提取了足够的内容，就提前结束
                if len(text) >= 100000:  # 假设100000字符足够进行分析
                    break
        logging.info(f"成功从PDF提取了 {len(text)} 个字符")
    except Exception as e:
        logging.error(f"PDF解析错误: {str(e)}")
    return text

def call_moonshot_api(prompt, content):
    """调用Moonshot API"""
    try:
        messages = [
            {
                "role": "system",
                "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
            },
            {
                "role": "system",
                "content": content,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"API 调用失败: {str(e)}")
        if hasattr(e, 'response'):
            logging.error(f"响应状态码: {e.response.status_code}")
            logging.error(f"响应内容: {e.response.text}")
        return None

def process_pdf(pdf_path, prompt, output_path):
    """处理单个PDF文件"""
    logging.info(f"处理文件: {pdf_path}")
    
    # 提取PDF文本
    pdf_content = extract_text_from_pdf(pdf_path)
    
    if not pdf_content:
        logging.error(f"无法从PDF中提取文本: {pdf_path}")
        return
    
    # 调用API
    result = call_moonshot_api(prompt, pdf_content)
    
    if result:
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        logging.info(f"结果已保存到 {output_path}")
    else:
        logging.error("API调用失败，未能获取结果")

def main():
    logging.info(f"使用的API密钥: {API_KEY[:5]}...{API_KEY[-5:]}")
    
    if not test_api_connection():
        logging.error("API 连接测试失败，程序终止")
        return

    pdf_path = Path("2024-09-17/20240531_Cloudbreak_Pharma_Inc.__B.pdf")
    prompt_file = Path("Prompt")
    output_file = Path("results/20240531_Cloudbreak_Pharma_Inc.__B_overview.txt")

    # 确保输出文件夹存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 读取提示文件
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
    except Exception as e:
        logging.error(f"读取提示文件失败: {str(e)}")
        return

    # 处理PDF文件
    process_pdf(pdf_path, prompt, output_file)

    logging.info("处理完成")

if __name__ == "__main__":
    main()