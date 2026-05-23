# Scale 的三次危机与三次抢救

> 样章 B｜Harari 式叙事候选主线之一
> 时间锚：2026-05。所有未注明的论断，要么标 [推测]，要么给出处。

---

## 一、序：一个时代的中心信条

2020 年到 2023 年，硅谷和北京的机器学习圈共享一句几乎宗教化的格言——**"scale is all you need"**。它的具体表述是 Kaplan 2020 与 Hoffmann (Chinchilla) 2022 两篇 scaling law 论文：模型损失随参数量、数据量、算力呈幂律下降，趋势横跨 7 个数量级仍不见拐点[^kaplan][^chinchilla]。这句格言塑造了一切：OpenAI 用 GPT-3 → GPT-4 的算力翻 100 倍证明它[^gpt4-tr]；Anthropic 把它写进 Responsible Scaling Policy 当作未来威胁的基准[^rsp]；Meta 用它向 Zuckerberg 申请 35 万张 H100[^zuck-h100]；DeepMind、xAI、字节、阿里都按这条曲线规划集群采购。

但格言不是定理。从 2023 年底开始，scale 这条主线在三年内连续撞了三堵墙。每一次撞墙，行业都以为"AI 寒冬"要来；每一次最后又被一种**架构层面或训练范式层面的"抢救"** 接住。被接住的不是 scaling law 本身——而是它的具体兑现方式。

这一章讲这三次危机、三次抢救，以及三轮赌局里押对和押错的人。

---

## 二、第一次危机：dense 模型撞 compute 墙（2023 末 - 2024 中）

### 危机的形状

GPT-4 训练完成于 2022 年 8 月，公开发布于 2023 年 3 月。它是一个 dense Transformer（或者按 SemiAnalysis 的泄漏说法，是 16 个 expert 的 MoE，但 OpenAI 从未承认[^semi-gpt4]）。无论真相如何，GPT-4 这个量级的 dense 训练，第一次让所有人看见了**计算账本的尽头**：

- 单次训练 ~2.15e25 FLOPs（Epoch AI 估算）[^epoch-gpt4]，约 2.5 万张 A100 跑 90 天；
- inference 单 token 成本约是 GPT-3.5 的 30 倍 [推测，基于 API 定价反推]；
- 要把 GPT-4 再 scale 10 倍，需要 30 万张 H100 级别的同步集群，而 2023 年全球 H100 出货总量也才刚刚到这个数。

dense scaling 的物理边界，不在 paper 里，在台积电的 CoWoS 产能里。

### 抢救：MoE 复活

抢救来自一个被冷藏了五年的想法——**Mixture of Experts**。Shazeer 2017 提出 sparsely-gated MoE[^shazeer]，Google 用 Switch Transformer / GLaM 验证过工程可行性[^switch][^glam]，但 OpenAI、Anthropic、Meta 在 2020-2023 几乎都不碰它，理由是 load balancing 难、训练不稳、shipping 风险高。

打破僵局的不是三巨头，而是 **Mistral**（2023-12 Mixtral 8×7B 开源）和**幻方 DeepSeek**（2024-01 DeepSeekMoE，2024-05 DeepSeek-V2，2024-12 DeepSeek-V3）。DeepSeek 的贡献是把 MoE 从"能跑"推到"frontier 可用"：

- **MLA（Multi-head Latent Attention）**：把 KV cache 压到 GQA 的约 1/4，让长上下文 inference 不再是 OOM 噩梦[^v2]；
- **fine-grained expert + shared expert**：256 个细 expert + 1 个共享，top-8 路由，让 specialization 真正发生[^moe-paper]；
- **aux-loss-free load balancing**：用一个无梯度的 bias controller 替代损害主任务的辅助损失[^aux-free]；
- **FP8 训练栈**：把 V3 的训练成本压到声称的 558 万美元（H800 报价）[^v3-paper]——这个数字真假可以争论，但它在 2025-01 的舆论冲击是真实的。

