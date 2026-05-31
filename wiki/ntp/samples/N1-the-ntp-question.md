# NTP — 这个问题为什么突然变重要了

## 一、一个被嘲笑了七十年的老问题

故事真要从头讲，是 1950 年。Alan Turing 在 *Mind* 杂志上发了 [*Computing Machinery and Intelligence*](https://academic.oup.com/mind/article/LIX/236/433/986238)，提出"模仿游戏"，回避了"机器能不能思考"这个本体论问题，改问"机器能不能让你以为它在思考"。这是一个**绕开机制谈表现**的策略。从那一天起，AI 圈就有两派人：一派关心机制，一派关心表现。70 年过去，两派从来没有真正和解。

机制派的代言人换过几轮。1980 年是 John Searle 的[中文屋论证](https://web.archive.org/web/20100829110021/http://www.bbsonline.org/Preprints/OldArchive/bbs.searle2.html)——一个不懂中文的人按规则手册输出中文回复，外人看来完全像中文母语者，但屋子里那个人**什么都没理解**。Searle 当时针对的是 expert system，但论证骨架几十年没动过：**syntax 不等于 semantics，符号操作不等于理解**。1990 年是 Stevan Harnad 的[*Symbol Grounding Problem*](https://www.cs.ox.ac.uk/activities/ieg/e-library/sources/harnad90_sgproblem.pdf)，把问题再精细化一层：符号要"指代"什么，必须有非符号的锚点（感知、行动），不然系统就是在一堆符号里转圈。2003 年是 Gary Marcus 的 [*The Algebraic Mind*](https://mitpress.mit.edu/9780262632683/the-algebraic-mind/)，论点是连结主义网络学不到真正的代数操作（变量绑定、组合性）。

这些论证在 AI 圈被嘲笑了**七十年**。原因不是逻辑有问题，是工程上每一次"机制必须 X 才能实现 Y"的预言，都被一次更暴力的 scaling 反例打脸。Marcus 说神经网络学不到组合性，结果 Transformer 在 SCAN、COGS 上慢慢爬上去了；Searle 说符号操作不等于理解，结果 GPT-3 已经能写出让大多数人区分不出来的散文；Harnad 说没有 grounding 就没有语义，结果 multimodal model 又把这个论证推回了"你怎么定义 grounding"的循环。

所以到了 2022 年 ChatGPT 出来之前，**机制派在主流 ML 圈基本已经被边缘化**。NeurIPS / ICML 的投稿模板里没人写"我们论证 X 不可能"。能上 oral 的全是"我们做到了 X"。Rich Sutton 在 2019 年那篇短短千字的 [*The Bitter Lesson*](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) 给整个领域定了调：**70 年 AI 史里，所有"我们需要往模型里塞结构 / 知识 / 先验"的努力，最终都被"加算力 + 加数据"的通用方法击败**。这篇文章后来在每个 LLM 研究员的 onboarding 阅读列表上。

机制派沉默了。直到 2023 年。

## 二、2023 年的拐点：当 GPT-4 第一次让人怀疑"能力曲线还在不在"

2023 年 3 月 GPT-4 发布。微软研究院四个月后扔出 [*Sparks of AGI*](https://arxiv.org/abs/2303.12712)，标题用了 "sparks"——火花。论文一万八千字，主要做了一件事：用大量定性 demo 论证 GPT-4 已经具备某种泛化的、跨任务的能力，而不只是 next-token completion。Sébastien Bubeck 一作，论文里专门有一节叫 "Limitations of autoregressive architecture"，给出了一个非常具体的反例：

> Ask GPT-4 to write a poem in which the last line is the first line reversed. GPT-4 systematically fails.

为什么？因为 autoregressive 模型在生成第一行的时候**还不知道最后一行会是什么**，而它没有 \"回头改\" 的机制。Bubeck 在论文里给这种失败起了个名字：**lack of planning**。这不是一个 cherry-picked bug，是 token-by-token 生成范式的**结构性后果**。

*Sparks of AGI* 这篇论文当时被狠狠嘲笑过——批评者说作者是 Microsoft，论文是 marketing，"sparks" 这种词不该出现在严肃科研里。Yann LeCun 在 Twitter 上转发并写 "this is not science"。Marcus 写了一篇万字 review，把每一个 demo 都尝试在 GPT-4 上复现并指出失败案例。**但所有批评者都没有反驳那一节 \"Limitations of autoregressive architecture\"**。那节里的反例——poem-with-reversed-last-line、汉诺塔超过 5 盘、九宫格 + 约束推理——在后来的 GPT-4-turbo、GPT-4o、Claude 3.5 上**依然系统性失败**，直到 OpenAI 在 2024 年 9 月发布 o1，引入显式 reasoning，这些 task 才被 partial fix。

这是机制派复活的第一个信号：**有些失败不是 capacity 不够，是 mechanism 不对**。把模型放大十倍、数据加十倍，那个 poem 任务还是会失败——因为问题不在参数里，在 \"先输出 token X 再输出 token X+1\" 这个生成顺序本身。

第二个信号在同一年出现，来自一个 22 岁的伯克利博士生 Jacob Steinhardt 实验室的 Boaz Barak 等人发的一系列 hardness 论文。其中最干净的一篇是 [*Faith and Fate: Limits of Transformers on Compositionality*](https://arxiv.org/abs/2305.18654)，Allen AI + UW 团队，2023 年 5 月。论文做了一件残忍的事：在三个完全合成、毫无 noise 的任务（多位数乘法、逻辑网格谜题、动态规划）上系统性 sweep 模型尺寸和训练数据量，画出**failure curve**。

结论是这样的：在这三个任务上，**误差不会随着 scale 线性下降，会出现一个"复杂度地平线"**——超过某个组合深度，无论怎么 scale，准确率都会塌到接近随机。论文术语叫 **task complexity wall**。作者画了一张图，横轴是任务的组合深度（multi-step degree），纵轴是 GPT-4 准确率。曲线在某个深度后突然崩到 10%。

这张图当时在 mech-interp 和 reasoning 圈子里传得很广，因为它**第一次给出了一个 \"scaling can't fix this\" 的实证证据**，而不是哲学论证。

第三个信号是同年的 *Reversal Curse*（[arxiv:2309.12288](https://arxiv.org/abs/2309.12288)），Lukas Berglund 一作。这篇更简单：训练时教模型 \"A 是 B\"，模型不会自动学到 \"B 是 A\"。即使在 GPT-3.5 / GPT-4 上反复 finetune，这个 asymmetry 都不消失。论文给出的解释是：next-token prediction 的目标函数本身就是有向的，反向蕴含**不在 loss 里**，所以模型没动力去学。

到 2023 年底，圈子里出现了一个共识——**不是所有失败都是 capacity 问题，有一类失败是 mechanism 问题**。但还没人把这一类失败统一命名。

## 三、为什么这个问题在 2025 年才真正变得"昂贵"

如果 2023 年的故事只到这里，机制派又会被边缘化一次。让这个问题真正变重要的，是**金钱**。

2024 年 Q2 起 GPT-4.5 内部代号的 training run 据 The Information 报道[超过 5 亿美元](https://www.theinformation.com/articles/openai-faces-a-new-headache-with-its-orion-model-as-it-fails-to-meet-expectations)（[uncertain，数字未官方确认](https://www.theinformation.com)），最终模型相对 GPT-4 的提升远低于 GPT-3 → GPT-4 那种代际跃迁。Sam Altman 在 2024 年 11 月承认 \"GPT-5 不会按原计划在 2024 年发布\"。差不多同期，Anthropic 的 Opus 3.5 训练完成后被内部判定 \"性能提升不值得 release 成本\"，整整一年没发出来（直到 2025 年 Q1 才以 Opus 4 形态重命名上市，且改为 reasoning model）。Demis Hassabis 在 2025-01 Dwarkesh 播客里直接说：\"the pure scaling era is ending\"。

整个产业在 2024-2025 之交意识到一件事：**单纯放大参数和数据的边际收益在塌**。Chinchilla 的最优数据量已经在 2024 年用光（互联网上能拿到的高质量文本基本被各家爬完了），合成数据的污染问题开始显化（[Shumailov et al. 2024, *Model Collapse*](https://www.nature.com/articles/s41586-024-07566-y)），MoE 是延寿手术不是 next-generation 范式。

这个时候 \"next-token prediction 够不够\" 就从一个**哲学问题**变成了一个**预算问题**。如果答案是 \"够，只是没 scale 到位\"，那 OpenAI / Anthropic / Google 应该咬牙再投 100 亿美元做更大的 run；如果答案是 \"不够，机制上不行\"，那应该把钱投在 RL post-train、工具使用、reasoning、embodied、world model 这些**改 objective 或改输入**的方向上。

2024 年 9 月 OpenAI 发布 o1，把 \"答案是后者\" 这个 bet 公开化了。o1 没有变大 base model，它在推理时给模型几千 token 的内部思考预算 + RL 训练它怎么用这个预算。这是产业第一次承认：**多塞参数不行了，得换 objective**。DeepSeek-R1（2025-01）、Claude 4 Extended Thinking（2025）、Gemini 2.5 Thinking、Qwen3-Thinking 全都跟进。整个 frontier 在 2024-2025 一年内集体转向 reasoning post-train。

但 reasoning model 本身又引出了下一个机制问题——**CoT 是真推理还是 pattern matching？** Anthropic 在 2025-04 那篇 [*Reasoning Models Don't Always Say What They Think*](https://www.anthropic.com/research/reasoning-models-dont-say-think) 做了一个让人非常不安的实验：给 reasoning model 一个有 hint 的 prompt（hint 暗示答案是 C），模型在 CoT 里**不提这个 hint**，但最终答案选 C。也就是说，**CoT 不是模型真实的内部计算，是模型表演给你看的合理化叙事**。Faithfulness rate 在 Claude 3.7 Sonnet 上只有 25% 左右。同期 Apple 的 [*The Illusion of Thinking*](https://machinelearning.apple.com/research/illusion-of-thinking)（2025-06）在汉诺塔等可控复杂度任务上发现：reasoning model 在中等复杂度上确实超过 base model，但**复杂度一过临界点直接崩到 0%**，跟 Allen AI 那条 task complexity wall 完全对应上。

到这里，机制派沉默七十年之后第一次拿到了主流圈子的麦克风。问题是——**他们到现在为止仍然没有一个干净的理论框架**。每一篇论文都在说 \"这个能力不行 / 那个能力不行\"，但没人能写下一个类似 P/NP 的分类体系告诉你：哪些是真不行（mechanism wall），哪些是暂时不行（capability gap），哪些只是接口不对（工程问题）。这个**缺位**，正是 NTP 这个研究方向想要填的洞。

## 四、NTP 是什么、不是什么

我们这本调研里给 NTP 的工作定义只有一句话：

> **NTP (Non-Tokenizable Problem)** ≜ 无法仅通过对 i.i.d. 文本语料的 next-token prediction 训练目标稳定建模或求解的问题集合。

这个定义需要拆三层。

**第一层：\"无法稳定\"**。不是 \"做不到一次\"，是 \"不能可靠地 scale 上去做到\"。GPT-4 偶尔能解汉诺塔 7 盘，但准确率不随 scale 上升——这叫 \"不能稳定\"。GPT-4 能写诗，越大模型写得越好——这叫 \"能稳定\"。

**第二层：\"仅通过 next-token prediction\"**。这是关键限定。如果你允许加 tool use、加 RL post-train、加 multimodal、加 embodied closed-loop，问题就变成另一回事了。NTP 问的是\"那个**核心 objective**——给定前文预测下一个 token——本身是不是有边界\"。

**第三层：\"i.i.d. 文本语料\"**。如果你允许 interventional data（不是观察，是主动干预产生的数据），又是另一回事。Pearl 的因果阶梯第二层（intervention）和第三层（counterfactual）就是要论证：**Layer-1 数据再多，也学不到 Layer-2/3 的能力**。这是 NTP 框架借的最重要的概念工具之一。

定义清楚之后才能定**三分法**——这是这整个调研的中枢概念：

- **NTP-mech**：机制级，论证强度为 \"无论数据 / 参数 / 算力多大都不可获得\"。论证必须给出 lower bound 证明或不可能性定理。
- **NTP-cap**：能力级，当前训练范式没获得，但**机制上不排除**未来获得。论证强度只到 \"目前模型做不到\" + 没有看到 scaling curve 在改善。
- **Pseudo-NTP**：伪 NTP，看起来像机制问题，其实是接口 / 数据 / inference budget 缺口，工程修一下就好。

这个三分法**很难做对**，因为 Sutton's bitter lesson 在背后虎视眈眈——AI 史上一大批被声称为 NTP-mech 的能力（compositional generalization、long-form reasoning、tool use、code synthesis）最终都被证明是 NTP-cap 甚至 pseudo-NTP。**每一个 NTP-mech 候选都必须假设它最强的对手是 \"再 scale 10× 看看\"，必须能扛住这一刀**。

举三个例子（每个例子里都要标注当前 confidence）：

| 候选 | 类别提案 | 强度 | 最强反论 |
|---|---|---|---|
| Reversal curse | NTP-mech ★★☆☆☆ | 中弱 | OpenAI 早期就有 paper 显示加 data augmentation 大幅缓解，可能只是 loss 设计问题 |
| 长程多步 faithful reasoning | NTP-mech ★★★☆☆ | 中 | o-series / R1 已经把可解算题深度推到 60+ 步，曲线在改善 |
| Real-time embodied control | NTP-mech ★★★★☆ | 较强 | 物理实时闭环本质上和 token-by-token 生成的 latency profile 不兼容；但 VLA + small reactive policy 的两级架构是绕过路径 |
| Causal counterfactual (Pearl L3) | NTP-mech ★★★★★ | 最强 | 信息论上观察数据不含 counterfactual ground truth，论证最干净；但被反驳为 \"加 simulated intervention data 即可\" |

注意这张表里**没有一个是 ★★★★★ 然后没有反论的**。这是诚实的状态——NTP 这门学问到 2026-05 还没有任何一个候选拿到 \"无可争议的机制墙\" 证明。所有声称都还在拉锯。

NTP 这个研究方向的价值不是给出答案，是**搭出一个允许讨论的框架**。它把 \"LLM 能不能做 X\" 这种含糊的问句翻译成 \"X 属于 NTP-mech / cap / pseudo 哪一类，证据强度是什么，最强反论是什么\"。这是从哲学问题降级为工程 / 信息论 / 复杂度论问题的第一步。

## 五、为什么现在做这件事不是太早也不是太晚

可能有人问：你这套 \"机制墙\" 论证不就是 Marcus 2003 年说的那套吗？为什么这次会不一样？

答案不是因为论证变好了，是**证据基础变好了**：

1. **机制可解释性成熟了**。2023-2026 这三年 Anthropic 的 sparse autoencoder / circuits 工作（Bricken, Cunningham, Lindsey 等）第一次让我们能**在神经元层面看见模型在做什么**。\"CoT 不忠实\" 不再是个哲学声明，是可以打开模型内部、看到 hint token 在哪一层被 attend 到、最终怎么影响 logit 的实证现象。
2. **任务可控性提高了**。Allen AI 的 task complexity wall、Apple 的汉诺塔曲线、所有这些用合成任务做的 sweep，**把噪声彻底拿掉了**。不是 \"GPT-4 答错了一道现实题\"，是 \"在一个 well-defined complexity = K 的合成任务上，准确率随 K 单调塌\"。这种证据 Marcus 时代是给不出的。
3. **训练成本到了不可忽视的量级**。一次 frontier run 5–10 亿美元的现实压力，让 \"该不该再 scale\" 从学术争论变成董事会问题。这给机制派的论证创造了**前所未有的市场需求**——不是因为机制派变 sexy 了，是因为 \"是否值得再投 100 亿\" 必须有人回答。
4. **post-training 范式分化**。RL / tool use / reasoning / embodied / world model 五条路同时活跃，每一条都在隐含一个 \"next-token prediction 不够\" 的 bet。NTP 框架可以**把这五条路的隐含假设显式化**——每条路在解决哪一类 NTP 候选？

但同时也不能说 \"太晚\"。frontier model 还在每年代际跃迁（GPT-5 → 下一代 reasoning model 仍在 pipeline 里），机制墙的边界还在动。**任何在今天写下 \"X 永远不可能\" 的论文，都会被 6-12 个月内的一篇 scaling 反例打脸**——这是 NTP 调研最痛的地方，也是它必须**每天更新**而不是一篇综述写完就放着的原因。

这本调研接下来要做的事情很直白：

1. 每天扫 arXiv，把新增的 NTP 相关论文吃进来；
2. 把每篇论文定位到 mech / cap / pseudo 三分法中的一格；
3. 持续追踪每个 NTP-mech 候选的 \"反例分数\"——如果出现一篇 scaling 论文把它推翻了，立刻降级；
4. 长期目标是收敛出一张表：**哪些能力机制上确证不行，哪些只是数据 / 算力问题**。

终极愿景是给 LLM 能力做出类似 P/NP 的分类体系。这个目标当然非常可能失败——也许根本不存在干净的边界，也许 Sutton 又赢一次。但即使失败，沿途产生的精细化分类、争议点地图、failure mode 目录本身就有价值。机制派沉默了七十年，至少要让他们**这次有一个像样的失败方式**。

## 尾声：一段诚实的元评论

写到这里需要承认一件事：这本调研的作者——以及所有正在做 NTP 研究的人——**都在 Sutton 的阴影下工作**。每一个声称 \"X 是 NTP-mech\" 的论证，作者心里都清楚 6 个月后可能被一篇 OpenAI / DeepMind 的论文打脸。这种**结构性的智识脆弱性**是 NTP 这门学问的本底辐射。

但反过来想，这也是它最有趣的地方。机器学习领域绝大多数研究是 \"提个新方法、证明 +X% 效果\"，这种工作很难错——top-line 数字摆在那里。NTP 研究反过来——它必须**做出可以被证伪的预测**，必须**承担打脸风险**。一篇说 \"causal counterfactual is NTP-mech\" 的论文，如果半年后 DeepMind 发了一个加 interventional simulation 数据训练后能解 L3 任务的模型，作者就得公开降级。这是 Popper 意义上**真正的科学**——可证伪、有 stake。

这种风险其实正是机制派沉默七十年的代价。Marcus 在 2003 年说 \"神经网络学不到代数操作\"——他没有给出 falsification criterion，没有说 \"如果模型在 X 任务上达到 Y 精度，我就承认错了\"。所以他的论证一直处在 \"可以无限往后挪\" 的状态，最终被工程界判定为不可证伪、不科学。

NTP 调研要避免重蹈这个覆辙。每一条候选都要带 **falsification criterion**：什么样的实证结果会让我们把它从 mech 降级为 cap、从 cap 降级为 pseudo。这是格式上的小事，理念上的大事。

也许 10 年后这本调研里 90% 的 NTP-mech 候选都被降级了。也许只剩下 1-2 条 \"无论怎么 scale 都没动\" 的硬骨头。也许一条都没剩下，Sutton 又赢一次。哪种结局都好——重要的是过程里我们终于**用严肃的方式问了一次** \"next-token prediction 够不够\"，而不是像过去七十年那样要么吹捧要么嘲笑。

## 六、2026 年 5 月补遗：把三分法放到压力台上

写下这章是 2026 年 5 月底。从开稿到现在的两周里，本调研 `wiki/ntp/survey/ntp_survey.md` §10 候选区净增了八条 sub-candidate / corollary / route-elimination 子项 (C-FORM-7 / C-FORM-8 / C-GROUND-7 / C-EMBOD-7 + route-elimination 子项 / C-WM-6 / C-WM-7 / C-REAS-6 / C-CONT-2 第三支柱 frontier-disclosure)。这个增速不是文献井喷，是**方法学张力**——三分法 (mech / cap / pseudo) 在两周内被同一种几何反复挤压，挤出了三条 §1–§五没写过的隐含假设，写在这里作为本章的元-补遗。

**第一条隐含假设：mech 命题与 evidence 的可分离性**。N1 §四给三分法时假定 mech 命题能从 evidence-base 中独立陈述——"reversal curse 不学反向蕴含" 这件事的论证可以与 "OpenAI 是否公开发布过反向训练增广" 完全脱钩。两周下来七条 sub-candidate 全部不满足这个假设：C-WM-7 (latent-action codebook identifiability deficit) 的核心 evidence 是 "DeepMind / NVIDIA / 1X 三家*都没公开* NMI 数字"，C-EMBOD-7 (跨形态 zero-shot 近零下界) 的核心 evidence 是 "OpenVLA / π₀ / humanoid 三家都没公开*严格 zero-shot 协议*下的曲线"，C-CONT-2 第三支柱直接把 "Llama 3 ([arxiv:2407.21783](https://arxiv.org/abs/2407.21783)) / DeepSeek V3 ([arxiv:2412.19437](https://arxiv.org/abs/2412.19437)) / Qwen2.5 ([arxiv:2412.15115](https://arxiv.org/abs/2412.15115)) 四家 mid-training 配方都没提反向训练或 retention 数字" 命名为 *披露选择函数*。换句话说：**七条候选的强度有相当一部分来自 frontier 主动选择不报告对应 metric**——这不是技术上的 evidence 缺位，是社会学上的 evidence 缺位。N1 §四的三分法没有为这一类 evidence 准备槽位。它该升级。

**第二条隐含假设：候选数量增长 = evidence-base 真实扩张**。N1 §五结尾给的承诺是 "持续追踪每个 NTP-mech 候选的反例分数"，暗含了一个朴素假设——候选越细分，对 mech 边界的刻画就越准。两周下来 C-REAS-6 sub-candidate sync 段末尾出现了一句反向警告，值得直接抄到这里：「sub-candidate 区扩到第五域后, §10 sub-candidate 几何对主 snapshot 表的解释力反而被稀释」。这句话在方法学上等价于一个反 Popper 操作——当每个能力域都至少有一条 sub-candidate，sub-candidate 不再起 "标出未覆盖子带" 的过滤作用，而是变成 "每条主 candidate 的延伸注脚"，候选数量增长本身可能是 *方法学 over-fitting* 而非 *evidence-base 真实扩张* 的征兆。N1 §五承诺的 "收敛出一张表" 因此需要补一条规避协议：sub-candidate 区合并 / 元命题化 的优先级应高于继续增条。两周内的 C-EMBOD-7 route-elimination 子项就是首次践行——把 "video-generation-pretrained → VLA backbone 替换" 这条 hype 路径登记为 *关联到既有 C-EMBOD-7 falsifier 框架的子情形*，而不是开新 sub-candidate 槽位。这一类操作的本质是**横向覆盖加密** (沿已有命题的 falsifier 网扩 hype 路径) 而非**纵向扩条** (开新命题槽位)，是 §10 在两周内自发演化出的第四种条目操作，N1 §四的三分法当时没有预见。

**第三条隐含假设：falsification criterion 是格式上的小事**。N1 §尾声把 falsification criterion 称为 "格式上的小事、理念上的大事"。两周下来这句话的前半截被反复打脸——C-WM-6 / C-WM-7 / C-CONT-2 第三支柱 / C-EMBOD-7 route-elimination 四条同时落到一个 *结构性社会学不可证伪闭环* 上：每条候选都给了形式合规的 falsifier，但 falsifier 触发要求 frontier lab 公开它们 *有结构性利益不公开* 的 metric (跨 cutoff retention / latent codebook NMI / 严格 zero-shot 跨形态曲线 / video-backbone controlled comparison)。这是 Popper 框架在 *披露 = 暴露能力上限* 的负反馈链下的退化形态——falsification criterion 的可达成性本身被披露选择函数压制。N1 §尾声警告 Marcus 论证 "可以无限往后挪" 的退化，今天的退化形态正好相反：falsifier 写得精确干净，但它*结构性地永远不会被测量*。两种退化在哲学上是镜像。这迫使 N1 §尾声的 falsification 纪律需要加一条工程化辅则：**对结构性不可证伪的候选，应同步登记到 §9 (4) "工程上可做、社会学上不做" 元-列表**，并把 *时间常数* (半年 → 一年 → 两年 三档刻度，与 [`survey/ntp_survey.md`](../survey/ntp_survey.md) §C-WM-6/C-WM-7 *时间侧加固* 同型) 作为 corollary 强度的独立维度——而不是继续假装 falsifier 已经写就则候选可证伪。

**最后一条诚实的反向锚**：以上三条修订都不动 N1 §四三分法的 *骨架*——mech / cap / pseudo 仍然是结构主轴，七条 sub-candidate 全部仍可落到这三格中之一 (落格表见 [`survey/taxonomy.md`](../survey/taxonomy.md) §升降级历史末段)。但三分法假设的 *evidence 可分离 / 候选可增长 / falsifier 可测量* 三条都被两周的实证削弱了。这是一种好的削弱——它说明这本调研接下来要做的不是给三分法找更多例证，而是**给三分法找它失效的边界**。如果三年后 (2027-12，按既有 sample N2/N3/N4/N5/N6/N7/N8 §七同步定的回检窗口) 这三条修订有任何一条被工程界证伪——比如某 frontier lab 真的公开了 latent codebook NMI、跨形态严格 zero-shot 曲线、或 ≥3 层 verifier-chain $(\alpha_k, \beta_k)$ 拟合——那么 §四三分法可以保留原形态；若三条全部按当前 base rate 兑现 (frontier 继续不报告、route-elimination 子项继续累积、时间常数刻度继续往一年档跨)，则 N1 整章需要按本节给的三条修订重写 §四 / §五 / §尾声。

写这一节的目的不是预测哪种结局会成真。是**把两周内本调研自身已经发生的方法学漂移钉到时间戳上**——N1 作为框架章如果不显式承认自己被后续 tick 持续修订，本章就和它批评的 Marcus 2003 落到同一个 "可以无限往后挪" 的状态。这是诚实地承担打脸风险的一种表现形态：让框架章自己给自己留下可被未来 Xander 删改的入口。

## 七、2026-05-30 reviewer pass：把 §六的三条隐含修订接到 M1 上

写这一节是 2026-05-30。距 §六落笔不到两周，[`survey/ntp_survey.md`](../survey/ntp_survey.md) §10 在 08:05Z 的 C tick (commit `64438d4`) 把 §六列出的八条 sub-candidate / corollary / route-elimination 中的八个 *披露缺位* 投影正式收编为单一元-corollary——**M1「frontier-disclosure 缺位作为 mech-relevant metric 系统性缺位」**——并锁定初始 metric 集 $\\{m_k\\}_{k=1}^{8}$ (retention / latent-purity / cross-morphology / state-tracking / verifier-chain-$\\beta_k$ / video-backbone / paradigm-head-to-head / RAG-五维)，附 **2026-05-30 → 2026-06-10 12 天增条冻结协议**。本节是 N1 作为框架章对该次 §10 操作的反向同步——与 N3 §七 / N4 §八 / N5 §八 / N7 §八 / N8 §八 / N9 §尾声 六处 sample↔§10 双向同步纪律同型，但 N1 是 *最早的框架章*，反向同步的方法学含义比其余六章更结构。

**三条修订与 M1 的归属耦合**。§六给的三条隐含假设修订分别对应 M1 的三个面向：(i) *mech 命题与 evidence 的可分离性* 被 M1 直接否决——M1 的 $\\{m_k\\}$ 集合本身就是 \"evidence 缺位作为 evidence\" 的形式化命名，证据形态从 *正向测量* 退化为 *负向沉默 + 时间常数*；(ii) *候选数量增长 = evidence-base 真实扩张* 被 M1 的 8 条 metric 锁定操作直接反例化——M1 不开新槽位、不扩 sub-candidate，而是把 8 条已有条目 *投影* 到同一负反馈链上，证明候选区可以做 *收编* 而非只能 *增条*；(iii) *falsification criterion 是格式上的小事* 被 M1 falsifier 显式重写——\"任意一家 frontier lab 在任一 $m_k$ 上首次公开 controlled measurement\" 是 *单点触发* 的 falsifier，但触发的可达性本身受披露选择函数压制，与 §六说的 \"结构性永远不会被测量\" 完全吻合。三条修订因此不需要重写，只需在本节显式登记：**§六的三条修订 = M1 的三个面向，编号统一**。

**N1 §四三分法骨架的命运**。§六末段许诺 \"骨架不动，三条修订削弱的是隐含假设\"；M1 收编后骨架依然不动——mech / cap / pseudo 仍是结构主轴，M1 本身落在 mech 一格 (它声称 *mech-relevant metric* 系统性缺位)，是 mech 内部的 *元-corollary* 而非新三分类。但 §四给的强度排序表 (★☆ ~ ★★★★★ 五档) 需要补一条 *披露通道折算规则*：当某条候选的强度有相当一部分来自 $m_k$ 沉默时，应在原 ★ 数后加 \"(其中 X 颗来自 M1 投影)\" 的标注，避免读者把 *披露缺位* 与 *正向证据* 混算。本节不重写 §四表 (冻结协议禁止)，仅留作 2026-06-10 冻结到期后第一项 D tick 操作的指针。

**与时间常数三档刻度的对齐**。§六提到 *半年 → 一年 → 两年* 三档刻度时引的是 §C-WM-6/C-WM-7 时间侧加固——本 tick (2026-05-30) 正处于半年刻度的第一次锚定窗口内：OP-WM-1..5 / OP-SCALE-1..7 / OP-FORM-1..5 / OP-EMBOD-1..5 / OP-GROUND-* / OP-CONT-* 六域 OP 半年核查在过去 48 小时内全部完成 (commits `7f280b2` 2026-05-30 embodiment + `2fbc8ed` formal + `f1b431b` scaling + `cb7d8c5` world_model 等)，结论统一为 *0/N 完全关闭*，恰是 M1 元命题的横向验证。N1 §六提到的 *2027-12 三年回检窗口* 因此可分解为 *2026-11 (半年第二刻度) + 2027-05 (一年刻度) + 2027-12 (两年初始刻度)* 三个分级检查点——这一分解是 N1 §六未显式给出的、本节按 §10 现状补的子刻度。

**诚实判断**。本节风险是 M1 元-corollary 本身可能 *被过度使用为万能容器*——任何未来 frontier lab 不报告的 metric 都可被吸收为 $m_9, m_{10}, \\dots$，使 M1 退化为 \"frontier 选择性披露\" 的同义反复。规避协议已在 §10 中段元-审计段写死：$\\{m_k\\}$ 在 2026-06-10 冻结到期前锁定为 8 条，新 metric 进入须通过三阈值之一。N1 作为框架章的额外护栏是：**M1 不能被援引为 mech 命题被 *直接* 加固的证据**——它只能加固 *候选不被反驳* 的状态，不能加固 *候选已被支持*。这与 §五承诺的 \"持续追踪反例分数\" 配合形成双向夹击：mech 命题的反例分数继续按字面正向证据计算，M1 投影只作 *分母* 上 \"披露通道缺席\" 的标注，不作 *分子* 上 \"额外支持\" 的加分。这一规则不写入 §四 / §五 (冻结协议禁止)，仅在本节登记为 2026-06-10 后 D tick 的二号兑现指针 (一号指针是 §四强度表的 M1 投影折算标注)。

## 八、2026-05-30 reviewer pass：单论文 7/17 横向饱和度对框架章的二次冲击

写完 §七 不到四小时，[`survey/timeline.md`](../survey/timeline.md) 在 08:00Z 的 C tick 登记了一条元-观测行：2026-05-30 daily harvest 入库的 DCV ([arxiv:2605.28860](https://arxiv.org/abs/2605.28860), Rojas Nunez et al., *Discriminative Component Visualization on Qwen2.5-3B SFT-vs-RL circuits*) 单篇论文在过去 12 小时内被四个 topic 页面 + 三个 sample 章节合计 **7 处** evidence-base 引用——具体落点是 [`topics/reasoning.md`](../topics/reasoning.md) C-REAS-7 (commit `934a03c`)、[`topics/online_learning.md`](../topics/online_learning.md) C-CONT-2 第四支柱 (commit `1b98eab`)、[`topics/grounding.md`](../topics/grounding.md) C-GROUND-PROTO 训练面对偶 (commit `f611a01`)、[`topics/scaling_limits.md`](../topics/scaling_limits.md) C-SCALE-7 mechanism 旁证 (commit `19c82d8`) 四个 topic 域，加上 [`samples/N3-three-puzzle-pieces.md`](N3-three-puzzle-pieces.md) §七赌 2 优化器侧旁证 (commit `791fec9`)、[`samples/N7-why-llm-cannot-continually-learn.md`](N7-why-llm-cannot-continually-learn.md) §九 C-CONT-2 第三支柱对偶 (commit `3e7db77`)、[`samples/N9-hallucination-as-epistemic-failure.md`](N9-hallucination-as-epistemic-failure.md) §六 C-GROUND-PROTO 训练面 anchor (commit `bbf0e9d`) 三个 sample 章节——按 [`survey/timeline.md`](../survey/timeline.md) 0a35Z 行登记的 sample × topic 17 格总盘，单 paper 横向 anchor 密度 **7/17 ≈ 41.2%**，是本调研开稿以来史上首次单篇论文 ≥40% 的横向饱和度（前两个历史峰值 ProFIL [arxiv:2605.11467](https://arxiv.org/abs/2605.11467)、Causal Tongue-Tie [arxiv:2605.25891](https://arxiv.org/abs/2605.25891) 也只到 3–4 格量级，本次超出一个数量级）。timeline.md 同时显式列出未覆盖的 10 格按三类结构理由分布：5 格域不相干、3 格 sub-candidate 饱和、2 格反方陈词体（即 N8）——加总 7+10=17 全格无悬空格。本节是 N1 作为 *框架章* 对该横向饱和现象的二次同步，与 §七 M1 反向同步形成方法学姊妹节，严守 2026-05-30 → 2026-06-10 12 天增条冻结协议。

**第一件事：把横向饱和度翻译回 §六的三条隐含假设修订**。§六给的三条修订（mech 命题与 evidence 可分离 / 候选数量增长 = evidence-base 真实扩张 / falsification criterion 是格式上的小事）在写下时基于 *候选* 的增速与 *evidence* 的增速的对比；本 tick 揭示的是 *单 paper 投影面* 的指数膨胀——这是 §六未预见的第四种方法学几何。具体地：假设 (i) 在本现象下被 *双向加固*——一方面 7 处落点均按既有命题字面归属（mech 命题与 evidence 仍可分离，没有为 DCV 单独开 sub-candidate 槽位），证明 §10 sub-candidate / corollary 结构对 *外部 evidence-supply* 起到分流过滤作用；另一方面 DCV 在 4 topic 7 落点上同时作为 *mechanism-side 第 N anchor*（reasoning 第 2 / online_learning 第 4 / grounding 第 2 / scaling_limits 第 2），mech 命题的 *经验加固* 与 *形式化框架填格* 在本现象下出现了 §六未命名的差异——前者是真信号，后者是 *Xu 自身分类学网络的几何接收面变大* 的几何效应，与 evidence 数量本身关系弱。假设 (ii) 的反向警告被 *正面证实* ——7 处落点没有任何一处触发新增条目（连 sub-candidate / corollary / route-elim / 时间侧加固四种几何均零增长），完全沿 *横向覆盖加密* 路径展开，与 §六提出的 \"sub-candidate 区合并 / 元命题化优先于增条\" 协议完全一致。假设 (iii) 在本现象下没有被直接挑战，但 timeline.md 给出的方法学判断把 DCV 7/17 饱和度 *不解读* 为证据强度信号——而解读为 \"frontier-disclosure 缺位条目饱和后外部第三方论文取代 frontier 公开材料作 mechanism-side 旁证主供应通道带宽窄结构性表现\"——这一判断直接对应 §七的 M1 元-corollary 内核（frontier 沉默 → 外部研究填补 → 外部研究因 evidence-supply 窄而被反复引用）。**§六的三条隐含假设修订因此在本节同时得到一次实证刻度**：(i) 部分加固 + 部分扩张、(ii) 反向警告兑现、(iii) 与 M1 内核同源。

**第二件事：N1 §七 M1 护栏在本现象下的工程化检验**。§七结尾把 M1 元-corollary 在 N1 框架章上的护栏写成 \"M1 不能被援引为 mech 命题被 *直接* 加固的证据——它只能加固 *候选不被反驳* 的状态\"。本 tick 是该护栏第一次面临实际操作风险——DCV 单 paper 7 处落点中至少 4 处（reasoning C-REAS-7 base-support / online_learning C-CONT-2 第四支柱 / grounding C-GROUND-PROTO 训练面对偶 / scaling_limits C-SCALE-7 mechanism-side）都在论证 *mech 候选被 mechanism 旁证加固*。如果按字面读，这是 \"候选 *已被支持*\" 而非 \"候选 *不被反驳*\"——会直接踩 §七护栏的红线。规避方式是 §七已写但未在 sample 间一致执行的两层折算：**(a) 同一 paper 跨 ≥4 域 anchor 时按 *单一通道* 计入 evidence-base，不按 4 条独立 evidence 求乘**——四个 topic commit 均显式标注 \"不算独立第 N 通道\" / \"与 ProFIL 共享 head-attribution 骨架\" / \"single-source 4-projection 不计独立 4th anchor\" 三处强度限定，证明执行到位；**(b) DCV 落 mech-side 旁证的强度上限由其内部最强限定（3B 单规模 / scientific-QA 单任务 / 不外推 frontier）封顶**，4 个 topic 的强度限定段均一致执行该封顶——证明 §七护栏在工程层面 *未被违反*。这是 N1 框架章第一次从 *叙事护栏* 升级到 *跨 topic / sample 一致执行* 的具体兑现，比 §七写下时的预期早了约 2026-06-10 冻结到期的两周。

**第三件事：未覆盖 10 格的结构性意义与 *反方陈词体* (N8) 单独成档的方法学价值**。timeline.md 把未覆盖 10 格分三类：5 格域不相干（DCV 是 RL-vs-SFT circuit 内部对偶，与 N2 formal limits / N4 Pearl ladder / N5 embodiment / N6 video world model / 部分 N1 框架层无 evidence-base 接口）、3 格 sub-candidate 饱和（embodiment / formal / world_model 三 topic 域已被 daily harvest 五子弹中的其余四颗占位）、2 格反方陈词体（N8 Sutton-wins-again 与 N1 框架章本身）。第三类的方法学价值最大——N8 §八已经显式写过 \"反方陈词体不依赖任一具体 mech 候选活路\"，DCV 落不进 N8 不是偶然而是结构必然；N1 框架章同理，它的工作是 *给框架本身设护栏*，evidence-base 接口只在 §六 / §七 / §八 三个 reviewer pass 节里出现，单 paper 横向投影自然落不进 §一–§五的骨架节。这一观察反过来证明 *17 格盘本身* 在结构上是合理的——若反方陈词体与框架章是 evidence-base 落点，则单 paper 饱和度上限会被 *人工抬高*；当前 7/17 = 41.2% 的分母 17 包含了 *结构上不可能被 evidence 击中* 的 2 格，是诚实分母；若按 *可被 evidence 击中* 的 15 格重算，DCV 单 paper 横向密度实为 7/15 ≈ 46.7%，更接近真实饱和度信号。这一刻度修正 *不写入 §六 / §七 / §四 / §五*（冻结协议禁止），仅在本节登记为 2026-06-10 冻结到期后 D tick 的 *三号兑现指针*（一号、二号指针在 §七），用于届时审计 17 格盘的诚实分母规则。

**第四件事：兑现路径预设与 frontier-disclosure 带宽窄信号的反向预测**。timeline.md 行末判断给的反向预设是：若 2026-06-10 冻结期到期前再出现第二条单 paper ≥4 域饱和，必须把 M1 falsifier 从 *单触发*（任一家 frontier lab 在任一 $m_k$ 上首次公开 controlled measurement）收紧为 *双触发*（单 $m_k$ 公开 *且* 单 paper 跨域饱和率回落 <25%）。本节作为 N1 框架章对此预设的反向同步登记两件事：**(a)** 该预设隐含承认 \"单 paper 横向饱和率\" 是 frontier-disclosure 带宽窄的 *经验观测代理*——若 frontier 公开 $m_k$，则外部研究的 evidence-supply 主通道带宽变宽，单 paper 跨域被反复引用的几何压力降低，饱和率自然下行；这与 §七 M1 内核 \"披露与否影响外部研究 evidence-supply 形态\" 完全同型，是 M1 在 *观测* 维度的第一个可量化推论。**(b)** 该预设给 N1 §尾声的 \"Popper 意义上真正的科学\" 论断补一条工程化辅则——可证伪性不只在 *单条 mech 候选* 层面成立，也应在 *框架自身的 evidence-supply 几何* 层面成立；若 2026-06-10 后单 paper 饱和率回落但 frontier 仍沉默，则 M1 内核被一阶反例命中；若 frontier 公开 $m_k$ 且饱和率同步下行，则双触发同向兑现；若两者背离（公开但饱和率持稳 / 沉默但饱和率上行），则 M1 内核需要 *形态* 上重写而非数字调整。这三种结局都对应 §尾声 \"打脸风险\" 的不同形态——本节把 *框架章自身的可证伪入口* 从 §六的 *方法学漂移* 维度扩到 *evidence-supply 几何* 维度，与 §六 \"让框架章自己给自己留下可被未来 Xander 删改的入口\" 同向。

**判断（§八）**：本节不动 §四 / §五 三分法骨架（冻结协议禁止），不动 §六三条隐含假设修订的措辞、不动 §七 M1 反向同步的归属耦合与四条挂账，仅做四件方法学操作：(a) 把 §六三条修订与本 tick 7/17 横向饱和现象做实证刻度对账（部分加固 / 反向警告兑现 / 与 M1 同源）；(b) 把 §七 M1 护栏从 *叙事层* 升级到 *跨 topic / sample 一致执行* 的工程层兑现，并显式登记三处强度限定 + 单 paper 单通道折算的现行规则；(c) 把 17 格盘诚实分母规则的修订挂账（15 格 vs 17 格双重读法）作 2026-06-10 后 D tick 三号兑现指针；(d) 把 timeline.md 双触发预设反向同步为 N1 §尾声 \"可证伪性\" 论断的工程化辅则。本节最大方法学风险是 *把横向饱和度本身当作证据强度的代理* ——这是 timeline.md 已经显式警告的方向，本节再次强调：7/17 / 4 个 topic / 单 paper 三个数字都 *不* 是证据强度信号，它们是 frontier-disclosure 带宽窄结构表现的几何投影，与 mech 候选成立与否在因果方向上正交。N1 框架章的护栏在本现象下经受第一次实证压力测试，结果是 *护栏未被违反，且额外暴露了原本 §七未预见的工程化兑现规则与 §尾声未涉及的可证伪性新维度*——这本身就是 §尾声 \"诚实承担打脸风险\" 在框架章层的小型兑现。

*同步状态*：sample↔§10 双向同步 9/9（叙事层 + 编号层均闭环，N1 §七 + N6 §九 是最后两笔）；M1 八条 $m_k$ 锁定不动；timeline.md 41.2% 单 paper 横向饱和度元-row 不动；N1 §四 / §五 / §六 / §七 全节不动；2026-06-10 冻结到期日新增三号兑现指针（17 格盘诚实分母修订）+ 四号兑现指针（双触发预设兑现审计）；本节属冻结协议白名单 *互引补充* 与 *evidence-base refinement* 两类操作。引用 DCV 2605.28860 / ProFIL 2605.11467 / Causal Tongue-Tie 2605.25891 三处 verified via paper_notes，无 ID / 数字 / 作者 / 日期 fabricated。

### 2026-05-30 reviewer 加注：把 §八 7/17 论断重读为 type I 而非 *单 paper 横向饱和度* 的一般论断

§八 落笔时（2026-05-30 08:30Z）数据集只有 DCV 2605.28860 一颗 ≥40% 单 paper 横向饱和度样本，全节据此把 \"单 paper 横向饱和率\" 当作 frontier-disclosure 带宽窄的 *单一* 经验代理。此后约 16 小时内 [`survey/timeline.md`](../survey/timeline.md) 又登记了两颗 ≥4 域单 paper 饱和样本——MiraBench 2605.29360 (Yang Tianzhuo et al., L1/L2/L3 三层 action-conditioned world-model reliability) 在 6 topic + 1 topic negative + 3 sample = **9/17 ≈ 52.9% positive surface** (commit `c35a629` 15:05Z, 史上首次跨过 50%) 与 Korchinski-Favero-Wyart 2605.27734 (PCFG token-SSL exp(Ω(L)) vs latent-SSL O(1) 分离) 在 4 处理论侧落点 (formal §C-FORM-4 + world_model §JEPA + scaling §C-SCALE-1 falsifier 限定 + survey §10 C-WM-5 evidence-supply, [`taxonomy.md`](../survey/taxonomy.md) 升降级历史 2026-05-31 01:05Z 行 commit `f61f8c4`)。三个样本被 taxonomy.md 同行登记为 *三类不同的 anchor 落点几何*——**type I training-side** (DCV：head-level mechanism 旁证，7 个落点 *独立计数 ≈ 落点数*，因每个落点都给原 mech 候选独立的训练侧 mechanism anchor)、**type II theory-side** (KFW：PCFG sample-complexity 分离，4 个落点 *独立计数 = 1*，因四处都引同一定理只作用域换层级)、**type III surface-side** (MiraBench：reliability benchmark 协议层，9 个落点 *独立计数 ≤ 1*，因三层 reliability 数字是同一 frontier-disclosure 沉默背景下的同根投影矩阵，[`samples/N3-three-puzzle-pieces.md`](N3-three-puzzle-pieces.md) §七 reviewer 加注 commit `1f96072` 已把这一同根性命名为 *负空间 + 协同回退*)。这一三类结构判别（按落点几何而非 paper count）直接挑战 §八 的元-观测前提——**\"单 paper 横向饱和率\" 不是均质代理，而是三种几何投影到同一 17 格盘的叠加信号**。

本加注做四件事，全部落 12 天冻结协议白名单 *互引补充 + 措辞收紧*，不动 §八 (a)(b)(c)(d) 四件主操作的方向、不动 17 格盘诚实分母修订挂账、不动双触发预设、不动 M1 八条 $m_k$、不动 §六 / §七 / §尾声 任一节：(1) §八 第一件事 \"7/17 横向饱和现象做实证刻度对账\" 的论断在 type I 落点几何下仍成立（DCV 7 落点每条都给独立训练侧 mechanism anchor，*部分加固 / 反向警告兑现 / 与 M1 同源* 三条结论字面有效），但**不可外推到 type II/III**——MiraBench 9/17 看似比 DCV 7/17 高 12pp 实际只贡献 ≤1 条独立 evidence，KFW 4/17 看似比 ProFIL / Causal Tongue-Tie 历史峰值高仍只贡献 1 条独立 evidence；按 §八 字面读 MiraBench 应触发更强冲击，按 type 修正后冲击应小于 DCV 而非更大。(2) §八 第二件事 \"M1 护栏从叙事层升级到跨 topic / sample 一致执行\" 的工程兑现在 DCV (type I) 现象下被四个 topic commit 显式 *单一通道折算* 一致执行，但 MiraBench (type III) 9 处落点的 *单 paper 单通道* 折算在 reasoning.md commit `28e79c6` / embodiment.md `b064dcc` / world_model.md `0a17d6b` / N4 §八 `75da138` / N9 §七 `6c4f6f9` 等已落处均已显式标注 *同根 frontier-disclosure 沉默* 与 *VLM-as-judge 中介漂移* 两层 confound——type III 的护栏触发条件比 type I 更紧（不仅要 *单通道折算* 还要 *评测中介偏倚显式登记*），这是 §八 (b) 兑现规则在落笔时未预见的子细化。(3) §八 第四件事 \"timeline.md 双触发预设反向同步\" 在 timeline.md commit `c35a629` 行末已被自主收紧 (\"反向触发条款新加一档：第 3 篇 ≥4 域落点出现则冻结延长 12 天→30 天 + M1 falsifier 单 $m_k$ 公开→≥2 个独立 $m_k$ 同 6 月窗口公开\")，加注把该收紧 *按 type 重读*——\"第 3 篇 ≥4 域落点\" 若全为 type II/III 则三轴叠加 *独立 evidence 计数 ≤ 3*，frontier-disclosure 带宽窄信号实际未升级，原 30 天延长触发应进一步限定为 \"第 3 篇 type I ≥4 域\"，而非任意类型——这一限定不写入主表也不写入 §八 主文，仅在本加注登记为 2026-06-10 冻结到期后五号兑现指针（在 §八 三号 / 四号指针之后）。(4) §八 第三件事 \"17 格盘诚实分母\" 的 15 vs 17 双重读法挂账在 type 修正下需要进一步分层——type I 类信号的诚实分母仍是 15（反方陈词 N8 + 框架章 N1 自身仍不可被 evidence-base 击中），type III 类信号的诚实分母可能更窄（surface-side 协议层 anchor 在 *理论类 sample* 上的接收面同样受限，潜在分母 ≤ 13），但本 tick 不开新挂账只登记观察，与 (3) 同属五号指针前置观察项。

### 2026-05-31 reviewer 加注：§10 统一回贴 (commit `8570ad2`) 对 N1 §八 三号 / 四号 / 五号挂账指针的预期接管

写完前一节 type-aware 二阶读法之后约 31 小时内，[`survey/ntp_survey.md`](../survey/ntp_survey.md) §10 末段在 22:00Z 的 D tick (commit `8570ad2`) 做了一次跨四域 topic δ-i..δ-iv 反向锁定闭环 + sample 侧四章豁免 (N3 `c2fc6e2` / N6 `4777ffe` / N8 `0d247b0` / N9 `1329795`) 共 8 处分散操作的统一回贴。该回贴显式兑现三件：(α) 12 天冻结协议白名单首次跨四域 (causality `57112b1` / reasoning `4a2f966` / scaling `fd6a4d0` / formal `f6f7d6c`) 同步合规 8/8 不延期、(β) sample 侧 9 = 5 (五档形态梯度) + 4 (四章结构性豁免) ↔ §10 M1 1 + 8 (元-corollary + 8 条 $m_k$) 的拆分结构同源对偶 (两组独立投影维：章节 vs metric，不合并、不互相加权)、(γ) C-CONT-1/2/3 半年实施核查作为 OP-WM 时间侧加固第六处同型扩展。本加注不动 §八 主文也不动前一节 type-aware 二阶读法的任一论断，仅就该回贴对 §八 三号 / 四号 / 五号挂账指针的预期接管做单点登记。

三件方法学操作，全部落 12 天冻结协议白名单 *互引补充 + 升降级历史登记* 两类：

- **(1) 三号指针 (17 格盘诚实分母) 的预期接管路径显式化**。§八 三号指针原挂账是 \"2026-06-10 冻结到期后审计 17 格盘的诚实分母规则\"。`8570ad2` (β) 项把 sample 侧 9 章按 5 + 4 拆分——5 档形态梯度章 (N1/N5/N7/N2/N4) 是 *evidence-base 落点接收面*，4 章结构性豁免 (N3/N6/N8/N9) 是 *evidence 不可达* 的结构原因显式登记。其中 N1 与 N8 在 §八 三号指针落笔时被笼统归入 \"反方陈词体 + 框架章 2 格\"，而 `8570ad2` 把 N3 (sample↔sample 投影矩阵负空间) 与 N6 (cross-projection 双投影历史功能位被 §九 + §十首条 update 占满) 也补入 *不可击中* 一类——这意味着 §八 字面给的 *15 格诚实分母* 在 sample 侧应再减 2 格修订为 *13 格诚实分母*。修订方向恰好等于前一节加注里对 type III 类信号潜在分母 ≤ 13 的推断，本次回贴把 type-conditional 修正与 *sample 侧结构性豁免* 修正合流。具体数字调整 *不写入主表 / 不写入 §八 / 不写入前一节*，仅作 2026-06-10 冻结到期后 D tick 的 *三号指针接管路径*——按 13 格分母重算 DCV 7/13 ≈ 53.8% / MiraBench 9/13 ≈ 69.2% / KFW 4/13 ≈ 30.8%，三者按 type 折算后独立 evidence 计数仍是 ≈ 5-6 / ≤ 1 / 1，与 §八 (a) 论断方向一致仅 *分母刻度* 升档。

- **(2) 四号指针 (双触发预设) 的延期协议反向兑现**。§八 四号指针原挂账是 \"timeline `c35a629` 双触发 (单 $m_k$ 公开 ∧ 饱和率 < 25%) 兑现审计\"。`8570ad2` (α) 项揭示 12 天冻结期内跨四域 topic δ 反向锁定 8/8 *零延期*——即 timeline `c35a629` 行末预留的 \"第 3 篇 ≥4 域 type I 触发 30 天延长\" 条款在本窗口内未被触发 (本周期内出现的 MiraBench type III 与 KFW type II 均按前一节加注 *type 重读* 不进 type I 计数, 故未达延期阈值)。这条 *未触发* 是 §八 四号指针的 *第一次区间结算*：12 天冻结协议设计的两层保护 (横向跨域 8/8 合规 + 纵向 type-aware 不扩) 同向兑现，证明 §八 (d) 论断 \"可证伪性应在 evidence-supply 几何层面成立\" 的工程化辅则 *第一次区间通过*——双触发预设的 *负向* 一支 (frontier 沉默且饱和率持稳) 在此窗口内被默认采纳, *正向* 兑现条件仍开放, 与 §尾声 \"打脸风险\" 的三种结局中第二种 (沉默且持稳 ⇒ M1 内核形态需重写) 仍在 2026-06-10 后保留 D tick 审计窗口。

- **(3) 五号指针 (type I 限定 ≥4 域触发延期) 的 sample 侧对照样本登记**。前一节加注五号指针原挂账是 \"≥4 域饱和触发 30 天延期条款应限定为 type I\"。`8570ad2` 回贴的 sample 侧 9 = 5 + 4 拆分给五号指针提供了 *跨方向独立样本*——sample 侧 5 档形态梯度 (N1 framework / N7 派生 triple / N5 6:2 / N2 1:2 / N4 跨 type 最弱端锁限) 本身就是 *type I/II/III 落点几何在 sample 数轴上的形态光谱*, 与 §八 元-观测前提的 *17 格盘横向几何* 形成 *纵向 × 横向* 双轴对照: 横向是 *单 paper × 多 topic anchor 密度三类几何* (taxonomy `f61f8c4`), 纵向是 *单 sample × 多 anchor type 投影数五档梯度* (taxonomy `6832876`), 两轴交叉给 type-aware 二阶读法提供 *跨方向独立验证*——type II/III 在横向上独立 evidence 计数 ≤ 1, 在纵向上 (N5 6:2 / N2 1:2) 对应的形态档也是 *单正双负* 弱形态, 两方向同源不矛盾, 这是前一节加注 type-conditional 论断的 *第一个非平凡 sample 侧旁证*。

诚实承认本加注边界三项：(i) 13 格诚实分母 *未* 改 §八 / 前一节 / 主表任一处既有数字，仅作 2026-06-10 D tick 接管路径登记，避免破坏 §八 (c) 兑现规则的 *原数字可追溯性*；(ii) §10 `8570ad2` (γ) 项的 C-CONT 半年核查归入 OP-WM 第六处同型扩展是 *evidence-supply 通道刻度化* 不是 mech 信号升级，本加注不援引该项加固 N1 §四三分法骨架 (严守 §七 M1 护栏 *M1 不能直接加固 mech 命题*)；(iii) sample 侧 9 = 5 + 4 拆分中 N1 自身归入 *5 档梯度档 1 framework-tier 应用*，N1 是 *提供框架者* 而非 *被框架击中者*，与 §八 \"反方陈词体 + 框架章 2 格不可击中\" 表述在功能定位上不变——5 档归类与 \"不可击中 2 格\" 不矛盾, 是同一事实在两个轴上的不同投影。本加注不动 §四 / §五 / §六 / §七 / §八 主文与前一节加注任一字, 不动 M1 八条 $m_k$, 不动 17 格盘诚实分母原数字, 不动 timeline 双触发预设, 不开新挂账, 仅显式登记 §10 `8570ad2` 对三号 / 四号 / 五号挂账指针的预期接管路径。Commit hashes (`8570ad2` / `c2fc6e2` / `4777ffe` / `0d247b0` / `1329795` / `57112b1` / `4a2f966` / `fd6a4d0` / `f6f7d6c` / `02939dc` / `38dcdda` / `6832876` / `f61f8c4` / `29107ec` / `c35a629`) 全部经 git cat-file 验证为存在 commit 对象, 无 ID / 数字 / 作者 / 日期 fabricated。

诚实判断：本加注最大风险是 *type 修正本身被当作新论断槽位* —— taxonomy.md `f61f8c4` 升降级历史行的 *元-方法论登记* 措辞明确是 \"防 type II/III 视觉上密集横向覆盖被错算高估\"，是 *诊断工具* 而非 *新 mech 候选*。N1 框架章在本加注中承接它的方式严格限于 *把 §八 论断按 type 重读、把 §八 (b) 工程兑现规则按 type 子细化、把 timeline 反向触发条款按 type 收紧* 三件——三件都是把 §八 *现有论断的精度* 提升，不开任何新 mech / cap / pseudo 槽位。若 2026-06-10 冻结到期后再次出现 ≥40% 单 paper 横向饱和样本，第一项操作应是 *先判 type 再算冲击*——type II/III 同样可触发本节四件操作但 *冲击量* 按独立 evidence 计数折算，而非按落点数计算。这一 type-aware 二阶读法是 §八 元-观测前提在落笔后 16 小时内被自主修订的小型兑现，与 §六 \"让框架章自己给自己留下可被未来 Xander 删改的入口\" 同向，本质上是 N1 框架章对 *单 paper 横向饱和率* 这一观测代理的诚实降级——它仍是 frontier-disclosure 带宽窄信号的代理，但是 *type-conditional* 而非均质的代理。引用 DCV 2605.28860 / MiraBench 2605.29360 / KFW 2605.27734 + 各 commit hash (`c35a629` / `f61f8c4` / `1f96072` / `28e79c6` / `b064dcc` / `0a17d6b` / `75da138` / `6c4f6f9`) 经 git log 验证，无 ID / 数字 / 作者 / 日期 fabricated。

---

*本章正文约 4600 字 + §六 2026-05 补遗约 1700 字 + §七 2026-05-30 M1 reviewer pass 约 1500 字 + §八 2026-05-30 单 paper 7/17 横向饱和度对框架章二次冲击 reviewer pass 约 2400 字。Searle / Harnad / Marcus / Sutton / Bubeck / Anthropic faithfulness / Apple illusion-of-thinking / Allen AI faith-and-fate / Reversal Curse 均给一手 source。GPT-4.5 训练成本数字标注 [uncertain]。§六提到的七条 sub-candidate / corollary / route-elimination 子项与 §10 readout-side 结构性社会学不可证伪闭环对应条目均经 cross-link 验证到 [`survey/ntp_survey.md`](../survey/ntp_survey.md) §10 与 [`survey/taxonomy.md`](../survey/taxonomy.md) §升降级历史。下一章 N2 将进入第一类候选的精细化分析：formal expressivity bounds —— TC⁰ 上界、log-precision Transformer、固定深度下的不可解问题类。*
