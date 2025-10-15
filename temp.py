import pandas as pd
import numpy as np

# 定义输入和输出文件名
# 请将 'your_new_large_file.csv' 替换为您实际的文件名
input_file = 'AGGREGATED_GENERATION_PER_TYPE_GENERATION_202312312300-202412312300.csv'
output_file = 'TotalGen.csv'

# 定义列名，与原始程序保持一致
COLUMNS = ['Time_Interval', 'Country_Area', 'Generation_Type', 'Generation_Value']

try:
    # Step 1: 读取 CSV 文件并处理混合类型问题
    # 使用 dtype=str 读取所有列，防止混合类型报错
    # 也可以直接在 read_csv 后使用 pd.to_numeric()
    df = pd.read_csv(
        input_file,
        header=None,
        usecols=[0, 1, 2, 3],
        names=COLUMNS,  # 直接指定列名
        skiprows=1 if pd.read_csv(input_file, nrows=1).iloc[0, 0] == COLUMNS[0] else 0  # 检查并跳过可能的标题行
    )

    # Step 2: 强制将 'Generation_Value' 列转换为数值类型
    # errors='coerce' 是关键：它会将所有无法转换为数字的值（如文本、空字符串）
    # 自动转换为 NaN (Not a Number，即缺失值)
    df['Generation_Value'] = pd.to_numeric(
        df['Generation_Value'],
        errors='coerce'
    )

    # 由于求和 (sum) 会自动忽略 NaN 值，所以无需手动删除或填充它们。
    # 如果您希望将缺失的发电量视为 0，可以添加：
    # df['Generation_Value'] = df['Generation_Value'].fillna(0)

    # Step 3: 按时间间隔和国家/地区分组求和
    df_aggregated = df.groupby(['Time_Interval', 'Country_Area'])['Generation_Value'].sum().reset_index()

    # 重命名聚合后的列
    df_aggregated.rename(columns={'Generation_Value': 'Total_Generation'}, inplace=True)

    # Step 4: 保存结果
    df_aggregated.to_csv(output_file, index=False, encoding='utf-8')

    print("-" * 50)
    print(f"✅ 成功！数据处理已完成。")
    print(f"聚合后的数据已保存到文件: {output_file}")
    print(f"最终表格列名: Time_Interval, Country_Area, Total_Generation")
    print("-" * 50)

except FileNotFoundError:
    print(f"错误：文件未找到。请确保文件名 '{input_file}' 正确且文件存在。")
except Exception as e:
    print(f"处理过程中发生未知错误: {e}")