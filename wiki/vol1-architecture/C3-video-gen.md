# 视频生成家族（DiT 路线 frontier，截至 2026-05）

## 路线定位

视频生成的 frontier 自 2024 年 Sora 起统一收敛到 **latent DiT + spatial-temporal full attention**：3D causal VAE 把视频压成 spacetime patches/tokens，再用 transformer 在这些 tokens 上 flow matching / rectified flow 训练。竞争分三圈：(1) 闭源 product-tier（OpenAI Sora/Sora 2、Google Veo 3、Kuaishou Kling 2、MiniMax Hailuo 02）追求物理一致性 + 音视频联合生成；(2) 开源 weights tier（Tencent HunyuanVideo、Alibaba Wan 2.1/2.2、Genmo Mochi）追赶质量并占领可微调生态；(3) "world model" 路线（NVIDIA Cosmos、Genie 3、Wayve GAIA-2）名义上是视频生成，但目标是 robot/AV policy 训练——**本节只覆盖以视频本身为产品的家族，world model 路线归到 E3**。Meta Movie Gen（2024-10 paper）发了 paper 但 weights/产品都未公开发布，作为架构 reference 在此一并讨论。

## 代表模型清单

| 模型 | 发布日 | 参数 | 关键变化 | 一手 source |
|---|---|---|---|---|
| Sora (v1) | 2024-02 (preview) / 2024-12 (GA) | [unknown] | 首个 spacetime patch DiT，最长 60s 1080p | [Video generation models as world simulators][^sora1] |
| Sora 2 | 2025-09-30 | [unknown] | 同步生成音频+对白，物理一致性大幅提升；社交 app 模式 | [Sora 2 launch][^sora2] |
| Veo 3 | 2025-05-20 (I/O) | [unknown] | 原生音频（对话/SFX/音乐）；1080p 8s | [Veo 3 announcement][^veo3] |
| Veo 3.1 | 2025-10 | [unknown] | 更强 prompt adherence、image-to-video、scene extension | [Veo 3.1 update][^veo31] |
| Kling 1.0 | 2024-06 | [unknown] | 首个国产可用 product-tier，DiT + 3D VAE | [Kling 官方][^kling1] |
| Kling 2.0 / 2.1 Master | 2025-04 / 2025-06 | [unknown] | "ultra-precise semantic responsiveness"，1080p 10s | [Kling 2.0 blog][^kling2] |
| Hailuo 02 (MiniMax) | 2025-06 | [unknown] | NCR (Noise-aware Compute Redistribution) 架构，1080p 10s | [Hailuo 02 page][^hailuo02] |
| HunyuanVideo | 2024-12-03 | **13B** | 当时最大开源 video DiT，dual-stream→single-stream transformer | [arXiv 2412.03603][^hunyuan] |
| HunyuanVideo-I2V | 2025-03 | 13B | image-to-video 版 | [HunyuanVideo-I2V repo][^hunyuan-i2v] |
| Wan 2.1 | 2025-02-25 | 1.3B / 14B | Alibaba 开源，T2V/I2V，支持中英文字幕渲染 | [Wan 2.1 report][^wan21] |
| Wan 2.2 | 2025-07 | 5B (dense) / 27B (A14B MoE) | 首个开源 video MoE，high-noise expert + low-noise expert | [Wan 2.2 GitHub][^wan22] |
| Movie Gen (Meta) | 2024-10-04 (paper) | **30B** video + 13B audio | flow matching DiT，paper 公开但 weights 未放出 | [Movie Gen paper][^moviegen] |
| Cosmos Predict / Transfer | 2025-01 (CES) / 2025-03 update | 4B / 12B / 14B | "world foundation model"，开源 weights；diffusion + autoregressive 两条 | [Cosmos paper][^cosmos] |

## 架构核心

### 共同骨架：latent DiT on spacetime tokens
所有上述模型在结构上是同一个三段式：

