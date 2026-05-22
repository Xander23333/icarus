# 视频生成 = world model？（Sora / Cosmos / GAIA 路线，截至 2026-05）

> **范围**：本节专门处理一个**叙事性 + 技术性混合**的争议：**"large-scale video generation model 是不是 world model"**。代表案例是 OpenAI Sora 技术报告标题里的 "video generation models as world simulators"，NVIDIA Cosmos World Foundation Model（WFM）的开源框架，以及 Wayve 的 GAIA-1 / GAIA-2 自动驾驶世界模型。读者 = Qwen agentic eval lead，本节不重复 C3 视频生成的 DiT 架构细节，也不重复 E1 JEPA 的 latent-prediction 路线，**只聚焦"是不是 WM、怎么测、当下到哪一步"**这三件事。截止时间 2026-05。

## 路线定位（1 段）

2024-02 Sora 技术报告标题"video generation models as world simulators"是这条叙事的起点[^sora-tr]，此后所有 video-DiT-as-WM 的论述都需要先回答两件事：(1) **生成视频"看起来对"**和 **可用于 agent planning** 是两回事；(2) **action conditioning** 是把 video gen 从 entertainment 提升到 WM 的最低门槛。截至 2026-05，"video gen = WM" 这个命题**在叙事层被 OpenAI / NVIDIA / Google DeepMind (Genie) 广泛复用**，**在技术层只在受限领域（AV、单机器人）被部分兑现**——Wayve GAIA 系列、NVIDIA Cosmos Predict + Reason 是最严肃的工程实现；Sora / Veo / Kling 在物理一致性 benchmark 上仍系统性失败（重力、刚体、流体、计数、长程因果）；LeCun 反复公开批评 "next-frame prediction in pixel space is the wrong objective"。这条路线和 E1 JEPA（latent-space prediction）、E2 Genie / Dreamer（latent dynamics + RL）构成 WM 的三种**互不兼容**的技术哲学。

## 代表事件 / 模型清单

