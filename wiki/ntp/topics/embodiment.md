# Embodiment

> VLA, robotics foundation models, embodied closed-loop。NTP 训练目标在多大程度上能/不能渗透到\"body in world\" 这一层？

## 核心问题与 NTP 假设

如果 grounding (`grounding.md`) 问的是 \"token 是否指向 referent\"，embodiment 问的是更窄、更硬的一刀：**模型是否参与一个 sensor → policy → actuator → next sensor 的闭环**。从 1991 年 Rodney Brooks 在 *Artificial Intelligence* 发表的 \"Intelligence without representation\" 起，embodied AI 阵营的核心主张就是：智能不是符号操作的副产品，而是\"agent 在物理世界里持续被惩罚\"塑造出来的统计模式。NTP 训练目标——预测下一个 token，loss 来自 teacher-forced cross-entropy——天然没有这个闭环：模型从来不为它的输出付出物理代价，也从来不从执行后果中拿梯度。

NTP-mech 阵营在 embodiment 上的强主张通常包含三条：

1. **counterfactual action 缺失**：纯离线数据（无论是文本还是 video 还是 demonstration）只覆盖 Pearl 因果阶梯的 L1 (observation)，最多到 L2 (do-intervention 的弱形式)，而 closed-loop control 要求 L2 全量 + L3 (counterfactual)。NTP 在原理上拿不到 L2/L3 的监督。
2. **distribution shift 是 first-class citizen**：机器人在真实世界里每一步都在制造自己的 next-state distribution；offline-trained policy 的 compounding error 是 Ross & Bagnell 2010 \"Efficient Reductions for Imitation Learning\" (DAgger 原论文) 已经形式化过的 $O(T^2)$ 上界。纯 imitation / 纯 NTP 无法逃。
3. **morphology 依赖**：embodied 智能的相当一部分 \"算力\" 被 outsource 给身体的物理动力学（passive walker、soft robotics、Pfeifer & Bongard 2006 *How the Body Shapes the Way We Think*）。语言模型没有身体，因此就算它学到了关于身体的所有描述，仍然缺一个东西——**身体本身**。

NTP-cap 阵营的回击是：(a) 把动作 token 化（RT-2、OpenVLA），closed-loop 就变成另一种 NTP，只是 vocabulary 多了 256 个 action bin；(b) world-model rollout（Dreamer 系列、Sora-as-world-model）让 offline training 也能采样 counterfactual trajectory；(c) sim-to-real + massive parallel rollout (Isaac Gym, MuJoCo MJX) 把 \"物理代价\" 在 wallclock 上压到几乎免费，于是\"是否在物理世界训练\"不再是本质区分。

