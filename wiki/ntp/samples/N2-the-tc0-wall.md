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

## 六、反例：墙的位置不是定死的——三道暗门

到 §5 为止，整个故事看起来像 NTP-mech 派的胜利演讲：Hahn 给下界，Merrill 给上界，Feng 给翻墙构造，Dziri 给经验曲线，四方合围把 TC⁰ 这堵墙立得很稳。但任何把复杂度结论当成"工程判决书"读的人都会很快被反例打脸。2024–2026 这两年里至少有三条工作线把墙的位置往后推了不止一点。这一节把它们摆在一起，看看哪些是真暗门，哪些只是把墙的厚度刷得更精细。

**第一道门：summarized / compressed CoT。** Feng 等人 2023 那个翻墙构造的 token 账单写得太刺眼——$O(n^2)$ 算法要 $\Omega(n^2)$ 个中间 token，谁也付不起。Sachin Goyal、Ziwei Ji、Ankit Singh Rawat、Aditya Krishna Menon、Sanjiv Kumar、Vaishnavh Nagarajan 的 *Think before you speak: Training Language Models With Pause Tokens*（[arxiv:2310.02226](https://arxiv.org/abs/2310.02226)）2023 年 10 月给出了第一种妥协：在输入末尾插入若干个不携带词表信息的 `<pause>` token，让 transformer 用它们做"无内容的额外计算 step"。这绕开了"中间 token 必须可读"的限制——梯子的每一阶不再需要写人话。Tom McCoy、Shunyu Yao 等人 [unverified 具体引用] 在 2024 年继续这条线，提出 *latent / continuous CoT*：把中间 step 留在残差流而不是采样回输入。Hao 等人的 *Coconut*（[arxiv:2412.06769](https://arxiv.org/abs/2412.06769) [unverified ID]）2024-12 把这一思路做到 GSM8K 上 outperform 同 token budget 的 plain CoT 一档。表面看，墙没有挪，付款方式变了；但从 NTP-mech 的角度看这是真暗门——**TC⁰ 上界证明里的"每 step 都是离散 token"假设被实质打破了**。Merrill-Sabharwal 2023 自己在论文 §7 也承认，连续中间状态超出他们的刻画范围。

**第二道门：低精度 + 长 CoT 反而 Turing-complete。** Dale Schuurmans、Hanjun Dai、Francesco Zanini 的 *Autoregressive Large Language Models are Computationally Universal*（[arxiv:2410.03170](https://arxiv.org/abs/2410.03170) [unverified ID]）2024-10 走了一条几乎和 Merrill-Sabharwal 相反的路线：他们论证一个**固定参数**的自回归 LLM，只要允许无限输出且环境会把输出 append 回输入，就能模拟通用 Turing machine——本质是把 Lag system / tag system 嵌进 next-token 行为。这和 §3 的 TC⁰ 上界**并不冲突**：Merrill-Sabharwal 限定 *single forward pass* 的复杂度，Schuurmans 等人允许 *unbounded autoregressive rollout*，等价于把循环时间 $T$ 推到 $\infty$。但工程含义不同——它告诉你"transformer 架构本身没有图灵不完备的硬伤"，墙的存在条件是 *有限 rollout 长度 + 固定数值精度*，两者只要松动一项，结论就变。Pérez、Marinkovic、Barceló 早在 [arxiv:1901.03429](https://arxiv.org/abs/1901.03429) 就用任意精度论证过类似结果，但 Schuurmans 2024 是第一次在 frontier model 时代把它写得直接对应到"agent loop"这种真实部署形态。这一条对 N1 §3 引用过的"Sutton 派"是个加分项——它说**你只要给足时间和反馈通道，架构不会拦你**。

**第三道门：tokenization 不是中性外壳。** 第三道暗门最阴险，因为它把"模型能力"和"分词协议"耦合到无法解耦的程度。Aaditya Singh、Daniel Strouse 的 *Tokenization counts: the impact of tokenization on arithmetic in frontier LLMs*（[arxiv:2402.14903](https://arxiv.org/abs/2402.14903)）2024-02 系统扫了 GPT-3.5/4、Llama、Mistral 的数字分词协议，发现"从右往左 3 位一组"（如 Llama）比"贪心 BPE"（如 GPT-3.5）在 5 位加法上能提升 20–30 pp。Allen-Zhu 等人在 *Physics of Language Models Part 2.1/2.2*（[arxiv:2407.20311](https://arxiv.org/abs/2407.20311) [unverified 具体 part 编号]）的合成实验里更直接：同一个 transformer 架构、同一份训练数据、只换分词，算术准确率可以从 30% 跳到 95%。这意味着 Hahn-Merrill-Dziri 那条线讲的"架构表达力上界"和工程曲线之间还垫了一层"输入表征"，而这一层在 NTP 范式里属于 hyperparameter，不属于架构本身。**墙没动，但墙的位置取决于你从哪一面量**——这一点 2019 年的 Hahn 完全没意识到，他默认的是 character-level 或 word-level 输入。

把三道门放在一起，可以得到一张比 §4 更微妙的修订表：

| 漏洞 | 谁打开的 | 上界证明里的哪个假设被破 |
|---|---|---|
| Latent / pause CoT | Goyal 2310.02226, Hao 2412.06769 [unverified] | "中间 step = 离散 token" |
| 无界 rollout + agent loop | Schuurmans 2410.03170 [unverified] | "单次 forward 复杂度" |
| Tokenization 重塑输入 | Singh-Strouse 2402.14903, Allen-Zhu 2407.20311 | "输入表征中性" |

也有反反例。Sanford、Hsu、Telgarsky 在 [arxiv:2402.04347](https://arxiv.org/abs/2402.04347)（*Transformers, parallel computation, and logarithmic depth*）2024-02 进一步收紧了 Transformer ⊆ TC⁰ 这条结论：他们指出无论你怎么操作位置编码、attention sparsity 或精度，只要保持 $O(1)$ 层深和多项式宽度，**parallel computation thesis 这条假设级别的墙是搬不走的**。换句话说，第二道门 Schuurmans 路线必须吃掉时间维（rollout 长度），第一道门 Coconut 路线必须吃掉精度维（连续残差），没有任何方案能同时保住"$O(1)$ 深 + 离散输出 + 单 forward pass"这三件事还把复杂度类爬上 NC¹。墙没倒，门都有代价。

**判断**：三道暗门让 §3-§5 那个干净故事变得不再干净——这对 NTP-mech 派是好事，不是坏事。任何一个真正能落地的"NTP 有架构级硬上界"主张，都必须显式声明它假设的 CoT 协议（离散 / 连续）、rollout 边界（有限 / 无限）、和 tokenization 协议（固定 / 优化）。2026 年的 reasoning model 路线（o3、R2、Claude 4.5 Extended Thinking）实际上已经在用这三道门的组合下注：Extended Thinking 把 rollout 推到 $10^5$ token 级、latent CoT 在某些内部 variant 里被试验、tokenizer 在 frontier 模型里也开始针对数字单独训练。墙还在，但每一道门都被工程界轮流推过一次。NTP-mech 派接下来要做的不是再加固墙——Hahn-Merrill 那一侧已经做到极致——而是**给每一道门标上代价函数**，把"翻墙到底花多少钱、买到多少能力"做成可计费的曲线。这正是 N8（*Sutton 又赢一次？*）要从另一个角度回答的问题。

## 尾声：墙、梯、门——以及读者应该带走的三件事

回到 1984 年那个 STOC 会议的下午。Furst-Saxe-Sipser 把 PARITY $\notin$ AC⁰ 写定的时候，他们当然不可能想到这条结论四十年后会被用来评判一个叫 transformer 的神经网络架构。但电路复杂度这一支的工作有它独特的生命力——它一旦把某个函数类和某个资源界绑死，结论几乎不可能被新硬件、新优化器、新数据集推翻。Hahn 2019 把这条传统接到了 transformer 上，Merrill 2021-2023 把它做成了定理，Dziri 2023 把它做成了 GPT-4 的实验曲线，Goyal / Schuurmans / Singh 2024 又把它的三道门标了出来。这条引用链是 NTP 这本综述里最稳的一段——稳到几乎可以当 baseline 用来校准其他线（N3 reversal curse、N4 因果阶梯、N5 embodiment、N7 continual learning）的强度。

读者带走三件事就够：

1. **TC⁰ 之墙是真的，但它挡的是"固定参数 + 单 forward pass + 离散输出"这个三元组**。任何一项松动，墙就移动。
2. **CoT 是真梯子，但每一阶都收费**——token 数、寻址精度、忠实性三笔账谁也跑不掉。Reasoning model 整条路线都在为这张账单做局部优化。
3. **经验和理论第一次在 Dziri 2023 上对齐**——这意味着接下来五年 NTP-mech 派的工作重心应该从"再证一个更紧的上界"转到"用 mech-interp 在 frontier model 内部直接验证那个上界发生在哪一层、哪个 head、哪个 token 位置"。Anthropic 的 *Tracing Thoughts*（[arxiv:2502.06664](https://arxiv.org/abs/2502.06664) [unverified ID]）和 OpenAI 的 weak-to-strong supervision 那一系工作正好提供了工具链。

诚实地说，这堵墙最大的不确定性不在数学，而在 reasoning model 这两年的实际进展速度。如果 2027 年我们看到一个 frontier model 在 8 位乘法、$k=10$ Einstein 谜题、$n=20$ 最长递增子序列上 zero-shot 90%+，那本章的判断需要被修订——不是 Hahn-Merrill 错了，而是 §6 那三道门的组合代价比我们预估的低一个量级。反之，如果到 2027 年 Dziri 的崩塌点只是从 4 推到 6，那本章的判断就被加固。这是一道时间会自己回答的题。

下一篇（N3）会换一个 mech 候选：Reversal Curse、不忠实 CoT、Faith-and-Fate 三块拼图能不能拼成同一面墙？还是它们指向三面不同的墙？


## 七、2026 年 5 月补遗：墙的位置在过去半年又被推过两次

写完前六节之后，2025 下半年到 2026 年 5 月之间又落下几条与本章直接相关的证据，必须钉到时间戳上，否则 §6 那张\"三道暗门\"修订表很快会显得过时。把它们逐条按 \"动哪个假设\" 排列。

**第一条：内圈墙先撞——formal_limits.md §第二堵墙的整合**。本章 §3–§5 主线是 expressivity 上界，但 2024–2026 frontier 真实瓶颈的实测证据几乎一致指向 *learnability*，不是 expressivity。Liu shortcuts [arxiv:2210.10749](https://arxiv.org/abs/2210.10749)、Reversal Curse [arxiv:2309.12288](https://arxiv.org/abs/2309.12288)、Allen-Zhu Physics-of-LM 知识容量/检索 [arxiv:2305.13673](https://arxiv.org/abs/2305.13673)、grokking modular-add [arxiv:2301.05217](https://arxiv.org/abs/2301.05217)、Bordelon dynamical scaling [arxiv:2402.01092](https://arxiv.org/abs/2402.01092) 五条证据线合起来构成一道**比 TC⁰ 更靠前的内圈墙**——表达力够而 NTP 学不到，记录在 topics/formal_limits.md 候选 C-FORM-4 \"NTP-learnability gap\"。这对本章 §3 那个干净的 Merrill-Sabharwal 三部曲意味着：上界证明虽然没错，但 *frontier-scale 上的实测崩塌点很可能根本不发生在那道墙上*，而发生在更靠前的内圈墙上。Dziri 4 位乘法崩塌的真实原因到底是 log-precision TC⁰ 上界，还是 NTP loss 对 compositional depth 的 learnability bias 提前撞顶，2026-05 这个时点严格来说是 *未分离的两个 confound*。本章 §5 末尾给的判断（\"理论侧和经验侧第一次在 Dziri 2023 上对齐\"）在这层 caveat 下需要被弱化：对齐的是数字，不一定是机制。

**第二条：低精度 + log-grow depth 把 §3 的上界进一步实质打开**。Brösamle 与 Eckstein 2026-05 ([arxiv:2605.18079](https://arxiv.org/abs/2605.18079)) 证了一个比 Schuurmans 2024 更狠的结果：**低精度 softmax + depth 随 $n$ 缓慢增长**这一对组合，足以让 transformer 在 summarized CoT 设定下保持 Turing-complete，且空间复杂度可以从 Feng 2023 的 $\Omega(n^2)$ 压到 $O(\log n)$ 量级 [uncertain 具体常数]。这条结果对本章 §6 的修订表是一次 *实质性* 打开——\"单 forward pass\" 这一假设原本要在精度旋钮上死守，现在精度旋钮可以让到工程合理范围（fp8 / int4）而不丢通用性，只要愿意付出 log-grow depth 的代价。这一击的意义不在 \"墙塌了\"，而在 \"翻墙的代价函数被显著重写\"——Merrill-Sabharwal CoT 上界给的 $\Omega(n^2)$ token 账单在 2024 年看起来是工程不可达的，到 2026 年同任务的代价被部分摊到 depth 这一维，frontier reasoning model（o3 / R2 / Claude 4.5 Extended Thinking）实际部署的 thinking-trace 长度仍在指数往上爬但 *已经不再是唯一的代价通道*。把这条钉回 §4 那张\"翻墙账单表\"，意味着账单从三笔（token、寻址精度、忠实性）扩到至少四笔，新加一笔 \"layer 数随输入 log-grow 的硬件代价\"。

**第三条：inference-time scaling 把 §6 第二道门做成了产品曲线**。Brown 2407.21787（Large Language Monkeys）+ Snell 2408.03314（compute-optimal test-time scaling）+ DeepSeek-R1 [arxiv:2501.12948](https://arxiv.org/abs/2501.12948) + Muennighoff s1 2501.19393 [unverified ID] 这条 2024-07 到 2025-01 的四篇 cluster，把 §6 \"无界 rollout + agent loop\" 这道门从理论可能性做成了 *frontier 生产环境的第二条 scaling 曲线*。topics/scaling_limits.md C-SCALE-4 给的形式陈述是 \"在 verifier-rich 子集上，inference compute 与 train compute 等价代换\"。这一条对本章判断的反向修正是：§6 三道门里第二道门（\"墙的存在条件是有限 rollout\"）已经在工程上被默认推开，过去两年 reasoning model 的实际进展速度证明 \"给足时间和反馈通道架构不会拦你\" 这条 Sutton 派直觉在 verifier 在场的窄域里是兑现了的。但同样要诚实写：Wu 2408.00724 inference-scaling-laws 显示在非 verifier 任务上 inference-scaling power-law exponent 降到 ~0，所以这道门**只在 verifier-rich 子集打开**，与 N8 §4 抽出的 Bitter Lesson 三条件（输入分布可合成 / verifier 存在 / 单步信号密集）正好对应——本章 §6 第二道门和 N8 那个三条件诊断工具是同一件事的不同侧面。

**判断**：把三条补遗合起来读，本章在 2026 年 5 月这个时点应该给出的修正版立场是：(a) §3–§5 的 expressivity 主线没有被推翻，但它对 frontier-scale 真实瓶颈的解释力下降了——内圈 learnability 墙先撞，C-FORM-4 才是 mech 派 2026–2028 真正应该工作的方向；(b) §6 三道门的代价函数都被向下修订过一次（Brösamle-Eckstein 给精度+depth、inference-scaling 给 rollout、tokenization 这条线在 2025 没有大新闻所以这一道暂时稳定），mech 派想守住\"架构级硬上界\"必须把假设三元组写得比 2023 年更精细；(c) Dziri 2023 那张曲线作为 \"经验/理论对齐\" 的 anchor 仍站，但 \"对齐\" 这个词需要降格到 \"数值对齐\"，机制对齐尚未被任何一份 mech-interp 工作做出。本章 §5 末段给的 \"如果 Allen-Zhu Physics-of-LM 在 2026 内把崩塌点和 attention head 内部寻址误差关联起来则三人会被串成不可拆的因果链\" 这一预言到 2026-05 *仍未兑现*——Physics-of-LM 后续 Part 3.x 在合成数据上复现了崩塌曲线，但**显式把崩塌点定位到具体 attention head 的工作没有公开** [unverified]，这件事本身就是 mech 派下一阶段的最大方法学债。

留给未来 Xander 一个 2027-12 回检锚：如果 C-FORM-4 到那时仍然没有形式 lower bound，而 reasoning model 在 8 位乘法、$k=10$ Einstein、$n=20$ LIS 上仍然崩，那本章的判断会从 \"墙在 expressivity\" 进一步退到 \"墙在 learnability\"，等价于承认整条 Hahn-Merrill 主线对 frontier scale 是 *正确但无关* 的——这是一种比被反驳更尴尬的结局，值得提前给读者打个预防针。

## 八、2026 年 5 月末尾再补一段：把 §六的三道暗门拼成一张 2×2 的小地图

写完 §七 三天之后又落了一组在 topics/formal_limits.md 和 survey §10 sub-candidate 区同步登记的工作 (C-FORM-8 / C-FORM-8b, 2026-05-29 至 30)，它们没有再加新门，而是把 §六那三道门里 *第一道 (Coconut / pause / latent CoT)* 与 *第二道 (Schuurmans 无界 rollout)* 共同的 *scratchpad 维度* 与 *backbone 维度* 正式拆成一张 2×2 小地图。**backbone 一维**取 softmax-attention 或 selective-SSM (Mamba / Mamba-2 / GLA, 形式由 Merrill *Illusion of State* [arxiv:2404.08819](https://arxiv.org/abs/2404.08819) 钉死同属 log-precision $\\mathsf{TC}^0$); **scratchpad 一维**取 *内化* (Giannou *Looped Transformers* [arxiv:2301.13196](https://arxiv.org/abs/2301.13196) 一支, 把 $T_{\\max}$ 步循环吃进 latent 不写回 token) 或 *外化* (Merrill–Sabharwal [arxiv:2310.07923](https://arxiv.org/abs/2310.07923) 一支, 把 $T_{\\text{CoT}}$ 步 token 写回 input)。四格全部命名: (attention, loop) = Giannou 2301.13196 / (attention, CoT) = Merrill–Sabharwal 2310.07923 / (SSM, loop) = C-FORM-8 / (SSM, CoT) = C-FORM-8b。

把这张表叠回 §六的三道暗门修订表上，可以读出两件 §六当时讲不出的事。**第一**，前三道门里第一道 (latent / pause) 与第二道 (无界 rollout) 实际上不是两条平行通道，而是 *scratchpad 这一维* 的内化与外化两端；frontier 工程现实里几乎所有 reasoning model (o3 / R2 / Claude 4.x Extended Thinking) 都默认走外化一端 — 内化一端在 latency 上是死的，1 GPU-week 内没人去做 controlled comparison ([`../survey/ntp_survey.md`](../survey/ntp_survey.md) §9 (4) 第 19 项现已拆为 19a/19b，19b 是 \"工程上可做、社会学上未做\" 的优先项)。**第二**，worst-case 上界沿 backbone 一维是 *trivial 继承* 的——Merrill–Sabharwal 论证骨架与 backbone 单步类无关，把 attention 换成 selective-SSM 不动 $\\mathsf{TIME}[T_{\\text{CoT}}\\cdot\\text{poly}]$ 结论；真正没被任何论文写下的不是 worst-case 上界，而是 *learnability 缝*——Mamba 单步在 $S_5$ 上长度泛化崩坏 (Merrill 2404.08819 实测) 是否能被 CoT 把 $S_5$ 拆成 $T_{\\text{CoT}}$ 个 sub-$S_5$ 救回来，1B Mamba + 1B Llama 各一档跑 length-100/200/500 即可判，但 SSM 派关心吞吐、formal 派关心 attention，无人接手 [unknown]。

把这张 2×2 钉回本章 §三的判决：Merrill–Sabharwal 三部曲在 worst-case 维度上已经把 *主干 × scratchpad* 四格的渐近行为全部锁死，参数只剩 $T_{\\max}$ 与 $T_{\\text{CoT}}$ 的阶。这把 §五末段 \"墙没倒，门都有代价\" 的判断进一步精确化为: 门的代价函数在 worst-case 维度上 *跨四格塌缩成同一条曲线*，门的 *learnability 差异* 才是 2026 年这个时点真正未测的缝——而这条缝刚好与 §七第一条 C-FORM-4 \"NTP-learnability gap\" 内圈墙是同一件事的两侧。诚实补一句: C-FORM-8b 在 sub-candidate 里 worst-case 强度最低 (两行论证)，登记它的价值不在预测新现象, 而在把 \"frontier 默认部署 CoT 却从不公开 backbone × scratchpad controlled comparison\" 这一社会学缺位钉成可命名条目 ([`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 C-FORM-8b sync 段) — 与 N8 §四 \"反墙四条件\" 第 (ii) 条 \"新架构在 capacity 维度上 strictly 超越 transformer\" 的可证伪窗口收窄是同一动作的对偶: 不是再加固墙, 而是把 *没被做的对照实验* 钉成时间常数。

