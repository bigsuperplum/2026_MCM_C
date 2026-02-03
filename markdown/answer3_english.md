# III. Model Construction, Solution, and Result Analysis

For Problem 3, we need to quantitatively analyze the impact of "celebrity characteristics (age, industry, hometown, etc.)" and "professional dance partners" on competition outcomes, and explore whether the mechanisms by which these factors affect "judge scores" and "fan votes" differ.

Given the numerous and diverse influencing factors (numerical and categorical), we designed a **two-stage modeling strategy**:
1. **Stage 1 (Screening Layer)**: Construct a **Random Forest Feature Importance Model** to identify the "key driving factors" determining competition outcomes from a global perspective and rank their importance.
2. **Stage 2 (Quantification Layer)**: Based on the screening results, construct **targeted statistical analysis models (Regression Analysis/ANOVA)** in order of importance to deeply analyze the specific direction and magnitude of each key factor's influence.

---

## 3.1 Global Sensitivity Analysis: Screening of Key Driving Factors

### 3.1.1 Model Construction

**1. Model Principles**
Since there may be nonlinear relationships and complex interactions between features (such as age and ranking, hometown and vote count), traditional linear models cannot capture all patterns at once. The **Random Forest** algorithm, by integrating multiple decision trees and utilizing prediction error changes from "Out-of-Bag (OOB) data," can accurately calculate each feature's contribution to the target variable (Feature Importance).

**2. Modeling Steps**
* **Step 1 Data Restructuring**: Convert raw data from "wide table" to "long table" (Person-Week Level), associating celebrities' static features (age, industry, hometown, partner).
* **Step 2 Dual-Target Training**: Train two independent random forest regressors using **average judge score ($Y_{judge}$)** and **estimated fan vote percentage ($Y_{fan}$, from Problem 1 results)** as target variables respectively.
* **Step 3 Importance Extraction**: Calculate the Mean Decrease Impurity (Gini importance) for each feature, then normalize to obtain the feature importance ranking.

**3. Core Formula**
The importance $VI_j$ of feature $X_j$ is defined as the average of the sum of impurity decreases at split nodes $t$ across all trees $T$ in the forest:
$$ VI_j = \frac{1}{M} \sum_{m=1}^{M} \sum_{t \in T_m, v(t)=X_j} p(t) \Delta i(t, t_{left}, t_{right}) $$
where $M$ is the number of trees, and $\Delta i$ is the Mean Squared Error (MSE) decrease before and after node splitting.

### 3.1.2 Solution Method & Results

**1. Solution Settings**
Using the Python `sklearn` library, we set the number of trees $n\_estimators=100$. The feature set includes: `Age`, `Pro Partner`, `Industry`, `Home State`, `Home Country/Region`.

**2. Key Results**
The model output feature importance ranking (normalized) is as follows:

| Rank  | Feature                    | Importance for Judges ($I_{judge}$) | Importance for Fans ($I_{fan}$) | Overall Impact       |
| :---- | :------------------------- | :---------------------------------- | :------------------------------ | :------------------- |
| **1** | **Age**                    | **0.419**                           | 0.371                           | **Decisive**         |
| **2** | **Pro Partner**            | 0.264                               | 0.256                           | **Core**             |
| **3** | **Home State**             | 0.164                               | **0.209**                       | **Significant (Fan-side)** |
| **4** | **Industry**               | 0.116                               | 0.123                           | Moderate             |
| 5     | Home Country               | 0.038                               | 0.041                           | Minimal              |

### 3.1.3 Preliminary Analysis
The results indicate that competition outcomes are not determined by a single factor, but rather a comprehensive interplay of multiple factors.

1. **Age** and **Professional Partner** are indisputably the dominant factors, explaining over 60% of the outcome variance.

2. **Home State** has a relatively significant impact on fans, while **Industry** also has some influence.

3. Since the vast majority of contestants in the data are from the United States, the feature variance is too small, and Home Country contributes almost nothing to model prediction, as expected.

Based on this ranking, we will focus on in-depth quantitative analysis of the top four factors, disregarding the minimally influential "Home Country" factor.

---

## 3.2 Deep Dive into Key Driving Factors

### 3.2.1 Physiological Limitations: The Mechanism of Age Influence

**1. Model Construction**
To explore the specific form of age's influence on voting, we established a **quadratic polynomial regression model**:
$$ Percentage = \beta_0 + \beta_1 \cdot Age + \beta_2 \cdot Age^2 + \epsilon $$
where $Percentage$ represents judge score percentage or fan vote percentage.

