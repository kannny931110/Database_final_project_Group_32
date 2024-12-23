import mysql.connector
import pandas as pd

def import_excel_to_db(excel_file):
    # 連接到 MySQL 資料庫
    mydb = mysql.connector.connect(
        host="localhost",
        user="tim",
        password="887414",
        database="LifeTableDB"
    )
    cursor = mydb.cursor()

    # 使用 Pandas 讀取 Excel 檔案
    try:
        df = pd.read_excel(excel_file, sheet_name='表1', skiprows=4)
        df.columns = ["年齡", "死亡機率", "生存數", "死亡數", "定常人口", "總人數", "平均餘命"]
    except Exception as e:
        raise ValueError(f"無法讀取 Excel 檔案: {e}")

    # 獲取 Excel 檔案名稱
    excel_name = excel_file.split('/')[-1].split('.')[0]

    # 找到三組數據的起始位置
    try:
        all_data_start = df[df['年齡'].astype(str).str.contains("0M")].index[0]
        male_data_start = df[df['年齡'].astype(str).str.contains("0M")].index[1]
        female_data_start = df[df['年齡'].astype(str).str.contains("0M")].index[2]
    except IndexError:
        raise ValueError("Excel 檔案格式不符合要求，無法找到分組數據起始位置。")

    # 分割數據
    df_all = df.iloc[all_data_start:male_data_start]
    df_male = df.iloc[male_data_start:female_data_start]
    df_female = df.iloc[female_data_start:]

    # 清理重複的標題行或空行
    def clean_data(df):
        return df[~df['年齡'].astype(str).str.contains("年齡|X", na=False)].dropna()

    df_all = clean_data(df_all)
    df_male = clean_data(df_male)
    df_female = clean_data(df_female)

    # 創建三個表格的通用函數
    def create_and_insert_table(table_name, data):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            年齡 VARCHAR(20),
            死亡機率 FLOAT,
            生存數 FLOAT,
            死亡數 FLOAT,
            定常人口 FLOAT,
            總人數 FLOAT,
            平均餘命 FLOAT
        )
        """
        cursor.execute(create_table_query)

        for _, row in data.iterrows():
            insert_query = f"""
            INSERT INTO {table_name} (年齡, 死亡機率, 生存數, 死亡數, 定常人口, 總人數, 平均餘命)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, tuple(row))

    # 處理三個數據表，使用動態命名
    data_tables = {
        f"{excel_name}_all": df_all,
        f"{excel_name}_male": df_male,
        f"{excel_name}_female": df_female
    }

    for table_name, data in data_tables.items():
        create_and_insert_table(table_name, data)

    # 提交更改並關閉連接
    mydb.commit()
    cursor.close()
    mydb.close()

def get_table_names():
    # 查詢資料庫中的所有資料表
    mydb = mysql.connector.connect(
        host="localhost",
        user="tim",
        password="887414",
        database="LifeTableDB"
    )
    cursor = mydb.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.close()
    mydb.close()
    return tables
