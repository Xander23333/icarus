# Frontier 的分裂——从一条路变成五条路

> 样章 C｜叙事主线候选之一｜≈4000 字
> 文风：Harari 式宏观叙事 + 一手出处 + 不确定处 [推测] 标记

---

## 一、分岔时刻：2024 年 9 月 12 日

如果要给"前沿大模型"这件事画一条族谱树，2024 年 9 月 12 日大概是上一次所有人还能坐在同一张桌子前吃饭的日子。那天 OpenAI 在博客上贴出一篇标题平淡到几乎像内部备忘录的文章——*Learning to Reason with LLMs*——并把一个叫 **o1-preview** 的模型推到了 ChatGPT 和 API 上[^o1-launch]。它没有更大的参数，没有更长的上下文，没有更花哨的多模态接口。它只是**在回答之前先想很久**，而且这种"想"是 RL 训练出来的、不是被 prompt 哄出来的。

在那之前的十八个月里，行业像是一支沿同一条河谷推进的部队。GPT-4 是地标，所有人——Anthropic 的 Claude 3、Google 的 Gemini 1.5、Meta 的 Llama 3、Mistral、阿里的 Qwen 1.5、深度求索的 DeepSeek V2——都在做同一件事的两个版本：**把模型做得更大，把对话能力做得更顺**。Chat 是产品形态，pretrain scaling 是技术信仰，MMLU 和 Chatbot Arena 是公认的裁判。竞争是激烈的，但竞争的**坐标系是一致的**。一个外行只要记住"谁的 Arena 排名最高、谁的 context window 最长、谁的 API 最便宜"，基本就能跟上故事。

o1 撕开了这个坐标系。它在 AIME 2024 上从 GPT-4o 的 13.4% 跳到 83.3%[^o1-launch]，但在闲聊、写作、翻译这些"老 benchmark"上几乎没有进步，甚至更慢、更贵、更啰嗦。第一批用户的反应分裂得让人印象深刻：做数学竞赛和写算法题的人惊呼"这是新物种"，做客服 bot 和营销文案的人耸耸肩说"还不如 GPT-4o-mini"。一条河谷开始分成两条。

到了 2026 年春天回头看，分出去的不止两条，而是**五条**。它们之间不再有公认的裁判，不再有可以横向比较的单一 benchmark，甚至不再使用同一种"模型"这个词所指代的东西。这一章想讲的，就是这五条路各自是怎么被一群人选中、又是怎么走到互相看不见对方的。

---

## 二、Reasoning：o1 到底是 hack 还是 paradigm？

o1 发布之后的半年，业内最常听到的私下讨论是一句很短的话："**这是不是一个 trick？**"

理由不是没有。o1 的"思考"在产品上被隐藏起来，用户看不到 chain-of-thought，只能看到一个旋转的菊花和最后的答案——OpenAI 给出的理由是 safety 和 competitive moat[^o1-launch]，但这同时让外界**无法独立验证它到底在做什么**。Sasha Rush 在 2024 年 10 月的一场公开演讲里列出了至少四种可能的实现路径：纯 RL on long CoT、tree search + value model、PRM-guided beam、以及某种 distillation + self-consistency 的混合[^rush-talk]。四种路径对应四种完全不同的 scaling 故事。

真正让"hack 假说"开始崩塌的，是 2025 年 1 月 20 日 DeepSeek-R1 paper 的发布[^r1]。这篇 paper 做了一件 OpenAI 没做的事：**把训练配方写出来**。它说，只要在一个足够强的 base model 上用 GRPO + 可验证 reward（数学答案、代码单元测试）做 RL，long chain-of-thought 会**自己长出来**，包括"等一下，让我重新想想"这种 reflection 行为。它还坦白承认：尝试过 process reward model（PRM），但 reward hacking 太严重，**放弃了**。

这一刻"reasoning 是不是 paradigm"的争论实质性结束了。因为如果一个 600B MoE 的中国团队、用几千万美元规模的预算、不依赖任何秘密 sauce，就能复现 o1 类行为，那么 OpenAI 当初做的就不是 trick，而是**一条可以被独立走出来的路**。Noam Brown 后来在 MIT 的一次问答里只是含糊地说"是的，是 RL"[^noam-mit]，但已经没有人再问"是不是 RL"了。

