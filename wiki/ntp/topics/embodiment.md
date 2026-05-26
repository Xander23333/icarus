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
| 2026-05-26 | Capability and Robustness Cannot Both Be Free (VLA IT bound) | 任何 discrete-action VLA policy 上：capability MI + robustness MI ≤ H(task) + adversarial channel capacity；OpenVLA encoder-specific corollary 把预算压到 ~31 nats，policy 已吃满 | mech (VLA 子带；信息论硬上界) | [2605.25889](../papers/paper_notes/2026-05-28-2605.25889-vla-capability-robustness-bound.md) |
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

## 关键证据线 (chronological)

把「NTP 能不能 cover embodied agent」这条线从 1986 拉到 2026，它至少经历了三次范式翻转。每一次翻转都不是某条算法刷新 SOTA，而是 **训练目标 / 数据来源 / 评测协议** 同时被换掉。

- **1986–1991 — Rodney Brooks 的 subsumption 架构**。Brooks 在 MIT AI Lab 用 *Elephants Don't Play Chess* (1990, *Robotics and Autonomous Systems* 6(1-2)) 与 *Intelligence without representation* (1991, *Artificial Intelligence* 47) 系统反对当时 SHRDLU / Cyc 这一脉的符号 AI。核心论点：智能不来自中央表征，而来自分层 reactive controller 在物理世界里的累积选择压力。这条 prior 一直是 NTP-mech 阵营在 embodiment 上的远端思想锚——三十年后 LeCun 在 *A Path Towards Autonomous Machine Intelligence* (2022, OpenReview) 复用了几乎相同的论证骨架反对 LLM-only AGI。
- **2010 — Ross, Gordon, Bagnell (AISTATS)**，*A Reduction of Imitation Learning to Structured Prediction* ([arxiv:1011.0686](https://arxiv.org/abs/1011.0686))。DAgger 论文第一次把 offline imitation 的 worst-case 上界形式化到 $O(T^2)$，并给出 online query 把它压回 $O(T)$ 的 reduction。这一篇是后来「为什么纯 NTP 不能做长 horizon control」这一类论证的形式根。任何 2024 之后的 VLA 论文谈 compounding error，引文链最终一定回到 1011.0686。
- **2018 — Levine, Pastor, Krizhevsky et al.**, *Learning Hand-Eye Coordination for Robotic Grasping with Large-Scale Data Collection* (IJRR 37(4-5), [arxiv:1603.02199](https://arxiv.org/abs/1603.02199))。Sergey Levine 在 Google X 用 14 台机械臂跑 80 万次抓取，证明 deep policy 可以靠 self-supervised closed-loop 数据 scale——但成本是 4 个月、6 位数美元、单一桌面任务。这一篇定下了之后十年「机器人数据 vs 文本数据」成本比的下界 baseline。
- **2022-12 — Brohan et al. (Google Robotics)**, *RT-1* ([arxiv:2212.06817](https://arxiv.org/abs/2212.06817))。13 万 episode、700 任务、35M 参数的 Transformer 把 action 离散成 256 个 bin 当 token 输出。这是 NTP 范式第一次明确写出「action 也是 token」并在真实机器人上做出 multi-task 收敛——之前的工作要么 simulator-only、要么 single-task。
- **2023-07 — Brohan et al.**, *RT-2* ([arxiv:2307.15818](https://arxiv.org/abs/2307.15818))。RT-1 + PaLI-X / PaLM-E co-finetune，把 web-scale VL prior 直接迁到机器人 policy。论文最强的论据不是绝对 success rate，而是 *emergent capability*：在训练集里完全没出现的「把可乐罐推给泰勒·斯威夫特图标」类指令上，VLA 的 zero-shot 成功率显著高于纯机器人数据 baseline。NTP-mech 阵营对此最强的反驳是 **Schaeffer et al. 2023, *Are Emergent Abilities a Mirage?* ([arxiv:2304.15004](https://arxiv.org/abs/2304.15004))**——但该论文反的是 LLM 上的相变阶梯，是否能套到 VLA 的 OOD 指令理解，至今未被严肃复现。
- **2023-10 — Open X-Embodiment Collaboration (21 机构)**, *RT-X* ([arxiv:2310.08864](https://arxiv.org/abs/2310.08864))。22 个机器人本体、527 技能、970k episode 的合并数据集。第一次让 *cross-embodiment transfer* 从思辨变成可测量——结果是正向但有限的（约 1.5–3× sample efficiency 提升），远不到「morphology-agnostic foundation model」的程度。这是 C-EMBOD-2 形态依赖论的最强经验背书。
- **2024-06 — Kim, Pertsch et al. (Stanford / Berkeley / Google)**, *OpenVLA* ([arxiv:2406.09246](https://arxiv.org/abs/2406.09246))。开源 7B VLA 在 OXE 上训练后，多任务平均压过闭源 55B RT-2-X。这一篇把「VLA 是否需要 frontier-scale backbone」清晰地推到一边——答案是：在桌面 short-horizon 上不需要。但 OpenVLA 自己的 OOD section 同时给出反方向证据：novel object / novel scene / novel lighting 下 success rate 普遍掉 30–60%。
- **2024 — Chi, Feng, Du et al. (Toyota Research)**, *Diffusion Policy* ([arxiv:2303.04137](https://arxiv.org/abs/2303.04137)) + **Physical Intelligence (Black, Levine et al.)**, *π₀* ([arxiv:2410.24164](https://arxiv.org/abs/2410.24164))。两条独立路线同时指出：离散 action token 在 contact-rich / 高频控制上分辨率不够。π₀ 选 flow matching、Diffusion Policy 选去噪生成——共同点是 **放弃 "action 就是 token" 这条 NTP 教条**。这是 VLA 范式在 embodiment 上第一次公开退却，也是 NTP-mech 阵营拿到的第一份 cap 侧自我承认的证据。
- **2025 — Gemini Robotics / Helix (Figure AI) / GR00T (NVIDIA)**。三家都在赌 humanoid + foundation model + data flywheel 的组合，但截至 2026-05 没有任何一家公开过 *true zero-shot cross-task* 的 success rate 矩阵；公开 demo 全是 cherry-picked highlight reel。Tesla Optimus 在 2024-10 We, Robot 活动上的远程操控争议 [unverified 具体程度] 进一步表明：**所谓「已 deploy」的 humanoid policy 与 teleoperation 的界线在公开数据里几乎不可分辨**。

## 2026-05-27 判断

把上面这条线压成一句话：**embodiment 上 NTP-mech 派的强命题（"action 不可 tokenize"）已部分被 RT-2 / OpenVLA 证伪；但弱命题（"long-horizon contact-rich 控制 ≫ token 序列建模"）反而被 π₀ / Diffusion Policy 用工程退却侧面背书**。这与 [reasoning](reasoning.md) 上 2026-05 之后 mech 派经验论据缩水、理论论据反而加强的格局如出一辙——证据不是单调走向某一派，而是 **强命题被冲掉、弱命题被钉得更死**。

具体到三条 mech 候选：(i) **C-EMBOD-1 (compounding error floor)** 仍未被证伪——目前所有公开 VLA demo 的 horizon 都落在 100–300 步量级，恰好处于 $T^{1.5}$ vs $T$ 差距未显著的盲区，等 horizon 上到 ≥1000 步才能开始检验。(ii) **C-EMBOD-2 (morphology gap)** 被 Open X-Embodiment 部分削弱，但 1.5–3× 的 transfer 提升远不到 LLM 上 web-prior transfer 的量级，弱命题幸存。(iii) 新增候选 **C-EMBOD-3 (continuous action lower bound)**：存在一类 contact dynamics 任务，使任何 K-bin 离散 action head 在 K → ∞ 之前都给出严格高于 continuous policy 的 task-completion error 下界。Falsification: 在 contact-rich benchmark (e.g. RoboMimic Square / Threading) 上证明存在 K\* < ∞ 使 K\*-bin token policy 与 flow matching policy 在 ±2% 内匹配；2024 末的 π₀ 论文已朝反方向给出经验证据，但未做完备 ablation。

最容易被忽视的是评测协议层面的退却：所有 2024–2026 的 VLA 论文都默认 in-distribution 桌面环境，**没有一个 benchmark 在 horizon、contact、novel object、light shift 四轴同时给出 sweep**。所以「VLA scaling law」作为 LLM scaling law 的 robot 对应物，到 2026-05 为止仍是工程信念而非实证结论——这和 [scaling_limits](scaling_limits.md) §「流形扩张」里讲的 (N, D, C, precision, horizon) 多轴现象同源：embodiment 维度上至少要 (N, D, C, morphology, horizon, contact-mode) 六轴才能定义一条像样的 scaling 曲线。

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
