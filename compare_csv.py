import os
import pandas as pd
from datetime import datetime
import shutil

def get_latest_folder(base_path):
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f)) and f.startswith("20")]
    if not folders:
        print("没有找到日期文件夹")
        return None
    latest_folder = max(folders, key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
    print(f"找到最新的文件夹: {latest_folder}")
    return latest_folder

def get_latest_csv(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f.startswith('hkex_data')]
    if not csv_files:
        return None
    return max(csv_files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))

def compare_csv_files(old_csv_path, new_csv_path):
    old_df = pd.read_csv(old_csv_path)
    new_df = pd.read_csv(new_csv_path)
    
    old_companies = set(old_df['Applicants'])
    new_companies = set(new_df['Applicants'])
    
    added_companies = new_companies - old_companies
    removed_companies = old_companies - new_companies
    
    added_companies_df = new_df[new_df['Applicants'].isin(added_companies)][['Latest Posting\nDate', 'Applicants']]
    added_companies_df = added_companies_df.reset_index(drop=True)
    added_companies_df.index += 1  # Start index from 1
    
    removed_companies_df = old_df[old_df['Applicants'].isin(removed_companies)][['Latest Posting\nDate', 'Applicants']]
    removed_companies_df = removed_companies_df.reset_index(drop=True)
    removed_companies_df.index += 1  # Start index from 1
    
    return added_companies_df, removed_companies_df

def write_update_file(added_companies_df, removed_companies_df, update_file_path):
    with open(update_file_path, 'w', encoding='utf-8') as f:
        if added_companies_df.empty and removed_companies_df.empty:
            f.write("没有任何更新\n")
        else:
            if not added_companies_df.empty:
                f.write("新增公司：\n")
                f.write("序号\t发布日期\t公司名称\n")
                for index, row in added_companies_df.iterrows():
                    f.write(f"{index}\t{row['Latest Posting\nDate']}\t{row['Applicants']}\n")
            
            if not removed_companies_df.empty:
                if not added_companies_df.empty:
                    f.write("\n")
                f.write("删除公司：\n")
                f.write("序号\t发布日期\t公司名称\n")
                for index, row in removed_companies_df.iterrows():
                    f.write(f"{index}\t{row['Latest Posting\nDate']}\t{row['Applicants']}\n")
    print(f"更新信息已写入 {update_file_path}")

def main():
    base_path = os.getcwd()
    
    # 获取根目录下的 hkex_data.csv 文件
    new_csv_file = 'hkex_data.csv'
    new_csv_path = os.path.join(base_path, new_csv_file)
    if not os.path.exists(new_csv_path):
        print("根目录下没有找到 hkex_data.csv 文件")
        return
    
    # 获取最新的日期文件夹
    latest_folder = get_latest_folder(base_path)
    if not latest_folder:
        return
    
    # 获取最新日期文件夹中的 CSV 文件
    old_csv_file = get_latest_csv(os.path.join(base_path, latest_folder))
    if not old_csv_file:
        print(f"在 {latest_folder} 文件夹中没有找到 CSV 文件")
        return
    old_csv_path = os.path.join(base_path, latest_folder, old_csv_file)
    
    # 比较 CSV 文件
    added_companies_df, removed_companies_df = compare_csv_files(new_csv_path, old_csv_path)
    
    # 写入更新信息到最新的子目录
    update_file_path = os.path.join(base_path, latest_folder, "update.txt")
    write_update_file(added_companies_df, removed_companies_df, update_file_path)

    # 删除根目录的 CSV 文件
    try:
        os.remove(new_csv_path)
        print(f"已删除根目录的 {new_csv_file}")
    except OSError as e:
        print(f"删除根目录的 {new_csv_file} 时出错: {e}")

    # 复制最新子目录中的 CSV 文件到根目录
    try:
        shutil.copy2(old_csv_path, new_csv_path)
        print(f"已将 {old_csv_file} 复制到根目录")
    except OSError as e:
        print(f"复制 {old_csv_file} 到根目录时出错: {e}")

if __name__ == "__main__":
    main()
