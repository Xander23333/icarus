# Grounding

> Symbol grounding, multimodal grounding, referent 锚定。LLM 的 token 究竟"指向"什么？

## 核心问题与 NTP 假设

Symbol grounding problem 最早由 Stevan Harnad 在 1990 年的 *Minds and Machines* 上提出 ("The Symbol Grounding Problem")：一套封闭的符号系统如果只通过别的符号定义符号，最终会陷入循环字典——一个不识中文的人拿到一本中文-中文字典永远学不会中文。Harnad 的解药是让至少一部分符号"接地"到非符号的感觉-运动表征。三十多年后，这个问题以一种几乎相同的形态回到了 LLM 时代：next-token-prediction 训练目标只看 token-token 共现，从未要求模型把 "cat" 这个 token 锚定到任何外部 referent。

NTP-mech 阵营在 grounding 上的强主张通常包含三条：

1. **形式封闭性**：纯文本 NTP 在原理上不可能区分两个外延不同但分布完全相同的世界（Bender & Koller 2020, ACL "Climbing towards NLU: On Meaning, Form, and Understanding in the Age of Data" 的章鱼实验）。
2. **referent 缺失**：即使加上图像/音频模态，CLIP-style contrastive objective 学到的也是"co-occurrence in caption-image pair"，而非真正的指称关系（Mollo & Millière 2023 称之为 *vector grounding problem*）。
3. **行为可分性**：grounded 与 ungrounded 模型在某些"反事实指称"任务上必须分裂——否则 grounding 是空假设。

NTP-cap 阵营的回击是：(a) 分布信号本身就包含大量被低估的 grounding 信息（distributional grounding，Patel & Pavlick 2022 ICLR "Mapping Language Models to Grounded Conceptual Spaces" 显示纯文本 LM 在 color / direction / spatial 子空间能用极少 anchor 对齐到 grounded 表征 [unverified ID]）；(b) multimodal pretraining 已经在 referent 任务（VQA-grounded、RefCOCO、ScanRefer）逼近人类。

