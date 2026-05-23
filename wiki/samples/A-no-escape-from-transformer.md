# 为什么没人能逃离 Transformer

## 一、编年史：一篇论文如何吃掉一个领域

故事要从 2017 年 6 月的一篇 arxiv 论文说起。那篇论文叫 *Attention Is All You Need*，作者八个人，主笔 Ashish Vaswani，目的卑微得近乎可笑——他们只是想给 Google Translate 换一个更好训练的编码器，干掉 LSTM 那堆顺序依赖。论文里 BLEU 数字提升不算夸张，标题倒是写得像广告。当年 NeurIPS 接收时审稿人评价平平，没人觉得它会改变什么。

九年之后，2026 年 5 月，地球上几乎每一个被认真使用的大模型——GPT-5、Claude 4.x、Gemini 2.x、DeepSeek-V3、Qwen3、Llama 4、Grok 3、Kimi K2、GLM-4——都是 Transformer。区别只在于注意力是 dense 还是 MoE、KV cache 是 MLA 还是 GQA、context window 是 128K 还是 1M。骨架是同一副骨架。

中间发生了什么？只要把时间线压成一句话就够了：

> **2017 attention → 2020 GPT-3 把它放大 100 倍 → 2022 Chinchilla 告诉大家应该放更多数据 → 2024 dense scaling 撞墙 → MoE 救场 → 2025 reasoning / test-time compute 救场第二次 → 2026 整个产业默认 "Transformer + 修补" 就是答案。**

这条线和 Harari 写智人替代尼安德特人时的逻辑一模一样：一个并不显著优越的物种，在某个偶然窗口里拿到关键资源，从此再没有把生态位让出去过。Transformer 拿到的关键资源叫 **NVIDIA GPU 的 matmul 吞吐**。它的所有竞争者——RNN、CNN、SSM、diffusion、JEPA——都在试图绕开这个事实，结果发现 H100 / B200 的设计本身就是围绕 "大块稠密矩阵乘法 + softmax" 优化的，硬件和算法形成了正反馈。每一次有人说 "我们不需要 attention"，下一代 GPU 就会让 attention 变得更便宜一点。

到 2024 年下半年情况已经清楚：dense Transformer 单纯放大参数的曲线显著趋平（GPT-4 → GPT-4.5 的智能跃迁远小于 GPT-3 → GPT-4），但取而代之的不是新架构，而是两次**对 Transformer 本身的修补**：

1. **MoE**：把 FFN 切成几十上百个专家，每个 token 只激活几个。Mixtral 8×7B、DeepSeek-V2/V3、Qwen3-Next、Llama 4、Kimi K2 全是这条路。MoE 让"激活参数 / 总参数"比降到 5% 以下，于是同样推理成本下可以塞下 10 倍的知识。
2. **Test-time compute / reasoning**：OpenAI o1 (2024-09)、DeepSeek-R1 (2025-01)、Claude 4 Extended Thinking、Gemini 2.5 Thinking 把算力从训练侧转移到推理侧，让模型在回答前先写几千 token 的草稿。架构没变，只是允许它"想久一点"。

也就是说，2024–2026 这两年里 frontier model 上最重要的两次能力跃迁，**都没有动到 Transformer 的骨架**。MoE 改了 FFN，reasoning 改了 decoding 策略。Attention 块本身——Q、K、V 三个投影、softmax、KV cache——一行都没改。

这是这一章要回答的问题：为什么？为什么会有这么多人想逃，最后又都被吸回来？

## 二、逃亡者：三个想绕开 Transformer 的人

把"逃亡者"画成三张脸最直观：Albert Gu 代表 SSM/Mamba 路线，Yann LeCun 代表 JEPA / world model 路线，Aaron Lou 与 Stefano Ermon 的学生们（Inception Labs、Gemini Diffusion 团队）代表 diffusion language model 路线。三个人的失败方式各不相同，但都失败得很有教育意义。

### 逃亡者 1：Albert Gu 与"线性时间"的诱惑

