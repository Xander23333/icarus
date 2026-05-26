# Grounding

> Symbol grounding, multimodal grounding, referent 锚定。LLM 的 token 究竟"指向"什么？

## 核心问题与 NTP 假设

Symbol grounding problem 最早由 Stevan Harnad 在 1990 年的 *Minds and Machines* 上提出 ("The Symbol Grounding Problem")：一套封闭的符号系统如果只通过别的符号定义符号，最终会陷入循环字典——一个不识中文的人拿到一本中文-中文字典永远学不会中文。Harnad 的解药是让至少一部分符号"接地"到非符号的感觉-运动表征。三十多年后，这个问题以一种几乎相同的形态回到了 LLM 时代：next-token-prediction 训练目标只看 token-token 共现，从未要求模型把 "cat" 这个 token 锚定到任何外部 referent。

NTP-mech 阵营在 grounding 上的强主张通常包含三条：

1. **形式封闭性**：纯文本 NTP 在原理上不可能区分两个外延不同但分布完全相同的世界（Bender & Koller 2020, ACL "Climbing towards NLU: On Meaning, Form, and Understanding in the Age of Data" 的章鱼实验）。
2. **referent 缺失**：即使加上图像/音频模态，CLIP-style contrastive objective 学到的也是"co-occurrence in caption-image pair"，而非真正的指称关系（Mollo & Millière 2023 称之为 *vector grounding problem*）。
3. **行为可分性**：grounded 与 ungrounded 模型在某些"反事实指称"任务上必须分裂——否则 grounding 是空假设。

NTP-cap 阵营的回击是：(a) 分布信号本身就包含大量被低估的 grounding 信息（distributional grounding，Patel & Pavlick 2022 ICLR "Mapping Language Models to Grounded Conceptual Spaces" 显示纯文本 LM 在 color / direction / spatial 子空间能用极少 anchor 对齐到 grounded 表征 [unverified ID]）；(b) multimodal pretraining 已经在 referent 任务（VQA-grounded、RefCOCO、ScanRefer）逼近人类。