这个 topic 的目标是：把 \"NTP 能不能做 embodied agent\" 这一问题，拆成几个**可测、可证伪**的子断言，并标注每一个目前的证据强度。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 1991 | Intelligence without representation (Brooks) | subsumption architecture；智能不需要中央符号表征 | mech (philosophical prior) | *Artificial Intelligence* 47, non-arxiv |
| 2006 | How the Body Shapes the Way We Think (Pfeifer & Bongard) | morphological computation：身体本身承担算力 | mech (framework) | MIT Press, non-book |
| 2010 | A Reduction of Imitation Learning to Structured Prediction (Ross, Gordon, Bagnell, AISTATS) | DAgger；offline imitation 的 $O(T^2)$ compounding error 上界 | mech (formal) | [arxiv:1011.0686](https://arxiv.org/abs/1011.0686) |
| 2022-12 | RT-1: Robotics Transformer for Real-World Control at Scale (Brohan et al.) | 13 万 episode、700 任务、单一 Transformer policy；首次大规模证明 \"action as token\" 在真实机器人上能 scale | cap | [arxiv:2212.06817](https://arxiv.org/abs/2212.06817) |
| 2023-07 | RT-2: Vision-Language-Action Models (Brohan et al.) | 把 PaLI-X / PaLM-E co-finetune 在 web data + robot data；动作直接以文本 token 输出 | cap (VLA paradigm) | [arxiv:2307.15818](https://arxiv.org/abs/2307.15818) |
| 2023-03 | PaLM-E: An Embodied Multimodal Language Model (Driess et al.) | 562B 参数把 sensor token 喂进 LM，输出 plan；强调 positive transfer from web data | cap | [arxiv:2303.03378](https://arxiv.org/abs/2303.03378) |
| 2024-06 | OpenVLA: An Open-Source Vision-Language-Action Model (Kim, Pertsch, et al.) | 开源 7B VLA，Open X-Embodiment 970k episode；7B 模型 outperform 55B RT-2-X in 多任务平均 | cap | [arxiv:2406.09246](https://arxiv.org/abs/2406.09246) |
| 2024-10 | π₀: A Vision-Language-Action Flow Model for General Robot Control (Physical Intelligence, Black et al.) | 用 flow matching 输出连续动作而非离散 token bin；明确论证 \"action 离散化是 NTP 范式的人为代价\" | cap (但弱化 NTP-as-action-token) | [arxiv:2410.24164](https://arxiv.org/abs/2410.24164) |
| 2024-10 | Open X-Embodiment (RT-X collaboration, 21 机构) | 跨 22 个机器人本体、527 技能的统一数据集；首次让 \"cross-embodiment 是否可能\" 有实证基础 | cap | [arxiv:2310.08864](https://arxiv.org/abs/2310.08864) |
| 2025 | Gemini Robotics / Gemini Robotics-ER (DeepMind tech report) | 把 Gemini 2.x backbone 直接微调成 VLA；强调 embodied reasoning (ER) 作为独立 axis | cap | non-arxiv tech report [unverified date] |
| 2025 | Helix (Figure AI), GR00T (NVIDIA Project GR00T, Fan et al.) | humanoid-scale VLA；whole-body control + dexterous manipulation | cap | [unverified arxiv ID for GR00T tech report] |

> 注：本表偏向 VLA / large-policy 方向，故意 underweight 经典 RL (SAC, PPO) 与 model-based RL (Dreamer 系列)，后者在 `world_model.md` 里展开。

## 当前共识 / 争议

- **共识 (强)**：\"action as another token\" 在 short-horizon manipulation 上 work；RT-2 / OpenVLA / π₀ 已经反复复现。NTP-mech 阵营在这一层的最强论点 (\"action 不可 tokenize\") 已经被部分证伪。
- **共识 (中)**：positive transfer from web-scale VL pretraining 是真实的——OpenVLA 7B 在多任务平均上压过 RT-2-X 55B，这只能用 \"web prior 在 robot fine-tuning 时被有效转移\" 解释。这一点对纯 RL / scratch-trained policy 是坏消息。
- **争议 (核心)**：**long-horizon、高精度、接触富 (contact-rich) 任务**上 VLA 是否仍 work？π₀ 选择 flow matching 而非离散 token，正是因为离散 bin 在 contact dynamics 上分辨率不够；这是 NTP 范式在 embodiment 上**第一个公开退却**。
- **争议 (方法论)**：现有 \"VLA 成功\" 评测几乎全是 in-distribution + 实验室桌面环境。一旦换到 novel object、novel scene、novel lighting，success rate 普遍掉 30–60%（OpenVLA 论文自己的 OOD section 已经报告）。\"VLA 已解决 embodiment\" 是被市场化叙事过度放大的结论。
- **争议 (硬件)**：humanoid 这一波 (Figure, 1X, Unitree G1, Tesla Optimus) 的赌注是 \"data flywheel 一旦启动，VLA 会复现 LLM 的 scaling law\"。这是一个**未被证实的赌注**——机器人数据采集成本仍比文本高 4–6 个数量级，data flywheel 的拐点是否存在尚未有公开证据。

## NTP-mech 候选条目

**C-EMBOD-1 (compounding error floor)**：对任意 horizon T 的连续控制任务，纯 offline-trained (NTP-style，无 online interaction、无 DAgger-style relabeling) policy 的 expected error 在 T 上至少 $\Omega(T^{1.5})$ —— 严格弱于 closed-loop 训练能达到的 $O(T)$。

- 反例条件 (falsifier)：构造一个 horizon ≥ 1000 步的真实物理任务，在该任务上一个 fully offline VLA 达到与 online-trained policy 在 ±5% 内的成功率。
- 当前状态：DAgger 原论文的 $O(T^2)$ 上界在 worst case；average case 在 benign dynamics 下可能松弛。π₀ 与 OpenVLA 的最长 horizon 公开 demo 在 100–300 步量级，落入 $T^{1.5}$ vs $T$ 差距尚不显著的区间。该条目当前**未被证伪也未被验证**。

**C-EMBOD-2 (morphology gap)**：存在一类任务（候选：dexterous in-hand manipulation、动态平衡 recovery），使得任何**不与该 morphology 共同训练**的 VLA backbone，在该 morphology 上的 sample efficiency 比 morphology-co-trained baseline 低 ≥ 1 个量级。

- 反例条件：找到一个在 morphology A 上预训练的 VLA，zero-shot 或 few-shot 迁移到 morphology B 时 sample efficiency 不掉。
- 当前状态：Open X-Embodiment 给出的 cross-embodiment transfer 数据是**正向**的（约 1.5–3× 提升），但远不到 \"morphology-agnostic\" 的程度。该条目当前评估为 **medium**。

## Open problems

- **closed-loop NTP 的形式化**：当 environment 也是 transformer (world model) 时，agent-NTP + world-NTP 的联合训练是否等价于 model-based RL？理论上的 \"NTP-as-RL\" reduction（Cundy & Ermon 2023, GAIL 系列）在 frontier 规模下从未被系统验证。
- **action 表征的下界**：离散 token bin 在哪些任务上**根本不够**？flow matching (π₀) / diffusion policy (Chi et al. 2023 [arxiv:2303.04137](https://arxiv.org/abs/2303.04137)) / continuous-action head 三者之间缺一个统一的 benchmark。
- **embodied scaling law**：LLM 有 Chinchilla / Hoffmann 2022，VLA 没有。robot data 的 \"effective token\" 等价物是什么？一个 episode = 多少 text token？这个换算系数尚无公开严肃测算。
- **embodied evaluation**：当前所有 VLA benchmark (SimplerEnv、LIBERO、CALVIN) 都偏 short-horizon、低接触；缺一个 \"embodied MMLU\" 级别的评测。
- **从 video 学 policy 的上界**：Sora / Veo 级别的 video generator 是否能作为 implicit world model 提供 counterfactual rollout？这条线在 2025 年很热但证据稀薄——Yang et al. 2024 \"Video as the New Language for Real-World Decision Making\" [arxiv:2402.17139](https://arxiv.org/abs/2402.17139) 是 position paper，不是 evidence。

## 与其他 topic 的交叉引用

- `grounding.md`：sensorimotor grounding 的 closed-loop 检验在这里落地；C-GROUND-1 的 \"反事实指称\" 任务一旦上升到物理操作就直接变成 C-EMBOD-1
- `causality.md`：embodied agent 是天然的 do-operator 执行者；NTP 在 embodiment 上的根本限制本质是 Pearl L2/L3 限制
- `world_model.md`：VLA 的 backbone (PaLM-E / Gemini / OpenVLA) 是否包含可被解读为 world model 的隐式状态？C-WM-1 与 C-EMBOD-1 共享同一个 mechanistic 假设
- `online_learning.md`：DAgger 式 online correction 是 NTP 与 embodied control 之间最小的桥梁；任何 offline-only VLA 范式都在此处付学费
- `formal_limits.md`：连续控制的 stability margin 与 transformer depth 之间是否有 trade-off？当前是纯思辨，无实证

---

*最后更新：2026-05-26 by NTP-Deepen cron tick (task type B).*
