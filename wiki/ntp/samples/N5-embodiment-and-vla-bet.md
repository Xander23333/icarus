# Embodiment 真的不可 tokenize 吗——VLA 路线的隐含赌注

> NTP 候选样章 N5。作者 Xander Xu。本篇试图把一个被两派人各自当成"显然"的问题摆到同一张桌上：把摄像头帧、本体感受、电机指令切成 token 喂给一个自回归 transformer，到底是 NTP 范式的自然延伸，还是 NTP 在物理世界面前最尴尬的滑铁卢。

## 一、Moravec 悖论与 LeCun 的拒绝接受 NTP

故事要从 1988 年 Hans Moravec 那本 *Mind Children* 说起。Moravec 在 CMU 机器人所写过一句被引了三十多年的话，大意是：让计算机在国际象棋上达到大师水平相对容易，让它有一个一岁小孩的感知运动能力却近乎不可能。这个"反直觉"——高阶认知便宜、低阶身体昂贵——被称作 Moravec 悖论。1988 年到 2012 年的二十四年里，这条悖论几乎没有被撼动：Deep Blue 在 1997 年赢了 Kasparov，但同一时期 DARPA Grand Challenge 的自动驾驶车队还在沙漠里迷路；2012 年 AlexNet 在 ImageNet 上压扁所有人，但同一年的 DARPA Robotics Challenge 视频里，价值百万美元的人形机器人还在开门时摔倒。

到 2022 年 ChatGPT 出来之后，悖论的形状变了，但**没有消失**。LLM 在 MMLU、GSM8K、HumanEval 上一路压过去，可同一时期最好的端到端机器人策略——RT-1、Diffusion Policy、ACT——在桌面抓取任务上的成功率还在 70%–90% 之间晃，对分布外物体几乎归零。**认知侧的进步几乎没有同步带来身体侧的进步**，这件事让 Moravec 悖论从一个怀旧 anecdote 变成了一个范式问题。

Yann LeCun 是把这个问题搬上桌的人。2022 年 6 月他发布 position paper *A Path Towards Autonomous Machine Intelligence*（OpenReview 版本，非 arxiv），后来在多次公开演讲（NeurIPS 2022、Berkeley AI Forum 2023、Lex Fridman 访谈多轮）里把它压成一句话：**Autoregressive LLM are an off-ramp, an exit ramp.** 他给的理由非常具体——一个四岁小孩在第一次睁眼到四岁之间，视网膜上接收的视觉信息量大约是 $10^{15}$ 字节量级 [uncertain — LeCun 不同场合给的数字在 $10^{14}$ 到 $10^{16}$ 之间]，远超 GPT-4 整个训练语料的 token 数。也就是说，**真实世界的信息密度本身就比文本高几个数量级**，而 NTP 范式核心的"用下一 token 预测当摩擦力"在视频和动作流上根本撑不起来——因为相邻帧的可预测部分太多、不可预测部分要么完全随机要么需要物理常识，预测损失梯度被低频背景吃掉了。

