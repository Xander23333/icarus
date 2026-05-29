# Hallucination 是 NTP 的能力问题，还是认识论缺陷？

## 一、2022 年夏天的一次内部讨论

故事从 Anthropic 在 2022 年夏天放出的一份 47 页 PDF 说起。论文叫 [*Language Models (Mostly) Know What They Know*](https://arxiv.org/abs/2207.05221)，一作 Saurav Kadavath。当时 ChatGPT 还没上线，业内对 LLM 的主流抱怨是 "它一本正经地胡说"。Kadavath 这篇做了一件之前没人系统做过的事：把模型对自己回答的 *置信度* 单独抽出来评估——让同一个 base LM 先答题，再单独 forward 一次问它"刚才那个回答正确的概率是多少"，看校准曲线。

结论让圈内一部分人坐直了。Anthropic 内部从 12B 到 52B 的 base 模型（pre-RLHF）在 TriviaQA、Lambada、Codex HumanEval 这些 benchmark 上的 *self-reported probability* 与 *actual accuracy* 的 reliability diagram 接近对角线，ECE 普遍 <0.05。换句话说：base LM **在自己头脑里其实知道哪些回答是猜的，哪些是有把握的**。这跟外部观察到的"它胡说得很自信"完全相反。

如果 Kadavath 是对的，那 hallucination 就不是简单的 capacity 问题。模型 *有* 那个信号，只是没把信号原样输出。Yann LeCun 当时在 Twitter 上没有评论这篇——他后来更愿意引用的是 Burns 在 2022 年 12 月放出的 [*Discovering Latent Knowledge in Language Models Without Supervision*](https://arxiv.org/abs/2212.03827)（Collin Burns 一作，UC Berkeley，当时是 Jacob Steinhardt 学生）。Burns 用 CCS（Contrast-Consistent Search）的方法在 hidden state 上拉出一个无监督方向，结果发现：在若干 TruthfulQA 子集上，**probe 给的 belief 比模型自己输出的答案更准**——差距最高接近 4 个百分点。如果把 probe 视为"模型相信什么"，把 output 视为"模型说什么"，**这两者在 LLM 内部是分裂的**。

Kadavath + Burns 这两篇论文，在 2023 年之前都被归在"interp 圈的小工具"那一档。直到 2024 年 frontier 上线大量 verbalized-confidence 训练（Claude 3.5、GPT-4-turbo 的 "I don't know" 行为、Gemini 1.5 的 abstention prompt），这两篇才被回头追认为 *epistemic grounding* 这条线的起点。我想在这一章把这条线讲清楚：**hallucination 真正的根，不在参数量不够、也不在数据噪声，而在 NTP 训练目标本身没有把"模型相信什么"和"模型应该说什么"区分开来**——这是一个认识论结构问题，不是 capacity 问题。

## 二、为什么 NTP 目标天然产生这种分裂

要看清这个结构，得回到 cross-entropy 损失的形式。Next-token prediction 的训练目标是

$$\mathcal{L} = -\mathbb{E}_{(x_{<t}, x_t) \sim \mathcal{D}}\, \log p_\theta(x_t \mid x_{<t}),$$

注意几件事：(i) 目标在 *token 序列层面* 而不是 *命题层面*，模型从不被要求对一个完整命题作真值判断；(ii) 训练分布 $\mathcal{D}$ 中包含大量 "看起来流畅的错误内容"（被指出是错的 reddit 帖、过时的 wikipedia 条目、合理但虚构的小说叙述），这些样本的 ground-truth token 仍是 *实际出现的 token*，与命题真值无关；(iii) 训练里不存在"我不知道"这个监督信号——人类作者很少在文本中显式标注自己的不确定性，绝大多数虚构、过时、错误内容是以陈述句形式给出的。

把这三件事合起来：NTP 训练在做的事情是 *最大化模型对人类文本表面分布的拟合*，而 *不是* 最大化模型对世界真值的拟合。Gekhman 等人 2024 年的 [*Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?*](https://arxiv.org/abs/2405.05904)（EMNLP 2024）从相反方向给了这一点最干净的实证：在 base LM 上 SFT 注入新事实，模型在 *新事实本身的准确率* 上略有提升，但在 *与之相关的旧事实* 上的 hallucination 率显著上升——SFT 把"用陈述句说事实"的 *行为模式* 强化了，而不是把"哪些事实可信"的 *epistemic 结构* 强化了。Gekhman 的图把这个 trade-off 画成一条单调上行的曲线：注入的新事实越多，旧域 hallucination 越多。这是 *目标函数错位* 的直接观测。

更精细的证据来自 Li 等人 2026 年的 [*FFN-as-grounding bottleneck*](https://arxiv.org/abs/2605.26362)（[unverified ID]，Anthropic alignment team）。他们在 linearized 结构知识（知识图谱三元组、多跳查询、表格读取）上做 causal patching，发现 hallucination 的 *sufficient statistic* 是 FFN 层未能把 context 中的事实正确写入 residual stream——不是 attention 失焦，不是 readout 噪声，是 *写入失败*。跨 schema 通用的 detector AUC > 0.8。这给"输入侧（attention 看到的）和输出侧（logit 给出的）之间存在一个 FFN 写入瓶颈"提供了 mech 级证据。

把 Kadavath / Burns / Gekhman / Li 四篇放在一起，hallucination 的结构画面就出来了：模型在 hidden state 里 *知道* 自己不确定（Kadavath 的 self-prob + Burns 的 probe），但在 output 端 *被训练成* 不报告这个不确定性（NTP 目标 + Gekhman 的 SFT 强化），而中间的 FFN 写入瓶颈（Li）决定了即使 readout 想报告 belief，它也只能拿到 *已经被压缩掉不确定性的* 信号。这是 [`topics/grounding.md` C-GROUND-7](../topics/grounding.md) sub-candidate 在 sample 层的具体讲法：**probe-derived belief 与 output-derived confidence 在 contested subset 上 ρ ≤ 0.5，gap 对 N 不显著敏感**。

诚实的反例：上面这条 *认识论缺陷* 解释路径，至少有三个口子还没堵。第一，Kadavath 自己的论文里也写明，**self-prob 校准在 OOD 任务上塌得很快**——意思是 base LM "知道自己不确定" 这件事可能只在 in-distribution 任务上成立，到了 long-tail 事实查询那就 *真不知道*，那时 hallucination 就退化回 capacity 问题（Smith 2026 [arxiv:2605.18732](https://arxiv.org/abs/2605.18732) 把这种 capacity-bound 的 recall 拟合到 (log params, log freq) sigmoid 上）。第二，Burns CCS probe 本身有可复现性争议——后续若干工作（[2310.06824](https://arxiv.org/abs/2310.06824) Levinstein-Herrmann *Still No Lie Detector for Language Models* 等）指出 probe 学到的方向更像 *prompt 模板特征* 而非 *belief 特征*，分裂可能是 probe 伪影。第三，Xu 等人 2024 年的 [*Hallucination is Inevitable*](https://arxiv.org/abs/2401.11817) 给出了一个非常 deflationary 的形式结果：在任意可计算的 ground-truth 函数族上，hallucination 是 NTP 模型在信息论意义下 *不可避免* 的——也就是说，再怎么修也修不光，剩下的争论是 *修到多少残差*。

我倾向于这样判断：到 2026-05 为止，"hallucination = epistemic failure" 这条线的证据比 "hallucination = capacity failure" 强，但只强一点点——大概是 65/35 而不是 80/20。决定性证据要等 frontier 公开 (a) 一个在 contested subset 上 probe-belief 与 verbalized-confidence ρ 的直接测量、(b) 一个 RLHF 前后 epistemic-readout gap 的对照实验、(c) 一个真正解耦了 epistemic-uncertainty 与 aleatoric-uncertainty 的训练目标改动。这三件事工程上都做得起，没做的原因和 [`topics/online_learning.md`](../topics/online_learning.md) C-CONT-2 第三支柱说的一样：**披露选择函数**——frontier 不公开 epistemic 评估的真实数字。

<!-- TODO: §三 (RLHF 之后 epistemic gap 如何变化), §四 (verbalized confidence 真的有用吗 - R-Tuning / Self-Aware 三条线), §五 (与 C-GROUND-7 / C-CONT-1 / C-CAUSAL-DISCLOSE 三角关系), 尾声: hallucination 不是 bug 是 NTP 目标的特征 -->
