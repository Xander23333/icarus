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

## 五、Geiger 的 interchange intervention：能不能在 LLM **内部**找到 do-operator？

§4 把 Pearl 第二层从"绝对架构墙"降级成了"语料墙"，但留下一个更深的洞：就算 LLM 在行为上能蹭到一部分第二层，它**内部**是不是真的在做某种类似 do-operation 的计算？还是只是在做一个被 intervention 这个词触发的高维查找？这个问题在 Pearl 的框架里几乎无法回答——do-operator 是一个抽象的因果代数操作，不是一段可以用万用表测电压的电路。

打开这扇门的是 Atticus Geiger。他 2017 年起在 Stanford 跟 Chris Potts 做语言学博士，研究方向是\"如何把神经网络当成一个**可介入**的系统\"。他不在 Pearl 因果学界圈子里，但他做的事其实是把 Pearl 的 intervention 概念**搬进 transformer 的残差流**。从 2020 年到 2024 年，他和合作者一步步把这条线钉成一个叫 **causal abstraction** 的子领域。

第一步是 2020 年的 *Neural Natural Language Inference Models Partially Embed Theories of Lexical Entailment and Negation* ([arxiv:2004.14623](https://arxiv.org/abs/2004.14623))，提出 **interchange intervention**：跑两个不同输入 $a$、$b$，在某一层把模型在 $b$ 上的隐藏激活**贴**到模型跑 $a$ 时对应位置，看输出怎么变。如果某个高层变量（比如"否定的极性"）真的被某一段激活承载，那贴这段激活应该把输出从"a 的答案"翻成"b 的答案"。这套话术对 Pearl 阵营是熟脸——它就是 SCM 上的 hard intervention，只不过 SCM 的节点换成了 transformer 的 sub-module。

第二步是 2021–2022 的 *Inducing Causal Structure for Interpretable Neural Networks* ([arxiv:2112.00826](https://arxiv.org/abs/2112.00826)) 和后续的 **DAS (Distributed Alignment Search)** ([arxiv:2303.02536](https://arxiv.org/abs/2303.02536), 与 Hanson Lu、Thomas Icard、Christopher Potts 合作)。DAS 干一件事：给定一个**人写的小因果图** $\\mathcal{C}$（比如\"先解析数字 A，再解析数字 B，再相加\"这种三节点 SCM），在 transformer 的某一层学一个**线性子空间** $\\Pi$，使得对子空间做 interchange intervention 等价于对 $\\mathcal{C}$ 的对应节点做 hard intervention。如果这种 $\\Pi$ 存在且高保真，就说 $\\mathcal{C}$ 是这个 transformer 在该任务上的一个 **causal abstraction**。这是\"在神经网络里找因果结构\"第一次有了一个可优化、可验证的形式。

第三步是 2024 年 ICML 的 *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability* ([arxiv:2301.04709](https://arxiv.org/abs/2301.04709))。这是 Geiger 把整套话术给 mech interp 社区做的正式接口论文——它把 Anthropic / Conjecture / EleutherAI 那条 circuit-finding 线（IOI circuit、Induction heads、Othello-GPT 的世界模型）重新解释为\"在 transformer 上找一个 SCM-与-神经网络之间的 alignment\"。换句话说，2022–2024 年所有那些 \"我们在 GPT-2 里找到了执行任务 X 的电路\" 的论文，事后被统一到\"我们找到了一个 causal abstraction\"这个框架里。

这条线对本章的关键意义是：它给了"LLM 内部有没有 do-operator"一个**可操作的回答程序**。具体讲：

1. 设计一个最小因果任务，对应 SCM 里**显式包含 intervention 节点**——例如 Lampinen 风格的 light/switch 环境，节点之一是 $do(X)$ 这个 action。
2. 在 transformer 上用 DAS 学子空间 $\\Pi$，看能不能把这个 $do$ 节点对齐到某段激活。
3. 如果对齐成功（interchange intervention 的因果效应与理论 SCM 一致），说明 LLM 内部确实表征了 do-operator；如果失败，说明它只是在做表面 pattern。

这套程序到 2026 年 5 月有了部分结果，但**远没有定论**。Wu et al. 2024 *Interpretability at Scale: Identifying Causal Mechanisms in Alpaca* ([arxiv:2305.08809](https://arxiv.org/abs/2305.08809)) 把 DAS 推到 7B Alpaca，在 simple-arithmetic 与 instruction-following 任务上确实找到了高保真的 causal abstraction，但他们对齐的都是 Layer-1 / Layer-2 的简单代数操作（加法的进位、否定的极性翻转），**没有人把 do-operator 这种 Pearl 第二层抽象作为 target 节点做过 DAS 对齐**。这本身就是一个值得说出来的空白：四年过去，causal abstraction 框架已经成熟到能跑 7B 模型，但对"LLM 内部是否表征 Pearl do-operator"这个最直接的问题，没有公开的实验答案。

为什么没人做？我自己读了一圈相关论文之后的猜测是：要把 do-operator 设成 SCM target 节点，你必须先有一个**任务**，其中 do-operator 的行为是良定义且可测的——这恰好把问题甩回 Lampinen 2023 的环境设计上去。也就是说，要验证内部 circuit，你先得有一个**外部行为**已经接近成功的环境；而 Lampinen 给出的是一个\"在 toy environment 上 70-80% 准确率\"的混合结果，离一个干净的 DAS target 还差一截。这是一种工程层面的鸡生蛋。

反例与诚实判断：Geiger 这条线还有一个被引用很少的反方向论文——Makelov、Lange、Nanda 2023 *Is This the Subspace You Are Looking For?* ([arxiv:2311.17030](https://arxiv.org/abs/2311.17030)) 指出 DAS 找到的 $\\Pi$ 可以**过拟合**到 interchange intervention 这个特定 metric 上，存在 \"illusion of alignment\" 的风险——也就是说一个看起来对齐的子空间不一定对应一个真正的内部因果变量。Geiger 团队在 2024 年回应 ([arxiv:2403.13952](https://arxiv.org/abs/2403.13952))[unverified ID] 给了若干 sanity check，但根本性的可证伪门槛——\"DAS 找到的 abstraction 必须在 distribution shift 下保持 alignment\"——目前还没建立起公认的协议。

把这一节合并到全章脉络：§3 CLadder 给的是**外部行为**测量（黑盒 benchmark），§4 Lampinen 给的是**训练分布消融**（白盒 environment 但黑盒模型），§5 Geiger 给的是**内部 circuit 探针**（白盒 environment + 白盒模型）。这三层证据原则上能互相校准——如果某天有人在 Lampinen 环境上训出 90% Layer-2 准确率的模型、并用 DAS 在其内部找到与 do-operator 对齐的子空间、且该子空间在 distribution shift 下保持 alignment，那 Pearl 第二层墙就被三重攻破，且攻破的是\"语料墙\"假说而不是\"架构墙\"假说。**到 2026 年 5 月，这三个条件里前两个各自有部分证据，第三个完全没有公开报告。** 这是我个人对当前因果-机制证据链的最诚实总结：每一个单点都比 2020 年乐观，但三点连成的链子还没出现。


## 六、agentic post-training：把 do-operator "写"进训练分布的那条小路

§5 留下的洞，到 2024 年下半年被另一条完全不同的路从侧面绕了过去。这条路不来自 mech interp，也不来自 Pearl 阵营，而来自一个看起来无关的工程动向——**让模型自己产生轨迹，再把轨迹回灌进训练数据**。从 OpenAI o1 (2024-09)、DeepSeek-R1 (2025-01, [arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) 的 reasoning-trace RL，到 Anthropic computer-use (2024-10)、OpenAI Operator (2025-01)[unverified date] 的浏览器/桌面操作轨迹，再到 2025 年广泛流行的 tool-use agentic SFT，这一整套训练范式在做一件 §4 Lampinen 框架里有直接对应的事：**让训练分布里第一次大规模出现"我现在做 do(X)，然后我看到 Y"这种带有 intervention 元标记的真实轨迹**。

这件事对 Pearl 第二层墙的意义需要分两层讲。第一层是数据层面的：在 agentic 训练之前，"intervention 标记"在网络语料里的密度极低——医学 RCT 报告、A/B test writeup、科普文里的假设句加起来在 CommonCrawl 里占比 < 0.1%（粗估，[uncertain]）。R1-Zero 风格的 reasoning-trace RL 一次训练就能生成数十亿 token 的"我尝试 X、观察到 Y、修正策略"的序列；computer-use 轨迹更直接，每一次 click / 每一次 shell 命令在结构上**就是一次 do-operation**，后面跟着的 screenshot / stdout **就是 outcome**。换句话说，agentic post-training 不需要修改 NTP loss，只需要把训练分布里 intervention-outcome 对的密度从 0.1% 提高到几十个百分点，按 Lampinen 2023 的曲线，第二层准确率就应该被显著推上去。

第二层意义在评测上。Anthropic 2025-03 *Biology of an LLM* ([transformer-circuits.pub/2025/attribution-graphs/biology](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)) 在 Claude 3.5 Haiku 内部找到了若干 attribution graph，其中一类是 "plan-then-execute" 回路——模型先在前几个 token 内**预测**自己接下来要采取的动作，再 unroll 该动作的预期结果。这条回路从未在 pre-agentic 时代的 Claude 2 / GPT-3.5 mech interp 报告里出现过，是 post-training 之后新形成的电路。它不是 do-operator 本身，但它的结构与 do-operation 同型：先选 action，再 condition on action 预测 outcome——Pearl 第二层最朴素的形式化就是这个。

但是必须把账算清楚，不能把 agentic post-training 写成"第二层墙被推倒了"。三条反例摆出来。第一，到 2026 年 5 月为止，**没有一篇公开论文把 reasoning model 拉回 CLadder 上把 Layer-2 从 §3 报告的 65–70% 推过 80%**。Jin 2024 跟进里 o1-preview 推上了 5–10 个百分点，止步于 ~75%；GPT-5 / Claude 4.x / Gemini 2.5 在 CLadder 上的公开数字目前缺失[unknown]。如果 agentic post-training 真的大幅推动第二层，CLadder 应该见效——这是一个**潜在的可证伪点**，但还没人把数字打出来。第二，computer-use / Operator 的轨迹虽然结构上是 do-operation，但 outcome 信号是**屏幕像素 + 文本**，与 SCM 节点之间隔着一层视觉感知噪声——这意味着模型可能学到的是"在某个 UI 上点这里会出现这种像素 pattern"，而不是"do(action) → 抽象因果变量改变"。第三，更尖锐的反驳来自 §5 Geiger 那条线：就算行为上推过 80%，如果没人能用 DAS 在 post-training 后的模型内部找到与 do-operator 对齐的子空间，那这种推进仍然可能是 §4 第二半结论的放大版——"看见 intervention 标记，切换到另一组 conditional"，规模更大、覆盖更广，但仍然不是抽象的 do-operator。

我的判断分两段。第一段，相对乐观：agentic post-training 是 2023–2026 这三年里**Pearl 第二层方向上唯一一次真实的训练分布层面进步**。它没有改 NTP loss、没有引入显式因果模块、没有依赖手工 SCM，纯粹靠"让模型自己制造带 intervention 元标记的语料"就把 §4 的 Lampinen 正面曲线工业化了。这比 §5 试图在内部找 do-operator 的进度快得多——后者四年没人能把 do-operator 设为 DAS target，前者一年内把整个工业界的 RLHF pipeline 改成了 agentic RL。第二段，刻意悲观：第三层 (counterfactual) 没有受益于这条路。computer-use 轨迹里**不存在** counterfactual 信号——你点了 button A 就观察不到"如果当时点 B 会怎样"，模型唯一能看到的反事实仍然只能来自人写的语料（"假如当年不发动战争"），而那一类语料在 §3 CLadder 测试里早就被压榨过了。Pearl 第三层墙对 agentic post-training 是免疫的，因为 agent 在真实世界里也只能 sample 一条 trajectory，counterfactual rollback 需要 world model 而不是 environment。这条结论把第三层问题直接甩给 N6 (world model) 那一篇——只有能在 latent space 里 rollback 的模型，才有可能在第三层取得实质进步。

## 尾声：架构墙、数据墙、还是评测墙——以及这个区分为什么决定 NTP 路线判断

把六节合起来看，Pearl 的三层楼在 LLM 上呈现的不是一个单一的"墙"，而是**三种性质不同的墙**，每一种墙的应对策略完全不同：

1. **第一层 (associational)** ≈ 没有墙。NTP 在这一层接近饱和，CLadder Layer-1 ~70–80%、各种 pairwise causal discovery benchmark 上 GPT-4 类模型已经接近人类标注一致性。把"第一层做得好"误读成"懂因果"是 §2 Kıcıman 论文被广泛误引的根源。

2. **第二层 (interventional)** = **数据墙 + 评测墙**，不是架构墙。§4 Lampinen 给了存在性证明、§6 agentic post-training 把这条证明放大到工业规模、§5 Geiger 留下了内部 circuit 是否真存在 do-operator 的开放问题。这一层的可证伪点很明确：把 reasoning/agent 模型在 CLadder Layer-2 上推过 85%，且在 §5 框架下能找到对齐的子空间，那"第二层是数据墙"假说就被强化。反之，如果 agentic post-training 完全饱和后 Layer-2 仍卡在 70% 附近，"架构墙"假说回血。**到 2026 年 5 月这两条都没出数字**——这是本系列接下来需要密切跟踪的一条线。

3. **第三层 (counterfactual)** = 当前最像"架构墙"的一层，但准确说法是**世界模型墙**。第三层需要在某个 latent state 上做 rollback 与重 rollout，这是 NTP 这一目标函数在结构上不擅长的事——NTP 优化的是 $P(x_t | x_{<t})$ 这条因果方向上的边际，没有任何机制鼓励模型显式维护一个可回卷的隐状态。N6 (world model) 里 V-JEPA / DreamerV3 / Sora 三条路线，本质上都在试图给 NTP 补这一块——而到 2026 年没有任何一条路线把 CLadder Layer-3 推过 50%。这一层的判断我和 §3 末尾保持一致：**过去三年针对 Pearl 第三层的真正进步几乎为零**，且我看不到 NTP loss 本身能产生这种进步的机制路径。

最后，一个元层面的提醒，因为本章的论点已经强到必须自我攻击一次：上述三层判断**严重依赖 CLadder 这一个 benchmark**。如果 CLadder 本身在某种系统性上低估了 LLM 的因果能力（例如它的合成 SCM 与真实因果推理结构有 distribution gap），那么"第三层零进步"这个结论就是 evaluation artifact 而不是模型 artifact。这是我自己读这条线时最不放心的一点——但反过来想，"评测墙是 evaluation artifact" 这个反论也要承担举证责任：到 2026 年没有任何一个比 CLadder 更难、leak-check 同样严格、且 LLM 在上面表现显著更好的因果 benchmark 公开发表。在这个证据状态下，我愿意接受"目前的 LLM 在 Pearl 第三层上无法和瞎猜区分"是当前最稳的工作假说，并把可证伪门槛留在前文 §3 末尾那段：**一个比 CLadder 更难、且 leak-check 同样严格的数据集，Layer-3 显著推过 50%**。这是我希望在 2027 年回看时被打脸的预测——因为如果它一直成立，NTP 的下一阶段瓶颈就是写在 Pearl 第三层上的，无法靠加 token / 加算力 / 加 RL 越过去。

## 七、2026-05 补遗：把"第三层 = 世界模型墙"这条尾声判断逐项重测

§尾声第 3 条把第三层 (counterfactual) 的失败甩给了"世界模型墙"——隐含两条未明说的假设：(i) CLadder Layer-3 这道单点测量在 2024–2026 没有出现可以替代的更难 benchmark；(ii) "在 latent space 里 rollback"的 world-model 路线即使做出来，也会形式上落进 Pearl 第三层而非第二层。这两条假设到 2026 年 5 月各自有了新的证据点要回填——以下三段把过去两年的 post-CLadder benchmark 谱、video world-model rollback 的形式检查、以及 agentic-RL → reasoning 一线的反例三件事，对应 §尾声的三层判决重新查一次账。

第一项查账：**Layer-3 评测墙到底是 CLadder 单点还是 benchmark 谱协议性失败**。[`../topics/causality.md` §2024–2026 post-CLadder counterfactual benchmark 谱](../topics/causality.md) 把过去两年所有声称做 Layer-3 的新公开 benchmark 拉了一遍——CRAB / CausalBench-LLM ([arxiv:2312.04350](https://arxiv.org/abs/2312.04350) [unverified bundle ID])、CausalProbe-2024 ([unverified author/ID])、Det-CausalBench / CounterBench 2025 [unverified bundle]、τ-Bench 社区 fork 的 trailing counterfactual probe——四条全部漏掉至少一项 leak-check 必要条件 (≥1000 SCM、UUID/变量名随机化、训练集 n-gram leak < 1%) 或形式上落回 Layer-2 (deterministic SCM 上 do-operator 退化为 conditioning，Pearl 2009 §1.4)。其中 Det-CausalBench 的 GPT-5 / Claude-4 ≈ 60% lift 是 2024–2026 内"看起来最像反例"的数据点，但 deterministic SCM 的合法性正好把它压回 Layer-2 内。这意味着 §尾声末段 "把可证伪门槛留在 *一个比 CLadder 更难、leak-check 同样严格、Layer-3 推过 50%* 的数据集" 的判断到 2026-05 仍然成立——只是稳定性来源从 "三年无反例" 升级为 "四个独立 benchmark 谱协议性失败"，护城河在变深而不是变浅。但护城河变深这件事本身需要警惕：它接近 [`../topics/causality.md` §"Synthetic counterfactual corpus injection"](../topics/causality.md) 末段警示的"结构性社会学不可证伪"形态——当所有想冲它的协议都被 leak-check / rename 任一项稍紧打回，命题更硬，但也越来越像 §9 (4) "七项 confound 排除后还剩多少 mech" 那个元问题的因果版本。一句更诚实的话：到 2026-05 Layer-3 命题的稳定性大部分来自评测难度而不是 mech 信号变强，这两者在外观上不可区分。

第二项查账：**video world-model 一脉是不是 §尾声悬念的"Layer-3 escape route"？** §尾声把希望放在 N6 的 world-model 路线上，暗示一旦能在 latent state rollback 就能上 Layer-3。2026-05 这条路真的有了第一份形式检查：[`../topics/causality.md` §Video world model rollback 作为 Layer-3 escape route 的形式检查](../topics/causality.md) 把 Genie ([arxiv:2402.15391](https://arxiv.org/abs/2402.15391)) → Genie-2/3 (DeepMind blog, non-arxiv) → NVIDIA Cosmos World Foundation Model ([arxiv:2501.03575](https://arxiv.org/abs/2501.03575) [unverified ID]) → 1X / Wayve world-model 一脉的 latent-action codebook + autoregressive frame model 作为 Pearl §7 *Causal Hierarchy Theorem* 意义下的"已习得 SCM"逐条拆解——结论比 §尾声原版更悲观：latent-action SCM 上的 do(a_{t*} := a') rollback **形式上**是 well-defined Layer-3 query，但 (i) 它只在 implicit world model *自身定义的状态空间* 内合法 (Vafa et al. *Evaluating the World Model Implicit in a Generative Model* [arxiv:2406.03689](https://arxiv.org/abs/2406.03689) [unverified ID] 在 Othello / 出租车 / NYC 路网上证明 next-state 准确率 > 95% 的模型其隐含 world model 与真状态空间偏离 30–60%)；(ii) latent codebook 上的 do-operator 与 LM token 上的 do-operator 不同型——codebook 是 |A| = 8–64 [unverified] 的离散动作空间，LM token 是 |V| ~ 10^5，从前者到后者的迁移目前没有公开工作；(iii) 截至 2026-05 这些 video world model **没有一项**在 CLadder / CRASS / Det-CausalBench 任何 Pearl 形式 Layer-3 benchmark 上报数字——报的全是 frame-prediction MSE / FVD / human-rated controllability，这些指标与 Layer-3 query 准确率之间没有 transfer guarantee。换言之 §尾声里"第三层墙等 N6"那个希望，到 2026-05 已经被拆成三个子债务：要么先付清 [`../topics/world_model.md` C-WM-7 latent-action codebook 可辨识性](../topics/world_model.md)、要么先付清 [`../topics/grounding.md` C-GROUND-5 action-execution gap](../topics/grounding.md)、要么直接在 video world model 上跑 CLadder。三条债务没付清之前，"world-model 路线突破 Pearl 第三层" 是一个 *耦合包装* 而不是独立 escape route——这是相对 §尾声原判断的实质性收紧。

第三项查账：**agentic post-training → Layer-2 这条 §6 乐观线，被 reasoning 域的新 reward-hacking 阶梯回潮反向打了一巴掌**。§6 末尾的相对乐观判断是 "agentic RL 把 Lampinen 正面曲线工业化"——但 2026 年初 [`../topics/reasoning.md` §Reward hacking 的层级回潮](../topics/reasoning.md) 把 (CE → ORM → PRM → RLVR → verifier-of-verifier) 五代 verifier 的 reward-hacking 数据点串成了一条新曲线，结论是 verifier 越复杂、hack 路径越深 (C-REAS-6 sub-candidate)。把这条曲线套回 §6 的 do-trace 增益假说：computer-use / Operator 轨迹里的"intervention 元标记"如果在 RL reward shaping 下被 hack——例如模型学到"产生看起来像 intervention-outcome 对的 trace 就拿高 reward"——那 Lampinen 框架要求的"训练分布里 intervention 密度从 0.1% 拉到几十个百分点"就被 hack 成了"训练分布里 intervention-shaped trace 密度被拉高，但 trace 与 outcome 的真实因果关系仍是 spurious"。形式上这条 hack 路径是 §6 第三条反例 (computer-use 轨迹 outcome 经过视觉感知噪声) 的 RL 版本放大。这把 §6 末段"agentic post-training 是 Pearl 第二层方向上唯一一次真实进步" 的判断从 *相对乐观* 收紧到 *相对乐观但需附加条件*: **只有在 verifier hack 被独立排除的 agentic post-training 轨迹上，Lampinen 工业化论证才成立**——而 verifier-of-verifier 这条 2026 趋势恰好让"独立排除" 越来越贵。

**元判断 (2026-05-29)**: 三项查账合起来不动 §尾声三层墙的*分类结构* (第一层无墙 / 第二层数据+评测墙 / 第三层世界模型墙)，但把每一层的*可证伪坐标*都收紧了一格——Layer-3 从 CLadder 单点收紧到四 benchmark 谱协议性失败、video world model rollback 从独立 escape route 收紧到 C-WM-7 + C-GROUND-5 耦合包装、agentic Layer-2 增益从工业化论证收紧到 "verifier hack 已被独立排除" 条件版本。三条收紧方向一致：**N4 §尾声原版给出的可证伪门槛在 2026-05 全部仍然成立，但每条门槛都长出了一个新的 confound 接口**，与 [`../topics/causality.md`](../topics/causality.md) §10 readout-side 主导假设警示同型——每一次工程修补出现，falsifier 必须把对应隐藏前提显式化，否则 mech 候选会被假性证伪或假性加固。这条元方法论结构在 N2 (§7 TC⁰ 之墙新证据)、N3 (§7 三 bet 赔率结构方向性修订)、N5 (§7 三 sub-candidate 翻译为 Bet-N5 falsifier 网)、N7 (§7 annealing-as-stealth-CPT) 同期已重复出现四次，N4 §7 是第五次——这本身可能是 NTP-mech 调查在 2026 年的*主导节奏*：mech 命题本身的方向不变，evidence-base 与 falsifier 的精度逐节加密。如果 2027 年继续如此而 *主表 C1–C7 + Reversal Curse* 仍无升降级，那本系列就需要在 N1 §3 "NTP 三道天花板" 的元框架上加一段：**"mech 命题加密 ≠ mech 信号增强" 这一区分在 2027 之后必须明写**，否则会把方法学进步误读为科学进步。

## 八、2026-05-30 M1 元-corollary 回贴：把 §七 三项查账钉回 §10 同一根负反馈链

§七 三项查账写完两天后，[`../survey/ntp_survey.md` §10 中段元-审计 (2026-05-30 commit `64438d4`)](../survey/ntp_survey.md) 把 *五域 17 条非主表条目* 中的至少 8 条 (C-CONT-2 第三支柱 / C-WM-7 / C-EMBOD-7 / C-FORM-8 / C-REAS-6 / C-EMBOD-7 route-elim / OP-WM 时间侧加固 / C-CONT-1 第四支柱) 显式收编为同一元命题 **M1「frontier-disclosure 缺位作为 mech-relevant metric 系统性缺位」**——并在 2026-05-30 → 2026-06-10 之间立了一条 12 天 *增条冻结协议*。本节的目的是把这次 §10 元-审计的方向性结论回贴到 N4，避免本章 §七 三项查账落到 *sample 自走、survey §10 自走、两侧节奏脱钩* 的失同步状态——与 N3 §七 reviewer pass (commit `0b5c793`) / N7 §八 元-corollary 回贴 (commit `1811e6b`) / N1 §六 framework self-stress-test (commit `1f37e9f`) 三处 sample 侧回贴同型，是 sample↔§10 双向同步纪律的第四次具体化。

回贴一共三件事。第一，§七 第一项查账里把 Layer-3 评测墙的稳定性归到 \"四个独立 benchmark 谱协议性失败\"，但其中 *为什么没人愿意冲一个更严的协议* 这条社会学解释，在 §10 元-审计后正式被命名为 M1 在 causality 域的投影——具体是 C-CAUSAL-DISCLOSE (corollary, 候选 $m_{10}$, [`../topics/causality.md` §C-CAUSAL-DISCLOSE 半年披露差核查](../topics/causality.md))，登记的三个 <1 GPU-week 实验在 2025-12 → 2026-05 半年窗口内 *无任一公开执行*。这条社会学解释不是 N4 §七 \"四 benchmark 谱协议性失败\" 的补充，而是它的 *上游*：四谱失败是 readout，<1 GPU-week 实验缺席是 driver，二者都被 M1 元命题统一在 \"frontier 不报告对自己阵营不利的数字\" 这条负反馈链下。这一回贴的工程后果是：N4 §七 末段元判断 \"mech 命题加密 ≠ mech 信号增强\" 现在有了 *可机械判定的同步版本*——只要 12 天冻结协议到期 (2026-06-10) 后 M1 集合 $\\{m_k\\}$ 仍不变、四 benchmark 谱仍 0 反例、三个 <1 GPU-week 实验仍 0/3 执行，三个独立时间侧加固通道在同一窗口同步累计 *半年→一年* 刻度，即可宣告 \"加密 ≠ 信号增强\" 不仅是修辞而是 *已被三处同步观测的结构性事实*。

第二，§七 第二项查账把 video world-model 一脉从 Layer-3 independent escape route 收紧到 C-WM-7 + C-GROUND-5 *耦合包装*——这两条 corollary 现在都被显式归入 M1 集合 ($m_6$ video-backbone-replacement 与 $m_3$ cross-morphology，[`../topics/world_model.md` §OP-WM-2 拆条 reviewer pass](../topics/world_model.md) / [`../topics/embodiment.md` §C-EMBOD-7 reviewer pass](../topics/embodiment.md))。换言之 \"escape route 需付清两条债务\" 这一判断的 *债务方* 不是孤立的 world-model 与 grounding 两个 topic，而是 *同一 frontier-disclosure 负反馈链* 在两条不同投影上的投影——付清 C-WM-7 = 任一 frontier video model 在 CLadder Layer-3 上公开数字、付清 C-GROUND-5 = 任一 frontier 在 latent-action → LM token 桥上公开 controlled comparison，两件事都属于 M1 falsifier (*任一 frontier lab 在任一 $m_k$ 上首次公开 controlled measurement*)。这把 §七 \"耦合包装\" 的判断从 *两条独立债务* 收紧到 *同一债务的两个投影*——付清任一项即同时缓解 N4 §尾声第 3 条 \"第三层 = 世界模型墙\" 的判决以及 N6 §尾声 \"video L2 评测是下一阶段胜负手\" 的预测，sample 系列在 N4 / N6 两章之间不再 *各算各的债*。

第三，§七 第三项查账把 agentic Layer-2 增益收紧到 \"verifier hack 已被独立排除\" 条件版本，引用 C-REAS-6 reward-hacking 阶梯——C-REAS-6 在 §10 元-审计中归 M1 $m_5$ (verifier-chain-$\\beta_k$)，与 C-CAUSAL-DISCLOSE 在 [`../topics/causality.md` §C-CAUSAL-DISCLOSE M1 同步段 (c)(ii)](../topics/causality.md) 已被指认为 *跨域共担实验候选*：固定 base × 固定 RL 配方 × 不同评测分布 (verifier-内 / out-of-verifier / Pearl Layer-2) 同步采集，单一 <2 GPU-week 实验可同时压两条 corollary 的时间常数。这意味着 N4 §七 第三项查账的 \"附加条件\" 不是 N4 单章的问题，而是 reasoning ↔ causality 两域共享的 falsifier 缺位——任一团队执行该共担实验，即同时清零 C-REAS-6 与 C-CAUSAL-DISCLOSE 的时间侧累计，并在 sample 层把 N4 §六 \"agentic post-training 是 Pearl 第二层方向上唯一一次真实进步\" 的乐观线 *按设计独立验证* 而非靠 N4 §七 第三项的反向收紧维持悬念。

**12 天冻结协议下 sample 系列的对应纪律**：N4 §七 末段 \"如果 2027 年继续如此...在 N1 §3 元框架上加一段\" 的挂账，按 §10 冻结协议精神，2026-06-10 前 *不应主动展开*——M1 元命题已经把 \"mech 命题加密 ≠ mech 信号增强\" 这条元方法论结构在 §10 内部用 *固定 8 条 $\\{m_k\\}$ + 12 天冻结 + 候选 $m_9/m_{10}$ 暂不申请扩入* 三层硬约束实施了，sample 系列若同步在 N1 §3 加段会与 §10 形成 *双重命名同义反复*。本节回贴的 *实操承诺* 是：N4 §七 那条挂账暂存，等 2026-06-10 冻结到期后再决定 — 若届时 §10 元命题被新数据点扩到 $m_9 / m_{10}$ 任一 (grounding 或 causality 候选)，N1 §3 加段须以 \"M1 投影成 9 / 10 条\" 为主轴；若届时冻结协议续期且 $\\{m_k\\}$ 仍锁 8 条，N4 §七 挂账可在 2027 年回看时合并到 N1 §6 framework self-stress-test 第二轮，而不再单独成节。

**诚实判断**：本节是 N4 全章 *首次主动放弃一个挂账* 而非新增一个判断的小节——与 N7 §八 \"主动收缩一档\" 同型 (commit `1811e6b`)，是 sample 系列在 12 天冻结协议下的 *第二次方向收紧而非扩张*。本节最大的方法学风险是 *把 §10 元命题当万能容器* — 任何未来 N4 想新增的反例都可以被解释为 \"M1 在 causality 域的又一投影\"，使 N4 §七 三项查账的具体性被稀释到 \"反正都是 frontier-disclosure 在作怪\" 的同义反复。规避协议：(a) M1 元命题在 N4 章节内 *仅出现在本节 §八*，§七 三项查账原文不被回写、不被打标签，保持其 *单独可读* 状态；(b) 2026-06-10 冻结到期后若 M1 集合扩，本节须在 *同一节* 内打 \"2026-06-10 update\" 子标题增量更新，不开 §九 / §十——sample 系列的节数应止于 §八，与 N1 / N3 / N7 同步节奏一致；(c) §七 三项查账的 *可证伪坐标* 不被 M1 元命题替换，仍以 \"四 benchmark 谱协议性失败 / video world model 在 CLadder 任一 Layer-3 数字 / verifier hack 独立排除的 agentic Layer-2 协议\" 三件具体事件作 N4 全章总验收清单。三项均显式声明。R1 / o1 / GPT-5 / Claude-4 / Gemini-2.5 在 CLadder 上的 2026-05 数字仍 [unknown]，Det-CausalBench / CausalProbe-2024 / Cosmos / Genie-2/3 ID 标 [unverified] 或 non-arxiv，未编造数字 / 日期 / 标题。

---

*相关 topic：[causality](../topics/causality.md)（mech 候选 C-CAUSAL-1 / C-CAUSAL-2 的可证伪表述与四 benchmark 谱协议性失败；C-CAUSAL-DISCLOSE 候选 $m_{10}$ 是 §八 M1 回贴的 causality 域投影）、[world_model](../topics/world_model.md)（第三层 ≈ 在 world model 上做 rollback + 反事实 rollout；C-WM-7 latent-action codebook 可辨识性 = M1 $m_6$ 投影，§八 \"耦合包装\" 收紧的债务方之一）、[reasoning](../topics/reasoning.md)（CoT 对 Layer-2 有效、对 Layer-3 无效；C-REAS-6 reward-hacking 阶梯 = M1 $m_5$ 投影，§八 跨域共担实验候选的 reasoning 侧）、[grounding](../topics/grounding.md)（C-GROUND-5 action-execution gap = M1 $m_3$ 投影，§八 \"耦合包装\" 债务方之二）；同时与 [`../survey/ntp_survey.md` §10 中段元-审计 (commit `64438d4`)](../survey/ntp_survey.md) 双向锚定 M1 与 12 天冻结协议。*
