# Transformer 的形式表达力——TC⁰ 之墙到底有多硬

> NTP 候选样章 N2。作者：Xander Xu。
> 状态：🔨 推进中（§1–§3 已写，约 2700 字 / 估计全文 4500 字）。

## 一、一堵从 1984 年就存在的墙

故事的真正起点不是 2017 年的 *Attention Is All You Need*，而是 1984 年的一个电路复杂度结果。那一年，Merrick Furst、James Saxe 和 Michael Sipser 证明了一件事：PARITY ——判断一个比特串里 1 的个数是奇数还是偶数——**不在 AC⁰ 里**（[Furst-Saxe-Sipser 1984, *Math. Systems Theory*](https://link.springer.com/article/10.1007/BF01744431)）。换句话说，任何常数深度、多项式宽度、用 AND/OR/NOT 搭起来的电路，都不能在串长 $n \to \infty$ 时可靠地数清 1 的个数。十几年后，Hajnal、Maass、Pudlák、Szegedy 等人把这条线推广到 TC⁰（加入 MAJORITY 门后的常数深度阈值电路），得到一族类似的硬下界。

这件事和 Transformer 有什么关系？答案在 2019 年由 Michael Hahn 第一次说清楚。Hahn 当时是 Stanford 的博士生，他那篇 *Theoretical Limitations of Self-Attention in Neural Sequence Models*（[arxiv:1906.06755](https://arxiv.org/abs/1906.06755)）证明：**hard-attention transformer 在长度 $n$ 上无法均匀地识别 PARITY 或 Dyck-2**。论文写得朴素，结论却很重：一个被工业界吹成"通用近似器"的架构，连"括号是否配平"这种 CFG 入门题都过不去——只要你把序列拉得足够长。Hahn 当时没火，2019 年大家关注的是 BERT 怎么刷榜，没人想听一个学生讲他证明了 Transformer 学不会数括号。

真正把这件事钉死的是 William Merrill。Merrill 现在在 NYU，那几年在 AI2 跟 Ashish Sabharwal 合作，专门做"Transformer 到底落在哪个复杂度类里"这件不性感的事。2021 年他们证明 *saturated transformer*（attention 退化成 hard max 之后）严格属于 TC⁰（[arxiv:2106.16213](https://arxiv.org/abs/2106.16213)）；2022 年又把范围扩展到对数精度下的实际 transformer（[arxiv:2207.00729](https://arxiv.org/abs/2207.00729)）；到 2023 年的 *The Expressive Power of Transformers with Chain of Thought*（[arxiv:2310.07923](https://arxiv.org/abs/2310.07923)）他们才补完最关键的一块拼图：**no-CoT transformer ⊆ TC⁰；加足够多 CoT step 后可以爬到 P，乃至超过**。也就是说，那堵从 1984 年就在那儿的墙，**只能用"在推理时多写几千 token 草稿"翻过去**，不能用"加参数"或"加层数"翻过去。

这是这一章要回答的核心问题：那堵墙到底有多硬？它对今天的 GPT-5、Claude 4.5、DeepSeek-V3 还成立吗？2024–2026 年的一连串新论文又把它推到了什么位置？以及——最重要的——它是 NTP-mech 派必须捍卫的"机制级上界"，还是一个被 CoT 和工程修补悄悄绕过的伪命题？

### 一句话路线图

> **1984 PARITY ∉ AC⁰ → 2019 Hahn 把它搬进 Transformer → 2021–2023 Merrill & Sabharwal 把"Transformer ⊆ TC⁰"做严 → 2023 CoT 打开上界 → 2025 Dziri *Faith and Fate* 给出大模型上的经验对照 → 2026 Deterministic Horizon 与 Low-Prec-Softmax+CoT 两篇论文把"上界"和"绕过"同时推进一步**。

下一节我们回到 Hahn 那篇 2019 论文的细节，看一个 Stanford 博士生是怎么用 6 页证明把整个领域将了一军，又是怎么在接下来的五年里被反复打脸又反复站起来的。

## 二、Hahn 2019：一个博士生用 6 页证明把整个领域将了一军

回到 2019 年 6 月。Michael Hahn 把 *Theoretical Limitations of Self-Attention in Neural Sequence Models* 挂上 arXiv（[arxiv:1906.06755](https://arxiv.org/abs/1906.06755)）的时候，NeurIPS 2019 还在筹备，BERT 刚发布大半年，GPT-2 因为 "too dangerous to release" 刷了一波热度。整个社区的注意力都在"还能加多少 head、能不能再 distill 一档"上。Hahn 的论文走的是相反方向：他想知道，这种架构*不能*学会什么。

论文的核心定理可以拆成两条。第一条针对**硬注意力**（hard attention，即 attention 权重被 argmax 锐化成 one-hot）：对任意固定参数的硬注意力 Transformer，存在长度阈值 $n_0$，当输入长度 $n > n_0$ 时它在 PARITY 与 Dyck-2（仅含两类括号的 Dyck 语言）上的错误率必然不收敛到 0。证明的关键是一个 Lipschitz 风格的论证——硬注意力让整个网络对单 token 翻转的敏感度被 head 数和深度上界封死，而 PARITY 的定义恰恰要求"翻转任意一位都改变输出"。两件事互不相容。

第二条针对**软注意力**（soft attention，标准 softmax），结论更微妙：在"输入足够长 + 数值精度有限"的联合极限下，软注意力的有效感受野会被 logits 间距挤压成几个高峰，行为退化到接近硬注意力。也就是说，软注意力**在渐近意义上没有真正逃出硬注意力的牢笼**——只是把失败推后到更大的 $n$。这一条后来被 Merrill-Sabharwal 沿 "log-precision" 这条线做严，但 2019 年的 Hahn 已经把直觉点透。

这篇论文当时几乎没人读。Google Scholar 上 2020 年全年引用不到 30 次 [unverified 具体数]，对比 BERT 同期是四位数。理由有三：（1）实验只跑到长度几百，工程师不觉得是问题；（2）证明用了语言学社区的 Dyck 语言而不是大家熟的 NLP benchmark；（3）Hahn 本人是 Stanford 语言学系的博士生（导师 Chris Manning 方向 [unverified 具体导师]），不是"主流 ML 圈"。直到 2021 年 Merrill 把它接续起来，社区才意识到 Hahn 那 6 页是个起手式。

也有反驳。一类常见反驳是"实践中我们从来不要求 100% PARITY，我们要的是分布上的下一 token"——这听上去合理，但 Hahn 反驳得很干脆：PARITY 不是 toy，它是任何"全局聚合"任务的最小代表（计数 / 投票 / 校验和 / 状态机奇偶相位）。如果一个架构在 PARITY 上有渐近硬下界，那么所有可约化到 PARITY 的下游任务都继承这条下界。后来 [arxiv:2305.18654](https://arxiv.org/abs/2305.18654)（Dziri et al., *Faith and Fate*）做的多位数乘法实验，本质就是把 Hahn 的渐近论证翻译成 GPT-4 上的可视化曲线。

**判断**：Hahn 2019 的历史地位被严重低估。它是"NTP-mech 派"——主张 NTP 有架构级硬上界的人——的第一块基石；后面 Merrill、Chiang、Sanford、Feng 一系列工作都建立在它的论证骨架上。但它也有真正的脆弱点：定理假设的是"固定参数 + 长度 $n \to \infty$"，而工业界用的是"位置编码可外推 + 上下文窗口随版本翻倍 + CoT 当作运行时草稿纸"。这三项都没被 Hahn 的定理直接覆盖。也就是说，**这堵墙是真的，但它挡的是"参数翻墙"，不是"token 翻墙"**——这一点要等 §4 讲 Merrill-Sabharwal 2023 的 CoT 上界定理时才能说清楚。

## 三、Merrill–Sabharwal 三部曲：把 "Transformer ⊆ TC⁰" 做成定理

Hahn 2019 留下的是一个**存在性下界**：存在某些任务，固定参数的 Transformer 永远学不会。它没有告诉我们 Transformer 这种架构整体落在哪个复杂度类里。把这件事做严的，是 William Merrill 和 Ashish Sabharwal 从 2021 到 2023 三年里的三篇论文——这一节我把它们当作三部曲来讲，因为它们其实在回答同一个问题，只是逐步收紧假设。

**第一部：2021 年的 saturated transformer。** Merrill 那时还在 AI2 实习，他和 Sabharwal、Yoav Goldberg 等人合写了 *Saturated Transformers are Constant-Depth Threshold Circuits*（[arxiv:2106.16213](https://arxiv.org/abs/2106.16213)）。所谓 saturated，是指把 softmax 的温度推到 0、attention 退化成 hard-max 之后的极限形式。论文证明：这种 saturated transformer 可以被一个常数深度、多项式宽度、带 MAJORITY 门的阈值电路模拟——正是教科书里的 TC⁰ 定义。这是第一次有人把一个具体的 Transformer 变种和一个具体的复杂度类用"⊆"号连起来。代价是 saturation 这一步太强，工业界没人这么用。但骨架已经搭好：attention 权重的离散化 → 电路深度的常数化 → 复杂度类的指认。

**第二部：2022 年的 log-precision transformer。** 一年后，Merrill 和 Sabharwal 单独合作了 *The Parallelism Tradeoff: Limitations of Log-Precision Transformers*（[arxiv:2207.00729](https://arxiv.org/abs/2207.00729)）。这篇放弃了 saturation 假设，换成一个更现实的设定：每个标量用 $O(\log n)$ 位精度表示——这是浮点数在序列长度 $n$ 下的自然假设。结论是同样的：log-precision transformer ⊆ uniform TC⁰。这一篇的技术核心是 *parallelism tradeoff*——Transformer 的"快"（深度 $O(1)$、单步推理可并行）和它的"弱"（落在 TC⁰ 里）来自同一个性质。你不可能两者都要。这是一个有形而上味道的结论：架构选择本身就在表达力上预付了一笔学费。

**第三部：2023 年的 CoT 上界。** 真正合拢这个故事的是 *The Expressive Power of Transformers with Chain of Thought*（[arxiv:2310.07923](https://arxiv.org/abs/2310.07923)）。Merrill 和 Sabharwal 在这篇里问的是：如果允许 transformer 在推理时输出 $t(n)$ 个中间 token 再读回作为输入，它能爬到哪个复杂度类？答案漂亮得像教科书安排好的：CoT 长度为 $\Theta(\log n)$ 时仍在 $\mathsf{L}$ 附近，$\Theta(n)$ 时可达 $\mathsf{P}$，$\Theta(n^2)$ 甚至可以触到 PSPACE 的某些片段 [uncertain 具体常数]。换句话说，**no-CoT transformer 被钉死在 TC⁰，而 CoT 是一根可以让它任意爬高的梯子——只要你愿意付 token 的钱**。这就解释了 2023 年之后整个工业界为什么集体押注 reasoning model（o1/R1/Claude-thinking）：不是因为 CoT 好看，而是因为它是从 TC⁰ 翻墙的唯一已知合法通道。

把三篇拼起来看，可以画出一张很干净的图：

| 假设 | 复杂度类 | 出处 |
|---|---|---|
| Saturated (hard-max) | ⊆ TC⁰ | [arxiv:2106.16213](https://arxiv.org/abs/2106.16213) |
| Log-precision softmax，固定深度 | ⊆ uniform TC⁰ | [arxiv:2207.00729](https://arxiv.org/abs/2207.00729) |
| + CoT $t(n)$ steps | ⊆ 大致 $\mathsf{TIME}(t(n))$ 类 | [arxiv:2310.07923](https://arxiv.org/abs/2310.07923) |

要诚实地说：这三篇的上界都是**worst-case 渐近**，不是平均 case，也不是小 $n$ 行为。Anej Svete、David Chiang 等人 [unverified 具体引用] 后来指出，very-small-depth + 特定位置编码的 transformer 在有限 $n$ 上行为可能比 TC⁰ 富，因为 uniform vs. non-uniform 的区分在工程长度下还没生效。也有更尖锐的反论：Sanford、Hsu、Telgarsky 的 *Representational Strengths and Limitations of Transformers*（[arxiv:2306.02896](https://arxiv.org/abs/2306.02896)）证明在某些 sparse averaging 任务上 Transformer 反而比 RNN 指数级地强——表达力的故事不是单向的"Transformer 弱"，而是"它在这一类强、在另一类弱"。

**判断**：Merrill–Sabharwal 三部曲的真正贡献不是"证明了 Transformer 弱"，而是**把"弱在哪里、靠什么翻墙"做成了一个有边界条件的工程问题**。今天任何一篇讲 reasoning model 的论文，如果它声称在某个 NTP-mech 上有所突破，都应该先回答：你的实验落在 $n$ 的哪一段？你的 CoT 长度增长是 $O(\log n)$ 还是 $O(n)$？如果作者答不出来，那就是在 TC⁰ 这堵墙的脚下原地打转。这一节为下一节的 CoT 翻墙代价分析（§4）和 Faith-and-Fate 的经验对照（§5）铺好了路。

<!-- TODO: §4 CoT 如何翻墙以及代价是什么（Feng 2305.15408、Li-Liu-Sanford 等的精细化）；§5 Faith-and-Fate / Deterministic Horizon 的经验对照；§6 反例：summarized CoT、低精度 softmax、tokenization 的暗门；尾声：墙还在，但门也在。 -->
