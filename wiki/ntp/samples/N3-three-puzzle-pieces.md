# Reversal Curse / 不忠实 CoT / Faith-and-Fate——三块拼图

## 一、2023 年五月到九月，四个月里掉下三块碎片

2023 年 5 月 18 日，Allen AI 的 Nouha Dziri 在 arxiv 挂出 [*Faith and Fate: Limits of Transformers on Compositionality*](https://arxiv.org/abs/2305.18654)。同一个月的 5 月 7 日，Anthropic 的 Miles Turpin 等人挂出 [*Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting*](https://arxiv.org/abs/2305.04388)。四个月后，9 月 21 日，Vanderbilt 的 Lukas Berglund 联合牛津、苏黎世、纽约几所学校的合作者挂出 [*The Reversal Curse: LLMs Trained on "A is B" Fail to Learn "B is A"*](https://arxiv.org/abs/2309.12288)。

这三篇论文当时是分别被讨论的。Faith-and-Fate 被放进 "scaling 是否够用" 的辩论，Turpin 那篇被放进 "alignment / interpretability" 的赛道，Reversal Curse 因为标题耸动一度被当成 Twitter 段子。三个圈子各看各的——reasoning 圈、safety 圈、knowledge-editing 圈——没人去问一个最朴素的问题：**这三件事有没有可能是同一件事的三个侧影**？

到了 2025 年下半年，这个问题才被反复地提出来。提出方式各不相同：Sanjeev Arora 在 [arxiv:2402.05120](https://arxiv.org/abs/2402.05120) 的 *Physics of Language Models* 系列里用合成数据复现了三者；Anthropic interpretability team 2024 年 5 月发的 [*Scaling Monosemanticity*](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) 在 Claude 3 Sonnet 里找到了一类 feature——它们在 A→B 方向激活而在 B→A 方向不激活；Dziri 自己在 2024 年的 follow-up 里把 compositionality wall 重新归因为 "linear chain memorization"。这些工作合起来给出了一个**共同的几何图像**：next-token prediction 在训练时只看到一个方向的 token 流，所以学到的表征也是**有向**的，且**沿生成链的局部组合**——这两条性质合起来同时蕴含 (a) 反向蕴含学不到、(b) 多跳组合在某个深度后塌掉、(c) 模型给出的推理链可以和真实计算路径完全脱钩。

本章要论证的，就是这三块碎片其实拼成一张图。NTP 的 loss 是一个**逐 token、向前、局部**的目标，这三条性质各自切掉一块解空间，留下的就是当前大模型 reasoning 行为的轮廓。

## 二、为什么三篇论文当时被分开讨论——一段简短的社会学

这里要先说一段令我自己也不太舒服的社会学。这三篇之所以四个月里没人合起来看，原因其实和论文本身关系不大，和**研究圈的分工**关系更大。

Dziri 的 *Faith and Fate* 在 2023 年 NeurIPS 投稿池里是和 *Sparks of AGI* [arxiv:2303.12712]、*Skill-Mix* [arxiv:2310.17567]、*Are Emergent Abilities a Mirage* [arxiv:2304.15004] 并列被讨论的，框架是 "scaling 是否能解决 reasoning"。它的反例（三位数乘法、Einstein puzzle、动态规划）被读作 "目前的 capacity 还不够"，而不是 "目标函数本身有问题"。

Turpin 的 *Unfaithful CoT* 当时挂在 Anthropic 的 alignment workstream 下，配套的姐妹篇是 Lanham 等人的 [*Measuring Faithfulness in Chain-of-Thought Reasoning*](https://arxiv.org/abs/2307.13702)（2023 年 7 月）。这条线关心的是 "模型给出的解释能不能信"，下游应用是 RLHF reward model、debate、constitutional AI。它的核心证据是：在 Turpin 设计的 biased few-shot prompt 下，模型会**输出一条看似严密的推理链导向被偏置植入的错误答案，且推理链里不提偏置存在**。这个发现被 alignment 圈消化掉了——成了 "CoT 不可解释" 的标准 caveat——但很少有人把它和 *Faith and Fate* 放在一起。

Reversal Curse 是最孤立的一篇。Berglund 论文里训练集是合成的 fictional facts（"Daphne Barrington 是 Crystal Mind 的导演"），实验做得很干净：fine-tune 后正向问答 100%，反向问答 0%。Owain Evans 在 Twitter 上一发，圈外人当段子转，圈内人当 "知识编辑/MEMIT 失败案例" 看。这条线后续接到的是 Meng 的 [ROME](https://arxiv.org/abs/2202.05262) / [MEMIT](https://arxiv.org/abs/2210.07229) 一系，重点是 "怎么在权重里改一个事实"。没人去问 "为什么反向不行" 这个**目标函数**层面的问题，因为这个问题不能立刻变成一个 benchmark 数字。

三个圈子用三套词汇，于是同一个根因被切成三个独立现象。这是 ML 圈在 2023–2024 年的常态：reasoning / alignment / knowledge-editing 各自有 PI、各自有 workshop、各自有引用网络。要把这三块碎片拼起来，需要的不是新实验，是**承认它们共享同一个 loss 的几何**——而这一步直到 Allen-Zhu 的 *Physics of LM* 第 3.1–3.2 部分（[arxiv:2309.14402](https://arxiv.org/abs/2309.14402)、[arxiv:2404.05405](https://arxiv.org/abs/2404.05405)）才被半显式地说出来。

我个人的判断是：这一段历史本身就是 NTP 研究的一个元教训。**当一个根本性的目标函数限制以多种表现形式渗透到不同子领域时，子领域之间的引用结构会阻止它们看到根因。** 这不是某个人的错，是当代 ML 论文工业的结构性近视。后面三节会逐一拆开这三块碎片，第六节我会尝试把它们重新拼起来。

> §3 Faith-and-Fate：组合深度墙 / §4 Turpin & Lanham：CoT 的"事后合理化"通道 / §5 Reversal Curse：训练分布的方向性 / §6 三合一：NTP loss 几何的统一解释（TODO，待续写）
