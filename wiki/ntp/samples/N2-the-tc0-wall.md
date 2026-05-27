# Transformer 的形式表达力——TC⁰ 之墙到底有多硬

> NTP 候选样章 N2。作者：Xander Xu。
> 状态：🔨 推进中（§1–§4 已写，约 3600 字 / 估计全文 4500 字）。

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

## 四、CoT 如何翻墙，以及一张账单

Merrill-Sabharwal 2023 那个\"加足够多 CoT 就能从 TC⁰ 爬到 P\"的结论看起来像免费午餐。但任何看起来像免费午餐的复杂度结果都附带一张账单。这一节把账单摊开。

时间回到 2023 年 5 月，Guhao Jiang、Bohang Zhang、Tianle Cai、Yuandong Tian、Liwei Wang、Di He 的 *Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective*（[arxiv:2305.15408](https://arxiv.org/abs/2305.15408)）和 Merrill-Sabharwal 几乎平行地给出了 CoT 的表达力刻画。他们走的路线略不同——Feng 等人是构造性证明：对任意可以被 $T(n)$ 步图灵机解决的问题，存在一个常数深度的 Transformer，只要允许它输出 $O(T(n))$ 个中间 token，就能模拟该图灵机。换句话说，**CoT 本质上是把\"算法的时间维\"展开到\"序列的空间维\"**，让本来要靠深度堆叠的递归被外化成 token 流。这和 Merrill-Sabharwal 的上界版本互为表里：一个给出 \"$\\leq$\"，一个给出 \"$\\geq$\"，把 CoT-augmented transformer 这个对象的复杂度边界夹住了。

但账单写在论文的脚注里。三笔费用：

**第一笔，token 数。** 若被模拟的算法是 $O(n^2)$（例如简单的多项式整除、长除法、Dyck-k 的栈模拟），CoT 长度也必须 $\\Omega(n^2)$。对 $n=1000$ 的输入，CoT 需要约 $10^6$ token——超过当前 frontier model 单次生成的实际上限两到三个数量级。Merrill-Sabharwal 的渐近翻墙在工程意义上对长输入是不可达的，对短输入又无人验证。

**第二笔，位置编码与注意力精度。** Feng 等人构造里的 Transformer 需要能精确寻址 $\\Theta(n)$ 范围的位置——这对 RoPE / ALiBi / NoPE 在长 context 下的外推精度提出了非平凡要求。Anthony Chen、Anej Svete、David Chiang 等人 [unverified 具体引用] 在 2024 年的后续工作里指出，许多 \"理论上 CoT 能解\" 的任务在标准位置编码下学不出来，原因恰恰是位置寻址的有限精度让 step-$t$ 的 token 无法可靠地回看 step-$t-k$ 的中间结果。**复杂度类上的翻墙不等于训练动力学上的翻墙**——这是 §6 会重提的反例线。

**第三笔，CoT 的可靠性。** Merrill-Sabharwal 与 Feng 的定理都默认 CoT 是\"忠实计算\"——模型输出的每一步中间 token 都被后续 step 真实使用。但 Miles Turpin 等人的 *Language Models Don't Always Say What They Think*（[arxiv:2305.04388](https://arxiv.org/abs/2305.04388)）和 Tamera Lanham 等人的 *Measuring Faithfulness in Chain-of-Thought Reasoning*（[arxiv:2307.13702](https://arxiv.org/abs/2307.13702)）经验地证明：今天的大模型 CoT 大量是事后合理化，模型即使写出\"step 1: 36×72 = ...\"也未必真把那一步当输入用。也就是说，**理论上的 CoT 翻墙假设了一个工程上几乎不成立的前提**——这一点 §5 讲 Faith-and-Fate 时会变成核心矛盾。

把三笔加在一起，可以得到一张更诚实的对照表：

| 维度 | 定理意义上 | 工程实际 |
|---|---|---|
| 复杂度类 | CoT 把 TC⁰ 扩展到 $\\mathsf{TIME}(t(n))$ | frontier model 实际 CoT $\\leq 10^4$ token |
| 位置寻址 | 精确到 $\\Theta(n)$ | RoPE 外推后明显衰减 |
| 忠实性 | 每一步 token 被后续使用 | Turpin/Lanham 显示大量是事后合理化 |
| 翻墙代价 | 多写 token | 推理时间 × 显存 × KV cache 平方增长 |

**判断**：CoT 是一根真梯子，但不是免费梯子。Merrill-Sabharwal 把墙的存在做严，Feng 等人把翻墙的可能做严，而 Turpin、Lanham、Chen-Svete-Chiang [unverified 后两人引用] 这一系列工作合起来在说：梯子在数学上够得着 P，但每一阶都收费，而且部分阶梯是纸糊的。2024–2026 年 reasoning model 的整条工程史——o1 把 CoT 拉到 $10^4$ 量级、R1 用 RL 学 long CoT、Claude 4 Extended Thinking 引入可计费的 thinking budget——本质都是在这张账单上做局部优化：要么压缩 token 数，要么提升忠实度，要么把寻址精度做高。没有人否认墙在那里，**他们都在为爬梯子付钱**。下一节回到经验侧，看 Dziri 的 *Faith and Fate* 怎么把这张账单画成 GPT-4 的实验曲线。

## 五、Faith and Fate：把账单画成 GPT-4 的实验曲线

理论那一侧的话讲到这里其实已经收尾——剩下的问题是：那条 TC⁰ 上界、那把 CoT 梯子、那张三笔费用的账单，在 GPT-4 这种已经放进生产环境的模型上**真的能看见**吗？2023 年 5 月 Nouha Dziri 等人在 NeurIPS 2023 spotlight 的 *Faith and Fate: Limits of Transformers on Compositionality*（[arxiv:2305.18654](https://arxiv.org/abs/2305.18654)）给出了一份接近实验室级别的答案。Dziri 当时在 Allen Institute for AI 的 Mosaic 团队，合作者包括 Faeze Brahman、Jena Hwang、Yejin Choi。这篇论文挑了三个 compositional 任务——**多位数乘法**（"3 位 × 3 位"到"5 位 × 5 位"）、**Einstein 风格逻辑谜题**（k 个属性、k 个对象的约束求解）、**动态规划**（最长递增子序列）——并且对每个任务系统地扫一个"难度参数"：乘法的位数 $d$、谜题的实体数 $k$、DP 的输入长度 $n$。

结果是教科书式的。三个任务都呈现同一个形态：在某个临界难度之前 GPT-4 的 accuracy 几乎 100%，越过临界点后**断崖式跌**到接近 0，且**无论怎么 prompt、怎么 fine-tune、怎么加 CoT，曲线都只是平移，不会变形**。具体的数：4 位 × 4 位乘法 GPT-4 zero-shot ≈ 4%，CoT 推到 ≈ 30%，scratchpad fine-tune 也只能把 4×4 拉到 50% 左右，再到 5×5 全军覆没 [unverified 具体百分比 — 见原论文 Figure 2/3]。Einstein 谜题在 $k=4$ 还能 80%+，$k=5$ 跌到 30%，$k=6$ 接近随机猜。DP 长度 $n=6$ 还行，$n=8$ 起塌。

最毒的一刀在论文 §5：Dziri 等人**显式做了 "在难度 $d$ 上 fine-tune 后能否外推到 $d+1$" 的实验**。答案是不能——in-distribution 准确率可以拉到 90%+，但 OOD（多一位）立刻掉到 10%。这把"模型只是没见够数据"这一最常见的辩护一次性堵死：见够了 $d$ 的数据并不构成对 $d+1$ 的任何先验。Dziri 把这种现象叫 *compositional gap*，并明确把它解读成"自回归 next-token 模型在 task graph 深度上的隐含天花板"。这恰好是 Hahn 2019 与 Merrill-Sabharwal 三部曲在经验侧的影子——一边渐近证明、一边经验测量，两条线在 GPT-4 上汇合。

这一击对 NTP-mech 派的意义是：墙不再是数学纸面上的事。3 位乘法对人类小学生是小事，对 GPT-4 也是；4 位起人类要拿草稿纸了，GPT-4 也得 CoT；5 位人类必须严格按算法走，GPT-4 即使 CoT 也开始系统性漏进位；6 位双方都崩——只是人类崩在工作记忆，GPT-4 崩在 attention 寻址精度（这一对应不是巧合，§4 的"第二笔费用"正是位置寻址）。这是过去十年里第一次，一个**架构上界的渐近预测**和**前沿模型的经验曲线**在同一张图里几乎对齐。

但 Faith and Fate 也有它的脆弱点，必须诚实写出来：

1. **任务选择偏倚**。三个任务都是 compositional/algorithmic 风格，GPT-4 训练分布里这类样本相对稀疏。换成 retrieval-heavy 或 commonsense reasoning 任务，同样深度下崩塌点会显著推后。Dziri 在论文 §7 自己承认这一点。
2. **CoT 协议局限**。论文里的 CoT 是 prompt-engineered scratchpad，不是 o1/R1 那种 RL-trained long CoT。2024-09 之后 reasoning model 在多位乘法上的成绩已经显著优于 GPT-4 base + CoT——但**仍未消除 compositional gap**，只是把临界点从 4 位推到 7-8 位 [uncertain 具体数据]。墙在退，没倒。
3. **GPT-4 黑盒**。Dziri 团队没法看模型内部，所以"4 位是 attention 寻址崩溃 vs 是数据稀疏 vs 是 tokenization artifact（数字 tokenizer 把"1234"切成多少 token 直接影响成败）"这三个 confound 没有被分离。Singh & Strouse 2024 *Tokenization Counts*（[arxiv:2402.14903](https://arxiv.org/abs/2402.14903)）后来证明数字分词协议对算术准确率有 10–30 pp 的独立影响——这一项 Faith and Fate 当年没控住。

**判断**：Faith and Fate 是 NTP-mech 派经验侧最干净的一发子弹，但它也是最容易被反驳模糊化的一发——因为它的实验设计同时混入了 compositional depth、tokenization、CoT 协议、训练分布四个变量。理论侧（Hahn / Merrill / Feng）说"墙存在且 CoT 是梯子"，经验侧（Dziri）说"在 GPT-4 上看得见且 fine-tune 不能外推"，但要把这两条线**严格对齐到同一个 mech 候选**——比如声称 "GPT-4 在 4 位乘法上的崩塌正是 log-precision TC⁰ 上界的体现"——目前还差一步可控实验。Allen-Zhu *Physics of Language Models Part 3.3*（[arxiv:2407.20311](https://arxiv.org/abs/2407.20311) [unverified 具体 part 编号]）这一系工作正在试图填上这一步：在完全合成的数据 + 受控架构下复现 Dziri 的曲线，并把崩塌点和 attention head 内部寻址误差关联起来。如果这条线能在 2026 内做严，那 Hahn-Merrill-Dziri 三人会在引用网络里被串成一条不可拆的因果链——TC⁰ 之墙就不再只是一个理论 corner case，而是 frontier model 的工程现实。

下一节（§6）回到反例侧：summarized CoT、低精度 softmax+CoT 的 Turing-completeness、tokenization 暗门，这三条 2024–2026 的工作分别从哪些方向把墙的位置又推了一下。

<!-- TODO: §6 反例：summarized CoT、低精度 softmax、tokenization 的暗门；尾声：墙还在，但门也在。 -->