到 2025 年中，**几乎所有 frontier 开源模型都是 MoE**：Qwen3-235B-A22B、Llama 4 Maverick (400B/17B)、Kimi K2、GLM-4.5、MiniMax-01。dense scale 这条原教旨主义路线，事实上只剩 Meta 的 Llama 3.x 系列还在硬抗。

---

## 三、第二次危机：pretraining data 撞墙（2024 中 - 2025）

### 危机的形状

第二次危机几乎和第一次同时浮现，但被人识别得更晚。Ilya Sutskever 2024-12 在 NeurIPS 的 keynote 第一次让它出圈：**"We have but one internet... pre-training as we know it will end."**[^ilya-neurips]

具体的撞墙信号：
- 高质量英文文本被估算在 2024-2028 之间用尽（Epoch AI 2024）[^epoch-data]；
- GPT-4.5 / Orion 训练结果（2025-02 发布）被广泛认为 capability 增益不及成本增益[^gpt45-takes]；
- Meta 的 Llama 4 Behemoth（约 2T 总参 / 288B 激活）2025 年中被多家媒体报道 "indefinitely delayed"[^behemoth-delay]，最终在 2026-04 被 Muse Spark 正式取代[^muse]；
- Anthropic 的 Dario 在多场访谈把"下一代训练成本 100 亿美元"挂在嘴边[^dario-cfr]，但 capability 增益的曲线已经开始可疑。

更尴尬的是：data 不只是量的问题，还有**质的问题**。互联网上"自然存在"的高质量推理样本极少——人不会在博客里写出 8000 token 的内心独白来推导一道数学题。pretraining 永远学不到的是"思考的过程"，因为人类不写。

### 抢救：reasoning / RL / test-time compute

抢救来自 OpenAI 2024-09 的 **o1-preview**。它带来的并不是新架构（OpenAI 至今未发任何 o 系列的架构 paper[^o1-launch][^o1-card]），而是一个新的 scaling 轴：

> **train-time RL compute 和 test-time thinking compute，两条轴都呈对数线性扩展性能。**[^o1-launch]

这是 GPT-3 paper 的双 log 图之后，行业拿到的第二张革命性双 log 图。它意味着：当 pretraining data 撞墙后，**人类可以用 RL on verifiable rewards (RLVR) 让模型自己生产 reasoning trace**——数学题和代码可以被自动判分，不需要人来写过程。

接下来 18 个月的时间线被这一个想法重塑：

- 2025-01 DeepSeek **R1-Zero / R1**：第一次公开证明纯 RL（无 SFT cold start）可以**涌现** long CoT，并把方法论开源[^r1]。这是中国团队第一次在 paradigm 层面而不是 incremental 层面影响行业。
- 2025-02 Anthropic Claude 3.7 Sonnet：第一个明确称自己为 "hybrid reasoning model"，把 extended thinking 做成同一权重的可调模式[^37sonnet]。
- 2025-04 Qwen3 全家：开源圈第一个 hybrid thinking ladder，但 2025-07 静默回退到双 ckpt[^qwen3]——这本身是一个失败信号，下文再谈。
- 2025-08 **GPT-5**：OpenAI 把 o 系列品牌停用，合并成一个 router-based "unified system"[^gpt5-launch]——这是抢救成功的标志，也是第三次危机的开始。
- 2026-Q1 Anthropic Mythos Preview：frontier 定位，受限发布[^opus47]。

到 2026-05，pretraining-as-we-know-it 没有结束，但已经不是 frontier capability 的主战场。**算力预算从 pretraining 向 post-train RL 显著迁移**——Epoch AI 估算 GPT-5 thinking 的 pretrain compute 与 GPT-4.5 同级或略低，节省下来的预算花在了 RL 上[^epoch-gpt5][推测]。

---

## 四、第三次危机：inference 经济学（2025 末 - 进行中）

### 危机的形状

第三次危机最隐蔽，因为它发生在 capability 还在涨的同时。它的形状是：**reasoning 越强，单 query 成本越贵。** o3 在 ARC-AGI-1 高算力档跑出 87.5% 的代价是单题 ~1000 美元[^arc]；GPT-5-Codex 的"dynamic thinking"可以在一个任务上连续工作 7 小时以上[^codex]；Anthropic Opus 4 的 sustained agent run 跑到 30 小时不停[^sonnet45]。每个 token 都比 2023 年贵。

