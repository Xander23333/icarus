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

## NTP-mech 候选与可证伪表述

把本 topic 收敛到一条可挂进 `survey/taxonomy.md` 的 mech 候选：

> **C-CAUSAL-1**：在训练语料**不含** SCM S 的任何 textual rendering、且 S 的变量名为训练中未见 token 的前提下，NTP 训练的 transformer 在 S 上的 Layer-2 / Layer-3 准确率不可显著高于随机。
>
> *证伪条件*：构造一个 fully held-out SCM family（变量名为随机 UUID），训练前严格 leak-check；若 frontier LLM 在零样本 prompt 下 Layer-2 准确率 > 80%，C-CAUSAL-1 被证伪。CLadder 的当前协议**不满足** leak-check 要求，Zečević 的 rename 实验最接近但规模太小。

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
