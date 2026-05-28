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
| 2026-05-25 | Klindt, LeCun, Balestriero, *When Does LeJEPA Learn a World Model?* | LeJEPA (alignment + Gaussian reg) 在 stationary additive-noise 世界类下 **linearly identifies** latent；并证 Gaussian 为 *唯一* 满足该 guarantee 的 latent prior；pixel 机器人控制实证 latent planning 收益 | mech (paradigm-replacement 路线的条件性数学加固) | [2605.26379](../papers/paper_notes/2026-05-29-2605.26379-lejepa-world-model-identifiability.md) |
| 2026-05-26 | Yang et al., *STARS — Stability-driven Recurrent Scaling for LoopLMs* | latent loop reasoning 的崩塌源于 Jacobian 谱半径 >1；Spectral Radius Regularization 把谱半径压到 <1，test-time 深度单调饱和；C1 forward-pass capacity 在 trained-stable looped 模型上需替换为 *converged depth* | counter-evidence (架构-训练协同修补 latent reasoning) | [2605.26733](../papers/paper_notes/2026-05-29-2605.26733-stars-looped-stability.md) |
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

## Video-NTP 这条暗线 (2024–2026)

text-NTP 的 world-model 证据基本上停在 Othello-GPT 与 chess-Transformer 这两个 closed-world 玩具上，开放域的同构性证据极弱（Vafa 2024, [arxiv:2406.03689](https://arxiv.org/abs/2406.03689)）。真正可能改写赌注的，是 2024 年起把 "下一帧 / 下一 latent 帧" 当作 token 的这一脉，下面按时间线收一遍。

- **2023-09, Wayve, GAIA-1** ([arxiv:2309.17080](https://arxiv.org/abs/2309.17080))：9B 参数 video + action + text 的自回归世界模型，在驾驶场景上做未来帧预测。这是工业界第一次把 "video-NTP" 当作 world-model 的训练范式公开发表，但生成长度仍以秒计。
- **2024-02, OpenAI, Sora** (technical report, 非 arxiv)：DiT-based latent video diffusion，不是严格自回归 NTP，但 OpenAI 在报告里明确把它列为 "world simulators"。社区里 LeCun 当周就在 Twitter 上反驳，列出物体永恒性失败、违反质量守恒的 cherry-pick 反例——这场争论本身就是 C-WM-2 的活样本。
- **2024-02, DeepMind, Genie** ([arxiv:2402.15391](https://arxiv.org/abs/2402.15391)) → **Genie 2** (blog, 2024-12)：从 unlabeled 2D 平台游戏视频里 *无监督* 抽出 latent action codebook，再训 dynamics。Genie 2 把同一套思路扩到 3D，可生成数十秒可控环境，但 demo 全部在 10–20 秒尺度内出现物体凭空消失。
- **2024-02, Liu et al., Large World Model (LWM)** ([arxiv:2402.08268](https://arxiv.org/abs/2402.08268))：1M context、video + text 自回归。论文宣称的是 long-context 能力而非 world-model 涌现，probe 类证据缺失。
- **2024-04, Meta, V-JEPA** ([arxiv:2404.08471](https://arxiv.org/abs/2404.08471))：LeCun 阵营对 Sora 的回应——*不要* 在像素空间做 NTP，要在 latent 上做 masked prediction + energy-based。Something-Something-v2 / Kinetics-400 frozen-eval 优于 video-MAE，证据指向 "non-generative latent prediction" 在动作识别上确实更省样本，但尚未在 controllable simulation 上拿出 Genie 量级的演示。
- **2024-05, Microsoft + EPFL, DIAMOND** ([arxiv:2405.12399](https://arxiv.org/abs/2405.12399))：把 diffusion 当 world model 在 Atari-100k 上训 RL，证明 *生成式* world model 在 sample-efficient RL 上能与 DreamerV3 同档。
- **2025-01, NVIDIA, Cosmos** (whitepaper, [unverified arxiv ID])：把 video world model 当作 robotics foundation 公开，30+ 模型变体，强调 physical AI 的 pretrain → post-train pipeline。是否真有 object permanence 提升尚无独立复现。
- **2025–2026** 的多模 VLA 论文（OpenVLA [arxiv:2406.09246](https://arxiv.org/abs/2406.09246)、pi0 [arxiv:2410.24164](https://arxiv.org/abs/2410.24164)、RT-2 [arxiv:2307.15818](https://arxiv.org/abs/2307.15818)）把 action 也丢进 next-token 序列，可视为 video-NTP 的延伸，但目前公开 eval 几乎不报 world-model 同构性，只报 task success rate——这是当前文献的一个系统性盲区。

把这条暗线对齐到 §核心问题的三种 world model：video-NTP 在 *第 1 种*（行为规划/可玩环境）上有了 Genie/DIAMOND 这样的真实存在性证据，比 text-NTP 强一个数量级；在 *第 2 种*（表征同构）上仍然只有 frozen-probe 的弱信号，没人做出 video 版 Othello-GPT 那种 1.7% 错误率线性可解码的干净 demo；在 *第 3 种*（反事实/因果）上彻底空白——没有任何一篇 video world-model 论文做过 do-operator 干预下的预测一致性 eval。

判断：video-NTP 把 "NTP 选不选 world model" 这道题的赌注真正抬高了，但 2024–2026 的证据告诉我们，**它选出来的仍然是行为级 / 帧级 dynamics**，object-level 长时序与因果结构依旧不来自 NTP 自发涌现。下一个能推动 discourse 的实验，不是再训一个更大的 Sora，而是在 Genie 2 / Cosmos 这类 latent-action 世界模型上做 Othello-GPT 风格的 probe——如果能在 latent 里线性可解码出物体身份、位置、速度，那 C-WM-1 的边界就从 closed-world 扩到了 mid-open-world；如果不能，那 video-NTP 也只是 text-NTP 的高维翻版。

## Object permanence 这把更细的尺子 (2018–2026)

§视频暗线 末尾那句\"10–20 秒后开始物体永恒性失败\"值得展开，因为这恰好是把 video-NTP world-model 讨论从\"看起来真不真\"拽回到\"可量化的世界变量是否被编码\"的最干净抓手。Object permanence——Piaget 1954 用来描述 8–12 月龄婴儿习得的\"物体被遮挡后仍存在\"能力——在视觉认知里有一条相对独立、可数字化的 benchmark 演化史，2024 之后才被 video-NTP 社区重新拾起，但很多人没意识到这条线在 LLM 时代之前已经走了将近十年。

- **2018-03, Riochet et al., IntPhys** ([arxiv:1803.07616](https://arxiv.org/abs/1803.07616))。第一个把 *violation-of-expectation* 范式（婴儿心理学经典做法）搬到 video model eval：构造一对 plausible / impossible 视频（物体应在 vs 凭空消失），让模型对二者输出 likelihood，看是否 plausible > impossible。当年最强 baseline 在 occluder 场景上只比 chance 高 ~5 个点。这条 protocol 是后续所有 object-permanence eval 的母本。
- **2019-08, Bakhtin et al., PHYRE** ([arxiv:1908.05656](https://arxiv.org/abs/1908.05656))。Facebook AI 的 2D 物理 puzzle benchmark，强调 *one-shot* 物理推理（放一个红球解决目标）。虽然不是纯 object permanence，但首次把\"物体在时间上的连续轨迹\"作为 success criterion 显式写进 eval；当年最佳 model-based agent solved ≈37% [uncertain 具体数字]，纯 model-free 更差。
- **2021-06, Bear et al., Physion** ([arxiv:2106.08261](https://arxiv.org/abs/2106.08261))。MIT/Stanford 联合的 8-scenario 物理预测 benchmark（drop / collide / dominoes / containment 等），首次把人类参与者打分作为 ceiling 与模型 head-to-head 对比。结果：当时最好的 visual dynamics model（GNS、SlotFormer 之类）整体 ~55%，人类 ~80%；containment / occlusion 上的 gap 最大——这正是 object permanence 直接相关的子集。
- **2022-11, Smith et al., Physion++** ([unverified ID])。在 Physion 基础上加 *latent property inference*（质量、摩擦），把任务从\"看得见的物理\"推到\"看不见的物理\"——object permanence 在 occluder 后的 *身份保持* 是其中一个特例。结果：所有 vision model 在 latent property 上系统性回退到 chance。
- **2024-06, Motamed et al., Phyworld** ([arxiv:2406.03520](https://arxiv.org/abs/2406.03520) [unverified ID])。第一个公开针对 *generative* video model（Sora 类 + Stable Video Diffusion 类）的物理一致性 benchmark，明确把\"物体凭空出现/消失\"作为可计数 failure mode。报告里 Sora-class 模型在 ≥10s 视频上 object-vanish 率仍高于 30% [数字 uncertain，依赖具体版本]。
- **2024-10, Meng et al., PhyGenBench / PhyGenEval** ([unverified IDs])。把 Phyworld 思路扩展到 force / energy / motion 四个维度，并引入 VLM-judge + 人类对照的 hybrid scoring；同期 Kang et al. 复现报告：state-of-the-art 闭源 video model 在 \"long-occluder + multi-object\" 子集上 *没有* 显著优于 2022 baseline，提升主要来自纹理/光照而非世界变量。
- **2024-12, DeepMind Genie 2** (blog, 非 arxiv)。官方 demo reel 自承\"world consistency over long horizons remains a challenge\"，是工业界第一次在产品材料里把 object-permanence 局限明文承认。
- **2025 — V-JEPA-2** ([unverified arxiv ID])。LeCun 阵营给出在 EgoSchema / Something-Something-v2 上的 frozen-eval 提升，并附 small-scale 物理直觉 probe；但*没有*在 IntPhys / Physion 系列上公开 head-to-head——这一缺席本身就是判据：JEPA 路线若真在 object-level 上比 video-NTP 强，最该报的就是这组 benchmark。

把上述时间线压成一句话：**object permanence eval 在 2018–2022 期间是 model-based vision community 的内部度量，2024 之后才被 generative video / NTP 社区认领；而认领之后的所有公开数字都告诉我们，frame-level photorealism 与 object-level 持久性的提升速度不在同一个数量级**。这与 §视频暗线 末尾的判断完全对齐，但量化粒度更细：不是\"10–20 秒后失败\"这种轶事描述，而是\"在 IntPhys violation-of-expectation 上 plausibility margin 仍 <0.1 nats\"这种可逐版本追踪的数字（前提是有人愿意报）。

反例与可能突破：
- **3D-aware video diffusion** (Stable Video 3D, CAT3D 系列, 2024) 把显式 NeRF / Gaussian splat 几何先验注入 latent，部分场景下 object identity 持久性显著好转——但这相当于把 world-model 一半的负担外置给几何模块，不再是\"纯 video-NTP 自发涌现\"的证据。
- **Causal Transformer + slot attention** 路线 (Slot-Diffusion, OCVP 系列 [unverified IDs]) 在 Physion-style 任务上接近 human ceiling，但 slot 数与 object 数强耦合，open-world 上未验证。
- **真正的可证伪窗口**：如果 2026–2027 出现一个未注入显式几何 / slot 先验的 pure video-NTP 模型，在 IntPhys 全集 + Physion containment 子集上同时超过 2022 SlotFormer baseline 5 个百分点以上，则\"NTP 自发挤出 object-level 持久性\"这一假说就拿到了第一份强证据；反之每多一年 nothing happens，C-WM-2 (open-world dilution) 的强度就加深一档。

判断：object permanence 是当前唯一一把*同时被 cognitive-science / model-based vision / generative video* 三个社区公认有意义的尺子，把它接到 C-WM-3 的 interventional benchmark 上不需要任何新理论——只需要把 IntPhys / Physion 改造成 counterfactual triplet 形式（同一 prefix + 仅在 occluder 出现时刻 do-intervene 物体身份），即可一次性把 §视频暗线 + §反事实空洞 两节的开题问题落到一组可重复实验上。这也是 N6 (embodiment-and-vla-bet) §3 之后的最自然延伸点。

## JEPA 可辨识性这一条理论暗线 (2019–2026)

§object permanence 把度量推到 *变量级*，但还有一条更底层的问题没被本页系统化：**如果某个 SSL/NTP 目标真的学到了 world model，它在数学意义上"学到了"什么？**——这就是 representation identifiability 这一脉。它和 NTP 讨论的相关性是：identifiability 定理给出 \"在某类世界假设下，某目标 → latent 可被线性恢复\" 的 *条件性正面* 结果；只要把 NTP 与 JEPA-类 SSL 放到同一坐标下，就能定位 \"NTP 在哪一类世界上 *能* 被证明挤出 world model、在哪一类 *不能*\"。该问题原本是 ICA / nonlinear ICA 社区的内部话题，2023 之后才与 SSL / world-model 讨论合流。

- **2019-07，Khemakhem et al., *Variational Autoencoders and Nonlinear ICA: A Unifying Framework*** ([arxiv:1907.04809](https://arxiv.org/abs/1907.04809))：iVAE，证明在 *auxiliary variable* (类标 / 时间索引 / domain id) 条件下指数族 prior 的非线性 ICA 可被 identifiability 到 affine 变换。这是把 \"nonlinear ICA 不可识别\"（Hyvärinen–Pajunen 1999 不可能性定理）局部翻盘的第一个干净结果，奠定后来所有 SSL identifiability 工作的模板。
- **2021-02，Zimmermann et al., *Contrastive Learning Inverts the Data Generating Process*** ([arxiv:2102.08850](https://arxiv.org/abs/2102.08850))：InfoNCE 在球面均匀 latent + von Mises–Fisher 条件下可识别到正交变换。这是 *contrastive* SSL 的第一条 identifiability 定理，也是后续 SPHERE-JEPA 的直接精神先驱（同样把球面流形当作 first-class 几何假设）。
- **2022-04，von Kügelgen et al., *Self-Supervised Learning with Data Augmentations Provably Isolates Content from Style*** ([arxiv:2106.04619](https://arxiv.org/abs/2106.04619))：augmentation 设计被形式化为 *content/style partition*，并给出 block-identifiability 定理。该结果第一次把 "augmentation 是不是必要" 这种工程直觉抬升到 mech 命题，是 V-JEPA / I-JEPA 选择 masking-as-augmentation 的理论支撑之一。
- **2023-01，Assran et al., *I-JEPA*** ([arxiv:2301.08243](https://arxiv.org/abs/2301.08243))：LeCun 阵营给出 image 上的 joint-embedding predictive 实证，无 augmentation、无 contrastive、只做 masked latent prediction。论文本身 *不* 包含 identifiability 定理，只给经验下游性能；这一空白被 2026 年的 LeJEPA 补上。
- **2024-04，Meta, V-JEPA** ([arxiv:2404.08471](https://arxiv.org/abs/2404.08471))：video 模态延伸，frozen-eval 优于 video-MAE，但同样停在经验层。
- **2025–2026 一系列 JEPA-变体**（V-JEPA-2 [unverified arxiv ID]、Hierarchical-JEPA、Action-JEPA [unverified IDs]）：扩 modality、扩 scale；几乎全部仍是经验论文，未触及 identifiability。
- **2026-05-25，Klindt–LeCun–Balestriero, *When Does LeJEPA Learn a World Model?*** ([arxiv:2605.26379](https://arxiv.org/abs/2605.26379))：JEPA 一族 *首条条件性数学定理*。alignment + Gaussian regularization 在 *stationary additive-noise* 世界类下使 latent 被 linearly identifiable；并反向证 Gaussian 是 *唯一* 满足该 guarantee 的 latent prior（Euclidean 嵌入空间下）。
- **2026-05-27，SPHERE-JEPA** ([arxiv:2605.26900](https://arxiv.org/abs/2605.26900))：紧接着把 LeJEPA 的 Euclidean 假设打破——在 *球面流形* 上 Gaussian 不再最优，必须改为 hyperspherical uniform（与 Zimmermann 2021 的 vMF 结果遥相呼应）。两文联读，把 JEPA 路线从 \"统一 SSL 目标\" 推入 \"**latent 几何先验依生成假设而定**\" 的精细化阶段。

把这条暗线压成判断：到 2026 年 5 月为止，**identifiability 定理在 SSL 子社区是 \"哪类目标 → 哪类 latent 可被线性恢复\" 的精细分类，但在 NTP 主流讨论里几乎隐形**。这是 NTP 调研一个真实的方法论缺口——同期 text-NTP 这边可拿出的 identifiability 结果几乎为零（Vafa 2406.03689 的 Myhill–Nerode 等价类是 *state equivalence* 而非 *latent identifiability*；Othello-GPT 的线性可解码是 *存在性*经验证据而非 *识别性* 定理）。

反例与待证伪点：
- **identifiability 定理是 *条件性* 的，不能跨假设外推**。LeJEPA 双定理在 \"stationary additive-noise + Euclidean 嵌入\" 下成立，SPHERE-JEPA 已展示 (Euclidean) 失效；任何真实 embodied 世界（非平稳、状态相关噪声、流形结构混合）目前都不被任一已知定理覆盖。把 LeJEPA 当作 \"JEPA 通用优于 NTP\" 的证据是过度外推。
- **未被识别的 latent ≠ 没学到 world model**。Othello-GPT、chess-Transformer 都没有 identifiability 定理护航，但 probe 证据强；反过来 identifiability 定理也只是 *充分条件*。
- **真正的可证伪窗口**：找到一个 NTP-only（纯像素/帧 next-token，无 JEPA 风格 latent target）的训练目标，在 LeJEPA 同一类世界假设下被证明 latent linearly identifiable——这将直接把 paradigm-replacement 路线击穿。目前 NTP-side 没有这样的定理，但也没有 *不可能性* 证明，这是开放问题。

判断：JEPA-identifiability 这条线值得每月追踪两到三篇，是 N6 §3 \"world-model 三家答卷\" 在 2026 下半年写作时唯一接近 *形式可证* 的子带。但要诚实标注：identifiability 定理给的 \"学到 world model\" 是非常 *狭义* 的——只是 latent 与真实潜变量之间存在 affine/orthogonal 对应，并不蕴含因果结构（这又把球扔回 §C-WM-3 反事实 eval）。把这两条线 *分开* 报告比合起来吹更负责任。

## 反事实 / 干预 eval：当前最大的方法论空洞

把上一节末尾那句"没有任何一篇 video world-model 论文做过 do-operator 干预下的预测一致性 eval"翻成 Pearl 的语言：当前所有公开 world-model benchmark 几乎全部停留在 Layer 1（observational）—— 给 prefix 预测续帧或下一动作 —— 而真正能区分"模型有 world model"vs"模型在做高阶 n-gram"的关键证据，是 Layer 2（interventional）的预测一致性。这一空洞不是"还没人想到"，而是工程上比 observational eval 难一个数量级，目前只有零散候选：

- **2023-11，Kıcıman et al., *Causal Reasoning and Large Language Models: Opening a New Frontier for Causality*** ([arxiv:2305.00050](https://arxiv.org/abs/2305.00050))。在 *text* 上系统测 LLM 的 counterfactual reasoning，结论是 GPT-4 在 pair-wise causal direction 上达到 SOTA 但在 counterfactual generation 上系统性 fail。这一结果是 text-NTP 的，但提供了 video-NTP 应该照搬的 protocol 模板。
- **2024-02，Vafa et al.** ([arxiv:2406.03689](https://arxiv.org/abs/2406.03689))。其 Myhill–Nerode 度量本质上是 *intra-model state equivalence* 的等价类检验，可以视为"半-interventional"——它问的不是 do(X) 后的 rollout，而是 internal state 在等价输入上是否被识别为同一类。这是目前最接近 Layer-2 的 NTP world-model eval。
- **2024-06，Brinkmann et al., *A Mechanistic Analysis of a Transformer Trained on a Symbolic Multi-Step Reasoning Task*** ([arxiv:2402.11917](https://arxiv.org/abs/2402.11917) [unverified ID])。在小规模 transformer 上用 activation patching 做 *causal mediation analysis*——这是 mech-interp 社区把 do-operator 真正落地到神经网络内部的标准做法，但还没人把同一套 patching scheme 搬到 video world model 上。
- **2025 — Phyworld / PhyGenBench / WorldSimBench 等物理 video benchmark**（[unverified] 多篇 2025 工作）：开始报"违反物理"率，但仍是 marginal observational metric，不构造 *counterfactual pair*（同一 prefix + 仅在某一物理参数上 do-intervene 的两段视频）。

把这些拼起来，可以勾勒出一个**还没有人做过、但 2026–2027 完全可做**的实验设计：取 Genie 3 / Cosmos / Sora 3 类 latent-action 世界模型，构造一个 counterfactual triplet benchmark $\{(s, a, s'), (s, \text{do}(a'), s'')\}$，其中 $a, a'$ 仅在某一物理可控变量（速度/方向/重力/碰撞）上不同；衡量模型 rollout 在 (a) 边际似然、(b) latent state 同构、(c) downstream 物理一致性三个层面的 ATE。**如果 video-NTP 真的学到了 world model，这三个量必须 *联合* 与 ground-truth simulator 一致；如果只学到了 frame-level dynamics，则 (a) 可对、(b)(c) 必然脱钩**。这是把 §视频暗线 的"行为级 vs 表征级 vs 因果级"三分法在单一 benchmark 上落地的最干净路径。

## C-WM-3：interventional consistency 作为强 mech 判据

**C-WM-3 (interventional rollout consistency)**：存在一个 simulator-backed counterfactual benchmark $\mathcal{B}_{\text{do}}$，对任意 video-NTP world model $M$ 与人为可控物理变量 $X \in \{v, \theta, g, \mu\}$，定义 ATE 误差

$$\varepsilon_{\text{do}}(M, X) = \mathbb{E}_{s,a}\bigl\|\mathbb{E}_M[s'\mid s,\text{do}(X{=}x)] - \mathbb{E}_{\text{sim}}[s'\mid s,\text{do}(X{=}x)]\bigr\|.$$

强 mech 假设：**∀ 仅在像素 / latent frame 上做 NTP 训练（无 simulator-backed counterfactual supervision）的 $M$，$\varepsilon_{\text{do}}(M, X) \gg 0$ 且不随训练 token 数衰减**。

- **可证伪条件**：找到一个 video-NTP $M$，在某个非平凡 $X$ 上 $\varepsilon_{\text{do}}(M, X) \to 0$，且与 observational eval 上的 $M$ *同一权重*——后一条件排除"换一个 fine-tuned 头"的 escape。
- **与 C-WM-1 的区别**：C-WM-1 是 *closed-world observational*（Othello/chess 上 NTP 自然挤出状态），C-WM-3 是 *open-world interventional*（video 上 NTP 是否能挤出 *因果* 状态而不只是 *关联* 状态）。从 Pearl 阶梯看，C-WM-1 在 Layer 1.5，C-WM-3 在 Layer 2。
- **与 [causality](causality.md) C-CAUSAL-1 的关系**：C-CAUSAL-1 押的是 text-NTP 在反事实问答上的失败；C-WM-3 把同一假设搬到 video 模态。两者若同时被证伪，则"NTP 选不出因果结构"这一 mech 命题需要整体重写。
- **当前状态**：simulator-backed counterfactual triplet benchmark *尚不存在*；最接近的资源是 Brax / MuJoCo / Isaac Sim 这些可程序化生成 counterfactual 的 simulator + Phyworld 类 observational eval 的拼接。该条目当前评估为 **medium**：理论清晰、benchmark 缺位、工程可行。

判断：C-WM-3 是当前 NTP-world-model 讨论里**最有可能在 18 个月内一锤定音**的候选——既不像 C-WM-2 那样依赖整个开放语料的统计论证（不可证伪），也不像 C-WM-1 那样停留在玩具 closed-world（可证伪但已被证实，没有新信息量）。Genie 3 / Cosmos 这一代模型权重不公开但 API 可调，足够做 counterfactual triplet 的 black-box ATE 估计；real bottleneck 在 benchmark 设计者，不在模型能力。

## 诚实判断

到 2026 年 5 月为止，三种 "world model" 的 NTP 兼容性大致是：第 2 种（表征同构）在 closed-world 上 *被证明存在*，在 open-world 上 *被证明稀疏且碎片化*；第 1 种（行为规划）目前最好的实例不是 LLM 而是 DreamerV3 与 MuZero 这类专用 model-based RL，video-NTP 是有希望的旁支；第 3 种（反事实/因果）几乎没有 NTP 自发挤出的证据，必须靠显式 reasoning trace 外接（见 [causality](causality.md) §C-CAUSAL-1）。

把这三件事混着说 "LLM 有/没有 world model" 是当前 discourse 最大的浪费。下一个真正能推进的实验是：在一个 *中等复杂度* 的 open-world 子集（比如 NetHack、Minecraft 文本子集、或可验证的城市路径数据）上，同时跑 NTP-only、NTP + Dreamer-style latent loss、NTP + 显式 state annotation 三个 setup，比较 probe accuracy 与 OOD 规划性能。已有零散工作但还没有公认 benchmark。

## NTP-vs-JEPA head-to-head benchmark 真空 (2023–2026)

§JEPA 可辨识性 那一节把 paradigm-replacement 路线推到了「条件性数学定理」阶段，但有一件事整个 2023–2026 文献都在系统性回避：**没有一篇公开论文把 NTP-style 与 JEPA-style 目标放在 *同一数据集、同一参数量、同一 token 预算、同一 downstream eval* 下做 head-to-head 比较**。这是判断「JEPA 是否真比 NTP 多挤出 world model」的最小必要实验，至今未做。把这条缺席整理出来，本身就是 §诚实判断 末尾「公认 benchmark 缺失」的具体化。

- **2023-01 I-JEPA ([arxiv:2301.08243](https://arxiv.org/abs/2301.08243))** 的 baseline 是 MAE / data2vec / iBOT 这一族 masked-image SSL，**不是** 像素级 next-frame NTP。LeCun 在 podcasts 里反复说「autoregressive 已经被证伪」，但论文 eval 表里没有任何一个 cell 是 *同等算力下* 跑了 video-NTP baseline 的。
- **2024-04 V-JEPA ([arxiv:2404.08471](https://arxiv.org/abs/2404.08471))** 的对照组是 video-MAE 与 OmniMAE，仍然回避 video-NTP。论文附录承认「a fair comparison to autoregressive video models is left for future work」——这个 future work 到 2026-05 没有出现。
- **2024-02 Sora 技术报告**（非 arxiv）反方向同样回避：把自己定位为 «world simulator» 但没和 V-JEPA 在任何 frozen-probe benchmark 上 head-to-head；OpenAI 公布的 eval 集中在 video quality（FVD / 主观打分）而非世界变量的 probe accuracy。
- **2024–2025 一波 video foundation model**（VideoPoet [arxiv:2312.14125](https://arxiv.org/abs/2312.14125)、Cosmos whitepaper [unverified ID]、Open-Sora 各 fork）几乎全部只报 generation quality，没人报 IntPhys / Physion / SlotFormer 上的 head-to-head probe——这正是 §object permanence 一节列的那把尺子的应用空缺。
- **2026-05 LeJEPA ([arxiv:2605.26379](https://arxiv.org/abs/2605.26379))** 给了 JEPA 一族第一条 identifiability 定理，但实证部分仍是 pixel robotics control 上的 latent planning，**没有** 与同 backbone 的 video-NTP 对照。SPHERE-JEPA ([arxiv:2605.26900](https://arxiv.org/abs/2605.26900)) 同月，同样缺席。

把这条缺席压一句：**「JEPA 比 NTP 更适合学 world model」目前是 *理论 + 局部经验* 的双重间接论据，没有任何一个公开实验在 controlled head-to-head setup 下直接量化二者差距**。这与 [reasoning](reasoning.md) §Garcia format-confound、[embodiment](embodiment.md) §评测协议退却线、[scaling_limits](scaling_limits.md) §流形扩张 一脉相承——都是同一种「缺失 confound 控制的 benchmark 真空」在不同 topic 上的化身。

新增候选 (corollary，不升主表)：

- **C-WM-4 — Head-to-head paradigm benchmark deficit**：在 fixed (backbone arch, param count, training token budget, downstream probe set) 四元约束下，video-NTP 与 V-JEPA-class objective 的 world-model probe 差距未被任何公开实验测量。**Falsification**：出现一篇 (a) 两条 objective 共享同一 backbone 与 token 预算、(b) downstream eval 同时包含 IntPhys / Physion / counterfactual triplet 三类、(c) 报告每类指标 ±2pp 置信区间的论文。**当前评估**: 不是 mech 命题本身，而是 *元-方法论命题*——下一次 C 任务时建议在 §10 survey 候选列表中以 corollary 形式登记（不进 taxonomy 主表），与 C-WM-3 的 benchmark 缺失互为镜像。

## Open problems

把上文 §C-WM-1 / §C-WM-2 / §C-WM-3 / §C-WM-4 与 §object permanence / §JEPA 可辨识性 / §反事实 eval 三条暗线交叉后，2026-05 视角下 world-model 议题剩下五个**已被清晰提问、但公开文献尚无收敛答案**的硬开题。每条都附最小可证伪实验与最近一次公开尝试，避免落入「open problem 罗列」的占位陷阱。

- **OP-WM-1 — open-world Othello**：是否存在一个 *中等开放* 的序列生成任务（候选：NetHack 子集、Minecraft chat+action 子集、可验证城市路径数据），在该任务上 NTP-only training 能让 linear probe 以 ≥95% 准确率恢复 *非平凡* 世界状态？目前最接近的资源是 Vafa 2024 ([arxiv:2406.03689](https://arxiv.org/abs/2406.03689)) 的纽约出租车 setup，但其结论是 *probe accuracy 高 + state graph 不同构*——这恰恰是开题，不是答案。**Falsification window**: 6–12 个月，需一个公开 backbone + 公开 probe 协议。
- **OP-WM-2 — video Othello-GPT**：在 Genie 2 / Cosmos / Sora-class latent-action 模型上做 Hazineh 2023 ([arxiv:2309.07815](https://arxiv.org/abs/2309.07815)) 风格的线性可解码 probe，目标变量是 object identity / position / velocity。如果能拿到 1.7% 错误率档的可解码性，C-WM-1 的边界就从 closed-world 外推到 mid-open-world。**当前距离**: 工程上完全可做（API black-box probe 足够），社会学上无人有动机做——闭源厂商不愿暴露 latent，开源团队没有 Genie 量级模型。
- **OP-WM-3 — counterfactual triplet benchmark**：把 IntPhys / Physion 改造成 $\{(s,a,s'),(s,\text{do}(a'),s'')\}$ 形式，让 video world model 在 *同一权重* 下报告 observational 与 interventional 两个分数。这是 §C-WM-3 的最小工程实例。**Falsification window**: 12–18 个月，bottleneck 在 benchmark 设计者而非模型能力；如果到 2027-Q4 仍无此 benchmark 公开，则 video-NTP world-model 的因果维度将继续停留在 §反事实 eval 末尾描述的方法论空洞中。
- **OP-WM-4 — fair JEPA-vs-NTP comparison**：即 C-WM-4 的实验落地。最小可行版本：在 Something-Something-v2 上用同一 ViT-L backbone、同一 token 预算分别跑 V-JEPA loss 与 next-frame patch NTP loss，下游用 frozen-probe + IntPhys violation-of-expectation。**当前距离**: 已具备所有条件（V-JEPA 代码开源、video-NTP baseline 多家可复现），只缺一个无 paradigm 立场的中立团队做这件事。FAIR 与 OpenAI 都有结构性利益不做。
- **OP-WM-5 — reasoning trace 是否真在外接 world model**：reasoning-model（R1、o3）把状态写到 scratchpad 上，但 Turpin 2023 ([arxiv:2305.04388](https://arxiv.org/abs/2305.04388)) 已证 CoT 与内部计算可不一致。开放问题：是否存在一组任务，使 (a) 模型给出正确答案、(b) scratchpad 显式列出关键中间状态、(c) activation patching 显示该中间状态 *不存在* 于内部表征？这是把 §反例与上界突破 末尾的 Turpin 怀疑推到 mech-interp 可测层面的最小协议。**Falsification window**: 6–12 个月，mech-interp 社区已具备 activation patching 标准工具（Brinkmann 2024 [arxiv:2402.11917](https://arxiv.org/abs/2402.11917) [unverified ID]），只需把 protocol 跨过 closed-world toy 到 frontier reasoning model 这一跳——后者闭源是主要 friction。

把这五条压成一个元判断：**world-model 议题的 2026 瓶颈不在新模型 / 新理论，而在 benchmark 设计与跨阵营对照实验的缺失**。OP-WM-2 / OP-WM-3 / OP-WM-4 都是工程 <1 GPU-week 的实验，但每一个都因「报告方向不利于自己阵营」而无人愿做——这与 [causality](causality.md) §RL-from-environment 三个 <1 GPU-week 实验缺失 / [reasoning](reasoning.md) §C-REAS-5 双段相变测量缺失同型。下一次 NTP-deepen 在 world_model.md 上的实质性更新，最有可能来自这五条 open problem 中任意一条被外部团队做掉——而不是又一篇 Sora-class 模型发布。

## Cross-links

- [causality](causality.md) — 第 3 种 world model 与 Pearl Layer 2/3；C-WM-3 与 C-CAUSAL-1 共享反事实失败的根
- [grounding](grounding.md) — world model 需不需要 sensorimotor 接地
- [embodiment](embodiment.md) — Genie / robotics 路线；§评测协议退却线 与 §object permanence 同型
- [reasoning](reasoning.md) — reasoning trace 作为外置 world model；OP-WM-5 是这条桥的 mech-interp 检验
- [scaling_limits](scaling_limits.md) — §流形扩张 与 §JEPA 可辨识性 在「benchmark confound 控制不足」上同型
- [online_learning](online_learning.md) — world model 的时间维度更新失败即 §online_learning 的 cutoff bottleneck
- 候选 mech 入口：`survey/taxonomy.md` C-WM-1, C-WM-2, C-WM-3；C-WM-4 仅在 §10 候选列表登记为 corollary