LeCun 由此推出 JEPA（Joint Embedding Predictive Architecture）：不在像素空间做自回归，而是在抽象表示空间做"被掩码块"预测，并且**不要求生成式重构**。I-JEPA（[arxiv:2301.08243](https://arxiv.org/abs/2301.08243)，He、Bardes、Balestriero、LeCun 等）和 V-JEPA（[arxiv:2404.08471](https://arxiv.org/abs/2404.08471)，Bardes 等）是这个路线的两块奠基石。LeCun 在多次演讲里直白说过：他不相信把视频和动作切成 token 喂给 transformer 这条路能通——这是一个**显式的范式赌注**。

把 LeCun 的赌注翻译成本章要回答的问题：**Embodiment 真的不可 tokenize 吗？** 如果答案是"是"，那么 RT-2 / OpenVLA / Pi0 整条 VLA（Vision-Language-Action model）路线就是在错误的范式里堆资源，最后会撞在一堵 LeCun 在 2022 年就画出来的墙上。如果答案是"否"，那么 LeCun 这次会输得很难看——因为产业资本（Tesla Optimus、Figure AI、1X、Physical Intelligence）已经在 VLA 路线上压了几十亿美元，赌的就是"够多够好的 action token 数据 + 够大的 transformer = 物理通用智能"。

这一章不会假装能给出最终答案——这个问题的答案要等 2027–2030 年的真实部署数据。但我会把现有证据沿三条线整理：(§2) RT-2 之后 VLA 路线的真实战绩；(§3) Pi0 / OpenVLA 公开的 scaling 曲线和它隐含的"数据墙"；(§4) JEPA 阵营到目前为止的反证据，以及为什么 LeCun 自己也开始悄悄妥协；(§5) 一个被双方都忽略的中间立场——hierarchical tokenization 与 latent action space。最后 (§6) 给一段诚实判断：到 2026 年 5 月为止，这场赌局的赔率在我看来是几比几。

## 二、RT-1 → RT-2 → OpenVLA：Brohan 与 Levine 的三步赌注

LeCun 在 2022 年画下那堵墙的同一时段，Google DeepMind 机器人组正在做相反方向的事。2022 年 12 月，Anthony Brohan、Karol Hausman、Sergey Levine 等人放出 RT-1（[arxiv:2212.06817](https://arxiv.org/abs/2212.06817)）。这篇文章的主张其实非常朴素——他们用 13 台机械臂在 17 个月里收集了约 13 万条 episode、覆盖 700 多个任务指令，然后把图像与文本指令一起 tokenize、用一个 35M 参数的 transformer 做自回归动作预测。RT-1 没有谈范式，只是把一件事做完：**把动作当 token 来预测，端到端能不能 work**。在桌面操作 benchmark 上他们报告了 97% 的训练任务成功率，对 unseen task 的 76%，对 unseen distractor 的 83%。数字本身不夸张，但它是第一份把 "action-as-token" 这条路从演示推到 *规模化训练* 的工程报告。

七个月后，2023 年 7 月，同一团队发布 RT-2（[arxiv:2307.15818](https://arxiv.org/abs/2307.15818)）。这一步在范式上是真正的赌注：他们直接把动作 token 塞进一个已经在互联网图像-文本上预训练过的 VLM（PaLI-X 55B 与 PaLM-E 12B），让动作 token 与语言 token 共享同一个词表，再用机器人数据做 co-finetune。论文里那张让所有人意外的图是 "emergent capabilities"——在没有专门训练的情况下，RT-2 能完成 "把草莓放进与它颜色相同的碗里"、"把可乐罐递给 Taylor Swift"（通过 VLM 的常识识别图片）一类需要符号-感知-动作三跳的任务。Brohan 等人的数据是：emergent reasoning 任务成功率从 RT-1-style baseline 的 ~25% 跳到 RT-2 的 ~60% 左右 [数字来自 RT-2 paper Table 4，按子类别取中位数]。这是 VLA 路线给出的第一份 **scaling-style 证据**：网络预训练知识，可以通过 token 共享渠道部分流入动作策略。

但 RT-2 的代价同样赤裸：它是闭源的、跑在 Google 内部 TPU 集群上、推理延迟在 1–3 Hz 量级（论文里直说 "we use cloud inference"）。对一个真正要装上机器人本体的策略而言，这个延迟意味着它无法做接触富的操作（contact-rich manipulation 一般需要 ≥20 Hz 闭环）。所以 RT-2 更像是 **"VLA 范式可行性的存在性证明"**，而不是可部署的方案。

第三步由 Stanford 的 Moo Jin Kim、Karl Pertsch、Chelsea Finn 等人在 2024 年 6 月走完——OpenVLA（[arxiv:2406.09246](https://arxiv.org/abs/2406.09246)）。OpenVLA 用 Llama-2 7B + DINOv2/SigLIP 视觉编码器搭骨架，在 Open X-Embodiment 数据集（[arxiv:2310.08864](https://arxiv.org/abs/2310.08864)，21 个机构、22 种机器人本体的 ~100 万条 episode 合并）上训练。它的关键贡献不是性能（在 BridgeData V2 与 LIBERO 上和 RT-2-X 大体打平），而是**把 VLA 拉进开源世界**：权重公开、可在单张 A100 上 6Hz 推理、LoRA 微调成本 < $100。这件事让 VLA 路线从 "Google 内部能不能 work" 的封闭问题，变成 "任何实验室都能复现并尝试推翻" 的公共问题。

三步合起来是 Brohan-Levine-Finn 这一脉的 **赌注序列**：RT-1 赌的是动作可 tokenize、RT-2 赌的是 VLM 常识可通过 token 共享渗入策略、OpenVLA 赌的是这一切可以在没有 Google 量级算力的条件下复现。到 2026 年中，前两个赌注大体兑现，第三个赌注还在被持续验证——Octo（[arxiv:2405.12213](https://arxiv.org/abs/2405.12213)）、TinyVLA、SpatialVLA 等后续工作都在沿这条线推。

但必须留两条反论。其一：所有 RT-2 / OpenVLA 报告的成功率都是 **桌面短程操作**（pick-place、stacking、wiping），任务时长 < 30 秒。一旦把任务延展到长程（如做一顿饭、收拾房间），公开 benchmark 上的成功率立刻塌到个位数——这正是 §4 要讨论的 JEPA 阵营的核心反驳。其二：emergent capability 的统计基础很薄。RT-2 论文报告的 emergent 任务一共只有几十个 prompt，置信区间宽到几乎覆盖全部 0–100%——Schaeffer 等人 2023 年那篇 *Are Emergent Abilities a Mirage?*（[arxiv:2304.15004](https://arxiv.org/abs/2304.15004)）的批评原则上完全适用。

我的判断：到 2026 年 5 月，RT-1 → RT-2 → OpenVLA 这条线已经把 "动作完全无法 tokenize" 这个强命题证伪了——LeCun 在 2022 年那句 "off-ramp" 至少在 *桌面短程操作* 这个子领域上是过强的。但它并没有证伪 "动作 tokenization 的样本效率在长程任务上指数恶化" 这个弱命题——而这个弱命题才是 §3 Physical Intelligence 路线真正要面对的数据墙。

## 三、Pi0 与 Physical Intelligence：把数据墙画在 PPT 上的那一年

2024 年 3 月，Sergey Levine、Chelsea Finn、Karol Hausman 三人离开各自的学术职位（Berkeley、Stanford、Google DeepMind）联合创立 Physical Intelligence（公司缩写 π，下面记作 PI）。这是 2024 年机器人界最罕见的一次资本投票——一家成立六个月就拿到 7000 万美元种子、隔年估值越过 20 亿美元 [按公开报道 2024-11 Thrive Capital 领投轮，数字 [uncertain]] 的公司，三位创始人都是 RT-1/RT-2/OpenVLA 这条 VLA 血脉的核心作者。也就是说，PI 的存在本身就是对 §2 那条赌注的资本翻倍：他们认为 VLA 路线的瓶颈不在范式，而在**数据规模与表示效率**。

2024 年 10 月，PI 放出 π0（[arxiv:2410.24164](https://arxiv.org/abs/2410.24164)，Black、Brown、Driess、Finn、Hausman、Levine 等十几位作者联署）。π0 在三件事上做了相对 RT-2 / OpenVLA 的范式增量：(a) 骨架不再是纯自回归 transformer，而是 **VLM backbone（PaliGemma 3B）+ action expert + flow matching head**——动作不再当 discrete token 预测，而是用 conditional flow matching 在连续 action 空间里生成 50 Hz 的 action chunk；(b) 训练数据从 OpenVLA 的 ~100 万 episode 扩到 **~10000 小时机器人交互** [按论文表 1 与 blog 报告综合估算]，并显式 mix 单臂 / 双臂 / 移动底座三种 morphology；(c) 公开 demo 第一次覆盖了**长程接触富任务**——叠衣服、装配纸盒、把咖啡豆从袋子倒进研磨器——任务时长跨入 5–10 分钟量级。

但这一步同时把"数据墙"画到了 PPT 上。π0 论文里有一个常被忽略的细节：他们的预训练已经用到了 **OXE + DROID + 内部数据 ≈ OXE 三倍多**（[DROID arxiv:2403.12945](https://arxiv.org/abs/2403.12945)，Khazatsky、Pertsch、Finn 等，76k episode、564 个场景，已是当时最大的公开学术数据集），而要达到 5–10 分钟长程任务的成功率所需的数据**几乎肯定是再一个数量级以上**。Chelsea Finn 在 2024-12 RSS keynote 里直接说过一句被广泛转引的话——大意是"语言模型用的是整个互联网，机器人现在只用了整个互联网千分之一规模的数据"[uncertain — 转述自现场录像，原话比例未严格核实]。这句话翻译成 NTP 的语言就是：**VLA 路线在 (N, D, C) 三轴里，D 轴比 LLM 落后约 3–4 个数量级**，而硬件采集 D 的成本是物理时间×机器人折旧，无法像爬 Common Crawl 那样几个月翻一番。

PI 的第二步 π0.5（2025 年公布、blog-only，arxiv 版本 [unverified]）把这个问题推到更尴尬的位置：他们开始向数据**异质化**借力——加入人类视频（Ego4D 类）、加入仿真 rollout、加入网页 grounding 数据——而这些都是 LeCun 在 §1 那条 JEPA 论证里早就主张过的方向。也就是说，**最 hardcore 的 VLA 阵营开始悄悄在数据侧妥协**，承认纯 robot-only NTP 的样本效率撑不到通用操作。

跨 embodiment 维度上，Octo（[arxiv:2405.12213](https://arxiv.org/abs/2405.12213)，Ghosh、Walke、Pertsch 等 Berkeley/CMU/Stanford 联合）给了另一份诚实的报告。Octo 的卖点是"一个 27M / 93M 参数的小 transformer policy，在 OXE 上预训练之后可以零样本迁移到 9 种未见 morphology"。但读它的 Table 3 会看到：**zero-shot 成功率均值 < 30%**，必须再做 ≥100 条目标本体演示的 fine-tune 才能爬到 60–80%。换句话说，VLA 路线的 "cross-embodiment generalization" 在 2024–2025 阶段是**带星号的**——预训练学到的是通用视觉-语言-动作映射的*骨架*，本体特异的动力学和接触模式仍然要在线收集。这和 LLM 在新语言上几乎零样本工作的形状是不一样的。

我对 §3 这条线的判断：到 2026 年 5 月，VLA 阵营自己已经在用工程动作（flow matching 替自回归、异质数据补 robot-only、本体特异 fine-tune）默认承认了**弱命题——动作 tokenization 的样本效率在长程接触富任务上确实指数恶化**。LeCun 的强命题已经被 §2 证伪，但他的弱命题正在被 PI 自己的路线图悄悄证实——只不过 PI 选择**用更多的钱去喂这堵墙**而不是换范式。哪一种是对的，要看 2027–2028 年 π0 系列在真实部署里的成功率曲线是接近 LLM-style log-linear scaling 还是更接近 saturation。两种结果都和 NTP 的命运直接挂钩——前者意味着 NTP 范式真的吞下了身体，后者意味着 Moravec 悖论以"数据-成本"的新形式回归。

<!-- TODO §3 Pi0 [arxiv:2410.24164 unverified ID] 与 Physical Intelligence 的数据墙赌注；Octo [arxiv:2405.12213] 跨 embodiment generalization 的实际限度 [已并入正文 2026-05-27] -->
## 四、JEPA 阵营的真实战绩——以及 LeCun 自己悄悄迁移的两步

回到 §1 那条 LeCun 划下的反对线。如果 RT-2/OpenVLA/π0 是 VLA 阵营的三步赌注，那么 I-JEPA → V-JEPA → V-JEPA 2 是 LeCun 这边对应的三步。但读这条线时要做的事和 §2/§3 不一样——VLA 阵营每一步都直接对着\"机器人能不能做这件事\"的成功率发布，JEPA 阵营每一步都先对着\"下游表征的 linear-probe / k-NN / frozen-feature 转移\"发布。这个发布方式上的差异本身就是证据：到 2026 年 5 月为止，**JEPA 路线还没有给出一份端到端机器人任务的可比基线**。

具体翻一下战绩。I-JEPA（[arxiv:2301.08243](https://arxiv.org/abs/2301.08243)，2023-01）在 ImageNet linear-probe 上把 MAE/SimCLR 全家比下去——这是表征学习圈的胜利，但和\"机器人是否需要 NTP\"几乎正交。V-JEPA（[arxiv:2404.08471](https://arxiv.org/abs/2404.08471)，Bardes、Garrido、LeCun 等，2024-04）把 JEPA 从图像扩到视频，主要 benchmark 是 Kinetics-400/SSv2 上的 frozen-feature 动作识别——同样属于\"判别式下游\"，仍然没有动作生成。论文里那个最常被截图的表是 V-JEPA frozen 在 SSv2 上达到 ~72% top-1，超过 VideoMAE/Hiera。但同一篇论文的 Limitations 一节明白写着：\"we do not address action-conditioned prediction or planning\"。这一行字本身就是 JEPA 阵营 2024 年的状态——**世界表征学得很好，但策略侧空缺**。

V-JEPA 2（[arxiv:2506.09985](https://arxiv.org/abs/2506.09985) [unverified ID]，Meta FAIR，2025 年中）开始往策略侧走，公开 demo 包括了一个用 V-JEPA 2 作为 world model、配 MPC（model predictive control）做桌面抓取的系统。在 LeCun 自己 2025-06 的 keynote 视频里 [uncertain — 转述自现场录像，无 arxiv 对应]，他展示的成功率大约在 60–80% 之间，任务是简单的 pick-and-place。这个数字本身不重要，重要的是**对比基线**——同样的桌面 pick-and-place，2022 年的 RT-1 就已经在 76–97% 区间。也就是说，到 2026 年 V-JEPA 系列在端到端机器人指标上还没能追上 2022 年的 VLA 基线，更不用说 π0 的长程接触富任务。这不是 JEPA 路线的死刑——它的核心论证从来不是\"短期能赢 benchmark\"，而是\"长期样本效率更好\"——但它意味着 LeCun 2022 年说\"autoregressive 是 off-ramp\"那句话，在 2026 年并没有被表征侧的胜利兑现成策略侧的胜利。

更值得注意的是 LeCun 自己的两步退却。第一步是 2023–2024 年间 FAIR 内部对 *generative* world model 的妥协：原版 JEPA 论证里非常清楚地说不要 pixel-level 生成，但 V-JEPA 2 的下游 planning 仍然需要 *decode* 出可用于 MPC 的状态预测；同期 Meta 内部另一条 latent-diffusion 路线（Movie Gen [arxiv:2410.13720](https://arxiv.org/abs/2410.13720)）在视频生成上拿到产品级结果，与 JEPA 的反 generative 立场形成内部对照。第二步更直接：2024-10 Meta AI 发布 Sphinx / Chameleon 一线 *统一 token 化* 路线（[Chameleon arxiv:2405.09818](https://arxiv.org/abs/2405.09818)），把图像、文本、（未来计划中的）音频都统一进自回归 token 流——这恰恰是 LeCun 2022 年那篇 position paper 显式劝退的方向。两条路线在同一家公司同时推进，意味着 Meta 自己也不敢把全部筹码压在 JEPA 上。LeCun 在 2025 年的多次公开访谈里仍然坚持\"LLM 不通向 AGI\"，但**他不再说 tokenization 这件事本身是错的**——立场从范式拒绝退到了\"objective shape 之争\"。

反论也要写在这一节里——这条线 JEPA 阵营有一份真正属于自己的强证据。Garrido 等人 2024 年的 *Learning and Leveraging World Models in Visual Representation Learning*（[arxiv:2403.00504](https://arxiv.org/abs/2403.00504)）显示，把 JEPA-style 潜在预测目标加进视觉预训练，下游对 *分布外* 几何/光照变化的鲁棒性显著优于 MAE/CLIP 全家——这是\"潜在空间预测比像素重构更接近世界结构\"这一弱命题的第一份可重复证据。Assran 等 2024 年的 *V-JEPA: Latent Video Prediction* 后续 ablation 也复现了这条结论。它构不成对 VLA 路线的反驳，但**构成对纯 pixel-NTP 视频生成路线（Sora 系）的反驳**——这两条战线不应混为一谈，我会在 N6 里把这层区分单独写一节。

我对 §4 这条线的判断：到 2026 年 5 月，JEPA 阵营赢了\"表征学习的局部赌注\"，但输了\"策略侧端到端范式赌注\"——后者甚至还没真正开打。LeCun 的立场从 2022 年的强范式拒绝退到了 2025 年的弱 objective-shape 偏好，这本身就是 §1 那个赌局赔率向 VLA 倾斜的证据。但这个赔率不是 5:1 或 10:1，而更像是 6:4——因为 §3 那堵数据墙仍然真实，而 JEPA 阵营保留了一张未打的牌：如果 V-JEPA 系列在 2027–2028 真的展示出*显著优于*纯 NTP 视频模型的下游 planning 样本效率，赔率可以再被翻转一次。

<!-- TODO §5 Hierarchical tokenization：RVQ、FAST tokenizer (Pi0)、latent action codebook，是不是把 NTP 与 JEPA 缝起来的中间方案 -->
<!-- TODO §6 尾声：这场赌局 2027 年才有真数据，但 2026 年的中间判断是什么 -->

---

*相关 topic：[embodiment](../topics/embodiment.md)（VLA 候选 mech 表）、[world_model](../topics/world_model.md)（JEPA 与视频生成两条线的对比）、[grounding](../topics/grounding.md)（symbol grounding 在动作空间里的化身）。*
