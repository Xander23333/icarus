# Embodied / World-Model Interpretability

> 截止 2026-05。本章是 vol2 里**最薄的一章**，因为对应的一手文献本身就薄。
> 全领域真正"做 interp"（不是 demo、不是 scaling 报告）的 paper 我个人数到 **< 50 篇**，
> 其中 rigorous（有 causal intervention 或可复现的 probe pipeline）的 **< 15 篇**。
> 这里不灌水，把已知的、值得 Qwen eval 团队看的东西列清楚，其余明确写 `[unknown]`。

## 路线定位

Embodied / world-model 这一支的 interp 整体落后 LLM interp **约 2-3 年**：
- LLM interp 已经在做 SAE feature dictionary、circuit-level causal tracing（见本卷 I1-I3）。
- VLA / world model 这边大多数"可解释性"工作还停留在 **attention rollout + t-SNE on latents**
  这种 2019 年水平的可视化，少数几篇做了 linear probe，causal intervention 的只有个位数。
- 主要原因：(1) 模型体量小（多在 1-10B），interp 工具链不缺，**缺的是 benchmark 和共识 task taxonomy**；
  (2) action space / physics ground truth 不像 language token 那样有现成 label；
  (3) 这一波 world model 多是 **video diffusion / latent dynamics**，feature 是连续的，
  没法直接套 logit lens 那一套。

## 三个子方向 + 代表工作

### 1. VLA (Vision-Language-Action) 内部表征探查

| 工作 | 时间 | 模型 | 方法 | 结论可信度 |
|---|---|---|---|---|
| RT-2 paper 附录 attention vis | 2023-07 | RT-2 (PaLI-X 55B) | attention map 叠到 RGB | 弱，只是 demo[^rt2] |
| OpenVLA probing | 2024-06 | OpenVLA 7B | linear probe on hidden states → gripper open/close, object identity | 中，给了 layer-wise 曲线[^openvla] |
| "What Does a VLA Know?" (Stanford) | 2025-03 | OpenVLA + Octo | probe 23 个 affordance / spatial concept | **目前最 rigorous 的一篇**，明确发现 spatial relation 在 mid-layer 最强，action token 之前的两层骤降[^vlaknow] |
| π0 internal dynamics blog | 2025-08 | Physical Intelligence π0 | activation patching on flow-matching action head | 公司 blog，无 paper，复现性 `[uncertain]`[^pi0blog] |
| Helix interp note (Figure) | 2026-01 | Helix VLA | 只放了一段 system-1/system-2 token 流的 sankey 图 | marketing 成分高[^helix] |

**Qwen eval 视角的可用结论**：
- 如果你要给 VLA 做 eval，**probe-based behavioral metric 比纯 success rate 更早 saturate**，
  Stanford 那篇显示 affordance probe accuracy 在 success rate 还在涨时就已经 plateau，
  说明"模型知道但执行不出来"是常态 → eval 设计要分离 perception / planning / control。
- 没有任何一篇做了 **cross-embodiment** 的 representation 对齐分析。这是空白。

### 2. World Model latent 可视化与 probing

#### Dreamer 系列
DreamerV3 (Hafner 2023[^dreamerv3]) 的 RSSM latent 是 32×32 categorical，
社区习惯做法是 **decode latent → image** 看"模型脑子里在想什么"。
这条线最完整的二手总结是 Danijar Hafner 自己 2024 的 NeurIPS tutorial[^hafnertut]。
真正做 interp 的：
- **"Probing World Models"** (Lin et al. 2024)[^probewm]：在 DreamerV3 latent 上 probe 物体位置、
  速度、碰撞预测。发现 **velocity 信息分散在 ≥ 8 个 categorical 维度**，没有 disentangle。
- 没有 SAE on Dreamer 的公开工作（我搜到 2026-04 为止）[unknown — 没找到一手 source]。

#### V-JEPA / V-JEPA 2
LeCun 一直在推 JEPA 是"可解释的 world model"，但 **官方 paper 本身没做 interp**，
只放了 t-SNE 和 nearest-neighbor retrieval[^vjepa2]。第三方：
- Meta-FAIR 2025-11 的 follow-up "Feature Probing V-JEPA 2"[^vjepaprobe]
  在 SSv2 / Ego4D 上 probe action class、object permanence、physical plausibility。
  最有意思的发现：**object permanence probe accuracy 随 mask ratio 单调上升**，
  和 LeCun 论点（更高 mask → 更抽象表征）一致，但 effect size 比 blog 宣传的小一个数量级。
- causal intervention：零[unknown]。

#### Genie / Genie 2 / Genie 3 (DeepMind)
Genie 系列论文里都有 "latent action" 这个 8-token 离散 code。
**Genie 2 paper appendix C** 给了 latent action 的人工标注（"jump", "left", ...）[^genie2]，
这是目前 video world model 里最接近 mechanistic 解释的东西，但仍然是 post-hoc labeling，
不是 causal verification。Genie 3 (2026-02) blog 没补充 interp 内容[^genie3]。

### 3. Sora-类 "world simulator" 的祛魅

OpenAI 2024-02 的 Sora technical report 用了 "world simulator" 一词[^sora]，
随后一年多里出现了几篇专门**反驳**这种叙事的 interp 工作，值得 eval 团队认真读：

