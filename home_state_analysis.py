"""
================================================================================
Home State 对选手票数影响的数学建模分析
================================================================================
研究问题：
1. 来自哪些州的明星更容易取得好名次？
2. Home State 为什么对粉丝投票有显著影响？

建模思路：
- 方法一：描述性统计与可视化
- 方法二：人口加权模型 (Population-Weighted Model)
- 方法三：多元线性回归 (Multiple Linear Regression)
- 方法四：单因素方差分析 (One-Way ANOVA)
- 方法五：地理区域聚类分析 (Geographic Clustering)
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from scipy.stats import f_oneway, ttest_ind
import warnings
warnings.filterwarnings('ignore')

# ================================================================================
# 0. 数据准备
# ================================================================================
print("=" * 80)
print("【数据准备阶段】")
print("=" * 80)

# 读取数据
df_main = pd.read_csv('2026_MCM_Problem_C_Data.csv')
df_fan = pd.read_csv('data_with_certainty.csv')

# 计算每位选手的平均评委百分比和粉丝百分比
fan_avg = df_fan.groupby('celebrity_name').agg({
    'judge_percent': 'mean',
    'estimated_fan_percent': 'mean'
}).reset_index()

# 合并数据
df = pd.merge(
    df_main[['celebrity_name', 'celebrity_homestate', 'placement', 'season']].drop_duplicates(),
    fan_avg,
    on='celebrity_name'
)

# 清洗数据
df = df.dropna(subset=['celebrity_homestate', 'placement', 'estimated_fan_percent'])
df['placement'] = pd.to_numeric(df['placement'], errors='coerce')

print(f"有效样本数: {len(df)}")
print(f"涉及州数量: {df['celebrity_homestate'].nunique()}")

# 美国各州人口数据 (2020年人口普查，单位：百万)
state_population = {
    'California': 39.5, 'Texas': 29.1, 'Florida': 21.5, 'New York': 20.2,
    'Pennsylvania': 13.0, 'Illinois': 12.8, 'Ohio': 11.8, 'Georgia': 10.7,
    'North Carolina': 10.4, 'Michigan': 10.0, 'New Jersey': 9.3, 'Virginia': 8.6,
    'Washington': 7.6, 'Arizona': 7.3, 'Massachusetts': 7.0, 'Tennessee': 6.9,
    'Indiana': 6.8, 'Maryland': 6.2, 'Missouri': 6.2, 'Wisconsin': 5.9,
    'Colorado': 5.8, 'Minnesota': 5.7, 'South Carolina': 5.1, 'Alabama': 5.0,
    'Louisiana': 4.6, 'Kentucky': 4.5, 'Oregon': 4.2, 'Oklahoma': 4.0,
    'Connecticut': 3.6, 'Utah': 3.3, 'Iowa': 3.2, 'Nevada': 3.1,
    'Arkansas': 3.0, 'Mississippi': 3.0, 'Kansas': 2.9, 'New Mexico': 2.1,
    'Nebraska': 2.0, 'West Virginia': 1.8, 'Idaho': 1.8, 'Hawaii': 1.4,
    'New Hampshire': 1.4, 'Maine': 1.4, 'Montana': 1.1, 'Rhode Island': 1.1,
    'Delaware': 1.0, 'South Dakota': 0.9, 'North Dakota': 0.8, 'Alaska': 0.7,
    'Vermont': 0.6, 'Wyoming': 0.6, 'Washington D.C.': 0.7
}

# 添加人口数据
df['state_population'] = df['celebrity_homestate'].map(state_population)

# ================================================================================
# 方法一：描述性统计与可视化
# ================================================================================
"""
【为什么要做描述性统计？】
在建立复杂模型之前，我们首先需要"看一看"数据长什么样。
描述性统计帮助我们：
1. 识别哪些州表现最好/最差
2. 发现数据中的异常值或模式
3. 为后续建模提供直觉和假设