但用户预期和定价被消费级产品压在了 chatbot 时代的水平。结果是：

- API provider 的边际成本曲线和 retail 价曲线**剪刀差越拉越大**；
- DeepSeek 在 2025-09 V3.2-Exp 后把 API 价格再砍 50%[^v32]，逼所有人跟；
- Google Gemini 2.5 Flash、Anthropic Haiku 4.5、DeepSeek V4-Flash、OpenAI GPT-5-mini/nano 集体登场，**轻量档成为产品主力**[^haiku45][^v4flash][^gpt5-dev]；
- 几乎所有大厂同时上线了 **router**：GPT-5 内建 router 在 fast / thinking 之间切[^gpt5-launch]；Claude 在 Sonnet / Opus / extended thinking budget 之间切；DeepSeek V3.1 把 thinking / non-thinking 折回单一权重[^v31]，V4 时代再次拆分为 Pro/Flash 两档。

### 抢救：路由 + 蒸馏 + sparse attention

正在发生的抢救有三层：

1. **路由（routing）**：让"贵模型"只在需要时被叫到。GPT-5 是第一个产品化的例子，但本质是把一部分用户体验和成本的优化责任，从模型权重转嫁到一个分类器上。
2. **蒸馏（distillation）**：把大模型的能力压到小模型里。DeepSeek-R1 一发布就给出 1.5B-70B 的 R1-Distill 系列[^r1]；Anthropic Haiku 4.5 把 Sonnet 4 级 coding 压到 Haiku 价位[^haiku45]；Meta 的 Llama 4 Scout/Maverick 据 blog 是 Behemoth 蒸出来的[^llama4-blog]。
3. **架构层 sparse 化**：DeepSeek V3.2 的 DSA（lightning indexer + top-k token selection）[^v32]；Qwen3-Next 的 hybrid linear attention（48 层里 36 层 Gated DeltaNet）[^qwen3-next]；MiniMax-01 的 lightning attention。这些是在 attention 层面继续把 inference 边际成本压下来。

这次抢救**还没完成**。Flash / router / distill 究竟是解药、还是把延迟和能力的差距重新拉大的下一轮危机的种子，2026-05 还看不清。Sonnet 4.5 的 60+% OSWorld[^sonnet45] 和 Haiku 4.5 的低价，是路由策略奏效的证据；但消费端用户已经在抱怨"GPT-5 不如 GPT-4o 'pop'"——这是 router 把简单 query 偷偷降级的副作用。

---

## 五、赌徒群像

三次危机的下注表，比技术细节更说明问题。

**Sam Altman（OpenAI）押对两次半**。GPT-4 是 dense scale 的极致兑现，让 OpenAI 在第一次危机来临之前已经收完红利；o1 是 reasoning 转向的首发，让 OpenAI 在第二次危机里继续领跑；GPT-5 的 router 化是第三次危机的首个产品级答卷，但它是不是"半个"还要看 GPT-5.5 / GPT-6 是否能继续抬高 frontier。

**梁文锋（DeepSeek）押对了 MoE+RL 双轨**。在大部分中国大厂还在堆 dense 参数的 2023-2024，幻方系把全部赌注放在 MLA + DeepSeekMoE + FP8 上；R1 又抢在 OpenAI 公布 o1 训练方法之前，先开源了一条可复现的 RLVR 路径。梁本人在采访里反复说 "AGI research first, revenue 不是目标"[^liang-interview]——这种姿态在 2024 年的中国语境里近乎反常，事后看是必要条件。

**Dario Amodei（Anthropic）早押 RLHF 和 alignment**。Constitutional AI / RLAIF 在 2022 还被视为"安全研究的小众做法"[^cai]，到 2025 reasoning 转向时，Anthropic 在 RLVR / agentic RL / Computer Use 的工程深度恰好对位——这是 Claude 3.7、4、Sonnet 4.5 在 SWE-Bench 持续领先的根因[^37sonnet][^sonnet45]。

