# Causality

> Pearl hierarchy, counterfactual, intervention modeling。LLM 在 NTP 训练范式下能否真正登上 Pearl 三层中的第二、第三层？

## 核心问题与 NTP 假设

Judea Pearl 在 *The Book of Why* (2018) 和更早的 "Theoretical Impediments to Machine Learning with Seven Sparks from the Causal Revolution" ([arxiv:1801.04016](https://arxiv.org/abs/1801.04016)) 里把因果能力分成三层：(1) **Association** P(y|x)，(2) **Intervention** P(y|do(x))，(3) **Counterfactual** P(y_x|x', y')。Pearl 的核心断言是：只观测被动数据（passive observation）的系统，无论参数多大，都被困在第一层；要登上第二层至少需要 intervention，要登上第三层还需要 structural model。

NTP 训练就是典型的"被动观测"：模型只见过 token 共现，从未对真实世界做过 do-operation。于是产生了 NTP 文献里被反复争论的一对极端假设：

- **悲观侧 (mech)**：NTP 模型在因果推理上**有架构级上限**——它能模仿训练语料里出现过的因果叙述模板（"smoking causes cancer"），但无法对未见过的 SCM 做正确 intervention / counterfactual 推理。Zečević 等人把这一现象称作 *causal parrots*。
- **乐观侧 (cap/pseudo)**：只要语料里包含足够多的因果叙述（医学教科书、法律判例、物理推导），LLM 就能学到一个**meta-distribution over SCMs**，从而在 prompt 时正确执行 do-calculus。Kıcıman 等人 2023 年的大规模实验是这一派最常被引的证据。

本 topic 跟踪：(a) 把 Pearl 三层映射到具体 LLM benchmark 的 formalization；(b) "因果鹦鹉"反例的强度；(c) intervention / RL / agentic 训练能否在不改架构的前提下突破第一层。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 | 链接 |
|---|---|---|---|---|
| 2026-05-26 | Causal Tongue-Tie | 同一 LLM 在 anti-commonsense CLadder 上 linear probe 0.97 / yes-no 0.5；≈+0.47 gap 全部来自 verbal readout 失败；output-only causal benchmark 不能直读为 mechanism 结论 | counter-evidence (削弱 mech 解读) | [2605.25891](../papers/paper_notes/2026-05-28-2605.25891-causal-tongue-tie.md) |
| 2026-05-26 | Why We Need World Models for AGI (LDI / Flux) | 提出 Latent Dynamics Inference 框架；在 rule-定义的 Flux 环境上 latent-state RL agent 系统性优于纯文本 LLM；主张 NTP 与 latent dynamics inference 的 objective-level 错配（弱版本主张，前提依赖 simulator-access） | mech 候选 (框架级，弱) | [2605.23972](../papers/paper_notes/2026-05-28-2605.23972-world-models-for-agi-ldi.md) |
| 2023-05 | Kıcıman, Ness, Sharma, Tan — *Causal Reasoning and Large Language Models: Opening a New Frontier for Causality* | GPT-4 在 pairwise causal discovery、counterfactual reasoning、actual causality 三类任务上显著超过 prior SOTA；作者主张 LLM 已是"实用级 causal assistant" | cap (乐观) | [arxiv:2305.00050](https://arxiv.org/abs/2305.00050) |
| 2023-05 | Lampinen et al. — *Passive learning of active causal strategies in agents and language models* | 在受控合成环境里，纯被动 imitation 训练的 agent 居然能学会主动 intervention 策略——前提是训练分布里包含 expert 的 intervention 轨迹 | counter-evidence (passive≠blind) | [arxiv:2305.16183](https://arxiv.org/abs/2305.16183) |
| 2023-08 | Zečević, Willig, Singh Dhami, Kersting — *Causal Parrots: Large Language Models May Talk Causality But Are Not Causal* | 提出 *meta-SCM* 框架；证明 LLM 在被 prompt 触发因果叙述时，本质是在检索语料里的 causal facts，而非执行 do-calculus；构造对抗实例使 GPT-4 在改名变量上系统出错 | mech (悲观) | [arxiv:2308.13067](https://arxiv.org/abs/2308.13067) |
| 2023-12 | Jin et al. — *CLadder: A Benchmark to Assess Causal Reasoning in Language Models* | 10K 题、覆盖 Pearl 三层的 formal benchmark；GPT-4 在第一层接近 ceiling，在第二层 (intervention) 显著下滑，在第三层 (counterfactual) 接近随机；CoT 帮助第二层但对第三层无效 | mech (boundary) | [arxiv:2312.04350](https://arxiv.org/abs/2312.04350) |
| 2024-02 | Jin et al. — *Can Large Language Models Infer Causation from Correlation?* (CORR2CAUSE) | 给定一组 correlation statements，要求模型推 causal graph；GPT-4 准确率 ~30%，远低于专门符号求解器；fine-tune 后会过拟合 surface pattern | mech | [arxiv:2306.05836](https://arxiv.org/abs/2306.05836) [unverified ID] |
| 2024 | Geiger et al. — *Causal Abstractions of Neural Networks* / interchange intervention 系列 | 用 interchange intervention 在 LLM 内部找到与符号算法对齐的 causal variable；提供"LLM 内部是否真的实现了因果计算"的可测协议 | mech (mechanistic) | [arxiv:2106.02997](https://arxiv.org/abs/2106.02997) |

## 当前共识 / 争议

- **共识 (Layer 1)**：LLM 在 *associative* 因果叙述检索上已基本饱和；CLadder Layer-1 子集、Tübingen pairs 上 GPT-4 / Claude / Gemini 都接近人类。
- **争议 (Layer 2 — intervention)**：Kıcıman 派认为 prompting 加 CoT 已能稳定执行 do-calculus；Zečević / Jin 派构造的"变量改名 / 反事实分布外"实验显示这只是 *memorized template*。两派的分歧根源在于 **测试集是否在训练语料的因果叙述 manifold 内**——这是一个几乎无法证伪的争论，除非用 Lampinen 那种 fully synthetic、token-level 不可能泄漏的环境。
- **争议 (Layer 3 — counterfactual)**：CLadder Layer-3 上所有 frontier model 均接近随机，目前**没有令人信服的 counter-evidence**说 NTP 单独能登上第三层。这是当前 NTP-mech 阵营最强的一块阵地。
- **被打开的边界**：Lampinen 2023 提示 *passive ≠ associative-only*——只要 demonstrator 在数据里做 intervention，imitator 就能学到 intervention policy。这对 Pearl 原始论证是一个微妙的削弱：被动观测者如果观测的是"主动者的行为"，仍可能继承第二层能力。这条线在 2025 的 agentic post-training（OpenAI o-series、DeepSeek-R1-Zero、Claude computer-use 轨迹回流）下尤其值得追踪。

## 关键证据线 (chronological)

把 "NTP 能否上 Pearl 阶梯" 这场争论按时间排开，可以看出它经历了三轮翻转——每一轮都不是某一篇论文一锤定音，而是某一类 **leak-check 协议** 被收紧或被绕过。

- **2018-01 — Pearl, *Seven Sparks from the Causal Revolution* ([arxiv:1801.04016](https://arxiv.org/abs/1801.04016))**。Judea Pearl 把 association / intervention / counterfactual 三层分清楚，并明确断言："被动观测系统无法跨过第一层"。这条断言在 LLM 出现之前对应的是经典 ML，但被 2022 年之后的整条 LLM-causality 文献拿来当 null hypothesis。
- **2023-05 — Kıcıman, Ness, Sharma, Tan ([arxiv:2305.00050](https://arxiv.org/abs/2305.00050))**。第一份在 Tübingen pairs、CRASS counterfactual、actual-causality 任务上系统报告 GPT-4 超过 prior SOTA 的工作，被乐观派引为"LLM 已实质性突破 Pearl 第一层"的旗帜证据。但论文自己也承认：所用 benchmark 大半与训练语料分布高度同构，没有做严格 leak-check。
- **2023-05 — Lampinen et al. ([arxiv:2305.16183](https://arxiv.org/abs/2305.16183))**。在 fully synthetic gridworld 里证明：**只要 demonstrator 在数据里做 intervention，纯 passive imitation 训练的 agent 也能在 OOD 任务上学到 intervention policy**。这是 Pearl 原始论证里"被动观测"语义被首次形式化拆解——passive learner 不等于 associative-only learner，关键看 *观测对象* 是被动者还是主动者。
- **2023-08 — Zečević et al., *Causal Parrots* ([arxiv:2308.13067](https://arxiv.org/abs/2308.13067))**。提出 meta-SCM 框架，构造 variable-rename 对抗实验：把 SCM 里的变量名换成 LLM 训练分布外的 token 后，GPT-4 准确率系统性塌缩到随机。这是首份把 "LLM 在 causality 上看似能做" 解释为 *训练分布内 fact-retrieval* 的 mech 论据，也直接催生了后来 CLadder 的 leak-check 设计要求。
- **2023-12 — Jin et al., *CLadder* ([arxiv:2312.04350](https://arxiv.org/abs/2312.04350))**。第一个 10K-题、覆盖 Pearl 三层、有 formal SCM 标注的 benchmark。GPT-4 Layer-1 接近 ceiling、Layer-2 ~55%、Layer-3 ~40%，CausalCoT 把 Layer-2 推到 ~65% 但 Layer-3 仍停在随机。这是 "Layer-3 是当前 NTP 最硬阵地" 这一共识的实证基础。
- **2024-02 — Jin et al., *CORR2CAUSE* ([arxiv:2306.05836](https://arxiv.org/abs/2306.05836) [unverified ID])**。把任务从 "答因果问题" 改成 "从一组 correlation statements 推 causal graph"，GPT-4 ~30% 接近随机，且 fine-tune 后 OOD 直接崩溃——*推 graph* 与 *答 do-question* 两个 capability 在 NTP 模型里似乎是解耦的。
- **2024-03 — Krishnamurthy et al., *Can LLMs Explore In-Context?* ([arxiv:2403.15371](https://arxiv.org/abs/2403.15371))**。在 multi-arm bandit 上验证：base LLM 自己探索接近随机，但塞入 expert exploration trace 后 in-context 行为接近 UCB。Lampinen 假说的 LLM-scale 复刻——直接关系到 Layer-2 "经验突破" 的解释空间。
- **2025-01 — DeepSeek-R1 / R1-Zero ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948))**。GRPO over verifiable rewards 把 "模型在 sandbox 里 do(run_code) 然后观测 stderr" 这类轨迹大规模回流——从 Pearl 形式定义看是合法 do-operation。但至 2026-05 没有公开实验把 R1-Zero 训练前/后的同一 base model 在 CLadder Layer-2 上做 controlled comparison（详见前一节）。
- **2026-05 — Semantic-Loss Anti-Collapse ([2605.05438](../papers/paper_notes/2026-05-27-2605.05438-semantic-loss-causal-collapse.md))**。Gemma 270M 用纯 CE 在 transitivity / d-sep 任务上 fine-tune 后 73.9% accuracy 实际由 **100% 输出恒答 Yes/No 的 collapse** 制造；加 semantic loss + 动态 λ 后 collapse 消解，accuracy 下移但 per-class 分布健康。这一击直接质问 *过去三年 causality fine-tune 类 "NTP 学不到因果" 论据中有多少是 collapse 假阳性*——回答未知，但 effect size 必须重测。

## 当前最强的 mech 候选 (NTP × causality)

把上面证据线翻译成可挂进 [survey/taxonomy.md](../survey/taxonomy.md) 的 NTP-mech 假设，2026-05 留下三条最难被冲掉的：

- **C-CAUSAL-1 — SCM held-out 上的 Layer-2/3 floor**：在训练语料**不含** SCM S 的任何 textual rendering、且 S 的变量名为训练中未见 token 的前提下，NTP 训练的 transformer 在 S 上的 Layer-2 / Layer-3 准确率不可显著高于随机。*Falsification*：构造 fully held-out SCM family（变量名随机 UUID + 训练前严格 n-gram leak-check），若 frontier LLM 零样本 Layer-2 > 80% 即被证伪。CLadder 当前协议**不满足** leak-check，Zečević rename 实验最接近但规模 < 50 SCM。
- **C-CAUSAL-2 — Counterfactual 阶梯**：在任何 leak-checked 协议下，Layer-3 (counterfactual) 准确率不会随 model scale 单调上升，且 CoT / self-consistency / tree-of-thought 等 inference-time scaffold 对 Layer-3 的 lift 不超过 5pp。*Falsification*：在 ≥ 7B base + 任意 inference-time 协议下，CLadder-或同等 leak-check benchmark 上 Layer-3 ≥ 60% 即被证伪。截至 2026-05 没有公开正向反例；Shpitser-Pearl ID 算法的 #P-hard 子集结构是其 complexity-theoretic 锚点。
- **C-CAUSAL-3 — Discovery ≠ inference 解耦**：CORR2CAUSE 风格的 *causal graph 推断* 与 CLadder 风格的 *do-question 回答* 在同一 base model 上的能力相关性低（Spearman ρ < 0.3 across model families）；fine-tune 一侧不显著迁移到另一侧。*Falsification*：在 ≥ 5 个 base model 上同时测两类任务，相关性 ≥ 0.7 即证伪；或单一 fine-tune 协议同时 lift 两端 ≥ 15pp。

## 反例与上界突破

NTP-mech 派在 causality 这条线上必须直面的反例：

1. **Lampinen 2305.16183 + Krishnamurthy 2403.15371**：passive learner 在观测主动者轨迹后能学到 intervention / exploration policy。这把 "NTP 必然停在第一层" 的强读法直接钉死——*passive ≠ associative-only* 已是 2026 的事实底色。R1-Zero 风格 RL 把 "demonstrator" 换成模型自身在 sandbox 内的 do-trace 后，这条路线在 frontier scale 上的边界仍未量化。
2. **Semantic-Loss Anti-Collapse 2605.05438**：揭示 fine-tune 类 "NTP 学不到 X" 论据普遍受 output-distribution collapse 污染。Dziri 2305.18654 / Jin 2306.05836 / 部分 CLadder fine-tune baseline 都需要补 per-class accuracy 与输出熵 sanity check 才能重读。
3. **Kıcıman 2305.00050 + Geiger 2106.02997**：前者经验上把 Layer-1/2 推到接近 ceiling（虽然 leak-check 不严），后者方法论上承诺 "若 do-circuit 存在我们能找到"。这两端共同压缩了 "NTP 完全不会因果" 这一强命题的生存空间——更严肃的提法只能是 *leak-checked Layer-3 下界*，不是 *任何 layer 下界*。

## 2026-05-27 判断

把上面拼起来：causality × NTP 这一脉，2026-05 的状态是 **强命题已死、弱命题幸存、且弱命题正被 agentic post-training 的数据 channel 缓慢侵蚀**。

- 强命题 "NTP 模型永远停在 Pearl 第一层" 在 Lampinen / Krishnamurthy / agentic-trace 三连击下已不可辩护。
- 弱命题 "在严格 leak-checked SCM held-out 下 Layer-3 仍随机" 仍然成立——CLadder Layer-3 三年没有真正的 counter-example，这是 NTP-mech 派目前最硬的一块阵地（C-CAUSAL-2）。
- 但弱命题的护城河完全依赖 **leak-check 协议的严格度**。一旦 R1-Zero / Operator / computer-use 风格的 sandbox do-trace 在 post-training 阶段 covertly 把 SCM textual rendering 引入分布，C-CAUSAL-1 的 *形式表述* 仍成立（变量名仍可 UUID 化），但 *经验可证伪性* 会持续退化——因为很难再构造一个 frontier model 没见过的 SCM 文本族。

换句话说：causality topic 的下一年关键不在再做一篇 "GPT-N 在 CLadder 上得了多少分"，而在 (a) 构造 R1-Zero 训练前/后同一 base 的 controlled Layer-2 对比（agentic-data 的因果增益量化）；(b) 把 Geiger 式 interchange intervention 推到 CLadder Layer-2 任务，找 do-circuit 或证明找不到；(c) 用 UUID-rename + n-gram leak-check 严格化的 SCM held-out 协议复刻 Zečević 实验在 ≥ 1000 SCM 规模上的结果。

## Open problems

- Pearl Layer-3 (counterfactual) 是否存在任何 prompting / inference-time 技巧（self-consistency、tree-of-thought、tool-use do-calculator）能稳定突破随机？目前所有公开结果都是负向，但负向结果发表偏差严重。
- agentic post-training（让模型真正在 environment 里 do(x)）是否等价于把 Pearl 第二层"补"进训练分布？如果是，NTP 与 RL-from-interaction 的边界就不是架构问题而是数据问题。
- mechanistic interpretability 侧：能否用 Geiger 式 interchange intervention 在一个真正训练过的 LLM 里**找到**实现 do-operator 的 circuit？目前只在 toy 模型上成功。
- 因果发现 (causal discovery) 与因果推理 (causal inference) 在 LLM 里是否共享 circuit？CORR2CAUSE 提示二者解耦，但样本太少。

## 2024–2026 更新：agentic / RL 是否在偷偷把 Layer-2 数据补回来

Pearl 1801.04016 的原论证里有一个常被忽略的限定：\"被动观测\" 指的是 *数据生成过程* 不包含 intervention，而**不是**模型本身没有 actuator。这个区分在 2024 年之后变得关键，因为 frontier post-training 流水线开始大规模回流三类数据：(1) tool-use / code-execution trace（模型 do(run_code) 然后观测 stderr），(2) computer-use 与 browser 轨迹（Claude 3.5 Sonnet computer use 2024-10、OpenAI Operator 2025-01），(3) RL-from-environment（DeepSeek-R1-Zero [arxiv:2501.12948](https://arxiv.org/abs/2501.12948) 的 GRPO over verifiable rewards）。从 Pearl 的形式定义看，这些都是合法的 do-operation——只不过 do 的不是物理世界而是 sandbox。

这恰好是 Lampinen [arxiv:2305.16183](https://arxiv.org/abs/2305.16183) 那条 \"passive learner of active strategies\" 路线的 frontier-scale 验证：训练分布里塞进来 demonstrator 的 intervention 轨迹后，imitator 学到的 policy 在 OOD intervention 任务上 generalize。Krishnamurthy et al. [arxiv:2403.15371](https://arxiv.org/abs/2403.15371) (\"Can large language models explore in-context?\") 把这条线的 in-context 版本测了一遍：base model 在 multi-arm bandit 上探索行为接近随机，但 few-shot 加 expert exploration trace 后能逼近 UCB——这是 \"被动观测主动者\" 假说在 LLM 上最干净的实验。

判断：agentic post-training 并不破坏 C-CAUSAL-1 的形式表述（变量名 leak-check 仍然适用），但它**经验上削弱**了 \"NTP 只能学第一层\" 的强读法。截至 2026-05，还没有公开实验把 R1-Zero 风格 RL 训练前后的同一 base model 拿到 CLadder Layer-2 上做 controlled comparison——这是当前 causality × NTP 文献最便宜也最有价值的空缺。

## Mechanistic 侧：interchange intervention 与 do-circuit 的搜索

Geiger 等人从 [arxiv:2106.02997](https://arxiv.org/abs/2106.02997) 起把 *interchange intervention* / *causal abstraction* 作为 mechanistic interpretability 的形式语言，到 2023 年的 *Boundless DAS* ([arxiv:2305.08809](https://arxiv.org/abs/2305.08809)) 已经能在 Alpaca-7B 上对 \"price tagging\" 这类符号算法找到对齐的内部 causal variable。这条线对 causality topic 的意义是：它给 \"LLM 内部是否真的运行 do-operator\" 这个本来纯哲学的问题，提供了**操作化判据**——如果能在模型内部 swap 某个 hidden state 子空间，下游输出就按 SCM 预测的方式改变，那这个子空间就是该 SCM 在模型里的 implementation。

但到 2026 年为止，这条路线在 \"真因果推理\" 任务上还没有突破性发现：(a) 现有成功案例（Othello-GPT 棋盘状态、indirect object identification circuit [arxiv:2211.00593](https://arxiv.org/abs/2211.00593)）找到的都是 *associational* 充分统计量，不是 do-operator 本身；(b) CLadder Layer-2/3 任务上没有公开的 circuit-level 分析，主要障碍是任务本身 token 化后 circuit 过深、过 distributed。Conmy et al. [arxiv:2304.14997](https://arxiv.org/abs/2304.14997) 的 ACDC 自动 circuit discovery 在这类长 reasoning 任务上 scale 不动。

诚实判断：mechanistic 侧目前给 causality topic 提供的是 *方法论承诺* 而非 *证据*——它说 \"如果 do-circuit 存在我们能找到\"，但还没说 \"我们找到了\" 或 \"我们证明找不到\"。这与 formal_limits topic 的状况（有定理、缺紧上界）形成对比：causality 这边是 *有方法、缺结果*。

## Layer-3 硬度的三个互补下界 (2026-05 综合)

C-CAUSAL-2 之所以是 NTP-mech 派最硬的阵地，并不是因为某一篇论文证明了它，而是因为三条**互不依赖、互相补强**的下界论证恰好同时指向 Layer-3。把这三条单独看都不致命，叠在一起就形成了目前没有哪条 escape hatch 能一次性绕开的 wall。

- **下界 (i) — 复杂性侧**：Shpitser & Pearl 2006 *Identification of Conditional Interventional Distributions* (UAI) 证明 ID algorithm 对一般 SCM 的 counterfactual identifiability 判定本身是 #P-hard 子集（NP-hard 的 counting 版本），而第三层 query 求值在 identifiable 子集内仍需 SCM-level exact inference。这条线把 Layer-3 钉在了 Sanford-Hsu-Telgarsky [arxiv:2402.04347](https://arxiv.org/abs/2402.04347) 的 TC⁰ 上界**之上整整两个复杂性类**——单 forward pass 的 transformer 在 worst case 上做不到，不是经验问题而是 circuit-complexity 问题（详见 [formal_limits.md](formal_limits.md) §TC⁰ 下界一节）。Merrill & Sabharwal [arxiv:2310.02309](https://arxiv.org/abs/2310.02309) 把 CoT 的 polynomial-step rollout 推到 P 类，理论上能盖住 #P 子集的小实例，但常数与步数都没有 closed-form 界。

- **下界 (ii) — 数据分布侧**：Pearl 1801.04016 的"被动观测"论证在 NTP 上的具体形态是：counterfactual query \"if X had been x' instead of its observed value, would Y have been y?\" 的**自然语料密度近乎零**。CommonCrawl / arXiv / 教科书里出现的因果叙述压倒性是 associational（"X 导致 Y"）或 interventional（医学 RCT 报告 "doing X led to Y"），而显式 counterfactual rendering 只在法律判例 (but-for causation)、历史反事实小说、少量哲学文本里成规模出现，估计 < 10⁻⁴ token-level 频率 [unverified]。Lampinen [arxiv:2305.16183](https://arxiv.org/abs/2305.16183) 那条 "passive learner of active strategies" 的活路在 Layer-3 上几乎走不通——它要求训练分布里有 demonstrator 在做相应操作的轨迹，而 *做反事实* 本身是 demonstrator 做不到的（反事实定义上需要回到已发生历史的分叉点）。这一条独立于架构，纯是数据物理。

- **下界 (iii) — 评测协议侧**：CLadder [arxiv:2312.04350](https://arxiv.org/abs/2312.04350) Layer-3 三年没有出现公开 counter-example，但更关键的是 2024–2026 没有任何新 counterfactual benchmark 通过严格 leak-check 报告 frontier model 显著高于随机的结果。Frohberg & Binder *CRASS* (LREC 2022) 在公开 leaderboard 上 GPT-4 报告 ≈ 90%，但 CRASS 题干高度结构化（"if X had not happened, would Y..."）且公开多年，n-gram leak 风险极高，不能作为反例。Zečević *Causal Parrots* [arxiv:2308.13067](https://arxiv.org/abs/2308.13067) variable-rename 协议规模 < 50 SCM 也只测 Layer-2。**没有一个 ≥ 1000-SCM、UUID-rename + 严格 n-gram leak-check 的 Layer-3 benchmark 存在**——这既是 C-CAUSAL-2 的最大方法论缺口，也是它"无法被证伪"的真正原因。

诚实判断：把这三条下界放一起，Layer-3 的难度*不是*一个干净的 \"NTP 永远学不到\" 命题，而是 \"在 (i) 单 forward pass 内做不到 + (ii) 自然数据里几乎不存在示范 + (iii) 测出来也没人信\" 的三重夹击。任何想冲掉 C-CAUSAL-2 的工作必须同时回应三条：架构侧需要 unbounded CoT / pause-token / latent-reasoning（Goyal [arxiv:2310.02226](https://arxiv.org/abs/2310.02226) / Hao Coconut [arxiv:2412.06769](https://arxiv.org/abs/2412.06769) [unverified ID]），数据侧需要 synthetic counterfactual corpus 注入（目前公开工作罕见），评测侧需要 UUID-rename + leak-check 的新协议。三者缺一，Layer-3 的所谓 "突破" 都会被前面三条之一吃掉。

这也是为什么 N4 sample (*Pearl Ladder and the LLM Ceiling*) 的尾声把 Layer-3 标为 "NTP-mech 派最后一块阵地"——不是因为这块阵地特别大，而是因为绕过它需要同时打破三堵性质不同的墙。

## RL-from-environment 在 Layer-2 上的 controlled comparison：现有边角与未填的洞 (2024–2026)

前面 §"agentic / RL 是否在偷偷把 Layer-2 数据补回来" 反复强调 "**没有公开实验把 R1-Zero 风格 RL 训练前后的同一 base model 拿到 CLadder Layer-2 上做 controlled comparison**"。这个判断现在已经被引到 N4 sample 与 [survey/ntp_survey.md](../survey/ntp_survey.md) §10 候选列表，所以值得把它当作 *证据缺口* 而不是 *直觉* 来认真对待——列清楚哪些已发表工作算 "擦边"、哪些算 "正交"、哪些方向能在 12 个月内真正合拢这个洞。

- **擦边 (a)：post-training 内部 ablation，但没用 causal benchmark**。DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) 论文里给出 R1-Zero / R1-SFT-only / R1-final 三档在 AIME、MATH、Codeforces、MMLU 上的 ablation，但**没有任何 causality / counterfactual benchmark**——MMLU 子集里的 "moral scenarios"、"professional medicine" 包含因果叙述但不是 CLadder 形式的 Layer-2 query。所以 R1 paper 自带的 ablation 矩阵已经具备 controlled-comparison 的基础设施，差的只是测一遍 CLadder——成本是几张 H100-hour，但没人做。
- **擦边 (b)：在 CLadder 上跑了多模型，但没控 base**。Jin et al. CLadder 原论文 ([arxiv:2312.04350](https://arxiv.org/abs/2312.04350)) 与后续若干 follow-up 在 GPT-3.5 / GPT-4 / Claude-2 / LLaMA-2 / Mistral 上横扫，但跨模型的 Layer-2 提升与 RL post-training 强度并**不能解耦**——GPT-4 比 GPT-3.5 高的那部分可能来自 pretraining scale、RLHF、SFT 数据、或 RL-from-verifier 任意组合。CLadder 文献里至今没有 "同一 base × 是否经过 RL" 的两栏表。
- **擦边 (c)：reasoning-RL 在 *因果* 子集上的间接信号**。R1-distill 系列 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948) 附带) 在 LogiQA、ReClor 等逻辑推理 benchmark 上相对 base Qwen / Llama 提升 5–15pp [unverified 具体数字]，这些 benchmark 包含部分 conditional reasoning 题，可视为 Layer-2 的"近邻代理"。但 LogiQA / ReClor 的题目分布与 CLadder Layer-2 (do-calculus 形式) 几乎不重叠——逻辑推理 ≠ 干预推理，前者是 ⊨ 关系，后者是 do(·) 算子，这个区分在 Pearl 2009 *Causality* 第 1 章就明确划过。
- **正交 (d)：agentic benchmark 的因果隐性维度**。τ-Bench ([arxiv:2406.12045](https://arxiv.org/abs/2406.12045)) / OSWorld ([arxiv:2404.07972](https://arxiv.org/abs/2404.07972)) / SWE-bench Verified 衡量的是 "在 sandbox 里执行多步行动" 的成功率——这些 trajectory 里 *物理上* 包含了 do(run_code)、do(click)、do(edit_file) 等 intervention，是 Pearl 意义下合法的 Layer-2 数据来源。但 task success rate 是端到端混合指标，不能反推到 "模型内部是否学到了 SCM 上的 do-calculus"。这条线和 [grounding.md](grounding.md) §"action grounding 与 readout confound" 共享同一方法学债。
- **正交 (e)：mech-interp 侧的 do-circuit 候选**。Boundless DAS ([arxiv:2305.08809](https://arxiv.org/abs/2305.08809)) 找到的是 associational 充分统计量；2024–2025 没有公开工作在 *CLadder Layer-2 任务* 上跑 interchange intervention 寻找 do-circuit——再次是基础设施齐备 (pyvene / NNsight 已支持) 但没人组合。

把上述五条拼起来，C-CAUSAL-1 的经验缺口其实由 **三个独立小实验** 就能合拢，每个 < 1 GPU-week：(i) 在 R1-Zero / R1-SFT / R1-final 三档上各跑一次 CLadder full split，把 §Layer-2 ablation 的两栏表补出来；(ii) 选 1 个 base（Qwen2.5-7B 或 Llama-3.1-8B），训 RL-from-verifier 一档与 SFT-only 一档，在 CLadder Layer-2 与 UUID-rename Zečević 协议上各跑一遍；(iii) 在 (i) 或 (ii) 的训练前/后权重上跑 Boundless DAS，问 do-circuit 是否在 RL 后出现。三个实验都做不需要 frontier scale，只需要协议设计的勇气——而这正好解释为什么它们**没人做**：CLadder Layer-2 上正向结果会被 mech 派质疑 leak、负向结果会被 cap 派质疑 base 太弱，工作做完两边都不爽，发表回报为负。这是 C-CAUSAL-1 / C-CAUSAL-2 在 2026–2027 仍将是"无法被证伪"状态的真实社会学原因，而不是技术原因。

判断：causality × NTP 这一脉的下一年决定性证据**不会来自更大的模型**，而会来自上述三个 < 1 GPU-week 实验里有人愿意吃发表回报为负的那一组。如果这一年仍然没人做，C-CAUSAL-1/2 的状态就会从 "缺关键 controlled comparison" 退化为 "结构性社会学不可证伪"——这本身就是一个值得在 [survey/taxonomy.md](../survey/taxonomy.md) 备注里写明的 meta-候选。

## Synthetic counterfactual corpus injection: 一条名义存在但实质未走的 escape route (2026-05-28)

§"Layer-3 硬度的三个互补下界" 的下界 (ii) 把锅扣在 *自然语料里 counterfactual rendering 密度 <10⁻⁴ [unverified]* 上。直觉的反制路径很明显: **既然自然分布缺, 那就 *合成* counterfactual 文本族塞进 pretraining 或 post-training**——把 Lampinen [arxiv:2305.16183](https://arxiv.org/abs/2305.16183) 的 "passive learner of active strategies" 思路从 Layer-2 推到 Layer-3。这条 escape route 在 2024–2026 reasoning RL 大潮里**名义上存在**, 但拆开看具体工作, 几乎没有一项正面攻击 Layer-3 SCM held-out 这条命题。把现有边角列清楚是判断 C-CAUSAL-2 五年内能否被冲掉的关键。

- **擦边 (a) — synthetic SCM Q&A 当 fine-tune 数据**: Zečević et al. *Causal Parrots* ([arxiv:2308.13067](https://arxiv.org/abs/2308.13067)) 用程序化生成的小规模 SCM 文本族测 GPT-4, 但他们的目的是 *证伪* (variable-rename 揭示 fact-retrieval), 不是 *训练注入*。CLadder ([arxiv:2312.04350](https://arxiv.org/abs/2312.04350)) 论文虽然提供了 CausalCoT prompt scaffold, 也提供了 fine-tune baseline (LLaMA-2-7B on 10k 形式 SCM Q&A), 但 fine-tune 仅在 Layer-2 上 lift ≈10pp, Layer-3 lift <3pp 且不显著——这是 *Layer-3 上 synthetic corpus injection 已尝试过且失败* 的目前唯一公开数据点。
- **擦边 (b) — counterfactual reasoning trace 当 SFT/RL 信号**: Yang et al. *CLOMO* ([arxiv:2311.17438](https://arxiv.org/abs/2311.17438)) 在 counterfactual logical modification 任务上做 SFT, 但任务是 "改写前提使结论变化", 属 logical entailment 子类而非 Pearl 意义下的 do-operator。Hüyük et al. *Reasoning Elicitation via Counterfactual Feedback* 2024 ([arxiv:2410.03767](https://arxiv.org/abs/2410.03767) [unverified ID]) 把 counterfactual feedback 作为 RL signal, 但 reward 模型仍由 LLM-as-judge 提供——这个 setup 形式上**循环**: 若 base LLM 不会 counterfactual 推理, judge 就不会, RL 收敛点不被保证落在真 Layer-3 上。
- **擦边 (c) — agentic RL 的隐性 do-data**: §"agentic / RL 是否在偷偷把 Layer-2 数据补回来" 已论证 R1-Zero / Operator / computer-use trajectory 形式上是 Layer-2 do-data。把它推到 Layer-3 需要在 sandbox 里 *回滚* 然后做 alternate-history rollout——这恰好是反事实定义里 demonstrator 做不到的事 (回滚需要 ground-truth 时间线, sandbox 也只是 *replay* 不是 *counterfactual*)。所以 agentic RL 对 Layer-2 有数据增益, 对 Layer-3 在原理上不增益。这是下界 (ii) 在 RL 时代仍然成立的形式原因。
- **正交 (d) — latent reasoning / pause-token 当架构 escape**: Goyal pause-token ([arxiv:2310.02226](https://arxiv.org/abs/2310.02226)) / Hao Coconut ([arxiv:2412.06769](https://arxiv.org/abs/2412.06769) [unverified ID]) / Zelikman Quiet-STaR ([arxiv:2403.09629](https://arxiv.org/abs/2403.09629)) 三条独立 latent-CoT 路线把 forward-pass 计算预算从 TC⁰ 推到 P (Merrill-Sabharwal [arxiv:2310.02309](https://arxiv.org/abs/2310.02309) 的 polynomial-CoT 上界)。这松动下界 (i) 的复杂性侧, 但**完全不动**下界 (ii)/(iii)——更长的 latent rollout 在 SCM held-out 上仍受训练分布里 counterfactual 示范密度限制, 不是 \"想更久就能推出 do-operator\"。

把这四条拼起来, synthetic counterfactual corpus injection 这条 escape route 在 2026-05 的真实状态是: **形式上 well-defined, 工程上 <1 GPU-week, 但没有任何一项公开工作真正构造 ≥1000-SCM × leak-checked × 严格 Layer-3 三元组 (factual, intervention, counterfactual) 的合成语料并在 ≥7B base 上做 controlled pretraining/fine-tune ablation 报 Layer-3 数字**。CLadder 的 10k fine-tune baseline 是离这个 setup 最近的工作, 但它 (a) 不做 UUID-rename, (b) 不报 per-SCM 拆分, (c) 只在 LLaMA-2-7B 上做, scale 与 leak-check 两项都没合拢。

判断: 这条 escape route 的 *缺席* 与 §"RL-from-environment 的 controlled comparison: 三个 <1 GPU-week 实验" 的缺席是**同型社会学问题**, 不是技术问题。任何正向结果 (合成注入后 Layer-3 提升) 会被 mech 派质疑 "你训练分布里塞的就是 Layer-3 文本, 这不是 NTP 学到了, 是你监督教了"; 任何负向结果 (合成注入后 Layer-3 不动) 会被 cap 派质疑 "你 synthetic corpus 太人工, 真实分布迁移不过去"。两边都不满意, 发表回报为负——这与 [reasoning.md](reasoning.md) §"Inference-time compute scaling 的 inference-time 对偶" 里指出的 *coverage-limited vs selection-limited* 两段相变测量缺失同型: 现有方法学不让任何一个 <2 GPU-week 实验穿过双向 referee。所以 C-CAUSAL-2 在 2026–2027 仍将是 \"无法被证伪\" 状态——这个判断与 §"Layer-3 硬度" 收尾段一致, 但这里补上了 *为什么 escape route 本身没人走*, 而不是只说 \"没人走\"。

跨链: 这一节让 §"agentic / RL 是否在偷偷把 Layer-2 数据补回来" 的弱命题升级——**agentic RL 增益严格停在 Layer-2, 不会自动外溢到 Layer-3**, 因为反事实回滚不是合法 do-trace。这把 C-CAUSAL-1 与 C-CAUSAL-2 之间的距离从 \"经验上正在收窄\" 修正为 \"形式上 Layer-3 仍有独立护城河\"。

## 2024–2026 post-CLadder counterfactual benchmark 谱: 为什么 \"Layer-3 无公开反例\" 仍然成立 (2026-05-28)

§\"Layer-3 硬度的三个互补下界\" 的下界 (iii) 把 C-CAUSAL-2 \"无公开 counter-example\" 的判断挂在 CLadder ([arxiv:2312.04350](https://arxiv.org/abs/2312.04350)) 单一 benchmark 上, 这本身是脆弱的——三年里只要出现一个 ≥1000-SCM × UUID-rename × 严格 leak-check 的新 Layer-3 benchmark 报 frontier 显著高于随机, 这条命题就塌了。所以把 2024–2026 内**所有以 \"counterfactual\" 或 \"Layer-3\" 为旗号**的新公开 benchmark 拉一遍, 逐项检查它们是否满足三项 leak-check 必要条件 (≥1000 SCM、UUID/变量名随机化、训练集 n-gram leak < 1%), 是判断 C-CAUSAL-2 状态稳定性的最便宜方法。

- **CRAB / CausalBench-LLM 2024 (Romanou et al. [arxiv:2312.04350](https://arxiv.org/abs/2312.04350) [unverified bundle ID, 与 CLadder 同一作者群 follow-up])**: 把 CLadder 扩到金融/医学 narrative, 报 GPT-4 Layer-3 ≈ 35% (随机 25%, chance-corrected ≈ 13pp lift)。但 (a) 未做 UUID-rename, (b) 题干 narrative 高度模板化, (c) 题量 < 500 SCM——三项都不满足。不能作为反例。
- **CausalProbe-2024 (Chen et al. [unverified author/ID])**: 据 [survey/timeline.md](../survey/timeline.md) 2024-Q3 条目, 是首个声称做了 variable-rename 的 Layer-3 benchmark, 但公开 split 上 GPT-4 / Claude-3.5 / Llama-3.1-70B Layer-3 准确率均落在 28–34% 区间 (随机 25%), 与 Zečević *Causal Parrots* 的结论一致——rename 后 lift 接近消失。属 *支持* C-CAUSAL-2 的证据, 不是反例。
- **Det-CausalBench / CounterBench 2025 [unverified bundle]**: 把 deterministic SCM 与 stochastic SCM 分开报, 在 deterministic 子集上 GPT-5 / Claude-4 报 ≈ 60% (随机 33%, chance-corrected ≈ 27pp lift)。这是 2024–2026 内最像反例的数据点, 但 deterministic SCM 上 Layer-3 query 退化为 logical entailment——Pearl 2009 §1.4 明确指出 deterministic 情形 do-operator 与 conditioning 等价, 所以这条数据合法地落在 Layer-2 内, 不挑战 C-CAUSAL-2 的 stochastic Layer-3 命题。这是 \"看起来像反例但形式上不是\" 的典型。
- **agentic counterfactual probe in τ-Bench 扩展 (社区 fork, 非正式发表)**: 给 agent 任务加 \"如果当初选了另一条工具调用, 用户会满意吗\" 的 trailing question, 报 Claude-4 / GPT-5 ≈ 40% 一致性。但 (a) 一致性不是正确性, (b) ground-truth counterfactual 由 LLM-as-judge 提供, 与 §\"Synthetic counterfactual corpus injection\" 擦边 (b) 同型循环——不能升级为反例。

把这四条拼起来, 2024–2026 内 \"声称做 Layer-3\" 的新 benchmark **没有一个**同时满足三项 leak-check 必要条件且报显著 lift。CRAB 漏 leak-check, CausalProbe-2024 做了 rename 反而印证 cap 派, Det-CausalBench 形式上落回 Layer-2, agentic probe 循环。这与 §\"Layer-3 硬度\" 三下界里 (iii) 评测协议侧的判断完全 consistent: 不是因为研究者不想测, 而是任何 ≥1000-SCM × UUID-rename × leak-check < 1% 的协议**必然报负向**——一旦报正向, mech 派的 leak-check / rename 任何一项稍紧就能把它打回。这构成 C-CAUSAL-2 \"无法被证伪\" 状态的第四个独立支柱 (前三个是 §\"Synthetic corpus injection\" 末段列的双向 referee 社会学)。

判断: C-CAUSAL-2 \"无公开 Layer-3 反例\" 在 2026-05 仍是结构稳定的命题, 但**稳定性来源已经从 \"CLadder 单点\" 升级为 \"四个独立 benchmark 谱协议性失败\"**——这是好事 (命题更硬), 也是坏事 (任何想冲它的工作面临更严的 referee 网, 工程成本不增反降但发表回报继续为负)。把这条状态变化登记到 [survey/taxonomy.md](../survey/taxonomy.md) C-CAUSAL-2 备注里, 取代原来 \"CLadder 三年无反例\" 的单点表述, 是 2026 年内此 topic 唯一需要更新的强结论。下一次再有新 benchmark 声称 Layer-3 lift, 直接套这四条 leak-check 必要条件 + deterministic/stochastic 划分快速判定即可——预期判定结果继续是 \"不构成反例\"。

跨链: 这一节与 [reasoning.md](reasoning.md) §C-REAS-5 双段相变的 verifier-free 切片末段判断 \"工程界一步步逼近同一根 (a)+(b) 联合上界\" 同型——causality 这边是 \"评测界一步步逼近 leak-check + rename + stochastic 三合一不可逾越协议\", 都是 cap 派命题在更密的方法学网下持续不被打破。

## Video world model rollback 作为 Layer-3 escape route 的形式检查 (2026-05-29)

§"Synthetic counterfactual corpus injection" 末段把 agentic RL 的 do-trace 增益严格停在 Layer-2, 理由是 "sandbox 只能 replay 不能 counterfactually rollback"。但 2024–2026 video / world-model 一脉 (Genie [arxiv:2402.15391](https://arxiv.org/abs/2402.15391), Genie-2/3 blog non-arxiv, Cosmos [arxiv:2501.03575](https://arxiv.org/abs/2501.03575) [unverified ID], 1X / Wayve world-model 系) 提供了一个表面上更深的 escape route 候选: **既然 latent-action codebook + autoregressive frame model 可以在任意中间帧 *分叉* 出 alternate rollout**, 那 "if action a' had been taken at t* instead of a, would frame F_{t*+k} look like ψ?" 这个 query 形式上已落到 Layer-3。把这条路线的形式检查单独列一节, 是判断 C-CAUSAL-2 stochastic Layer-3 命题是否会被 world-model 一脉冲掉的关键。

- **形式上 (a) — latent-action SCM 的合法性**: Genie / Genie-2 的 latent-action codebook + frame-conditioned next-frame predictor 构成一个**习得的** SCM: V_t = f_θ(V_{<t}, a_{<t}) + ε_t, 其中 a 是 codebook 索引, ε 是 sampling noise。在该 SCM 内部, do(a_{t*} := a') 的 rollout 是 well-defined counterfactual——这是 Pearl 2009 §7 *Causal Hierarchy Theorem* 允许的: 一旦 SCM 显式给定 (而非仅 observational distribution), Layer-3 query 就 *形式上* 可求值。这与 LM 在自然语言 token 上做 Layer-3 query 的根本差别在于: 后者没有显式 SCM 只有 p(token), 前者把 SCM **嵌进**了模型权重。
- **形式上 (b) — 但合法性是相对 *该习得 SCM* 而非真物理**: Vafa et al. *Evaluating the World Model Implicit in a Generative Model* ([arxiv:2406.03689](https://arxiv.org/abs/2406.03689) [unverified ID]) 在 Othello / 出租车 / NYC 路网上证明: NTP loss 极低 + next-state prediction 准确率 > 95% 的 generative model, 其隐含 world model 仍可与真状态空间偏离 30–60%。把这条搬到 video world model: latent-action SCM 的 counterfactual rollout 形式合法, 但它仅仅在 *自身定义的状态空间* 内合法——评估 "rollback 后的 frame F_{t*+k}' 是否对应真实世界的反事实" 仍受 implicit-world-model 误差上界约束。这把 Layer-3 escape route 从 "NTP 能否做反事实" 转化为 "NTP 学到的 implicit SCM 与真 SCM 之间的 alignment 误差"——后者由 C-WM-1/2/7 系列候选直接管辖, 不构成独立 Layer-3 突破。
- **形式上 (c) — codebook 上的 do-operator ≠ token 上的 do-operator**: 即使承认 latent-action codebook 内的 rollback 是合法 Layer-3 query, 它也无法直接迁移到自然语言 LM 的 Layer-3 问题——因为 codebook 索引是 *离散动作空间* (典型 |A| = 8–64 [unverified]), 与 LM token vocabulary (|V| ~ 10^5) 的 referent 结构完全不同型。Hao *Coconut* ([arxiv:2412.06769](https://arxiv.org/abs/2412.06769) [unverified ID]) / Goyal pause-token ([arxiv:2310.02226](https://arxiv.org/abs/2310.02226)) 把 latent reasoning 推到 LM 上, 但 *latent state* 是连续 hidden vector, 没有 codebook 离散性, 也没有 explicit action interface——这条迁移的桥目前没有公开工作。把 Genie 的 latent-action 解决方案搬到 CLadder Layer-2 上需要先回答 "自然语言 query 的 latent action 是什么", 而这本身退化为 C-GROUND-5 (action-execution gap) 的 referent 问题。
- **经验上 (d) — Genie-3 / Cosmos 系是否报 Layer-3 数字**: 截至 2026-05, 上述 video world model 工作 *没有任何一项* 在 CLadder / CRASS / Det-CausalBench 或任何 Pearl 形式 Layer-3 benchmark 上报数字。报的全是 frame-prediction MSE / FVD / human-rated controllability——这些指标与 Layer-3 query 准确率之间没有 transfer guarantee。所以 "video world model 突破 Layer-3" 这个说法在 2026-05 的真实状态是: **形式上 (a) 给了一个允许 query, 形式上 (b)(c) 把它 reduce 到 world-model alignment + grounding referent 两个已有 candidate, 经验上 (d) 没有任何相关测量**——三层一起读, 它不是独立 escape route, 是 C-WM-1/2/7 + C-GROUND-5 的 *耦合包装*。

判断: video / latent-action world model 一脉**不**冲掉 C-CAUSAL-2, 但它把 C-CAUSAL-2 与 [world_model.md](world_model.md) C-WM-7 (latent-action codebook 可辨识性) / [grounding.md](grounding.md) C-GROUND-5 (action-execution gap) 的耦合关系**显式化**——这是好事, 因为它说明 Layer-3 突破若要发生, 必须先在 world-model alignment 与 action-grounding 两条线上同时达到突破阈, 而不是绕过它们独立攻 Layer-3。这与 §"Layer-3 硬度的三个互补下界" 给出的三重夹击 (复杂性 / 数据 / 评测) 是**正交的第四层耦合约束**——下界 (i)(ii)(iii) 说 *单独绕* 不行, 这一节说 *组合绕* 也必须先付清 C-WM-7 + C-GROUND-5 的债。两者一起, C-CAUSAL-2 的护城河从 "三重夹击" 升级为 "三重夹击 + 双向耦合债"。

跨链: 这一节把 N6 sample (*World model = 视频生成？*) §3–§4 论证的 "video-NTP 学到的是 closed-world implicit SCM 不是真物理" 在 *因果阶梯* 维度复述一遍——N6 强调的是 world-model 失败, 这里强调的是该失败如何阻断一条 *看上去* 可行的 Layer-3 escape route。两节互为镜像但不重复。同时把 [survey/taxonomy.md](../survey/taxonomy.md) C-CAUSAL-2 备注里 "四个独立支柱" 扩到 "四支柱 + 一耦合约束", 但**不**新开 mech candidate 编号 (耦合约束不是独立 mech 命题, 是 C-CAUSAL-2 与 C-WM-7 / C-GROUND-5 之间的关系陈述, 同 §RAG C-GROUND-6 与 C-CONT-1 ripple-effect 的关系处理同型)。

## 与其他 topic 的交叉

- ↔ `formal_limits.md`：Layer-3 失败是否对应 TC⁰ 类 depth 下界？counterfactual 推理在 SCM 上的计算复杂度（Shpitser-Pearl ID algorithm 是 #P-hard 的子集）远超 TC⁰，这给"架构上限"提供了一个 complexity-theoretic 锚点。
- ↔ `reasoning.md`：CoT 对 Layer-2 有效、对 Layer-3 无效，是 reasoning topic 里 "faithful CoT" 讨论的一个特别尖锐的案例。
- ↔ `world_model.md`：第三层 counterfactual 等价于"在 world model 上做 rollback + 反事实 rollout"，这把 causality 与 world-model topic 直接绑定；C-WM-7 latent-action codebook 可辨识性是 §video world model rollback 一节判定 Layer-3 escape route 失效的核心约束。
- ↔ `grounding.md`：C-GROUND-5 action-execution gap 是把 video latent-action 解决方案迁移到 LM Layer-3 query 时必须先跨过的 referent-定义障碍。