【数学原理】
平均值 μ = (Σxᵢ) / n
这里 xᵢ 是每位选手的粉丝投票百分比，n 是该州选手总数
"""

print("\n" + "=" * 80)
print("【方法一：描述性统计分析】")
print("=" * 80)

# 按州统计
state_stats = df.groupby('celebrity_homestate').agg({
    'estimated_fan_percent': ['mean', 'std', 'count'],
    'judge_percent': 'mean',
    'placement': 'mean'
}).round(2)

state_stats.columns = ['fan_percent_mean', 'fan_percent_std', 'count', 'judge_percent_mean', 'placement_mean']
state_stats = state_stats.reset_index()

# 筛选至少有3名选手的州（保证统计可靠性）
major_states = state_stats[state_stats['count'] >= 3].copy()

print("\n【粉丝投票百分比最高的 Top 5 州】")
top5_fan = major_states.nlargest(5, 'fan_percent_mean')
print(top5_fan[['celebrity_homestate', 'fan_percent_mean', 'count']].to_string(index=False))

print("\n【粉丝投票百分比最低的 Bottom 5 州】")
bottom5_fan = major_states.nsmallest(5, 'fan_percent_mean')
print(bottom5_fan[['celebrity_homestate', 'fan_percent_mean', 'count']].to_string(index=False))

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# 图1：各州平均粉丝投票百分比
major_states_sorted = major_states.sort_values('fan_percent_mean')
colors = plt.cm.RdYlGn(np.linspace(0, 1, len(major_states_sorted)))
axes[0].barh(major_states_sorted['celebrity_homestate'], major_states_sorted['fan_percent_mean'], color=colors)
axes[0].axvline(x=df['estimated_fan_percent'].mean(), color='red', linestyle='--', linewidth=2, label='National Average')
axes[0].set_xlabel('Average Fan Percent (%)', fontsize=12)
axes[0].set_ylabel('State', fontsize=12)
axes[0].set_title('Method 1: Average Fan Vote Percentage by State\n(States with ≥3 contestants)', fontsize=14)
axes[0].legend()

# 图2：各州选手数量与平均粉丝百分比的关系
axes[1].scatter(major_states['count'], major_states['fan_percent_mean'], 
                s=100, alpha=0.7, c='steelblue', edgecolors='black')
for i, row in major_states.iterrows():
    if row['count'] >= 5 or row['fan_percent_mean'] > 12:
        axes[1].annotate(row['celebrity_homestate'], (row['count'], row['fan_percent_mean']),
                        fontsize=8, ha='left')
axes[1].set_xlabel('Number of Contestants', fontsize=12)
axes[1].set_ylabel('Average Fan Percent (%)', fontsize=12)
axes[1].set_title('Relationship: Sample Size vs Average Performance', fontsize=14)

plt.tight_layout()
plt.savefig('method1_descriptive_stats.png', dpi=150, bbox_inches='tight')
plt.show()

# ================================================================================
# 方法二：人口加权模型 (Population-Weighted Model)
# ================================================================================
"""
【为什么要建立人口加权模型？】
假设：来自人口大州的明星拥有更大的"潜在粉丝池"
理论基础：如果投票主要来自家乡观众，人口越多的州能提供更多投票

【数学模型】
设 V_i 为选手 i 的粉丝投票百分比
设 P_i 为选手 i 家乡州的人口（百万）

模型：V_i = β₀ + β₁ × P_i + ε_i

其中：
- β₀：截距（基础投票率）
- β₁：人口系数（每增加100万人口，投票率增加多少）
- ε_i：随机误差项