**Mark Zuckerberg 押 dense scale 押过了**。Llama 1-3 的成功让 Meta 相信 open-weight dense 是可持续的护城河。Llama 4（2025-04）想一次性追平 MoE + 长 ctx + 原生多模态三件事，结果 Maverick 在 LMArena 提交事件中信誉受损[^lmarena-maverick]，Behemoth 实质搁置[^behemoth-delay]。2025-06 Meta 成立 Superintelligence Labs (MSL)，Alexandr Wang 主导[^msl]；2026-04 MSL 发布 Muse Spark，官方原话 "ground-up overhaul"——这是 dense 路线在 frontier 序列的体面退场[^muse]。

赌局没有第四种姿态："不下注"。Cohere、Inflection、Adept、Character.ai、Stability——这一档玩家在三次危机里因为没有押任何一条新主线，被无差别地清出 frontier 牌桌。

---

## 六、被牺牲的路径

每一次抢救都意味着另一条路被关掉。把"被牺牲的路径"画出来，scaling 这个叙事才完整。

**dense pure-scaling 的拥趸**：早期 Llama 1/2、TII 的 Falcon 180B、MosaicML 的 MPT、Databricks DBRX 早期 dense 配方、Cohere Command R 早期。其中 Falcon 180B 是最戏剧性的例子——2023-09 发布时号称"开源最强 dense"，半年内被 Mixtral 8×7B 在 inference 成本上完全压制，再也没有继任者。MPT 系列在 MosaicML 被 Databricks 收购后悄无声息。

**reasoning / RL 的反对者**：2024 年有相当一批主流声音认为 long CoT 是"花哨的 prompt engineering"，不会真正改变 capability 上限。Yann LeCun 在多次访谈里把 autoregressive LLM 整体描述为"死胡同"，主张 JEPA / world model 才是出路[^lecun]——这个判断在 reasoning 转向后没有被证伪也没有被证实，但它让 Meta FAIR 在 2024-2025 的 reasoning 浪潮里几乎缺席。Gary Marcus 长期持类似立场。

**hybrid thinking 的早期信仰者**：Qwen3 在 2025-04 用 `enable_thinking=True/False` 切模式，被视为"first open hybrid"；2025-07 静默回退到双 ckpt[^qwen3]。Anthropic 的 hybrid 至今坚持，但已经是少数派——多数玩家承认了 reasoning 和 chat 在 RL 配方上的不可调和。

**纯 process reward model (PRM)**：OpenAI 2023 "Let's Verify Step by Step" 让 PRM 看起来像是 reasoning 的关键[^prm]，但 DeepSeek-R1 paper 公开宣布 PRM 在他们的实验里 reward hacking 严重、放弃了[^r1]。这是 paradigm 层面的一次集体转向，PRM 阵营在 2025 之后基本沉默。

---

## 七、2026 的现在：第三次危机进行中

写到 2026-05，事情没有结束。

frontier 端 GPT-5.5 Instant / Claude Opus 4.7 / Gemini 2.5 / Qwen3-Max-Thinking / DeepSeek V4-Pro 同台竞争，每家都有自己的 router、自己的 thinking budget、自己的 Flash 档。表面上是繁荣，底下是一个共同的赌：**reasoning 抢救出来的 capability，能不能在 inference 经济学被抢救出来之前，把用户从"通用 chatbot"转向"agentic workflow"，从而支撑一个数量级更高的客单价。**

如果可以，三次危机就被三次抢救稳稳接住，scaling 进入下一个十年。

如果不可以，那么 router 不是解药，而是第三次危机的形状本身——我们用产品复杂度暂时遮住了边际经济学的赤字，而真正的拐点会出现在第一家 frontier lab 因为 inference 亏损而不得不调价的那一天。

Harari 在《人类简史》里说过一句话大意是：**所有伟大的叙事，到最后都要面对自己的 inconvenient truth**。"scale is all you need" 这个叙事，目前正在经历它的第三次 inconvenient truth。前两次它都换了形状继续活了下来。第三次会不会，我们还在中间，[推测] 给不出诚实的答案。