1. **3D causal VAE**：把 RGB video `[T,H,W,3]` 压到 `[t,h,w,c]`，典型压缩比 4×8×8 (Sora/HunyuanVideo/Wan)。causal 是为了 streaming——第 t 帧只依赖前帧[^sora1][^hunyuan]。
2. **patchify → spacetime tokens**：把 latent 切成 `p_t × p_h × p_w` 的 3D patch（Sora 称 "spacetime patches"，HunyuanVideo `p=(1,2,2)`，Wan `(1,2,2)`）[^sora1][^hunyuan][^wan21]。
3. **transformer backbone with full 3D attention**：spatial 和 temporal 维度 flatten 到同一序列做 full attention，这是相对 2024 前 "spatial attention + temporal attention 分离"（AnimateDiff、SVD）的关键变化。Sora 技术 report 明说 "we represent videos as collections of patches… this is a highly-scalable and effective representation"[^sora1]，但具体 attention pattern 未披露。HunyuanVideo paper 写得最细：前 N 层 dual-stream（text/video 分支独立但 cross-attend），后 M 层 single-stream（concat 后 full self-attn）——与 Flux 的 MMDiT 同构[^hunyuan]。

### 训练目标：rectified flow / flow matching 取代 DDPM
- Sora 1 时仍倾向 DDPM-style noise prediction[^sora1]；2024 下半年起整个 frontier 切到 **rectified flow / flow matching**：HunyuanVideo[^hunyuan]、Wan 2.x[^wan21][^wan22]、Movie Gen[^moviegen]、Cosmos[^cosmos] 均明确写 flow matching loss `‖v_θ(x_t,t) − (x_1 − x_0)‖²`。这是 SD3/Flux 在图像端验证后向视频迁移的直接结果。
- **logit-normal timestep sampling**（SD3 引入）几乎所有开源 video DiT 都沿用[^hunyuan][^wan21]。

### 文本条件：从 CLIP 到 decoder LLM
- Sora 用了 GPT 改写 prompt 但 text encoder 未披露[^sora1]。
- HunyuanVideo 用 **MLLM (decoder-only)** 做 text encoder，论证 decoder LM 的 instruction-following 比 T5/CLIP 强[^hunyuan]。
- Wan 2.1 用 **umT5** (multilingual)，支持中英 prompt 与字幕渲染[^wan21]。
- Movie Gen 用 **MetaCLIP + ByT5 + Llama-3 text features** 多源融合[^moviegen]。

### 关键家族差异
- **Wan 2.2 MoE**：业界首个 video DiT MoE，把 denoising 过程按 SNR 切两段，**high-noise expert** 处理早期粗结构、**low-noise expert** 处理后期细节，激活 14B / 总 27B[^wan22]。这是 video 端对 timestep-conditioned MoE 的首次开源落地。
- **HunyuanVideo dual→single stream**：前几层 text/video 双流分别 self-attn 再 cross，后段合并 full attention——与 Flux 同构但首次在 13B video 规模 scale up[^hunyuan]。
- **Movie Gen "factorized" 1D temporal + 2D spatial 全替换为 full 3D**，paper 明确做 ablation 证明 full 3D 远胜分离[^moviegen]。
- **Sora 2 / Veo 3 音视频联合**：官方 blog 都说"同一模型同步生成视频与对应音轨"，但**架构细节未披露**。可能是 token-interleave（参考 Movie Gen 的 audio 13B 独立 model + condition on video latent[^moviegen]）也可能是 joint latent，OpenAI/Google 均未发 paper [推测]。
- **Cosmos 双路线**：发布 **Cosmos-Predict (diffusion)** 与 **Cosmos-Predict-AR (autoregressive on discrete video tokens)** 两条，后者用 transformer LM 在 FSQ 离散 token 上 next-token——这是当前唯一在 frontier 开源的 AR video 路线[^cosmos]。

## 训练规模（已披露的）

