这是一份针对**问题 2：投票机制对比与分析**的详细建模指南。

这一问的核心任务是**“历史重演”**。既然我们在第一问中已经（假设）拿到了粉丝投票的数据，现在我们要像上帝一样，通过修改游戏规则，看看历史会不会被改写。

---

### 第一部分：核心思路与“小白”解释

#### 1. 为什么要对比“排名法”和“百分比法”？
想象你在班里考试，有两门课：**数学（裁判分）**和**体育（粉丝票）**。

*   **排名法 (Rank Method)**：
    *   老师不管你考了多少分，只看名次。
    *   数学第1名得1分，第2名得2分... 体育第1名得1分...
    *   最后谁的总分（名次和）最大，谁就是倒数第一。
    *   **特点**：**“抹平差距”**。哪怕你数学考了100分，第二名考了99分，在排名上你们只差1位。你的巨大优势被压缩了。

*   **百分比法 (Percentage Method)**：
    *   老师看你的分数占全班总分的比例。
    *   你的总分 = (你的数学分/全班数学总分) + (你的体育分/全班体育总分)。
    *   **特点**：**“放大差距”**。如果你体育特别好（粉丝特别多，比如你是超级巨星），你的体育占比会非常大，大到可以弥补你数学考0分的劣势。

**建模目标**：我们要通过计算，找出哪些人是因为“排名法”才活下来的，哪些人是因为“百分比法”才活下来的。

#### 2. 什么是“裁判拯救环节” (Judges' Save)？
这是第28季引入的新规则：
*   先算出倒数两名（Bottom 2）。
*   然后裁判在这两个人里选一个留下来。
*   **建模逻辑**：裁判通常会选**跳舞技术更好**的那个人（也就是裁判分更高的那个人）。这是一个专门用来打击“跳得烂但人气高”选手的补丁。

---

### 第二部分：建模步骤与代码实现

我们需要建立一个**通用模拟器**。

#### 步骤 1：构建模拟模型 (The Simulator)

我们定义一个函数，输入某一周所有选手的**裁判分**和**粉丝票数**，输出三种规则下的淘汰者。

**输入变量**：
*   $J_i$: 第 $i$ 个选手的裁判得分。
*   $F_i$: 第 $i$ 个选手的粉丝票数（来自第一问的估算结果）。

**算法逻辑**：

1.  **规则 A (Rank)**:
    *   计算裁判排名 $R_{J,i}$ 和粉丝排名 $R_{F,i}$。
    *   计算总排名 $S_{Rank,i} = R_{J,i} + R_{F,i}$。
    *   淘汰者 = $\arg\max(S_{Rank,i})$ （数值最大者）。

2.  **规则 B (Percentage)**:
    *   计算裁判占比 $P_{J,i} = J_i / \sum J$。
    *   计算粉丝占比 $P_{F,i} = F_i / \sum F$。
    *   计算总占比 $S_{Perc,i} = P_{J,i} + P_{F,i}$。
    *   淘汰者 = $\arg\min(S_{Perc,i})$ （数值最小者）。

