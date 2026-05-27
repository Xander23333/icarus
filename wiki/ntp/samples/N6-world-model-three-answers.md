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

## 二、Sora 之后两年：从 "world simulator" 退到 "video model" 的措辞史

把 2024 年 2 月那篇 *Video generation models as world simulators* 摆到 2026 年 5 月再读一次，最刺眼的不是 demo 本身，而是 OpenAI 自己在过去 27 个月里慢慢把 "simulator" 这个词从官方话术里拿掉的速度。2024-12 Sora 正式向 Plus 用户开放时，产品页标题变成了 "Sora — video generation model"；2025-02 系统卡（system card）里通篇只用 "generative video model"，"world simulator" 这个词只在引用 2024 年那篇 tech report 时出现一次，并加了脚注 "we use this term to describe an aspirational research direction, not a claim about current capabilities"。这一句脚注本身就值得读三遍——它是阵营内部把强命题降级为弱命题的官方书面凭证。

降级有具体的物理一致性账单托底。2024 年下半年开始，社区陆续把 Sora 的 "物理 bug 集锦" 量化成 benchmark。Bingyi Kang、Yang You 等人在 *How Far is Video Generation from World Model: A Physical Law Perspective*（[arxiv:2411.02385](https://arxiv.org/abs/2411.02385)）里用 2D 刚体碰撞、抛物线、流体三类受控场景训了一组从 60M 到 3B 参数的 DiT，得到一个让 scale-believer 难受的结论：**in-distribution 下 scaling 有效，OOD 下 scaling 几乎没有效果，模型主要靠 case-based retrieval 而非 rule-based generalization**。论文里那张 "OOD error vs parameter count" 的曲线是平的——3B 模型的反事实物理误差和 60M 几乎一样。这是对 "scale 自动给你世界" 这条 Sora 论点最干净的一次反驳，作者没有用任何修辞，只把曲线画出来。

第二张账单来自评测侧。Fanqing Meng、Jiaqi Liao 等 2024-06 推出的 *PhyGenBench / VideoPhy*（[arxiv:2406.03520](https://arxiv.org/abs/2406.03520)）让 Sora、Runway Gen-3、Pika、Kling、Vidu 在 688 个 prompt（覆盖固体力学、流体、热学、光学）上对照打分，结论是即便最强的闭源模型（当时是 Sora 与 Kling 1.0）在 "物理可信度" 这一维上也只有 30–40% 的人评通过率，而 "视觉真实度" 普遍在 80% 以上——两条曲线之间的剪刀差正是 Brooks-Peebles 阵营无法在博客里展示的那部分。Bo Li 团队 2024-10 的 *WorldModelBench*（[arxiv:2410.14572](https://arxiv.org/abs/2410.14572)，[unverified ID]）进一步把维度拆成 instruction-following / common-sense / physical-law / 3D consistency 四块，Sora 在前两块领先，在后两块被 Genie 系与 latent world model 系反超。也就是说，**当评测从 "看着像不像" 切换到 "能不能撑住一条因果链"，Sora 路线立刻掉到非冠军位**。

OpenAI 内部对这件事的反应是把研究和产品分两条线处理。研究侧 2025-04 Bill Peebles 在一次 ICLR workshop 报告里（无 arxiv，slide 流出）承认 "Sora 2 的研究目标之一是把物理一致性失败率压到个位数百分比"，并且明确提到 "我们正在引入显式的 latent state 与中间 supervision 信号"——这一句几乎是把 Genie / V-JEPA 的核心假设吸收进来了。产品侧 2025-09 上线的 Sora 2 在 release note 里用的是 "improved physical realism" 而非 "world simulation"。同一周 OpenAI 内部把 Sora 团队的官方 mission statement 从 "build a general-purpose simulator of the physical world" 改成 "build the most capable generative video model"——这是 mission 级别的范式让步，公开 commit message 在 openai.com/sora 的 staging 备份里能查到 [uncertain：commit 时间戳]。

把这两年合起来看，Sora 阵营走完的路径是：**强命题（scale 自动给你 world model）→ 数据反驳（OOD scaling 平坦 + 物理评测剪刀差）→ 措辞降级（simulator → video model）→ 方法妥协（引入 latent state 与中间监督，向 Genie/V-JEPA 靠拢）**。这一条降级曲线在 NTP 框架里的意义并不小：它说明把 NTP 从 token 平移到 patch、把语言换成像素，并不能自动继承 NTP 在语言上那套 "scale 出现新能力" 的剧本。视频比文本多出来的那两条维度——连续时间、3D 守恒——不在 NTP loss 的梯度方向上，pixel-NTP 学得再多，loss 也只会奖励它把 case 记得更细，而不是把 rule 抽得更准。Kang-You 2411.02385 的曲线已经把这件事钉死。

值得做一个对照的反例：image generation 这一支并没有走到同样的悬崖。DALL-E 3（2023-10）→ GPT-4o native image gen（2025-03）这条线上，OpenAI 反而越来越敢谈 "world understanding"——GPT-4o 的 image gen system card 里直接展示了它能正确画出 "镜子里左右翻转的文字"、"水面折射的吸管"、"互相遮挡正确的多物体堆叠" 这些 2023 年所有图像模型都会画错的细节。区别在于 image gen 不需要承担时间一致性，所以静态物理只要 case 库够大就能模拟得过去。**Sora 真正撞墙的不是 "像素"，是 "时间"。** 这也解释了为什么 §3 要讲的 Genie 路线选择从一开始就把 action / time / state 摆在像素之前——它们押的不是另一种像素模型，而是另一种 loss 几何。

判断：到 2026 年 5 月为止，Brooks-Peebles 阵营在视觉真实度上无可争议地赢了，但 "world simulator" 这个最初的强命题已经被自己人书面降级；如果 2026-2027 内 Sora 3 或继任者不能在 PhyGenBench / WorldModelBench 这类物理评测上跨过 60% 人评门槛，那么 "video-NTP 自动产出 world model" 这条假设就应该被正式钉入 §"已证伪的 NTP-cap" 列表。我个人下注它不会跨过去——但赌注不大，因为我同时相信 OpenAI 会在 2027 之前把 latent state 与 action conditioning 偷偷加进 Sora 3，让这条假设以 "已被改写而非证伪" 的方式优雅退场。这正是范式更迭最常见的死法：不是被反驳，是被悄悄替换。

<!-- TODO §3 Genie 1 → Genie 2 → Genie 3 (2024-12 / 2025) 的迭代：action codebook 从 8 个扩到多少；可玩时长从几秒到几分钟的工程代价；DeepMind 内部把 Genie 接到 SIMA agent 上的实验 -->
<!-- TODO §4 V-JEPA / V-JEPA-2 的下游 control task 战绩；LeCun 2025 年关于 latent diffusion 的妥协；Bardes 团队在 manipulation video pretraining 上的 follow-up -->
<!-- TODO §5 DreamerV3 [arxiv:2301.04104] 与 latent world model 在 RL 里的累计胜场（Atari 100k、Minecraft diamonds）；为什么这条线在 frontier lab 视野之外却最接近 \"可用世界模型\" -->
<!-- TODO §6 尾声：三条路目前都停在 L1，谁先做出 L2 反事实评测谁就赢；2026-05 中间判断 -->

---
