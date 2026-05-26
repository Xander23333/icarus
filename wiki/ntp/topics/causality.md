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

## 与其他 topic 的交叉

- ↔ `formal_limits.md`：Layer-3 失败是否对应 TC⁰ 类 depth 下界？counterfactual 推理在 SCM 上的计算复杂度（Shpitser-Pearl ID algorithm 是 #P-hard 的子集）远超 TC⁰，这给"架构上限"提供了一个 complexity-theoretic 锚点。
- ↔ `reasoning.md`：CoT 对 Layer-2 有效、对 Layer-3 无效，是 reasoning topic 里 "faithful CoT" 讨论的一个特别尖锐的案例。
- ↔ `world_model.md`：第三层 counterfactual 等价于"在 world model 上做 rollback + 反事实 rollout"，这把 causality 与 world-model topic 直接绑定。
