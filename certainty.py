"""
================================================================================
置信度计算模块 (改进版 v2)
================================================================================
功能：计算每位选手每周的预测置信度 (Certainty)
      置信度高 = 预测结果可靠；置信度低 = 预测结果不确定

核心公式：
    Certainty = 1 - (α × EC_norm + β × PD_norm)
    
其中：
    - EC (Evidence Conflict): 证据冲突强度，评委排名与最终排名的差异
    - PD (Pressure of Death): 生存压力，粉丝投票在可行范围内的相对位置
    - α, β: 权重参数，默认 α=0.7, β=0.3

设计理念：
    - EC 高 → 评委与观众意见分歧大 → 不确定性高 → certainty 低
    - PD 高 → 粉丝投票接近下限 → 淘汰风险高 → certainty 低
    - 所有选手（包括淘汰者）均使用原始计算值，保留预测质量信息
================================================================================
"""

import pandas as pd
import numpy as np
from typing import Tuple

# ============================================================================
# 超参数配置（便于调整和敏感性分析）
# ============================================================================
ALPHA = 0.7           # EC (证据冲突) 权重
BETA = 0.3            # PD (生存压力) 权重
CERTAINTY_MIN = 0.2  # 置信度下限
CERTAINTY_MAX = 0.95  # 置信度上限
SIGMOID_K = 6         # Sigmoid 函数的陡峭程度


def sigmoid_transform(x: np.ndarray, k: float = SIGMOID_K) -> np.ndarray:
    """
    使用 Sigmoid 函数将值平滑映射到 [CERTAINTY_MIN, CERTAINTY_MAX]
    
    优点：相比 clip，保留了极端值的相对差异，避免信息丢失
    
    公式：y = min + (max - min) / (1 + exp(-k * (x - 0.5)))
    
    Parameters:
        x: 输入数组，范围 [0, 1]
        k: 陡峭程度，k 越大曲线越陡
    
    Returns:
        映射后的数组，范围 [CERTAINTY_MIN, CERTAINTY_MAX]
    """
    sigmoid = 1 / (1 + np.exp(-k * (x - 0.5)))
    return CERTAINTY_MIN + (CERTAINTY_MAX - CERTAINTY_MIN) * sigmoid


def calculate_evidence_conflict(group: pd.DataFrame) -> pd.Series:
    """
    计算证据冲突强度 EC (Evidence Conflict)
    
    原理：评委给分排名 (RJ) 与赛季最终排名 (season_rank) 的差异
          差异越大，说明评委意见与最终结果冲突越大，不确定性越高
    
    公式：EC_norm = |RJ - season_rank| / (N - 1)
    
    Parameters:
        group: 某一周的选手数据
    
    Returns:
        EC_norm: 归一化的证据冲突强度，范围 [0, 1]
    """
    N = len(group)
    
    # RJ: 评委排名 (1 = 最高分)
    RJ = group['total_score'].rank(ascending=False, method='min')
    
    # 计算差异并归一化
    diff = np.abs(RJ - group['season_rank'])
    EC_norm = diff / (N - 1) if N > 1 else 0.0
    
    # 确保范围在 [0, 1]（防止异常数据）
    return EC_norm.clip(0, 1)


def calculate_survival_pressure(group: pd.DataFrame) -> pd.Series:
    """
    计算生存压力 PD (Pressure of Death)
    
    原理：粉丝投票百分比在可行范围 [min, max] 内的相对位置
          越接近下限 (min)，淘汰风险越高，不确定性越大
    
    公式：PD_norm = 1 - (fan_percent - min) / (max - min)
    
    边界情况处理：
        - 当 max ≈ min（范围极窄）时：
          * 若选手被淘汰 → PD = 0（结果已确定，无压力）
          * 若选手存活 → PD = 0.5（中等压力，保守估计）
    
    Parameters:
        group: 某一周的选手数据
    
    Returns:
        PD_norm: 归一化的生存压力，范围 [0, 1]
    """
    denom = group['fan_percent_max'] - group['fan_percent_min']
    
    # 正常情况：计算相对位置
    PD_norm = 1 - (group['estimated_fan_percent'] - group['fan_percent_min']) / denom
    
    # 边界情况：分母接近 0
    narrow_range_mask = denom < 1e-7
    
    if narrow_range_mask.any():
        # 被淘汰者：结果确定，压力设为 0
        eliminated_mask = narrow_range_mask & (group['is_actual_eliminated'] == True)
        PD_norm = PD_norm.copy()
        PD_norm.loc[eliminated_mask] = 0.0
        
        # 存活者但范围极窄：保守设为中等压力
        survived_narrow_mask = narrow_range_mask & (group['is_actual_eliminated'] == False)
        PD_norm.loc[survived_narrow_mask] = 0.5
    
    # 确保范围在 [0, 1]
    return PD_norm.clip(0, 1)


