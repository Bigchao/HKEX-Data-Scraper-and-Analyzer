import os
from datetime import datetime
import logging
import asyncio
import aiohttp
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 启用 headless 模式
    chrome_options.add_argument("--disable-gpu")  # 对某些系统需要
    chrome_options.add_argument("--no-sandbox")  # 在某些环境中需要
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决内存不足的问题
    service = Service('C:\\ChromeDriver\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www1.hkexnews.hk/app/appindex.html")
    return driver

def scrape_hkex_data(driver):
    logging.info("开始抓取 HKEX 数据")
    try:
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table"))
        )
        
        headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
        headers.insert(0, "Number")
        headers.append("PDF Link")
        
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]
        data = []
        for index, row in enumerate(rows, start=1):
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [index] + [cell.text for cell in cells]
            
            # 查找 PDF 链接
            pdf_link = None
            links = cells[-1].find_elements(By.TAG_NAME, "a")
            for link in links:
                if "Full Version" in link.text:
                    pdf_link = link.get_attribute('href')
                    break
            row_data.append(pdf_link)
            
            data.append(row_data)
        
        df = pd.DataFrame(data, columns=headers)
        logging.info(f"成功抓取 {len(df)} 行数据")
        return df
    except Exception as e:
        logging.error(f"抓取 HKEX 数据时发生错误: {str(e)}", exc_info=True)
        return pd.DataFrame()

def clean_data(df):
    logging.info("开始清理数据")
    if 'Latest Posting\nDate' in df.columns:
        df['Latest Posting\nDate'] = pd.to_datetime(df['Latest Posting\nDate'], format='%d/%m/%Y', errors='coerce')
    if 'Applicants' in df.columns:
        df['Applicants'] = df['Applicants'].str.split('\n').str[0]
    return df

def create_date_folder():
    today = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(os.getcwd(), today)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

async def download_pdf(session, pdf_url, company_name, posting_date, folder_path):
    try:
        clean_company_name = ''.join(e for e in company_name if e.isalnum() or e in [' ', '.', '_'])
        clean_company_name = clean_company_name.replace(' ', '_')
        formatted_date = posting_date.strftime('%Y%m%d')
        filename = f"{formatted_date}_{clean_company_name}.pdf"
        file_path = os.path.join(folder_path, filename)

        logging.info(f"开始下载文件: {filename}")
        async with session.get(pdf_url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as f:
                    f.write(await response.read())
                logging.info(f"成功下载 PDF 文件: {filename}")
                return file_path
            else:
                logging.warning(f"下载 PDF 失败，HTTP 状态码: {response.status}")
                return None
    except Exception as e:
        logging.error(f"下载 PDF 时发生错误: {str(e)}", exc_info=True)
        return None

async def process_pdfs(df, folder_path):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _, row in df.iterrows():
            if pd.notna(row['PDF Link']):
                task = download_pdf(session, row['PDF Link'], row['Applicants'], row['Latest Posting\nDate'], folder_path)
                tasks.append(task)
        await asyncio.gather(*tasks)

def update_csv(df, folder_path):
    # 生成带有日期和时间的文件名
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    csv_filename = f"hkex_data_{current_time}.csv"
    csv_path = os.path.join(folder_path, csv_filename)

    df.to_csv(csv_path, index=False)
    logging.info(f"CSV 文件已创建: {csv_path}")

    return csv_path

def main():
    start_time = time.time()  # 记录开始时间
    
    driver = setup_driver()
    
    try:
        logging.info("开始执行主程序")
        df = scrape_hkex_data(driver)
        df = clean_data(df)
        
        if not df.empty:
            folder_path = create_date_folder()
            logging.info(f"创建新文件夹: {folder_path}")
            
            asyncio.run(process_pdfs(df, folder_path))
            
            csv_path = update_csv(df, folder_path)
            
            logging.info("数据：")
            logging.info(df.to_string())
        else:
            logging.warning("未能抓取到任何数据")
    
    except Exception as e:
        logging.error(f"执行过程中发生错误: {str(e)}", exc_info=True)
    
    finally:
        driver.quit()
        end_time = time.time()  # 记录结束时间
        execution_time = end_time - start_time
        logging.info(f"程序执行完毕，总运行时间: {execution_time:.2f} 秒")
        print(f"程序总运行时间: {execution_time:.2f} 秒")

if __name__ == "__main__":
    main()