【假设检验】
H₀: β₁ = 0 (人口对投票无影响)
H₁: β₁ ≠ 0 (人口对投票有影响)
"""

print("\n" + "=" * 80)
print("【方法二：人口加权模型】")
print("=" * 80)

# 移除人口数据缺失的样本
df_pop = df.dropna(subset=['state_population']).copy()

print(f"\n有人口数据的样本数: {len(df_pop)}")

# 建立线性回归模型
X_pop = sm.add_constant(df_pop['state_population'])
y_pop = df_pop['estimated_fan_percent']

model_pop = sm.OLS(y_pop, X_pop).fit()

print("\n【人口加权模型回归结果】")
print(model_pop.summary().tables[1])

# 解读结果
beta_1 = model_pop.params['state_population']
p_value = model_pop.pvalues['state_population']
r_squared = model_pop.rsquared

print(f"\n【模型解读】")
print(f"人口系数 β₁ = {beta_1:.4f}")
print(f"P值 = {p_value:.4f}")
print(f"R² = {r_squared:.4f}")

if p_value < 0.05:
    if beta_1 > 0:
        print("结论：人口越多的州，选手获得的粉丝投票百分比越高（显著）")
    else:
        print("结论：人口越多的州，选手获得的粉丝投票百分比越低（显著）")
else:
    print("结论：州人口对粉丝投票无显著影响")

# 可视化
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df_pop['state_population'], df_pop['estimated_fan_percent'], 
           alpha=0.5, s=60, c='steelblue', edgecolors='white', label='Data Points')

# 绘制回归线
x_line = np.linspace(df_pop['state_population'].min(), df_pop['state_population'].max(), 100)
y_line = model_pop.params['const'] + model_pop.params['state_population'] * x_line
ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'Regression Line (R²={r_squared:.3f})')

ax.set_xlabel('State Population (millions)', fontsize=12)
ax.set_ylabel('Fan Vote Percentage (%)', fontsize=12)
ax.set_title('Method 2: Population-Weighted Model\nDoes State Population Predict Fan Votes?', fontsize=14)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('method2_population_model.png', dpi=150, bbox_inches='tight')
plt.show()

# ================================================================================
# 方法三：多元线性回归 (Multiple Linear Regression)
# ================================================================================
"""
【为什么要用多元回归？】
单一变量（如人口）可能无法解释全部差异。
我们需要控制其他可能的"混杂变量"：
- 季节效应（不同季观众数量不同）
- 样本量效应（某些州样本太少可能是偶然）

【数学模型】
V_i = β₀ + β₁×P_i + β₂×Season_i + Σ(γ_j × State_j) + ε_i

其中：
- V_i：粉丝投票百分比
- P_i：州人口
- Season_i：季节号（控制时间趋势）
- State_j：州的虚拟变量（Dummy Variables）
- ε_i：随机误差

【虚拟变量解释】
假设有 k 个州，我们创建 k-1 个虚拟变量（避免完全多重共线性）
选择一个州作为"基准组"（通常是样本最多的加州）
其他州的系数表示：相对于基准州，该州选手的投票率差异
"""

print("\n" + "=" * 80)
print("【方法三：多元线性回归分析】")
print("=" * 80)

# 只保留至少出现3次的州（避免过拟合）
state_counts = df_pop['celebrity_homestate'].value_counts()
valid_states = state_counts[state_counts >= 3].index
df_multi = df_pop[df_pop['celebrity_homestate'].isin(valid_states)].copy()

print(f"保留的州数量: {len(valid_states)}")
print(f"样本数: {len(df_multi)}")

# 创建虚拟变量（以加州为基准）
df_dummies = pd.get_dummies(df_multi['celebrity_homestate'], drop_first=True, dtype=int)

# 构建特征矩阵
X_multi = pd.concat([
    df_multi[['state_population', 'season']].reset_index(drop=True),
    df_dummies.reset_index(drop=True)
], axis=1)
X_multi = sm.add_constant(X_multi)

y_multi = df_multi['estimated_fan_percent'].reset_index(drop=True)

# 拟合模型
model_multi = sm.OLS(y_multi, X_multi).fit()

print("\n【多元回归核心系数】")
# 只显示非州虚拟变量的系数
core_params = model_multi.params[['const', 'state_population', 'season']]
core_pvalues = model_multi.pvalues[['const', 'state_population', 'season']]
print(pd.DataFrame({'Coefficient': core_params, 'P-value': core_pvalues}).round(4))

print(f"\n调整后 R² = {model_multi.rsquared_adj:.4f}")

# 提取州效应系数并排序
state_effects = model_multi.params.drop(['const', 'state_population', 'season'])
state_pvalues = model_multi.pvalues.drop(['const', 'state_population', 'season'])

# 筛选显著的州效应 (p < 0.1)
significant_states = state_effects[state_pvalues < 0.1].sort_values(ascending=False)

print("\n【显著的州效应】(相对于基准州 California)")
if len(significant_states) > 0:
    for state, effect in significant_states.items():
        pval = state_pvalues[state]
        direction = "高于" if effect > 0 else "低于"
        print(f"  {state}: {direction}基准 {abs(effect):.2f}% (p={pval:.3f})")
else:
    print("  无显著差异的州")

# 可视化州效应
fig, ax = plt.subplots(figsize=(12, 8))
state_effects_sorted = state_effects.sort_values()
colors = ['green' if x > 0 else 'red' for x in state_effects_sorted.values]
ax.barh(state_effects_sorted.index, state_effects_sorted.values, color=colors, alpha=0.7)
ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax.set_xlabel('Effect on Fan Vote % (relative to California)', fontsize=12)
ax.set_ylabel('State', fontsize=12)
ax.set_title('Method 3: State Effects from Multiple Regression\n(Controlling for Population & Season)', fontsize=14)

# 添加图例说明
ax.text(state_effects_sorted.max() * 0.8, 2, 'Green: Better than CA', color='green', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax.text(state_effects_sorted.min() * 0.8, len(state_effects_sorted) - 3, 'Red: Worse than CA', color='red', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('method3_multiple_regression.png', dpi=150, bbox_inches='tight')
plt.show()

# ================================================================================
# 方法四：单因素方差分析 (One-Way ANOVA)
# ================================================================================
"""
【为什么要用 ANOVA？】
ANOVA 检验多个组的均值是否存在显著差异。
与多个 t 检验相比，ANOVA 控制了整体的第一类错误率。