def calculate_certainty(group: pd.DataFrame, alpha: float = ALPHA, beta: float = BETA) -> pd.Series:
    """
    计算综合置信度
    
    公式：Certainty = 1 - (α × EC_norm + β × PD_norm)
    
    解释：
        - EC 和 PD 都是"不确定性指标"（越高越不确定）
        - 加权求和得到总不确定性
        - 取补数得到置信度（越高越确定）
    
    方案B：不对淘汰者做特殊处理，保留预测质量信息
        - 高置信度的淘汰者 = 预料之中的淘汰
        - 低置信度的淘汰者 = 爆冷淘汰
    
    Parameters:
        group: 某一周的选手数据
        alpha: EC 权重
        beta: PD 权重
    
    Returns:
        certainty: 置信度，范围 [CERTAINTY_MIN, CERTAINTY_MAX]
    """
    EC_norm = calculate_evidence_conflict(group)
    PD_norm = calculate_survival_pressure(group)
    
    # 综合不确定性
    uncertainty = alpha * EC_norm + beta * PD_norm
    
    # 置信度 = 1 - 不确定性
    certainty = uncertainty
    
    # 使用 Sigmoid 平滑映射到目标范围
    certainty = sigmoid_transform(certainty)
    
    return certainty


def calculate_final_certainty(file_path: str, output_path: str, 
                               alpha: float = ALPHA, beta: float = BETA) -> pd.DataFrame:
    """
    主函数：计算所有选手每周的置信度
    
    Parameters:
        file_path: 输入数据文件路径
        output_path: 输出文件路径
        alpha: EC 权重（默认 0.7）
        beta: PD 权重（默认 0.3）
    
    Returns:
        result_df: 包含置信度列的 DataFrame
    """
    # 读取数据
    df = pd.read_csv(file_path)
    print(f"读取数据: {len(df)} 条记录")
    
    # 验证必需列
    required_cols = ['season', 'week', 'total_score', 'season_rank', 
                     'estimated_fan_percent', 'fan_percent_min', 'fan_percent_max',
                     'is_actual_eliminated']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必需列: {missing_cols}")
    
    results = []
    
    # 按 (season, week) 分组处理
    for (season, week), group in df.groupby(['season', 'week']):
        group = group.copy()
        
        # 计算置信度（方案B：不对淘汰者做特殊处理）
        group['certainty_final'] = calculate_certainty(group, alpha, beta)
        
        # 保存中间变量用于调试（可选）
        group['EC_norm'] = calculate_evidence_conflict(group)
        group['PD_norm'] = calculate_survival_pressure(group)
        
        results.append(group)
    
    # 合并结果
    result_df = pd.concat(results, ignore_index=True)
    
    # 保存到文件
    result_df.to_csv(output_path, index=False)
    print(f"处理完成！置信度已存入: {output_path}")
    
    # 打印统计信息
    print(f"\n【置信度统计】")
    print(f"  最小值: {result_df['certainty_final'].min():.4f}")
    print(f"  最大值: {result_df['certainty_final'].max():.4f}")
    print(f"  均值:   {result_df['certainty_final'].mean():.4f}")
    print(f"  中位数: {result_df['certainty_final'].median():.4f}")
    
    return result_df


# ============================================================================
# 运行
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("置信度计算模块 (改进版 v2 - 方案B)")
    print("=" * 60)
    print(f"\n【参数配置】")
    print(f"  α (EC 权重): {ALPHA}")
    print(f"  β (PD 权重): {BETA}")
    print(f"  置信度范围: [{CERTAINTY_MIN}, {CERTAINTY_MAX}]")
    print(f"  Sigmoid K: {SIGMOID_K}")
    print(f"  淘汰者处理: 不做特殊处理，保留原始计算值")
    print()
    
    # 输出到新文件，不覆盖原文件
    calculate_final_certainty(
        './estimated_fan_data.csv', 
        'data_with_certainty.csv'
    )
