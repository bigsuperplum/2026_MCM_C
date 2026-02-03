为了构建估算粉丝投票数的数学模型，基于数据的特性及统计学原理，我们做出以下假设：

**假设 1：总投票数与收视率呈线性正相关 (Proportionality of Total Votes to Viewership)**
虽然并非每一位观看节目的观众都会参与投票，但我们假设在同一季节目中，参与投票的观众比例（投票转化率）保持相对稳定。因此，每一集的**总粉丝有效投票数**与当集的**收视率（Viewership）**成正比。这允许我们将外部的收视率数据作为总票数池（Total Vote Pool）的有效代理变量。

**假设 2：投票行为的同质性 (Homogeneity of Voting Behavior)**
尽管规则允许观众投出多票，我们假设支持不同选手的粉丝群体具有相似的投票强度分布（即每位选手的粉丝群中，“路人粉”与“狂热粉”的比例大致相同）。基于此，选手的**得票百分比（Vote Share）\**可以直接反映其\**粉丝群体规模的相对大小**。模型中估算的“票数”实质上是归一化后的“人气指数”。

**假设 3：淘汰结果的严格一致性 (Strict Consistency of Elimination Rules)**
我们假设节目组严格遵循公布的淘汰规则（即综合评分最低者被淘汰），不存在未公开的操纵或随机干预。这意味着，在任意一周，幸存选手的综合得分（裁判分+粉丝分）必然高于或等于被淘汰选手的综合得分。这是我们利用不等式反推粉丝投票区间的核心逻辑基础。

**假设 4：裁判评分与粉丝投票的独立性 (Independence of Judgement and Popularity)**
我们假设粉丝的投票倾向主要受明星个人魅力及过往知名度影响，而不过度依赖当周裁判的具体打分。即裁判打分反映“技术表现”，粉丝投票反映“观众缘”，两者作为独立变量共同决定结果。

To construct a mathematical model for estimating fan votes, based on data characteristics and statistical principles, we make the following assumptions:

**Assumption 1: Proportionality of Total Votes to Viewership**
While not every viewer casts a vote, we assume that the viewer-to-voter conversion rate remains relatively stable throughout a season. Therefore, the **total effective fan votes** for any given episode are **linearly proportional** to that episode's **TV ratings (viewership)**. This allows us to use external viewership data as a valid proxy for the Total Vote Pool.

**Assumption 2: Homogeneity of Voting Behavior**
Although rules permit multiple votes per fan, we assume that the distribution of voting intensity is similar across different contestants' fan bases (i.e., the ratio of "casual voters" to "superfans" is roughly consistent for each celebrity). Consequently, a contestant's **percentage of vote share** directly reflects the **relative size of their fan base**. The "votes" estimated by our model effectively represent a normalized "Popularity Index."

**Assumption 3: Strict Consistency of Elimination Rules**
We assume the show strictly adheres to its stated elimination protocols (i.e., the couple with the lowest combined score is eliminated), with no undisclosed manipulation. This implies that for any given week, the combined score (Judge Score + Fan Vote) of a surviving couple is strictly greater than or equal to that of the eliminated couple. This assumption serves as the foundational constraint for inferring fan vote intervals.

**Assumption 4: Independence of Judgement and Popularity**
We assume that fan voting preferences are primarily driven by the celebrity's charisma and pre-existing popularity, rather than being solely dependent on the judges' scores for that specific week. Thus, judges' scores (reflecting technical performance) and fan votes (reflecting popularity) are treated as independent variables that collectively determine the outcome.