到 2025 年下半年，这条路上挤满了选手：Anthropic 的 Claude 3.7 Sonnet 把"extended thinking"做成了可滑动的预算条；Google Gemini 2.5 Pro 推出 "Thinking" 模式；xAI Grok 4 把 reasoning 做成默认；阿里 Qwen 推出 QwQ 和 Qwen3-Thinking；甚至 Meta 也在 Llama 4 系列里加入 reasoning 变体[^a-series-cross-ref]。OpenAI 自己则在 2025 年 8 月把 o-series 品牌**收编**进了 GPT-5——一个 router 系统，前面挂一个分类器，按 query 难度决定走 "fast" 路径还是 "thinking" 路径[^gpt5-launch]。换句话说，reasoning 不再是一种模型，而是一种**状态**。

但这条路也开始暴露它的代价。AIME 在 2025 年底基本饱和（GPT-5 / o4-mini 都在 95% 以上），社区被迫往 HMMT、Putnam、USAMO、FrontierMath 这些更难、更小众的题库迁移[^lambert-evals]。FrontierMath 本身又陷入丑闻——Epoch AI 在 2025 年初承认收了 OpenAI 的资助、且 OpenAI 可以访问大部分题目[^epoch-frontiermath]。ARC-AGI-1 上 o3 报出 87.5% 的成绩，但 François Chollet 同时披露：那是 high-compute setting，单题推理成本超过 1000 美元[^arc-blog]。**Reasoning 路线把"成本-性能"曲线从一条线变成了一个三维曲面**，而曲面之间不能简单比大小。

---

## 三、Agentic：当模型开始**替你按回车**

第二条岔路几乎是和 reasoning 同时分出去的，但它的祖师爷不在 OpenAI，而在 Anthropic 和一群创业公司里。

故事的起点是 2024 年 10 月 Anthropic 发布 **Claude 3.5 Sonnet (new)** 时附带的一个被低估的特性：**computer use**[^claude-cu]。模型被允许看屏幕截图、移动鼠标、敲键盘。第一批 demo 笨拙得令人发笑——Claude 会盯着一个按钮看十几秒、点错位置、然后陷入循环——但有些人立刻意识到这不是一个 feature，而是一个**新范式的宣言**：模型不再只是一个回答问题的 oracle，它要变成一个**会自己按回车的雇员**。

2025 年是这条路的爆发年。时间线密集到几乎周更：

- **Cursor** 在 2025 年初把 "composer" 模式升级成真正的 multi-file agent；
- **Cognition** 的 Devin 从一个争议性 demo 变成可以挂在 Linear/GitHub 上的 24×7 工程师；
- **Anthropic** 在 5 月发布 Claude Code，把 agent 做成一个 CLI 工具，明确切走 "Claude 是聊天框" 的旧定位[^claude-code]；
- **OpenAI** 在 9 月推出 **GPT-5-Codex**，官方原话是 "dynamic thinking"，可以在单个 task 内**持续工作 7 小时以上**[^codex]；
- **Google** 在 2025 年底推出 Antigravity，把 agent 嵌入 IDE；
- **阿里 Qwen** 把 Qwen3-Coder 系列做成 open-weight agentic 模型，配套 Qwen Code CLI[^qwen-coder]。

这条路在技术上和 reasoning 有交集——agent 也需要长 CoT、也用 RLVR——但它的**评测语言完全不同**。Reasoning 路线问的是"AIME 多少分"，agentic 路线问的是 "SWE-bench Verified 多少 %、50% time horizon 多长、单 task 成本多少美元、有没有把 prod 搞挂"。METR 的 time-horizon 评测在 2025 年成为这条路的事实标准：GPT-5 在 ~2 小时 17 分，比 o3 的 ~1 小时 30 分长[^metr-gpt5]。

但即便是这个 benchmark 也被业内嘲讽——一个 agent "能独立工作 2 小时"到底意味着什么？意味着它能写完一个 feature，还是意味着它在 2 小时内不会把 git 仓库格式化掉？SWE-bench Verified 上 OpenAI、Anthropic、Google 报的数字差异巨大，但每家用的 harness、retry 策略、scaffold 都不一样，**不可直接比较**[^swebench-note]。一个搞 eval 的朋友（这里就不点名了）对我说过一句话，大意是："以前我能告诉你哪个模型更强，现在我只能告诉你哪个模型在我的 harness 下今天更强。"——这句话本身就是 frontier 分裂的一个症候。