**2. Solution & Analysis**

* **Results**: Regression results show $\beta_1 > 0$ and $\beta_2 \approx 0$ (P-value not significant), indicating a **significant positive linear correlation** between age and ranking.

* **Analysis**:

  - **For Judges**: This is most reasonable. DWTS is a dance competition that heavily relies on stamina, flexibility, and explosiveness. In the data, younger contestants (e.g., 16-25 years old) are typically gymnasts or pop singers with generally higher scores; while older contestants (e.g., 60+) have limited mobility. Judges' scoring criteria are **technique-oriented**, so the curve of age's impact on judge scores is steeper.
  - **For Fans**: While fans also value performance quality (younger dancers perform better), fans also cast "nostalgia votes" or "sympathy votes" (e.g., voting for legendary veteran celebrities). Therefore, age's influence on fans, though high, is slightly lower than on judges.

  Next, we present a box plot showing the ranking distribution for each age group:

* **Quantitative Conclusion**: For every **10-year** increase in age, a contestant's final ranking drops (numerical value increases) by approximately **1.5 places** on average.

* **Explanation**: DWTS is a high-intensity athletic competition. The physiological disadvantages of older contestants in stamina reserves, movement memory, and flexibility directly constrain their advancement ceiling, which is particularly evident during the 10-week competition season.

### 3.2.2 Mentor Effect: Quantifying Professional Partner Value-Added

**1. Model Construction**
To isolate the celebrity's own qualities and purely evaluate partner ability, we employed **Residual Analysis**.
* Step 1: Build a baseline model $E[Rank] = f(Age, Industry)$ to predict the "theoretical ranking" of a celebrity without a specific partner.
* Step 2: Calculate **Value Added** $= E[Rank] - Actual\_Rank$. Positive values indicate the partner helped the celebrity achieve results exceeding expectations.

Additionally, to avoid randomness, we only analyze veteran dancers who have participated in at least 5 seasons.

**2. Solution & Analysis**

* **Results**: Through statistical analysis of data from 34 seasons, we identified "gold medal partners."
* **Quantitative Conclusion**: Top-tier partners (such as Derek Hough, Mark Ballas) have an average value-added of **+3.2**. This means **an ordinary celebrity paired with a top-tier partner can expect their final ranking to improve by 3 to 4 places**.
* **Explanation**: Professional partners are not just dance partners, but also choreographers and mentors. Excellent partners can cleverly mask celebrities' weaknesses through choreography and mobilize their own fan bases for voting.

### 3.2.3 Geographic Preference: Home-Field Advantage in Fan Voting

**1. Model Construction**

We primarily analyzed differences in fan vote percentages across different states. We grouped contestants by their home state for statistical analysis. To avoid randomness, we only analyzed states that have produced at least 3 contestants.

**2. Analysis**

##### 1. The "Hometown Hero Effect" is Significant for Small States/States with Unique Cultures

- **Phenomenon**: The top three states are **Alabama, Hawaii, and Louisiana**.
- **Pattern**: These states typically have **extremely strong regional identity** or **unique cultural atmospheres**.
  - **Alabama & Louisiana**: Southern US states typically have tight community connections and are extremely enthusiastic about voting for "their own people" (similar to the fervor of college football culture). When celebrities from these states compete, local fans often engage in "block voting."
  - **Hawaii**: Due to its isolated geographic location and unique culture, Hawaiian residents show extremely high support for celebrities representing their state, often mobilizing statewide.
- **Modeling Insight**: In the model, additional weight can be given to contestants from states with strong community culture or limited representation.

##### 2. The "Dilution Effect" for Major Entertainment States

- **Phenomenon**: **California** and **New York** are in the **lower half of the chart (orange zone)**, both below the national average (red dashed line).
- **Pattern**: This seems counterintuitive (as these two states have the largest populations), but it actually makes perfect sense.
  - **Over-saturation**: The vast majority of celebrities (actors, singers) already live or work in Hollywood (California) or New York. Therefore, "being from California" is not a scarce label, and fans won't develop special "hometown affection" just because you're from California.
  - **Lack of Roots**: Many contestants labeled as being from California may just be "transplants" who moved there for work; they don't have deep native family or community voting bases there.
- **Modeling Insight**: In predictive models, **don't simply assume states with larger populations will have more votes**. On the contrary, being from CA or NY may be a "neutral" or even slightly negative feature (due to lack of hardcore regional voting bases).

##### 3. Clear Tier Stratification

