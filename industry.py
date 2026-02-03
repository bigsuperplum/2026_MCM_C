import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats

def analyze_industry_impact():
    print("="*50)
    print("开始分析：Celebrity Industry 对比赛排名的影响")
    print("="*50)

    # ---------------------------------------------------------
    # 0. 数据读取与预处理
    # ---------------------------------------------------------
    filename = '2026_MCM_Problem_C_Data.csv'
    try:
        df = pd.read_csv(filename)
        # 清除列名首尾空格，防止 KeyError
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        return

    # 转换排名为数字
    df['placement'] = pd.to_numeric(df['placement'], errors='coerce')

    # 去除 'placement' 或 'celebrity_industry' 为空的行
    df_clean = df.dropna(subset=['placement', 'celebrity_industry']).copy()

    # --- 关键步骤：行业归类 ---
    # 许多行业只出现过1-2次，需要将它们归类为 'Other'，否则分析会很乱
    # 统计每个行业的人数
    industry_counts = df_clean['celebrity_industry'].value_counts()
    
    # 选取人数最多的前 6 个行业 (例如 Actor, Athlete, Singer 等)
    top_n = 6
    top_industries = industry_counts.nlargest(top_n).index.tolist()
    
    # 创建新列 'industry_group'
    df_clean['industry_group'] = df_clean['celebrity_industry'].apply(
        lambda x: x if x in top_industries else 'Other'
    )

    print(f"数据清洗完毕，共保留 {len(df_clean)} 条有效记录。")
    print(f"保留的主要行业类别: {top_industries}")
    print("-" * 50)

    # ---------------------------------------------------------
    # 方法一：分组统计与可视化 (Descriptive Statistics)
    # ---------------------------------------------------------
    print("\n【方法一：分组均值统计】")
    
    # 计算均值并排序
    rank_stats = df_clean.groupby('industry_group')['placement'].mean().sort_values()
    print("各行业平均排名 (数字越小越好):")
    print(rank_stats)

    # 绘图：箱线图
    plt.figure(figsize=(12, 6))
    # 按中位数排序箱线图顺序
    order = df_clean.groupby('industry_group')['placement'].median().sort_values().index
    
    sns.boxplot(x='industry_group', y='placement', data=df_clean, order=order, palette="Set3")
    plt.title('Method 1: Final Placement Distribution by Industry')
    plt.ylabel('Rank (1 = Winner)')
    plt.xlabel('Industry Group')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.show()

    # ---------------------------------------------------------
    # 方法二：虚拟变量回归分析 (Dummy Variable Regression)
    # ---------------------------------------------------------
    print("\n" + "-" * 50)
    print("【方法二：虚拟变量回归分析】")

    # One-Hot 编码
    # drop_first=True 表示去掉第一个类别作为“基准组”(Baseline)，通常是字母顺序排第一的，比如 Actor
    df_dummies = pd.get_dummies(df_clean['industry_group'], drop_first=True, dtype=int)
    
    # 准备回归数据
    X = sm.add_constant(df_dummies) # 添加截距项
    y = df_clean['placement']

    # 拟合 OLS 模型
    model = sm.OLS(y, X).fit()
    
    print(model.summary())

    # 绘图：系数可视化
    params = model.params.drop('const') # 去掉截距，只看行业系数
    
    plt.figure(figsize=(10, 6))
    # 先排序，再根据排序后的值分配颜色
    params_sorted = params.sort_values()
    colors = ['green' if x < 0 else 'red' for x in params_sorted.values]
    params_sorted.plot(kind='barh', color=colors)
    
    plt.axvline(x=0, color='black', linestyle='-', linewidth=1)
    plt.title('Method 2: Regression Coefficients (Impact on Rank)')
    plt.xlabel('Coefficient Value (Negative = Better Performance)')
    plt.ylabel('Industry (Relative to Baseline)')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # 添加注释（使用白色背景框使文字可见）
    plt.text(0.5 * params_sorted.max(), len(params_sorted)-1, 'Red: Worse than Baseline', 
             color='red', fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    plt.text(0.5 * params_sorted.min(), 0, 'Green: Better than Baseline', 
             color='green', fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.show()

    # ---------------------------------------------------------
    # 方法三：单因素方差分析 (One-Way ANOVA)
    # ---------------------------------------------------------
    print("\n" + "-" * 50)
    print("【方法三：单因素方差分析 ANOVA】")

    # 提取各组数据
    groups = []
    unique_inds = df_clean['industry_group'].unique()
    for ind in unique_inds:
        groups.append(df_clean[df_clean['industry_group'] == ind]['placement'].values)

    # 计算 F值 和 P值
    f_stat, p_value = stats.f_oneway(*groups)

    print(f"F-statistic: {f_stat:.4f}")
    print(f"P-value:     {p_value:.4e}")  # 科学计数法

    print("\n--- 结论判定 ---")
    if p_value < 0.05:
        print("★ P值 < 0.05，拒绝零假设。")
        print("结论：不同行业的明星在比赛排名上存在【显著差异】。")
        print("这意味着“行业”确实是影响比赛结果的一个重要因素，不仅仅是偶然现象。")
    else:
        print("★ P值 >= 0.05，无法拒绝零假设。")
        print("结论：不同行业的明星排名差异在统计上不显著，可能是由随机波动引起的。")
    print("="*50)

if __name__ == "__main__":
    analyze_industry_impact()