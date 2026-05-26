# Embodiment 真的不可 tokenize 吗——VLA 路线的隐含赌注

> NTP 候选样章 N5。作者 Xander Xu。本篇试图把一个被两派人各自当成"显然"的问题摆到同一张桌上：把摄像头帧、本体感受、电机指令切成 token 喂给一个自回归 transformer，到底是 NTP 范式的自然延伸，还是 NTP 在物理世界面前最尴尬的滑铁卢。

## 一、Moravec 悖论与 LeCun 的拒绝接受 NTP

故事要从 1988 年 Hans Moravec 那本 *Mind Children* 说起。Moravec 在 CMU 机器人所写过一句被引了三十多年的话，大意是：让计算机在国际象棋上达到大师水平相对容易，让它有一个一岁小孩的感知运动能力却近乎不可能。这个"反直觉"——高阶认知便宜、低阶身体昂贵——被称作 Moravec 悖论。1988 年到 2012 年的二十四年里，这条悖论几乎没有被撼动：Deep Blue 在 1997 年赢了 Kasparov，但同一时期 DARPA Grand Challenge 的自动驾驶车队还在沙漠里迷路；2012 年 AlexNet 在 ImageNet 上压扁所有人，但同一年的 DARPA Robotics Challenge 视频里，价值百万美元的人形机器人还在开门时摔倒。

到 2022 年 ChatGPT 出来之后，悖论的形状变了，但**没有消失**。LLM 在 MMLU、GSM8K、HumanEval 上一路压过去，可同一时期最好的端到端机器人策略——RT-1、Diffusion Policy、ACT——在桌面抓取任务上的成功率还在 70%–90% 之间晃，对分布外物体几乎归零。**认知侧的进步几乎没有同步带来身体侧的进步**，这件事让 Moravec 悖论从一个怀旧 anecdote 变成了一个范式问题。

Yann LeCun 是把这个问题搬上桌的人。2022 年 6 月他发布 position paper *A Path Towards Autonomous Machine Intelligence*（OpenReview 版本，非 arxiv），后来在多次公开演讲（NeurIPS 2022、Berkeley AI Forum 2023、Lex Fridman 访谈多轮）里把它压成一句话：**Autoregressive LLM are an off-ramp, an exit ramp.** 他给的理由非常具体——一个四岁小孩在第一次睁眼到四岁之间，视网膜上接收的视觉信息量大约是 $10^{15}$ 字节量级 [uncertain — LeCun 不同场合给的数字在 $10^{14}$ 到 $10^{16}$ 之间]，远超 GPT-4 整个训练语料的 token 数。也就是说，**真实世界的信息密度本身就比文本高几个数量级**，而 NTP 范式核心的"用下一 token 预测当摩擦力"在视频和动作流上根本撑不起来——因为相邻帧的可预测部分太多、不可预测部分要么完全随机要么需要物理常识，预测损失梯度被低频背景吃掉了。

LeCun 由此推出 JEPA（Joint Embedding Predictive Architecture）：不在像素空间做自回归，而是在抽象表示空间做"被掩码块"预测，并且**不要求生成式重构**。I-JEPA（[arxiv:2301.08243](https://arxiv.org/abs/2301.08243)，He、Bardes、Balestriero、LeCun 等）和 V-JEPA（[arxiv:2404.08471](https://arxiv.org/abs/2404.08471)，Bardes 等）是这个路线的两块奠基石。LeCun 在多次演讲里直白说过：他不相信把视频和动作切成 token 喂给 transformer 这条路能通——这是一个**显式的范式赌注**。

把 LeCun 的赌注翻译成本章要回答的问题：**Embodiment 真的不可 tokenize 吗？** 如果答案是"是"，那么 RT-2 / OpenVLA / Pi0 整条 VLA（Vision-Language-Action model）路线就是在错误的范式里堆资源，最后会撞在一堵 LeCun 在 2022 年就画出来的墙上。如果答案是"否"，那么 LeCun 这次会输得很难看——因为产业资本（Tesla Optimus、Figure AI、1X、Physical Intelligence）已经在 VLA 路线上压了几十亿美元，赌的就是"够多够好的 action token 数据 + 够大的 transformer = 物理通用智能"。

这一章不会假装能给出最终答案——这个问题的答案要等 2027–2030 年的真实部署数据。但我会把现有证据沿三条线整理：(§2) RT-2 之后 VLA 路线的真实战绩；(§3) Pi0 / OpenVLA 公开的 scaling 曲线和它隐含的"数据墙"；(§4) JEPA 阵营到目前为止的反证据，以及为什么 LeCun 自己也开始悄悄妥协；(§5) 一个被双方都忽略的中间立场——hierarchical tokenization 与 latent action space。最后 (§6) 给一段诚实判断：到 2026 年 5 月为止，这场赌局的赔率在我看来是几比几。

<!-- TODO §2 RT-1 (2212.06817) → RT-2 (2307.15818) → OpenVLA (2406.09246)：Brohan 与 Levine 的三步赌注，以及 RT-2 论文里那条让所有人意外的 emergent capability 曲线 -->
<!-- TODO §3 Pi0 [arxiv:2410.24164 unverified ID] 与 Physical Intelligence 的数据墙赌注；Octo [arxiv:2405.12213] 跨 embodiment generalization 的实际限度 -->
<!-- TODO §4 V-JEPA / I-JEPA 的下游迁移战绩；为什么 LeCun 团队 2024 年开始接受 latent diffusion 而非纯 JEPA -->
<!-- TODO §5 Hierarchical tokenization：RVQ、FAST tokenizer (Pi0)、latent action codebook，是不是把 NTP 与 JEPA 缝起来的中间方案 -->
<!-- TODO §6 尾声：这场赌局 2027 年才有真数据，但 2026 年的中间判断是什么 -->

---

*相关 topic：[embodiment](../topics/embodiment.md)（VLA 候选 mech 表）、[world_model](../topics/world_model.md)（JEPA 与视频生成两条线的对比）、[grounding](../topics/grounding.md)（symbol grounding 在动作空间里的化身）。*
