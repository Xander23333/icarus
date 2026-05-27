# Sutton 又赢一次？回顾被打脸的"机制墙"

> N8 是 NTP 系列的**反方陈词**。前七篇 (N1–N7) 用了大量篇幅论证各种 NTP 机制墙——TC⁰、Faith-and-Fate、Reversal Curse、Pearl 第三层、Embodiment、Catastrophic Forgetting。本章故意站到对立面：把过去三十年里**那些被广而告之、最后被 scaling 一脚踢翻的"机制墙"**编成一张清单，逼自己回答一个问题——如果上一代机制派输得这么彻底，凭什么这一代不会？
>
> 这不是修辞性自我怀疑。Rich Sutton 的 [*The Bitter Lesson*](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) (2019) 在每一代深度学习研究者的 onboarding 阅读清单里都出现，原因是它**已经赢了不止一次**。在敢说"这一次不一样"之前，先把"上一次"完整地讲清楚。

## 一、2019 年 3 月那篇千字短文，以及它为什么至今没被反驳

2019 年 3 月 13 日，Rich Sutton 在自己的个人页面发了一篇大约一千字的文章，标题 *The Bitter Lesson*。没有 arxiv 编号，没有同行评审，没有图。文章的核心论点用一句话能写完：

> 70 年 AI 史里，所有"我们需要往模型里塞结构 / 知识 / 先验"的努力，最终都被"加算力 + 加数据"的通用方法击败。

Sutton 当时 71 岁，是强化学习的奠基人之一（与 Andrew Barto 合著 *Reinforcement Learning: An Introduction*），不久后两人会因此拿到 2024 年的 Turing Award (2025-03 颁发) [uncertain 颁奖日期]。他在文章里点了四个例子：计算机国际象棋（Deep Blue 的暴力搜索打败了基于人类棋理的程序）、计算机围棋（AlphaGo 的 self-play 打败了基于围棋知识的程序）、语音识别（HMM + DNN 打败了基于音素学的程序）、计算机视觉（CNN 打败了基于 SIFT / HOG 的人工特征）。每一个例子的剧本都一样：先是几十年时间里一群非常聪明的人用手工结构小步前进，然后某一年算力够了，一个"无结构 + 算力 + 数据"的方法直接吞掉这条曲线。

