# Transformer 的形式表达力——TC⁰ 之墙到底有多硬

> NTP 候选样章 N2。作者：Xander Xu。
> 状态：🔨 推进中（§1 已写，约 900 字 / 估计全文 4500 字）。

## 一、一堵从 1984 年就存在的墙

故事的真正起点不是 2017 年的 *Attention Is All You Need*，而是 1984 年的一个电路复杂度结果。那一年，Merrick Furst、James Saxe 和 Michael Sipser 证明了一件事：PARITY ——判断一个比特串里 1 的个数是奇数还是偶数——**不在 AC⁰ 里**（[Furst-Saxe-Sipser 1984, *Math. Systems Theory*](https://link.springer.com/article/10.1007/BF01744431)）。换句话说，任何常数深度、多项式宽度、用 AND/OR/NOT 搭起来的电路，都不能在串长 $n \to \infty$ 时可靠地数清 1 的个数。十几年后，Hajnal、Maass、Pudlák、Szegedy 等人把这条线推广到 TC⁰（加入 MAJORITY 门后的常数深度阈值电路），得到一族类似的硬下界。

这件事和 Transformer 有什么关系？答案在 2019 年由 Michael Hahn 第一次说清楚。Hahn 当时是 Stanford 的博士生，他那篇 *Theoretical Limitations of Self-Attention in Neural Sequence Models*（[arxiv:1906.06755](https://arxiv.org/abs/1906.06755)）证明：**hard-attention transformer 在长度 $n$ 上无法均匀地识别 PARITY 或 Dyck-2**。论文写得朴素，结论却很重：一个被工业界吹成"通用近似器"的架构，连"括号是否配平"这种 CFG 入门题都过不去——只要你把序列拉得足够长。Hahn 当时没火，2019 年大家关注的是 BERT 怎么刷榜，没人想听一个学生讲他证明了 Transformer 学不会数括号。

真正把这件事钉死的是 William Merrill。Merrill 现在在 NYU，那几年在 AI2 跟 Ashish Sabharwal 合作，专门做"Transformer 到底落在哪个复杂度类里"这件不性感的事。2021 年他们证明 *saturated transformer*（attention 退化成 hard max 之后）严格属于 TC⁰（[arxiv:2106.16213](https://arxiv.org/abs/2106.16213)）；2022 年又把范围扩展到对数精度下的实际 transformer（[arxiv:2207.00729](https://arxiv.org/abs/2207.00729)）；到 2023 年的 *The Expressive Power of Transformers with Chain of Thought*（[arxiv:2310.07923](https://arxiv.org/abs/2310.07923)）他们才补完最关键的一块拼图：**no-CoT transformer ⊆ TC⁰；加足够多 CoT step 后可以爬到 P，乃至超过**。也就是说，那堵从 1984 年就在那儿的墙，**只能用"在推理时多写几千 token 草稿"翻过去**，不能用"加参数"或"加层数"翻过去。

这是这一章要回答的核心问题：那堵墙到底有多硬？它对今天的 GPT-5、Claude 4.5、DeepSeek-V3 还成立吗？2024–2026 年的一连串新论文又把它推到了什么位置？以及——最重要的——它是 NTP-mech 派必须捍卫的"机制级上界"，还是一个被 CoT 和工程修补悄悄绕过的伪命题？

### 一句话路线图

> **1984 PARITY ∉ AC⁰ → 2019 Hahn 把它搬进 Transformer → 2021–2023 Merrill & Sabharwal 把"Transformer ⊆ TC⁰"做严 → 2023 CoT 打开上界 → 2025 Dziri *Faith and Fate* 给出大模型上的经验对照 → 2026 Deterministic Horizon 与 Low-Prec-Softmax+CoT 两篇论文把"上界"和"绕过"同时推进一步**。

下一节我们回到 Hahn 那篇 2019 论文的细节，看一个 Stanford 博士生是怎么用 6 页证明把整个领域将了一军，又是怎么在接下来的五年里被反复打脸又反复站起来的。

<!-- TODO: §2 Hahn 2019 与"硬注意力"的代价；§3 Merrill–Sabharwal 三部曲与 TC⁰ 的精确刻画；§4 CoT 如何翻墙以及代价是什么；§5 Faith-and-Fate / Deterministic Horizon 的经验对照；§6 反例：summarized CoT、低精度 softmax、tokenization 的暗门；尾声：墙还在，但门也在。 -->