---

## 四、Omni Multimodal：Google 为什么押"原生多模态"？

第三条路在外行眼里最热闹、在内行眼里反而最低调。

2024 年 5 月 13 日，OpenAI 发布 GPT-4o——"o" for "omni"。一个模型同时吃文本、图像、音频，输出文本、图像、音频，端到端、低延迟。发布会上的实时翻译、即兴唱歌、看摄像头解数学题 demo 让整个互联网炸了一天[^gpt4o]。第二天，Google I/O 上 Demis Hassabis 发布 Gemini 1.5 Pro 的多模态长上下文 demo，2024 年底又推出 Gemini 2.0 Flash 的原生图像生成和 Astra agent 原型[^gemini2]。

但 Google 在这条路上的押注比 OpenAI 更深、也更早。Gemini 从 1.0 起就明确写在 tech report 里："**natively multimodal, pre-trained from the start across different modalities**"[^gemini1-report]——不是先训一个 LLM 再贴上 vision encoder，而是从 token 级别就把图像、音频、视频和文本混在一起训练。这是一个**架构上的赌注**，赌的是未来主要的智能任务一定是多模态的，单独优化文本会留下 capability ceiling。

为什么是 Google 押得最重？我倾向于一个**结构性解释** [推测]：

1. **数据禀赋**。YouTube 是地球上最大的视频语料库，Google Search 索引了最多的图文混合页面，Android 摄像头是最大的实时视觉传感器入口。把多模态做成原生范式，Google 的数据护城河才有意义。
2. **产品分发**。Google 的核心产品（搜索、地图、Photos、Workspace、Android）天然是多模态的，纯文本 chat bot 对它的存量业务杠杆有限。把 Gemini 嵌进搜索、嵌进 Pixel 摄像头，才是 Google 的主场。
3. **DeepMind 的研究文化**。从 WaveNet、AlphaFold 到 Gato，DeepMind 长期把"单一架构吃多种模态"当作美学追求，这一点和 OpenAI "scale text to AGI" 的工程美学不同。

到 2025-2026 年，这条路上的玩家其实不多但都很硬：OpenAI（GPT-4o → GPT-5 omni 接口）、Google（Gemini 2.x 系列 + Veo + Imagen 整合）、阿里 **Qwen-Omni** / Qwen2.5-Omni（开放权重的原生多模态）[^qwen-omni]。Anthropic 显著地**没有**全力跟进——Claude 至 2026 年仍然没有原生音频输出，图像生成也不是产品重点。这是一个**主动选择不去打的仗**，Anthropic 把资源压在 agentic 上。

Omni 路线的评测困境比 reasoning 还严重。MMMU、Video-MME、AudioBench 都还在被刷，但它们和"真实的多模态产品体验"之间的相关性极弱。一个能看视频解微积分题的模型，未必能在 Pixel 上帮你认出冰箱里那块发霉的奶酪。

---

## 五、Test-Time Orchestration：当"模型"变成"调度系统"

第四条路最年轻、最不被 mainstream 媒体讨论，但可能是**最具范式杀伤力**的一条。

它的起点也许可以追溯到 Google 在 2024 年底 Gemini 2.0 Flash Thinking 上推出的 **Deep Think** 模式——一个公开承认会"并行采样多条 reasoning 轨迹、再投票合并"的产品形态[^deepthink]。到了 2025 年，xAI Grok 4 推出 "Heavy" 档，本质上是同一个 trick：多 agent 并行 + 后处理融合。OpenAI 的 o1-pro、o3-pro、GPT-5-Pro 走的是同一条路，只是叫法不同。

更激进的是 Microsoft Research 在 2025 年发布的 **Muse Contemplating** 框架 [推测——名字可能记错，文献请核] 和 Anthropic 在 2026 年初公开讨论的 "Constitutional Orchestration"：**单次 query 触发的不再是单个模型推理，而是一个由 router、planner、worker、critic、verifier 组成的小型 multi-agent 系统**，每个角色可能是不同尺寸、不同训练目标的模型。

这条路有几个特征让它和前三条路彻底**不可比**：