这篇文章发表的时候——2019 年 3 月——GPT-2 才发布一个月（OpenAI 2019-02-14 的 staged release），上下文窗口 1024 token，参数 15 亿。当时没人把它和 *Bitter Lesson* 联系在一起。两年之后回头看，GPT-2 → GPT-3 ([arxiv:2005.14165](https://arxiv.org/abs/2005.14165), 2020-05) → ChatGPT (2022-11) → GPT-4 ([arxiv:2303.12712](https://arxiv.org/abs/2303.12712), 2023-03) → o1 (2024-09) → R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948), 2025-01) 这条曲线，**几乎就是 *The Bitter Lesson* 的第五个例子**：自然语言处理。曾经被认为必须靠 syntactic parsing / semantic role labeling / discourse representation theory / WordNet / FrameNet 才能解决的任务——指代消解、隐喻理解、跨句推理、翻译、写诗——被一个"无结构的 next-token prediction + 算力 + 数据"路线整体吞掉。

到 2026 年 5 月写这一章的此刻，再读 *Bitter Lesson*，最难受的不是它说了什么，是**它说了之后这七年发生的事**。七年里有过至少五次"NTP 撞墙了 / 需要新范式"的小高潮：2020 GPT-3 的算术失败、2022 Gopher / Chinchilla 显示参数和数据要重新平衡、2023 *Sparks of AGI* 的反例清单、2024 dense scaling 趋平、2025 pretraining loss 与下游能力解耦。**每一次**——除了 dense scaling 这一次还没有定论——业界的回应都不是换范式，而是：MoE、long context、RLHF、PRM、test-time compute、agentic post-training。骨架始终是 Transformer + NTP loss。

Sutton 没有反驳者。他有不同意者，但没有反驳者。这一点必须先讲清楚，再讨论"这次为什么可能不一样"。

## 二、清单：过去三十年里塌掉的机制墙

下面这张表不完整，但每一条都是一次有据可查的"机制派预言 X 不可能 → scaling 派把 X 做出来了"。我刻意只挑论点曾经写进**论文 / 教科书**、且后来被**论文 / 公开 benchmark** 反驳的事件，避开纯 Twitter 嘴炮。

**墙 1：连结主义学不到组合性 (1988 → 2020s)**

Fodor 与 Pylyshyn 1988 年那篇 [*Connectionism and Cognitive Architecture: A Critical Analysis*](https://www.sciencedirect.com/science/article/abs/pii/0010027788900315) (Cognition 期刊) 给出过一个非常清晰的预言：神经网络无法学会"系统性"(systematicity)——即从"John loves Mary"自动推广到"Mary loves John"那种结构性泛化。这个论点 Gary Marcus 在 [*The Algebraic Mind*](https://mitpress.mit.edu/9780262632683/the-algebraic-mind/) (2003) 中翻新成"代数操作 vs 统计模式"的二分。

Lake 与 Baroni 2017 年的 [SCAN benchmark ([arxiv:1711.00350](https://arxiv.org/abs/1711.00350))](https://arxiv.org/abs/1711.00350) 把这个论点 operationalize：训练集里出现 "jump twice"，测试集要泛化到 "jump thrice"。当时的 seq2seq LSTM 准确率接近 0%。Lake 自己在论文里写："These results suggest that standard sequence-to-sequence models are not capable of [the kind of] systematic compositional generalization [needed]." 这句话被引用成"神经网络学不到组合性"的实证证据。

七年之后再看：Csordás 2021 的 [*The Devil is in the Detail*](https://arxiv.org/abs/2108.12284) [unverified ID] 显示只要换 PE 和初始化 Transformer 在 SCAN 上能到 80%+，COGS ([arxiv:2010.05465](https://arxiv.org/abs/2010.05465)) 上 Furrer / Csordás / Zhou 等多组也分别把 generalization split 推过 70%；GPT-4 在 zero-shot SCAN 上直接 >95%。Fodor-Pylyshyn 的强命题（神经网络**原则上**学不到组合性）**死了**。Marcus 退到弱命题"它学得不像人那么样本高效"，那是一个完全不同的论点。

**墙 2：分布式表示学不到代数推理 (1990s → GPT-3)**

Hinton 1990 年代多次写过，分布式表示天然适合相似性匹配，但不适合**精确的离散代数操作**（比如多位数加法、变量绑定）。Marcus 2018 年那篇 [*Deep Learning: A Critical Appraisal* ([arxiv:1801.00631](https://arxiv.org/abs/1801.00631))](https://arxiv.org/abs/1801.00631) 把这个论点列成 10 条之一，并断言 deep learning 解不了 systematic arithmetic。GPT-3 ([arxiv:2005.14165](https://arxiv.org/abs/2005.14165)) 论文 §3.9.1 直接做了 2/3/4/5 位数加减法的 sweep：2-digit 100%, 3-digit ~80%, 4-digit ~25%, 5-digit ~10%。曲线难看但**斜率是正的**，且完全来自 next-token pretraining，没有任何 arithmetic-specific 模块。再过两年 [Singh-Strouse 2402.14903](https://arxiv.org/abs/2402.14903) 显示换 BPE 为 character-level 直接把 4-digit 推到 80%+，Lee 等 abacus embedding ([arxiv:2405.17399](https://arxiv.org/abs/2405.17399)) 推到 100 位以上。**强命题（神经网络不能做精确算术）死了**，弱命题（tokenization 制造了一个工程级别的难度墙）反而成了 2024–25 年的活跃研究方向。

**墙 3：没有 grounding 就没有语义 (1990 → 2023)**

Stevan Harnad 1990 年的 [*Symbol Grounding Problem*](https://www.cs.ox.ac.uk/activities/ieg/e-library/sources/harnad90_sgproblem.pdf) 给出过一个被引超过 7000 次的论点：纯符号系统不可能拥有语义，必须有非符号锚点（感知 / 行动）。Emily Bender 与 Alexander Koller 2020 年 ACL 的 [*Climbing towards NLU* (ACL Anthology 2020.acl-main.463)](https://aclanthology.org/2020.acl-main.463/) 把它升级成"octopus paper"：只见过文本的模型**原则上**学不到 meaning。Bender 与 Gebru 2021 年的 [*Stochastic Parrots* (FAccT 2021)](https://dl.acm.org/doi/10.1145/3442188.3445922) 给整个论点配上了一个万人传唱的隐喻。

到 2026 年我们知道：text-only LLM 在某些感知结构上**确实**学到了非平凡的对应。Abdou 2021 [*Can Language Models Encode Perceptual Structure* ([arxiv:2109.06129](https://arxiv.org/abs/2109.06129))](https://arxiv.org/abs/2109.06129) 显示 BERT 学到了颜色空间的几何，Patel-Pavlick 2022 [*Mapping Language Models to Grounded Conceptual Spaces*](https://openreview.net/forum?id=gJcEM8sxHK) [unverified ID] 显示方向、大小、温度等概念在 embedding 空间有可解码的拓扑，Søgaard 2023 [*Grounding the Vector Space of an Octopus* ([arxiv:2305.02223](https://arxiv.org/abs/2305.02223))](https://arxiv.org/abs/2305.02223) 直接形式化反驳了 octopus 论证。Bender 的**强命题（text-only 系统原则上没有 meaning）**站不住，弱命题（它学的不是人那种 meaning）退回到哲学辩论。

我把这条墙的塌方写得详细一点，是因为它和 N4（Pearl 阶梯）有结构相似：哲学论证 → benchmark 化 → benchmark 被 scaling 打穿 → 哲学论证退到不可证伪。每一次都是这个模式。

**墙 4：自回归生成做不了长程规划 (2017 → o1)**

这条墙最年轻，也最有教育意义。Bubeck 在 [*Sparks of AGI* (2303.12712)](https://arxiv.org/abs/2303.12712) 第 8 节给的那个 "poem with reversed last line" 反例 (N1 §2 已详述)，明确把"缺少规划"归为 autoregressive 范式的**结构性后果**。LeCun 2022 年 [*A Path Towards Autonomous Machine Intelligence*](https://openreview.net/forum?id=BZ5a1r-kVsf) 把同一论点写成了 JEPA 的纲领：autoregressive 不能做 hierarchical planning，所以必须换范式。

2024-09 OpenAI o1 发布，2025-01 DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) 复现，2025 全年 Claude Extended Thinking / Gemini 2.5 Thinking / Qwen3-Thinking 全部跟进。**架构没有变**：还是 dense / MoE Transformer，还是 NTP loss。变的只是 decoding 允许写几千 token 的草稿，加上 RL on verifiable rewards。Bubeck 给出的反例任务（汉诺塔 ≥5 盘、九宫格约束推理）在 o1 / R1 上**部分通过**——准确率从 GPT-4 的 <10% 提到了 >70%，但还没饱和。

这条墙**没有完全塌**，但**塌了一半**。N2 §4 已经讨论过：CoT 把 TC⁰ 墙翻过去要付出 Ω(n²) token 的工程代价 ([Feng 2305.15408](https://arxiv.org/abs/2305.15408))，但**翻得过去**——这是 Sutton 阵营的部分胜利。LeCun 的强命题（autoregressive 不能做 planning）目前看是错的，弱命题（autoregressive 做 planning 在经济上不可持续）还在被 inference scaling law ([Brown 2407.21787](https://arxiv.org/abs/2407.21787), [Snell 2408.03314](https://arxiv.org/abs/2408.03314)) 一点点蚕食。

## 三、判断：四条塌方的共同剧本，以及它们给 NTP 系列的警告

上面四条塌方有一个共同结构：

1. **第一阶段（哲学）**：基于某种关于"真正的理解 / 真正的推理 / 真正的语义"的定义，论证神经网络 / 分布式表示 / NTP 原则上做不到。
2. **第二阶段（benchmark 化）**：某个团队把这个定义 operationalize 成一个具体测试（SCAN / 算术 sweep / octopus probe / poem-reversal）。
3. **第三阶段（scaling 蚕食）**：5–10 年内，scale + 工程修补（更好的 PE、更好的 tokenization、CoT、RL）把 benchmark 推过 50%、再推过 90%。
4. **第四阶段（撤退）**：原命题被分拆为"强命题（已被证伪）"和"弱命题（样本效率 / 经济成本 / 鲁棒性 / 像不像人）"，机制派守着弱命题继续叙事。

这是过去三十年的**主导剧本**。N2–N7 那六篇样章里的每一个 NTP 机制候选——TC⁰ 墙、Faith-and-Fate 复杂度地平线、Reversal Curse、Pearl 第三层、Embodiment 数据墙、Catastrophic Forgetting——**都在第二阶段或第三阶段早期**。读者有理由怀疑：再过五年，每一个都会按同样的剧本塌掉。

我对此的判断分三层：

**第一层（同意 Sutton 阵营）**：上面四条剧本是真实的，机制派在过去 30 年里**总账是输的**。任何新的 NTP 机制墙叙事都必须扛住一个反问——"你凭什么不是第五个塌方？"如果扛不住，这个候选就还在第二阶段，不算 mech 候选，只是 cap 候选 (taxonomy.md 的 4-prong 标准)。

**第二层（对 Sutton 阵营的部分保留）**：四条塌方里有**两条只塌了一半**。算术（墙 2）塌了强命题但弱命题（tokenization 工程墙）反而被正式化成 Singh-Strouse / abacus 这一波研究。Planning（墙 4）塌了"做不到"但没塌"经济上做得起"——inference scaling 的 power-law 指数在 verifier-rich 任务上 ~0.3，verifier-poor 任务上 ~0 (N4 §3 / scaling_limits §inference)。**半塌的墙不算输**——它们告诉我们，弱命题如果一开始就被精确陈述、配上可证伪的经济或样本量条件，**能活过 scaling 浪潮**。这正是 N2–N7 里我反复强调"机制候选必须带 falsification condition"的原因。

**第三层（这一次可能不一样的一个具体理由）**：上面四条塌方都发生在**算法被算力解锁**的阶段——硬件给了算法一个之前没有的预算，原本的工程墙被预算冲塌。但 2024–2026 这一轮的 NTP 机制候选有一个不同点：**dense scaling 的曲线已经趋平**（GPT-4 → GPT-4.5 → GPT-5 [uncertain，GPT-5 状态截至 2026-05 仍未公开发布] 的能力斜率显著小于 GPT-3 → GPT-4），救场的 MoE 与 inference scaling **都不增加 effective sample，只是更便宜地使用既有 sample**。N7 §1 引用的 FreshQA / RealTime QA 三年非证伪、N3 §5 的 Reversal Curse 三年未被任何 ≥7B 标准 NTP 干净修复，都符合一个"算力解锁失效"的画像。

但请注意"可能"二字。这一段是**预测，不是结论**。Sutton 已经赢过四次。如果到 2028 年 Reversal Curse 被某个 reverse-pretraining + RAG + agentic post-training 的组合干净修掉、Faith-and-Fate 曲线被 inference scaling 平推到任意深度、Pearl 第二层被 agentic RCT post-training (N4 §4 已埋伏笔) 攻破，那这一章就成为 N8 的反面教材——又一个被 *Bitter Lesson* 吞掉的"机制墙清单"。

---

> **§3–§6 路线图**（后续 tick 续写）：
> - §3：被遗忘的塌方——三条小一些但同样有教育意义的墙（symbol manipulation by Transformer / commonsense knowledge graph 必要性 / multi-hop QA 需要显式 reasoning）
> - §4：另一面——四条**没有塌**的墙（数学证明的形式化、强化学习的样本效率、physical embodiment 的 sim-to-real、scientific discovery 的 hypothesis generation），并讨论它们和 NTP 系列的关系
> - §5：Sutton 自己的内部张力——*Bitter Lesson* 与 *The Alberta Plan* (2022) 之间，他本人也承认结构在某些场景下不可避免
> - §6：给 N1–N7 的元批注——按本章四阶段剧本，逐一打分每一篇里的机制候选目前处在哪个阶段，并给出"被塌方"的最可能路径与时间窗口
