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

<!-- TODO §3 Pi0 [arxiv:2410.24164 unverified ID] 与 Physical Intelligence 的数据墙赌注；Octo [arxiv:2405.12213] 跨 embodiment generalization 的实际限度 -->
<!-- TODO §4 V-JEPA / I-JEPA 的下游迁移战绩；为什么 LeCun 团队 2024 年开始接受 latent diffusion 而非纯 JEPA -->
<!-- TODO §5 Hierarchical tokenization：RVQ、FAST tokenizer (Pi0)、latent action codebook，是不是把 NTP 与 JEPA 缝起来的中间方案 -->
<!-- TODO §6 尾声：这场赌局 2027 年才有真数据，但 2026 年的中间判断是什么 -->

---

*相关 topic：[embodiment](../topics/embodiment.md)（VLA 候选 mech 表）、[world_model](../topics/world_model.md)（JEPA 与视频生成两条线的对比）、[grounding](../topics/grounding.md)（symbol grounding 在动作空间里的化身）。*
