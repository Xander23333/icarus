# NTP Taxonomy

## 一级分类

```
NTP (Non-Tokenizable Problems)
├── NTP-mech   机制级 — 论证级别为 "无论 scale 多大都不可获得"
├── NTP-cap    能力级 — 当前训练范式未获得，但机制上不排除
└── Pseudo-NTP 伪 NTP — 数据/接口/budget 工程缺口
```

## 二级 (按能力领域)

| 大类 | 子类 | 候选 NTP-mech 论点 (待严格化) |
|---|---|---|
| Formal | Expressivity bound | 固定深度 TC⁰ 上限内的问题类 |
| Formal | Sequential computation | inherently sequential 问题在 fixed-depth 下不可解 |
| Reasoning | Faithful multi-step | CoT 与内部计算偏离 → 长链可靠性上限 |
| Reasoning | Compositional gen | 训练分布外的 systematic generalization |
| Grounding | Symbol → referent | 纯文本下的物理 referent 锚定 |
| Causality | Layer-2/3 inference | 无干预数据时的反事实预测 |
| Embodiment | Closed-loop control | 实时感知-行动闭环 |
| Online | Non-stationary adapt | 训练后真分布漂移下的持续适应 |
| World model | Long-horizon dynamics | 视频/语言序列上的长程动力学一致性 |
| Scaling | Sample efficiency floor | 某类任务存在 sample-complexity 下界 |

## 三级 (per candidate, 在 paper_notes 内单独维护)

每个候选 NTP-mech 论点维护：
- 形式陈述 (formal statement)
- 已有 lower bound 证据
- 已有反例 / 上界突破
- 当前共识强度: ★ ☆☆☆☆ → ★★★★★

## 升降级的判定规则 (grading rubric)

把一个论点从 NTP-cap **升**为 NTP-mech，须同时满足：

1. **形式陈述可在不引入未定义新概念的前提下写出**（lemma-style，不是 prose）。
2. **存在与某个已知复杂度类、信息论量或代数对象的非平凡映射**（如 TC⁰、KL Ω(H)、Pearl Layer 2/3 do-operator）。
3. **可证伪条件具体到 protocol 级**——给出一个能在 ≤1k GPU·h 内执行的实验，其结果能在该论点的成立/不成立间二分。
4. **现有反例已被显式排除**——对照 [`ntp_survey.md`](ntp_survey.md) §10 的「五道工程 confound」清单（format/readout/CE-collapse/attribute-head/representation-geometry under-constraint）逐一回应。

反过来，把一个 NTP-mech 候选**降**回 NTP-cap 的触发条件：

