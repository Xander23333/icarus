# JEPA 家族（I-JEPA / V-JEPA / V-JEPA 2）

> **范围**：本节覆盖 Meta FAIR 在 Yann LeCun 主导下推动的 **Joint-Embedding Predictive Architecture (JEPA)** 路线，从 2023-01 的 I-JEPA 到 2025-06 的 V-JEPA 2 / V-JEPA 2-AC，截止 2026-05。重点是**在表示空间（latent）而非像素空间做预测**这条与主流 generative pretraining 平行的技术线，以及 LeCun 围绕 "world model" 的更大叙事在 2025–2026 真实落地到了哪一步。读者 = Qwen agentic 评测 owner，熟 SSL（MAE / DINO / contrastive）；本节不科普 self-supervised 基础。

## 路线定位（1 段）

JEPA 是 **LeCun 个人下注最重、但工业采纳最浅**的一条 self-supervised 路线。它和主流的两条 SSL 路线——**生成式 pretraining**（MAE / VideoMAE / 像素重建）与**判别式 contrastive / self-distillation**（DINOv2、DINOv3、SigLIP）——并列，但坚持一个独立主张：**预测目标应当是"另一个 encoder 编出的表示"，而不是像素，也不是 contrastive 的"和谁更近"**。在 vision encoder 实战榜单上，2024–2026 的事实赢家是 DINOv2 / DINOv3 / SigLIP2，JEPA 系列的 frozen-feature 评测**没有显著超越** DINOv2。JEPA 真正翻身的机会是 LeCun 反复讲的 **world model for planning**——V-JEPA 2-AC 第一次把这个故事跑到真机器人 zero-shot 抓取/放置 demo 上，这是 2025 年这个家族最有信服力的产出，也是它在 2026 年 robotics / embodied 圈被重新关注的原因。

## 代表模型清单

