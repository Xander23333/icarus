# 第七章 为什么 Anthropic 在可解释性上一家独大

## 引子：一份名单

2024 年春天，一位研究者在个人博客上贴出一张图：横轴是年份，纵轴是机构，节点是人。Chris Olah 从 Google Brain 走到 OpenAI，又从 OpenAI 走到 Anthropic；Catherine Olsson 走过同样的路径；Neel Nanda 从 Anthropic 短暂停留后回到 DeepMind；Evan Hubinger 从 MIRI 来到 Anthropic；Arthur Conmy 在 DeepMind 与 Anthropic 之间反复横跳；Tom Henighan、Nelson Elhage、Tristan Hume——这串名字几乎覆盖了"机制可解释性"（mechanistic interpretability，下称 mech interp）这门年轻学科的整个核心圈。

图的右下角写着一行小字："2024 年，全球约 70% 的 mech interp 全职研究者直接受雇于 Anthropic，或正在与 Anthropic 合作发表论文。"[uncertain，数字来自社区粗略统计，无权威普查]

这是一张令人不安的图。在一个号称由三到四家前沿实验室竞争的行业里，一个被普遍认为对 AI 安全"至关重要"的子领域，几乎被一家公司垄断。OpenAI 有 Superalignment——已解散；DeepMind 有 Neel Nanda 团队——存在但规模有限；Google Research 有零星工作——多是学术合作。剩下的人，几乎都坐在 Anthropic 旧金山办公室的同一层楼里。

为什么？这是本章试图回答的问题。表层答案是"Anthropic 出价高、文化好、Chris Olah 个人魅力大"。这些都对，但都是结果，不是原因。真正的原因藏在三层结构里：组织结构、商业激励、文化叙事。这三层互相咬合，构成了一台只有 Anthropic 跑得起来的"可解释性飞轮"。

## 一、人才地图：一次缓慢的迁徙

要理解今天的格局，先回到 2014 年。那一年 Chris Olah 加入 Google Brain，写出后来被无数人当作启蒙读物的 Distill 文章——"Feature Visualization"、"Building Blocks of Interpretability"。Distill 这个期刊本身就是 Olah 与 Shan Carter 推动的实验：把研究做成可交互的网页，把可视化当作一等公民。

Olah 在 Brain 待到 2018 年，然后跳到 OpenAI，组建了 Clarity 团队。Catherine Olsson、Nelson Elhage、Ludwig Schubert 陆续加入。他们在 OpenAI Microscope 上做出了 InceptionV1 的电路解剖——"Curve Detectors"、"High-Low Frequency Detectors"——这是 mech interp 真正成形的时刻：研究者第一次声称，他们能指着神经网络的一组权重说，"这里是检测曲线的算法"。

2021 年 1 月，Dario 与 Daniela Amodei 带走七人，创立 Anthropic。Olah 是创始团队成员之一。Olsson、Elhage、Henighan、Hume 几乎同期跟进。这是一次"整建制"的迁徙：不是猎头一个一个挖，而是一整个研究文化连根拔起，移植到新土壤。

之后五年，迁徙继续单向流动。Evan Hubinger（"Risks from Learned Optimization" 论文一作）从 MIRI 来；Arthur Conmy（ACDC 算法作者）从 DeepMind 来；Trenton Bricken（SAE 关键贡献者之一）从博士项目直接来。反向流动几乎不存在——Neel Nanda 是唯一显著的例外，他在 2022 年从 Anthropic 短暂离开后选择回到 DeepMind 组建团队，理由公开说是"希望在 Google 内部推动可解释性"[来源：Nanda 个人博客与 80,000 Hours 访谈]。

到 2024 年，Anthropic 的 Interpretability Team 公开成员已超过 30 人[来源：Anthropic 官网团队页]，是 DeepMind 同类团队的三到四倍，是 OpenAI 的……无穷大倍——因为 OpenAI 已经没有这个团队了。

## 二、OpenAI 的失败：Superalignment 的解散

2023 年 7 月，OpenAI 高调宣布 Superalignment 项目，承诺投入 20% 的算力，由 Ilya Sutskever 与 Jan Leike 共同领导，目标是"四年内解决超级智能对齐"。一年后，2024 年 5 月，Sutskever 离开，Leike 在 X 上发出那条著名的辞职帖：

