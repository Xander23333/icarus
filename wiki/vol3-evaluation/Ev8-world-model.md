# 世界模型评测 (World Model Benchmarks)

## 路线定位

到 2026-05，「世界模型」eval 仍处在 **没有事实标准** 的状态——和 Ev1/Ev3 那种「报 MMLU/SWE-Bench 就行」的成熟度差一个数量级。原因很简单：world model 这个词同时被三拨人用——(1) **video generation** 圈（Sora / Veo / Kling / Wan / Hunyuan / Movie Gen 等）把 text-to-video / image-to-video 当 world simulator 卖；(2) **playable / interactive 世界** 圈（GameNGen、Genie 2/3、Oasis、DeepMind SIMA-style）把 action-conditioned next-frame prediction 当 world model；(3) **embodied / robotics** 圈（1X World Model、NVIDIA Cosmos、Wayve GAIA-2、V-JEPA 2）把 future-prediction backbone 当 policy 的 latent simulator。三拨人的评测互不通用。本节按这三层梳理 2026-05 能用的 benchmark，明确指出 **大部分轴还在「靠 cherry-pick demo + VLM-as-judge」的阶段**，并给 Qwen-VL/Qwen-Video 团队一个最小可信组合。

## 代表 benchmark 清单

| Benchmark | 出处 | 测什么 | 状态 (2026-05) |
|---|---|---|---|
| VBench / VBench++ | arxiv [2311.17982](https://arxiv.org/abs/2311.17982), CVPR'24；扩展 [2411.13503](https://arxiv.org/abs/2411.13503) | text-to-video，16 维度 × 自动指标 | T2V 圈事实标准，已被广泛 game |
| VBench-2.0 | arxiv [2503.21755](https://arxiv.org/abs/2503.21755) (2025-03) | 「intrinsic faithfulness」5 大维 18 子维：常识、物理、人类、创造力、可控性 | 下一代 T2V eval，2026 起 frontier 报数转向它 |
| Physics-IQ | arxiv [2501.09038](https://arxiv.org/abs/2501.09038) (2025-01, Google DeepMind) | 396 真实拍摄场景的「物理后续帧预测」 | 当前最严肃的 **物理一致性** 测法 |
| VideoPhy / VideoPhy-2 | arxiv [2406.03520](https://arxiv.org/abs/2406.03520)；v2 [2503.06800](https://arxiv.org/abs/2503.06800) | 物理常识 prompt 集 + VLM judge | 与 Physics-IQ 互补，更便宜 |
| WorldModelBench | arxiv [2502.20694](https://arxiv.org/abs/2502.20694) (2025-02, MIT/Adobe) | 7 domain × instruction following + physics, 350 human-rater | 目前最接近「跨 domain world model」总分 |
| WorldScore | arxiv [2504.00983](https://arxiv.org/abs/2504.00983) (2025-04) | 3D/4D/video gen 统一为 next-scene generation, 3000 prompt | 偏 3D / camera-controllable 这一支 |
| GameNGen eval | arxiv [2408.14837](https://arxiv.org/abs/2408.14837) (Google, 2024-08) | DOOM neural simulator：PSNR + LPIPS + 人类 5s/30s 真假辨别 | 单游戏 closed-loop，行业引用最多的 playable 案例 |
| Genie 2 / Genie 3 | DeepMind blog [Genie 2](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/) (2024-12), [Genie 3](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) (2025-08) | action-conditioned playable world, minutes-scale consistency | **没有公开 benchmark**，全靠 demo + 内部 eval |
| Cosmos Predict / Reason eval | NVIDIA [Cosmos paper](https://arxiv.org/abs/2501.03575) (2025-01) | physical AI 用 video world model 的 downstream policy 提升 | embodied 侧，绑 Isaac Lab |
| V-JEPA 2 | Meta [arxiv 2506.09985](https://arxiv.org/abs/2506.09985) (2025-06) | self-supervised video latent + 下游 action / planning | 不报 pixel quality，报 latent probing + robot success rate |
| 1X World Model Challenge | 1X blog [worldmodel](https://www.1x.tech/discover/1x-world-model) (2024-09) + Kaggle | humanoid first-person video forecasting | 唯一公开的 humanoid embodied world model 公测 |

## 三层分别讲

### Layer 1：video generation 当 world simulator

#### VBench / VBench++（事实标准但已被 game）
- 把 T2V 质量拆 **16 维**：subject consistency, background consistency, temporal flickering, motion smoothness, dynamic degree, aesthetic quality, imaging quality, object class, multiple objects, human action, color, spatial relationship, scene, appearance style, temporal style, overall consistency [arxiv 2311.17982](https://arxiv.org/abs/2311.17982)。每维用一个**预训好的小模型**（DINO/CLIP/RAFT/GRiT/UMT/LAION-Aesthetic 等）给分，然后加权出总分。
- 优点：全自动、可复现、覆盖广。**问题**：每个子指标的 proxy model 都能被反向利用——比如 motion smoothness 用 RAFT optical flow 的 variance，**直接降低 motion magnitude 就能拉分**；这也是 VBench-2.0 论文里点名的 "extrinsic faithfulness only" 批评。
- 实操：到 2026 头部商用模型（Veo 3、Sora 2、Kling 2.5、Wan 2.5、Hunyuan Video 2、MovieGen）VBench 总分都挤在 83–88 之间，1pt 差距已无意义。看子维 radar + 与 VBench-2.0 联报 才有信息量。

#### VBench-2.0 —— 2025-03 后的新基准
- 5 大维 18 子维：**Human Fidelity**（anatomy / identity / clothing）、**Controllability**（camera motion / dynamic spatial relation / dynamic attribute / motion order / complex landscape / complex plot）、**Creativity**（composition / instance preservation）、**Physics**（mechanics、material、thermotics、multi-object interaction）、**Commonsense** [arxiv 2503.21755](https://arxiv.org/abs/2503.21755)。
- 关键变化：从 VBench 的「pixel/aesthetic proxy」转向 **VLM-as-judge + 专家小模型 hybrid**，并把 physics 单拎出来。论文显示在 VBench 上贴近的 Sora / Kling / Gen-3 在 VBench-2.0 physics 维上分化到 30–50% 区间。
- 评测建议：2026 起的 T2V tech report **必须报 VBench-2.0 physics 与 commonsense 子分**；单 VBench 总分已无 frontier 区分度。

#### Physics-IQ —— 目前最严肃的物理一致性
- DeepMind 2025-01 放出的 396 段真实拍摄视频，**每段同位置/光照拍 2 take 当人类上界**，模型给前 3s，要求生成接下来 5s [arxiv 2501.09038](https://arxiv.org/abs/2501.09038)。
- 用 4 个 metric（spatial IoU、spatiotemporal IoU、weighted spatial IoU、MSE）打分，最后归一到 **Physics-IQ score**（人类 take 2 ≈ 100%）。
- 论文报：Sora 10%、Runway Gen-3 11%、Lumiere 23%、VideoPoet 29.5%、Stable Video 24%，**最强也只到人类 30%**——说明 2024–2025 video model 物理还很差，且 **视觉真实感与物理一致性弱相关甚至 0 相关**（Pearson r ≈ 0.06）。
- 2026 更新：[uncertain] 论文 leaderboard 持续更新 Veo 3/Sora 2，但官方数字未单列，参考 [Physics-IQ project](https://physics-iq.github.io/)。
- 评测建议：Physics-IQ 是目前唯一**几乎没法 game** 的 world-model physics 测法（需要真拍 ground-truth 后续帧），frontier video 必报。

#### VideoPhy / VideoPhy-2
- VideoPhy [arxiv 2406.03520](https://arxiv.org/abs/2406.03520) 用 688 个物理 prompt（solid-solid、solid-fluid、fluid-fluid interaction）+ 人类打 PC (physical commonsense) 与 SA (semantic adherence) 两分。VideoPhy-2 [arxiv 2503.06800](https://arxiv.org/abs/2503.06800) 扩到 3940 prompt，加自动 evaluator (VideoCon-Physics)。
- 与 Physics-IQ 互补：Physics-IQ 要 future prediction (i2v + 续帧)，VideoPhy 是纯 t2v + judge。**便宜，但 judge 漂移问题与 MM-Vet 一样**——VideoPhy-2 论文承认 evaluator 与人类 agreement 只有 ~70%。

### Layer 2：综合 world model benchmark（跨 domain 尝试）

#### WorldModelBench
- MIT + Adobe 2025-02 提出，覆盖 7 domain（**driving、robotics、industrial、indoor、natural、game、human activity**）, 350 video × 多模型 × **人类打 3 轴**：instruction following、common-sense、physics adherence [arxiv 2502.20694](https://arxiv.org/abs/2502.20694)。
- 关键贡献：训了一个 **judger 模型** (3B) 微调到 human label 上，Pearson 0.85，**比 GPT-4o-as-judge 更稳**且便宜。
- 测了 14 个 OS / 商用模型：发现 ① physics 是普遍短板，**没有模型超过 50%**；② driving / robotics domain 反而比 game domain 更难（OOD）；③ 模型规模 ≠ physics 提升。
- 2026-05 状态：[uncertain] 是否已被 Veo 3 / Sora 2 / Wan 2.5 等正式报数 —— 截至成稿主要仍是研究圈内引用，未进入大厂 system card。

#### WorldScore
- 2025-04 提出，把 3D scene gen / 4D scene gen / video gen 统一到 **next-scene generation**：给当前场景 + camera 轨迹 / action，要求模型给下一段 [arxiv 2504.00983](https://arxiv.org/abs/2504.00983)。
- 3000 prompt，分 controllability / quality / dynamics 三轴。优点是把 3D Gaussian Splatting 类、video diffusion 类、playable world 类拉到同一张表上——但**正因为太通用，每一类都不一定服气**。

### Layer 3：playable / interactive world

#### GameNGen
- Google 2024-08 用 SD 1.4 backbone + RL agent 收集的 DOOM 帧/动作对，做 **action-conditioned next-frame diffusion** [arxiv 2408.14837](https://arxiv.org/abs/2408.14837)。
- Eval 三个轴：
  1. **PSNR / LPIPS** vs 真实游戏帧（20fps simulated）—— PSNR 29.4, LPIPS 0.249。
  2. **人类辨别测试**：5s 和 30s 片段，让 10 raters 区分真 DOOM vs 神经模拟，正确率分别 58% / 60%——**只略高于随机 50%**（这是论文最常被引用的卖点）。
  3. 长 horizon drift：auto-regressive 推理 N 步后用辅助 model 检查游戏状态一致性。
- 影响：**确立了「人类真假辨别 + horizon drift」作为 playable world model 的 de-facto eval**，后续 Oasis (Decart, 2024-10)、Genie 2/3 都在自己 blog 里报类似数字。

#### Genie 2 / Genie 3 —— 没有公开 benchmark
- Genie 2 [DeepMind blog 2024-12](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/)：foundation world model，单张图 → playable 3D 世界，consistency 「up to a minute」。
- Genie 3 [DeepMind blog 2025-08](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/)：720p, **multi-minute** 交互，「promptable world events」。
- **eval 完全是 demo 驱动 + 内部 user study**：没放任何数字、没放复现 protocol、没放对比表。这是 frontier playable world model 的普遍状态——**Layer 3 目前没有任何公开可复现 benchmark**。
- 第三方 proxy：Oasis (Decart/Etched) 把 weight 公开了，社区做了一些 horizon drift 复测 [uncertain]，但都不算 benchmark。

#### Embodied / robotics 侧
- **NVIDIA Cosmos** [arxiv 2501.03575](https://arxiv.org/abs/2501.03575)：Cosmos-Predict (diffusion + autoregressive 两条线) + Cosmos-Reason。eval 重点在 **下游 robot policy success rate** 而非 pixel quality——这与 Physics-IQ 哲学一致：world model 好不好看 downstream task。
- **V-JEPA 2** [arxiv 2506.09985](https://arxiv.org/abs/2506.09985)：1B param self-supervised video JEPA，**不报 pixel reconstruction**，报 ① frozen probing on Something-Something v2 / Kinetics / EPIC-Kitchens action anticipation；② post-train V-JEPA 2-AC 做 robot pick-and-place success rate (Franka arm)。LeCun 系一贯的「pixel 是 distraction」立场。
- **1X World Model Challenge** [1X blog](https://www.1x.tech/discover/1x-world-model)：humanoid 第一人称视频 + action token，公开 dataset + Kaggle compensated leaderboard，metric 是 future-frame prediction loss。是 humanoid 圈第一个真正公开的 challenge。
- **Wayve GAIA-1 / GAIA-2** [GAIA-2 blog](https://wayve.ai/thinking/gaia-2/) (2025-03)：driving world model，eval 是 driving-specific（lane keeping、agent behavior plausibility），与通用 video gen benchmark 不接轨。

## 主要争议与坑（重点）

1. **「world model」定义不统一是评测乱的根**。Layer 1 把 pixel quality 当 proxy（VBench），Layer 2 想做 physics-aware judge（WorldModelBench / VideoPhy），Layer 3 关心 closed-loop 可玩性（GameNGen）。**没有任何 single number 能跨层比较**——任何「Sora vs Genie 3 谁是更好的 world model」的横评目前都是胡说。
2. **VLM-as-judge 是当前 physics/commonsense 评测的主力，但远未稳**。VideoPhy-2 自报 evaluator vs human 一致率 ~70%，MM-judge 漂移问题（见 Ev5、Ev10）在视频侧更严重——视频 judge 还得吃帧采样、temporal aggregation 两层方差。
3. **Physics-IQ 的「视觉真实 ≠ 物理真实」 (Pearson r ≈ 0.06)** 是 2025 最重要的实证结论之一。意味着 **VBench 高分根本不能保 physics**，过去两年「Sora 的世界模型涌现」类叙事在此 benchmark 下被打回原形。
4. **VBench 已被广泛 game**：motion smoothness、temporal flickering 这类基于 optical flow 的 proxy 可被「降低动态」直接刷分。Wan / Hunyuan / Pika 等开源模型 tech report 报 VBench 时若不附 dynamic degree 子分，基本可以当作 cherry-pick。
5. **Layer 3 完全没有公开 benchmark**。Genie 2/3 / Oasis / V-JEPA 2-AC 都是 demo + 自报数字，**「无法被独立证伪」**。读者做 Qwen-Video / Qwen-Embodied 评测时，如果声明 playable world，建议自己出一个小型 horizon-drift 测法（哪怕只是 GameNGen 的 30s 人类辨别复刻）。
6. **embodied / robotics 评测的 sim-to-real gap**：Cosmos / V-JEPA 2 报的下游 robot success 高度依赖具体 task suite（RoboCasa / LIBERO / Franka pick-and-place），跨 suite 不可比；且公开 robot benchmark 本身样本量小、方差大。
7. **Long-horizon consistency 是公共空白**。Genie 3 报「multi-minute」但无定量；GameNGen 报到 30s；学术界目前没有 >1min 的 closed-loop world-model benchmark。这是 2026 下半年最值得做的 eval 方向之一。

## 推荐 protocol（针对 video / world model 团队）

如果你要在 tech report 里报「我们是 world model」，2026-05 的最小可信组合：

- **T2V quality**：VBench (全 16 维 radar，不要只报总分) + VBench-2.0 (尤其 physics + commonsense 子分)
- **Physics**：Physics-IQ (i2v 续帧) + VideoPhy-2 (t2v + 自动 judge)
- **跨 domain world**：WorldModelBench (7 domain, 用其官方 judger 模型)
- **如果 claim playable**：自己复刻 GameNGen 的 5s/30s 人类辨别 + horizon drift；至少在一个 closed-loop 环境上跑
- **如果 claim embodied**：必须报下游 robot/driving policy success rate，不能只报 pixel quality（参考 V-JEPA 2 / Cosmos）

每项报数附带：(a) 采样 step / cfg、(b) 分辨率与帧率、(c) 上下文长度 / 续帧条件、(d) judge 模型版本（VBench-2.0/VideoPhy-2 都吃 VLM judge）、(e) 是否做 prompt rewrite。

## 未知与争议

- **Veo 3 / Sora 2 / Kling 2.5 在 VBench-2.0 与 Physics-IQ 的官方分数** —— Google / OpenAI / Kuaishou 的 model card 均未一致披露 [uncertain]，参考第三方 [Artificial Analysis Video Arena](https://artificialanalysis.ai/text-to-video) 与 [VBench leaderboard](https://vchitect.github.io/VBench-project/)。
- **Genie 3 vs Oasis 的定量对比** —— DeepMind 未给数字，社区也无独立测评 [unknown — 没找到一手 source]。
- **WorldModelBench 是否会成为下一代事实标准** —— 2026-05 还在「论文发布 < 6 个月、大厂尚未引用」状态 [uncertain]。
- **V-JEPA 2 与 diffusion video model 的「哪个更适合 world model」之争**：LeCun 主张 latent JEPA、OpenAI/Google 主张 pixel diffusion，目前**没有公平 benchmark 能裁决**——双方测法都不一致 [开放问题]。
- **Long-horizon (>1min) closed-loop benchmark** —— 公认空白，无 SOTA 也无 dataset [unknown]。

## 推荐外部材料

- [VBench leaderboard](https://vchitect.github.io/VBench-project/) — VBench 1 + 2 官方榜，每月更新一次。
- [Physics-IQ project page](https://physics-iq.github.io/) — 含可下载数据集与 evaluator 脚本，是目前最干净的 physics 测法。
- [VBench-2.0 paper (arxiv 2503.21755)](https://arxiv.org/abs/2503.21755) — 必读，定义了「intrinsic faithfulness」框架，对 VBench 1 的批评在第 2 节。
- [WorldModelBench (arxiv 2502.20694)](https://arxiv.org/abs/2502.20694) — 第一个认真做跨 domain world model judger 的工作。
- [GameNGen paper (arxiv 2408.14837)](https://arxiv.org/abs/2408.14837) — playable world model eval 的 reference 模板。
- [Genie 3 blog](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) — frontier playable world model 的现状（同时也是「为什么 Layer 3 还没 benchmark」的代表）。
- [V-JEPA 2 (arxiv 2506.09985)](https://arxiv.org/abs/2506.09985) — Meta 的 non-pixel world model 路线，eval 哲学完全不同，值得对照阅读。
- [Artificial Analysis Video Arena](https://artificialanalysis.ai/text-to-video) — 商用 video model 价格-质量-速度散点，做选型最快。