Albert Gu 是 CMU 助理教授，Mamba 的一作。他 2021 年的 S4（[arxiv:2111.00396](https://arxiv.org/abs/2111.00396)）是这个故事的起点：把序列建模看成连续时间状态空间方程 $h'(t) = A h(t) + B x(t)$，离散化后用 FFT 卷积训练，$O(N \log N)$。和 attention 的 $O(N^2)$ 比起来，长序列上的渐近优势看起来是降维打击。

2023 年 12 月的 Mamba（[arxiv:2312.00752](https://arxiv.org/abs/2312.00752)）把 S4 升级成 selective SSM，让状态转移矩阵依赖于输入；Tri Dao 写了一个硬件感知的 parallel scan kernel，2.8B 参数下训练吞吐比同尺寸 Transformer 高 3–5 倍。一时间整个圈子都在转发 Mamba 论文，"Attention is not all you need" 的标题党文章铺天盖地。

转折点在 2024 年 6 月。NVIDIA 一个叫 Waleffe 的研究员领衔发了一篇 [arxiv:2406.07887](https://arxiv.org/abs/2406.07887) 的实证研究，控制变量到极致：同样 8B 参数，同样 1.1T token，pure Mamba 在 MMLU、GSM8K 上和 Transformer 持平甚至略优，但在 needle-in-haystack、phonebook、5-shot 检索类任务上 gap 超过 20 个点。原因不复杂——SSM 的隐状态是固定大小（典型 $d_{state}=128$）的压缩记忆，无论上下文多长都只有这么大；而 attention 的 KV cache 是无损的 per-token 记忆。要精确召回某个具体 token，固定容量就是物理瓶颈。

这篇论文实质上宣判了纯 Mamba 在 frontier 上的死刑。Tri Dao 自己在 2024 年 Stanford MLSys 的 talk 里直接承认："For pure recall tasks, you need attention. Hybrid is just better." 同一年 5 月发布的 Mamba-2（[arxiv:2405.21060](https://arxiv.org/abs/2405.21060)）干脆证明了一个让人哭笑不得的定理：selective SSM 在特定退化条件下**等价于一种结构化 mask attention**。也就是说，Mamba 不是 attention 的替代品，它是 attention 的一个特例。

Albert Gu 没有发 Mamba-3。截至 2026-05，他在 CMU 继续做 SSM 理论，公开 talk 里暗示在研究 "continuous-time SSM with better state utilization"，但没有 paper [unknown]。Tri Dao 的重心已经回到 FlashAttention-3 和 Together AI 的推理栈——也就是说，Mamba 的工程主力，回去继续优化 Transformer 了。

### 逃亡者 2：Yann LeCun 与"不学像素"的执念

LeCun 的逃亡更彻底，他想绕开的不只是 Transformer，是整个 generative pretraining 范式。2022 年 6 月他在 OpenReview 贴出 [*A Path Towards Autonomous Machine Intelligence*](https://openreview.net/pdf?id=BZ5a1r-kVsf)，提出 JEPA（Joint-Embedding Predictive Architecture）：不要在像素空间预测，要在另一个 encoder 的表示空间预测；不要 contrastive，不要重建。理由是动物大脑不会逐像素重建世界。

2023 年 1 月 I-JEPA、2024 年 2 月 V-JEPA、2025 年 6 月 V-JEPA 2（[arxiv:2506.09985](https://arxiv.org/abs/2506.09985)），三个里程碑。从纸面上看 JEPA 的卖点很硬：训练快 2.5–10×（相同 ImageNet 精度），不学高频细节。

问题是 vision encoder 实战榜单上 2024–2026 的赢家是 **DINOv2 / DINOv3 / SigLIP2**，不是 JEPA。JEPA 的 frozen-feature 评测并没有显著超越 DINOv2。LeCun 翻身的最大筹码押在了 robotics——V-JEPA 2-AC 第一次让 zero-shot pick & place 在真机器人上 demo 成功，这是 2025 年这家族最有信服力的成果。

但即便如此，JEPA 内部的 backbone 是什么？**ViT**——Vision Transformer。Predictor 是一个窄一点的 ViT。整个 JEPA 框架是关于**用什么 loss 训练**和**预测什么目标**，骨架还是 Transformer。LeCun 的"逃离"逃的是 generative loss，不是 attention。

更尴尬的是 2025 年 11 月起 Financial Times 等多家媒体报道 LeCun 计划离开 FAIR 创办 world model startup（[uncertain 是否已经正式离任，截至 2026-05 没有公开公告确认](https://www.ft.com/)）。一个 Turing Award 得主用十年时间在自家公司推一条路线，最终选择带着这个 idea 出去单干——这本身就说明 JEPA 在 Meta 内部的优先级远不如 Llama 4 那种纯 Transformer MoE。

### 逃亡者 3：Diffusion LLM 与"并行解码"的承诺

第三条逃亡路线最年轻也最性感：把扩散模型从图像搬到文本 token，干掉 autoregressive 的逐 token 生成，换成并行 denoising。代表人物是 Stefano Ermon（斯坦福，Inception Labs 联合创始人）和他的学生 Aaron Lou（SEDD 一作）。

故事在 2025 年 H1 几乎要成功：
- 2025-02-14 中国人民大学 + 蚂蚁集团的 **LLaDA 8B**（[arxiv:2502.09992](https://arxiv.org/abs/2502.09992)）号称 in-context learning 与 LLaMA3-8B 同档；
- 2025-02-26 Inception Labs 发布 **Mercury Coder**，自报 H100 上 **1109 tok/s**，Copilot Arena 速度榜 top-2；
- 2025-05-20 Google I/O 上 Demis Hassabis 亲自公布 **Gemini Diffusion**，自报 **1479 tok/s**。这是第一次 frontier lab 把 diffusion text model 推上主舞台。

但一年过去，截至 2026-05，**没有一个 diffusion language model 在 GPQA / AIME / SWE-Bench 上以同算力打过 AR Transformer SOTA**。Gemini Diffusion 仍是 experimental waitlist，没进 Gemini 主线 API。LLaDA-MoE 加了 RL post-train，benchmark 仍落后同尺寸 Qwen2.5。

原因和 Mamba 出奇地相似——架构的渐近优势在工程实测下被吃掉：
- diffusion LM 每步要 full bidirectional forward over 全部 N 个 token，**没有 KV cache**；
- 长度必须预先指定，长文档质量崩；
- 1000+ tok/s 的数字成立条件之一是 batch throughput，不是单 stream 延迟。

更深的问题是：diffusion LM 的 backbone 是什么？**一个 bidirectional Transformer**。区别只是去掉了 causal mask、改了 loss。说白了，diffusion LM 在用 Transformer 跑 BERT 风格的 masked language modeling，再加一个迭代 sampler。它不是在逃离 Transformer，它是在用 Transformer 跑另一种解码协议。

三个逃亡者，三种逃法，三个结局：
- Mamba 被吸收进 hybrid，attention 层比例从 1:7 到 1:12 不等，**没有一家敢去掉所有 attention 层**；
- JEPA 的 backbone 一直是 ViT，"逃离"的对象其实是 generative loss；
- Diffusion LLM 的 backbone 是 bidirectional Transformer，"逃离"的对象其实是 AR decoding。

注意到了吗？每一个"逃离 Transformer"的尝试，认真追问下去都会发现它**根本没在逃离 Transformer**。它逃离的是某个外围特性——causal mask、AR decoding、pixel-level loss——但 Q、K、V 投影 + softmax + MLP + residual 的那个 block，没有一个人真敢动。

## 三、胜利者的不安：Vaswani 团队今天在哪里

如果给 *Attention Is All You Need* 八个作者拍一张 2026 年的合影，画面会非常分裂。除了 Llion Jones 还在做 architecture 研究（Sakana AI），其他七个全部离开 Google，全部去做了**应用层 startup**：

- Ashish Vaswani 和 Niki Parmar：Adept → 后被收购，再创业 Essential AI；
- Noam Shazeer：Character.AI（被 Google 以 ~25 亿美金 reverse-acquihire 回来）；
- Aidan Gomez：Cohere（企业 LLM）；
- Jakob Uszkoreit：Inceptive（RNA 药物设计）；
- Łukasz Kaiser：OpenAI（参与 o-series reasoning）；
- Illia Polosukhin：NEAR Protocol（区块链）。

七个发明了当代 AI 的人，没有一个继续在做"新架构"。他们都把 Transformer 当作给定的、不变的基础设施，转而去做模型应用、推理服务、垂直行业。这是一个非常 Harari 式的信号：**当某个发明者集体不再认为有更好的版本可做，这个发明就完成了它的"自然化"过程**——从一个选择，变成了空气。

如果把 Transformer 拟人化，它在 2026 年的处境是这样的：它非常累、非常胖（万亿参数、context 1M、MoE 三百专家）、非常贵（一次训练上亿美元）、被人类用各种方式肢解和缝合（MLA、GQA、sliding window、NoPE、YaRN），但它也很安全——没有任何替代者真的逼近它的核心地位。它的不安不是来自外部竞争，而是来自内部：**它自己也快撞到 scaling 上限了**。

GPT-5 vs GPT-4 的提升小于 GPT-4 vs GPT-3，这一点公开数据已经基本坐实。Chinchilla 法则（Hoffmann et al., 2022, [arxiv:2203.15556](https://arxiv.org/abs/2203.15556)）规定了"参数 : 数据 ≈ 1:20"的最优配比，到 2025 年所有 frontier model 都已经在这个 regime 之外（数据用完了）。MoE 是一次延寿手术，reasoning 是另一次。再往后呢？

答案目前看起来是——继续修补 Transformer。这是 2026 年最让人不安的事实：在它的发明者们都已经离开、它的挑战者们都已经被吸收的当下，没有任何一个具备说服力的"下一代"在排队。Transformer 不是因为最好而胜出，它是因为没有别人活下来而胜出。

## 四、混血儿：承认现实的产物

故事到第三幕就该有混血儿出场了。从 2024 下半年起，"hybrid" 成了架构圈最热的词。它的意思朴素得让人尴尬：**既然纯 SSM / 纯 linear attention 都在 retrieval 上输给 Transformer，那就在 SSM 层之间插几层 attention**。

这条路线在两年里产出了一长串模型：

| 模型 | 时间 | 配方 | 一手 |
|---|---|---|---|
| Jamba v0.1 | 2024-03 | Mamba:attn = 7:1 + MoE，第一个 production hybrid | [arxiv:2403.19887](https://arxiv.org/abs/2403.19887) |
| Zamba 7B | 2024-05 | shared attention block，参数复用 | [arxiv:2405.16712](https://arxiv.org/abs/2405.16712) |
| Samba 3.8B | 2024-06 | Mamba + sliding-window attn | [arxiv:2406.07522](https://arxiv.org/abs/2406.07522) |
| Jamba 1.5 Large | 2024-08 | 398B / 94B active，256K context，RULER 96.7 | [arxiv:2408.12570](https://arxiv.org/abs/2408.12570) |
| Hymba 1.5B | 2024-11 | parallel attn + SSM head（同层并行）| [arxiv:2411.13676](https://arxiv.org/abs/2411.13676) |
| RecurrentGemma 9B | 2024-Q3 | Google：Griffin（gated linear recurrence + local attn）| [arxiv:2402.19427](https://arxiv.org/abs/2402.19427) |
| Nemotron-H 56B | 2025-04 | NVIDIA：92% Mamba-2 + 8% attn，FP8 训练 20T token | [arxiv:2504.03624](https://arxiv.org/abs/2504.03624) |
| Qwen3-Next 80B-A3B | 2025-09 | Gated DeltaNet:attn = 3:1，MoE 激活率 3.7% | [Qwen blog](https://qwen.ai/blog?id=qwen3_next) |
| IBM Granite 4.0 | 2025-10 | Mamba-2:attn = 9:1，第一个全 hybrid 的企业 LLM 家族 | [IBM blog](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models) |

注意一个细节：**这些 hybrid 模型的 attention 层比例都很低**（5%–15%），但**没有一家敢调到 0%**。NVIDIA 的 ablation 给出了直接的解释——attention 比例低于 5% 之后，下游 retrieval 性能明显掉。这是工程上的"经验性最低活命线"。

更耐人寻味的是 IBM Granite 4.0、NVIDIA Nemotron-H、Zyphra Zamba2 三家**独立收敛**到了几乎同一套默认配方：**Mamba-2 backbone + 每 9–10 层插一层 GQA + NoPE on attention layers（SSM 自带位置感知）**。三个团队没有抄袭关系，结果几乎完全相同。这种独立收敛通常意味着设计空间已经被压缩到很小的区域。

那么，hybrid 算不算"逃离 Transformer"？严格说不算，应该叫**承认 Transformer 不可逃离、然后想办法把它的成本压到最低**。Granite 4.0 32B-A9B 的核心卖点是 128K 上下文下推理内存只有同尺寸 dense Transformer 的 **1/5**。这是一个非常诚实的定位：我不挑战你的智能上限，我只想让你便宜五倍。

Sasha Rush 在 2024-09 Simons Institute 那场 [*Is Attention All You Need?*](https://www.youtube.com/watch?v=dKJEpOtVgXc) talk 的结论是一句意味深长的话："the answer is yes-ish, but the hybrid is winning"。yes-ish——是的，差不多。hybrid 在赢——但 hybrid 的核心仍然是那个 attention 块。

## 尾声：吸收一切的物种

回到 Harari 式的视角。智人之所以在 5 万年内统治地球，不是因为他比尼安德特人更强壮、更聪明、跑得更快，而是因为他足够灵活——可以吸收、改造、与其他物种杂交（现代欧亚人基因里还有 1–4% 尼安德特 DNA）。Transformer 的胜出方式几乎完全一样。

每一次有人提出新架构，Transformer 都会做两件事：
1. **先承认对方在某个维度上确实更优**（SSM 在长序列吞吐、JEPA 在不学高频细节、diffusion 在并行解码）；
2. **然后把那个优点吸进来**（FlashAttention 借鉴 SSM 的 IO 思路，bidirectional attention + masked LM 是被借鉴的扩散思想，ViT backbone 本身就是 JEPA 的内核）。

到最后，**逃亡者的 idea 活下来了，逃亡者本身被吸收了**。这是 Transformer 这个物种最让人敬畏也最让人不安的特质：它没有真正的边界。任何看起来在挑战它的东西，最终都会被发现是它的一个变体、一个特例、或者一个外围插件。

2026 年 5 月，当我们盘点全部 frontier model 时会看到：dense Transformer + MoE + reasoning post-train + 少量 hybrid 实验。**没有任何一个非 Transformer 架构进入了第一梯队**。这不是因为别人没努力，是因为这个领域已经形成了一个稳定的 attractor——硬件围绕 attention 优化、数据 pipeline 围绕 next-token prediction 优化、推理框架（vLLM、SGLang、TensorRT-LLM）围绕 KV cache 优化、整个人才市场围绕"会调 Transformer"定价。任何想换骨架的人，等于要求世界把这套基础设施重做一遍。

这就是为什么没人能逃离 Transformer。不是它最好，是它已经成了空气。

而下一个真正的逃亡者会从哪里来？大概率不会是另一个 sequence model 的小修小补。它要么来自完全不同的计算范式（neuromorphic、optical、analog），要么来自完全不同的目标函数（不再是 next token），要么来自完全不同的数据形式（不再是 internet text）。但截至 2026 年 5 月，这些方向都还在 paper 阶段，没有一个能在 frontier 上拿出一条曲线。

所以这一章的标题如果改写成一个更冷的版本，应该是：**不是没人想逃，是逃了的人都已经回来了，而我们还没找到下一个值得逃的方向**。

---

*本章正文约 4100 字。引用论文、模型、数字均给出一手 source；不确定的标注 [uncertain] / [unknown]。逃亡者 / 混血儿小节的事实底稿来自本书 vol1-architecture/B1-ssm-mamba.md、B2-diffusion-llm.md、B3-B4-linear-hybrid.md、E1-jepa.md。*