3.  **规则 C (Judges' Save)**:
    *   基于规则A或B（题目暗示S28后回归Rank，所以通常基于Rank）找出倒数两名。
    *   比较这两人的 $J_i$。
    *   淘汰者 = $J_i$ 较小的那个（如果 $J_i$ 相同，则看粉丝）。

---

#### Python 代码实现

这段代码可以直接运行，它会模拟一个赛季的对比。

```python
import pandas as pd
import numpy as np

# --- 模拟数据生成 (实际使用时请替换为第一问的 df_result) ---
# 假设这是某一周的数据：Name, JudgeScore, EstFanVotes
data = {
    'Name': ['Bobby Bones', 'Milo Manheim', 'Evanna Lynch', 'Joe Amabile'],
    'JudgeScore': [24, 29, 30, 22],  # 裁判分
    'EstFanVotes': [500000, 150000, 120000, 480000] # 粉丝票数 (Bobby和Joe人气很高但分低)
}
df_week = pd.DataFrame(data)

def simulate_elimination(df):
    """
    输入一个DataFrame，包含当周所有选手的裁判分和粉丝票
    输出三种规则下的淘汰者
    """
    # 1. Rank Method (排名法)
    # rank(ascending=False) 意味着分数越高，rank值越小(1st)
    df['Rank_J'] = df['JudgeScore'].rank(ascending=False, method='min')
    df['Rank_F'] = df['EstFanVotes'].rank(ascending=False, method='min')
    df['Sum_Rank'] = df['Rank_J'] + df['Rank_F']
    
    # 找 Rank Sum 最大的 (表现最差)
    # 注意：如果有并列，实际规则比较复杂，这里简化为取第一个
    eliminated_rank = df.loc[df['Sum_Rank'].idxmax()]['Name']
    
    # 2. Percentage Method (百分比法)
    total_judge = df['JudgeScore'].sum()
    total_fan = df['EstFanVotes'].sum()
    
    df['Perc_J'] = df['JudgeScore'] / total_judge
    df['Perc_F'] = df['EstFanVotes'] / total_fan
    df['Sum_Perc'] = df['Perc_J'] + df['Perc_F']
    
    # 找 Percent Sum 最小的 (表现最差)
    eliminated_perc = df.loc[df['Sum_Perc'].idxmin()]['Name']
    
    # 3. Judges' Save (裁判拯救)
    # 假设基于 Rank 选出 Bottom 2
    # 排序找到倒数两名
    bottom_2 = df.sort_values('Sum_Rank', ascending=False).head(2)
    
    # 裁判会救 JudgeScore 高的那个人
    # 所以淘汰的是 JudgeScore 低的那个人
    loser_save = bottom_2.loc[bottom_2['JudgeScore'].idxmin()]['Name']
    
    return eliminated_rank, eliminated_perc, loser_save, df

# --- 运行模拟 ---
loser_rank, loser_perc, loser_save, df_result = simulate_elimination(df_week.copy())

print("--- 模拟结果 ---")
print(df_result[['Name', 'JudgeScore', 'EstFanVotes', 'Sum_Rank', 'Sum_Perc']])
print(f"\n1. 排名法淘汰: {loser_rank}")
print(f"2. 百分比法淘汰: {loser_perc}")
print(f"3. 裁判拯救法淘汰: {loser_save}")

# --- 结果分析 ---
if loser_rank != loser_perc:
    print("\n发现！投票机制改变了结果！")
    print("百分比法通常有利于粉丝基数极大但裁判分一般的选手。")
```

#### Matlab 代码实现

```matlab
% --- 模拟数据 ---
Names = {'Bobby Bones', 'Milo Manheim', 'Evanna Lynch', 'Joe Amabile'};
JudgeScores = [24, 29, 30, 22];
FanVotes = [500000, 150000, 120000, 480000];

% 调用函数
analyze_voting_methods(Names, JudgeScores, FanVotes);

function analyze_voting_methods(names, j_scores, f_votes)
    n = length(names);
    
    % --- Method 1: Rank Sum ---
    % 裁判排名 (分数高排名小)
    [~, idx_j] = sort(j_scores, 'descend');
    rank_j = zeros(1,n);
    % 处理排名 (简单处理，不含并列逻辑，实际可用 tiedrank)
    rank_j(idx_j) = 1:n; 
    
    % 粉丝排名
    [~, idx_f] = sort(f_votes, 'descend');
    rank_f = zeros(1,n);
    rank_f(idx_f) = 1:n;
    
    total_rank = rank_j + rank_f;
    [~, idx_loser_rank] = max(total_rank); % 找最大值(最差)
    loser_rank = names{idx_loser_rank};
    
    % --- Method 2: Percentage Sum ---
    perc_j = j_scores / sum(j_scores);
    perc_f = f_votes / sum(f_votes);
    total_perc = perc_j + perc_f;
    
    [~, idx_loser_perc] = min(total_perc); % 找最小值(最差)
    loser_perc = names{idx_loser_perc};
    
    % --- Method 3: Judges' Save ---
    % 基于 Rank 找出 Bottom 2
    [~, sorted_idx] = sort(total_rank, 'descend');
    bottom2_idx = sorted_idx(1:2); % 取倒数两名
    
    % 比较裁判分
    if j_scores(bottom2_idx(1)) < j_scores(bottom2_idx(2))
        idx_loser_save = bottom2_idx(1);
    else
        idx_loser_save = bottom2_idx(2);
    end
    loser_save = names{idx_loser_save};
    
    % --- 输出 ---
    fprintf('排名法淘汰: %s\n', loser_rank);
    fprintf('百分比法淘汰: %s\n', loser_perc);
    fprintf('裁判拯救法淘汰: %s\n', loser_save);
end
```

If differences in outcomes exist, does one method seem to favor fan votes more than the other?

这个问题非常关键，它触及了评分系统的核心数学机制。要回答“哪种方法更偏向粉丝？”，我们不能只凭感觉，必须用数学语言来定义“偏向（Favor）”。

这里有三种不同深度的建模方式，分别从**结果统计**、**相关性分析**和**方差贡献**三个角度切入。

---

### 核心通俗解释：拔河比赛

把每一周的比赛看作一场**拔河**。
*   左边是**裁判**（Judge），右边是**粉丝**（Fan）。
*   最终的**总分**就是绳子中间的红标。
*   如果红标最终倒向右边（结果和粉丝排名更一致），那这种计分方法就是“偏向粉丝”的绳子。

我们需要衡量的是：**在“排名法”和“百分比法”这两根绳子里，哪一根更容易被粉丝拉过去？**

---

### 模型：Spearman 相关系数分析 (Correlation Analysis)

**适合小白：统计学标准做法。**

**建模逻辑：**
我们不看谁淘汰了，我们要看**最终排位**。
*   计算“Rank法算出的总排名”和“纯粉丝排名”的相关性（Correlation A）。
*   计算“Percent法算出的总排名”和“纯粉丝排名”的相关性（Correlation B）。
*   **结论：** 如果 Correlation B > Correlation A，说明 Percent 法产生的结果与粉丝的意愿贴合得更紧密。

**为什么用 Spearman？** 因为我们关心的是**排序**（谁第一谁第二），而不是具体的数值。

**Matlab 代码实现：**

```matlab
function check_correlation(judge_scores, fan_votes)
    % 1. 计算两种方法的最终得分向量
    
    % Rank Method
    % tiedrank处理并列排名
    r_j = tiedrank(-judge_scores); % 负号是为了让高分排前面(1)
    r_f = tiedrank(-fan_votes);
    score_rank_method = r_j + r_f; % 数值越小越好
    
    % Percent Method
    p_j = judge_scores / sum(judge_scores);
    p_f = fan_votes / sum(fan_votes);
    score_perc_method = p_j + p_f; % 数值越大越好
    
    % 2. 计算相关性 (与粉丝排名的相关性)
    % 注意方向：
    % Rank法总分(小好) vs 粉丝Rank(小好) -> 正相关代表一致
    % Percent法总分(大好) vs 粉丝Rank(小好) -> 负相关代表一致
    
    corr_rank = corr(score_rank_method', r_f', 'Type', 'Spearman');
    corr_perc = corr(score_perc_method', -r_f', 'Type', 'Spearman'); % -r_f 转换方向
    
    fprintf('Rank法与粉丝意愿的相关性: %.4f\n', corr_rank);
    fprintf('Percent法与粉丝意愿的相关性: %.4f\n', corr_perc);
    
    if corr_perc > corr_rank
        disp('结论：百分比法更偏向粉丝');
    else
        disp('结论：排名法更偏向粉丝');
    end
end
```

---

### 第三部分：深入分析“争议人物” (Case Studies)

题目特别点名了几个引起争议的人：Jerry Rice, Billy Ray Cyrus, Bristol Palin, Bobby Bones。你需要针对这些人做具体分析。

寻找“争议人物”的过程，本质上就是寻找**数据中的异常值（Outliers）**。

通俗地说，我们要找的是那些**“严重偏科”**的学生：要么是“老师眼里的学霸，同学眼里的透明人”（裁判分高，粉丝票低），要么是“老师眼里的差生，同学眼里的万人迷”（裁判分低，粉丝票高）。

这里提供三种由浅入深的建模方式，帮你把隐藏在30多个赛季里的“漏网之鱼”全部抓出来。

---

### 模型一：排名差异法 (Rank Gap Model) —— 最简单直观

**小白解释：**
想象两张榜单。
*   左手一张榜：裁判给出的排名（1是最好，10是最后）。
*   右手一张榜：粉丝给出的排名（1是票最多，10是票最少）。

如果小明在左手榜排第10（倒数第一），在右手榜排第1（人气第一），他的**“排名差”**就是 $10 - 1 = 9$。这个数字越大，说明争议越大。

**数学定义：**
定义“争议指数” $C_{gap}$：
$$ C_{gap} = \text{Judge Rank} - \text{Fan Rank} $$

*   如果 $C_{gap} > 0$（比如 $10 - 1 = 9$）：说明 **粉丝排名远高于裁判排名**（这是我们重点要找的“Bobby Bones型”选手）。
*   如果 $C_{gap} < 0$（比如 $1 - 10 = -9$）：说明 **裁判排名远高于粉丝排名**（这是“冤死型”选手，跳得好但没人气）。

**Python 代码：**

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 假设 df 包含了 'Name', 'Season', 'Week', 'JudgeScore' 以及第一问算出的 'EstFanRank'
# 为了演示，我们生成一些模拟数据
data = {
    'Name': ['Star A', 'Star B', 'Star C', 'Star D', 'Star E'],
    'Season': [10, 10, 10, 10, 10],
    'Week': [5, 5, 5, 5, 5],
    'JudgeScore': [28, 27, 25, 15, 29], # Star D 分很低
    'EstFanRank': [2, 3, 4, 1, 5]       # Star D 粉丝排名第1
}
df = pd.DataFrame(data)

def find_controversy_rank_gap(df):
    # 1. 计算裁判排名 (分数越高，排名数值越小)
    df['JudgeRank'] = df['JudgeScore'].rank(ascending=False, method='min')
    
    # 2. 计算争议指数 Gap
    # Gap > 0: 粉丝更喜欢 (Fan Favorite)
    # Gap < 0: 裁判更喜欢 (Judge Favorite)
    df['Controversy_Gap'] = df['JudgeRank'] - df['EstFanRank']
    
    # 3. 筛选出大争议 (比如排名差超过 3 位)
    # 绝对值越大，争议越大
    threshold = 3
    controversial_cases = df[df['Controversy_Gap'].abs() >= threshold].copy()
    
    # 排序：先看谁是最大的"粉丝宠儿"
    controversial_cases = controversial_cases.sort_values('Controversy_Gap', ascending=False)
    
    return controversial_cases

# 运行
result = find_controversy_rank_gap(df)
print("发现的争议案例：")
print(result[['Name', 'JudgeRank', 'EstFanRank', 'Controversy_Gap']])
```

**Matlab 代码：**

```matlab
% 模拟数据
Names = {'Star A', 'Star B', 'Star C', 'Star D', 'Star E'};
JudgeScore = [28, 27, 25, 15, 29];
EstFanRank = [2, 3, 4, 1, 5];

% 1. 计算裁判排名 (descend: 高分排前面)
% tiedrank 处理并列情况
JudgeRank = tiedrank(-JudgeScore); 

% 2. 计算 Gap
ControversyGap = JudgeRank - EstFanRank;

% 3. 找出差异大的索引 (比如差值绝对值 > 2)
idx = find(abs(ControversyGap) > 2);

% 输出
disp('发现的争议案例:');
for i = 1:length(idx)
    k = idx(i);
    fprintf('%s: JudgeRank=%.1f, FanRank=%.1f, Gap=%.1f\n', ...
        Names{k}, JudgeRank(k), EstFanRank(k), ControversyGap(k));
end
```

---

### 模型二：Z-Score 偏差法 (Standardized Deviation) —— 更科学

**小白解释：**
排名法有个缺点：第一名和第二名可能只差0.5分，也可能差10分。单纯看排名会丢失“分差”的信息。
我们要用**“标准分” (Z-Score)** 来衡量。
*   把裁判分换算成：你比平均分高几个档次？
*   把粉丝票换算成：你比平均票数高几个档次？
*   如果你的裁判分比平均分**低2个档次**，但粉丝票比平均分**高2个档次**，那你就是妥妥的争议人物。

**数学定义：**
$$ Z_{judge} = \frac{Score - \mu_{judge}}{\sigma_{judge}} $$
$$ Z_{fan} = \frac{Votes - \mu_{fan}}{\sigma_{fan}} $$
$$ C_{dev} = Z_{fan} - Z_{judge} $$

*   $C_{dev}$ 很大：说明粉丝热情远超你的舞蹈水平。

**Python 代码：**

```python
from scipy.stats import zscore

def find_controversy_zscore(df):
    # 假设 df 里有 'EstFanVotes' (估算的票数)
    # 如果没有票数只有排名，可以用排名转化为一种正态分布分数 (Normal Scores)
    # 这里假设我们有票数 EstFanVotes
    df['EstFanVotes'] = [5000, 4500, 3000, 10000, 2000] # 模拟票数
    
    # 1. 计算 Z-Score
    df['Z_Judge'] = zscore(df['JudgeScore'])
    df['Z_Fan'] = zscore(df['EstFanVotes'])
    
    # 2. 计算偏差
    # Z_Fan 高 (正数大) 而 Z_Judge 低 (负数大) -> 差值会非常大
    df['Controversy_Index'] = df['Z_Fan'] - df['Z_Judge']
    
    # 3. 排序
    return df.sort_values('Controversy_Index', ascending=False)

res_z = find_controversy_zscore(df.copy())
print("按 Z-Score 偏差找到的争议人物：")
print(res_z[['Name', 'Z_Judge', 'Z_Fan', 'Controversy_Index']])
```

**Matlab 代码：**

```matlab
% 模拟数据
JudgeScore = [28, 27, 25, 15, 29];
FanVotes = [5000, 4500, 3000, 10000, 2000]; % Star D 票数极高

% 1. 计算 Z-Score
z_j = zscore(JudgeScore);
z_f = zscore(FanVotes);

% 2. 计算差异
c_index = z_f - z_j;

% 3. 展示结果
table(Names', z_j', z_f', c_index', 'VariableNames', {'Name', 'Z_Judge', 'Z_Fan', 'ControversyIndex'})
```

---

### 模型三：象限分析法 (Quadrant Analysis) —— 视觉化挖掘

**小白解释：**
我们可以画一张图，把所有人扔进去。
*   X轴是 **裁判排名**。
*   Y轴是 **粉丝排名**。
*   画一条 $y=x$ 的对角线。
    *   在对角线附近的，是“德艺双馨”或“又菜又没粉”的正常人。
    *   **远离对角线的点**，就是我们要找的妖魔鬼怪。
    *   特别是位于**左下角**（裁判差、粉丝好）和**右上角**（裁判好、粉丝差）的区域。

**这种方法的优势**：你可以直接通过**距离对角线的垂直距离**来定义争议度。

**Python 代码 (绘图分析):**

```python
import seaborn as sns

def plot_controversy(df):
    # 确保有排名数据
    df['JudgeRank'] = df['JudgeScore'].rank(ascending=False, method='min')
    
    plt.figure(figsize=(8, 8))
    
    # 绘制散点图
    sns.scatterplot(data=df, x='JudgeRank', y='EstFanRank', s=100, hue='Name')
    
    # 绘制对角线 (代表裁判和粉丝意见完全一致)
    max_rank = max(df['JudgeRank'].max(), df['EstFanRank'].max())
    plt.plot([0, max_rank], [0, max_rank], 'r--', label='Perfect Agreement')
    
    # 标注区域
    plt.text(max_rank*0.8, max_rank*0.2, 'Judge Favorite\n(Good Dance, Low Votes)', color='blue', ha='center')
    plt.text(max_rank*0.2, max_rank*0.8, 'Fan Favorite\n(Bad Dance, High Votes)', color='green', ha='center')
    
    plt.title('Judge Rank vs. Fan Rank Controversy Analysis')
    plt.xlabel('Judge Rank (Lower is Better)')
    plt.ylabel('Fan Rank (Lower is Better)')
    plt.gca().invert_xaxis() # 翻转坐标轴，让第1名在右上方或按习惯调整
    plt.gca().invert_yaxis()
    plt.legend()
    plt.grid(True)
    plt.show()

plot_controversy(df.copy())
```

**Matlab 代码 (绘图):**

```matlab
% 假设 JudgeRank 和 FanRank 已计算好
JudgeRank = [2, 3, 4, 10, 1]; % 假设Star D裁判排第10
FanRank = [2, 3, 4, 1, 5];

figure;
scatter(JudgeRank, FanRank, 100, 'filled');
hold on;

% 画对角线
max_r = max([max(JudgeRank), max(FanRank)]);
plot([1, max_r], [1, max_r], 'r--', 'LineWidth', 2);

xlabel('Judge Rank');
ylabel('Fan Rank');
title('Controversy Quadrant');
axis square;
grid on;

% 标记名字
text(JudgeRank+0.1, FanRank, Names);

% 解释：离红线越远，点越有争议
```

---

### 如何挖掘更多例子？（策略）

既然建立了模型，你需要在报告中展示你是如何“海选”出新例子的：

1.  **全历史扫描**：把第1季到第34季的所有数据扔进 **模型一**。
2.  **设定阈值**：设定 $Rank Gap \ge 4$ （比如裁判排第8，粉丝排第4，或反之）。
3.  **统计频次**：
    *   **单周爆发型**：某人在某一周Gap巨大（比如可能是那一周跳了某种奇怪的舞，或者那周有场外新闻）。
    *   **持续输出型**：计算每个选手整个赛季的 **平均 Gap**。如果平均 Gap 很大，这才是你要找的“争议人物”。
4.  **分类讨论**：
    *   **类型 A (The "People's Champ")**: 裁判分 consistently bottom 50%，但粉丝票 consistently top 3。
        *   *潜在候选人*: 搜索数据中像 **Bill Engvall (S17)**, **David Ross (S24)**, **Sean Spicer (S28)** 这样的人。他们通常走得很远但分很低。
    *   **类型 B (The "Shocking Exit")**: 裁判分 top 3，但突然被淘汰。
        *   *潜在候选人*: 搜索 **Sabrina Bryan (S5)**, **Juan Pablo Di Pace (S27)**, **Willow Shields (S20)**。这几位都是著名的“高分低票惨遭淘汰”案例。

**总结：**
用 **模型一（Rank Gap）** 快速筛选出候选名单，然后用 **模型二（Z-Score）** 验证其严重程度，最后用 **模型三（象限图）** 在论文中展示你的发现。这样既有数学依据，又有视觉冲击力。

找到争议人物之后，我们对他们进行分析：

#### 建模思路：敏感度分析 (Sensitivity Analysis)

我们要回答：“如果换一种规则，他们会不会死得早一点？”

**Python 分析脚本 (逻辑流程):**

1.  **Jerry Rice (S2)**:
    *   S2 用的是 Rank 法。Jerry Rice 活到了决赛。
    *   **分析**：把他那一季的数据代入 **Percentage 法**。
    *   **预期结论**：如果当年用的是 Percentage 法，Jerry Rice 可能早就被淘汰了。因为他的裁判分太低，而 Percentage 法会放大裁判分的劣势（除非他的粉丝票数是天文数字）。或者反过来，如果他的粉丝票数真的是天文数字，Percentage 法反而会保护他更久。你需要根据第一问估算的票数来定论。

2.  **Bobby Bones (S27)**:
    *   S27 用的是 Percentage 法。Bobby Bones 夺冠了。
    *   **分析**：
        1.  如果用 **Rank 法**，他会不会在某一周边成倒数第一？
        2.  如果加入 **Judges' Save**，他一定会死。因为他经常在 Bottom 2 边缘，一旦落入 Bottom 2，他的裁判分极低，裁判肯定淘汰他。
    *   **代码验证**：提取 Bobby Bones 每一周的数据，计算 `Bottom 2` 列表。如果他在列表中，输出“Judges' Save 会淘汰他”。

---

### 第四部分：推荐方案 (Recommendation)

你需要基于上述分析，向节目组推荐一个方案。

#### 推荐方案：混合制 + 裁判底线 (Hybrid System)

**小白解释**：
纯靠排名，可能不够刺激；纯靠百分比，容易出像 Bobby Bones 这样纯靠人气碾压比赛的人。
我们建议：
1.  **常规轮次**：使用 **Rank 法**。
    *   *理由*：Rank 法相对温和，不会让超级巨星的票数优势无限放大，给其他选手留活路。
2.  **淘汰机制**：必须保留 **Judges' Save**。
    *   *理由*：这是防止“灾难性结果”（跳得最烂的人夺冠）的最后一道防线。它保证了比赛的专业性底线。

**如何写进 Memo？**
> "我们的模型显示，Season 27 的争议结果主要是由于百分比法过度放大了粉丝投票的权重。如果当时采用了裁判拯救规则（Judges' Save），Bobby Bones 在第 6 周就会被淘汰。因此，我们强烈建议保留 Judges' Save 机制，并回归到 Rank 积分系统，以平衡娱乐性和专业性。"

---

### 总结

这一问的关键在于**比较**。你不需要预测未来，你只需要用不同的尺子（规则）去量过去的数据。

1.  **Rank法** = 抹平贫富差距，大家差距不大。
2.  **Percent法** = 赢家通吃，人气王无敌。
3.  **Judges' Save** = 裁判的尚方宝剑，专门斩杀人气高但技术差的选手。

用代码把所有赛季跑一遍，统计一下：“如果换规则，会有多少次淘汰结果不同？” 这个百分比（比如 15% 的结果会改变）就是你论文里最有力的证据。