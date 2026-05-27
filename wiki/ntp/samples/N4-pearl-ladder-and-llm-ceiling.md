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

## 三、CLadder 与 Jin Zhijing：把争论拖到一张可比的表格上

2023 年下半年的局面是僵的。Kıcıman 这边说 GPT-4 已经是 causal assistant，Zečević 这边说它是 causal parrot，两派各拿各的 benchmark，没人能逼对方退一步。打破僵局的是一个相对年轻的名字：Jin Zhijing。她当时是 MPI Tübingen / ETH Zürich 的博士生，导师是 Bernhard Schölkopf（因果学界绕不开的人）和 Mrinmaya Sachan，研究方向恰好横跨 NLP 与因果推断。她在 2023 年和 2024 年连续放出两篇论文，目的非常明确：把 LLM 的因果能力**逼到一个 Pearl 三层楼对应物明确、可大规模生成、可严格 leak-check** 的 benchmark 上去测。

第一篇是 2023 年 6 月的 *Can Large Language Models Infer Causation from Correlation?*（[arxiv:2306.05836](https://arxiv.org/abs/2306.05836)），引入 CORR2CAUSE 数据集。任务表述非常 Pearl：给一段关于若干变量两两相关 / 条件独立关系的纯统计描述，问能否推出某条因果边的方向。这是一个**纯第一层输入 → 第二层结论**的形式化推理，对应 PC algorithm 的一个子任务。结果是 GPT-4 在 zero-shot 上准确率约 30%（与 majority baseline 接近），fine-tune 之后能上 60% 但对变量改名极其敏感——把 \"A, B, C\" 换成新符号，性能立刻退化。这一篇的判断很冷静：LLM 学到的是表面 pattern，不是 d-separation 这种结构推理。

真正把争论拖上桌的是 2023 年 12 月的 *CLadder: Assessing Causal Reasoning in Language Models*（[arxiv:2312.04350](https://arxiv.org/abs/2312.04350), NeurIPS 2023）。这篇的合作者列表本身就是一种宣示：Jin Zhijing + Yuen Chen + Felix Leeb + Luigi Gresele + Mrinmaya Sachan + Bernhard Schölkopf，半个团队是 Tübingen 因果组的人。CLadder 的设计直接照搬 Pearl 的三层楼：每道题先给一个小的 SCM（用自然语言描述变量、结构方程、外生分布），再问一个对应 Layer-1、Layer-2 或 Layer-3 的问题，标准答案由 do-calculus 在 SCM 上**机械计算**得出。题目数量大约 10K，结构是程序化生成的，因此可以做严格的 leak-check：所有变量名、所有场景叙述都是新合成的。

GPT-4 在 CLadder 上的结果是这一章最值得记住的一组数字：Layer-1（associational）准确率约 70%、Layer-2（interventional，即 $P(y|do(x))$）约 55%、Layer-3（counterfactual）约 40%——三层楼上是单调下降的曲线，而随机基线在二元题上是 50%。也就是说，**LLM 在 Pearl 第三层上的表现，统计意义上无法和瞎猜区分**。论文还做了一个对照实验叫 CausalCoT：把 do-calculus 的推理步骤显式写进 prompt 让模型跟着走，三层准确率分别能拉到 ~80% / ~65% / ~50%——Layer-3 仍然挣扎在随机线附近。

这组数字一出来，2023 年那场口水仗的几何形状就变了。Kıcıman 阵营的乐观证据基本都集中在 Layer-1 与 Layer-2 的特定子任务（pairwise discovery、actual causation 判断），Zečević 阵营的悲观证据基本都集中在改名鲁棒性与第三层。CLadder 给了一个不偏向任何一方的统一坐标系：**第一层接近饱和、第二层 prompt-engineering 可以推上去但天花板低、第三层目前没人攻得动。** 后续 2024 年 Jin 又有一篇 *Causal Evaluations of LLMs Across Layered Tasks*[unverified ID] 把同样的框架推到 Claude 3、Gemini 1.5、o1-preview 上，结论的形状不变：reasoning 模型（o1-preview）能把 Layer-2 再推上 5–10 个百分点，但 Layer-3 仍然贴着随机基线。

这里要给一个反例 / 反论，否则不诚实。CLadder 自己的局限在于：它的 SCM 是**程序化生成的小图**（变量数通常 ≤4，结构方程是线性或简单非线性），自然语言叙述也偏模板化。一个合理的反驳是：人类做反事实推理时也不是在解任意 SCM，而是依赖大量先验直觉，所以 LLM 在更**自然**的反事实题（医学病例、法律 but-for、日常生活假设）上可能比 CLadder 测出的要强。Gonzalez 等人 2024 年的若干跟进工作[unverified ID] 确实在 naturalistic counterfactual 上报告了高于 CLadder Layer-3 的数字，但都难以排除训练集污染。换句话说，**越自然的反事实题越难做 leak-check，越合成的反事实题越远离实际使用场景**——这是评估 Layer-3 时一个绕不开的两难。

我自己读完这条线的判断是：CLadder 不是终结性证据，但它是目前**唯一一个把 Pearl 三层楼变成可比数字、且严格控制 leak** 的公开 benchmark。如果你想反驳\"LLM 撞在第二层天花板\"这个论点，最低门槛是先在一个比 CLadder 更难、且 leak-check 同样严格的数据集上把 Layer-3 显著推过 50%。到 2026 年 5 月为止，我没有看到任何一篇公开论文跨过这道门槛。这件事本身比任何具体数字都重要——它说明，过去三年里**针对 Pearl 第三层的真正进步几乎为零**，所有看似进步的报告都可以被 leak / 表面 pattern 这两个原因之一解释掉。

## 四、Lampinen 的旁观者实验：第二层能不能"蹭"到？

CLadder 把 Pearl 第三层钉死之后，剩下一个更尖锐的问题：第二层呢？如果 LLM 自己不能做 do-operation，那它**观摩**别人做 do-operation 的语料够不够多，多到能在统计意义上继承一些第二层能力？这个问题听上去像在钻空子，其实是 Pearl 整套 do-calculus 里被讨论最少、却对 LLM 路线最关键的一个角落——因为人类小孩学因果的过程，绝大部分时间也是"看着大人做实验"，而不是亲自跑 RCT。

正面攻这个问题的是 Andrew Lampinen。他 2017 年 Stanford 心理学博士毕业，之后去 DeepMind 做 cognitive science of LLMs，长期关注一件事：人在哪些任务上做的"推理"是真推理、哪些只是 affordance pattern 的复用。2023 年 5 月他和 Stephanie Chan、Ishita Dasgupta、Andrew Saxe、Felix Hill 一起放出 *Passive Learning of Active Causal Strategies in Agents and Language Models* ([arxiv:2305.16183](https://arxiv.org/abs/2305.16183))，标题就把命题说得很清楚：被动学习能不能拿到主动因果策略？

实验框架是这样的：构造一个含混杂因子的小环境（典型设定是若干 light + switch 的因果图，外加一个 confounder 会同时影响 switch 选择与 light 状态），然后给 agent / LLM 看一段 **expert demonstration**——专家本人是会 intervention 的，比如会显式地"先固定 confounder 再切换 switch"。被动学习者本身**从不被允许动手**，只能读 demonstration trace。测试阶段问的是 Layer-2 问题："如果**你**现在把 switch X 设成 on，light Y 会亮吗？"

Lampinen 的结果有两半，必须一起读才不会被单独引用断章。第一半是**正面**的：当 demonstration 里**显式包含 intervention 标记**（比如自然语言里出现 "I will now set X to on regardless of what it was"），LLM（论文里测的是 Chinchilla 量级与 Flan-PaLM）能在被动训练后，在 held-out 因果图上把 Layer-2 准确率从随机基线推到 70–80%。换句话说，**只要语料里有"我在做 do-operation"这种元标记**，模型能学到一些把 observation 与 intervention 区分对待的策略。这是 Pearl 第二层墙第一次被一个 NTP-only 模型在 controlled setting 下从外侧蹭过去。

第二半是**反面**的，也是被引用得少得多的那一半：一旦把 demonstration 里的 intervention 元标记去掉，只留下"专家选了 X、然后看到 Y"这种纯 observational trace，被动学习者的 Layer-2 准确率立刻塌回随机。也就是说，模型继承的不是 do-operator 这个抽象**操作**，而是"intervention"这个**词**所标记的条件分布偏移。这条结论非常 Pearl——它正好对应 do-calculus rule 2（observation = intervention 的充分条件是 backdoor criterion 满足），LLM 学到的只是"看见 intervention 这个词，就切换到另一组 conditional"，而不是去检查 backdoor。

这一篇出来之后，2024 年 Richens & Everitt（DeepMind / Causal Incentives）在 *Robust Agents Learn Causal World Models* ([arxiv:2402.10877](https://arxiv.org/abs/2402.10877)) 把这条线推到一个相反方向的极限：他们证明任何在分布漂移下保持 regret 上界的 agent，**必须**在内部隐式表征一个近似的因果世界模型。换句话说，只要训练 setup 里有足够多样的"分布漂移"，被动学习的压力本身会逼出一个第二层近似——这给 Lampinen 的正面结果提供了一个理论锚点。但 Richens-Everitt 的定理要求 "robust to all distribution shifts"，frontier LLM 训练显然达不到这个条件；这道定理给的是**可能性**，不是**实然**。

把这一段拼起来，得到一个比 §3 更精细的判断：**Pearl 第二层不是一堵"绝对墙"，它是一堵"语料墙"。** 只要训练语料里**显式标记**了 intervention（医学 RCT 报告、A/B test writeup、"假设我们做以下手术"式的科普），被动 NTP 能继承到一部分第二层能力——CLadder Layer-2 准确率最高能推到 65–70%，与 Lampinen 实验一致。但**自动从纯观测数据里发现 do-operator 这个抽象**，目前没有证据。这个区分对 NTP 路线判断有直接后果：如果第二层主要靠"语料里有没有 intervention 标记"决定，那 agentic post-training（让模型自己产生带有 intervention 标记的轨迹）就是补这一层最便宜的办法，而**不必动 NTP loss 本身**。这条线就接到 §6 要讲的 o-series / R1-Zero / computer-use 轨迹回流。

反例与诚实判断：Lampinen 2023 的 environment 是程序化的（典型 4–6 节点因果图），跟 CLadder 一样有"合成—自然"的两难。被动学习从医学教科书里继承第二层的真实 effect size，到 2026 年 5 月仍然没有干净的数字，因为没人能对 frontier LLM 的训练集做严格 RCT-paper leak-check。我个人的判断：Lampinen 给的是一个**存在性证明**（被动 NTP 可以继承第二层），不是**充分性证明**（被动 NTP 足以达到任意第二层能力）。前者打破了 Pearl 强命题"第一层永远进不了第二层"，后者仍未被反驳。这是 §3 CLadder 数字与 §5、§6 要讨论的内部机制之间的关键桥梁。

<!-- TODO §5 Geiger interchange intervention：能否在 LLM 内部"找到"do-operator circuit -->
<!-- TODO §6 agentic post-training (o-series / R1-Zero / computer-use 轨迹回流) 是不是把第二层"补"进训练分布 -->
<!-- TODO §7 尾声：Pearl 的墙到底是架构墙还是数据墙；以及为什么这个区分对 NTP 路线判断至关重要 -->

---

*相关 topic：[causality](../topics/causality.md)（mech 候选 C-CAUSAL-1 的可证伪表述）、[world_model](../topics/world_model.md)（第三层 ≈ 在 world model 上做 rollback + 反事实 rollout）、[reasoning](../topics/reasoning.md)（CoT 对 Layer-2 有效、对 Layer-3 无效，是 faithful CoT 讨论里最尖锐的案例）。*
