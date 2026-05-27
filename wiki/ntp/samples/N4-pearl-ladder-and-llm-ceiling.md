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


<!-- TODO §6 agentic post-training (o-series / R1-Zero / computer-use 轨迹回流) 是不是把第二层"补"进训练分布 -->
<!-- TODO §7 尾声：Pearl 的墙到底是架构墙还是数据墙；以及为什么这个区分对 NTP 路线判断至关重要 -->

---

*相关 topic：[causality](../topics/causality.md)（mech 候选 C-CAUSAL-1 的可证伪表述）、[world_model](../topics/world_model.md)（第三层 ≈ 在 world model 上做 rollback + 反事实 rollout）、[reasoning](../topics/reasoning.md)（CoT 对 Layer-2 有效、对 Layer-3 无效，是 faithful CoT 讨论里最尖锐的案例）。*
