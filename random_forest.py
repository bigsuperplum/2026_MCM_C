import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# ==========================================
# 第一部分：数据读取与预处理
# ==========================================
print("正在读取数据...")

# 1. 读取官方原始数据
try:
    df_raw = pd.read_csv('2026_MCM_Problem_C_Data.csv', encoding='utf-8')
    # 【关键修复1】清除列名可能存在的首尾空格
    df_raw.columns = df_raw.columns.str.strip()
except FileNotFoundError:
    print("错误：找不到 2026_MCM_Problem_C_Data.csv")
    exit()

# 2. 读取你的粉丝预测数据
fan_data_filename = 'estimated_fan_data.csv' 

try:
    df_fan = pd.read_csv(fan_data_filename, encoding='utf-8')
    # 【关键修复2】清除列名可能存在的首尾空格
    df_fan.columns = df_fan.columns.str.strip()
    
    # 【关键修复3】只保留粉丝表中必要的列，防止合并时产生 _x, _y 后缀
    required_cols = ['season', 'celebrity_name', 'week', 'estimated_fan_percent']
    
    # 检查列是否存在
    missing = [c for c in required_cols if c not in df_fan.columns]
    if missing:
        print(f"错误：你的粉丝数据表缺少以下列: {missing}")
        exit()
        
    # 这一步去掉了 df_fan 中可能重复存在的 partner、industry 等列
    df_fan = df_fan[required_cols]
    
    print(f"成功读取粉丝数据，共 {len(df_fan)} 行。")
except FileNotFoundError:
    print(f"错误：找不到 {fan_data_filename}，请确认文件名。")
    exit()

# 3. 将原始宽表转换为长表 (Week-by-Week)
print("正在整合特征数据...")
long_data = []

# 检查原始数据中是否存在需要的列
required_raw_cols = ['celebrity_name', 'season', 'ballroom_partner', 'celebrity_industry', 
                     'celebrity_homestate', 'celebrity_homecountry/region', 'celebrity_age_during_season']
for col in required_raw_cols:
    if col not in df_raw.columns:
        print(f"错误：原始数据表中找不到列 '{col}'。")
        print(f"当前存在的列: {df_raw.columns.tolist()}")
        exit()

for index, row in df_raw.iterrows():
    name = row['celebrity_name']
    season = row['season']
    
    # 提取特征
    partner = row['ballroom_partner']
    industry = row['celebrity_industry']
    homestate = row['celebrity_homestate']
    homecountry = row['celebrity_homecountry/region']
    age = row['celebrity_age_during_season']
    
    # 遍历第1周到第11周
    for w in range(1, 12):
        judge_cols = [c for c in df_raw.columns if f'week{w}_judge' in c and 'score' in c]
        
        scores = []
        for col in judge_cols:
            val = row[col]
            try:
                val = float(val)
                if not np.isnan(val) and val > 0:
                    scores.append(val)
            except:
                continue
        
        if len(scores) == 0:
            continue
            
        avg_score = np.mean(scores)
        
        long_data.append({
            'season': season,
            'celebrity_name': name,
            'week': w,
            # 保证这里的 Key 名字简洁且与后面 cat_features 一致
            'ballroom_partner': partner,
            'celebrity_industry': industry,
            'celebrity_homestate': homestate,
            'celebrity_homecountry': homecountry,
            'celebrity_age': age,
            'avg_judge_score': avg_score
        })

df_long = pd.DataFrame(long_data)

# 4. 合并数据
# 去除名字空格以防匹配失败
df_long['celebrity_name'] = df_long['celebrity_name'].astype(str).str.strip()
df_fan['celebrity_name'] = df_fan['celebrity_name'].astype(str).str.strip()

print("正在合并评委与粉丝数据...")
df_model = pd.merge(df_long, df_fan, on=['season', 'celebrity_name', 'week'], how='inner')

if len(df_model) == 0:
    print("错误：合并后数据为空！请检查两个文件的姓名拼写格式是否一致。")
    exit()

print(f"建模数据准备完毕，样本量: {len(df_model)}")

# 【调试信息】打印当前列名，确保 ballroom_partner 存在
# print("当前列名:", df_model.columns.tolist())

# ==========================================
# 第二部分：特征编码与选择
# ==========================================
print("正在进行特征编码...")

# 注意：这里我们使用了简化的 key 名字
cat_features = ['ballroom_partner', 'celebrity_industry', 'celebrity_homestate', 'celebrity_homecountry']

# 填充缺失值
for col in cat_features:
    if col not in df_model.columns:
        print(f"严重错误：列 '{col}' 在合并后的数据中丢失！")
        print(f"可能原因：df_fan 中也包含该列，导致合并后变成了 {col}_x 和 {col}_y。")
        print(f"当前列名: {df_model.columns.tolist()}")
        exit()
    df_model[col] = df_model[col].fillna('Unknown')

# Label Encoding
label_encoders = {}
for col in cat_features:
    le = LabelEncoder()
    df_model[f'{col}_code'] = le.fit_transform(df_model[col].astype(str))
    label_encoders[col] = le

# ==========================================
# 第三部分：随机森林训练
# ==========================================

# 1. 定义 X (特征矩阵)
# 对应上面生成的 code 列
feature_cols_for_model = [
    'ballroom_partner_code',   
    'celebrity_industry_code', 
    'celebrity_homestate_code',
    'celebrity_homecountry_code',
    'celebrity_age'            
]

feature_display_names = ['Pro Partner', 'Industry', 'Home State', 'Home Country/Region', 'Age']

X = df_model[feature_cols_for_model]
y_judge = df_model['avg_judge_score']
y_fan = df_model['estimated_fan_percent']

print(f"使用的特征: {feature_display_names}")
print("正在训练模型...")

# 2. 训练模型
rf_judge = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_judge.fit(X, y_judge)

rf_fan = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_fan.fit(X, y_fan)

# 3. 提取重要性
importances_judge = rf_judge.feature_importances_
importances_fan = rf_fan.feature_importances_

# ==========================================
# 第四部分：可视化
# ==========================================
x_pos = np.arange(len(feature_display_names))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

# 绘制柱状图
rects1 = ax.bar(x_pos - width/2, importances_judge, width, label='Impact on Judges', color='#2ca02c', alpha=0.8)
rects2 = ax.bar(x_pos + width/2, importances_fan, width, label='Impact on Fans', color='#d62728', alpha=0.8)

ax.set_ylabel('Feature Importance Score')
ax.set_title('Feature Impact Analysis: Judges vs Fan Votes', fontsize=14)
ax.set_xticks(x_pos)
ax.set_xticklabels(feature_display_names, fontsize=11)
ax.legend()

# 标注数值
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

autolabel(rects1)
autolabel(rects2)

plt.tight_layout()
plt.show()

print("\n分析完成！")