| 模型 | 参数 | 训练数据 | 算力 |
|---|---|---|---|
| Sora 1/2 | [unknown] | [unknown] | [unknown] |
| Veo 3 | [unknown] | [unknown] | [unknown] |
| Kling 2 | [unknown] | [unknown] | [unknown] |
| Hailuo 02 | [unknown] | [unknown] | [unknown] |
| HunyuanVideo | 13B | "billions of images and millions of videos"（具体数 [unknown]）[^hunyuan] | [unknown] |
| Wan 2.1 | 14B | 1.5B image + image-video pairs 规模 [uncertain] | [unknown] |
| Wan 2.2 | 27B MoE / 14B activated | 相对 2.1 增加 65.6% 图像、83.2% 视频[^wan22] | [unknown] |
| Movie Gen Video | 30B | **O(100M) videos + O(1B) images**，详细 data pipeline 章节[^moviegen] | 6144 H100 训练 [^moviegen] |
| Movie Gen Audio | 13B | ~1M hours audio[^moviegen] | 同上集群 |
| Cosmos | 4B / 12B / 14B | **20M hours video → 100M clips → 9000T tokens**[^cosmos] | 10000 H100 × 3 months[^cosmos] |

闭源 product tier 全部不披露任何训练数。Movie Gen 是当前最完整的 first-party 报告，Cosmos 是 NVIDIA 给出最完整 token 数的 video FM。

## 与 eval / benchmark 的接口

### VBench 仍是事实标准
**VBench**（PKU-Shanghai AILab，2024 CVPR）把视频生成质量拆 16 个维度（subject consistency、motion smoothness、aesthetic quality、object class、spatial relationship、scene、…），是当前唯一被广泛对比的 benchmark[^vbench]。**VBench-2.0**（2025-03）加入物理合理性、commonsense reasoning 维度[^vbench2]。

公开榜上的关键数据点（截至 2026-05 leaderboard 抓取）：
- HunyuanVideo paper 自报 VBench total 83.24，超过当时所有开源[^hunyuan]。
- Wan 2.1 / 2.2 在 VBench 上交替占据开源第一[^wan21][^wan22]。
- 闭源（Sora 2、Veo 3、Kling 2、Hailuo 02）的 VBench 分数主要由 **VBench team 自己 benchmark** 或第三方（如 Artificial Analysis Video Arena）评测，**模型方官方很少正式 report VBench**——这与图像/语言模型不同，反映视频领域 product tier 更看 **人评 ELO Arena**（Artificial Analysis、LMArena Video）。
- Sora 2 launch blog 不报任何数值，只展示样例视频[^sora2]；Veo 3 blog 同理[^veo3]。

### 第三方独立评测
- **Artificial Analysis Video Arena**：用户盲投 ELO。截至 2026-05，Veo 3.1 / Sora 2 / Kling 2.1 Master 长期占据前三，Wan 2.2 是开源最高[^aa-video]。
- **VBench leaderboard**：开源模型分数普遍高于闭源，部分原因是开源模型针对 VBench dimension 做了对齐/过拟合 [推测]。

### Contamination / overfit 信号
- VBench 用固定 prompt suite，发布时间早于多数当前模型，存在**显式 prompt-level 训练时见过**的可能。VBench-2.0 部分缓解但 prompt 仍公开。
- HunyuanVideo / Wan 系列在 VBench 报数显著高于人评 Arena 排名，提示**对齐 VBench dimension** 的 RLHF/SFT 倾向 [推测]。

## 未知与争议