> "过去几年，安全文化和流程让位于亮眼的产品。"[来源：Jan Leike, X, 2024-05-17]

Leike 随即加入 Anthropic。Superalignment 团队解散，成员四散，其中相当一部分流向 Anthropic。

这不是孤立事件，而是 OpenAI 组织结构必然的结果。OpenAI 的商业模式高度依赖 GPT 系列的产品节奏：每一代模型必须按时发布，必须比上一代显著更强，必须支撑微软的 Azure 与 ChatGPT 的订阅收入。在这种节奏下，可解释性研究处于一个尴尬位置——它既不能直接提升下一代模型的能力，又不能在短期内为"对齐"提供可验证的承诺，于是在每一次资源分配的拔河中都站在弱势一方。

Leike 在 Anthropic 的入职公告里写："我加入 Anthropic 是因为 Anthropic 是少数把对齐研究放在 critical path 上的组织。"[来源：Anthropic 博客，2024-05-28] "Critical path"——这是关键词。在 OpenAI，可解释性是 nice-to-have；在 Anthropic，它被声称是 must-have。

[推测] 一种合理但无法证实的解读是：Sam Altman 个人对可解释性研究的兴趣有限，而 Dario Amodei 个人对其有近乎信仰般的执着。两位创始人的偏好，在公司还小的时候，就是公司的偏好。

## 三、DeepMind 的路径差异：Nanda 团队为何留下

DeepMind 是另一种故事。Neel Nanda 是个有趣的样本：他在 Anthropic 工作过，写过 mech interp 入门教程"A Comprehensive Mechanistic Interpretability Explainer"，培训了今天这个领域大半的新人。2022 年他离开 Anthropic，加入 DeepMind 组建 mech interp 团队。