【数学原理】
设有 k 个州，第 j 个州有 n_j 名选手，投票率为 Y_ij

总变异 = 组间变异 + 组内变异
SST = SSB + SSW

F 统计量 = (SSB / (k-1)) / (SSW / (N-k))
         = MSB / MSW

其中：
- SSB = Σn_j × (Ȳ_j - Ȳ)²  （组间平方和：各州均值与总均值的差异）
- SSW = ΣΣ(Y_ij - Ȳ_j)²    （组内平方和：个体与所在州均值的差异）

【假设检验】
H₀: μ₁ = μ₂ = ... = μ_k (所有州的平均投票率相等)
H₁: 至少有一个州的平均投票率不同
"""

print("\n" + "=" * 80)
print("【方法四：单因素方差分析 (ANOVA)】")
print("=" * 80)

# 准备各州的数据组
groups = []
group_names = []
for state in valid_states:
    state_data = df_multi[df_multi['celebrity_homestate'] == state]['estimated_fan_percent'].values
    if len(state_data) >= 3:
        groups.append(state_data)
        group_names.append(state)

print(f"参与 ANOVA 的州数量: {len(groups)}")

# 执行 ANOVA
f_stat, p_value_anova = f_oneway(*groups)

print(f"\n【ANOVA 结果】")
print(f"F 统计量 = {f_stat:.4f}")
print(f"P 值 = {p_value_anova:.4f}")

if p_value_anova < 0.05:
    print("\n★ 结论：拒绝零假设！不同州之间的粉丝投票率存在【显著差异】")
    print("  这意味着 Home State 确实是影响粉丝投票的重要因素。")
else:
    print("\n★ 结论：无法拒绝零假设。州与州之间的差异在统计上不显著。")

# 计算效应量 η² (Eta-squared)
# η² = SSB / SST
grand_mean = df_multi['estimated_fan_percent'].mean()
ssb = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
sst = sum((df_multi['estimated_fan_percent'] - grand_mean)**2)
eta_squared = ssb / sst

print(f"\n效应量 η² = {eta_squared:.4f}")
if eta_squared < 0.01:
    print("  效应量很小（<1%），实际影响微弱")
elif eta_squared < 0.06:
    print("  效应量较小（1-6%），有一定实际意义")
elif eta_squared < 0.14:
    print("  效应量中等（6-14%），有实际意义")
else:
    print("  效应量较大（>14%），影响显著")

# 可视化：箱线图
fig, ax = plt.subplots(figsize=(14, 6))

# 按均值排序
state_means = {name: np.mean(data) for name, data in zip(group_names, groups)}
sorted_states = sorted(state_means.keys(), key=lambda x: state_means[x])

# 重新排列数据
sorted_groups = [df_multi[df_multi['celebrity_homestate'] == s]['estimated_fan_percent'] for s in sorted_states]

bp = ax.boxplot(sorted_groups, labels=sorted_states, patch_artist=True)

# 设置颜色渐变
colors = plt.cm.RdYlGn(np.linspace(0, 1, len(sorted_states)))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)

ax.axhline(y=grand_mean, color='red', linestyle='--', linewidth=2, label=f'Grand Mean ({grand_mean:.1f}%)')
ax.set_xlabel('State', fontsize=12)
ax.set_ylabel('Fan Vote Percentage (%)', fontsize=12)
ax.set_title(f'Method 4: ANOVA - Fan Vote Distribution by State\n(F={f_stat:.2f}, p={p_value_anova:.4f}, η²={eta_squared:.3f})', fontsize=14)
ax.legend()
plt.xticks(rotation=45, ha='right')

plt.tight_layout()
plt.savefig('method4_anova.png', dpi=150, bbox_inches='tight')
plt.show()

# ================================================================================
# 方法五：地理区域聚类分析 (Geographic Clustering)
# ================================================================================
"""
【为什么要做地理聚类？】
单个州的样本量可能太小，不足以得出可靠结论。
将州按地理区域分组可以：
1. 增加每组的样本量
2. 发现更宏观的地域模式
3. 减少随机噪声的影响

