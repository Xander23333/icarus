# Pearl 的因果阶梯与 LLM 的天花板

> NTP 候选样章 N4。作者 Xander Xu。本篇试图回答一个反复被搬到饭桌上、又反复没有结论的问题：一个只见过 token 共现、从未对世界做过 do-operation 的模型，能不能登上 Pearl 三层因果阶梯的第二、第三层？

## 一、2018 年那本小书：Pearl 为什么要画三层楼

故事得从 2018 年说起。那一年 Judea Pearl 八十二岁，已经拿了图灵奖（2011 年，因贝叶斯网络），按学术界的惯例，他可以从此安静地坐在 UCLA 的办公室里被引用。但他没有。2018 年 5 月 *The Book of Why* 出版，半本写历史（Galton、Wright、Neyman、Rubin），半本写一件他想做但还没做完的事：把"因果"从一个含糊的哲学词，逼成一个有三层楼的、可计算的层级结构。同年，他把这一立场压成一篇技术文章 *Theoretical Impediments to Machine Learning with Seven Sparks from the Causal Revolution* ([arxiv:1801.04016](https://arxiv.org/abs/1801.04016))，正面挑战当时如日中天的深度学习社区——副标题里那个 "impediments"（阻碍）是写给 Yann LeCun、Geoffrey Hinton、Yoshua Bengio 看的。

Pearl 三层楼，用最不哲学的方式讲是这样：

1. **Association** — $P(y \mid x)$。"看见 x 之后 y 出现的概率"。Galton 的回归、Pearson 的相关、几乎所有 supervised learning、几乎所有 NTP loss，都住在这一层。
2. **Intervention** — $P(y \mid do(x))$。"如果**我**把 x 强行设成某个值（不是观测到它，是动手设置），y 的分布是什么"。RCT、A/B test、强化学习里的 on-policy 探索、do-calculus，住在第二层。
3. **Counterfactual** — $P(y_x \mid x', y')$。"已知现实里 x=x'、y=y'，那么**假如**当初 x 是别的值，y 会怎样"。法律里的"若非因果"（but-for causation）、医学里的"个体处理效应"、人类道德推理里的"如果我没那样做"，都住在第三层。

Pearl 的核心断言用一句话就能讲完：**只观测、不干预的系统，无论参数多大、数据多多，理论上都被锁在第一层。** 要登第二层，需要 intervention；要登第三层，还需要 structural equation model。这不是一个工程瓶颈，是一个**数学事实**——同样的观测分布 $P(X,Y,Z,\dots)$ 可以对应到无穷多个不同的 SCM，它们对 do-operation 给出**完全不同**的答案。这种"观测等价"（observational equivalence）就是第一层与第二层之间那堵透明的墙。

把这个论断扔到 2018 年的会场是有点尴尬的。那一年正好是 BERT 出来的半年前，所有人都在追 ELMo 和 ULMFiT，没人想听 "你们的范式有上限"。Pearl 在那本书的访谈里说过一句话，大意是：深度学习是非常出色的曲线拟合，而曲线拟合永远进不了第二层楼。他被采访时口气不算客气。LeCun 回应过几次，态度大致是"我们不打算用 Pearl 的 do-calculus，但我们会用别的办法解决因果"——具体是哪个别的办法，七年之后的今天还没看到。

到 2022 年底 ChatGPT 出来之后，Pearl 的这堵墙突然变成了一个**经验问题**：一个吃了几乎整个互联网文本的 transformer，能不能因为见过足够多的因果叙述（医学教科书、流行病学论文、法律判例、物理推导、孩子问"为什么"的家长回答），自动学会一些 do-calculus？

这就是这一章要回答的问题。

## 二、两种立场：因果鹦鹉，还是事实上的 Pearl 第二层求解器

2023 年的整个春夏，关于 LLM 和因果的争论被两篇论文劈成了两半。

第一篇是 2023 年 5 月 Emre Kıcıman、Robert Ness、Amit Sharma、Chenhao Tan 的 *Causal Reasoning and Large Language Models: Opening a New Frontier for Causality* ([arxiv:2305.00050](https://arxiv.org/abs/2305.00050))。四个人来自微软研究院和芝加哥大学，他们在三类公开 benchmark 上跑 GPT-4：pairwise causal discovery（给一对变量判断因果方向，用 Tübingen pairs 等数据集）、counterfactual reasoning、actual causality（"是 A 还是 B 真正导致了 C"）。结果是 GPT-4 在所有三类任务上都显著超过 prior SOTA，其中 pairwise discovery 的准确率从专门符号方法的 ~70% 推到 ~95%。论文的结论写得很大胆：LLM 已经是"实用级 causal assistant"，因果学界应该把它当作工具接受下来。

第二篇是 2023 年 8 月 Matej Zečević、Moritz Willig、Devendra Singh Dhami、Kristian Kersting 的 *Causal Parrots: Large Language Models May Talk Causality But Are Not Causal* ([arxiv:2308.13067](https://arxiv.org/abs/2308.13067))。Kersting 是 TU Darmstadt 的教授，长期做概率图模型与神经符号。他们给 LLM 的行为起了一个会被传开的名字：**causal parrots**。论文的核心论证是引入 *meta-SCM* 这个概念——LLM 在被 prompt 触发因果叙述时，本质上是在它训练语料的因果事实分布里做检索和插值，而不是在执行 do-calculus。证据是一组**变量改名实验**：把 Tübingen pairs 里的 "altitude → temperature" 改写成 "X7Q → K3M"，并附上同构的 textual context，GPT-4 的准确率立刻塌掉。

这两篇论文测的是同一个模型、用的是相关的任务集，结论却几乎相反。整个 2023 年下半年关于 "LLM + causality" 的讨论，本质上是这两派各自挑实验细节互相攻击。Kıcıman 这边说 Zečević 的对抗实例不够 ecologically valid，真实用户不会用 UUID 当变量名；Zečević 这边说 Kıcıman 的 benchmark 大概率已经在 GPT-4 的训练集里（Tübingen pairs 至少从 2014 年起就是公开数据），所以测的是记忆不是推理。

这场争论真正的不舒服之处在于：**它几乎无法证伪**。只要 frontier LLM 训练语料是闭源的、且包含几乎整个英文学术互联网，任何一个公开 benchmark 都可能在分布内。要做真正干净的 holdout 测试，你得构造一个全新的 SCM family、变量名用训练前不存在的 token、并严格 leak-check——而几乎没人有能力对一个万亿 token 量级的训练集做严格 leak-check。

这是 §3、§4 要展开的两条线。先把这一节的判断说在前面：到 2026 年 5 月为止，我倾向于认为 Kıcıman / Zečević 的争论**在 Layer 1 已经收敛**（LLM 在因果叙述检索上接近饱和，没人否认），**在 Layer 2 仍未收敛**（取决于测试集是否在训练 manifold 内，这是个数据问题不是架构问题），**在 Layer 3 收敛到悲观侧**（CLadder Layer-3 上所有 frontier model 接近随机，目前没有公开的反例）。这个三段判断本身就是这一章的骨架。

<!-- TODO §3 CLadder 与 Jin 系列：把争论拖到一个量化 benchmark 上 -->
<!-- TODO §4 Lampinen 2305.16183：被动观测一个会 intervention 的 demonstrator，能继承多少第二层能力 -->
<!-- TODO §5 Geiger interchange intervention：能否在 LLM 内部"找到"do-operator circuit -->
<!-- TODO §6 agentic post-training (o-series / R1-Zero / computer-use 轨迹回流) 是不是把第二层"补"进训练分布 -->
<!-- TODO §7 尾声：Pearl 的墙到底是架构墙还是数据墙；以及为什么这个区分对 NTP 路线判断至关重要 -->

---

*相关 topic：[causality](../topics/causality.md)（mech 候选 C-CAUSAL-1 的可证伪表述）、[world_model](../topics/world_model.md)（第三层 ≈ 在 world model 上做 rollback + 反事实 rollout）、[reasoning](../topics/reasoning.md)（CoT 对 Layer-2 有效、对 Layer-3 无效，是 faithful CoT 讨论里最尖锐的案例）。*
