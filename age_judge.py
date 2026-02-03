import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 数据预处理
df = pd.read_csv('2026_MCM_Problem_C_Data.csv')

# 找出所有评委分数列，按周分组
score_cols = [col for col in df.columns if 'judge' in col and 'score' in col]

# 按周提取列名
weeks = sorted(set(col.split('_')[0] for col in score_cols))  # ['week1', 'week2', ...]

# 计算每位选手的评委分数百分比（每周分数 / 该周所有选手总分）
percent_list = []
for week in weeks:
    week_cols = [col for col in score_cols if col.startswith(week + '_')]
    # 每位选手该周的总分（所有评委之和）
    week_total_per_person = df[week_cols].replace(0, np.nan).sum(axis=1)
    # 该周所有选手的总分
    week_total_all = week_total_per_person.sum()
    # 计算百分比（跳过该周总分为0的情况）
    if week_total_all > 0:
        week_percent = week_total_per_person / week_total_all * 100
    else:
        week_percent = pd.Series([np.nan] * len(df))
    percent_list.append(week_percent)

# 计算每位选手在所有活跃周的平均评委分数百分比
df['Avg_Judge_Percent'] = pd.concat(percent_list, axis=1).mean(axis=1)

# 准备数据，剔除缺失值
data = df[['celebrity_age_during_season', 'Avg_Judge_Percent', 'celebrity_industry']].dropna()
data.columns = ['Age', 'Score_Percent', 'Industry']

# --- 建模方式 1：线性回归 (Linear Trend) ---
X1 = sm.add_constant(data['Age'])
model1 = sm.OLS(data['Score_Percent'], X1).fit()

# --- 建模方式 2：二次多项式回归 (Non-linear Peak) ---
data['Age_Squared'] = data['Age'] ** 2
X2 = sm.add_constant(data[['Age', 'Age_Squared']])
model2 = sm.OLS(data['Score_Percent'], X2).fit()

print("--- 线性模型结果 ---")
print(model1.summary().tables[1])
print("\n--- 二次模型结果 ---")
print(model2.summary().tables[1])

# --- 可视化对比 ---
plt.figure(figsize=(10, 6))
sns.regplot(x='Age', y='Score_Percent', data=data, order=2, 
            scatter_kws={'alpha':0.3, 'color':'blue'}, 
            line_kws={'color':'red', 'label':'Quadratic Fit'})
plt.title('How Age Impacts Judge Score Percentage')
plt.xlabel('Celebrity Age')
plt.ylabel('Average Judge Score Percentage')
plt.legend()
plt.show()