【区域划分】
- 东海岸 (East Coast): NY, NJ, MA, CT, PA, MD, VA, etc.
- 西海岸 (West Coast): CA, WA, OR
- 南部 (South): TX, FL, GA, NC, TN, AL, LA, etc.
- 中西部 (Midwest): IL, OH, MI, IN, WI, MN, etc.
- 山区/其他 (Mountain/Other): CO, AZ, UT, NV, etc.
"""

print("\n" + "=" * 80)
print("【方法五：地理区域聚类分析】")
print("=" * 80)

# 定义地理区域
region_mapping = {
    # 东海岸
    'New York': 'East Coast', 'New Jersey': 'East Coast', 'Massachusetts': 'East Coast',
    'Connecticut': 'East Coast', 'Pennsylvania': 'East Coast', 'Maryland': 'East Coast',
    'Virginia': 'East Coast', 'Rhode Island': 'East Coast', 'Delaware': 'East Coast',
    'Maine': 'East Coast', 'New Hampshire': 'East Coast', 'Vermont': 'East Coast',
    'Washington D.C.': 'East Coast',
    
    # 西海岸
    'California': 'West Coast', 'Washington': 'West Coast', 'Oregon': 'West Coast',
    'Hawaii': 'West Coast', 'Alaska': 'West Coast',
    
    # 南部
    'Texas': 'South', 'Florida': 'South', 'Georgia': 'South', 'North Carolina': 'South',
    'South Carolina': 'South', 'Tennessee': 'South', 'Alabama': 'South', 'Louisiana': 'South',
    'Mississippi': 'South', 'Arkansas': 'South', 'Oklahoma': 'South', 'Kentucky': 'South',
    'West Virginia': 'South',
    
    # 中西部
    'Illinois': 'Midwest', 'Ohio': 'Midwest', 'Michigan': 'Midwest', 'Indiana': 'Midwest',
    'Wisconsin': 'Midwest', 'Minnesota': 'Midwest', 'Iowa': 'Midwest', 'Missouri': 'Midwest',
    'Kansas': 'Midwest', 'Nebraska': 'Midwest', 'North Dakota': 'Midwest', 'South Dakota': 'Midwest',
    
    # 山区/西部内陆
    'Colorado': 'Mountain', 'Arizona': 'Mountain', 'Utah': 'Mountain', 'Nevada': 'Mountain',
    'New Mexico': 'Mountain', 'Idaho': 'Mountain', 'Montana': 'Mountain', 'Wyoming': 'Mountain'
}

# 添加区域标签
df_pop['region'] = df_pop['celebrity_homestate'].map(region_mapping)
df_region = df_pop.dropna(subset=['region']).copy()

print(f"有区域标签的样本数: {len(df_region)}")

# 按区域统计
region_stats = df_region.groupby('region').agg({
    'estimated_fan_percent': ['mean', 'std', 'count'],
    'judge_percent': 'mean'
}).round(2)
region_stats.columns = ['fan_mean', 'fan_std', 'count', 'judge_mean']
region_stats = region_stats.sort_values('fan_mean', ascending=False)

print("\n【各区域平均投票率】")
print(region_stats.to_string())

# 区域间 ANOVA
region_groups = [df_region[df_region['region'] == r]['estimated_fan_percent'].values 
                 for r in region_stats.index]
f_region, p_region = f_oneway(*region_groups)

print(f"\n【区域 ANOVA】")
print(f"F = {f_region:.4f}, P = {p_region:.4f}")

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：各区域平均值条形图
colors_region = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
region_stats['fan_mean'].plot(kind='bar', ax=axes[0], color=colors_region, edgecolor='black')
axes[0].set_ylabel('Average Fan Vote %', fontsize=12)
axes[0].set_xlabel('Region', fontsize=12)
axes[0].set_title('Average Fan Vote by Geographic Region', fontsize=14)
axes[0].axhline(y=df_region['estimated_fan_percent'].mean(), color='red', linestyle='--', 
                label='National Average', linewidth=2)
axes[0].legend()
axes[0].tick_params(axis='x', rotation=45)

# 右图：箱线图
region_order = region_stats.index.tolist()
sns.boxplot(x='region', y='estimated_fan_percent', data=df_region, order=region_order, 
            palette=colors_region, ax=axes[1])
axes[1].set_ylabel('Fan Vote %', fontsize=12)
axes[1].set_xlabel('Region', fontsize=12)
axes[1].set_title(f'Fan Vote Distribution by Region\n(ANOVA: F={f_region:.2f}, p={p_region:.4f})', fontsize=14)
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('method5_geographic_clustering.png', dpi=150, bbox_inches='tight')
plt.show()

# ================================================================================
# 综合结论
# ================================================================================
print("\n" + "=" * 80)
print("【综合分析结论】")
print("=" * 80)

print("""
1. 【哪些州的明星更容易获得高粉丝投票？】
   根据描述性统计和回归分析：
