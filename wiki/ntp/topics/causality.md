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

## 与其他 topic 的交叉

- ↔ `formal_limits.md`：Layer-3 失败是否对应 TC⁰ 类 depth 下界？counterfactual 推理在 SCM 上的计算复杂度（Shpitser-Pearl ID algorithm 是 #P-hard 的子集）远超 TC⁰，这给"架构上限"提供了一个 complexity-theoretic 锚点。
- ↔ `reasoning.md`：CoT 对 Layer-2 有效、对 Layer-3 无效，是 reasoning topic 里 "faithful CoT" 讨论的一个特别尖锐的案例。
- ↔ `world_model.md`：第三层 counterfactual 等价于"在 world model 上做 rollback + 反事实 rollout"，这把 causality 与 world-model topic 直接绑定。
