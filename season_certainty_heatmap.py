"""
第27季每一周每位选手置信度热力图
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 读取数据
df = pd.read_csv('data_with_certainty_v3.csv')

SEASON = 34

# 筛选第27季
df_s27 = df[df['season'] == SEASON].copy()

# 创建透视表：行是选手，列是周数，值是置信度
pivot_table = df_s27.pivot_table(
    index='celebrity_name', 
    columns='week', 
    values='certainty_final',
    aggfunc='mean'
)

# 按照赛季最终排名 (season_rank) 排序
# 获取每位选手的最终排名（取最后一周的 season_rank）
season_rank = df_s27.groupby('celebrity_name')['season_rank'].last().sort_values()
pivot_table = pivot_table.reindex(season_rank.index)

# 绘制热力图
plt.figure(figsize=(14, 10))
ax = sns.heatmap(
    pivot_table,
    annot=True,
    fmt='.2f',
    cmap='RdYlGn',  # 红黄绿色阶：低置信度红色，高置信度绿色
    vmin=0, vmax=1,
    linewidths=0.5,
    linecolor='white',
    cbar_kws={'label': 'Certainty', 'shrink': 0.8}
)

# 设置标签
plt.xlabel('Week', fontsize=14)
plt.ylabel('Celebrity', fontsize=14)
plt.title(f'Season {SEASON}: Weekly Certainty Heatmap for Each Contestant', fontsize=16)

# 调整x轴标签
plt.xticks(fontsize=11)
plt.yticks(fontsize=11, rotation=0)

plt.tight_layout()
plt.savefig(f'v2_season{SEASON}_certainty_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"热力图已保存: v2_season{SEASON}_certainty_heatmap.png")
print(f"\n透视表数据:\n{pivot_table.round(2)}")