---

[^kaplan]: Kaplan et al. 2020, "Scaling Laws for Neural Language Models", arxiv:2001.08361
[^chinchilla]: Hoffmann et al. 2022, "Training Compute-Optimal Large Language Models", arxiv:2203.15556
[^gpt4-tr]: OpenAI 2023, GPT-4 Technical Report, arxiv:2303.08774
[^rsp]: Anthropic 2024-10, Responsible Scaling Policy v2.0
[^zuck-h100]: Zuckerberg 2024-01 Instagram post 提及 350k H100 by EOY
[^semi-gpt4]: SemiAnalysis 2023-07 "GPT-4 Architecture, Infrastructure" 泄漏报道
[^epoch-gpt4]: Epoch AI GPT-4 compute estimate
[^shazeer]: Shazeer et al. 2017, "Outrageously Large Neural Networks", arxiv:1701.06538
[^switch]: Fedus et al. 2021, "Switch Transformers", arxiv:2101.03961
[^glam]: Du et al. 2021, "GLaM", arxiv:2112.06905
[^v2]: DeepSeek-V2 paper, arxiv:2405.04434
[^moe-paper]: DeepSeekMoE, arxiv:2401.06066
[^aux-free]: "Auxiliary-Loss-Free Load Balancing", arxiv:2408.15664
[^v3-paper]: DeepSeek-V3 tech report, arxiv:2412.19437
[^ilya-neurips]: Sutskever NeurIPS 2024 keynote "Sequence to sequence learning"
[^epoch-data]: Villalobos et al. (Epoch AI) 2024, "Will we run out of data?"
[^gpt45-takes]: 多家 takes，e.g. interconnects.ai 2025-02
[^behemoth-delay]: The Information 2025-05, WSJ 2025-08
[^muse]: ai.meta.com/blog/introducing-muse-spark-msl 2026-04-08
[^dario-cfr]: Dario Amodei, Council on Foreign Relations 2025 [口头]
[^o1-launch]: OpenAI 2024-09 "Learning to reason with LLMs"
[^o1-card]: o1 system card
[^r1]: DeepSeek-R1 paper, arxiv:2501.12948
[^37sonnet]: anthropic.com/news/claude-3-7-sonnet 2025-02-24
[^qwen3]: qwenlm.github.io/blog/qwen3, HF Qwen3-235B-A22B-Instruct-2507 model card
[^gpt5-launch]: OpenAI 2025-08-07 "Introducing GPT-5"
[^opus47]: anthropic.com/news/claude-opus-4-7 2026-04-16
[^epoch-gpt5]: Epoch AI GPT-5 compute estimate [推测]
[^arc]: ARC Prize 2024 results, arcprize.org
[^codex]: OpenAI 2025-09-15 "GPT-5-Codex" blog
[^sonnet45]: anthropic.com/news/claude-sonnet-4-5 2025-09-29
[^v32]: api-docs.deepseek.com/news/news250929 2025-09-29
[^haiku45]: anthropic.com/news/claude-haiku-4-5 2025-10-15
[^v4flash]: api-docs.deepseek.com/updates 2026-04-24
[^gpt5-dev]: OpenAI 2025-08-07 "GPT-5 for developers"
[^v31]: api-docs.deepseek.com/news/news250821
[^qwen3-next]: qwenlm.github.io/blog/qwen3-next 2025-09-12
[^llama4-blog]: ai.meta.com/blog/llama-4-multimodal-intelligence 2025-04-05
[^liang-interview]: 暗涌 36kr 2024-07; ChinaTalk 2024-11
[^cai]: Bai et al. 2022, "Constitutional AI", arxiv:2212.08073
[^lmarena-maverick]: blog.lmarena.ai/blog/2025/maverick-tracker/ 2025-04-08
[^msl]: Bloomberg 2025-06-30 "Meta Creates New Superintelligence AI Group"
[^lecun]: LeCun 多次访谈，e.g. Lex Fridman #416 2024-03
[^prm]: Lightman et al. 2023, "Let's Verify Step by Step", arxiv:2305.20050
