# 为什么 LLM 不会持续学习

## 一、2021 年 2 月的一篇 DeepMind 论文：把"时间"从直觉变成曲线

故事可以从 2021 年 2 月的一篇 DeepMind 论文开始。作者是 Angeliki Lazaridou，论文叫 *Mind the Gap: Assessing Temporal Generalization in Neural Language Models* ([arxiv:2102.01951](https://arxiv.org/abs/2102.01951))。在那之前，所有人都"知道"语言模型会过时——GPT-2 不知道 COVID-19，BERT 不知道 GPT-2——但这件事一直是茶水间的段子，而不是一条可以画在 PPT 上的曲线。Lazaridou 做的事很朴素：固定一个 Transformer LM，把测试集按"事件发生的月份"分桶，看 perplexity 怎么随训练-评测时间差变化。结果在新闻、科学、推特三类语料上几乎一致——每过 12 个月，关于**新实体 / 新事件**的 perplexity 单调上升，而**通用语言能力**几乎不动。

这条曲线之所以重要，不在于数字本身，而在于它**第一次把"时间漂移"从知识问题里剥离出来**。在 Lazaridou 之前，社区习惯把 LM 的过时归因于"知识不够"——再多塞点训练数据就好。Lazaridou 的图说：不是的，**语法、句法、风格在 cutoff 之后还活着，只有"指称世界的能力"在死**。这是两件不同的事，会有两条不同的衰减常数。

紧接着，2021 年 8 月 Wenhu Chen 等人发布 TimeQA ([arxiv:2108.06314](https://arxiv.org/abs/2108.06314))，构造 ~20k 时间敏感问答（"X 在 2010 年是哪个队的成员"）。closed-book setting 下 T5-large 准确率长期停在 ~25%，远低于人类 ~85%——而且**即便答案完全在训练集内，模型也常给出时间错配的旧答案**。这件事更尖锐：它证明问题不只是"新知识进不来"，而是"模型连内部已有知识的时间索引都建不出来"。同年 Bhuwan Dhingra 等人的 TempLAMA (TACL 2022) 在 cloze 风格上重复验证了这一点：T5 内部确实存在某个"时间敏感"维度，但同一事实在不同时间 prompt 下答案漂移，**没有一致的时间一致性约束**。

到 2022 年 7 月 Jungo Kasai 等人推出 RealTime QA ([arxiv:2207.13332](https://arxiv.org/abs/2207.13332))，事情进入"工业测量"阶段：每周更新一次的开放问答基准，让任意 LLM 在固定 cutoff 后被持续 evaluate。三年下来的数据冷酷得近乎滑稽——所有 closed-book frontier model 在"上周新闻题"上的 accuracy 几乎为 0（除非泄漏），而**只要加上 retrieval 就立即跃到 50–70%**。这个 retrieval gap 就是 cutoff gap 最直接的量化：模型权重里**真的没有**这些信息，不是"召回不出来"，是"根本不在那里"。

2023 年 10 月 Tu Vu 等人在 Google 推出 FreshLLMs / FreshQA ([arxiv:2310.03214](https://arxiv.org/abs/2310.03214))，第一次把 cutoff 衰减、staleness 与 hallucination 三者**联立测量**：fast-changing 题 closed-book accuracy 接近 0，而模型在 false-premise 题上有强烈的"自信编造"倾向（约 30–50%）。这件事的意义在于：**模型不仅不知道自己不知道，它会在知识真空里主动补一个错误答案**——这是 NTP loss 的一阶 artifact。Cross-entropy 不允许"我不知道"作为高概率 next token，于是模型必须 commit 到某个 trajectory，即便所有可能的 trajectory 都已经过期。

但真正让我（Xander）开始怀疑"cutoff"这个概念本身是否成立的，是 2024 年 6 月 Cheng 等人的 *Dated Data: Tracing Knowledge Cutoffs in LLMs* ([arxiv:2403.12958](https://arxiv.org/abs/2403.12958)) [unverified ID]。他们反过来问：能不能仅靠模型行为反推它的真实 cutoff？答案是可以——通过对一组已知时间戳事实做 forced-answer probe，能把模型的 *effective* cutoff 定位到月级别。意外的副产物：**很多模型的 effective cutoff 显著早于厂商公布的 data cutoff**。比如一个声称 cutoff 在 2024-04 的模型，其行为更像 cutoff 在 2023-10。这意味着 pretraining 末段语料对权重的写入是**稀疏的**——LR 退火窗口里那些"最后看到的 token"并没有真正进入参数。

把这条线拉直，到 2026 年 5 月的视角下可以下一个比 mech 阵营原本论点更强的判断：**LLM 不会持续学习这件事，不是从 cutoff 那一刻开始的，而是从 cutoff 之前 6–12 个月就开始了**。原本的强主张是"$t > t_{\text{cutoff}}$ 时知识为空"；实际经验是"$t > t_{\text{cutoff}} - \Delta$ 时知识已稀疏"，其中 $\Delta$ 取决于 LR schedule，量级几个月。这把"continual learning 失败"从一个**部署后的问题**改写成一个**训练末段就已存在的结构性问题**——而后者要难得多。

## 二、为什么这章不是 online_learning.md 的复述

写到这里我必须停下来回答一个元问题：既然 `wiki/ntp/topics/online_learning.md` 已经把证据链梳理过一遍，这一章存在的意义是什么？

答案是：topic 页面给的是**证据 catalog**，sample 章给的是**判断 stack**。两个 artifact 在结构上完全不同。topic 页面是"如果你想知道这个领域有哪些工作，按时间排好了"；sample 章是"如果你想知道 *Xander 看完这些工作后认为发生了什么*，下面这条叙事线就是答案，每一段都可以挑战"。后者的失败方式是被人当面指出"你这条因果链断了"，前者的失败方式是被人指出"你漏了一篇论文"。

接下来的 §3 到 §5 会沿着这条判断 stack 走：§3 把 catastrophic forgetting 形式化为 NTP loss 的不动点，并解释为什么 Kirkpatrick 2017 的 EWC ([arxiv:1612.00796](https://arxiv.org/abs/1612.00796)) 在 LLM 规模下退化为 replay 的最贵实现；§4 拆 Ibrahim 2024 ([arxiv:2403.08763](https://arxiv.org/abs/2403.08763)) 把 continual pretraining 成本压到 retrain 1/10 之后剩下的硬骨头是什么——为什么"批处理 + replay"不算 streaming；§5 处理三条仍然站着的反例（TTT-Linear、MEMIT 批量编辑、agent memory 系统），并解释为什么它们都不构成对 C-CONT-1 的真正反驳。结尾 §6 给一个 2027 年的可证伪 bet。

如果读完这一章你只能记住一件事，请记住这个：**LLM 不持续学习这件事，不是"我们还没找到正确的算法"，而是 NTP loss 的几何形状本身禁止它**。这是一个比"reasoning 不够好"或"grounding 不够多模态"都要更深的论断，因为它说的是即便你把数据、算力、模态都拉满，只要 loss function 还是 $-\log p(x_t | x_{<t})$，部署后的模型就会以可预测的速率失去对世界的索引。下面我会尝试把这件事说成不只是"我觉得"。

<!-- TODO §3: catastrophic forgetting as NTP loss fixed point — McCloskey 1989 → EWC 1612.00796 → Lyle 2303.01486 plasticity loss → Dohare Nature 2024 continual backprop -->
<!-- TODO §4: Ibrahim 2024 2403.08763 anatomy — replay ratio, LR re-warming, what's still missing for "streaming" -->
<!-- TODO §5: three live counter-examples — TTT-Linear 2407.04620 / MEMIT 2210.07229 / Letta-Mem0-Zep agent memory; why each is "推迟" not "解决" -->
<!-- TODO §6: 2027 falsifiable bet + Sutton bitter-lesson rebuttal -->
