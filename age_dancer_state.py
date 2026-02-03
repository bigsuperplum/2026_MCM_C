import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# 读取数据
df = pd.read_csv('2026_MCM_Problem_C_Data.csv')

# 数据清洗：确保排名是数字
df['placement'] = pd.to_numeric(df['placement'], errors='coerce')
df['age'] = df['celebrity_age_during_season']
# 去除排名为空的数据
df_clean = df.dropna(subset=['placement', 'age'])

# ==========================================
# 方式一：分箱统计 (Binning)
# ==========================================
bins = [0, 25, 40, 55, 100]
labels = ['14-25 (Gen Z)', '26-40 (Millennials)', '41-55 (Gen X)', '55+ (Boomers)']
df_clean['age_group'] = pd.cut(df_clean['age'], bins=bins, labels=labels)

plt.figure(figsize=(10, 6))
# 画箱线图：展示每个年龄段排名的分布情况
sns.boxplot(x='age_group', y='placement', data=df_clean, palette="Set2")
plt.title('Placement Distribution by Age Group')
plt.ylabel('Placement')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# ==========================================
# 方式二：二次回归 (Quadratic Regression)
# ==========================================
# 公式: Placement = b0 + b1*Age + b2*Age^2
X = df_clean['age']
y = df_clean['placement']

# 构造 X 矩阵：包含 Age 和 Age^2
X_poly = pd.DataFrame({'age': X, 'age_sq': X**2})
X_poly = sm.add_constant(X_poly)

model = sm.OLS(y, X_poly).fit()
print(model.summary())

# 画出拟合曲线
plt.figure(figsize=(10, 6))
plt.scatter(df_clean['age'], df_clean['placement'], alpha=0.5, color='gray', label='Actual Data')

# 生成预测线
age_range = np.linspace(df_clean['age'].min(), df_clean['age'].max(), 100)
pred_X = sm.add_constant(pd.DataFrame({'age': age_range, 'age_sq': age_range**2}))
preds = model.predict(pred_X)

plt.plot(age_range, preds, color='red', linewidth=3, label='Quadratic Fit')
plt.title('Regression Analysis: Optimal Age for Winning')
plt.xlabel('Celebrity Age')
plt.ylabel('Predicted Placement')
plt.legend()
plt.show()

# 计算理论最佳年龄 (-b1 / 2*b2)
b1 = model.params['age']
b2 = model.params['age_sq']
optimal_age = -b1 / (2 * b2)
print(f"根据模型预测，理论上获得最好名次的最佳年龄是: {optimal_age:.1f} 岁")

# 接上面的代码

# ==========================================
# 方式一：历史均值排行
# ==========================================
# 计算每个舞者的平均排名和参赛次数
pro_stats = df_clean.groupby('ballroom_partner')['placement'].agg(['mean', 'count'])

# 只看至少参加过 5 个赛季的资深舞者 (避免偶然性)
veteran_pros = pro_stats[pro_stats['count'] >= 5].sort_values('mean')

plt.figure(figsize=(12, 6))
# 画水平条形图，让人名完整显示
veteran_pros['mean'].plot(kind='barh', color='skyblue')
plt.title('Top Pro Dancers by Average Placement')
plt.xlabel('Average Placement')
plt.ylabel('Pro Dancer')
plt.axvline(x=df_clean['placement'].mean(), color='r', linestyle='--', label='League Average')
plt.legend()
plt.tight_layout()
plt.show()

# ==========================================
# 方式二：相对能力分析 (控制年龄变量)
# ==========================================
# 1. 训练一个基准模型：只用年龄预测排名
# Placement_pred = f(Age)
model_base = sm.OLS(df_clean['placement'], sm.add_constant(df_clean[['age']])).fit()
df_clean['expected_placement'] = model_base.predict(sm.add_constant(df_clean[['age']]))
# 2. 计算“增益” (Value Added)
# 实际排名 3，预测排名 8 -> 增益 = 8 - 3 = 5 (提升了5名，正数代表厉害)
df_clean['pro_value_added'] = df_clean['expected_placement'] - df_clean['placement']

# 3. 统计舞者的平均增益
pro_value = df_clean.groupby('ballroom_partner')['pro_value_added'].agg(['mean', 'count'])
top_value_pros = pro_value[pro_value['count'] >= 5].sort_values('mean', ascending=False) # 越大越好

print("\n=== '带飞'能力最强的舞者 (考虑明星年龄后) ===")
print(top_value_pros.head(5))

plt.figure(figsize=(12, 6))
top_value_pros['mean'].head(10).plot(kind='barh', color='lightgreen')
plt.title('Pro Dancers Adding Most Value (Outperforming Expectations)')
plt.xlabel('Placement Improvement')
plt.ylabel('Pro Dancer')
plt.tight_layout()
plt.show()