- (A) 某 confound 被新工作（如 [Garcia 2026](https://arxiv.org/abs/2605.10799)、ProFIL [2605.11467](https://arxiv.org/abs/2605.11467)、NITP [2605.24956](https://arxiv.org/abs/2605.24956) [unverified ID]）证明可解释观察到的 effect size 大半；
- (B) 同一现象在新旋钮上被打开（例：[Ruoss 2305.16843](https://arxiv.org/abs/2305.16843) 的随机 PE 打开 Bhattamishra 2009.11264 的 PARITY 墙；[McLeish 2405.17399](https://arxiv.org/abs/2405.17399) Abacus embedding 打开 length-extrapolation 墙）；
- (C) 形式陈述被发现 implicit 假设了某个工程默认（如 vanilla BPE、no-CoT、fixed depth），换默认后陈述失效。

降级到 Pseudo-NTP 的触发条件更严：必须证明所谓"缺失能力"在**当前**主流工程栈内已被覆盖（retrieval、tool-use、scratchpad、外部状态机），且 cost 不随 scale 发散。

## 已升降级历史 (rolling log)

| 时间 | 论点 | 旧级别 | 新级别 | 触发文献 |
|---|---|---|---|---|
| 2023 中后 | "CoT 一定不忠 → NTP 推理是表演" | NTP-mech 候选 | NTP-cap 候选 | Anthropic 2025-03 attribution graph 在 Claude 3.5 Haiku 上观察到多步算术的逐级合成 |
| 2024-06 | "fixed-depth transformer 不能数 parity" 全局命题 | NTP-mech | 条件 NTP-mech (仅 vanilla PE) | [Ruoss 2305.16843](https://arxiv.org/abs/2305.16843)、[McLeish 2405.17399](https://arxiv.org/abs/2405.17399) |
| 2026-05-26 | "CoT corruption → reasoning 是表演" | NTP-mech 候选 | 待重做 (format confound) | [Garcia 2605.10799](https://arxiv.org/abs/2605.10799) |
| 2026-05-27 | "Causal FT 失败 → NTP 学不到 causality" | NTP-mech 候选 | NTP-cap (CE-collapse 假阳性) | [Semantic-Loss Anti-Collapse 2605.05438](https://arxiv.org/abs/2605.05438) [unverified ID] |
| 2026-05-27 | "NTP local objective ⇒ 不会全局规划" | NTP-mech 候选 | NTP-cap (head 工程问题) | [Conditional Attribute Transformers 2605.14004](https://arxiv.org/abs/2605.14004) [unverified ID] |
| 2026-05-28 | "yes/no 准确率代表 causal mechanism" | 默认假设 | 已证伪 | [Causal Tongue-Tie 2605.25891](https://arxiv.org/abs/2605.25891) [unverified ID]，probe 0.97 vs output 0.5 |
| 2026-05-28 | "post-commitment CoT theater 是机制缺陷" | NTP-mech 候选 | NTP-cap (RL-readout 可修) | [ProFIL 2605.11467](https://arxiv.org/abs/2605.11467) [unverified ID] |
| 2026-05-28 | "VLA capability+robustness 总预算" (discrete-action) | 未分类 | 条件 NTP-mech (encoder-specific) | 2605.25889 [unverified ID] |
| 2026-05-28 | C5: NTP continual-learning 不动点 (streaming, no-replay, backbone) | 未登记 | Conditional NTP-mech 候选 (4 升级条件 ✅✅✅❌ — (iv)(v) confound 未排除) | N7 §3–§5 综合 (Lazaridou 2102.01951 + Kirkpatrick 1612.00796 + Lyle 2303.01486 + Dohare 2024 *Nature* + Ibrahim 2403.08763) |
| 2026-05-28 | C6: Video-NTP interventional rollout consistency (open-world Layer-2) | 未登记 | Conditional NTP-mech 候选 (4 升级条件 ✅⚠✅⚠ — 映射 non-trivial 度中等, confound (v) representation-geometry 未排除) | world_model.md §C-WM-3 综合 (Vafa 2406.03689 + Brinkmann 2402.11917 + Phyworld 2406.03520 + Kıcıman 2305.00050 + IntPhys 1803.07616) |
| 2026-05-28 | C7: Post-training compute scaling 是闭区间 + 非 NTP 子轴 (verifier-rich subset) | 未登记 | 边界 NTP-mech 候选 (taxonomy-level 争议: \"算不算 NTP\" 本身未定 — 4 升级条件 ⚠⚠✅✅, formal 化在 reward-hacking 区拐点未严格化, 与 C-SCALE-6 DPO 边界纠缠) | scaling_limits.md §C-SCALE-7 综合 (Ouyang InstructGPT 2203.02155 + Bai Constitutional AI 2212.08073 + Rafailov DPO 2305.18290 + Gao RM-overoptim 2210.10760 + DeepSeek-R1 2501.12948 + RLVR reward-hacking bundle [unverified]) |
| 2026-05-29 | C-WM-6: Head-to-head paradigm benchmark deficit (video-NTP vs JEPA-class objective, controlled 4-tuple) | 未登记 | Corollary（元-方法论 candidate, 不入 candidate snapshot 主表, 仅入升降级历史与 [`ntp_survey.md`](ntp_survey.md) §10 corollary 段） — 编号避让说明: §7 表已用 C-WM-4 标 object-permanence floor / C-WM-5 标 JEPA identifiability 局部翻盘, topics/world_model.md §NTP-vs-JEPA head-to-head 真空 节原写 C-WM-4 与之冲突, 本 tick 改为 C-WM-6 并同步三处 | topics/world_model.md §NTP-vs-JEPA head-to-head benchmark 真空 综合 (I-JEPA 2301.08243 + V-JEPA 2404.08471 + Sora 技术报告非 arxiv + VideoPoet 2312.14125 + LeJEPA 2605.26379 + SPHERE-JEPA 2605.26900) |
| 2026-05-29 | C-EMBOD-6: Demo-credibility prior (humanoid/VLA demo 视频在缺 N-trial+intervention+OOD 三元组披露下 Bayes factor ≤ 1) | 未登记 | Corollary（评测-认识论 candidate, 不入 candidate snapshot 主表, 仅入升降级历史与 [`ntp_survey.md`](ntp_survey.md) §10 corollary 段） — 与 C-WM-6 同型: 是 \"评测协议 confound\" 框架在 embodiment 维度的对偶, 形式上属 epistemic 而非物理命题, 落 corollary 不落 mech; 与 C-EMBOD-4 (capability-robustness IT 上界) 互为评测层↔形式层对偶 (前者钉最弱评测协议可信度上界, 后者钉最强评测协议下 capability 总量信息论上界); 与 reasoning §C-REAS-* 中 format-confound 不可控时 reasoning 评测应被视作零证据 同型 | topics/embodiment.md §远程操控/autonomy模糊带/demo可信度 综合 (Tesla Optimus 2024-10 We-Robot 事件 + Figure 01→02 + 1X NEO + Unitree G1 + Apptronik Apollo + π₀ task-level retry + 2605.25889 + 2605.26820 [unverified: 远程操控具体比例/Helix arxiv 状态]) |
| 2026-05-28 | C-SCALE-6 (data-quality multiplier): 单位 token 教学价值是 (raw web → tau model collapse) 闭区间 | 未登记 | NTP-cap (sub-mech) | scaling_limits.md §Data-quality scaling 综合 (Phi-1 2306.11644 + DoReMi 2305.10429 + Rephrase the Web 2401.16380 + FineWeb-Edu 2406.17557 + Model Collapse 2305.17493 + Joint-KL 2605.12316) — 决策: 不入 candidate snapshot 主表 (机制级强度不足, 与 C-SCALE-7 DPO setup 部分重叠), 仅入历史日志作 sibling-cap 备查 |
| 2026-05-29 | C-FORM-7: looped-sparse depth-gating (任何 fixed backbone + per-token (expert, recursion) 双路由, 表达力类由 $T_{\max}$ 渐近行为单一决定) | 未登记 | Sub-candidate (formal domain, 不入 candidate snapshot 主表, 仅入升降级历史与 [`ntp_survey.md`](ntp_survey.md) §10 C-FORM-7 sub-candidate sync 段) — 决策依据: 与 C-SCALE-6 / C-WM-6 / C-EMBOD-6 同型属 "机制级强度不足时仅入升降级历史日志作 sibling-cap 备查"; C-FORM-7 工程射程内 ($T_{\max}\leq 8$) 与 MoE 形式等价 (C-FORM-5 已涵盖), 越出工程射程退化为 CoT-bound (Merrill-Sabharwal 2310.07923 已涵盖), 不撑起独立 mech 命题, 但 *补全* C-FORM-1/2/5/6 联合地图中 looped-sparse 复合的形式空白 (2025 MoR / Recursive-MoE 涌现后社区直觉未对齐), 关闭 [`formal_limits.md` §Open problems](../topics/formal_limits.md) 第 2 条挂账的一半 (剩 selective-SSM × loop 复合) | topics/formal_limits.md §Looped × Sparse 复合架构 综合 (Dehghani Universal Transformer 1807.03819 + Giannou looped programmable 2301.13196 + Fan/Yang looped length-gen [unverified IDs] + MoR / Recursive-MoE [unverified bundle 2025-xx] + MoD 2404.02258 [unverified ID] 对照) |
| 2026-05-29 | C-GROUND-7: epistemic asymmetry between internal belief and output confidence (对任意纯 NTP 训练 LM 含 RLHF, 存在 atomic-claim 评估族 E 使 Burns-style probe AUC ≥ 0.8 + verbalized/logit ECE ≤ 0.05 但 probe-derived belief 与 output-derived confidence 在 contested subset 上 ρ ≤ 0.5, gap 在 7B–400B 对 N 不显著敏感) | 未登记 | Sub-candidate (grounding domain, 不入 candidate snapshot 主表, 仅入升降级历史与 [`ntp_survey.md`](ntp_survey.md) §10 C-GROUND-7 sub-candidate sync 段) — 决策依据: 与 C-FORM-7 / C-SCALE-6 / C-WM-6 / C-EMBOD-6 同型属 \"机制级强度不足时仅入升降级历史日志作 sibling-cap 备查\"; C-GROUND-7 与 C-GROUND-5 (action-execution gap) / C-GROUND-6 (RAG-injection ≠ referent stabilization) 三连组合钉 action / fact / belief 三类 token 接地缺口, 把 Mollo-Millière 2023 五分类扩到八类 (+ tool-use / + RAG / + epistemic); 镜像方向与 reasoning §readout-side 主导假设相反 (reasoning 上 verbal readout 是 confound, epistemic 上 verbal readout 反而更 calibrated, Tian 2305.14975), 这一方向反转是不能被吸入单一 readout-side 条目的形式理由; 直接部分回答 [`topics/grounding.md` §Open problems](../topics/grounding.md) 第 1 条 \"缺 epistemic grounding 标准评测\" 挂账, 剩余空白收紧为 \"probe-vs-readout 双轨 epistemic benchmark\" | topics/grounding.md §Epistemic grounding 综合 (Kadavath 2207.05221 + SelfAware 2305.18153 + Tian 2305.14975 + R-Tuning 2311.09677 + SimpleQA non-arxiv + SelfCheckGPT 2303.08896 + Burns CCS 2212.03827 + Marks-Tegmark 2310.06824 + MacDiarmid 2024 blog non-arxiv + Li 2605.26362) — falsifier 双门槛 probe AUC ≥ 0.8 *且* ρ ≥ 0.85 同时在非 \"easy factual / 高 self-consistency\" 子集上达到 |
| 2026-05-29 | C-CONT-2 / C5 falsification 条件: 从 (a) retention ≥ 99% + (b) 同语料 retrain 量级 + (c) wallclock ≤ 1/20 三元组细化为四元组 (新增 (d) replay ratio → 0 不退化) | 三元组 | 四元组 (falsifier 收紧, 非级别升降) | online_learning.md §Continual pretraining recipe 边界 综合 (Gupta 2308.04014 + Ibrahim 2403.08763 + Parmar 2407.07263 [unverified] + Hägele 2405.18392 + Roberts Gemini blog [unverified title] + Çağatan 2402.17400 + Dohare 2024 *Nature* 2306.13812) — 决策: replay → 0 退化为 fine-tune 灾难性遗忘是 CPT 三年曲线的硬常数, LoRA-merge / merging-based streaming-CPT [unverified IDs] 在固定非零 replay 下可 spoof (a)(b)(c) 三项, 必须强制 (d) 否则 mech 被假性证伪; 与 §10 readout-side 假设 (vi)(vii) 接口层补丁同型 (每一次工程修补出现, falsifier 须把对应隐藏前提显式化); C5 仍停 *Conditional NTP-mech 候选 (streaming setting)*, ✅✅✅❌ 状态不变, snapshot 表 falsification 列同步收紧描述 |
| 2026-05-29 | C-EMBOD-7: morphology-layer transfer 近零下界 (在固定 NTP 训练协议下, cross-embodiment policy 在 unseen morphology 上的 zero-shot success rate 在 ≥10 demo 校准前不显著高于 BC-from-scratch baseline, 粗估差距 ≤5 pp 绝对值; 表示层迁移 LoRA 加速真实存在但与策略 / 形态层迁移在数值上必须分开报告) | 未登记 | Sub-candidate (embodiment domain, 不入 candidate snapshot 主表, 仅入升降级历史与 [`ntp_survey.md`](ntp_survey.md) §10 C-EMBOD-7 sub-candidate sync 段) — 决策依据: 与 C-FORM-7 / C-GROUND-7 / C-SCALE-6 / C-WM-6 / C-EMBOD-6 同型属 "机制级强度不足时仅入升降级历史日志作 sibling-cap 备查"; C-EMBOD-7 不撑起独立 mech 命题, 只把 *表示层 / 策略层 / 形态层* 三层迁移 budget 拆开命名 (LLM 侧三层同步生效无需拆分, VLA 侧 2023–2026 五数据点把三层差距推到一个量级以上才形成命名必要); 与 C-EMBOD-6 互为 *能力层 ↔ 评测层* 对偶 (C-EMBOD-7 钉严格 zero-shot 物理/算法命题, C-EMBOD-6 钉单段视频 epistemic 命题), 两者合起来构成 humanoid foundation model capability claim 在 2026 的双面 evidence-bar; embodiment 域至此 sub-candidate / corollary 已三条 (C-EMBOD-5/6/7), 与 grounding 域三条 (C-GROUND-5/6/7) 形成对称 — 两域三连是 §10 sub-candidate 区在能力领域分布上首次出现, 后续任一域新 sub-candidate 须先检查是否已被覆盖避免重复登记; 部分回答 [`topics/embodiment.md` §Open problems](../topics/embodiment.md) 第二条 "action 表征下界" 从 *表示层* 推到 *形态层* 的挂账 | topics/embodiment.md §Cross-embodiment transfer / morphology generalization 实证错位 综合 (RT-X 2310.08864 §6 unseen morphology single-digit pp [unverified pp] + OpenVLA 2406.09246 §5.3 LoRA 10–150 demo 可迁但 zero-shot 新 gripper ≈0 + CrossFormer 2408.11812 [unverified ID] 三形态 unseen chance 水平 + π₀ 2410.24164 §4.2 new embodiment 仍需百-量级 demo + 2025–2026 humanoid 侧 1X/Figure/Apptronik 无任何跨厂迁移曲线公开) — falsifier: 严格 zero-shot 协议 (无该本体 demo + 无该本体 morphology embedding 微调) 下 unseen morphology success ≥ from-scratch BC + 15 pp 绝对值 且在 ≥3 个独立任务上一致 |
| 2026-05-29 | C-CAUSAL-2 evidence-base 稳定性来源: 从 "CLadder 单点三年无反例" 升级为 "四 benchmark 谱协议性失败 (≥1000 SCM × UUID-rename × leak-check<1% 三必要条件无人同时满足)" | 单点 | 四支柱 (evidence-base 内部细化, 非级别升降, 不新增 sub-candidate / corollary 槽位) | causality.md §2024–2026 post-CLadder counterfactual benchmark 谱 综合 (CLadder 2312.04350 + CRAB/CausalBench-LLM 2024 [unverified bundle, CLadder follow-up] + CausalProbe-2024 [unverified author/ID, rename 后 28–34% 落随机区 = 反向加固 cap 派] + Det-CausalBench/CounterBench 2025 [unverified bundle, deterministic 子集 ≈ 60% 但 Pearl 2009 §1.4 deterministic do=conditioning 形式落回 Layer-2 不是反例] + agentic τ-Bench causal fork 社会学 leak) — 决策: 四 benchmark 不撑起新 mech 命题, 只把 "无反例" 判断的稳定性来源从单点改为四支柱; 与 C-FORM-7/C-GROUND-7 sub-candidate sync 区别在 sub-candidate 在主表外新增一格, evidence-base refinement 只在 §4 主 evidence 表内格升级措辞 (本 tick CLadder 行从 "三年无反例" 改为 "四 benchmark 谱协议性失败"); 与 C-CONT-2 上 tick 三→四元组 falsifier 收紧同型方法学操作 (mech 命题不动, falsifier 可证伪面被工程进步反向推紧); 元意义警示: "benchmark 谱协议性失败" ≠ "NTP 真的学不到 Layer-3", 后者仍需 R1-Zero/SFT/final × Boundless DAS do-circuit 搜索 (causality.md §RL-from-environment 三个 <1 GPU-week 实验), 否则属 §9 meta-候选 "结构性社会学不可证伪" 征兆而非 mech 真信号变强证据 |

判断：本表的形状给出一个非常硬的经验观察——**升级事件极少（近三年实质只有 C1 Deterministic Horizon 与 C4 VLA 预算上界两个真正达到 conditional NTP-mech），降级事件密集**。任何还没经历过至少一次"被认真挑战、并把可证伪条件改写至少两遍"的候选，目前的默认假设应当是它会在下一个 confound 被识别后降级，而不是相反。这是 [`ntp_survey.md`](ntp_survey.md) §10 维护节奏的方法论依据。

## 当前 candidate 状态快照 (2026-05-28)

| ID | 内容 | 当前级别 | 关键 falsification | 主页面 |
|---|---|---|---|---|
| C1 | Deterministic Horizon H* ∈ [19,31] @ (L, d, tokenization) | Conditional NTP-mech (no-CoT) | 在 no-CoT / 固定 tokenization 下找到打破 H* 的任务族 | [formal_limits §C-FORM-1](../topics/formal_limits.md) |
| C2 | Hallucination ∝ (log params, log freq) sigmoid | NTP-cap | 某域内 hallucination 率随频率非单调且不能由 SNR 解释 | [scaling_limits §C-SCALE-2](../topics/scaling_limits.md) |
| C3 | Long-horizon imitation Ω(H) joint-KL 下界 | NTP-cap | 存在算法在无外部状态压缩下使 KL-error 次线性于 H | [scaling_limits §C-SCALE-1](../topics/scaling_limits.md) / [reasoning §C-REAS-3](../topics/reasoning.md) |
| C4 | VLA capability+robustness MI ≤ H(task)+adv | Conditional NTP-mech (discrete VLA) | encoder 子空间假设在 white-box 下失效 | [embodiment](../topics/embodiment.md) |
| C5 | NTP-loss continual-learning 不动点 (streaming, no-replay, backbone-weight) | Conditional NTP-mech 候选 (streaming setting) | 四元组 (a) retention ≥ 99% + (b) 同语料 retrain 量级 perplexity + (c) wallclock ≤ 1/20 + (d) replay ratio → 0 不退化 同时跨阈值 (2026-05-29 收紧, 防 LoRA-merge spoof) | [online_learning](../topics/online_learning.md) / [N7 §3–§5](../samples/N7-why-llm-cannot-continually-learn.md) |
| C6 | Video-NTP interventional rollout consistency (open-world Pearl-Layer-2) | Conditional NTP-mech 候选 (video subband) | 存在 simulator-backed counterfactual triplet $\mathcal{B}_{\text{do}}$ 使某 video-NTP 模型同权重下 $\varepsilon_{\text{do}}(M,X)\to 0$ | [world_model §C-WM-3](../topics/world_model.md) |
| C7 | Post-training compute scaling 闭区间 (verifier-rich subset only) | 边界 NTP-mech 候选 (taxonomy 级争议) | 找到 RLVR setting 使 10× C_post 与 holdout 真实 utility 同步线性, 无 reward-hacking decoupling | [scaling_limits §C-SCALE-7](../topics/scaling_limits.md) |
| — | Reversal Curse 方向不对称 | NTP-mech 候选 (待 ≥7B prefix-LM 复现) | 7B+ prefix-LM 训练消解该效应 | [reasoning §C-REAS-1](../topics/reasoning.md) |

C1 与 C4 是当前唯二写出"形式陈述 + 非平凡映射 + protocol 级 falsification + 排除五 confound"全套的候选；C5 是 2026-05-28 新登记的 streaming-setting 条件 mech 候选，形式陈述齐但 falsification protocol 中第 (iv)(v) 两条 confound 尚未排除（详见下节判例）；其余仍处于 NTP-cap 或待形式化阶段。

## 升降级判例 — C5 (continual learning) 走一遍四条升级条件

把 [N7 §3–§5](../samples/N7-why-llm-cannot-continually-learn.md) 推出的弱化命题——"在分钟级、单样本、无 replay、backbone-weight 更新的 streaming setting 下，纯 NTP-loss + dense transformer + cross-entropy 三件套使旧域知识以非零速率被擦除"——按 §升降级规则 走一遍，是当前 candidate snapshot 里最干净的一份 worked example，也能解释为什么它停在 *conditional NTP-mech 候选* 而不是直接升 mech。

1. **形式陈述（lemma-style，不引入未定义概念）**：✅ 达标但 **conditional**。命题可写成 \"∃ ε>0, ∀ streaming protocol Π 满足 (batch=1, replay=0, ∀t θ_{t+1} ← θ_t − η·∇_θ CE(x_t)), ∀ ε-flat-minimum θ* 起步, 旧域 (D_old) 上 KL(p_θ_T ‖ p_θ*) ≥ ε·T/T₀\"。三个限定 (batch=1 / replay=0 / 单 cross-entropy) 都必须写出，否则被 Ibrahim 2403.08763 的工程配方反例命中——把 (batch, replay, schedule) 任一旋钮放宽 4 倍以上，KL 增长曲线就被压平 10×。这与 C1 把 (L, d, tokenization) 三参数全部 lock-in 才能成立同型。

2. **与已知复杂度/信息论/代数对象的非平凡映射**：⚠ 部分达标。最干净的映射是把 Lyle 2303.01486 的 *plasticity loss* 与 Dohare 2024 *Nature* 的 *unit-saturation* 框架翻译成 NTP loss landscape 的 Hessian-trace 单调上界——形式上属于优化几何/representation collapse 一族，但**还没有人**给出在 SGD/AdamW + i.i.d. mini-stream 通道下的紧上界。目前最接近的是 [`formal_limits.md`](../topics/formal_limits.md) §表达力 vs 可学性 提到的 C-FORM-4（NTP-learnability gap）的特化，可视为 C5 = C-FORM-4 ∩ (streaming axis)。映射存在但**不平凡程度低于** C1（C1 与 TC⁰ depth 之间是已证下界）。

3. **protocol 级 falsification（≤1k GPU·h）**：✅ 达标。在 1B 规模 OLMo / Pythia base 上，构造一个 1k token/step 的 streaming corpus（Common Crawl 按时间窗切分 + 旧域 RealTime-QA-style closed-book probe），运行 24h 单 GPU 训练，测旧域 closed-book accuracy 漂移。若 replay=0 / batch=1 / vanilla CE 下漂移 ≤ 2pp/day 且新事实写入率 ≥ 80%，C5 直接被证伪降级。这与 N7 §6 (待写) 计划登记的 2027 bet 同构。

4. **排除五 confound**：❌ 仅排除 (i)–(iii)，**(iv) attribute-head 缺失** 与 **(v) representation-geometry under-constraint** 尚未控制。NITP ([2605.24956](../papers/paper_notes/2026-05-28-2605.24956-nitp-next-implicit-token-prediction.md)) 加一项浅层激活作下一 token 稠密 self-target 即把 9B MoE MMLU-Pro 推高 5.7%——这意味着 \"NTP 几何欠约束\" 可能在 streaming 通道下提供一个未被测试的 plasticity 恢复机制；C5 必须先在 NITP-augmented base 上复现旧域漂移率，才能称已排除 (v)。Conditional Attribute Transformers ([2605.14004](../papers/paper_notes/2026-05-27-2605.14004-conditional-attribute-transformers.md)) 同样未在 streaming setting 下被复现。

**判定**：C5 当前停在 *conditional NTP-mech 候选*，与 C1 / C4 并列在第三栏；要升 mech 必须先在 NITP-augmented + attribute-head-augmented 两条工程修补下复现 §1 Lazaridou-style 漂移曲线。预计 2027 中之前若无 frontier lab 出 streaming pretraining 配方，C5 自然趋向 mech；若 NITP-style 修补在 streaming 下把旧域漂移压到与 Ibrahim 配方同量级，C5 退到 NTP-cap (objective-engineering 层)，与 ProFIL / NITP 同一处理。这也是判例选 C5 而非 Reversal Curse 的原因——后者还卡在 (3) protocol 级 falsification 的复现成本上（≥7B prefix-LM 训练 ≫ 1k GPU·h）。

## 升降级判例 — C6 (video-NTP interventional consistency) 走一遍四条升级条件

把 [`topics/world_model.md`](../topics/world_model.md) §C-WM-3 推出的命题——"∀ 仅在像素 / latent frame 上做 NTP 训练（无 simulator-backed counterfactual supervision）的 $M$，simulator-backed counterfactual benchmark $\mathcal{B}_{\text{do}}$ 上的 ATE 误差 $\varepsilon_{\text{do}}(M, X)$ 严格大于 0 且不随训练 token 数衰减"——按 §升降级规则 走一遍。选 C6 当判例的理由：它是 2026-05 全部候选里 *形式陈述与 falsifier 都已写出但映射 non-trivial 度和 confound 排除都只走了一半* 的最干净样本，恰好暴露 \"为什么开放域 NTP-mech 比 closed-world / discrete-action 子带难升一级\"。

1. **形式陈述（lemma-style，不引入未定义概念）**：✅ 达标但 **conditional**。命题写法在 §C-WM-3 已给——三个变量必须同时锁定：(a) 训练目标限定为 *像素/latent frame next-token* 而非加 simulator counterfactual supervision，否则 falsifier 平凡满足；(b) ATE 在 \"同一权重\" 上测量，排除 fine-tuned readout 头——这一条直接吸取 Causal Tongue-Tie [2605.25891](https://arxiv.org/abs/2605.25891) [unverified ID] 与 ProFIL [2605.11467](https://arxiv.org/abs/2605.11467) [unverified ID] 的教训；(c) 物理可控变量 $X$ 必须取 *非平凡* 维度（速度/方向/重力/碰撞），不是同分布 prefix-completion——若 $X$ 是 observational 噪声维度，$\varepsilon_{\text{do}}\to 0$ 可以由 Layer-1 拟合达成。三条限定缺一不可，与 C1 锁 (L, d, tokenization)、C4 锁 (encoder subspace, discrete action) 同型。

2. **与已知复杂度 / 信息论 / 代数对象的非平凡映射**：⚠ 部分达标。最干净的映射是 Pearl 因果阶梯——Layer 1 (observational, $P(s'|s,a)$) → Layer 2 (interventional, $P(s'|s,\text{do}(X))$) → Layer 3 (counterfactual)。C-WM-3 钉的是 Layer 1 → Layer 2 的鸿沟，由 Pearl & Mackenzie 2018 *The Book of Why* 第 1 章的 do-vs-see 区分 + Bareinboim & Pearl 2016 PNAS 的 identifiability 形式定义提供。**但**：这条映射的"非平凡"程度比 C1 弱——C1 与 TC⁰ depth 之间是 *已证下界*（log-depth 下 PARITY 不可解），C6 与 Pearl Layer 拒乘的"映射"目前只是 *定义级嵌入*，没有"video-NTP 训练动力学 ⊢ Layer-2 不可达" 的形式证明。最接近的是 Zecevic et al. 2023 *Causal Parrots* ([arxiv:2308.13067](https://arxiv.org/abs/2308.13067)) 论证 \"LLM 学的是 metainformation 上的 correlational meta-SCM 而非真实 SCM\"——这在 text 上提供了 *观察侧* 间接证据，但搬到 video-NTP 仍是模拟而非证明。这正是 C6 当前差 C1 一个量级的根因。

3. **protocol 级 falsification（≤1k GPU·h）**：✅ 达标。最干净的设计：取 Brax / MuJoCo / Isaac Sim 任一可程序化 simulator，构造 N≈10⁴ counterfactual triplet $\{(s, a, s'), (s, \text{do}(X{=}x), s'')\}$，$X$ 取 (initial velocity, friction coefficient, gravity, contact restitution) 四个独立维度；以同一 Cosmos / Genie-3 / OpenVLA-style 权重对 prefix 续 rollout，比较 marginal likelihood + latent state 同构 + downstream 物理一致性三层 ATE。Black-box API 调用即可，模型权重不需要公开；single H100 ≤200h 完成。若任一 $X$ 上 $\varepsilon_{\text{do}}(M,X)\to 0$ 且 marginal likelihood 与 sim 一致，C-WM-3 直接证伪降级为 NTP-cap。与 C1 (`H*` 测量) 同复杂度量级。

4. **排除五 confound**：⚠ 仅显式排除 (i)–(iii)，**(iv) attribute-head 缺失** 与 **(v) representation-geometry under-constraint** 在 video 域未被控制。(iv) 在 video-NTP 上的对应是 \"video model 没有显式的物理变量 head——速度 / 摩擦 / 重力都被压进 frame-level latent\"——Conditional Attribute Transformers [2605.14004](https://arxiv.org/abs/2605.14004) [unverified ID] 的 attribute-head 修补在 text 上证明可显著降低读出失败率，但在 video diffusion / latent-action 模型上至今无人复现。(v) 在 video-NTP 上的对应是 NITP-style 浅层激活 self-target ([2605.24956](https://arxiv.org/abs/2605.24956) [unverified ID]) 是否能把 video latent 几何拽进 *因果可解码* 子空间——目前文献空白。必须先在 NITP-augmented + attribute-head-augmented 两条工程修补下复现 $\varepsilon_{\text{do}}$ 测量，才能称 confound 已排除。这与 C5 卡在完全相同的两条 confound 上，是 Readout-side 主导假设 (见 [`ntp_survey.md`](ntp_survey.md) §10 闭环段落) 对每一条新 NTP-mech 候选征收的统一税。

**判定**：C6 当前停在 *conditional NTP-mech 候选 (video subband)*，与 C1 / C4 / C5 并列在第三栏；四升级条件 ✅⚠✅⚠，比 C5 的 ✅✅✅❌ 更不均匀——C6 的弱项不在 confound 数量，而在 (2) 映射非平凡度。要升 mech 至少需要：(a) 把 Zecevic 2308.13067 在 text 上的 meta-SCM 论证升级为 video-NTP 训练动力学下的形式不可达定理（即证 ∃ ε>0, ∀ video-NTP 训练协议 + ∀ pixel/latent objective, $\varepsilon_{\text{do}}\geq\varepsilon$）；(b) 与 [`causality.md` §C-CAUSAL-1](../topics/causality.md) 在跨模态 falsifier 上做 joint 设计，避免 text-only / video-only 各自被对偶 confound 掩盖；(c) 排除上述 (iv)(v)。三步任一缺失，C6 在下一个 readout-side 修补出现时仍可能被降回 NTP-cap，与 ProFIL / NITP 当年降 \"CoT theater\" 同型。

判例选 C6 的方法学增量：C1 是 closed-world / no-CoT / 单 forward pass 上写得最干净的 mech，C4 是 discrete-action VLA 这种 *枚举有限* 的子带 mech，C5 是 streaming 这种 *优化几何* 的子带 mech；C6 第一次把候选推到 *open-world + continuous variable + generative readout* 三重困难叠加的子带。这恰好是 NTP-mech 战线 2026 年最缺合格候选的位置——本仓库 [`samples/N6`](../samples/N6-world-model-three-answers.md) 的整章叙事都建立在这个位置上，但此前一直没有把它写成可走完判例的形式。本节是把 N6 §叙事 与 candidate snapshot 之间的方法学桥补齐。

## 与其它文档的接口

- [`ntp_survey.md`](ntp_survey.md) §10 维护候选清单的逐条状态；本页维护**升降级规则**与历史日志。
- 各 [`topics/*.md`](../topics/) 维护 mech-level 候选的形式细节与实测证据线。
- [`samples/`](../samples/) 把每个候选叙事化（如 [N2 the-tc0-wall](../samples/N2-the-tc0-wall.md) 对应 C1）。

任何对 candidate 做升降级的 commit 都应同时改三处：候选所在 topic 页（证据线）+ ntp_survey.md §10（候选条目）+ 本页升降级历史表。三处不同步即视为 incomplete。
