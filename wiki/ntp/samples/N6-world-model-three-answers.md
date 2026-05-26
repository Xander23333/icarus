# World model = 视频生成？三个团队的三种答案

> NTP 候选样章 N6。作者 Xander Xu。本篇尝试把 2024 年初一周之内连续放出的三份工作——OpenAI 的 Sora、Google DeepMind 的 Genie、Meta FAIR 的 V-JEPA——摆到同一张桌面上，看这三家在「视频建模 = 世界模型」这件事上分别下了哪种性质完全不同的赌注，以及到 2026 年 5 月为止赌局的中间比分。

## 一、2024 年 2 月那一周：三份相互矛盾的世界模型宣言

2024 年 2 月 15 日，OpenAI 在博客上挂出一篇标题写得非常张扬的技术报告——*Video generation models as world simulators*（作者 Tim Brooks、Bill Peebles 等，无 arxiv 编号，只有 openai.com 上的 tech report 与一组 demo 视频）。这不是 paper，是 demo。十几段最长 60 秒、1080p 的视频里，无人机视角的东京街道、显微镜下的细胞分裂、戴墨镜的猛犸象走过雪原，每一段都在视觉上让人挑不出毛病。报告里只给了非常稀薄的实现细节——一个 patch-based 的 diffusion transformer，把视频在 spatiotemporal 维度上切块再展平、按时间顺序训练，规模与训练数据量都没有披露。但博客那句副标题——\"We explore large-scale training of generative models on video data\"——和正文里那句 \"continued scaling of video models is a promising path towards building general purpose simulators of the physical world\" 把范式赌注摆得很清楚：**只要视频生成模型足够大，它就会自发学到世界**。这是把 GPT-3 那一套 \"scale 即智能\" 的信念直接平移到像素流上的版本。

八天之后，2024 年 2 月 23 日，两份完全相反的回应同日挂上 arxiv。

一份来自 Google DeepMind 的 Genie 团队（Jake Bruce、Michael Dennis、Ashley Edwards、Tim Rocktäschel 等），论文叫 *Genie: Generative Interactive Environments*（[arxiv:2402.15391](https://arxiv.org/abs/2402.15391)）。Genie 用了 30 万小时无标注游戏视频训练一个 11B 参数的模型，但它的关键不在像素质量——Genie 的生成质量明显不如 Sora——而在于它**学到了一个潜在动作空间**：模型把每两帧之间的差分压缩到 8 个离散 latent action 上，推理时人类按键就能驱动一段从未存在过的 2D platformer 关卡。Genie 团队的赌注与 Sora 完全不同：他们不相信 \"被动看视频\" 能学到世界，他们相信**世界模型的核心是 action-conditional next-frame**，没有 action 就没有世界。Rocktäschel 在 talk 里把这句话说得很白——\"a world model that you cannot poke is just a video\"。

同一天，Meta FAIR 的 Adrien Bardes、Quentin Garrido 与 Yann LeCun 等人放出 V-JEPA（[arxiv:2404.08471](https://arxiv.org/abs/2404.08471)，arxiv 索引日期略晚但内部技术报告与 Sora/Genie 同周）。V-JEPA 把 LeCun 在 *A Path Towards Autonomous Machine Intelligence* 里写了快两年的方案做到了视频规模：**不预测像素，而预测被掩码视频块在表示空间里的 embedding**。论文里那段话几乎是对着 Sora 写的——\"reconstruction-based objectives in pixel space waste capacity on irrelevant details\"——并且报告 V-JEPA 在 Kinetics-400、SSv2 上的 frozen-feature 评测明显强过 V-MAE 这类 pixel-reconstruction baseline。LeCun 后来在 X 上更直接：\"Sora is impressive but it is not a world model.\"

把三家的立场翻成一句话：

| 团队 | 主导人 | 对 \"世界模型 = ?\" 的回答 | 范式赌注 |
|---|---|---|---|
| OpenAI Sora | Brooks, Peebles | 视频生成模型 scale 上去之后 *自动成为* 世界模拟器 | pixel-NTP + scale |
| DeepMind Genie | Bruce, Rocktäschel | 世界模型必须是 action-conditional next-frame，否则只是视频 | latent-action + interactive NTP |
| Meta V-JEPA | Bardes, LeCun | 像素本身就不该被预测，要在 representation 空间做 mask-prediction | non-generative latent-only |

这三个赌注在 2024 年 2 月那一周里像三发同时打出的信号弹，把社区接下来两年关于 \"video 是不是 NTP 的物理世界版\" 的讨论锚定下来。本章接下来用四节回顾这场三方对峙：(§2) Sora 路线在过去两年实际兑现了多少 \"自动世界模拟器\" 的承诺，以及 Brooks-Peebles 阵营悄悄退到哪条防线；(§3) Genie 1 → Genie 2 → Genie 3 的迭代揭示了 \"action-conditional\" 这一假设的真正代价；(§4) V-JEPA / V-JEPA-2 在下游 control task 上的迁移成绩，以及 LeCun 阵营自己在 2025 年开始向 latent diffusion 偏移的事实；(§5) 一条被三家都避而不谈的中间线——Hafner 的 DreamerV3 与 latent world model 在 RL 里默默累计的胜场。最后 (§6) 给一段诚实判断：到 2026 年 5 月为止，\"video-NTP = world model\" 这个等式在哪段成立、在哪段已经被反例打穿。

判断先放在这里以免读者悬着：**三家都在赢一部分、输一部分**。Sora 赢了视觉真实度，输了物理一致性与长程对象身份；Genie 赢了 interactive 这一关键概念，输了像素质量与 generalization；V-JEPA 赢了 representation evaluation，输了 \"看得见的成果\"（没有 demo 视频就没人转发）。三家共同输的那一件事是：**没人证明 \"看视频\" 这条路真的能产生 Pearl L2 / L3 意义上的世界模型**——所有三条路目前都停在 L1 联合分布拟合的不同变体上。这一点 §6 会展开。

<!-- TODO §2 Sora 之后两年：Brooks-Peebles 路线的物理一致性账单；从 \"世界模拟器\" 退到 \"视频生成模型\" 的措辞演化（OpenAI 2025 年关于 Sora 的官方表述变化）；DALL-E 3 / GPT-4o image gen 的对照 -->
<!-- TODO §3 Genie 1 → Genie 2 → Genie 3 (2024-12 / 2025) 的迭代：action codebook 从 8 个扩到多少；可玩时长从几秒到几分钟的工程代价；DeepMind 内部把 Genie 接到 SIMA agent 上的实验 -->
<!-- TODO §4 V-JEPA / V-JEPA-2 的下游 control task 战绩；LeCun 2025 年关于 latent diffusion 的妥协；Bardes 团队在 manipulation video pretraining 上的 follow-up -->
<!-- TODO §5 DreamerV3 [arxiv:2301.04104] 与 latent world model 在 RL 里的累计胜场（Atari 100k、Minecraft diamonds）；为什么这条线在 frontier lab 视野之外却最接近 \"可用世界模型\" -->
<!-- TODO §6 尾声：三条路目前都停在 L1，谁先做出 L2 反事实评测谁就赢；2026-05 中间判断 -->

---