# 接上面的代码

# ==========================================
# 方式一：Top States 表现分析 (评委百分比 & 粉丝百分比)
# ==========================================
# 读取包含 judge_percent 和 estimated_fan_percent 的数据
df_fan = pd.read_csv('data_with_certainty.csv')

# 计算每位选手在整个赛季的平均百分比
fan_avg = df_fan.groupby('celebrity_name').agg({
    'judge_percent': 'mean',
    'estimated_fan_percent': 'mean'
}).reset_index()

# 与主数据合并获取州信息
df_merged = pd.merge(df[['celebrity_name', 'celebrity_homestate']].drop_duplicates(), 
                     fan_avg, on='celebrity_name')

# 清洗：处理缺失值
df_state = df_merged.dropna(subset=['celebrity_homestate'])

# 统计每个州的平均百分比和人数
state_stats = df_state.groupby('celebrity_homestate').agg({
    'judge_percent': 'mean',
    'estimated_fan_percent': 'mean',
    'celebrity_name': 'count'
}).rename(columns={'celebrity_name': 'count'})

# 筛选产生过至少 3 名选手的州
major_states = state_stats[state_stats['count'] >= 3].sort_values('judge_percent', ascending=False)

print("\n=== 表现最好的州 (至少3名选手) - 按评委百分比 ===")
print(major_states.head(5))

# 绘制双条形图：评委百分比和粉丝百分比
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 左图：评委百分比
major_states_sorted_judge = major_states.sort_values('judge_percent')
major_states_sorted_judge['judge_percent'].plot(kind='barh', color='steelblue', ax=axes[0])
axes[0].set_title('Average Judge Percent by Home State')
axes[0].set_xlabel('Average Judge Percent (%)')
axes[0].set_ylabel('State')
axes[0].axvline(x=df_state['judge_percent'].mean(), color='r', linestyle='--', label='National Average')
axes[0].legend()

# 右图：粉丝百分比
major_states_sorted_fan = major_states.sort_values('estimated_fan_percent')
major_states_sorted_fan['estimated_fan_percent'].plot(kind='barh', color='coral', ax=axes[1])
axes[1].set_title('Average Fan Percent by Home State')
axes[1].set_xlabel('Average Fan Percent (%)')
axes[1].set_ylabel('State')
axes[1].axvline(x=df_state['estimated_fan_percent'].mean(), color='r', linestyle='--', label='National Average')
axes[1].legend()

plt.tight_layout()
plt.show()

# ==========================================
# 方式二：人口大州 vs 其他州 (假设检验) - 评委百分比 & 粉丝百分比
# ==========================================
# 假设人口大州/娱乐重镇有：California, New York, Texas, Florida
big_states = ['California', 'New York', 'Texas', 'Florida']

# 创建一个新列：是否来自大州
df_state['is_big_state'] = df_state['celebrity_homestate'].apply(lambda x: 'Big 4 State' if x in big_states else 'Other')

# 绘图对比：两个子图
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# 左图：评委百分比
sns.boxplot(x='is_big_state', y='judge_percent', data=df_state, ax=axes[0])
axes[0].set_title('Judge Percent: Big 4 States vs Others')
axes[0].set_ylabel('Judge Percent (%)')
axes[0].set_xlabel('')

# 右图：粉丝百分比
sns.boxplot(x='is_big_state', y='estimated_fan_percent', data=df_state, ax=axes[1])
axes[1].set_title('Fan Percent: Big 4 States vs Others')
axes[1].set_ylabel('Fan Percent (%)')
axes[1].set_xlabel('')

plt.tight_layout()
plt.show()

# 进行 T检验
from scipy.stats import ttest_ind

# 评委百分比 T检验
group1_judge = df_state[df_state['is_big_state'] == 'Big 4 State']['judge_percent']
group2_judge = df_state[df_state['is_big_state'] == 'Other']['judge_percent']
t_stat_judge, p_val_judge = ttest_ind(group1_judge, group2_judge)

# 粉丝百分比 T检验
group1_fan = df_state[df_state['is_big_state'] == 'Big 4 State']['estimated_fan_percent']
group2_fan = df_state[df_state['is_big_state'] == 'Other']['estimated_fan_percent']
t_stat_fan, p_val_fan = ttest_ind(group1_fan, group2_fan)

print(f"\n评委百分比 T-test 结果: p-value = {p_val_judge:.4f}")
if p_val_judge < 0.05:
    print("结论：来自人口大州的选手评委分数显著不同！")
else:
    print("结论：评委分数的地域差异在统计上不显著。")

print(f"\n粉丝百分比 T-test 结果: p-value = {p_val_fan:.4f}")
if p_val_fan < 0.05:
    print("结论：来自人口大州的选手粉丝投票显著不同！")
else:
    print("结论：粉丝投票的地域差异在统计上不显著。")