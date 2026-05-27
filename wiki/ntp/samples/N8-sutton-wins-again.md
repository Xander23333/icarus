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

## 三-bis、被遗忘的三堵小墙

§二里那四堵墙都是写进教科书的大墙。下面三堵小一些，但它们的塌方过程更短、更干净，因此更适合用来校准"机制墙塌方"的典型时间常数。

**小墙 A：常识需要显式 knowledge graph (1984 → 2020)。** 1984 年 Doug Lenat 启动 Cyc 项目，假设是"机器若想拥有常识，必须把人类常识手工编码成 ≥10⁶ 条逻辑公理"。Cyc 在 30 多年里累积到约 2400 万断言 (Lenat & Marcus 2023 [*Getting from Generative AI to Trustworthy AI*](https://arxiv.org/abs/2308.04445) 自己给的数字)。同一时期 ConceptNet (Speer et al.)、ATOMIC ([arxiv:1811.00146](https://arxiv.org/abs/1811.00146)) 走同样的路线——区别只在于是否众包。2019-04 Sap 等的 *ATOMIC* 论文里还明确写：large-scale neural language models do not exhibit the kind of if-then commonsense reasoning that humans take for granted. 到 2020-05 GPT-3 发布、2022-11 ChatGPT 上线，常识 QA (CommonsenseQA, PIQA, HellaSwag, WinoGrande) 的 SOTA 全部被 NTP 模型零样本拿走，几乎没人再训练 ConceptNet-augmented 模型。Cyc 没有公开倒下的时刻，但 Lenat 2023-08-31 去世后这条路线在工业界事实上结束 [uncertain Cycorp 后续状态]。机制派的强命题"常识必须显式编码"**死了**；弱命题"LLM 的常识在长尾、组合场景下脆"还活着，但已经退化成 robustness 论文，不是范式论文。

**小墙 B：multi-hop QA 必须显式 reasoning module (2018 → 2022)。** HotpotQA ([arxiv:1809.09600](https://arxiv.org/abs/1809.09600)) 与 2WikiMultiHopQA ([arxiv:2011.01060](https://arxiv.org/abs/2011.01060)) 发布时，公认观点是"end-to-end Transformer 在 multi-hop 上必须显式拼接 graph reasoning / decomposition"，这一时期产出了大量 PathNet / GraphRetriever / DecompRC 的变种。2022-01 Wei 等 *Chain-of-Thought Prompting* ([arxiv:2201.11903](https://arxiv.org/abs/2201.11903)) 一篇 prompt-only paper 把 GSM8K / MultiArith / multi-hop QA 的 SOTA 一并刷新——**模块没了，只剩一行提示词**。再往后 self-consistency ([arxiv:2203.11171](https://arxiv.org/abs/2203.11171))、Tree-of-Thoughts ([arxiv:2305.10601](https://arxiv.org/abs/2305.10601))、PRM800K (Lightman et al. [arxiv:2305.20050](https://arxiv.org/abs/2305.20050))、o1 / R1 完全沿着"把 reasoning 留在 token 序列里"的路线推进。强命题"必须显式 module"**死了**；弱命题"CoT 是不忠实的、是 post-hoc rationalization" (Turpin 2023 [arxiv:2305.04388](https://arxiv.org/abs/2305.04388)) 活着，但它已经是 N3 §3 的核心议题，不再是反 NTP 的范式论点。

**小墙 C：Transformer 不能 symbolic variable binding (2019 → 2023)。** 这堵墙比墙 2 更窄、更早：一系列"Transformer 学不到 systematic variable binding"的实验给出过一个版本的预言——Transformer 拿到 `x=3, y=5, x+y=?` 时会失败，因为它缺 *register* 机制。GPT-3 早期确实失败。Anthropic 2022 *In-context Learning and Induction Heads* ([arxiv:2209.11895](https://arxiv.org/abs/2209.11895)) 把 induction head 命名为"分布式 register 的一种实现"；Allen-Zhu 等 Physics of LM 系列 ([arxiv:2305.13673](https://arxiv.org/abs/2305.13673) [unverified Part 编号]) 在受控合成数据上做出 attention head 实现 binding 操作的 mech 解读。到 2024-2025 的 reasoning model 上，已经没人再把 variable binding 当 Transformer 的硬墙了。这一堵塌得最安静，几乎没有讣告——这本身就是 *Bitter Lesson* 剧本里最常见的结尾方式：墙塌时不会有人开新闻发布会。

判断：这三堵小墙的共同点是**塌方时间常数 ≈ 4–10 年**，并且每一次塌方都伴随"机制派从范式论点退到 robustness / 样本效率论点"的转写。把它叠到 §二的四大墙上，*Bitter Lesson* 的实证基线已经是 7 例，不是 4 例。这是 N2–N7 任何机制候选必须正视的先验：哪怕你写得再形式化、再 falsifiable，先验概率仍然偏向你的候选会塌——只是塌的方式不一定是"被证伪"，更常见的是"被绕过 + 没人再提"。把这一行写到本章最显眼的位置，是为了让 N2–N7 的读者在读完那六篇高 conviction 的 mech 叙事后，不要忘了 base rate。

## 四、另一面：四堵到 2026 年仍然没有塌的墙

把 §二 / §三-bis 七个塌方事件全部承认下来之后，下一个诚实的问题是——**有没有反例？有没有同样年份级、同样被反复挑战、但 scaling 没能推过去的墙？**有。下面四堵墙是我能找到的最干净的反例。它们的存在不是用来安慰 N2–N7 的 mech 派——它们是用来校准"*Bitter Lesson* 的适用域"的。

**反墙 1：数学证明的形式化合成 (1956 → 2026 仍开)。** Newell-Simon 1956 *Logic Theorist* 启动了机器证明，70 年里这条线分裂成两条子线：(a) 交互式定理证明器 (Coq / Isabelle / Lean) 走的是"人写策略 + 机器检查"路线；(b) 自动定理证明 (E / Vampire / Z3) 走的是"完全自动 + 受限片段"路线。GPT-3 之后业界尝试把 LLM 接上去：GPT-f ([arxiv:2009.03393](https://arxiv.org/abs/2009.03393))、Lean-Gym、Magnushammer、Llemma ([arxiv:2310.10631](https://arxiv.org/abs/2310.10631))、DeepSeek-Prover ([arxiv:2405.14333](https://arxiv.org/abs/2405.14333))、AlphaProof (DeepMind 2024-07 IMO 银牌博客 [unverified arxiv])。到 2026 年战绩是这样的：miniF2F 高中竞赛集合上 SOTA 已被推到 70–80% 区间 (DeepSeek-Prover-V2 [unverified ID])，AlphaProof 在 2024 IMO 拿到 4/6 题 28/42 分；但 PutnamBench (Tsoukalas et al. [arxiv:2407.11214](https://arxiv.org/abs/2407.11214)) 公开 LLM 最佳通过率 **<10%**，且大部分通过题集中在低难度。**这堵墙没塌**：scaling + RL + verifier 把简单证明吃光了，但复杂证明的曲线**不像算术那样有明显斜率**。NTP 视角下的解释 (N3 §6 提过) 是"过程-结果同构惩罚"——证明对错由 Lean 检查 0/1 给出，**中间步骤的 NTP 损失提供不了梯度信号**，于是只能靠 RL，而 RL 在搜索空间组合爆炸时样本效率下降。这堵墙的形态符合 *Bitter Lesson* 的反例标准：算力已经堆了，方法已经换过两轮，曲线仍然平。

**反墙 2：长程强化学习的样本效率 (1992 → 2026 仍开)。** Sutton 自己 1992 年 *Reinforcement Learning is direct adaptive optimal control* 之后就清楚这条墙的样子：tabular RL 在 state-action 空间稍大时样本复杂度爆炸。深度 RL 时代 DQN (Mnih 2013) → A3C → PPO → SAC 把 Atari / MuJoCo / Go 推到超人，但**每一个超人结果都伴随 10⁷–10⁹ 步交互**。Hafner 2020 *Dreamer* 系列 ([arxiv:2010.02193](https://arxiv.org/abs/2010.02193) → DreamerV3 [arxiv:2301.04104](https://arxiv.org/abs/2301.04104)) 用 world model 把 Atari-100k benchmark 的样本预算压到 10⁵，但 100k 步仍是"100k 帧 ≈ 27 分钟人类游戏"，且 score 远低于人类。EfficientZero ([arxiv:2111.00210](https://arxiv.org/abs/2111.00210)) 类似。到 2026 年 LLM-as-policy / VLA 路线 (N5) 把语言先验注入 RL，但 OpenVLA / π₀ 的 sample efficiency 仍然以 "数千 demo + 数万 rollout" 为单位，**没有出现"再加 10 倍算力"就能把样本效率改善一个数量级的现象**。Sutton 本人在 *The Alberta Plan* ([arxiv:2208.11173](https://arxiv.org/abs/2208.11173) [unverified ID]) 里承认 model-based / option / state-abstraction 这些"结构"在长程 RL 中不可避免——这是 *Bitter Lesson* 作者自己留的口子。

**反墙 3：Physical embodiment 的 sim-to-real gap (1980s → 2026 仍开)。** Brooks 1991 *Intelligence Without Representation* 提出的"现实世界是它自己最好的模型"，到 2026 年仍然没有被"在 sim 里加 10 倍算力"打穿。OpenAI Rubik's cube (2019 [arxiv:1910.07113](https://arxiv.org/abs/1910.07113)) 用 domain randomization + LSTM 在仿真里训练，迁移到 Shadow Hand 真机；五年后 sim-to-real gap 仍然是 manipulation 论文的标配 caveat 章节。DeepMind robocat / RT-X ([arxiv:2310.08864](https://arxiv.org/abs/2310.08864)) / Physical Intelligence π₀ ([arxiv:2410.24164](https://arxiv.org/abs/2410.24164)) 全部走"真机数据为主、sim 仅辅助"路线，恰恰是因为 sim-trained policy 在真机上 zero-shot 仍然崩。LeCun 在 2024 多次访谈里把这条墙作为"world model 必须存在"的论据。N5 §3 的判断更精细：**强命题（action 不可 tokenize）已被 RT-2 / OpenVLA 部分证伪**，但**弱命题（sim → real 样本效率指数恶化）未被证伪**，因此这堵墙仍然算"半开"——它告诉我们 *Bitter Lesson* 的边界在哪里：当**输入分布**只能靠物理世界产生（不能像文本 / 棋盘那样合成），算力解锁失效。

**反墙 4：Scientific discovery 的 novel-hypothesis 生成 (1965 → 2026 仍开)。** Dendral (Feigenbaum 1965) → BACON (Langley 1981) → Adam (Ross King 2009 *Science* 的酵母代谢机器人) 这条线在 2023 后被 LLM 接管：FunSearch (DeepMind 2024 *Nature* [unverified arxiv])、AI Scientist (Sakana 2024-08 [arxiv:2408.06292](https://arxiv.org/abs/2408.06292))、Coscientist (Boiko-Gomes 2023 *Nature*)、Google Co-Scientist (2025-02 blog)。它们能复述、能组合、能在 well-defined search space 内 (Cap-set / 蛋白质结构 / 分子优化) 真出现"新"结果——但**完全开放式的科学假设生成**没有可信报告：没有任何 LLM 系统在 2026 年之前**独立**提出过被同行评审接收的新生物学机制或新数学猜想。Ouyang et al. *Hallucinations in LLMs Hinder Scientific Inquiry* (2024 *Nature MI* 评论) 与 Cheng et al. 2024 [arxiv:2402.07207](https://arxiv.org/abs/2402.07207) [unverified ID] 都把瓶颈定位在"无法生成既新颖又可验证的假设"。这堵墙和反墙 1 同源——**verifier 稀缺 + reward sparse + 搜索空间组合爆炸**——但更彻底，因为连"什么算对"本身都是开放的。

**判断（§四）**：把这四堵反例墙叠到 §三的剧本上，能精炼出 *Bitter Lesson* 的**适用条件**——它过去赢的每一次，都满足三个隐含前提：(i) 输入分布可合成 / 可大规模采集（文本、棋盘、图像、语音）；(ii) verifier 存在 (棋局规则、ASR ground-truth、image label、unit-test、math answer key)；(iii) 搜索/学习的单步信号密集 (NTP loss / TD error 每 step 给梯度)。**当这三个条件中任何一个垮掉，scaling 就停在弱命题的台阶上不再前进**。反墙 1 缺 (iii)、反墙 2 缺 (i)、反墙 3 缺 (i)、反墙 4 缺 (ii)+(iii)。这给 N2–N7 一个非常具体的诊断工具：**问任意 mech 候选——它打的是 (i)(ii)(iii) 三个条件中的哪一个？打中一个就有活路，三个都不打就是下一个塌方候选。**

按这个工具回去看 N2–N7：N2 (TC⁰) + N3 (Reversal Curse / 不忠实 CoT) 主要打 (iii) 单步信号的方向性/同构性，活下来的概率最高；N4 (Pearl 第二/三层) 打 (ii) verifier 稀缺 (反事实没有 ground-truth)，第二层弱命题已被 Lampinen / agentic post-training 蚕食，第三层仍然干净；N7 (continual learning) 打 (i) streaming 输入分布的不可重采样，但工业界用 replay + RAG 绕过的成本越来越低；N5 (embodiment) 同时打 (i) 与 (ii)，是 N2–N7 里**最有可能写进"反墙"清单**的一个；N6 (world model) 取决于具体定义，video-NTP 子命题打 (ii)+(iii)，可能活；observational pixel-only 子命题三条都不打，是最像下一次塌方的。这给 §六的 N1–N7 元批注留了完整骨架。

## 五、Sutton 自己的内部张力——*Bitter Lesson* 与 *Alberta Plan* 不是同一个 Sutton

把 *Bitter Lesson* 当作教条之前，先要正视一件让两边都不舒服的事：**Sutton 自己在 2022 年之后写的东西，并不是 *Bitter Lesson* 的延长线**。如果只读 2019 年那篇千字短文、不读后面这些，得到的会是一个被简化得太干净的 Sutton——一个把所有问题都归到"算力 + 通用方法"的 Sutton。真实的 Sutton 比这个稻草人复杂得多，而这种复杂在 N8 上下文里非常重要：它直接决定了 *Bitter Lesson* 的**适用域**比拥护者通常承认的窄，比反对者通常想象的宽。

2022 年 8 月，Sutton 与 Michael Bowling、Patrick Pilarski 联名挂出了 *The Alberta Plan for AI Research* ([arxiv:2208.11173](https://arxiv.org/abs/2208.11173))，一份四十多页的研究纲领。这是 Sutton 1985 年博士论文以来最长、最具体的一次"我接下来要做什么"陈述。文档把目标定为构造一个能在持续 (continual)、嵌入式 (embodied)、有限算力 (resource-bounded) 条件下学习的 agent，并列出十二个核心研究问题。**没有一个问题是"把模型放大十倍会不会解决"**。十二个问题里有 model-based RL、option discovery、state abstraction、meta-learning step-size、average-reward formulation、planning with learned models、knowledge representation by predictions (GVF / Horde 谱系，最早可回溯到 Sutton-Modayil-Delp [arxiv:1112.1133](https://arxiv.org/abs/1112.1133) [unverified ID])——清一色是"结构"。Sutton 在文档摘要里写了一句几乎要被忽略的话：*"intelligence requires architecture, not just scale"* [unverified 原话措辞]——这句话与 *Bitter Lesson* 的字面立场存在公开张力，但作者本人显然不觉得这是矛盾。

要解释这种"自我矛盾"，必须回到 *Bitter Lesson* 的原文措辞。Sutton 反对的从来不是"任何结构"，而是"**编码人类对问题怎么思考的特定先验**"。CNN 不是反例（它编码的是平移不变性，是关于**世界**的先验，不是关于"人怎么识别物体"的先验）；attention 也不是反例（编码的是"任意距离的 pair-wise 交互"，同样是关于序列结构的弱先验）。*Bitter Lesson* 攻击的是 SHRDLU 那种 hand-engineered 语法树、是国际象棋开局库、是 SIFT 那种基于人类视觉理论的特征。**search 与 learning 这两件"通用方法"本身就是结构**——只是 Sutton 把它们叫做"通用结构"而把另一类叫做"特定结构"。这条切割线在 *Alberta Plan* 里被显式承认：model-based RL 的 world model 是结构、option 是结构、state abstraction 是结构，但它们是"通用的、可被学习而非被手写的"结构。Sutton 反对的是**手写**，不是**结构本身**。

这条切割线对 N2–N7 至关重要，因为它意味着 mech 派的活路并不在于"举出一堵 scaling 推不过去的墙"——那是反方陈词最弱的一面，N8 §二已经枚举了七堵塌方墙、§四只能找到四堵半开墙。mech 派真正的活路是**举出一类无法被"通用方法"自动学到的结构**，并证明它必须以某种形式被显式构建。Sutton 自己在 *Alberta Plan* 里就给了模板：option discovery 这件事，他承认到 2022 年（论文挂出时）仍然没有任何端到端 self-supervised 方法能稳定从原始经验里发现有用的 temporal abstraction——这是 Sutton-Precup-Singh 1999 *Between MDPs and semi-MDPs* 之后二十多年的悬案。他给的回应不是"再加 10 倍算力"，而是"我们需要新的算法原语"。**Sutton 本人在 2022 年同意：算力解决不了 option discovery**。这与 §四反墙 2 (长程 RL 样本效率) 是同一个口子，只是从 Sutton 这边看见。

更进一步，2024–2025 间 Sutton 在多次访谈与 podcast (Dwarkesh Patel 2023-09 [unverified date]、Pieter Abbeel TalkRL 2024 [unverified date]、Cohere For AI 2025-02 [unverified date]) 里反复表达一个判断：**LLM 走在错的方向上**。原话大意是 "prediction of human-generated text is not the right objective"、"there is no goal"、"this is mimicry, not understanding" [unverified 原话措辞]。注意这不是 mech 派的话，是 Sutton 的话。它的内部一致性是这样的：*Bitter Lesson* 说赢家是"通用 learning + search"；NTP on internet text 是"通用 learning"但**完全没有 search、也没有 reward**——后两者在 Sutton 的语境里和前者同样不可省略。从他的视角看，pretraining-only LLM 是 *Bitter Lesson* 的**半成品**，不是它的胜利。他赞同的下一步是把 search 和 reward 真正接回来——这恰好就是 2024 之后 o1 / R1 / agentic post-training 走的方向，但 Sutton 显然认为目前的接法（PRM + outcome reward 在 verifiable domain）只是冰山一角。

由此可以厘清 §三那张"四阶段塌方剧本"的一个潜在误读。剧本里说 scaling 总能吞掉机制派，但**剧本的隐含假设是"objective 和 verifier 已经对齐到目标任务"**。国际象棋有胜负、ASR 有 ground-truth、image classification 有 label——都是 verifier 与 objective 对齐的清洁场景。NTP-only LLM 的 objective (token cross-entropy) 与目标任务 (helpful / honest / reasoning / agent action) 之间存在著名的失配——这是 RLHF / RLAIF / RLVR / process reward 整个分支存在的原因。Sutton 在 *Alberta Plan* 与 podcast 里反复指向的，正是这个失配：当 objective 与 verifier 不对齐时，"再加 10 倍算力"会加快收敛到错的极值。这给 §四 (i)(ii)(iii) 三条件诊断工具补了第四条隐藏条件：**(iv) objective 与 verifier 在目标任务上对齐**。N8 §四的反墙 4 (scientific discovery) 最彻底的原因正是 (iv) 整个崩掉——"什么算新颖且正确的科学假设" 本身没有 verifier。

**判断（§五）**：把 *Bitter Lesson* 与 *Alberta Plan* 并置之后，N8 的反方陈词应当**收窄**而不是被放弃。收窄的版本是这样的：在 (i) 数据可大规模采集、(ii) verifier 存在且廉价、(iii) 单步信号密集、(iv) objective 与 verifier 对齐 四条件同时成立的子领域里，"机制墙"几乎一定会被"通用 learning + search"推平，N2–N7 不应在这种场景下押注 mech；而在四条件**任意一条**不成立的子领域里，scaling 会停在弱命题的台阶上，mech 候选有真正的活路——但只有当它打的是"通用结构"（可被学习、可被推广），而不是"特定结构"（手写、不可外推）时才有活路。这一节其实是把 §四的诊断工具从"反方自我修正"升级成"Sutton 本人都同意的边界条件"，这让 N1–N7 的元批注（§六）可以站在一个更稳的基线上展开——不再是"mech 派 vs Sutton"，而是"哪些 mech 候选符合 Sutton 自己留下的口子"。

---

> **§6 路线图**（后续 tick 续写）：
> - §6：给 N1–N7 的元批注——按 §三的四阶段剧本、§四的 (i)(ii)(iii) 三条件、§五补出的 (iv) objective-verifier 对齐条件，逐一打分每篇 mech 候选目前处在哪个阶段、打中哪几个条件，并给出"被塌方"的最可能路径与时间窗口。重点回应 N5 (embodiment 同时打 (i)(ii))、N4 (Pearl 第三层打 (ii))、N6 (observational pixel-only world model 三条全不打)、N7 (continual learning 打 (i))。