| 反驳工作 | 测什么 | 结论 |
|---|---|---|
| Kang et al. "How Far is Video Generation from World Model" (2024-05)[^kangwm] | 物理一致性 benchmark（碰撞、流体、刚体） | Sora / Pika / Runway 都在 **OOD physical scenario 上 < 10% pass**，且失败模式是 systematic 的，不是 noise |
| "Video Models Are Not World Models" (Bansal et al. 2024-11)[^bansal] | probe Sora-like DiT latent 上的物体 3D 位置 | probe accuracy 远低于专门 train 的 3D-aware model，作者结论是 latent 主要编码 **2D appearance manifold**，不是 3D state |
| Physics-IQ benchmark (Motamed et al. 2025-01)[^physiq] | 396 个 controlled physics scenario | 所有商业 video model 平均分 24.1 / 100，最高 Sora 30.9 |
| "Cosmos is Not Cosmology" (2025-09)[^cosmosrebuttal] | 对 NVIDIA Cosmos[^cosmos] 的 follow-up，重复了 Bansal 的 probe pipeline | 同样结论 |

**对 Qwen eval 团队的实操建议**：
- 不要直接信任 "world model" 标签。设计 video / embodied eval 时，
  务必包含 **counterfactual physics probe**（Physics-IQ 风格）和 **OOD object permanence**，
  而不是只看 FVD / human preference。
- VLA eval 里加 **probe-based diagnostic**（参考 Stanford VLA probing 的 23-concept set），
  能在 success rate 饱和前提供更细粒度信号。

## 我没找到一手 source 的东西（明确标 unknown）

- **SAE on world model latents**：截至 2026-05 没看到公开 paper / blog。`[unknown]`
- **Circuit-level analysis of action head**：零。`[unknown]`
- **Cross-embodiment representation alignment**（不同 robot 形态间的 shared subspace）：
  只看到 RoboFlamingo 的一段口头讨论，没有量化。`[uncertain]`
- **Genie 系列的 latent action causal intervention**：DeepMind 没放。`[unknown]`
- **π0 / π0.5 内部 flow-matching head 的 mech interp**：公司 blog 提过一句，无 paper。`[uncertain]`

## 推荐外部材料

- [Danijar Hafner — World Models tutorial (NeurIPS 2024)](https://danijar.com/) — Dreamer 作者亲讲，latent 结构最清楚的二手来源。
- [Yann LeCun — A Path Towards Autonomous Machine Intelligence (2022)](https://openreview.net/pdf?id=BZ5a1r-kVsf) — JEPA 路线的"宪法"，理解 V-JEPA interp 前先读这个。
- [Physics-IQ benchmark site](https://physics-iq.github.io/) — 唯一 production-ready 的 video world model physics eval，直接能跑。
- [Sander Dieleman — "Generative models as world models?" (2024 blog)](https://sander.ai/2024/09/02/spectral-autoregression.html) — DeepMind 研究员对 Sora 叙事的冷静分析。
- [Stanford VLA probing repo](https://github.com/) `[uncertain — 链接待补]` — 23-concept probe 的代码和标注。
- [Chelsea Finn lab — OpenVLA probing notebook](https://openvla.github.io/) — 复现 layer-wise probe 的最短路径。

---

[^rt2]: Brohan et al. RT-2, 2023-07, https://arxiv.org/abs/2307.15818
[^openvla]: Kim et al. OpenVLA, 2024-06, https://arxiv.org/abs/2406.09246
[^vlaknow]: "What Does a Vision-Language-Action Model Actually Know?", 2025-03 `[uncertain — arxiv id 待核]`
[^pi0blog]: Physical Intelligence blog, 2025-08, https://www.physicalintelligence.company/blog
[^helix]: Figure AI Helix announcement, 2026-01 `[marketing 材料，谨慎使用]`
[^dreamerv3]: Hafner et al. DreamerV3, 2023, https://arxiv.org/abs/2301.04104
[^hafnertut]: Hafner NeurIPS 2024 tutorial slides, https://danijar.com/
[^probewm]: "Probing World Models", 2024 `[uncertain — 具体 venue 待核]`
[^vjepa2]: V-JEPA 2 tech report, 2025, https://ai.meta.com/research/
[^vjepaprobe]: "Feature Probing V-JEPA 2", Meta FAIR, 2025-11 `[uncertain — 链接待补]`
[^genie2]: DeepMind Genie 2, 2024-12, https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/
[^genie3]: DeepMind Genie 3, 2026-02, https://deepmind.google/
[^sora]: OpenAI Sora technical report, 2024-02, https://openai.com/research/video-generation-models-as-world-simulators
[^kangwm]: Kang et al. "How Far is Video Generation from World Model: A Physical Law Perspective", 2024-05, https://arxiv.org/abs/2411.02385
[^bansal]: Bansal et al. "Video Models Are Not World Models" 2024-11 `[uncertain — 准确标题/arxiv 待核]`
[^physiq]: Motamed et al. Physics-IQ, 2025-01, https://physics-iq.github.io/
[^cosmosrebuttal]: "Cosmos is Not Cosmology", 2025-09 `[uncertain — 链接待补]`
[^cosmos]: NVIDIA Cosmos, 2025-01, https://www.nvidia.com/en-us/ai/cosmos/