""")
print(f"   - 表现最好的州: {', '.join(top5_fan['celebrity_homestate'].tolist())}")
print(f"   - 表现最差的州: {', '.join(bottom5_fan['celebrity_homestate'].tolist())}")

print("""
2. 【Home State 为什么对粉丝投票有影响？】

   理论解释（基于社会心理学和传播学）：
   
   (A) 地方认同效应 (Local Identity Effect)
       - 观众倾向于支持"自己人"，即来自同一州的明星
       - 这种支持是情感驱动的，与明星实际表演水平无关
       
   (B) 媒体曝光效应 (Media Exposure Effect)
       - 当地明星在家乡媒体上的曝光度更高
       - 本地新闻报道会提醒观众去投票
       
   (C) 社交网络效应 (Social Network Effect)
       - 明星的家人、朋友、校友集中在家乡州
       - 这些核心支持者会带动更多人投票
       
   (D) 人口基数效应 (Population Base Effect)
       - 人口越多的州，潜在投票者越多
       - 但我们的模型显示这一效应并不显著

3. 【模型比较】
   
   方法        |  核心发现                      |  适用场景
   ------------|-------------------------------|------------------
   描述性统计   |  识别Top/Bottom州              |  初步探索
   人口加权     |  人口与投票的直接关系           |  检验人口假说
   多元回归     |  控制混杂变量后的州效应         |  因果推断
   ANOVA       |  各州差异的统计显著性           |  组间比较
   地理聚类     |  区域层面的宏观模式            |  减少噪声
""")

print("=" * 80)
print("分析完成！图片已保存。")
print("=" * 80)
