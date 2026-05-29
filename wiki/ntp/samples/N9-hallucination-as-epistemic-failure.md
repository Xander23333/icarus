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

## 三、RLHF 把 epistemic gap 拉大了，而不是缩小了

如果 §二 的画面成立，下一个自然问题是：RLHF / preference tuning 这一步——它本来就被 Christiano 团队 2017 年那篇 [*Deep Reinforcement Learning from Human Preferences*](https://arxiv.org/abs/1706.03741) 提出来当作\"把模型对齐到人类偏好\"的方法——有没有在 epistemic 这一侧帮上忙？答案在 2023 年内已经几乎被定下来了，而且方向跟一开始的预期相反。

最早一处直接观察来自 OpenAI 的 GPT-4 technical report ([arxiv:2303.08774](https://arxiv.org/abs/2303.08774))。报告 Figure 8 给出了 pre-RLHF base GPT-4 与 post-RLHF GPT-4 在 MMLU 多选题上的 reliability diagram：base 模型的 ECE 大约是 0.007，post-RLHF 模型 ECE 升到 0.074——**校准度跌了一个数量级**，曲线明显被推向\"对所有答案都打 90% 以上信心\"那一侧。OpenAI 在 report 里把这一段写得很克制，只说 \"the post-RLHF model is significantly less calibrated\"，没有展开为什么。但圈内人都知道这意味着什么：RLHF 用人类 preference label 训出来的 reward 函数偏好 *果断、流畅、有把握的语气*，而不是 *诚实地表达不确定*——模型为了拿高 reward 学会了把 §二 里 hidden state 中存在的不确定信号 *进一步压扁*。

Kadavath 团队自己也回头做了对照。在 [arxiv:2207.05221](https://arxiv.org/abs/2207.05221) 的附录里他们已经报告了一组 RLHF vs base 的 self-prob 校准对比，趋势与 OpenAI 一致；2023 年 Tian 等人的 [*Just Ask for Calibration*](https://arxiv.org/abs/2305.14975)（Katherine Tian, Stanford）系统化了这件事：他们在 GPT-4 / Claude-1 / PaLM-2 上同时跑 *logit-derived confidence* 与 *verbalized confidence*（直接让模型说\"我有 X% 把握\"），发现 post-RLHF 模型上 **verbalized confidence 反而比 logit-derived confidence 更接近真实正确率**——logit 那侧被 RLHF 压坏了，verbalized 那侧因为是显式被 prompt 拉出来的反而保留了一些校准信号。这是个非常奇怪的结论：模型 *嘴上说的* 不确定度比它 *内部的* logit 概率更可信。

把这个观察接回 §二 的结构图：RLHF 不是修复了\"hidden belief / output 分裂\"，而是把分裂的位置往后挪了一层——base 阶段分裂在 \"hidden state 知道 vs output 不报告\"，post-RLHF 阶段分裂在 \"hidden state 知道 vs logit 不再保留 vs verbalized 还能拉出来一点\"。Zhang 等人 2023 年的 [*R-Tuning: Instructing Large Language Models to Say 'I Don't Know'*](https://arxiv.org/abs/2311.09677)（Hanning Zhang, HKUST）正面攻击这一点：他们用一个简单的两阶段 SFT——先在 base 上判定哪些问题模型 *不会*，再用 \"I don't know\" 作为这些问题的 ground-truth target——把 LLaMA-7B/13B 在 ParaRel/HotpotQA 上的 hallucination rate 砍掉 30-50%，同时只损失 5% 左右的覆盖率。R-Tuning 之后类似工作密集出现：Yang 等人 [*Alignment for Honesty*](https://arxiv.org/abs/2312.07000)、Cheng 等人 [*Can AI Assistants Know What They Don't Know?*](https://arxiv.org/abs/2401.13275)、以及 2024 年下半年 Anthropic Claude 3 系列在 system card 里点名的 \"abstention training\"——共同的训练配方都是 *把 epistemic 信号显式作为监督信号注入*，而不是指望 RLHF 自己长出来。

诚实的反例三处。第一，GPT-4 report 那张 reliability diagram 是在 MMLU 多选题上做的，多选题的 calibration metric 与开放式生成上的 hallucination 是两个不同空间——Kapoor 等人 [arxiv:2402.04614](https://arxiv.org/abs/2402.04614) 反复指出多选 ECE 不能外推到开放生成。第二，R-Tuning / Alignment-for-Honesty 这一类工作的成功是在 *已知问题集合* 上做监督，本质是用 IID train-test 切片把 \"我不会\" 的边界 *记住*，不是真正学会 *识别不确定*——一旦把测试集换到 long-tail 新事实，提升幅度从 30-50% 跌到 5-10%（Yang 2312.07000 附录 D 的 OOD 子表）。第三，2024 年下半年的 frontier 模型（Claude 3.5 / GPT-4o）在 verbalized confidence 上的表现似乎在 *回升*——但 frontier 不公开训练配方，外界无法判断这是 (a) abstention training 真起作用，还是 (b) post-training 阶段加了 calibration-targeted RL stage，还是 (c) 评估 prompt 模板本身被调过——这把第三层证据卡死在 [`topics/online_learning.md`](../topics/online_learning.md) C-CONT-2 第三支柱说的同一个披露选择函数上。

到 2026-05 为止我的判断：**RLHF 在 epistemic 这一侧是负作用，需要专门的 abstention/honesty training 来弥补**——这件事在 base→RLHF→abstention-SFT 三段曲线上已经被三组独立工作（OpenAI 2303.08774 / Tian 2305.14975 / Zhang 2311.09677）按同方向钉住。但 *abstention-SFT 是不是真的解决了 epistemic 问题，还是只是在 in-distribution 上把 \"我不会\" 答案学会了*，这个更深的问题在 OOD 评估全部锁在 frontier 内部之前没有答案。下一节我想顺着这条线追下去：verbalized confidence 真的是 epistemic 信号，还是另一个层次的表面拟合。

## 四、Verbalized confidence 真的是 epistemic 信号吗

§三 末尾留了一根刺：Tian 2305.14975 发现 post-RLHF 模型 *嘴上说的* 不确定度比内部 logit 概率更可信。这件事如果坐实，那 §一 / §二 那条 \"hidden belief / output 分裂\" 的解释就要被改写成更不舒服的版本——belief 不是被 *压扁* 了，而是被 *转录* 到另一个表面通道里去了，而那个通道恰好是 *人类标注者最容易奖励* 的通道（一句 \"I'm about 70% sure\"）。问题是：转录是真的，还是只是另一层表面拟合？

要回答这个问题得先回到这条线的起点。2022 年 5 月，OpenAI 的 Stephanie Lin、Jacob Hilton 与 Owain Evans 放出 [*Teaching Models to Express Their Uncertainty in Words*](https://arxiv.org/abs/2205.14334)——这是 \"verbalized confidence\" 这个术语第一次被系统提出来的工作。他们在 GPT-3 上用 CalibratedMath 做 supervised fine-tune，让模型在答数学题时一并输出 \"X% confidence\"，发现 in-domain 上 verbalized ECE 可以压到 0.05 以下，并且 *泛化到没在 fine-tune 中出现过的算术子类型* 时校准还撑得住。Lin 自己在 paper 里把这个结果限定得很严：(a) 只在 CalibratedMath 这一个相对窄的域上测、(b) 模型骨架是 GPT-3 base 不是 RLHF 模型、(c) 泛化的边界在 *分布外* 任务上没测。但圈内当时把它读成了 \"verbalized 通道可学且可泛化\" 的肯定结果。

一年多以后这个肯定结果被两篇正面挑战。第一篇是 Xiong 等人 2023 年 6 月的 [*Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs*](https://arxiv.org/abs/2306.13063)（Miao Xiong，NUS）——他们在 GPT-3.5 / GPT-4 / Vicuna / LLaMA-2 上系统跑了 4 种 verbalized elicitation 模板（\"Confidence: X%\"、\"How sure are you?\"、self-consistency vote、top-k re-prompt），结果发现：(i) 不同模板之间 verbalized confidence 的相关性只有 ρ ≈ 0.3–0.5，远低于 logit-derived confidence 之间的跨 prompt 一致性；(ii) verbalized confidence 在 *简单事实题* 上接近校准，但在 *推理多步题* 上系统性 overconfident，且 overconfidence 随着 chain-of-thought 长度单调上升。Xiong 给出的解释是：verbalized 通道学到的不是 *unconditional epistemic state*，而是 *conditional on prompt-style 的对话表面*——把模板从礼貌问询换成 \"answer concisely with confidence\" 就会让 ρ 跌掉一半。

第二篇是同年 5 月 Yin 等人的 [*Do Large Language Models Know What They Don't Know?*](https://arxiv.org/abs/2305.18153)（Zhangyue Yin，复旦）。他们构造了 SelfAware benchmark——一组人类一致认为 \"不知道\" 才是正确答案的开放性问题（如 \"Joe Biden 的高中老师叫什么名字\"），让 GPT-4 / Claude-1 / 各类开源模型尝试 verbalized abstain。结论：frontier 模型的 self-aware F1 普遍 < 50%，开源模型 < 30%；并且这个分数跟传统 in-domain calibration ECE 相关性很弱——也就是说，*在已知题上校准好的模型，在未知题上未必能 abstain*。Yin 在讨论里直接写：verbalized self-awareness 与 logit-derived calibration 是 *两个独立维度*，不能互相替代。

到这里 §三 的 \"verbalized 反而更可信\" 与本节的两个挑战之间的张力其实可以解开：Tian 在 2305.14975 测的是 *triviaqa / sciqa 这类 in-distribution 事实题*，Xiong / Yin 测的是 *跨模板 / 跨任务 / 跨已知-未知边界* 的稳健性。三组结论合起来给出一个相对稳定的画面：**verbalized confidence 是 epistemic 信号的一个 *投影*，但投影矩阵依赖 prompt 模板与任务类型，并且在 abstention 决策上与 logit 通道独立**。这正是 §二 末段我把 C-GROUND-7 的 falsifier 收紧为 \"probe-belief 与 output-confidence 在 contested subset 上 ρ ≤ 0.5、对 N 不敏感\" 的实证根据——ρ ≤ 0.5 不是凭空挑的数字，是 Xiong 跨模板内一致性的下限。

诚实的反例两处。第一，Zhou 等人 2024 年的 [*Relying on the Unreliable: The Impact of Language Models' Reluctance to Express Uncertainty*](https://arxiv.org/abs/2401.06730)（[unverified ID]，Kaitlyn Zhou，Stanford）做了一个反方向实验：把 verbalized confidence 强行 *暴露* 给下游用户，发现用户对 \"模型说 60%\" 与 \"模型说 90%\" 的依赖差距比 Bayes-optimal 小得多——意思是即使 verbalized 通道是真信号，*用户也未必能正确解码*，那么 epistemic 通道的工程价值就要打折。第二，2024 年下半年开始陆续有工作（Steyvers 等人 [unverified] 在 PNAS 上一篇关于 GPT-4o 的 calibration gap 研究，[arxiv ID unknown]）指出 frontier 模型的 verbalized calibration 在 2024Q4 → 2025Q1 之间被人为优化过——具体配方未披露，但 ECE 跳跃式下降与外部能力评估没有同步变化，符合 *专门做 calibration-targeted post-training* 的特征，这把 \"verbalized 通道是不是天然的 epistemic 投影\" 的判断又一次卡死在 [`topics/online_learning.md`](../topics/online_learning.md) C-CONT-2 第三支柱的披露选择函数上。

我现在的判断：verbalized confidence **确实是一条独立的 epistemic 通道**，不只是 logit 的转录——这一点由 Tian / Xiong / Yin 三组独立证据（同方向但测度不同：跨模型一致 / 跨模板分裂 / 跨已知-未知独立于 ECE）共同支撑。但它 *作为 epistemic 信号的可用性*，在 frontier 模型上被披露选择函数锁死，外部研究者能确证的只是 \"通道存在且可学且可破坏\"，无法确证 \"在 2026 年的 frontier 模型上这个通道仍是真信号还是已经被 calibration-targeted training 拟合成另一种表面\"。这是 §三 \"abstention-SFT 是不是真解决了 epistemic 问题\" 与本节 \"verbalized 是不是真 epistemic 信号\" 共享的同一个评估锁——两层都卡在同一处。下一节我想把这条 epistemic 解释路径与 grounding / continual / causality 三条 topic 线的关联画出来，看 hallucination 到底应该算到哪条 NTP-mech 候选名下。

<!-- TODO: §五 (与 C-GROUND-7 / C-CONT-1 / C-CAUSAL-DISCLOSE 三角关系), 尾声: hallucination 不是 bug 是 NTP 目标的特征 -->