这个 topic 的目标是：把"grounding 在 LLM 上是真问题还是哲学问题"这一长期口水仗，转成一组**可被实验证伪**的具体子断言。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 | 引用 |
|---|---|---|---|---|
| 2026-05-25 | Li, Han, Wang et al., *Why LLMs Hallucinate on Structured Knowledge* | 在 linearized graph/multi-hop/table context 上，hallucination 的 sufficient statistic 是 **FFN-as-grounding** 失败而非 attention 失焦；跨 schema 通用，detector AUC>0.8 | mech (FFN-grounding 层；新候选 confound) | [2605.26362](../papers/paper_notes/2026-05-29-2605.26362-llm-hallucinate-structured.md) |

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 1990 | Symbol Grounding Problem (Harnad) | 纯符号系统无法 escape 字典循环，必须 anchor 到非符号表征 | mech (philosophical prior) | *Physica D* 42, non-arxiv |
| 2020-04 | Experience Grounds Language (Bisk, Holtzman, Thomason, et al.) | 提出 World Scopes (WS1 corpus → WS5 social interaction) 五级语料层次；指出纯文本停在 WS2 | mech (framework) | [arxiv:2004.10151](https://arxiv.org/abs/2004.10151) |
| 2020-07 | Climbing towards NLU (Bender & Koller, ACL) | 章鱼思想实验：分布信号原则上无法恢复 meaning = ⟨form, communicative intent⟩ 的 intent 分量 | mech | ACL 2020 anthology, non-arxiv |
| 2021-02 | CLIP (Radford et al.) | 4 亿图文对 contrastive 训练拿到 zero-shot ImageNet 76.2%；被广泛误读为 "grounding solved" | cap | [arxiv:2103.00020](https://arxiv.org/abs/2103.00020) |
| 2022 | Mapping LMs to Grounded Conceptual Spaces (Patel & Pavlick, ICLR) | 纯文本 GPT-3 在 color/direction 子空间能用 ~10 anchor pair 线性对齐到 grounded coords | cap (weakens strong-mech) | [unverified ID] |
| 2023-04 | The Vector Grounding Problem (Mollo & Millière) | 区分 5 种 grounding（referential, sensorimotor, relational, communicative, epistemic）；论证 RLHF 提供的是 *referential* grounding 的弱形式 | mech (taxonomy) | [arxiv:2304.01481](https://arxiv.org/abs/2304.01481) |
| 2023 | Symbols and grounding in large language models (Pavlick, Phil Trans R Soc B) | 实证综述：LLM 内部表征在多个 modality 上与 grounded 表征同构度高于随机 baseline 但低于 multimodal 模型 | cap (empirical) | non-arxiv |

> 注：本表为最小可引用集合，不追求完整。daily pipeline 后续会自动追加 2025–2026 的 grounding-relevant 论文（VLA 路线对 grounding 的隐含赌注另见 `embodiment.md`）。

## 当前共识 / 争议

- **共识 (弱)**：Harnad-Bender 强 mech 论点在"完全纯文本 LM、零 RLHF、零 multimodal" 这个极端 setting 下大致成立；问题是这个 setting 自 2022 年起已不存在于 frontier model。
- **共识 (中)**：现代 LLM 至少拥有 Mollo & Millière 分类中的 *relational* grounding（token 间结构关系正确）和部分 *referential* grounding（RLHF 期间人类标注提供了 token↔ 世界事件的稀疏对齐信号）。
- **争议**：sensorimotor grounding 是否能仅通过"看视频 / 读人类描述动作的文本"获得，还是必须 closed-loop interaction？这条线和 embodiment topic 高度耦合。
- **方法论争议**：用 probing classifier 测出来的"grounded 子空间"到底是模型真的 ground 了，还是 probe 自己在学映射？Hewitt & Liang 2019 "Designing and Interpreting Probes with Control Tasks" (EMNLP) [unverified ID] 的 selectivity 标准在 grounding 文献里被严重低估。

## NTP-mech 候选条目

**C-GROUND-1 (referential closure)**：存在一类"纯反事实指称"任务 T，使得 ∀ 仅在 text-only NTP 上训练的模型 M，pass@k(T, M) ≤ chance + ε，而同等容量的 multimodal/embodied 模型 pass@k(T, ·) ≥ 0.5。

- 反例条件 (falsifier)：找到一个 text-only NTP 模型在 T 上 ≥ 0.5。
- 当前状态：T 的标准化定义本身就有争议；Patel & Pavlick 的结果给出了**反向**证据（在 conceptual space 类 T 上 text-only 已经显著超 chance）。该条目当前评估为 **weak**，需要把 T 严格限制到 *deictic* / *novel-object* 子集才有救。

**C-GROUND-2 (RLHF as sparse referent injection)**：RLHF 通过 reward model 把人类对"输出是否对应真实世界事实"的判断注入梯度，等价于在 token-token 共现矩阵之外，新增了一条 token ↔ world-state 的稀疏监督信号。该信号的有效 bit/参数 量级远低于 pretraining，但解释力可能不成比例。

- 可测量 proxy：base model vs RLHF model 在 TruthfulQA / SimpleQA 上 gap 中，**多少**能用 "更精确的 token grounding" 解释，多少能用 "更好的指令跟随" 解释？目前文献几乎没区分这两者。

## Open problems

- 把 Mollo & Millière 的 5 类 grounding 落到**具体 benchmark**：每一类至少配一个 ≥ 1k 样本、能在 frontier model 上跑出 < 1.0 的 eval。当前缺 *epistemic grounding* (模型是否知道自己知不知道) 的标准评测——SimpleQA / SelfAware 是最接近的，但都未明确标 grounding 维度。
- 严格区分 grounding 与 hallucination：所有 hallucination 都是 grounding 失败，但反之不必然（一个 fully grounded 模型仍可以撒谎）。当前文献把两者混为一谈。
- VLA / embodied 路线（π₀、OpenVLA、RT-2）是否真的把 token grounding 推进了一步，还是只是在"被 ground 过的 caption"上做 imitation？需要 closed-loop counterfactual 测试 (见 `embodiment.md`)。
- distributional grounding 的上界：纯文本 LM 在哪些 modality 上能渐近达到 multimodal 模型？哪些根本达不到（候选：颜色 OK，3D 空间 OK 但慢，触觉/嗅觉 几乎不可能）？

## 反例与近期突破 (2023–2026)

把 grounding 当作\"text-only 永远不行\"的 mech 上界，是 2020–2022 那一波的共识。2023 年起，三条独立的证据线把这条上界压得越来越窄。

**线 1：纯文本 LM 能学出非平凡 spatial / perceptual 结构。** Patel & Pavlick 2022 之外，Abdou 等人 \"Can Language Models Encode Perceptual Structure Without Grounding?\" ([arxiv:2109.06129](https://arxiv.org/abs/2109.06129)) 在 BERT / RoBERTa 上发现 color term 的内部表征与 CIELAB 颜色空间存在显著但非完美的同构（Pearson r ≈ 0.5–0.7，远高于 random baseline 但低于人类 ≈ 0.9）。Li 等 \"Implicit Representations of Meaning in Neural Language Models\" ([arxiv:2106.00737](https://arxiv.org/abs/2106.00737)) 在 Alchemy / TextWorld 上探针出 entity-state 表征。Søgaard 2023 *Grounding the Vector Space of an Octopus* (TACL, [arxiv:2305.02223](https://arxiv.org/abs/2305.02223) [unverified ID]) 直接反驳 Bender-Koller 章鱼论：在分布信号足够丰富的情况下，referent 集合可以在同构 *up to permutation* 的意义上被恢复。这些结果不构成 \"grounding solved\"，但**确实把强 mech 的可证伪 setting 从 \"任何 grounded structure\" 缩到 \"deictic / novel-object / first-person sensorimotor\" 这个更窄的子集**。

**线 2：multimodal pretraining 在 referent 任务上的天花板比预想的低。** CLIP 之后五年，业界普遍假设 vision-language 模型已经把 referential grounding 解决了。2024 年的几个结果泼了冷水：Tong 等 \"Eyes Wide Shut? Exploring the Visual Shortcomings of Multimodal LLMs\" ([arxiv:2401.06209](https://arxiv.org/abs/2401.06209)) 构造的 MMVP benchmark 包含人类 95% 准确但 GPT-4V / Gemini Pro 仅 ~25% 的视觉对比题，多数失败模式是模型\"看见\"了 CLIP embedding 相近但语义相反的物体（朝左 vs 朝右、有 vs 无、开 vs 关）。Rahmanzadehgervi 等 \"Vision Language Models Are Blind\" ([arxiv:2407.06581](https://arxiv.org/abs/2407.06581)) 在七项小学几何任务（线段是否相交、圈是否重叠、字母计数）上 frontier VLM 全军溃败，准确率 20–60%。这条线说明：把 CLIP-style contrastive objective 扩到 10 亿规模并不能填上 grounding，contrastive loss 只学共现，不学 \"指称\"。从 NTP 视角看，VLM 的 next-token 目标在 vision token 上同样是分布信号——它继承了文本 NTP 的全部 grounding 局限，只是把模态换了一个。

**线 3：VLA / embodied 路线提供了第一批 closed-loop counterfactual 数据。** Open X-Embodiment ([arxiv:2310.08864](https://arxiv.org/abs/2310.08864)) 的 60 个数据集 + RT-2 ([arxiv:2307.15818](https://arxiv.org/abs/2307.15818)) / OpenVLA ([arxiv:2406.09246](https://arxiv.org/abs/2406.09246)) / π₀ ([arxiv:2410.24164](https://arxiv.org/abs/2410.24164)) 把 \"语言 token → 动作 token\" 的链路第一次大规模 closed-loop 化。但 Kim 等 2024 的 OpenVLA evaluation 显示：在 *unseen object × unseen instruction* 组合上成功率从 in-distribution 的 70% 跌到 < 20%，且失败模式高度集中在 deictic 指令（\"把*那个*放到*这边*\"）。这恰好是强 mech 阵营预言的 grounding 残差。

> **2026-05-27 判断**：grounding 这条战线上，2023–2026 的净进展不是\"text-only 不行\"被证否，也不是\"multimodal 解决了 grounding\"被证实，而是**可证伪 setting 被双向收窄**——一边把强 mech 推到 deictic / first-person 子集，一边把弱 cap 推到 contrastive 之外的 closed-loop interaction。这正好是 N5 (VLA bet) 与本 topic 的接合面。

## NTP-mech 候选条目 (续)

**C-GROUND-3 (deictic asymmetry)**：在 deictic / first-person 指令子集 D 上，纯文本 + image-caption multimodal 训练的模型成功率上界 ≤ 0.3，而加入 ≥ 10⁴ 小时 ego-centric 视频或 ≥ 10⁶ 步真实/仿真 closed-loop 交互的模型成功率 ≥ 0.6。

- 反例条件 (falsifier)：任意 text-only 或 image-caption-only 模型在标准化 D 上 > 0.5；或任何 embodied 模型在 D 上 < 0.4。
- 当前状态：D 的候选包括 RefCOCO 的 deictic 子集、Ego4D NLQ ([arxiv:2110.07058](https://arxiv.org/abs/2110.07058)) 的 first-person 指代部分、RoboVQA ([arxiv:2311.00899](https://arxiv.org/abs/2311.00899) [unverified ID]) 的 embodied QA。三者都没被刻意当作 grounding falsifier 设计，需要重切。该条目当前评估为 **medium**：方向清晰但 benchmark 不齐。
- 与 C-GROUND-1 的区别：C-GROUND-1 押的是 \"任意反事实指称\"，已经被 Patel-Pavlick / Søgaard 削弱；C-GROUND-3 把战场限定到 deictic / first-person，理论上更难被纯分布信号攻陷。

**C-GROUND-4 (contrastive ≠ referential)**：存在一个 benchmark 家族 B，使得 ∀ 只用 contrastive (CLIP-style) 或 captioning (BLIP-style) objective 训练的 VLM，pass@1(B) ≤ 0.3，而加入 region-level grounding loss (GLIP / Grounding-DINO 风格 [arxiv:2112.03857](https://arxiv.org/abs/2112.03857)) 或 spatial supervision 的同等规模模型 pass@1(B) ≥ 0.7。

- 候选 B：MMVP ([arxiv:2401.06209](https://arxiv.org/abs/2401.06209)) 已经部分满足；BLINK ([arxiv:2404.12390](https://arxiv.org/abs/2404.12390)) 的 spatial relation / depth ordering 子集是更干净的候选。
- 工程意义：如果 C-GROUND-4 成立，那么 \"把数据量再放大 10 倍\" 不是出路，必须改 objective。这与 NTP-cap 阵营的\"scale is all you need\" 直接对立。

## 经验测量线 — probe / activation patching / counterfactual 三代探测史 (2018–2026)

Grounding 这条战线在 2020 年之前几乎全是哲学论战，2020 年之后逐渐变成一个 *方法学* 问题：我们到底用什么测量手段判定一个 LM 内部"接地了"？这条线大致分三代，每一代都修正了上一代的最大方法学漏洞。

**第一代：linear / MLP probe (2018–2021)。** Conneau 等 *What you can cram into a single vector* ([arxiv:1805.01070](https://arxiv.org/abs/1805.01070)) 用 10 个 sentence-level 任务 probe BiLSTM/Transformer 句向量，开启 "训一个 classifier 就能宣称模型 encode 了 X" 的范式。Hewitt & Manning 2019 *A Structural Probe for Finding Syntax in Word Representations* (NAACL) 在 BERT 上拿出树结构 probe distance correlation ≈ 0.85，被广泛误读为 "BERT 学了语法"。问题在 Hewitt & Liang 2019 *Designing and Interpreting Probes with Control Tasks* (EMNLP, [arxiv:1909.03368](https://arxiv.org/abs/1909.03368)) 当场捅破：用同样大小的 probe 去拟合 *随机标签*（control task）能达到 selectivity-defined baseline 的 50–80%，意味着 probe 自身的拟合能力被严重低估为 "模型自带的结构"。这条批评对 grounding 文献的杀伤被 *系统性低估* 了——Abdou 2021 / Patel & Pavlick 2022 的结果若不附 control task，仅能说明 probe 能学映射，不能直接断言模型 ground 了 color/direction。

**第二代：activation patching / causal mediation (2022–2024)。** 为绕开第一代的拟合幻觉，Vig 等 *Causal Mediation Analysis for Interpreting Neural NLP* ([arxiv:2004.12265](https://arxiv.org/abs/2004.12265)) 把 Pearl mediation 框架第一次搬进 transformer。Meng 等 ROME ([arxiv:2202.05262](https://arxiv.org/abs/2202.05262)) 用 causal tracing 在 GPT-J 上定位 "Eiffel Tower → Paris" 事实的中层 MLP，并通过 rank-one 编辑成功改写事实——这是**第一次** grounding-style 表征被 *干预测试* 而非仅 *观察相关*。Geva 等 *Dissecting Recall of Factual Associations* ([arxiv:2304.14767](https://arxiv.org/abs/2304.14767)) 在 GPT-2 / Pythia 上把事实回忆拆成 subject enrichment → relation propagation → object readout 三阶段。同期 Geiger DAS ([arxiv:2303.02536](https://arxiv.org/abs/2303.02536)) / Conmy ACDC ([arxiv:2304.14997](https://arxiv.org/abs/2304.14997)) 提供了端到端自动定位 grounding 子电路的工具。这一代把 "模型表征是否 ground" 从相关性升级到 *干预等价类*，但 grounding 社区采纳得极慢——MMVP / VLM-Blind 之类 2024 年的 grounding-failure 论文几乎没用 activation patching。

**第三代：counterfactual + cross-modal causal probe (2024–2026)。** 第二代仍主要在文本-only 单模态内做，对 grounding 的核心问题 "token 是否 *指向* 外部世界" 力度不够。三个 2024–2026 方向把闸门往前推：(i) Vafa 等 *Evaluating the World Model Implicit in a Generative Model* ([arxiv:2406.03689](https://arxiv.org/abs/2406.03689)) 用 Myhill-Nerode 半干预测试在 Othello/纽约出租车数据上同时检测 *相关* 与 *因果* world-model 强度，揭示 next-token-low-loss + world-model-incorrect 的常见组合；(ii) Brinkmann 等 multimodal activation patching ([arxiv:2402.11917](https://arxiv.org/abs/2402.11917) [unverified ID]) 在 LLaVA 上做 cross-modal causal mediation，定位 vision token 在哪一层真正进入 "semantic" 残差流——结果是大多数 vision token 直到 layer 18+ 才被语义化，前层只走拷贝路径，部分解释了 MMVP 失败；(iii) Causal Tongue-Tie ([arxiv:2605.25891](https://arxiv.org/abs/2605.25891)) 在 anti-commonsense CLadder 上 linear probe 0.97 vs yes/no readout 0.5 — 直接证明 *内部表征* 与 *外部行为* 在 grounding-相关任务上能解耦 0.47 个 accuracy 单位，迫使任何 grounding 声称必须附 probe + readout 双轨证据。

> **2026-05-27 判断**：grounding 文献在概念层面发达，在测量层面落后两代——大量被引用的 "LM 学到/没学到 grounded structure" 结论实际只用了第一代 probe，未控制 Hewitt-Liang selectivity，也未做 Vig-Meng 风格干预。这意味着 grounding 的 *经验* 共识比表面上脆弱得多：把现有结果按 "probe-only / patched / counterfactual-validated" 三档重新分箱，2026 年能进入第三档的论文不超过 5 篇。这也是 C-GROUND-1/3/4 三个候选条目至今没人能严格 falsify 的*方法学*原因，而非 *机制* 原因——我们没有合格的测尺。下一步行动：把 MMVP / VLM-Blind 上失败的 ~30 个最干净 minimal-pair 用 activation patching 重测一遍 vision token 是否真的进入 semantic 残差流，是 18 个月内最可能产出 grounding mech-vs-cap 判决的实验。

## Tool-use / action grounding — 第六类 grounding (2023–2026)

Mollo & Millière 2023 的五分类（referential / sensorimotor / relational / communicative / epistemic）写于 ChatGPT plugins 刚发布、function-calling API 尚未标准化的窗口期。三年下来，frontier model 的实际使用形态被 *tool use / function call / agentic loop* 重塑——而这个形态触碰到一种五分类没有显式覆盖的 grounding：**模型输出的 \"action token\"（函数名、参数、bash 命令、SQL 语句）是否真的对应可执行的、有正确副作用的操作**。Sensorimotor grounding 讨论的是连续控制信号（电机扭矩、关节角），不能直接覆盖离散符号 API 调用；referential grounding 讨论的是名词 token 是否指向稳定 referent，但不约束 \"做\" 这个动词的真值条件。把这条线单拉出来是必要的，因为 2024–2026 大半 agentic-eval 失败模式都落在这一类。

- **2023-03 — Schick et al., *Toolformer* ([arxiv:2302.04761](https://arxiv.org/abs/2302.04761))**。Meta FAIR 的 Timo Schick 把 calculator / Wikipedia / translate 等 5 个工具调用通过 self-supervised 方式 inline 进 GPT-J 的 NTP 训练。关键操作化：工具调用结果 *作为 token 序列回灌* 进 context，模型不直接接触执行环境。这定义了 \"action grounding\" 的最弱版本——token 序列正确 ≠ 动作真正发生。
- **2023-04 — Yao et al., *ReAct* ([arxiv:2210.03629](https://arxiv.org/abs/2210.03629))**。把 reasoning trace 与 action trace 交错生成；在 ALFWorld / WebShop 上展示纯 prompting 即可推动 agentic loop。但同期 Liu et al. *AgentBench* ([arxiv:2308.03688](https://arxiv.org/abs/2308.03688)) 在 8 类 agent 任务上测出 GPT-4 平均成功率 ~42%、open-source 7B–70B 多在 10% 以下；失败模式高度集中在 \"语法正确但语义错的 action token\"（参数顺序错、字段名幻觉、null 字段当字符串填）。这是 action grounding 第一次被系统量化为独立失败维度。
- **2024-03 — Patil et al., *Gorilla* ([arxiv:2305.15334](https://arxiv.org/abs/2305.15334))** + **APIBench / BFCL (Berkeley Function-Calling Leaderboard, 2024-05)**。把 API 调用 hallucination 拆成 \"function name hallucination / parameter name hallucination / type error / required-arg missing\" 四类独立 metric。frontier model 在 simple call 上 ≥ 90% 但 parallel + nested call 上跌到 50–70%——与 N3 §3 Reversal Curse / N4 d-sep 那种 \"训练分布外即崩\" 的 NTP 内禀失败模式同源。
- **2024-10 — SWE-bench 系列 (Jimenez et al., [arxiv:2310.06770](https://arxiv.org/abs/2310.06770))** 与其后 *SWE-bench Verified* (OpenAI, 2024-08, non-arxiv)。把 \"模型给出的 patch 是否真能让 test suite 通过\" 作为唯一指标——这是第一次让 action grounding 完全由 *外部执行器* 仲裁，绕开 LLM-judge。2024 年初 SOTA 4.4% (Devin demo)、年中 22–43%（Cognition / Cursor / Anthropic SWE-agent），2025 年中已到 60%+。但 Aleithan et al. 2024 *SWE-Bench+* ([arxiv:2410.06992](https://arxiv.org/abs/2410.06992)) 指出 SWE-bench 训练集污染与 test-leakage 占测出收益的 30–60%——这意味着\"action grounding 在工程任务上的真实进步\" 与 *公开 leaderboard 数字* 之间存在显著差距。
- **2025–2026 — τ-Bench / WebArena / OSWorld 多轮 agentic eval**。τ-Bench (Yao et al., [arxiv:2406.12045](https://arxiv.org/abs/2406.12045)) 把 customer-service 多轮 tool-use 做成可复现协议，frontier model 在 retail 域 pass^4 跌到 25% 以下；OSWorld (Xie et al., [arxiv:2404.07972](https://arxiv.org/abs/2404.07972)) 在真实 OS GUI 上 GPT-4V 仅 12%。**所有这些 eval 共同特征**：单步 action token 准确率高（语法、API 名都对），但 *跨步 state-tracking* 错——即模型不能稳定维护 \"我刚才已经把这个 field 改过了\" 这种 grounded world state。这把 action grounding 与 [world_model](world_model.md) C-WM-1 的 closed-world bottleneck 直接耦合。
- **2026-05 — readout-side confound 在 agentic setting 的对应**。Garcia 2026 / Causal Tongue-Tie 2605.25891 / ProFIL 2605.11467 这一波的核心结论是 \"verbal CoT 失败一半是 readout 伪影\"——把同一框架搬到 agent 上的对应预测是：**agentic 失败的相当比例不是 planning 失败而是 \"内部知道下一步该调什么 API 但 output token 走偏\"**。截至 2026-05 公开文献里 *没有* 在 agentic trajectory 上做对应的 probe-vs-readout 拆分实验——这是 action grounding 与 reasoning 文献当前最大的方法学债。

新增候选条目：

**C-GROUND-5 (action-execution gap)**：对任意纯 NTP 训练的 LM（含 VLM/VLA），存在一类多轮 tool-use 任务族 A，使得 (i) 单步 action-token *语法合法率* ≥ 0.9，但 (ii) 端到端 *执行器仲裁* pass^k(k≥4) ≤ 0.4；且差距 (i)−(ii) ≥ 0.4 在 7B–400B 规模范围内对 N 不显著敏感。

- 反例条件 (falsifier)：找到一个纯 NTP 训练的模型在某个公开多轮 agentic benchmark 上 pass^4 与单步 syntactic accuracy 差距 < 0.1，且 benchmark 不存在 SWE-bench+ 报告的污染等级 (≥ 30%)；或证明 (i)−(ii) gap 随 N 单调收敛到 0。
- 当前评估：**medium-strong**。AgentBench / τ-Bench / OSWorld / BFCL parallel-call 四条独立测量在数量级上一致；尚缺 controlled re-fit 把 \"action-grounding 失败\" 与 \"state-tracking 失败\" 分离。
- 与现有候选的关系：C-GROUND-5 与 C-GROUND-3 (deictic asymmetry)、C-GROUND-4 (contrastive ≠ referential) 互补——前两个钉名词类 token 的 referent 锚定，C-GROUND-5 钉动词类 token 的 truth-conditional 执行对应；与 C-WM-1 (closed-world bottleneck) 共享 multi-step state-tracking 这个 confound 通道。
- 工程意义：若 C-GROUND-5 成立，则 \"把 base model 再放大\" 在 agentic deployment 上的边际收益受 *grounding 而非 reasoning* 限制——这恰好解释了为何 2024–2026 工程界把投资从 base-scale 转向 (i) 执行环境 RL（SWE-RL / agent-RL）、(ii) 外部 verifier / scratchpad-memory（Letta、Mem0、context engineering）两路而非继续堆参数。

> **2026-05-28 判断**：把 action / tool-use grounding 从 sensorimotor + referential 两类的边缘地带拎出来作为独立第六类，不是 taxonomy 洁癖，而是因为它对应的失败模式（参数幻觉、跨步 state 漂移、执行器仲裁 vs LLM-judge 落差）在 2024–2026 已经成为 frontier deployment 主要瓶颈，且其 *证据链已比 C-GROUND-1 当年完整*：四个独立 benchmark 一致、与 N3 / N4 / N6 已有 mech 候选可对接、有清晰 falsifier。下一步关键不在再做一个 agent eval，而在 (i) 在某个公开 agent trajectory 上做 readout-vs-probe 拆分实验，看 action-token 出口前的 hidden state 是否已经包含正确动作（类似 Causal Tongue-Tie 在 yes/no 上做的事）；(ii) 把 SWE-bench+ 污染量级稳定后，跨 7B / 70B / 400B 三档拟合 (i)−(ii) gap 随 N 的曲线，给 C-GROUND-5 一个 Allen-Zhu Part 3.3 级别的硬约束。两项实验都不需要新数据，只需要现有 model + 现有 benchmark 重测。

## Retrieval-augmented grounding — 第七类 candidate (2020–2026)

把 RAG 单拎为一类 grounding，乍看像凑数：检索系统从 1990s IR 一路延续，BM25 + 大模型在工程上是把 retrieval 当 *context-injection*，与 grounding 哲学讨论似乎隔行。但 2023 年起，关于 RAG 究竟"接地了什么"的争论日益尖锐，且与 Mollo & Millière 五分类、与上文 §Tool-use 第六类都有清晰分界，所以单列。

核心问题：当 LM 在 generation 时把外部文档 *拼进 context* 并据此输出 token，这套机制提供的 grounding 与 (i) RLHF 注入的稀疏 referent 信号、(ii) multimodal pretraining 提供的 cross-modal 共现、(iii) tool-execution 提供的 truth-conditional 仲裁，分属什么层级？

- **2020-05 — Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP* ([arxiv:2005.11401](https://arxiv.org/abs/2005.11401))**。RAG 原始定义：一个 dense retriever + 一个 seq2seq generator，end-to-end 训练。彼时 framing 是 "把 parametric memory 与 non-parametric memory 解耦"，未触及 grounding。
- **2022-08 — Izacard et al., *Atlas* ([arxiv:2208.03299](https://arxiv.org/abs/2208.03299))**。few-shot KILT / Natural Questions 上 11B Atlas 接近 540B PaLM——表面上是参数效率胜利，潜台词是：当 retrieval 命中时，generator 不需要把事实 *存* 进权重，只需要 *搬运*。从 grounding 视角，这是把 referent → 权重内部联想链 解耦为 referent → 检索证据 → 输出 的可审计链路。
- **2023-05 — Min et al., *FActScore* ([arxiv:2305.14251](https://arxiv.org/abs/2305.14251))** 与 **Gao et al., *ALCE: Enabling LLMs to Generate Text with Citations* ([arxiv:2305.14627](https://arxiv.org/abs/2305.14627))**。第一次把 "输出的每个原子事实是否被引用文档支持" 操作化为 atomic-fact-level metric。结果令人沮丧：ChatGPT-RAG 在 ALCE 上 citation precision/recall 60–70%、原子事实 attributable 比例 ~60%；纯参数 ChatGPT 在 FActScore 上传记类原子事实正确率 58%——RAG 注入的 "grounding" 在 atom 级别远比 leaderboard 数字脆弱。
- **2023-10 — Asai et al., *Self-RAG* ([arxiv:2310.11511](https://arxiv.org/abs/2310.11511))**。在 generation 时插入 self-reflection token（[Retrieve]、[IsRel]、[IsSup]、[IsUse]）让模型自我判断检索必要性与支持度。把 grounding 决策内部化的尝试，但 Wu et al. 2024 *How faithful are RAG models?* ([arxiv:2404.10198](https://arxiv.org/abs/2404.10198)) 后续实验显示：当 retrieved context 与 parametric memory 冲突时，frontier LLM 倾向 *选权重内的答案*，且这种 confirmation-bias 随模型规模轻微 *上升* 而非下降——RAG 没有自动覆盖 parametric prior。
- **2024-01 — Niu et al., *RAGTruth* ([arxiv:2401.00396](https://arxiv.org/abs/2401.00396))**。把 RAG hallucination 分成 *evident conflict / subtle conflict / evident introduction / subtle introduction* 四类，标了 18k human-annotated spans。frontier model 在 *subtle introduction*（在 context 没说的地方编一个合理的额外细节）类别上 hallucination rate 仍 8–20%，且 retrieval 召回率提升不能消除——这是 grounding-as-injection 范式的 *内禀* 失败模式，不是召回工程问题。
- **2024-04 — Lee et al., *Long-Context vs RAG* on LOFT ([arxiv:2406.13121](https://arxiv.org/abs/2406.13121) [unverified ID])** 与 **Gemini 1.5 1M-token 一类长上下文模型的兴起**。当 context window 涨到 1M token，RAG 的 chunk-retrieve-rerank pipeline 在多个 benchmark 被 native long-context 反超——这逼出一个新问题：long-context attention 内部对 retrieved span 的处理，和 RAG-injection 是否本质同构？还是注意力分配模式不同导致 grounding 效果不同？目前没有 controlled 拆解。
- **2024-10 — Wei et al., *Long-form factuality in LLMs* (SAFE, [arxiv:2403.18802](https://arxiv.org/abs/2403.18802))** 把 atomic-fact 评估自动化（LLM-judge + 在线搜索），F1 与人类标注 ~72%。但 LLM-judge 本身的 grounding 缺陷使这套 metric 自身有 ~10% 系统偏差，构成 grounding 评估的"测量者悖论"。
- **2025–2026 — Agentic RAG / GraphRAG / multi-hop retrieval**（如 Edge et al. *GraphRAG* [arxiv:2404.16130](https://arxiv.org/abs/2404.16130)）。把检索从 single-shot 推到 iterative + structured，但 Yu et al. 2025 *Evaluation of RAG: a Survey* ([arxiv:2405.07437](https://arxiv.org/abs/2405.07437) [unverified ID]) 综合 30+ benchmark 显示：multi-hop QA 的 RAG 收益相对 single-hop 显著下降，且 *retrieval-induced hallucination*（错误检索导致的下游错误）超过单纯参数 hallucination——更多检索 ≠ 更多 grounding。

新增候选条目：

**C-GROUND-6 (RAG-injection ≠ referent stabilization)**：对任意纯 NTP 训练的 LM，在标准 RAG pipeline（top-k retrieval + context concatenation + greedy/sample generation）下，存在一类 atomic-fact 评估族 F，使得 (i) retrieval recall@5 ≥ 0.9，(ii) generator output 的 citation precision ≥ 0.8，但 (iii) atomic-fact attribution rate ≤ 0.75 且 (iv) 在 context 与 parametric prior 显式冲突的 subset 上 ≥ 30% 概率选择 parametric 答案。

- 反例条件 (falsifier)：在 F 上某模型同时达到 (iii) ≥ 0.9 且 (iv) ≤ 0.1，且 F 不限定到 "高 retrieval recall + 简单 single-hop" 的窄子集。
- 当前评估：**strong**。ALCE / FActScore / RAGTruth / Wu 2024 / SAFE 五条独立测量在数量级一致；frontier model 2023–2026 进步主要在 (i)(ii) 工程层，(iii)(iv) 的 internal-prior-vs-context 张力没有可衡量收敛。
- 与 C-GROUND-5 (action-execution gap) 的对偶：C-GROUND-5 押 action token 的执行真值 gap，C-GROUND-6 押 fact token 的支持文档 gap；前者由外部 executor 仲裁，后者由 atom-level NLI / human 仲裁；两者都揭示 *NTP loss 低 + grounding 失败* 的常见组合（与 N6 §Vafa world-model 实验同构）。
- 与 [online_learning](online_learning.md) C-CONT-1 知识编辑 ripple-effect 的耦合：RAG 被工程界推为 "不用改权重就能更新知识" 的方案，但 (iv) 揭示 parametric prior 在冲突时仍占优——这意味着 RAG 不能真正绕开 online-learning 的 plasticity 问题，只是把它推迟到 generation 时刻的 attention 选择上。

> **2026-05-28 判断**：把 RAG / retrieval-augmented context 单列为第七类 grounding 而非 *referential grounding 的工程实现*，理由有三：(a) 它的失败模式（subtle introduction、parametric-prior dominance、retrieval-induced cascading hallucination）与纯 referential 的失败模式（章鱼论、deictic asymmetry）不同源——前者是 *有 grounding 信号但不被采纳*，后者是 *grounding 信号缺失*；(b) 它与 C-GROUND-5 (action) 在仲裁机制上构成对偶（executor vs attribution-NLI），与 C-GROUND-3 (deictic) 在符号-感觉接口上无重叠，三者切的是 grounding 这条战线上 *被忽视的不同维度*；(c) 工程意义不一样——若 C-GROUND-6 成立，则 "retrieval-augmented frontier LM 就是 grounded LM" 的产品级说辞是 *测量不足导致的乐观*，真实接地度需要 atom-level 而非 leaderboard-level 评估。下一步关键实验：把 RAGTruth 的 subtle-introduction 子集与 Wu 2024 的 context-parametric conflict probe 合并，跨 7B / 70B / 400B / RAG-tuned-vs-vanilla 四档拟合 (iv) 随 N、随 RAG-训练量的曲线，给 C-GROUND-6 同样 Allen-Zhu Part 3.3 级别的硬约束——此实验同样不需要新数据，只需 controlled re-fit。

## Epistemic grounding — 第八类 candidate (2022–2026)

Mollo & Millière 2023 把 *epistemic grounding* 列为五分类的最后一项，但论文里几乎只占两段——它指的是 \"模型 token 是否锚定到一个 *关于自己知识的二阶事实*\"，例如\"我不知道这位作者的生卒年\"。这一类 grounding 与前七类的形式区别在于：referent 不是外部对象，而是 *模型自身权重内部知识的边界*——这把 grounding 问题压成 LLM 的内省可靠性问题。三年下来，相关 benchmark 与 mech-interp 工作积累得比 Mollo & Millière 当年预计的更密，但 2026-05 仍未被任何文献正面纳入 grounding taxonomy；与 §Tool-use (第六类) / §Retrieval-augmented (第七类) 同样有把它单列为第八类 candidate 的结构性理由。

- **2022-07 — Kadavath et al. (Anthropic), *Language Models (Mostly) Know What They Know* ([arxiv:2207.05221](https://arxiv.org/abs/2207.05221))**。在 TriviaQA / Codex 等 23 个 task 上让模型自评 P(answer is correct)，发现 frontier (52B) Claude-precursor 的 calibration ECE < 0.05，且 \"P(IK) — 我知道这题答案吗\" 在 fine-tune 后跨任务 generalize。这是 epistemic grounding 第一次被操作化为可测量的 *self-knowledge probability*，而不是哲学论断。但该论文也明确：calibration 在 OOD / adversarial 分布上崩溃，且 scale 收益在 13B → 52B 之后边际递减——self-knowledge 不随 N 单调改善。
- **2023-05 — Yin et al., *Do Large Language Models Know What They Don't Know?* (SelfAware, [arxiv:2305.18153](https://arxiv.org/abs/2305.18153))**。构造 1032 个明确 unanswerable 问题（未来事件、主观偏好、未定义概念），测 GPT-3.5 / GPT-4 / LLaMA 在 \"答 unknown\" 上的 F1。frontier 模型 F1 ≈ 75%，open-source 7B 多在 40–55%——但 SelfAware 的 unanswerable 边界本身存在 ground-truth 争议，约 15% 样本不同标注者意见分歧。这是 epistemic grounding 评测的 *测量者* 问题，结构同 §RAG 的 LLM-judge 悖论。
- **2023-09 — Tian et al., *Just Ask for Calibration* ([arxiv:2305.14975](https://arxiv.org/abs/2305.14975))**。系统比较 verbalized confidence（让模型直接说 \"我有 80% 把握\"）vs logit-based confidence（softmax probability）vs consistency-based（采样多次的一致率）。结论：RLHF 后的 frontier model 在 verbalized confidence 上 calibration *优于* logit——这是 readout-side 现象的一个正向案例（与 reasoning topic Causal Tongue-Tie 方向相反，verbal readout 在 epistemic 维度有时反而更准）。
- **2023-11 — Zhang et al., *R-Tuning: Instructing Large Language Models to Say I Don't Know* ([arxiv:2311.09677](https://arxiv.org/abs/2311.09677))**。第一次把 \"知道-边界 tuning\" 操作化为 fine-tune 数据格式：把训练集按模型当前 P(correct) 切成 \"willing\" / \"refusal\" 两半。post-tuning 模型在 hallucination rate 上降 10–30%，但对 in-distribution accuracy 几乎无害——这意味着 epistemic grounding 不必和 capacity 交换。但 Yin et al. 后续在 OOD 上测发现 R-Tuning 的 refusal 行为对 *分布偏移* 高度敏感，generalize 不稳。
- **2024-10 — OpenAI *SimpleQA* (non-arxiv tech report)**。4326 个 short-form factual 问题、人类双标、显式 *not attempted* 类别。frontier 报告：GPT-4o ≈ 38% correct / 47% incorrect / 15% not attempted，o1-preview ≈ 42% / 35% / 23%——更强的模型 *不是* 在 correct 上提升，而是在 *学会说我不知道* 上提升。这是 epistemic grounding 在 frontier 上的第一份 production-grade 测量，且其 \"correctness − attempted\" gap 与 §RAG C-GROUND-6 的 (iv) parametric-prior dominance 直接对偶——前者衡量模型 *不该答时是否克制*，后者衡量 *该用 context 时是否克制 prior*。
- **2024-04 — Manakul et al., *SelfCheckGPT* ([arxiv:2303.08896](https://arxiv.org/abs/2303.08896))** + 后续 *FactScore* / *HaluEval* 系。基于 sampling-consistency 的 hallucination 检测在 7B–70B 上 AUC 0.7–0.85，但跨 domain (biomedical vs general) 显著退化——hallucination 与 epistemic mis-grounding 不完全重合，前者包含后者但还有 stylistic confabulation 等非 epistemic 成分（与 grounding 总论里 \"所有 hallucination 都是 grounding 失败，但反之不必然\" 一致）。
- **2024–2026 mech-interp 侧 — internal-belief vs output-confidence 解耦**。Burns et al. *Discovering Latent Knowledge Without Supervision* (CCS, [arxiv:2212.03827](https://arxiv.org/abs/2212.03827)) 在隐藏层找到 \"模型相信 X 为真\" 的方向，且该方向与 output 的 yes/no 概率分离度可达 0.3–0.5 ROC-AUC——内部 belief 与外部声称的 confidence 在 epistemic 维度系统性脱钩。MacDiarmid et al. (Anthropic) 2024-04 *Simple probes can catch sleeper agents* (non-arxiv blog) 显示 probe 能检测出模型 \"知道自己在撒谎\" 的 internal signal。Marks & Tegmark 2023 *The Geometry of Truth* ([arxiv:2310.06824](https://arxiv.org/abs/2310.06824)) 提供线性 truth direction。这些工作把 epistemic grounding 从 \"output 校准\" 问题升级到 \"output 与内部 belief 是否一致\" 问题，与 reasoning topic readout-主导假设直接平行。
- **2026-05 — Li/Han/Wang *Why LLMs Hallucinate on Structured Knowledge* ([2605.26362](../papers/paper_notes/2026-05-29-2605.26362-llm-hallucinate-structured.md))**。在 linearized graph / multi-hop / table context 上，hallucination 充分统计量是 FFN-as-grounding 失败而非 attention 失焦。把 epistemic grounding 失败 *定位* 到 FFN 子电路——这是把上述 mech-interp 线落到 grounding 失败具体机制的最近期数据点，且 detector AUC > 0.8 跨 schema 通用。

新增候选条目：

**C-GROUND-7 (epistemic asymmetry between internal belief and output confidence)**：对任意纯 NTP 训练的 LM（含 RLHF / verbalized-confidence tuning），存在一类 atomic-claim 评估族 E，使得 (i) Burns-style internal probe 对 \"模型相信该 claim 为真\" 的 ROC-AUC ≥ 0.8，(ii) 同一 forward pass 上 verbalized confidence 与 logit-based confidence 的 ECE ≤ 0.05，但 (iii) probe-derived belief 与 output-derived confidence 在 contested / hallucination-prone subset 上的相关 ρ ≤ 0.5；且该 gap (iii) 在 7B–400B 规模范围内对 N 不显著敏感，对 RLHF 训练量轻微下降但不归零。

- 反例条件 (falsifier)：在 E 上某模型同时达到 (i) AUC ≥ 0.8 与 (iii) ρ ≥ 0.85，且 E 不限定到 \"easy factual / 高 self-consistency\" 的窄子集；或证明 (iii) gap 随 N 或 RLHF 量单调收敛到 0。
- 当前评估：**medium-strong**。Burns 2212.03827 / Marks-Tegmark 2310.06824 / MacDiarmid 2024 / Li 2605.26362 四条独立测量在 internal-vs-output 解耦上数量级一致；SimpleQA 的 *correct − attempted* gap 跨 frontier model 不收敛构成宏观对应证据。缺 controlled re-fit 跨 N × RLHF 量两维度的 calibration 曲线。
- 与其他 candidate 的关系：C-GROUND-7 押 *epistemic readout* 与 *internal belief* 的分离，是 reasoning topic Causal Tongue-Tie / ProFIL 那条 readout-主导假设在 grounding 维度的 *镜像*——但镜像方向相反（reasoning 上 verbal readout 拉低 accuracy，epistemic 上 verbal readout 反而更校准），所以两者合在一起说明 readout-side 现象的 *方向* 由 task type 决定，不是单一 direction 偏差。与 C-GROUND-5 (action-execution gap) / C-GROUND-6 (RAG-injection gap) 共同构成 \"NTP loss 低 + grounding 失败\" 三连组合，分别对应 action / fact / belief 三类 token 的 truth-conditional 接地缺口。
- 工程意义：若 C-GROUND-7 成立，则 *基于 verbalized confidence 的 abstention/refusal 部署*（包括 R-Tuning / SimpleQA-style not-attempted、Anthropic constitutional self-critique）在系统性 hallucination-prone 分布上 *本质不可靠*——因为模型 *能* 知道自己不该答（probe 测得到），但 readout 不让它说出来；解决方案不是更大 RLHF 而是 *probe-based abstention*（同 reasoning topic ProFIL 把 probe 当 RL filter 同型）。

> **2026-05-28 判断**：把 epistemic grounding 单列为第八类 candidate 而非 *referential / RAG / action 三类的 calibration sub-aspect*，理由有三：(a) 它的 referent 是 *模型自己*，与前七类的 *外部对象 / 文档 / 执行环境* 在 grounding 类型上不同源——内省可靠性是独立 grounding 维度而非校准副作用；(b) 它的失败模式（internal-belief 与 output-confidence 解耦、 frontier scale 不单调改善、verbal readout 方向与 reasoning 相反）与前七类失败模式 *形式不同源*——这正是 taxonomy 单列的 Mollo-Millière 标准；(c) 工程意义不同：若 C-GROUND-7 成立，所有基于 verbalized refusal 的安全部署都要补 probe-based abstention，这是与 §Tool-use C-GROUND-5 / §RAG C-GROUND-6 *正交* 的修复方向。下一步关键实验：把 Burns CCS / Marks linear-probe 在 SimpleQA contested subset 上跑一遍，量化 (iii) 跨 frontier × RLHF 量曲线——同样不需要新数据，只需现有 probe code + 现有 benchmark 重测。

更新 Open problems 第一条：\"缺 *epistemic grounding* 的标准评测\" 现在 *部分回答* — Kadavath / SelfAware / SimpleQA / R-Tuning 四条已构成 frontier-scale benchmark 雏形，但缺 internal-belief probe 与 output-confidence 双轨协议；剩余空白收紧为 \"probe-vs-readout 双轨 epistemic benchmark\"。

## 与其他 topic 的交叉引用

- `embodiment.md`：sensorimotor grounding 的 closed-loop 检验
- `causality.md`：referential grounding 是 Pearl 因果阶梯 L1 (observation) 的必要前置——如果 token 不指向稳定 referent，干预 do(X) 在 token 空间里就无意义
- `formal_limits.md`：grounding 与 TC⁰ 上界正交——增加 modality 不改变 depth，但改变 readout label space
- `world_model.md`：world model 需要 grounded token 作为状态变量；否则只是 textual rollout
- `online_learning.md`：RAG 被吹捧为权重外的知识更新通道，但 C-GROUND-6 (iv) parametric-prior dominance 把 plasticity 问题推迟而非消除——见 C-CONT-1 ripple-effect 暗线

---

*最后更新：2026-05-28 by NTP-Deepen cron tick (task type B) — 新增 §Epistemic grounding + C-GROUND-7；上 tick 新增 §Retrieval-augmented grounding + C-GROUND-6.*