1. **Sora / Veo / Kling / Hailuo 全员不披露**：参数量、训练数据小时数、算力、tokenizer、text encoder 选型、是否 MoE，统统 [unknown]。Sora 1 那篇 technical report 是 OpenAI 在视频侧迄今最详细的公开材料，但也不含上述任一数字[^sora1]。
2. **"音视频 joint" 实现**：Sora 2 / Veo 3 是端到端单 transformer 还是 video DiT + audio model 后融合，无一手 source。
3. **Sora 是不是 "world simulator"**：OpenAI 原报告标题 "Video generation models as world simulators"[^sora1] 引发大量讨论。Yann LeCun（2024-02 X）直接反驳："generating mostly realistic-looking videos from prompts does not indicate that a system understands the physical world"[^lecun-sora]。本节立场：**Sora/Veo/Kling/Hailuo/HunyuanVideo/Wan/Movie Gen 都是"以视频为产品输出"的生成模型**，与"以视频为 latent 训练 robot policy"的 world model（Cosmos、Genie 3、V-JEPA 2）是两件事，后者见 E3。Cosmos 出现在本表是因为它**同时**作为视频生成 FM 发布了 weights+API。
4. **数据来源**：所有家族对训练数据来源（是否含 YouTube、是否含版权内容）都极度回避。NYT 诉 OpenAI 等案件中 Sora 训练数据是 discovery 焦点之一，截至 2026-05 仍未庭审[^nyt-suit]。
5. **Scaling law**：视频侧没有公开的 chinchilla-style scaling law paper。Sora 报告里有一张 "base/4x/16x compute" 的样本质量对比图但**无定量曲线**[^sora1]。

## 推荐外部材料

- [Sora technical report](https://openai.com/index/video-generation-models-as-world-simulators/) — frontier 视频侧第一份且唯一一份 OpenAI 公开材料，必读。
- [HunyuanVideo paper (arXiv 2412.03603)](https://arxiv.org/abs/2412.03603) — 当前最详细的开源 13B video DiT tech report，是理解 Sora-style 架构最具体的代理。
- [Movie Gen paper](https://ai.meta.com/static-resource/movie-gen-research-paper) — Meta 92 页 paper，data/architecture/eval 章节是教科书级，可惜 weights 未放。
- [Wan 2.2 GitHub](https://github.com/Wan-Video/Wan2.2) — 首个开源 video MoE，high/low-noise expert 设计值得读 inference code。
- [VBench paper (CVPR 2024)](https://arxiv.org/abs/2311.17982) + [VBench-2.0](https://arxiv.org/abs/2503.21755) — 视频 eval 设计哲学，对照自己设计 Qwen-VL video eval 时可直接借鉴 dimension 拆解。
- [Cosmos paper (arXiv 2501.03575)](https://arxiv.org/abs/2501.03575) — NVIDIA 把 video FM 当 world model 卖的最完整白皮书，data pipeline 章节披露的 token 规模目前是 video 侧最大公开数。
- [Lilian Weng — Diffusion Models for Video Generation (2024-04)](https://lilianweng.github.io/posts/2024-04-12-diffusion-video/) — 综述 2024 上半年 video diffusion 演进，DiT 之前的 baseline 都在这。

[^sora1]: https://openai.com/index/video-generation-models-as-world-simulators/
[^sora2]: https://openai.com/index/sora-2/
[^veo3]: https://deepmind.google/technologies/veo/veo-3/
[^veo31]: https://blog.google/technology/google-deepmind/veo-3-1/
[^kling1]: https://kling.kuaishou.com/
[^kling2]: https://app.klingai.com/global/release-notes
[^hailuo02]: https://hailuoai.video/
[^hunyuan]: https://arxiv.org/abs/2412.03603
[^hunyuan-i2v]: https://github.com/Tencent/HunyuanVideo-I2V
[^wan21]: https://github.com/Wan-Video/Wan2.1
[^wan22]: https://github.com/Wan-Video/Wan2.2
[^moviegen]: https://ai.meta.com/static-resource/movie-gen-research-paper
[^cosmos]: https://arxiv.org/abs/2501.03575
[^vbench]: https://arxiv.org/abs/2311.17982
[^vbench2]: https://arxiv.org/abs/2503.21755
[^aa-video]: https://artificialanalysis.ai/text-to-video
[^lecun-sora]: https://x.com/ylecun/status/1758740106955952191
[^nyt-suit]: https://nytco-assets.nytimes.com/2023/12/NYT_Complaint_Dec2023.pdf
