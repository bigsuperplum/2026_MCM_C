# MCM 2026 Problem C - 第四问详解
## 设计新的评分方式 (New Scoring System Design)

---

## 📋 目录
1. [问题背景与分析](#1-问题背景与分析)
2. [现有评分系统回顾](#2-现有评分系统回顾)
3. [新评分系统设计方案](#3-新评分系统设计方案)
4. [数学模型详解](#4-数学模型详解)
5. [代码实现说明](#5-代码实现说明)
6. [方案对比与推荐](#6-方案对比与推荐)

---

## 1. 问题背景与分析

### 1.1 原始问题
> "Propose another system using fan votes and judge scores each week that you believe is more 'fair' (or 'better' in some other way such as making the show more exciting for the fans). Provide support for why your approach should be adopted by the show producers."

### 1.2 关键词解读
- **"fair"（公平）**: 评分系统应该公正地反映选手的综合实力
- **"better"（更好）**: 可能指更有趣、更能吸引观众、更能产生戏剧效果
- **"exciting for fans"（对粉丝刺激）**: 增强观众参与感和观看体验

### 1.3 现有系统的问题
根据题目描述的争议案例：
| 案例 | 问题描述 |
|------|----------|
| Season 2 Jerry Rice | 尽管连续5周评委最低分，仍获得亚军 |
| Season 4 Billy Ray Cyrus | 连续6周评委最低分，获得第5名 |
| Season 11 Bristol Palin | 12次评委最低分，仍获得第3名 |
| Season 27 Bobby Bones | 尽管评委分数一直较低，最终获得冠军 |

**核心矛盾**: 技术表现（评委评分）vs 人气支持（粉丝投票）

---

## 2. 现有评分系统回顾

### 2.1 方法一：基于排名的合并（Rank-Based, Season 1-2, 28-34）

**原理**:
将评委分数和粉丝投票分别转化为排名，然后相加。

**数学表达**:
设有 $n$ 位选手，第 $i$ 位选手：
- 评委总分：$J_i$
- 粉丝投票百分比：$F_i$

则：
$$R_{judge}^{(i)} = \text{rank}(-J_i)$$
$$R_{fan}^{(i)} = \text{rank}(-F_i)$$
$$R_{combined}^{(i)} = R_{judge}^{(i)} + R_{fan}^{(i)}$$

**淘汰规则**: $R_{combined}$ 最大的选手被淘汰。

**优点**: 简单直观，两方面都有发言权
**缺点**: 忽略了分数差距的大小

### 2.2 方法二：基于百分比的合并（Percent-Based, Season 3-27）

**原理**:
将评委分数转化为百分比，与粉丝投票百分比加权平均。

**数学表达**:
$$J_{percent}^{(i)} = \frac{J_i}{\sum_{k=1}^{n} J_k} \times 100\%$$

$$S_{combined}^{(i)} = \alpha \cdot J_{percent}^{(i)} + \beta \cdot F_i$$

其中通常 $\alpha = \beta = 0.5$。

**淘汰规则**: $S_{combined}$ 最低的选手被淘汰。

**优点**: 保留了分数差距信息
**缺点**: 权重固定，不够灵活

---

## 3. 新评分系统设计方案

### 📊 方案汇总表

| 方案 | 名称 | 核心思想 | 复杂度 | 推荐场景 |
|------|------|----------|--------|----------|
| 1 | 动态权重系统 | 权重随赛程变化 | ⭐⭐ | **强烈推荐** |
| 2 | 累积表现系统 | 考虑历史表现 | ⭐⭐⭐ | 强调持续性 |
| 3 | 多维度评价系统 | 多指标综合评价 | ⭐⭐⭐ | 追求全面性 |
| 4 | 自适应阈值系统 | 安全区/危险区 | ⭐⭐ | 增加戏剧性 |
| 5 | 公平性优化系统 | 数学优化最优权重 | ⭐⭐⭐⭐ | 追求理论最优 |
| 6 | 博弈论平衡系统 | 平衡各方利益 | ⭐⭐⭐⭐ | 学术研究 |

---

## 4. 数学模型详解

### 4.1 🌟 方案一：动态权重系统 (Dynamic Weighting System)

#### 建模动机
- **问题**: 固定权重无法适应比赛不同阶段的需求
- **观察**: 
  - 早期：需要人气选手维持收视率
  - 后期：需要技术选手确保比赛质量

#### 数学模型

设第 $w$ 周，总共 $W$ 周：

$$\boxed{\alpha(w) = \alpha_{min} + (\alpha_{max} - \alpha_{min}) \cdot \frac{w-1}{W-1}}$$

$$\beta(w) = 1 - \alpha(w)$$

**最终分数**:
$$S_i(w) = \alpha(w) \cdot J_{percent}^{(i)} + \beta(w) \cdot F_i$$

#### 参数选择建议
| 参数 | 推荐值 | 含义 |
|------|--------|------|
| $\alpha_{min}$ | 0.3 | 第1周评委权重（粉丝主导） |
| $\alpha_{max}$ | 0.7 | 最后一周评委权重（技术主导） |

#### 为什么这样建模？

1. **线性变化**: 选择线性函数是因为：
   - 简单易懂，便于向观众解释
   - 变化平稳，不会造成规则突变感
   - 参数少，易于调节

2. **权重范围**: 选择 0.3-0.7 而非 0-1 是因为：
   - 始终保持两方都有一定发言权
   - 避免极端情况

3. **公式推导**:
   ```
   第1周: w=1, α(1) = 0.3 + 0.4 × 0/(W-1) = 0.3
   最后周: w=W, α(W) = 0.3 + 0.4 × (W-1)/(W-1) = 0.7
   中间周: 线性插值
   ```

---

### 4.2 方案二：累积表现系统 (Cumulative Performance System)

#### 建模动机
- **问题**: 只看当周表现，一次失误可能致命
- **目标**: 奖励持续努力和稳定发挥的选手

#### 数学模型

设选手 $i$ 在第 $w$ 周的基础分数为 $B_i(w)$：

**1. 势头分数 (Momentum)**:
$$M_i(w) = \gamma \cdot \frac{B_i(w) - B_i(w-1)}{B_{max}}$$

**2. 稳定性分数 (Stability)**:
$$\sigma_i(w) = \text{std}\{B_i(1), ..., B_i(w)\}$$
$$Stab_i(w) = \delta \cdot \left(1 - \frac{\sigma_i(w)}{\sigma_{max}}\right)$$

**3. 最终分数**:
$$\boxed{Final_i(w) = B_i(w) + M_i(w) + Stab_i(w)}$$

#### 参数建议
| 参数 | 推荐值 | 含义 |
|------|--------|------|
| $\gamma$ | 0.1 | 势头系数（进步奖励） |
| $\delta$ | 0.05 | 稳定性系数 |

---

### 4.3 方案三：多维度评价系统 (Multi-Dimensional Evaluation)

#### 建模动机
- **问题**: 二维评价过于简单
- **目标**: 全面反映选手的各方面表现

#### 数学模型

**四个维度**:

1. **技术分** (Technical, $T$):
   $$T_i = \frac{J_i}{\sum J_k} \times 100$$

2. **进步分** (Improvement, $I$):
   $$I_i = \max\left(0, \frac{J_i(w) - J_i(w-1)}{J_{max}} \times 100\right)$$

3. **人气分** (Popularity, $P$):
   $$P_i = F_i$$

4. **惊喜分** (Surprise, $Sur$):
   $$Sur_i = \max\left(0, \frac{J_i - \mathbb{E}[J_i]}{J_{max}} \times 100\right)$$

**综合公式**:
$$\boxed{Final_i = w_T \cdot T_i + w_I \cdot I_i + w_P \cdot P_i + w_S \cdot Sur_i}$$

#### 权重建议
| 权重 | 推荐值 | 理由 |
|------|--------|------|
| $w_T$ | 0.35 | 技术是核心 |
| $w_I$ | 0.15 | 鼓励进步 |
| $w_P$ | 0.35 | 粉丝参与 |
| $w_S$ | 0.15 | 增加悬念 |

---

### 4.4 方案四：自适应阈值系统 (Adaptive Threshold System)

#### 建模动机
- **问题**: "谁被淘汰"缺乏悬念
- **目标**: 增加戏剧性和观众参与感

#### 数学模型

设所有选手分数为 $\{S_1, ..., S_n\}$：
$$\mu = \frac{1}{n}\sum_{i=1}^n S_i, \quad \sigma = \sqrt{\frac{1}{n}\sum_{i=1}^n (S_i - \mu)^2}$$

**三个区域**:
$$\boxed{T_{safe} = \mu + k_{safe} \cdot \sigma}$$
$$\boxed{T_{danger} = \mu - k_{danger} \cdot \sigma}$$

| 区域 | 条件 | 状态 |
|------|------|------|
| 安全区 | $S_i > T_{safe}$ | 直接晋级 |
| 待定区 | $T_{danger} < S_i \leq T_{safe}$ | 进入待定 |
| 危险区 | $S_i \leq T_{danger}$ | 面临淘汰 |

#### 实现机制
- 待定区选手可以通过"附加赛"或"观众复活投票"决定命运
- 增加了节目的互动性和不确定性

---

### 4.5 方案五：公平性优化系统 (Fairness Optimization)

#### 建模动机
- **问题**: 什么样的权重最"公平"？
- **目标**: 用数学方法找到最优权重

#### 数学模型

**多目标优化问题**:
$$\boxed{\max_{\alpha} F(\alpha) = \lambda_1 \cdot \rho(R_{final}, R_{judge}) + \lambda_2 \cdot \rho(R_{final}, R_{fan}) + \lambda_3 \cdot H_{norm}}$$

其中:
- $\rho(\cdot, \cdot)$: Spearman相关系数
- $R_{final}, R_{judge}, R_{fan}$: 最终排名、评委排名、粉丝排名
- $H_{norm}$: 归一化熵（衡量结果的"惊喜度"）

$$H = -\sum_{i=1}^n p_i \log p_i, \quad H_{norm} = \frac{H}{\log n}$$

#### 参数建议
| 参数 | 推荐值 | 含义 |
|------|--------|------|
| $\lambda_1$ | 0.4 | 技术公平权重 |
| $\lambda_2$ | 0.4 | 民意公平权重 |
| $\lambda_3$ | 0.2 | 娱乐性权重 |

---

### 4.6 方案六：博弈论平衡系统 (Game Theory Balance)

#### 建模动机
- **视角**: 将评分系统视为多方博弈
- **参与方**: 评委、粉丝、制作方

#### 数学模型

**三方效用函数**:

1. **评委效用** (追求技术公平):
   $$U_J = \rho(R_{final}, R_{judge})$$

2. **粉丝效用** (追求民意反映):
   $$U_F = \rho(R_{final}, R_{fan})$$

3. **制作方效用** (追求戏剧性):
   $$U_P = \frac{\sigma(S)}{\mu(S)}$$

**Nash均衡**:
$$\boxed{\max_{\alpha, \beta} \left( U_J + U_F + U_P \right)}$$

约束: $\alpha + \beta = 1$, $\alpha, \beta \in [0.2, 0.8]$

---

## 5. 代码实现说明

### 5.1 Python代码文件
文件：`problem4_new_scoring_system.py`

**核心函数**:
```python
# 动态权重系统
def method_dynamic_weight(judge_scores, fan_percents, current_week, total_weeks,
                          alpha_min=0.3, alpha_max=0.7):
    # 返回：combined_scores, alpha, beta

# 多维度评价系统  
def method_multi_dimensional(judge_scores, fan_percents, prev_judge_scores=None,
                            expected_scores=None, w_T=0.35, w_I=0.15, w_P=0.35, w_S=0.15):
    # 返回：final_scores, components字典

# 公平性优化系统
def method_fairness_optimization(judge_scores, fan_percents, 
                                 lambda1=0.4, lambda2=0.4, lambda3=0.2):
    # 返回：final_scores, optimal_alpha
```

### 5.2 MATLAB代码文件
文件：`problem4_new_scoring_system.m`

**核心函数**:
```matlab
% 动态权重系统
[combined_scores, alpha, beta] = method_dynamic_weight(judge_scores, fan_percents, ...
    current_week, total_weeks, alpha_min, alpha_max)

% 多维度评价系统
[final_scores, components] = method_multi_dimensional(judge_scores, fan_percents, ...
    prev_judge_scores, expected_scores, weights)

% 自适应阈值系统
[zones, thresholds] = method_adaptive_threshold(combined_scores, k_safe, k_danger)
```

---

## 6. 方案对比与推荐

### 6.1 综合评估

| 评估维度 | 动态权重 | 累积表现 | 多维度 | 自适应阈值 | 公平性优化 |
|----------|---------|---------|--------|-----------|-----------|
| 公平性 | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★★ |
| 娱乐性 | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| 简洁性 | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |
| 可解释性 | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| 实施难度 | ★☆☆☆☆ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ | ★★★☆☆ |

### 6.2 🏆 最终推荐

**主推方案**: 动态权重系统 + 自适应阈值系统（组合使用）

**推荐理由**:

1. **平衡各方需求**:
   - 早期保护人气选手 → 维持收视率
   - 后期强调技术 → 确保冠军实至名归

2. **增加节目吸引力**:
   - 安全区/待定区/危险区增加悬念
   - 权重变化可作为节目宣传点

3. **易于实施和解释**:
   - 公式简单，观众易懂
   - 参数可视化调整

4. **可解决历史争议**:
   - Bobby Bones案例：后期权重偏向评委，技术差的选手更难获胜
   - Bristol Palin案例：稳定性低的选手在累积系统中处于劣势

### 6.3 实施建议

```
【第1-3周】α = 0.3-0.4, β = 0.6-0.7
    → 粉丝主导，保护人气选手

【第4-7周】α = 0.4-0.55, β = 0.45-0.6  
    → 平衡阶段

【第8周至决赛】α = 0.55-0.7, β = 0.3-0.45
    → 技术主导，确保质量
```

---

## 📚 参考文献

1. Dancing with the Stars官方规则文档
2. MCM 2026 Problem C 题目说明
3. Ranking methods comparison literature
4. Game theory in competition design

---

*文档生成时间: 2026年2月*