| 事件/模型 | 日期 | 关键主张 | 一手 source |
|---|---|---|---|
| **Sora 技术报告**："Video generation models as world simulators" | 2024-02-15 | 第一次把 video DiT 公开框架成 "world simulator"；展示 emergent 3D 一致性、物体永久性、镜头运动、digital world simulation | [openai.com/index/video-generation-models-as-world-simulators](https://openai.com/index/video-generation-models-as-world-simulators/)[^sora-tr] |
| **GAIA-1**（Wayve） | 2023-09-29 (arxiv v1) / 2023-06 blog | 9B 自动驾驶 world model；text + action + video → 未来视频；首次大规模 driving-WM | [arxiv:2309.17080](https://arxiv.org/abs/2309.17080)[^gaia1] |
| **Genie 1**（DeepMind） | 2024-02-23 | latent action codebook 从无标 gameplay 视频学，"foundation world model"；2D 平台游戏 | [arxiv:2402.15391](https://arxiv.org/abs/2402.15391) |
| **Genie 2** | 2024-12-04 | 一张图 → 可用键盘交互的 3D 世界（最长 ~1 分钟） | [DeepMind blog](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/) |
| **Sora 1 GA** | 2024-12-09 | product 发布；社区独立测物理一致性，差评较多（VBench-Phys, PhysBench） | [OpenAI Sora launch](https://openai.com/sora/) |
| **NVIDIA Cosmos WFM (v1)** | 2025-01-06 (CES) | "World Foundation Model Platform"；同时放 diffusion 与 autoregressive 两条；4B/12B/14B 开源 weights；明确目标是 robotics/AV physical-AI 训练 | [arxiv:2501.03575](https://arxiv.org/abs/2501.03575)[^cosmos]；[github.com/NVIDIA/Cosmos](https://github.com/NVIDIA/Cosmos) |
| **GAIA-2**（Wayve） | 2025-03-26 | structured action conditioning（ego + 其他车 + 天气 + 国家 + 摄像头参数）；多摄像头一致；driving simulation 升级 | [Wayve blog 2025-03](https://wayve.ai/thinking/gaia-2/)；[arxiv:2503.20523](https://arxiv.org/abs/2503.20523)[^gaia2] |
| **Veo 3 / Sora 2** | 2025-05 / 2025-09 | 音视频联合；"more physical"营销话术，无系统 WM eval 披露 | C3 节已展开 |
| **Cosmos-Predict2 / Cosmos-Reason1** | 2025-06 ~ 2025-09 | Predict2 提升 instruction following 与 horizon；Reason1 引入 video → action/decision LLM | [research.nvidia.com/labs/dir/cosmos-predict2](https://research.nvidia.com/labs/dir/cosmos-predict2/)；[arxiv:2503.15558](https://arxiv.org/abs/2503.15558) (Cosmos-Reason1)[^cosmos-reason] |
| **Genie 3** | 2025-08-05 | real-time interactive world generation @ 720p/24fps，promptable events；DeepMind 明确称 "general-purpose world model" | [DeepMind blog 2025-08](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) |
| **LeCun 公开批 Sora-as-WM**（多次） | 2024-02 起 / 2024-2025 多次 talk + X | 主张 "generating pixels to predict is wasteful and wrong"；推 JEPA 替代叙事 | [LeCun X 2024-02-19 thread](https://x.com/ylecun/status/1759933365241921817)；[Lex Fridman #416 2024-03](https://www.youtube.com/watch?v=5t1vTLU7s40) |
| 2026-05 状态 | — | 三派共存：Sora/Veo（pixel WM 营销）、Cosmos/GAIA（pixel WM + action 工程）、JEPA/Dreamer（latent WM）；尚无统一 WM benchmark | — |

## 什么时候"video model 可以算 world model"？（操作定义）

这是本节核心问题。综合 Cosmos paper §1[^cosmos]、GAIA-1 §3[^gaia1]、Dreamer / MuZero 系传统定义，**一个 WM 的最低门槛**有 4 项（任一缺失就只是 video generator）：

1. **可被 action / control 条件化**。给定 `(s_t, a_t)` 必须能给出 `p(s_{t+1} | s_t, a_t)`。Sora 1 / Veo 3 不接受 action input（只接 text/image 条件），**这一项就已经失格**——OpenAI 自己在 Sora tech report 里没说它是 WM，标题用了"world *simulator*"，正文也只声称 "simulating digital and physical worlds *emerge* from training"，**这是个有意为之的弱措辞**[^sora-tr]。
2. **预测和真实环境的 dynamics 误差可被独立测量**。即必须能 rollout → 和真实数据对齐 → 给出 metric（FVD/FID 之外的物理 metric）。GAIA-1 给了 action-conditioned 重建质量；Cosmos paper §6 给了一组 Physical-AI eval（3D consistency, object permanence, gravity, rigid-body collision）；Sora tech report **没有任何定量物理 eval**——只有 cherry-picked clip。
3. **policy / planner 能从中 rollout 并改善 downstream task**。这是 Dreamer 传统的 "WM 必须能用来 plan / RL" 标准。Cosmos 通过把 WFM 接到 policy training（NVIDIA Isaac），GAIA-2 通过 driving simulation，部分满足。Sora 至今**没有任何 published 案例**显示 agent 从 Sora rollout 中学到可部署 policy。
4. **counterfactual 一致性**。同样起始状态、不同 action 必须导出**不同但物理自洽**的未来。GAIA-2 paper Figure 6 系列展示了同一 ego frame 下变更 weather / steering 的 counterfactual rollout，**这是当前公开 source 里最接近此标准的展示**[^gaia2]。

**结论性陈述（截至 2026-05）**：

| 模型 | (1) action 条件 | (2) 物理 metric | (3) 可用于 policy | (4) counterfactual | 是否算 WM |
|---|---|---|---|---|---|
| Sora 1 / 2 | 否 | 仅 cherry-pick | 无报告 | 弱 | **否，是 video simulator** |
| Veo 3 / 3.1 | 否 | 无 | 无 | 弱 | **否** |
| Genie 2 / 3 | **是**（latent action / 键盘） | 部分（interactive 一致性） | 部分（可玩） | 强 | **是**，受限 domain |
| Cosmos Predict (1/2) | **是**（action / trajectory token） | 有（Physical-AI eval） | **是**（接 Isaac policy） | 中 | **是**，physical-AI 范畴 |
| GAIA-1 / 2 | **是**（structured action） | 有（driving-specific） | **是**（Wayve 内部 sim） | **强** | **是**，driving 范畴 |
| HunyuanVideo / Wan / Kling | 否 | 无 | 无 | 弱 | **否** |

> 这张表的核心 takeaway：**"是不是 WM" 不是模型规模或视觉质量问题，是 conditioning interface + 是否定义并测量了 dynamics correctness 的问题**。Sora 没失败，它只是没有声称自己是这张表意义上的 WM——它的标题用 "world simulator" 是公关性更强、可证伪性更弱的术语。

## Cosmos WFM：把 video gen 工程化为 WM 的最严肃尝试

[arxiv:2501.03575](https://arxiv.org/abs/2501.03575)[^cosmos] §1 明确定义 WFM 是 "a generative model that, given past observations and perturbations including actions, predicts future observations"。架构上 Cosmos 同时给了两条：

- **Cosmos-Predict (Diffusion WFM)**：标准 latent video DiT（C3 节路线），但在条件输入侧暴露 **camera trajectory / robot action / text** 三类 control signal；输出仍是像素 video。规模 4B / 12B / 14B。Tokenizer 是 Cosmos 自家的 3D causal VAE，**continuous + discrete 两种**都开源。
- **Cosmos-Predict (Autoregressive WFM)**：把视频离散化为 token 序列，token-level next-token-prediction，类似 VideoPoet / MAGVIT-v2 路线；规模 4B / 12B。NVIDIA 同时押两条，是因为 AR 更容易和 LLM-style action token interleave。

**Cosmos 的 Physical-AI eval（paper §6.4）**给出了 video-WM 领域**第一个尝试系统化**的物理 benchmark：3D consistency、object permanence、gravity、collision、cloth/fluid 等子项，用 VLM judge + human rater 评分。**问题**：这套 eval **是 NVIDIA 自己提的、没有第三方独立复现**；judge 用了 GPT-4o，引入 LLM-judge 偏差。但相比 Sora 报告里的纯 demo，已是巨大进步。

**Cosmos-Reason1**[^cosmos-reason] (2025-03) 是配套的 video → text reasoning LLM，目的是给 WFM 输出补一个"semantic verifier"——这是承认 pure pixel WFM 无法独立 close loop 的信号。

## GAIA-1 → GAIA-2：domain-restricted WM 的成功配方

GAIA-1[^gaia1] 是 2023-09 第一个把 "video gen + action + text" 三模态联合在 driving 上做的 9B WM。架构：image tokenizer → 自回归 world model transformer → video diffusion decoder。**action 是连续的 steering + speed 向量**，注入到每个 timestep 的 cross-attn。Eval 是 driving-specific：lane keeping consistency、其他车辆 trajectory plausibility、weather/lighting controllability。

GAIA-2[^gaia2] (2025-03) 的关键升级：

- **结构化 action space 大幅扩展**：ego control + 其他 agent 行为 + camera intrinsics/extrinsics（多摄像头一致）+ scene-level（weather, country, time of day）。
- **multi-camera spatial consistency**：同一 scene 5 个摄像头视角联合生成，避免每个摄像头独立 rollout 漂移。
- **可控 counterfactual**：paper 展示同一起始状态变更 action / weather / country，产出**自洽且语义可控**的不同 rollout。

**为什么 driving 上能跑通而 general video gen 跑不通**：(1) 状态空间窄（道路、车、行人），物理 prior 强；(2) action space 低维明确；(3) 有大量 paired (action, video) 数据（Wayve 自有车队）；(4) eval metric 可绑定到 driving KPI。这四条在 general world 上**全部缺失**——这是 Sora 路线想做 general WM 的根本性困难。

## Sora-as-WM 的批评（LeCun 与其他）

LeCun 2024-02-19 在 X 上系列 post（[原帖](https://x.com/ylecun/status/1759933365241921817)）核心论点：

1. **"Generating mostly realistic-looking videos from prompts does not indicate a system understands the physical world."**——可生成 ≠ 可预测；可预测 ≠ 可 plan。
2. **像素空间预测在信息论上是浪费的**：高频细节、噪声、纹理对 dynamics 无关却消耗大部分 model capacity。这是 JEPA 的核心动机（E1 节展开）。
3. **缺乏 abstraction hierarchy**：Sora 没有 H-JEPA 式的层级 representation，无法做 long-horizon planning。

第三方独立验证 Sora 物理失败的工作（截至 2026-05 部分）：

- **PhysBench / VideoPhy / VBench-Physics** 等 benchmark 系列陆续发表，普遍报告 Sora / Kling / Veo 在重力、刚体碰撞、物体计数、因果链 4 类任务上 **<50% pass rate**（具体数据多 paper 间口径不一，[uncertain 引用具体一篇]）。
- Bytedance Research 2024-11 "How Far is Video Generation from World Model" 系列分析（[arxiv:2411.02385](https://arxiv.org/abs/2411.02385)），结论："current video gen models learn statistical regularities, not physics laws"。
- OpenAI 自家 Sora 2 launch[^sora2] post 也承认 "we are still far from a perfect simulator"，相对 Sora 1 的"world simulator"用词显著收敛。

## 评测 gap（写给 Qwen eval lead）

如果你要在 2026 年组织一次"video gen 是不是 WM"的独立评测，**当前 benchmark 生态的实际状况**：

1. **没有公认的 WM benchmark**。VBench、EvalCrafter 测 video quality / text alignment，不是 WM。Cosmos Physical-AI eval 是 vendor-proposed。GAIA driving eval 是 domain-specific。Dreamer 系 control benchmark（DMC、Atari100k）不接受 video-DiT 类模型。**这是个空位**。
2. **action conditioning interface 缺标准**。Sora / Veo 不暴露 action；Cosmos / GAIA 各自定义；Genie 用 latent action codebook。**评测设计要先选 conditioning 协议**。
3. **物理一致性 metric 几乎都依赖 VLM-judge**，引入 GPT-4o / Gemini 系 judge bias。**值得搞一个 rule-based / physics-engine-based 的客观 eval**（例如让模型预测一个已知物理 sim 的 rollout，对比 pixel + state divergence）——截至 2026-05 公开 source 里**没看到这种 eval**。
4. **closed-loop policy eval 几乎不存在**。最接近的是 Wayve 内部 driving sim 和 NVIDIA Isaac + Cosmos——都不开放。**这是当前 WM 评测最大的空白**，也是 agentic RL 圈最需要的能力。
5. **counterfactual eval**（同 state 不同 action → 不同 future 的自洽性）也几乎没人测。GAIA-2 paper 给了定性 figure 但没给定量 metric。

> **practical 建议**：如果 Qwen 要做 WM 相关 eval，**短期最有 ROI 的方向是接 NVIDIA Cosmos 开源 weights + 自定义 physics-sim oracle 做 closed-loop divergence eval**——这比从零造一套 video-WM benchmark 现实，且能直接对 Cosmos / 未来 Qwen-WM 类工作给可比 metric。

## 未知与争议

1. **Sora 内部是否真当 WM 用**：tech report 标题诱导，但正文措辞保守；OpenAI 2024-2026 间**没有发表过 Sora-based agent / planning 工作** [unknown — 没找到一手 source]。
2. **Cosmos 在 NVIDIA 内部的 robotics 实战采纳度**：Cosmos paper 与 Isaac 团队挂钩，但**第三方 robotics lab 用 Cosmos 做 policy training 的公开案例稀少** [uncertain，截至 2026-05]。
3. **Genie 3 的真实交互长度与一致性**：DeepMind blog 给了少量 demo，**没发 paper**，无法独立评估（截至 2026-05）。
4. **"video gen 涌现物理理解" 的强弱争议未结**：支持方（OpenAI、NVIDIA、部分 DeepMind）vs 怀疑方（LeCun、Bytedance Research、多数 robotics PI）。没有 decisive experiment。
5. **三派融合的可能性**：是否会出现 "pixel video gen backbone + JEPA-style latent predictor head + Dreamer-style RL training" 的 hybrid？截至 2026-05 **无公开尝试**。

## 推荐外部材料

- [OpenAI, "Video generation models as world simulators" (2024-02)](https://openai.com/index/video-generation-models-as-world-simulators/) — Sora tech report；要读"world simulator"用词的措辞分寸而不是当结论。
- [NVIDIA Cosmos WFM paper, arxiv:2501.03575](https://arxiv.org/abs/2501.03575) — 当前最严肃的"video-DiT 工程化为 WM"实践；§1 定义、§6 eval 必读。
- [GAIA-1 paper, arxiv:2309.17080](https://arxiv.org/abs/2309.17080) + [GAIA-2 arxiv:2503.20523](https://arxiv.org/abs/2503.20523) — domain-restricted WM 成功配方的两代演进。
- [Wayve GAIA-2 blog](https://wayve.ai/thinking/gaia-2/) — counterfactual rollout 视频比 paper 直观。
- [LeCun X thread on Sora (2024-02-19)](https://x.com/ylecun/status/1759933365241921817) — 反方最 concise 的陈述。
- [Bytedance Research, "How Far is Video Generation from World Model", arxiv:2411.02385](https://arxiv.org/abs/2411.02385) — 第三方系统性 audit 视频生成模型的物理学习上限。
- [DeepMind Genie 3 blog (2025-08)](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) — 另一条 "interactive WM" 叙事的当前最高点。
- [Lilian Weng, "World Models" (持续更新)](https://lilianweng.github.io/) — 把 Dreamer / JEPA / video-WM 三派放一起的 reference [uncertain 具体 URL，搜 "lilian weng world model"]。

---

[^sora-tr]: OpenAI, "Video generation models as world simulators", 2024-02-15, https://openai.com/index/video-generation-models-as-world-simulators/。标题"world simulator"在正文中只出现 emergent 描述，无定量物理 eval。
[^sora2]: OpenAI, "Sora 2 is here", 2025-09-30, https://openai.com/index/sora-2/。
[^cosmos]: NVIDIA, "Cosmos World Foundation Model Platform for Physical AI", arxiv:2501.03575, 2025-01-06；§1 定义 WFM 必含 action conditioning，§6.4 Physical-AI eval。
[^cosmos-reason]: NVIDIA, "Cosmos-Reason1", arxiv:2503.15558, 2025-03。
[^gaia1]: Wayve, "GAIA-1: A Generative World Model for Autonomous Driving", arxiv:2309.17080, 2023-09。
[^gaia2]: Wayve, "GAIA-2: A Controllable Multi-View Generative World Model for Autonomous Driving", arxiv:2503.20523, 2025-03。