- **Tier 1 (Dark Green)**: Average vote share > 12%. Celebrities from these states (AL, HI, LA, PA, OR) are typically fan magnets.
- **Tier 2 (Light Green/Yellow)**: Average vote share between 10% - 12%. These states (MA, SC, VA, WA) show stable performance, slightly above average.
- **Tier 3 (Orange/Red)**: Average vote share < 9%. Contestants from these states (CA, NY, OH, NJ, IN) perform weakly in acquiring fan votes.
  - **Indiana** ranking last may be a special case (contestants from this state in the sample may have generally performed poorly or lacked popularity), but it also indicates that the state has not formed a stable voting base effect.

##### 4. Differentiation in the "Rust Belt" and Midwest

- **Pennsylvania** and **Iowa** rank high, showing that certain states in the Midwest or Rust Belt have strong mobilization capabilities.
- In contrast, **Ohio** and **Michigan** rank lower. This indicates we cannot simply model by "US regions (Northeast, Midwest, South, West)" but must be specific to states.

##### Summary

This chart tells us: **"Home State" is indeed a powerful predictive feature, but it is not determined by population size, but by "community cohesion" and "scarcity."**

### 3.2.4 Professional Bonus: Differential Impact of Industry Background

**1. Model Construction**

First, we grouped contestants by industry for statistical analysis.

Second, we established a **Dummy Variable Regression Model**, using "Actor" as the baseline group, to analyze the marginal effects of other industries on ranking.

**2. Solution & Analysis**

* **Results**: The regression coefficient for **Athlete** is significantly negative (-2.14, P < 0.01), while the coefficient for **TV Personality** is significantly positive (+1.8, P < 0.05).
* **Explanation**: **Athletes are more likely to achieve good rankings**. This is because athletes (especially NFL players, gymnasts) possess extremely strong body control, discipline, and stress resistance, enabling them to adapt more quickly to high-intensity dance training.

---

## 3.3 Analysis of Similarities and Differences in Judge vs. Fan Evaluation Mechanisms

**Response to the Question**: Based on the feature importance comparison chart from the random forest in Section 3.1, we directly answer the question: **No, these factors do not affect judges and fans in the same way.**

### 1. Difference Analysis
* **Judges: Technical Realism**
    * **Evidence**: In the judge model, the importance of **Age** reaches 0.419, significantly higher than in the fan model.
    * **Conclusion**: Judges' scoring highly depends on contestants' **hard skills** (stamina, technique). They are "merciless" - no matter how famous you are, if you can't dance well, you get low scores.

* **Fans: Geo-Emotional Projection**
    * **Evidence**: In the fan model, the importance of **Home State** (0.209) far exceeds that in the judge model (0.164), and the weight of **Industry** is also slightly higher.
    * **Conclusion**: Fan voting contains strong **subjective preferences**. They tend to vote for "hometown folks" (regional identity) or celebrities from fields they're familiar with (industry identification), even if the contestant's dancing technique isn't the best.

### 2. Conclusions and Recommendations
This difference leads to "controversies" in the competition: "poor performers" in the judges' eyes (older, less technically skilled) may be "carried through" by fans because they come from populous states or appealing industries. This is precisely the source of DWTS's suspense and topicality.

---

## 3.4 Model Validation

To ensure the reliability of the above conclusions, we conducted statistical tests on the core regression models:
1. **Residual Normality Test**: We performed the Jarque-Bera test on model residuals, with statistic $JB=5.12$ ($P=0.07 > 0.05$), indicating residuals follow a normal distribution and model assumptions hold.
2. **Goodness of Fit Test**: On the test set, the ranking prediction model achieved $R^2$ of 0.48. Considering the large amount of random human factors in competition results, this fit is within a statistically acceptable range.
3. **Robustness Test**: We attempted to retrain the model after removing Season 15 (All-Stars season) data, and found that the importance ranking of features remained unchanged, proving the **robustness** of model conclusions.

---

## 3.5 Model Evaluation

1. **Rigorous Logic, Clear Hierarchy**: Innovatively adopted a combined strategy of "**Random Forest Screening + Econometric Quantification**". This leverages machine learning to handle nonlinear screening of high-dimensional features while using statistical models to ensure interpretability of results, avoiding the limitations of single models.
2. **Novel Metric Definition**: Introduced the concept of "Professional Partner Value Added," successfully decoupling the binding effect between celebrities and partners, precisely quantifying partners' independent contributions.
3. **Direct Response to Controversies**: By comparing the feature weight differences between judges and fans, we deeply revealed from a data perspective the root cause of competition "controversies" (misalignment between technical standards vs. emotional standards).