- **"模型"作为度量单位失效**。当 GPT-5-Pro 实际上是 GPT-5-thinking 跑 N 次 + GPT-5-fast 做 critic 时，问"GPT-5-Pro 多大"是一个**类型错误**的问题。
- **成本-性能权衡变成一维滑块**。Anthropic Claude 3.7 把 "thinking budget" 直接做成 API 参数；Google Deep Think 让用户选 "Standard / Deep / Ultra"。性能成了**可购买的连续量**。
- **Inference compute 的总盘子开始超过 training compute**。Jared Kaplan 在 2025 年的一次公开访谈里估计 [推测]，到 2026 年 Anthropic 的 inference FLOPs 投入将是 pretrain 投入的数倍——这在 GPT-3 时代是不可想象的。

如果说前三条路还是"模型之争"，这一条路开始问一个更深的问题：**智能到底是参数里的事，还是调度里的事？** Rich Sutton 的 "The Bitter Lesson" 说 search 和 learning 是唯二 scalable 的东西[^bitter-lesson]——pretrain 时代我们重学习轻搜索，test-time orchestration 路线本质上是把搜索这一半补回来。

---

## 六、Open-Weight：中国公司为什么集体选这条路？

第五条路是地缘的，也是经济的。

2024 年 5 月 DeepSeek-V2 发布[^dsv2]，2024 年 12 月 V3 发布[^dsv3]，2025 年 1 月 R1 发布[^r1]——深度求索用三步把"开放权重 + 极低 API 价格 + 顶级性能"这三件事第一次绑在一起摆上桌面。紧随其后：阿里 Qwen 系列（从 2.5 到 3 到 3-Max，到 Coder、Omni、VL 全家桶）[^qwen3]、月之暗面 Kimi K2（万亿参数 MoE，2025 年中开源）[^kimi-k2]、智谱 GLM-4.5 / 4.6[^glm45]、零一万物、阶跃星辰、MiniMax、字节豆包……到 2026 年春天，**全球 open-weight leaderboard 的前十名里有七到八个是中国实验室的产品**。

为什么是中国公司**集体**选了同一条路？同样给一个结构性解释 [推测]：

1. **算力约束倒逼效率**。出口管制让中国公司拿不到最新的 H100/B200 集群，必须在更小的 cluster 上做更聪明的事——MoE、FP8 训练、DualPipe（DeepSeek 在 V3 paper 里详细写了通信-计算 overlap）[^dsv3]——这些东西最后变成了**真正的技术资本**。
2. **闭源没有商业出路**。在国内做 ChatGPT 直接对标 OpenAI 几乎不可能赢（监管 + 渠道 + 品牌），但做"全世界开发者都用的开放权重"是一个可以绕开美国云生态的路径——HuggingFace 下载量、Ollama 集成、本地部署，这些渠道是 OpenAI 鞭长莫及的。
3. **集体身份的政治经济学**。一旦 DeepSeek 证明"中国公司也能做出全球认可的 frontier 模型"，其它实验室如果继续做闭源 + 国内 to C，叙事上就矮了一截。**Open-weight 成了一种集体的国家叙事**——这不是阴谋论，是一种**可观察的同侪压力**。

这条路的代价同样显著。**Open-weight 不等于开放**：DeepSeek、Qwen、Kimi 都没有公开训练数据、训练 code、完整 RL 配方；Llama 4 的发布也被广泛批评为"open-weight in name only"[^llama4-criticism]。**开放权重的真实含义是"你可以本地跑、可以微调、可以蒸馏"，但你无法独立复现**。这让 open-weight 路线变成了一个奇怪的生态位：**比闭源透明，比真正的开源科学保守得多**。

---

## 七、尾声：不可比性的代价

写到这里应该承认一件让搞评测的人绝望的事：**到 2026 年，"哪个模型最强" 这个问题已经没有定义良好的答案了。**

- 一个 reasoning 模型在 AIME 上拿 99%，但在 multi-turn agentic 任务上做不过 Claude；
- 一个 agentic 模型 SWE-bench 74%，但不会说话、不会画图、不会唱歌；
- 一个 omni 模型能实时翻译、能看视频、能生成图像，但数学竞赛得分远落后；
- 一个 test-time orchestration 系统在所有 benchmark 上都赢，但单次 query 成本 100 美元；
- 一个 open-weight 模型免费、可本地、可微调，但官方训练细节一概不知。