| 模型/事件 | 发布日 | 关键变化 | 一手 source |
|---|---|---|---|
| LeCun "A Path Towards Autonomous Machine Intelligence" position paper | 2022-06 | 提出 JEPA / H-JEPA / world model 整体蓝图 | [openreview PDF](https://openreview.net/pdf?id=BZ5a1r-kVsf) |
| **I-JEPA** | 2023-01-19 | 第一个 JEPA 实例；image，masked block prediction in representation space；ViT-H/14 | [arxiv:2301.08243](https://arxiv.org/abs/2301.08243)；[FAIR blog 2023-06](https://ai.meta.com/blog/yann-lecun-ai-model-i-jepa/) |
| **V-JEPA** | 2024-02-15 (blog) / 2024-04-15 (arxiv v1) | 视频扩展；feature prediction 取代 pixel reconstruction；VideoMix2M (2M 视频) | [arxiv:2404.08471](https://arxiv.org/abs/2404.08471)；[FAIR blog](https://ai.meta.com/blog/v-jepa-yann-lecun-ai-model-video-joint-embedding-predictive-architecture/) |
| MC-JEPA | 2023-07 | motion + content 联合 JEPA（早期变体，少人引用） | [arxiv:2307.12698](https://arxiv.org/abs/2307.12698) |
| Image World Models / IWM | 2024-03 | I-JEPA 思路扩展到 conditional prediction，做 controllable transformation 学习 | [arxiv:2403.00504](https://arxiv.org/abs/2403.00504) |
| **V-JEPA 2** | 2025-06-11 | 1M+ 小时视频 + 1M 图像；ViT-g (1B+) scaling；引入 action-conditioned 后训练 V-JEPA 2-AC，做 robot world model；zero-shot pick & place | [arxiv:2506.09985](https://arxiv.org/abs/2506.09985)；[FAIR blog 2025-06](https://ai.meta.com/blog/v-jepa-2-world-model-benchmarks/) |
| V-JEPA 2 权重开源 | 2025-06 | code + 多尺度 ckpt 上 GitHub `facebookresearch/jepa` | [github.com/facebookresearch/jepa](https://github.com/facebookresearch/jepa) |
| LeCun 离任 Meta 传闻 / 新 startup | 2025-11 起多次报道 | Financial Times / Reuters 报 LeCun 计划离开 FAIR 创办 world-model startup | [FT 2025-11](https://www.ft.com/) [uncertain 具体链接]；[unknown — 截至 2026-05 是否已正式离任，需查最新公告] |
| 2026-05 状态 | — | V-JEPA 2 仍是该家族最新主线模型；社区围绕 V-JEPA 2 的衍生 finetune / robotics 复现陆续出现；尚无 "V-JEPA 3" 一手 source | — |

## 架构核心（按 paper 写的）

### 1. JEPA 的通用范式

JEPA 训练 3 个组件[^lecun-2022]：
- **context encoder** $f_\theta$：编码可见输入 $x$；
- **target encoder** $f_{\bar\theta}$：编码完整或被掩盖的目标 $y$，权重通常是 context encoder 的 **EMA**（无梯度，防 collapse 的关键之一）；
- **predictor** $g_\phi$：从 $f_\theta(x)$ 出发，**在表示空间**预测 $f_{\bar\theta}(y)$。

Loss 通常是 L1 / smooth-L1 / cosine，**没有像素重建项**，**没有 contrastive 的负样本**。LeCun 反复强调的卖点："不学那些为了重建像素必须学的高频细节、贴图、噪声"，让 representation 留在 high-level 抽象层。

### 2. I-JEPA（图像）

[arxiv:2301.08243](https://arxiv.org/abs/2301.08243) §3：

- Backbone：ViT-B / ViT-L / **ViT-H/14**（最大 632M）。
- **masking 策略**：在 image patch grid 上采 1 个 **context block**（覆盖 ~85% 区域但带 spatial mask）和 4 个 **target blocks**（每个覆盖 15–20%），target block **互不重叠** 且 context 不能完全覆盖 target。这个 block-level masking 是 I-JEPA 区分 MAE 的关键——MAE 用 random patch masking，I-JEPA 强调"预测 semantic 区域而不是孤立 patch"。
- predictor 是窄的 ViT（depth 6–12，宽度小于 backbone），输入 context tokens + target block 的 **positional embeddings**（mask tokens），输出每个 target patch 的预测 representation。
- 评测：linear probe / fine-tune ImageNet-1k、低数据 1% labels、ADE20k 分割等。报数与 DINOv1 / MAE 相比 **训练快 2.5–10×**（相同精度），但 frozen-feature 绝对 SOTA 不如 DINOv2[^dinov2]。

### 3. V-JEPA（视频）

[arxiv:2404.08471](https://arxiv.org/abs/2404.08471)：

- backbone：ViT-L / ViT-H over **spatiotemporal patches**（16×16×2 tubelets）。
- 数据：**VideoMix2M** = HowTo100M + Kinetics-710 + Something-Something-v2 + 自采，~2M clips。
- masking：3D **tubelet masking**，random + block 两种 strategy 混合；mask ratio 高（~90%），predictor 在 latent 空间补全被 mask 的 spatiotemporal regions。
- 训练目标：smooth L1 on EMA-target feature。**完全没有 pixel decoder**——这是 V-JEPA 对 VideoMAE 的主要 architectural difference。
- 评测：
  - frozen probe 在 Kinetics-400、Something-Something-v2、ImageNet-1k、AVA 上**优于 VideoMAE / OmniMAE**；
  - 对"motion / temporal" 任务（SSv2）相对增益最大——paper 论点："feature prediction 比 pixel prediction 更关注 motion semantics"；
  - 与 image SSL 顶流（DINOv2）在**视频**任务对比 V-JEPA 占优，在**纯静态**任务持平或略输。
- 算力：V-JEPA ViT-H 用 ~$10^5$ GPU-hour 量级 [uncertain 具体数字，paper 表给的训练 step + batch 可粗算]。

### 4. V-JEPA 2 与 V-JEPA 2-AC

[arxiv:2506.09985](https://arxiv.org/abs/2506.09985) 是这个家族最重要的一次升级，主要变化：

#### (a) 数据 / scale 跳跃
- **视频量从 2M clip → "1M+ 小时"** 量级（paper §3 数据表），来源是 internet-scale curated video + 1M+ images（图像-视频联合）。规模相对 V-JEPA 提升约 **10–100×**[^vjepa2]。
- backbone scale 到 **ViT-g (≈1B)**（V-JEPA 1 最大是 ViT-H/632M）。

#### (b) 两阶段训练：action-free → action-conditioned
- **Stage 1：action-free V-JEPA 2**——还是 feature prediction，但在 1M+ 小时视频上 scaling。frozen 评测在 video understanding benchmark（EpicKitchens action anticipation、SSv2、Diving-48、Perception Test）上**全面刷 SOTA**[^vjepa2-blog]。
- **Stage 2：V-JEPA 2-AC**——在小规模 robot interaction 数据（**Droid 数据集**~62 小时）上**仅训练一个轻量 action-conditioned predictor**，frozen V-JEPA 2 backbone。新 predictor 接受 `(s_t latent, a_t)` 预测 `s_{t+1} latent`，即一个 latent dynamics model。
- **Zero-shot deployment**：用 V-JEPA 2-AC 作为 world model，在新机器人 (Franka) 上用 **model predictive control (MPC)** 做 pick & place——**没有在该机器人上训练过任何 action data**。paper 报 single-object pick & place 65–80% 成功率（reach/grasp/place 子任务分别报）；多物体场景大幅退化。
- 这是 JEPA 第一次在真机器人上做**zero-shot planning** demo，对 LeCun "world model 才是通向 autonomy 的路" 的叙事是一个**部分兑现**。

#### (c) 评测面的扩张
V-JEPA 2 paper 评测覆盖 3 类：
1. **video understanding**（frozen probe / attentive probe）；
2. **video QA**（接 LLM 做 video-text 任务）；
3. **robot control**（zero-shot MPC，上面）。

Paper §5 报在 EpicKitchens action anticipation 上是 SOTA，在 Perception Test 上**显著优于** InternVideo2、VideoMAEv2 等同代视频 SSL backbone。

## 训练方法核心

- **Pretrain**：纯 self-supervised，无标签；EMA target encoder 是防 collapse 的关键 trick（与 BYOL / DINO 同源）。
- **没有显式 "post-train"**：V-JEPA 2-AC 的 action-conditioned predictor 训练算是一种 light post-training，但 backbone frozen。
- **没有 SFT / RLHF / RLVR** —— JEPA 是 representation pretraining，不是 chat model。这恰是 LeCun 叙事的一部分："autoregressive LLM 的整套 post-train 都是建立在错的 base 上"。
- **算力**：V-JEPA 2 paper 给出 batch size 与 step 数，可推 ≈ 数千 H100 卡周量级 [uncertain 精确数字，paper 未直接列 GPU-hour]；blog 提"在 Meta GenAI 集群训练"，无具体披露。

## 与 eval / benchmark 的接口

- **官方报**：
  - I-JEPA：ImageNet-1k linear probe / fine-tune、ADE20k、低数据 transfer；
  - V-JEPA：Kinetics-400、SSv2、ImageNet（image probe）、AVA；
  - V-JEPA 2：上述视频 benchmark + **EpicKitchens action anticipation**（重点）+ **Perception Test** + Droid robot eval。
- **第三方复现 / 独立评测**：
  - V-JEPA 1 在 timm / OpenCLIP-style 社区评测中**没有像 DINOv2 那样被广泛采用作为 backbone**——一个常见的社区抱怨是 "frozen-feature 在 image classification 上不如 DINOv2，又没有 CLIP 的 text alignment"。
  - V-JEPA 2 发布后，少量 robotics 团队（HF lerobot、CMU、Berkeley 个人项目）开始把 V-JEPA 2 frozen feature 当 visual encoder 试用，但截至 2026-05 **没看到一篇主流 VLA paper（π-series / Gemini Robotics / GR00T）把 V-JEPA 2 作为 backbone** [unknown — 没有反向证据但也没采用证据]。
- **质疑 / contamination**：
  - **没有显著 contamination 指控**（SSL pretraining 不太会有 test-set 泄漏问题）；
  - 主要质疑是 **"为什么 frozen-feature 比 DINOv2 没有压倒性优势"**——LeCun 在多次 talk（[Lex Fridman #416 2024-03](https://www.youtube.com/watch?v=5t1vTLU7s40)）回应是"评测维度选错了，static image classification 不是 world model 该被衡量的地方"。
  - V-JEPA 2-AC 的 robot demo 第三方未复现；Droid 训练 + Franka 部署的 sim-to-real / lab-to-lab 泛化性 [uncertain]。

## 未知与争议

明确未披露 / 未明项（截至 2026-05）：

1. **V-JEPA 2 真实算力 / 训练成本** —— paper 给 hyperparams，但没明列 GPU-hour 或集群规模。
2. **"1M+ hours" 视频数据的精确来源** —— paper 给类别但不给 source URL list，社区无法完全复现 data mixture。
3. **V-JEPA 2-AC predictor 的具体架构 / 参数量** —— paper 只说 "lightweight"，具体 layer 数 / context length [uncertain]。
4. **"H-JEPA" / hierarchical JEPA 的实战实现** —— LeCun 2022 position paper 的核心是多层级 JEPA 实现长 horizon planning，但**截至 2026-05 没有任何 FAIR 论文展示 H-JEPA 工作**。V-JEPA 2-AC 仍是 single-level。
5. **LeCun 离任 / startup** —— 2025-11 起多次媒体报道但官方未确认。如果属实，JEPA 路线在 Meta 内的优先级 [uncertain]。
6. **是否有 V-JEPA 2 + LLM 融合的端到端模型** —— paper 报了"V-JEPA 2 接 LLM 做 video QA"，但只 finetune adapter；和 native multimodal（Gemini / GPT-4o 路线）的差距巨大。

主要争议：

- **JEPA vs DINOv3 vs MAE 三方对决**：到 2025–2026，frozen visual feature 评测的主流 winner 是 DINOv2/v3（Meta FAIR 同一个组的另一条线，Maxime Oquab / Piotr Bojanowski 主导）。DINOv3 paper（2025）和 V-JEPA 2 几乎同期发布——同一公司内两条 SSL 路线**没有合并**也是个有意思的信号。LeCun 公开站 JEPA，但 vision 实战 community 站 DINO。
- **"World model" 叙事的兑现进度**：LeCun 自 2022 起每年都说"再过几年 LLM 就是 off-ramp"。2025-06 V-JEPA 2-AC 的 zero-shot robot demo 是这个叙事**第一次有可演示的产出**，但和 π0.5 / Gemini Robotics 在真实任务上的能力差距仍然巨大——后两者是 BC + VLM + 大量真实机器人数据；JEPA 路线主张"无需大量 robot data，只靠观察视频学 world model"，**这个核心假设至今未被 large-scale 验证**。
- **学术声誉 vs 产品采纳的剪刀差**：JEPA 在 LeCun 个人 talk 影响力下知名度极高，但被实际下游 production 系统采用的频率**接近零**——2026-05 的 frontier robotics、VLM、multimodal LLM 系统里基本看不到 JEPA backbone 出场。这种"思想流派受关注 / 工程采纳落后"是 JEPA 当下最准确的画像。

## 与同代 visual SSL 的快速对照

| 维度 | I-JEPA / V-JEPA 2 | DINOv2 / v3 | VideoMAE v2 | SigLIP 2 |
|---|---|---|---|---|
| 监督信号 | latent feature prediction (EMA target) | self-distillation + iBOT patch loss | pixel reconstruction (masked) | image-text contrastive |
| 是否需要文本 | 否 | 否 | 否 | **是** |
| Frozen image classification 强度 | 中 | **强** | 中 | 强（zero-shot） |
| Frozen video understanding 强度 | **强**（V-JEPA 2 SOTA EpicKitchens 等） | 中 | 强 | 中 |
| World model / planning 能力 | **有 demo**（V-JEPA 2-AC） | 无 | 无 | 无 |
| 下游 VLM / VLA 采纳度 | 极低 | 高（多家用作 vision encoder） | 中 | **高**（Gemini / 多 VLM） |
| 开放度 | 权重 + code 开 | 权重 + code 开 | 权重 + code 开 | 权重开 |

**核心 takeaway for Qwen eval lead**：
1. 如果你做**视觉 encoder 选型**评测，2026 年的事实选择是 **DINOv3 + SigLIP2**，不是 JEPA。
2. 如果你关心**video understanding** frozen feature，V-JEPA 2 是值得纳入对照集的——它在 EpicKitchens / Perception Test 这类**时序密集** benchmark 上确实领先。
3. 如果你关心**world model / planning / agentic RL** 的长期路线，JEPA 的 latent-space prediction 思想是必须读的——但它在 LLM agentic 领域**至今没有可工业部署的实例**。把它当作 "思想储备" 而非 "现成 baseline" 更准确。
4. LeCun 的赌注（autoregressive LLM 是死路、world model 是未来）和当前 frontier model 实际状态之间的**张力**本身是一个值得在评测策略里反映的元问题——agentic RL 训练循环中的"world model rollout"思路（Dreamer-style）和 JEPA 是同源。

## 推荐外部材料

- [LeCun, "A Path Towards Autonomous Machine Intelligence" (2022)](https://openreview.net/pdf?id=BZ5a1r-kVsf) — JEPA 整个叙事的源头 position paper，必读以理解动机。
- [I-JEPA paper, arxiv:2301.08243](https://arxiv.org/abs/2301.08243) — 第一个 JEPA 实例，最干净的方法定义。
- [V-JEPA 2 paper, arxiv:2506.09985](https://arxiv.org/abs/2506.09985) — 这个家族当下最重要的论文，含 action-conditioned + robot eval。
- [Meta FAIR V-JEPA 2 blog](https://ai.meta.com/blog/v-jepa-2-world-model-benchmarks/) — 含 zero-shot robot 视频 demo，比 paper 直观。
- [github.com/facebookresearch/jepa](https://github.com/facebookresearch/jepa) — 官方 code + 多尺度权重；V-JEPA 2 base + AC predictor。
- [Lex Fridman Podcast #416 — Yann LeCun (2024-03)](https://www.youtube.com/watch?v=5t1vTLU7s40) — LeCun 自己 narrate 为什么 LLM 是 off-ramp，对 JEPA 路线动机讲得最透。
- [Sebastian Raschka, "Understanding Self-Supervised Learning" 系列 blog](https://magazine.sebastianraschka.com/) — 把 I-JEPA / DINO / MAE 放一起对比的高质量科普。
- [Lilian Weng, "Self-Supervised Representation Learning" (持续更新)](https://lilianweng.github.io/posts/2019-11-10-self-supervised/) — JEPA 类方法的 EMA / collapse 防御 trick 在更大 SSL context 里的位置。

---

[^lecun-2022]: LeCun, "A Path Towards Autonomous Machine Intelligence", OpenReview 2022, §III-IV 定义 JEPA 与 H-JEPA；EMA target 与 representation-space loss 的动机在 §III.D。
[^dinov2]: Oquab et al., "DINOv2: Learning Robust Visual Features without Supervision", arxiv:2304.07193, 2023-04；其 ViT-g/14 在 ImageNet linear probe / ADE20k 等多个 benchmark 上仍是 V-JEPA 1 系列没有压过的同公司参照。
[^vjepa2]: Assran et al., "V-JEPA 2", arxiv:2506.09985, 2025-06，§3 数据与 scaling，§4 训练，§5 评测含 robot zero-shot MPC。
[^vjepa2-blog]: Meta FAIR, "V-JEPA 2: world model benchmarks", https://ai.meta.com/blog/v-jepa-2-world-model-benchmarks/, 2025-06。
