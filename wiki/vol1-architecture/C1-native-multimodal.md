# Native / Early-Fusion Multimodal LLM

## 路线定位

这一节关心的不是\"多模态 LLM 怎么做\"的全景（那是单独一卷），而是 **early-fusion / native multimodal** 这一条具体技术路线：**文本 / 图像 / 音频（/ 视频）共享同一 transformer backbone，从 pretrain 第一步就被同一组 loss 训出来，token 序列里几种模态可以任意 interleave**。它和占据多数生态位的 **adapter / late-fusion** 路线（CLIP-style vision encoder + projector + 冻结 LLM，代表是 LLaVA / InternVL / 早期 Qwen-VL / GPT-4V）形成对照。2024-05 的 GPT-4o 和 Chameleon 把这条路线推到 frontier 视野，2025 的 Gemini 2.x / Qwen2.5-Omni / Qwen3-Omni 把它做成了产品级 omni 模型，到 2026-05 它已经是 **frontier 闭源（GPT-5o, Gemini 3）的默认形态、开源里 Qwen-Omni 系一家独大**的局面。

## 代表模型清单

| 模型 | 发布日 | 模态 in / out | 早融合关键点 | 一手 source |
|---|---|---|---|---|
| Chameleon 7B / 34B | 2024-05-16 (paper) | text+image in/out | 图像→VQ token，与 text token 拼成单一序列，单 transformer + 单 softmax | [arxiv:2405.09818](https://arxiv.org/abs/2405.09818) |
| GPT-4o | 2024-05-13 | text+audio+image in / text+audio+image out | 官方称 \"single new model end-to-end across text, vision and audio\"；音频延迟 320ms | [openai.com/index/hello-gpt-4o](https://openai.com/index/hello-gpt-4o/) |
| Gemini 1.0 / 1.5 | 2023-12 / 2024-02 | text+image+audio+video in | tech report 明写 \"trained jointly\"，video 按帧 + audio track tokenize 进同一序列 | [arxiv:2312.11805](https://arxiv.org/abs/2312.11805), [arxiv:2403.05530](https://arxiv.org/abs/2403.05530) |
| Anole 7B | 2024-07-08 | text+image in/out | Chameleon-7B 基础上**只 fine-tune image head**，恢复 image generation（Meta 放出的 Chameleon 把图像生成头阉割了） | [arxiv:2407.06135](https://arxiv.org/abs/2407.06135) |
| Gemini 2.0 Flash (native image gen) | 2024-12 / 2025-03 (public) | + native image out | image gen 内置 backbone，不再走外挂 Imagen | [blog 2025-03](https://developers.googleblog.com/en/experiment-with-gemini-20-flash-native-image-generation/) |
| Qwen2.5-Omni 7B | 2025-03-27 | text+image+audio+video in / text+audio out | \"Thinker–Talker\" 双 head + TMRoPE 时间对齐音视频；single end-to-end model | [arxiv:2503.20215](https://arxiv.org/abs/2503.20215) |
| GPT-4o image gen (\"4o image\") | 2025-03-25 | + native image out | 把 4o 的图像 head 真正打开，autoregressive image token；DALL·E 体系退役 | [openai.com/index/introducing-4o-image-generation](https://openai.com/index/introducing-4o-image-generation/) |
| Gemini 2.5 Flash Image (\"Nano Banana\") | 2025-08-26 | text+image in / image out | 与 2.5 同 lineage 的图像专用 ckpt | [blog 2025-08-26](https://blog.google/technology/google-deepmind/gemini-2-5-flash-image/) |
| Qwen3-Omni 30B-A3B (MoE) | 2025-09-22 | 全模态 in / text+audio out；119 lang text / 19 in speech / 10 out speech | MoE Thinker + MoE Talker；audio 用 multi-codebook (MTP-style) 解码降延迟 | [arxiv:2509.17765](https://arxiv.org/abs/2509.17765), [qwenlm.github.io 2025-09-22](https://qwenlm.github.io/blog/qwen3-omni/) |
| GPT-5o (omni 线) | 2025-?? → 2026 | 全模态 in/out，realtime voice 整合 | [uncertain] OpenAI 是否仍把 omni 单列 SKU，2026-05 主线 GPT-5 / GPT-5.1 已 native multimodal | [unknown — 没找到 GPT-5o 独立 system card；见 GPT-5 system card](https://openai.com/index/gpt-5-system-card/) |
| Gemini 3 Pro / Deep Think | 2025-11-18 | 全模态 in，image+text out | 延续 native multimodal lineage | [blog 2025-11-18](https://blog.google/products/gemini/gemini-3/) |

> 说明：表里**不收** LLaVA / InternVL / MiniGPT / Qwen-VL（adapter 路线）、不收 Whisper+LLM pipeline（cascade）。把 Qwen2-VL / Qwen2.5-VL 也算 adapter 路线（用 ViT encoder + MLP projector + LLM），Qwen-Omni 才是 Qwen 系第一个真正 early-fusion 产品。

## 架构核心

### Early fusion 的定义（本节口径）
我们这里用三条硬标准判定是否 early-fusion，避免和\"natively multimodal\" 这类 marketing 词混淆：
1. **单 backbone**：所有模态共享同一组 transformer 权重，**不是 frozen LLM + 旁挂 encoder**。
2. **token-level 同序列**：非文本模态被离散化（VQ / RVQ / codec / patch token）后与 text token 拼成一条 sequence，attention 跨模态自由流动。
3. **从 pretrain 起就联合训练**（不是 SFT 阶段才接进来）。

按这个标准：Chameleon / GPT-4o / Gemini / Qwen-Omni 满足；LLaVA / Qwen2.5-VL / InternVL 不满足；Flamingo（cross-attention adapter）也不满足。Gemini 2.0/2.5 的 image gen 头算满足条件 1+2，pretrain 是否联合训 image-gen [uncertain]，但 input 侧肯定是 early fusion。

### Chameleon（最清晰的开盒样本）[^cham]
- **统一离散 tokenizer**：image tokenizer 是一个 VQ-VAE（codebook 8192），把 512×512 图压成 1024 个 token；文本用 BPE 65536；两个词表 concat 成 union vocab。
- **单一 transformer + 单一 softmax**：next-token-prediction loss 在 union vocab 上算，模型自己学会什么时候出 image token 什么时候出 text token。
- **训练稳定性问题**：paper §3 花了大段讲早融合在 7B+ 规模会出现 logit drift / softmax 爆炸，解决方法是 **QK-Norm + dropout + z-loss + 调整 norm 位置**。这套\"早融合稳定 trick\"后来被 Anole / Qwen-Omni 部分继承。
- **训练数据 4.4T token**（其中 image-only 1.4T, image-text 1.5T, text 1.4T），7B 用 856K H100-hour。
- **Meta 发布时阉割 image generation head**（safety），所以社区拿到的 Chameleon 实际只能做 vision understanding。Anole 用 ~6K 样本就把 image head 微调回来了，证明 backbone 自身保留了生成能力。

### GPT-4o
- 官方 blog 的关键句：**\"GPT-4o (\"o\" for \"omni\") ... we trained a single new model end-to-end across text, vision, and audio, meaning all inputs and outputs are processed by the same neural network.\"** [^4o]
- 没有 paper，没有 tech report，没有 system card 级架构图。架构细节几乎全是 [推测]。能确定的只有：（a）单一模型；（b）音频是直接 token in / token out（不是 Whisper → GPT → TTS pipeline），证据是 320ms 平均响应延迟（接近人类对话）和\"能听到笑声 / 多人声 / 唱歌\"这类 paralinguistic 信号。
- image gen 头在 2025-03-25 才真正开放（[\"Introducing 4o image generation\"](https://openai.com/index/introducing-4o-image-generation/)），写明 \"natively multimodal model capable of generating images\"；text-in-image 渲染、instruction following 比 DALL·E 3 强一大档，强烈暗示是 autoregressive image token 而不是 diffusion（[Tang et al. 2025 \"How GPT-4o Generates Images: A First Look\"](https://arxiv.org/abs/2504.02782) 做了第三方逆向分析，结论 [推测] autoregressive token + 后接 lightweight diffusion decoder）。

### Gemini 1.0 / 1.5 / 2.x / 3
- 1.0 tech report §2 明写 early fusion[^gem10]，1.5 paper 进一步把 video / 长 audio 加进同一序列。
- Native image gen（2.0 Flash 开始）：与 GPT-4o image gen 同期出现，Google 称 \"native image generation\"，与 Imagen 是不同 lineage。2.5 Flash Image 是同 backbone 的 image-heavy ckpt。
- Audio dialog：2.0 Flash 起有 native audio in/out，2.5 Live API 双向低延迟，路线和 GPT-4o realtime 对位。
- 详细的 Gemini 架构 / 长上下文 / MoE 讨论见 [A3-gemini.md](./A3-gemini.md)，这里不重复。

### Qwen2.5-Omni（开源 early-fusion 的第一个产品级）
- **Thinker–Talker 架构**[^qomni25]：Thinker 是主 LLM（基于 Qwen2.5 7B），输入端把 image / video / audio 都 tokenize 后 concat 进同一序列；Talker 是一个**与 Thinker 共享 hidden state** 的轻量 decoder，专门生成 audio token（基于 Qwen 自家 codec），从而实现 streaming voice out。
- **TMRoPE（Time-aligned Multimodal RoPE）**：处理 video+audio 时间同步问题——video 帧和 audio chunk 各自带绝对时间戳，RoPE 维度被切成 (time, height, width, text) 四段，让模型能对齐 \"第 3.2 秒说了什么\" 与 \"第 3.2 秒画面里发生了什么\"。这是 Qwen-Omni 区别于 GPT-4o / Gemini 的最关键公开技术点。
- **真 end-to-end**：input 侧 vision encoder 仍存在（Qwen2.5-VL 的 ViT），但它的输出 feature 直接被当作 visual token 喂进 LLM、**在 pretrain 阶段联合训练**，不是 frozen + adapter。按我们前面的 early-fusion 三条标准，算满足条件 1（联合训练）+ 2（同序列）+ 3（pretrain 阶段就接），第 1 条\"完全同一组权重\" 部分例外（vision encoder 是独立小模块）。所以严格说 Qwen2.5-Omni 是 **\"deep-fusion\" 而不是像 Chameleon 那种 \"pure token-level early-fusion\"**。这条区别读者团队评测 omni 时要注意。
- Output 侧 audio：Talker 输出 codec token，外接一个 streaming codec decoder（Qwen 自训）合成波形。延迟分摊到 chunk-level，可做到 ≤300ms 首音。

### Qwen3-Omni[^qomni3]
- 2025-09-22 发布，30B-A3B MoE（30B 总参，激活 3B），同时放出 dense Captioner 变体。
- 架构上沿用 Thinker–Talker，但**两边都换成 MoE**；Talker 改用 **multi-codebook (类似 MTP) 并行预测多个 codec stream**，把首音延迟降到官方 report 的 211ms（cold）/ 1.5×参数下不退化。
- 文本能力官方声称\"与同尺寸纯文本 Qwen3 持平\"——这是 omni 路线长期被质疑的痛点（多模态 pretrain 是否拖累文本 reasoning），Qwen3-Omni 给出的反驳数据见 tech report §5。**第三方独立复现：[unknown — 2026-05 没有看到独立 benchmark 系统对比 Qwen3-Omni vs Qwen3-30B-A3B 纯文本侧]**。
- 支持 119 种文本语言、19 种语音输入、10 种语音输出，是当前 open-weight 里 coverage 最广的 omni。
- License：Apache-2.0（与 Qwen3 系一致）。

### Anole（开源最小可复现样本）[^anole]
- 在 Chameleon-7B 上用 ~6K image-text interleaved 样本、只解冻 image-related output head（\"transformer logits over image-token IDs\"那一段），就让 Chameleon 恢复 image generation 能力。
- 价值在于**证明早融合 backbone 的能力是真的潜伏在权重里，head 阉割是个浅层 patch**；同时它是目前能在单卡跑、最接近\"看 GPT-4o image gen 怎么做\" 的开源样本。
- 局限：仍然是 Chameleon 时代的能力上限，图质量、指令跟随都被 2025 年标准甩开。

## 训练方法核心

### Pretrain 阶段
- **数据混合**：early-fusion 模型的 pretrain data 通常是 \"text + image-text pair + image-only + (audio + video)\" 多桶 sampling。Chameleon 给了精确比例（见上），GPT-4o / Gemini / Qwen-Omni 都没给精确数字。
- **Tokenizer 设计**：
  - 图像：VQ-VAE / VQ-GAN / RVQ。Chameleon 用 8192 codebook，Qwen-Omni 用 ViT feature → projector（不是离散 VQ）。GPT-4o image gen [推测] 用某种离散 token（autoregressive 形态推出）。
  - 音频：codec token 是主流。GPT-4o [推测] 自家 codec；Qwen-Omni 自训 codec（report 里有架构图但没放 codebook size）。
  - **vocab 拼接**：Chameleon 是 union vocab + 单 softmax；Qwen-Omni 是 text vocab + 独立 audio decoder head。这是\"硬早融合\" vs \"软早融合\"的标志性区别。
- **稳定性 trick**（早融合规模化的核心难点）：
  - **QK-Norm**：Chameleon §3.1 强调；Qwen-Omni 也用。
  - **z-loss**（softmax over union vocab 时 logit drift）：Chameleon 用。
  - **norm 位置调整**：Chameleon 把 post-norm 换成特殊位置，paper 有详述。
  - 这些 trick 现在被 2025 年的 \"如何稳定 train early-fusion\" 当成 baseline，[Sebastian Raschka 2024-06 Chameleon 拆解](https://magazine.sebastianraschka.com/p/research-papers-in-may-2024) 写得很清楚。

### Mid-train / Annealing
- Qwen2.5-Omni report §3 描述了\"先文本-image 联合 pretrain → 加入 audio → 加入 video + TMRoPE → cooldown\" 的阶段化流程。Qwen3-Omni 类似但量级放大。
- GPT-4o / Gemini 完全没披露。

### Post-train
- **SFT**：interleaved instruction 数据，覆盖 \"看图回答 / 听音回答 / 看视频回答 / 多轮跨模态\"。
- **RLHF/RLAIF**：Gemini 1.0 tech report §5.2 提及，4o / Omni 系列没单独写。
- **RLVR**：math / code / speech recognition WER 这种可验证 reward 在 Qwen3-Omni 训练里被使用（report §4.3 提 \"verifiable rewards\"）。
- **Voice 后训练**：GPT-4o realtime 的笑声 / 唱歌 / 情感语气几乎肯定来自专门的 voice SFT 数据，OpenAI 未披露规模。

### 算力披露
- Chameleon-7B: 856K H100-hour（paper §3）；34B 没公开 hour 数。
- GPT-4o / Gemini / Qwen-Omni：均未披露 FLOPs。

## 与 eval / benchmark 的接口

- **Image understanding**：MMMU, MMBench, MathVista, ChartQA — 这些 bench 早融合和 adapter 模型都报，可直接对比。Qwen2.5-Omni / Qwen3-Omni report 上 MMMU 与 Qwen2.5-VL 同级，证明早融合**没有 understanding 上的代价**（争议见下）。
- **Image generation**：GenEval, DPG-Bench, T2I-CompBench。GPT-4o image gen / Gemini 2.5 Flash Image / Qwen-Image 是当前 frontier，Chameleon / Anole 完全跟不上。
- **Audio**：ASR 上 LibriSpeech / Common Voice WER；speech-to-speech 上还没有大家都认的 bench（一个公开的尝试是 [VoiceBench 2024](https://arxiv.org/abs/2410.17196)，Qwen-Omni 系列在它上面 SOTA open-weight）。
- **Video**：Video-MME, MVBench, LongVideoBench。Gemini 1.5 / 2.5 是 closed-source 标杆，Qwen3-Omni 是开源标杆。
- **Omni / cross-modal**：还没有 saturate-resistant 的统一 bench。OpenAI 在 4o blog 里给的\"M3Exam\" 之后没什么人用。**这是 omni 评测的真空地带**，读者要做 omni eval 是有空间的。
- **Contamination / 复现疑点**：
  - Qwen-Omni 的 ASR 数字（LibriSpeech test-clean WER < 2%）和最强 ASR 专用模型接近，[推测] 训练里包含 LibriSpeech 同分布数据，但 Qwen 团队没确认。
  - Chameleon paper 自报的 image-text interleaved 能力没有第三方独立复测过（社区跑的是 Anole 版本）。

## 未知与争议

- **\"native\" 这个词被 marketing 严重滥用**：OpenAI 用 native 指 GPT-4o（单模型），Google 用 native 指 Gemini（pretrain 起 joint），Meta 用 unified token 指 Chameleon。三家具体实现可能完全不同。读者遇到\"native multimodal\"四个字时务必追到一手 paper / blog 看实现是 \"union vocab + 单 softmax\" 还是 \"shared backbone + 独立 head\" 还是 \"shared backbone + frozen encoder\"。
- **早融合是否伤文本能力**：Chameleon 7B 文本 bench 明显落后同期 Llama 2 7B（paper 自己也承认）；Qwen3-Omni report 反驳称\"持平 Qwen3 30B-A3B 纯文本\"。**这是 omni 路线最大的开放问题**，[uncertain] 是数据 mix / scale 解决了，还是 bench 选择性披露。Sebastian Raschka 在 [2025-10 LLM 路线综述](https://magazine.sebastianraschka.com/) 里把这条列为\"open question\"。
- **GPT-4o / GPT-5o 架构**：完全黑盒，没有 paper、没有 tech report，连参数量级都没披露过。所有 4o 相关\"架构图\" 都是第三方逆向。
- **Image gen 是 AR token 还是 diffusion**：GPT-4o image gen 官方只说 \"natively multimodal\"。[Tang et al. 2025](https://arxiv.org/abs/2504.02782) [推测] 是 AR token + diffusion decoder hybrid，[Bytedance 团队 2025 BAGEL paper](https://arxiv.org/abs/2505.14683) 实现了类似结构并公开，可作旁证。Gemini 2.5 Flash Image [unknown]。
- **Early-fusion 会不会被 adapter 路线吃回去**：2024 时大家以为 adapter（Qwen-VL 系）注定胜出（便宜、文本不退化），2025 frontier 全转 early-fusion 后这个判断被推翻；但开源生态里 adapter 模型（InternVL3, Qwen2.5-VL）仍是绝对主流，omni 只是\"上层一支\"。2026-05 看，**adapter 仍占大部分 vision LLM 部署份额，early-fusion 主要在 voice / image-gen / 真 omni 场景才被需要**。
- **离散 token vs 连续 feature**：Chameleon (VQ 离散) vs Qwen-Omni (ViT 连续 feature)。前者理论更\"纯\" early-fusion、易做生成；后者保留更高的 understanding 信噪比。学界这俩路线都有人推，未收敛。

## 推荐外部材料

- [Chameleon paper (arxiv:2405.09818)](https://arxiv.org/abs/2405.09818) — 唯一一篇把 early-fusion 训练稳定性 trick 写清楚的公开 paper，必读。
- [GPT-4o launch blog](https://openai.com/index/hello-gpt-4o/) + [4o image generation blog](https://openai.com/index/introducing-4o-image-generation/) — OpenAI 关于 4o 的全部一手信息，加起来不到 5 页。
- [Qwen2.5-Omni tech report (arxiv:2503.20215)](https://arxiv.org/abs/2503.20215) — Thinker–Talker + TMRoPE 的 reference 实现，开源里讲得最细的 omni paper。
- [Qwen3-Omni tech report (arxiv:2509.17765)](https://arxiv.org/abs/2509.17765) + [qwenlm.github.io 2025-09-22](https://qwenlm.github.io/blog/qwen3-omni/) — MoE Omni 的工程落地。
- [Anole paper (arxiv:2407.06135)](https://arxiv.org/abs/2407.06135) — 6K 样本恢复 Chameleon image gen，验证早融合 backbone 能力的最小成本实验。
- [Gemini 1.0 tech report (arxiv:2312.11805)](https://arxiv.org/abs/2312.11805) §2 — early fusion 描述的奠基段落。
- [Tang et al. 2025 \"How GPT-4o Generates Images\" (arxiv:2504.02782)](https://arxiv.org/abs/2504.02782) — 第三方对 4o image gen 的逆向分析，可作[推测]来源。
- [BAGEL paper (arxiv:2505.14683)](https://arxiv.org/abs/2505.14683) — Bytedance 公开的 AR-token + diffusion-decoder unified model，是看\"open-source GPT-4o image gen\"的合理参考实现。
- [Sebastian Raschka, \"Multimodal LLM landscape 2025\"](https://magazine.sebastianraschka.com/) — 季度复盘里 early-fusion vs adapter 的对比表，最新一期到 2026-Q1。
- [Lilian Weng \"Generalist Multimodal\" 2024](https://lilianweng.github.io/posts/2022-06-09-vlm/) — 旧但概念框架清楚，配合上面的 paper 一起读校准术语。

[^cham]: Chameleon paper §2-3 — 详述 unified VQ tokenizer (8192 codebook, 1024 tokens / 512² image) + QK-Norm / z-loss 稳定性 trick + 4.4T pretrain tokens。 https://arxiv.org/abs/2405.09818
[^4o]: GPT-4o launch blog — \"with GPT-4o, we trained a single new model end-to-end across text, vision, and audio, meaning that all inputs and outputs are processed by the same neural network.\" https://openai.com/index/hello-gpt-4o/
[^gem10]: Gemini 1.0 tech report §2 — \"trained to accommodate textual input interleaved with a wide variety of audio and visual inputs ... and can produce text and image outputs.\" https://arxiv.org/abs/2312.11805
[^qomni25]: Qwen2.5-Omni tech report §2 — Thinker–Talker 架构 + TMRoPE（time-aligned RoPE 把 RoPE 维度按 time/H/W/text 分段）。 https://arxiv.org/abs/2503.20215
[^qomni3]: Qwen3-Omni tech report — MoE Thinker + MoE Talker + multi-codebook 并行 audio decoding；首音延迟 211ms；119/19/10 多语支持。 https://arxiv.org/abs/2509.17765
[^anole]: Anole paper — 在 Chameleon-7B 上 ~6K 样本只 fine-tune image output head 即恢复 image generation 能力。 https://arxiv.org/abs/2407.06135