Chatbot Arena 还在更新，但它**只能测对话偏好**；MMLU 已经被废弃；HELM、BIG-Bench 这些 holistic 评测被 frontier labs 实质性遗弃。新的评测——SWE-bench、METR time horizon、ARC-AGI、FrontierMath、AIDER polyglot、τ-bench、GPQA Diamond——**每一个只服务一条路**，互相之间不能加权平均。

这是 frontier 分裂在评测层面的代价：**我们失去了一个公共的智能坐标系**。在物理学里，这有点像 19 世纪末的"两朵乌云"前夕——大家还在用同一套语言谈论"模型"，但语言下面的指称对象正在分裂成五种完全不同的物种。Harari 在写智人的认知革命时说，是共同的虚构故事把人类联结成大规模协作的群体。**Frontier 这个共同故事正在解体**——而下一个共同故事是什么，2026 年春天还看不清楚。

也许根本不需要一个共同故事。也许多元化本身就是答案——就像生物多样性比单一最优物种更鲁棒一样。但如果你是一个想"跟上前沿"的从业者，2026 年的真相是残酷的：**你不能再跟上"前沿"，你只能选一条路，并接受自己看不见其它四条路的代价**。

这本书后面的章节会试着把这五条路各自走一遍。但请记住：**它们之间的距离正在变大，而不是变小**。

---

## 注释

[^o1-launch]: OpenAI, *Learning to Reason with LLMs*, 2024-09-12. https://openai.com/index/learning-to-reason-with-llms/
[^rush-talk]: Sasha Rush, *Speculations on Test-Time Scaling*, 2024-10 公开演讲。
[^r1]: DeepSeek-AI, *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning*, 2025-01-20, arXiv:2501.12948.
[^noam-mit]: Noam Brown, MIT EI 演讲 Q&A, 2024-10.
[^gpt5-launch]: OpenAI, *Introducing GPT-5*, 2025-08-07.
[^a-series-cross-ref]: 详见本书 vol1-architecture A1-A10 各章。
[^lambert-evals]: Nathan Lambert, Interconnects newsletter on benchmark saturation, 2025 多篇。
[^epoch-frontiermath]: Epoch AI 公开声明 + LessWrong 讨论, 2025-01.
[^arc-blog]: François Chollet, ARC Prize blog on o3 results, 2024-12 / 2025-03 updates.
[^claude-cu]: Anthropic, *Introducing computer use*, 2024-10-22.
[^claude-code]: Anthropic, *Claude Code launch*, 2025-02 (research preview) / 2025-05 (GA).
[^codex]: OpenAI, *GPT-5-Codex* blog, 2025-09-15.
[^qwen-coder]: Alibaba Qwen team, *Qwen3-Coder* release notes, 2025.
[^metr-gpt5]: METR, *Measuring AI Ability to Complete Long Tasks*, 2025 updates including GPT-5.
[^swebench-note]: SWE-bench team, harness comparison notes; Carlos Jimenez 等多次 Twitter 澄清。
[^gpt4o]: OpenAI, *Hello GPT-4o*, 2024-05-13.
[^gemini2]: Google DeepMind, *Introducing Gemini 2.0*, 2024-12.
[^gemini1-report]: Google, *Gemini: A Family of Highly Capable Multimodal Models*, tech report 2023-12.
[^qwen-omni]: Alibaba, *Qwen2.5-Omni Technical Report*, 2025.
[^deepthink]: Google DeepMind, *Gemini 2.0 Flash Thinking / Deep Think* blog, 2024-12.
[^bitter-lesson]: Rich Sutton, *The Bitter Lesson*, 2019.
[^dsv2]: DeepSeek-AI, *DeepSeek-V2 Technical Report*, 2024-05, arXiv:2405.04434.
[^dsv3]: DeepSeek-AI, *DeepSeek-V3 Technical Report*, 2024-12, arXiv:2412.19437.
[^qwen3]: Alibaba Qwen team, *Qwen3 Technical Report*, 2025.
[^kimi-k2]: Moonshot AI, *Kimi K2* release, 2025 年中。
[^glm45]: Zhipu AI, *GLM-4.5 / 4.6* release notes, 2025.
[^llama4-criticism]: Simon Willison / Nathan Lambert 等就 Llama 4 发布的公开批评, 2025.