为什么选 DeepMind 而非留在 Anthropic？Nanda 公开给过几个理由[来源：80,000 Hours 播客 #197，2024]：

第一，他想做"独立的"工作。在 Anthropic，Olah 是绝对的智识中心，所有方向都围绕 Olah 的品味展开；在 DeepMind，他能从零开始定义一个团队的研究议程。

第二，他相信 Google 的影响力。如果 mech interp 真的重要，那它需要被推广到 Google 这种规模的组织里，而不是只在一家 500 人的初创公司里精致地存在。

第三，[推测] 与 Anthropic 的高强度安全主义文化保持一定距离。Nanda 本人在公开场合表达过对"AI doom"叙事的保留态度，这种立场在 Anthropic 内部可能不算主流。

但 DeepMind 团队规模始终有限——公开估计在 10 人左右[uncertain]。原因不在于 DeepMind 不愿投入，而在于 DeepMind 的研究文化是"自下而上的兴趣驱动"：研究员可以做任何方向，但没有任何方向被组织性地推为"必须做"。这是 Google Research 的传统，也是它的诅咒——在一个"什么都可以做"的地方，没有任何东西能形成压倒性的资源集中。

Anthropic 反过来：它是"自上而下的方向收敛"。Dario 与 Olah 决定可解释性是公司的"科学旗舰"，于是公司的招聘、算力、对外品牌都向这个方向倾斜。一个小团队在大公司里慢慢长，永远长不过一个被整个公司当作核心叙事的团队。

## 四、Constitutional AI / RSP / Mythos：商业-安全飞轮

第三层，也是最容易被低估的一层，是商业层。

Anthropic 卖什么？表面上卖 Claude API，与 OpenAI 卖 GPT API 没有本质区别。但 Anthropic 卖给企业客户时，多了一个 OpenAI 不卖的东西：可审计的安全承诺。Constitutional AI（2022）、Responsible Scaling Policy（2023）、以及 2026 年初公布的"Mythos"框架与 Opus 4.7 的 RSP 触发机制[来源：Anthropic RSP v2.3 文档]，构成了一套向监管者与大企业 CISO 讲述的故事：

> 我们不仅训练强大的模型，我们还能向你证明——通过可解释性研究——这些模型内部正在发生什么。

这个故事是不是完全成立，是另一回事。但它能讲——能讲就有商业价值。金融、医疗、政府客户愿意为"可解释性背书"付溢价。可解释性研究在 Anthropic 不是成本中心，而是产品差异化的一部分。

这就是飞轮：安全研究 → 安全叙事 → 企业客户溢价 → 营收 → 更多算力 → 更多安全研究。OpenAI 没有这个飞轮，因为它的故事是"我们造最强的 AI"；DeepMind 没有这个飞轮，因为它属于 Google，对外讲故事的权力不在自己手里。只有 Anthropic 同时拥有三个条件：足够独立的品牌、足够聚焦的安全叙事、足够强的模型来支撑议价。

Opus 4.7 的发布过程是飞轮最赤裸的展示。RSP 触发了 ASL-3 评估，Anthropic 公开声明："基于内部可解释性团队对模型规划能力的 SAE 探针结果，我们推迟发布两周以完成额外评估。"[来源：Anthropic 模型卡，2026 Q1] 没有任何其他实验室做过类似的事——把可解释性的探针读数当作产品发布的 gate。这一刻，可解释性从一个"研究品味"变成了一个"商业决策依据"。

业内评测者中有一种常见的表达："benchmark 是给学界看的，决策 gate 才是给自己用的。"Anthropic 的可解释性团队，是全球唯一一个其研究产出被组织内部当作 decision gate 的可解释性团队。这是它能聚拢这么多人的根本原因——研究者想看到自己的工作真的影响什么。

## 五、垄断的代价

把可解释性集中在一家公司里，是好事还是坏事？

支持者会说：集中带来效率。SAE（Sparse Autoencoder）方向的爆发——从 Cunningham 等人 2023 年的早期工作，到 Anthropic 2024 年的 "Scaling Monosemanticity"，再到 2025 年对 Claude 3 Sonnet 的全模型特征字典——这种速度需要 50 个全职研究员、需要专门的训练算力、需要与模型团队的深度耦合。分散在五家公司里，永远做不出来。

批评者会说：集中带来偏见。如果所有 mech interp 论文都出自 Anthropic，那么这个领域的"什么算重要问题"完全由 Anthropic 定义。SAE 是不是最好的方法？也许是，也许只是 Anthropic 押注的方法。Circuit-style analysis 是不是真的能 scale？也许能，也许只是因为 Olah 喜欢 circuits。一个垄断的研究领域，会失去自我纠错的能力。

[推测] 更长期的风险是监管层面的：如果未来某国要求"前沿模型必须通过可解释性审计"，而全球只有一家公司有能力提供这种审计，那么 Anthropic 就同时是被监管者、监管工具的供应商、与监管标准的事实制定者。这是 Aaron Swartz 式的、Lessig 式的、所有研究"代码即法律"的人都熟悉的剧本。

## 结语：一座灯塔，还是一座围城

回到本章开头那张迁徙图。看图的方式有两种。

第一种看法：这是一座灯塔。一群信仰相同、品味相近、能力顶尖的研究者聚在一起，做出了任何分散组织都做不出的成果。人类对自己造出的智能体的理解，五年内从"完全黑箱"推进到"能在 Claude 3 Sonnet 中定位金门大桥特征"，主要要归功于这座灯塔。

第二种看法：这是一座围城。一个本该开放的科学领域，被一家公司的招聘、算力、叙事三重网络圈了起来。城外的研究者要么进城、要么改行、要么做边缘工作。学界几乎没有独立的 mech interp 教席[uncertain，截至 2025 年底]，因为最优秀的博士毕业生第二天就被 Anthropic 收编。

灯塔与围城是同一座建筑的两面。它之所以能照亮远方，正是因为它把所有的光收拢在一处；它之所以让人焦虑，也正是因为同一个理由。

下一章我们将走进这座建筑内部，看 Olah 团队真正在做什么——SAE 字典、特征引导、Golden Gate Claude——以及这些工作离"真正理解一个 LLM"还有多远。

---

**资料说明**：本章涉及的人员迁徙路径主要来源于 LinkedIn 公开履历、Anthropic 与 DeepMind 官网团队页、研究者本人博客与播客访谈。商业策略与 RSP 细节来源于 Anthropic 官方发布文档。标注 [推测] 与 [uncertain] 的段落为作者基于公开信息的解读或社区粗略数据，不构成事实陈述。