这个 topic 的目标是：把"grounding 在 LLM 上是真问题还是哲学问题"这一长期口水仗，转成一组**可被实验证伪**的具体子断言。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 1990 | Symbol Grounding Problem (Harnad) | 纯符号系统无法 escape 字典循环，必须 anchor 到非符号表征 | mech (philosophical prior) | *Physica D* 42, non-arxiv |
| 2020-04 | Experience Grounds Language (Bisk, Holtzman, Thomason, et al.) | 提出 World Scopes (WS1 corpus → WS5 social interaction) 五级语料层次；指出纯文本停在 WS2 | mech (framework) | [arxiv:2004.10151](https://arxiv.org/abs/2004.10151) |
| 2020-07 | Climbing towards NLU (Bender & Koller, ACL) | 章鱼思想实验：分布信号原则上无法恢复 meaning = ⟨form, communicative intent⟩ 的 intent 分量 | mech | ACL 2020 anthology, non-arxiv |
| 2021-02 | CLIP (Radford et al.) | 4 亿图文对 contrastive 训练拿到 zero-shot ImageNet 76.2%；被广泛误读为 "grounding solved" | cap | [arxiv:2103.00020](https://arxiv.org/abs/2103.00020) |
| 2022 | Mapping LMs to Grounded Conceptual Spaces (Patel & Pavlick, ICLR) | 纯文本 GPT-3 在 color/direction 子空间能用 ~10 anchor pair 线性对齐到 grounded coords | cap (weakens strong-mech) | [unverified ID] |
| 2023-04 | The Vector Grounding Problem (Mollo & Millière) | 区分 5 种 grounding（referential, sensorimotor, relational, communicative, epistemic）；论证 RLHF 提供的是 *referential* grounding 的弱形式 | mech (taxonomy) | [arxiv:2304.01481](https://arxiv.org/abs/2304.01481) |
| 2023 | Symbols and grounding in large language models (Pavlick, Phil Trans R Soc B) | 实证综述：LLM 内部表征在多个 modality 上与 grounded 表征同构度高于随机 baseline 但低于 multimodal 模型 | cap (empirical) | non-arxiv |

> 注：本表为最小可引用集合，不追求完整。daily pipeline 后续会自动追加 2025–2026 的 grounding-relevant 论文（VLA 路线对 grounding 的隐含赌注另见 `embodiment.md`）。

## 当前共识 / 争议

- **共识 (弱)**：Harnad-Bender 强 mech 论点在"完全纯文本 LM、零 RLHF、零 multimodal" 这个极端 setting 下大致成立；问题是这个 setting 自 2022 年起已不存在于 frontier model。
- **共识 (中)**：现代 LLM 至少拥有 Mollo & Millière 分类中的 *relational* grounding（token 间结构关系正确）和部分 *referential* grounding（RLHF 期间人类标注提供了 token↔ 世界事件的稀疏对齐信号）。
- **争议**：sensorimotor grounding 是否能仅通过"看视频 / 读人类描述动作的文本"获得，还是必须 closed-loop interaction？这条线和 embodiment topic 高度耦合。
- **方法论争议**：用 probing classifier 测出来的"grounded 子空间"到底是模型真的 ground 了，还是 probe 自己在学映射？Hewitt & Liang 2019 "Designing and Interpreting Probes with Control Tasks" (EMNLP) [unverified ID] 的 selectivity 标准在 grounding 文献里被严重低估。

## NTP-mech 候选条目

**C-GROUND-1 (referential closure)**：存在一类"纯反事实指称"任务 T，使得 ∀ 仅在 text-only NTP 上训练的模型 M，pass@k(T, M) ≤ chance + ε，而同等容量的 multimodal/embodied 模型 pass@k(T, ·) ≥ 0.5。

- 反例条件 (falsifier)：找到一个 text-only NTP 模型在 T 上 ≥ 0.5。
- 当前状态：T 的标准化定义本身就有争议；Patel & Pavlick 的结果给出了**反向**证据（在 conceptual space 类 T 上 text-only 已经显著超 chance）。该条目当前评估为 **weak**，需要把 T 严格限制到 *deictic* / *novel-object* 子集才有救。

**C-GROUND-2 (RLHF as sparse referent injection)**：RLHF 通过 reward model 把人类对"输出是否对应真实世界事实"的判断注入梯度，等价于在 token-token 共现矩阵之外，新增了一条 token ↔ world-state 的稀疏监督信号。该信号的有效 bit/参数 量级远低于 pretraining，但解释力可能不成比例。

- 可测量 proxy：base model vs RLHF model 在 TruthfulQA / SimpleQA 上 gap 中，**多少**能用 "更精确的 token grounding" 解释，多少能用 "更好的指令跟随" 解释？目前文献几乎没区分这两者。

## Open problems

- 把 Mollo & Millière 的 5 类 grounding 落到**具体 benchmark**：每一类至少配一个 ≥ 1k 样本、能在 frontier model 上跑出 < 1.0 的 eval。当前缺 *epistemic grounding* (模型是否知道自己知不知道) 的标准评测——SimpleQA / SelfAware 是最接近的，但都未明确标 grounding 维度。
- 严格区分 grounding 与 hallucination：所有 hallucination 都是 grounding 失败，但反之不必然（一个 fully grounded 模型仍可以撒谎）。当前文献把两者混为一谈。
- VLA / embodied 路线（π₀、OpenVLA、RT-2）是否真的把 token grounding 推进了一步，还是只是在"被 ground 过的 caption"上做 imitation？需要 closed-loop counterfactual 测试 (见 `embodiment.md`)。
- distributional grounding 的上界：纯文本 LM 在哪些 modality 上能渐近达到 multimodal 模型？哪些根本达不到（候选：颜色 OK，3D 空间 OK 但慢，触觉/嗅觉 几乎不可能）？

## 与其他 topic 的交叉引用

- `embodiment.md`：sensorimotor grounding 的 closed-loop 检验
- `causality.md`：referential grounding 是 Pearl 因果阶梯 L1 (observation) 的必要前置——如果 token 不指向稳定 referent，干预 do(X) 在 token 空间里就无意义
- `formal_limits.md`：grounding 与 TC⁰ 上界正交——增加 modality 不改变 depth，但改变 readout label space
- `world_model.md`：world model 需要 grounded token 作为状态变量；否则只是 textual rollout

---

*最后更新：2026-05-26 by NTP-Deepen cron tick (task type B).*
