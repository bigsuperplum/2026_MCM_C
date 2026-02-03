import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures

# 1. 加载数据
df_main = pd.read_csv('2026_MCM_Problem_C_Data.csv')
df_fan = pd.read_csv('estimated_fan_data.csv')

# 2. 合并数据 (假设通过 celebrity_name 和 season 关联)
# 粉丝数据通常是按周分的，我们取每个选手在整个赛季的平均得票率
fan_avg = df_fan.groupby(['celebrity_name', 'season'])['estimated_fan_percent'].mean().reset_index()
merged_data = pd.merge(df_main, fan_avg, on=['celebrity_name', 'season'])

# 准备建模数据
data = merged_data[['celebrity_age_during_season', 'estimated_fan_percent', 'placement']].dropna()
data.columns = ['Age', 'FanPercent', 'Rank']

# --- 方法一：多项式回归 (探究是否存在“黄金年龄”) ---
X = data[['Age']]
y = data['FanPercent']

# 增加二次项 (Age^2)
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)

model = sm.OLS(y, X_poly).fit()
print("多项式回归总结：")
print(model.summary())

# --- 可视化 ---
fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(x='Age', y='FanPercent', data=data, order=2, 
            scatter_kws={'alpha':0.5}, 
            line_kws={'color':'red', 'label':'Quadratic Fit'},
            ax=ax)
plt.title('How Age Impacts Estimated Fan Percent')
plt.xlabel('Celebrity Age')
plt.ylabel('Estimated Fan Percent')

# 将 y 轴刻度除以 100
from matplotlib.ticker import FuncFormatter
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y/100:.1f}'))

plt.legend(loc='upper right')
plt.show()

# --- 方法二：年龄段对比 (分组分析) ---
bins = [0, 25, 40, 60, 100]
labels = ['Young (<25)', 'Prime (25-40)', 'Mature (40-60)', 'Senior (>60)']
data['AgeGroup'] = pd.cut(data['Age'], bins=bins, labels=labels)

age_impact = data.groupby('AgeGroup', observed=True)['FanPercent'].mean().sort_values(ascending=False)
print("\n不同年龄段的平均得票率：")
print(age_impact)