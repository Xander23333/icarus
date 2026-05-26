# World Model & Planning

> JEPA、Dreamer、latent dynamics、model-based RL — 以及一个更尖锐的问题：**next-token prediction 在多大程度上 *被迫* 学到一个可用的世界模型？**

## 核心问题与 NTP 假设

"world model" 这个词在 2024–2026 的文献里至少有三种互不兼容的用法，混着用是当前讨论最大的污染源：

1. **行为主义版本**：模型能在新环境里规划出有效动作序列（Dreamer 系、MuZero、Genie 2）。
2. **表征版本**：模型内部状态里存在与外部世界状态同构的可线性解码的变量（Othello-GPT、Emergent World Representations 系列）。
3. **反事实/因果版本**：模型能正确回答 "if I had done X instead, what would have happened" — 即 Pearl Layer 2/3（见 [causality](causality.md)）。

NTP 视角下，最值得问的不是 "LLM 有没有 world model"，而是 **"NTP loss 这个目标函数，对哪一种 world model 提供了选择压力？"** 默认假设：NTP 强烈选择第 2 种（够预测下一 token 的最小充分统计量），偶然挤出一点第 1 种（在 trace 足够密时），几乎完全不选择第 3 种。

## 关键证据线 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 |
|---|---|---|---|
| 2018-03 | Ha & Schmidhuber, *World Models* ([arxiv:1803.10122](https://arxiv.org/abs/1803.10122)) | 把 VAE+RNN 当做 latent dynamics，再在其中训练 controller。第一次把 "world model" 作为可训练模块明确提出 | 框架，非 NTP |
| 2019-12 | Hafner et al., *Dreamer* ([arxiv:1912.01603](https://arxiv.org/abs/1912.01603)) → DreamerV3 ([arxiv:2301.04104](https://arxiv.org/abs/2301.04104)) | 同一套 latent imagination 在 150+ 任务上 zero hyperparameter tuning。证明 **predict-next-latent** 这个目标在小规模 RL 上够用 | NTP-类（next-latent，非 next-token） |
| 2022-10 | Li et al., *Emergent World Representations* — Othello-GPT ([arxiv:2210.13382](https://arxiv.org/abs/2210.13382)) | 一个只看 Othello 棋谱 (PGN 序列) 训练的 GPT，内部线性可解码出棋盘状态。Hazineh 2023 ([arxiv:2309.07815](https://arxiv.org/abs/2309.07815)) 与 Nanda et al. ([arxiv:2309.00941](https://arxiv.org/abs/2309.00941)) 后续把这个可解码性强化到 "线性 probe 1.7% 错误率" | mech：NTP 在 closed-world 下被迫学世界模型的最干净证据 |
| 2023-06 | LeCun, *A Path Towards Autonomous Machine Intelligence* (position paper, 已更新到 v2) | 论证 NTP/自回归 *不可能* 通向 robust world model，必须 JEPA + energy-based + non-generative | 反方旗手 |
| 2024-02 | Vafa et al., *Evaluating the World Model Implicit in a Generative Model* ([arxiv:2406.03689](https://arxiv.org/abs/2406.03689)) | 提出 Myhill–Nerode-style 度量：在纽约出租车路线、Othello、逻辑谜题上发现 LLM 能预测下一步但 *内部状态图* 与真实状态图不同构（"它走对了路但脑子里的地图是错的"） | NTP 选不出第 2 类的强反例 |
| 2024-02 | DeepMind, *Genie* ([arxiv:2402.15391](https://arxiv.org/abs/2402.15391)) → Genie 2 (blog, 2024-12) | 从 unlabeled video 学 latent action + dynamics，可生成可玩 3D 环境。video-NTP 的 world-model 副产物 | mech 候选 |
| 2024-06 | Bachmann & Nagarajan, *The Pitfalls of Next-Token Prediction* ([arxiv:2403.06963](https://arxiv.org/abs/2403.06963)) | "teacher-forcing" 在简单 path-finding 任务上学不到正确世界模型——即便测试分布与训练完全一致 | NTP 局限的形式化反例 |
| 2024-10 | Ruoss et al., *Grandmaster-Level Chess Without Search* ([arxiv:2402.04494](https://arxiv.org/abs/2402.04494)) | 270M Transformer 在 chess action prediction 上 2895 Elo，无显式搜索 | 弱 mech：是否真有世界模型 vs. 只是把 Stockfish 蒸馏成 policy 仍有争议 |
| 2025-01 | DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) 等 reasoning model | 把 "world model" 部分外包给推理时显式 trace。模型不需要内部完整状态机，只需要把状态机 *写在 scratchpad 上* | 改变了赌注：external state vs. internal world model |
| 2025-09 | Wang et al., *Do Language Models Have a Common Sense of the World?* (NeurIPS 2025, [unverified ID]) | 在 ~1k 物理直觉 minimal pairs 上测前沿模型，GPT-5 / Claude 4.5 仍在 "容器漏水"、"绳子被切" 等基本因果上系统失败 | NTP-grounded world knowledge 的 ceiling 证据 |

## 当前最强的 mech 候选

**C-WM-1: Closed-world bottleneck principle.** 当生成序列的真实数据生成过程是一个 *小* 状态机（Othello 64 格、chess 64 格、迷宫几十节点），且训练数据覆盖足够多的转移，NTP loss 的最优解必须在隐状态里编码该状态机的一个充分统计量——否则下一 token 的条件熵无法降到 Bayes 下界。Othello-GPT 与 chess-Transformer 是这条原理的两个干净实例。**可证伪条件**：找到一个 closed-world 序列任务，训练损失达到 Bayes 下界，但 linear/non-linear probe 无法以高准确率恢复状态。Vafa 2024 部分提供了这种反例，但他们的"状态图不同构"是更弱的判据。

**C-WM-2: Open-world dilution principle.** 当真实数据生成过程是开放世界（自然语言 trace、互联网文本），NTP loss 只对 *与下一 token 相关的* 世界变量提供选择压力，而开放世界里绝大多数变量对任一具体 token 的边际信息量极低。结果是 LLM 学到的是 **"context-conditional next-token surface statistics"**，叠加少量在大量上下文中被反复使用的高频世界变量（实体、时间、空间关系），而不是一个 globally coherent world model。Bachmann & Nagarajan 2024、Vafa 2024、以及一系列 physical-commonsense ceiling 论文共同支持这一点。

## 反例与上界突破

- **Genie 2 / Sora 类 video-NTP** 把"下一帧"当 token，挤出来的 latent dynamics 在短时间尺度上对刚体、流体、光照确实成立。这是 NTP 选第 1 类 world model 的最强证据，但目前的所有公开 demo 都在 10–20 秒后开始 *物体永恒性失败*（物体凭空消失/复制），说明压力够强地在帧级，不够强地在 object-level 长时序。
- **Reasoning model 把状态外置** 是 C-WM-2 的 escape hatch：与其逼内部学 world model，不如让模型把当前状态显式写出来。R1 / o3 在 ARC-AGI、AIME 上的提升大半来自这条。代价是 inference cost 与 trace 可读性，以及对 "scratchpad 是否忠实反映内部计算" 的怀疑（见 Turpin et al. 2023, [arxiv:2305.04388](https://arxiv.org/abs/2305.04388)）。

## 诚实判断

到 2026 年 5 月为止，三种 "world model" 的 NTP 兼容性大致是：第 2 种（表征同构）在 closed-world 上 *被证明存在*，在 open-world 上 *被证明稀疏且碎片化*；第 1 种（行为规划）目前最好的实例不是 LLM 而是 DreamerV3 与 MuZero 这类专用 model-based RL，video-NTP 是有希望的旁支；第 3 种（反事实/因果）几乎没有 NTP 自发挤出的证据，必须靠显式 reasoning trace 外接（见 [causality](causality.md) §C-CAUSAL-1）。

把这三件事混着说 "LLM 有/没有 world model" 是当前 discourse 最大的浪费。下一个真正能推进的实验是：在一个 *中等复杂度* 的 open-world 子集（比如 NetHack、Minecraft 文本子集、或可验证的城市路径数据）上，同时跑 NTP-only、NTP + Dreamer-style latent loss、NTP + 显式 state annotation 三个 setup，比较 probe accuracy 与 OOD 规划性能。已有零散工作但还没有公认 benchmark。

## Cross-links

- [causality](causality.md) — 第 3 种 world model 与 Pearl Layer 2/3
- [grounding](grounding.md) — world model 需不需要 sensorimotor 接地
- [embodiment](embodiment.md) — Genie / robotics 路线
- [reasoning](reasoning.md) — reasoning trace 作为外置 world model
- 候选 mech 入口：`survey/taxonomy.md` C-WM-1, C-WM-2
