# Adapter-based VLM 家族（2025-2026 active lines）

> **范围**：本节只覆盖\"独立 vision encoder + 轻量 connector + 预训练 LLM backbone\" 这条路线（即 LLaVA-style adapter VLM），不覆盖 native multimodal early-fusion（Gemini / GPT-4o 路线，那条留给 C3）。reader = Qwen VL 评测 owner，Qwen-VL 自家细节只补外部对比视角。

## 路线定位（1 段）

到 2026-05，adapter VLM 仍是**开源权重 VLM 的事实标准范式**：vision encoder（SigLIP-2 / InternViT / 自研 ViT）独立预训练 → MLP/cross-attn connector → 文本 LLM。竞争集中在三家：**Qwen-VL 系**（产品完整度 + 闭源 Max）、**InternVL 系**（OpenGVLab，学术开源 SOTA）、**LLaVA-OneVision 系**（学术 recipe 透明度第一）。MiniCPM-V 占边端 (≤8B) 实用 niche，Cambrian/Eagle 提供\"多 encoder 融合\"消融基线。与 native VLM（Gemini 2.5 / GPT-5 / Qwen3-Omni）相比，adapter 路线的卖点仍是 **训练成本低 1-2 个数量级 + 可继承任意新 LLM backbone**；代价是 audio/video 长流和 any-to-any 生成弱。

## 代表模型清单

| 模型 | 发布 | Vision encoder | Connector | LLM backbone | source |
|---|---|---|---|---|---|
| Qwen2-VL (2B/7B/72B) | 2024-09 | 自研 ViT-675M + 2D-RoPE | MLP + 2×2 patch merge | Qwen2 | [arxiv:2409.12191](https://arxiv.org/abs/2409.12191) |
| Qwen2.5-VL (3B/7B/32B/72B) | 2025-01 / 2025-03 | 同上 + window attn | MLP merge | Qwen2.5 | [arxiv:2502.13923](https://arxiv.org/abs/2502.13923), [blog](https://qwenlm.github.io/blog/qwen2.5-vl/) |
| **Qwen3-VL (2B/4B/8B/32B/30B-A3B/235B-A22B)** | 2025-08 ~ 2025-10 | 升级 ViT + M-RoPE 时间轴 | MLP merge | Qwen3 dense/MoE | [blog](https://qwenlm.github.io/blog/qwen3-vl/), [HF Qwen3-VL-235B](https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct) |
| Qwen3-VL-Plus / Max | 2026-Q1 [uncertain release date] | 闭源 | — | 闭源 | [Artificial Analysis](https://artificialanalysis.ai/) |
| InternVL 2.0 / 2.5 (1B~78B) | 2024-07 / 2024-12 | InternViT-300M / 6B | MLP + pixel shuffle 1/4 | InternLM2 / Qwen2 | [arxiv:2412.05271](https://arxiv.org/abs/2412.05271) |
| **InternVL3 (1B/2B/8B/14B/38B/78B)** | 2025-04 | InternViT-300M / 6B v2 | MLP + pixel shuffle | Qwen2.5 / InternLM3 | [arxiv:2504.10479](https://arxiv.org/abs/2504.10479) |
| InternVL3.5 | 2025-08 | InternViT v2.5 | + Cascade RL | 同上 | [arxiv:2508.18265](https://arxiv.org/abs/2508.18265) |
| LLaVA-OneVision (0.5B/7B/72B) | 2024-08 | SigLIP-SO400M | 2-layer MLP | Qwen2 | [arxiv:2408.03326](https://arxiv.org/abs/2408.03326) |
| **LLaVA-OneVision-1.5 (4B/8B)** | 2025-10 | SigLIP-2 SO400M | 2-layer MLP | Qwen3 | [arxiv:2510.??? OV-1.5 tech report](https://arxiv.org/abs/2510.05887) [uncertain id]; [github LLaVA-VL](https://github.com/LLaVA-VL/LLaVA-NeXT) |
| MiniCPM-V 2.6 | 2024-08 | SigLIP-400M | perceiver resampler (64 q) | Qwen2-7B | [arxiv:2408.01800](https://arxiv.org/abs/2408.01800) |
| **MiniCPM-V 4.0 / 4.5** | 2025-08 / 2025-10 | SigLIP-2 | resampler | Qwen3-4B/8B | [github OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V) |
| MiniCPM-o 2.6 (omni) | 2025-01 | SigLIP + Whisper | resampler | Qwen2.5 | 同 repo |
| Cambrian-1 (8B/13B/34B) | 2024-06 | **4-encoder mix** (CLIP+SigLIP+DINOv2+ConvNeXt) | SVA spatial cross-attn | Vicuna / Llama-3 | [arxiv:2406.16860](https://arxiv.org/abs/2406.16860) |
| Eagle / Eagle-2 / Eagle-2.5 | 2024-08 / 2025-01 / 2025-04 | 多 encoder channel-concat | MLP | Llama-3 / Qwen2.5 | [arxiv:2408.15998](https://arxiv.org/abs/2408.15998), [arxiv:2501.14818](https://arxiv.org/abs/2501.14818) |
| NVILA / VILA-2 | 2024-12 | SigLIP | scale-then-compress MLP | Llama-3 | [arxiv:2412.04468](https://arxiv.org/abs/2412.04468) |

## 架构核心（按家族写）

### 1. Vision encoder 选择：SigLIP-2 vs InternViT 二分天下

到 2025 年下半年外部能看到的明确收敛：

- **SigLIP-2 SO400M-patch14-384/512**（Google, [arxiv:2502.14786](https://arxiv.org/abs/2502.14786)） 是开源 adapter VLM **默认选项**。LLaVA-OV-1.5、MiniCPM-V 4.x、NVILA、Eagle-2.5 全部默认 SigLIP-2。原因（LLaVA-OV-1.5 ablation §4）：相同算力下 OCR / chart / doc 指标领先 SigLIP-1 ~3-5 分，且原生支持 naflex（可变长宽比）。
- **InternViT-300M-448 / InternViT-6B-448** 是 OpenGVLab 路线的差异化。InternViT-6B 是目前**唯一公开的 6B 级 ViT**，InternVL3 paper §3.1 显示在 78B 主干下 InternViT-6B 仍能多给 ~2 分 MMMU；但 8B 以下 size 上 InternViT-300M 收益≈SigLIP-2，所以 InternVL3 1B/2B/8B 实际用 300M 版本。
- **Qwen-VL 系**坚持**自研 ViT**（ViT-675M 起步，Qwen2.5-VL 在 backbone 内插 window attention 降算力，Qwen3-VL 进一步加 timestamp-aware position）。Qwen2.5-VL paper §2.1 解释自研是为了 native dynamic resolution + 视频时间编码，**不直接用 SigLIP**。外部 ([HF discussion threads](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/discussions)) 偶尔抱怨这让第三方做 vision-only feature 提取不方便。
- **Cambrian / Eagle 的多 encoder 路线**：Cambrian-1 paper 是这条线最完整的 ablation——同时跑 CLIP / SigLIP / DINOv2 / ConvNeXt 四 encoder + SVA(spatial vision aggregator) cross-attn 融合。结论：多 encoder 在 vision-centric benchmark（CV-Bench、自家提的）有 +5~10 分提升，但**通用 VQA 上收益≈1 分，工程复杂度极高**。社区到 2025 年基本回退到\"SigLIP-2 单 encoder + 强 LLM\"，Cambrian/Eagle 主要作为消融基线被引用 ([Raschka 2025 VLM survey](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms))。

### 2. Connector 设计

三条主流：

- **MLP（2-layer GELU）**：LLaVA 原始方案，至今仍是 LLaVA-OV-1.5、Qwen-VL 全系（在 patch-merge 之后接 MLP）、InternVL 系的事实标准。优点：无信息丢失、训练稳定。缺点：visual token 数 = patch 数，长上下文压力大。
- **Pixel shuffle / patch merge（2×2 → 4×）**：InternVL 2.0 起引入，把相邻 4 个 patch 在 channel 上拼接再过线性层，**visual token 数立降 4×**（InternVL paper 表 2 显示 OCRBench 几乎无损）。Qwen2-VL 起也用 2×2 merge。这是当前 8K 视觉 token 上限内塞 4K×4K 图的关键 trick。
- **Perceiver / Q-Former resampler**：MiniCPM-V 系坚持 64-query perceiver resampler，使整图压到固定 64 token，**这是 MiniCPM 能在手机 4B 模型跑高分辨率的核心**（MiniCPM-V 2.6 paper §3.2）。代价是信息瓶颈，OCR 长文本场景弱于 pixel-shuffle 派。LLaVA-OV-1.5 paper §4.3 ablation 明确反对 resampler：\"with sufficient LLM capacity, MLP > resampler on all OCR/doc tasks\"。

外部综合判断（[Raschka VLM post 2025](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms)、[Cambrian §5 connector ablation](https://arxiv.org/abs/2406.16860)）：**资源充足→MLP+patch merge；端侧极致压缩→resampler**。Cross-attn-only connector（Flamingo 风格）在 2025 后基本绝迹。

### 3. Dynamic / native resolution

这是 2024→2025 最大架构演化，所有 active 家族都已切到\"任意分辨率\"：

- **Qwen-VL 系 native dynamic resolution**：Qwen2-VL 起，ViT 直接吃任意 H×W（patch=14，最大 token 上限可调，默认 ≤16384 visual tokens）。位置编码用 **M-RoPE**（time/height/width 三维分解），Qwen2.5-VL 进一步加绝对时间戳（[Qwen2.5-VL paper §2.2](https://arxiv.org/abs/2502.13923)）。Qwen3-VL blog 强调时间编码升级到\"interleaved MRoPE\" + 视频里的真实秒数注入。
- **InternVL dynamic tiling**：把高分辨率图切成 ≤40 个 448×448 tile + 1 个 thumbnail，每个 tile 独立过 ViT 后拼回（[InternVL 1.5 paper](https://arxiv.org/abs/2404.16821)，InternVL3 沿用）。和 Qwen 的 native 差别：**实现简单、对原 ViT 零改动**，代价是 tile 边界信息缺失，长宽比极端图（>1:4）需要补 padding。
- **LLaVA-OneVision higher-resolution AnyRes**：和 InternVL tiling 类似但 tile 数和分组策略不同（OV-1.5 paper §3）。
- **MiniCPM-V LLaVA-UHD 变种**：把图切成自适应 slice，每 slice 独立 resample 到 64 token，**总 token 数 ≤ slice_num×64**，在端侧场景里比 Qwen-VL 的 native 路线 token 数更可控。
- **SigLIP-2 NaFlex**：原生支持可变长宽比 patch grid，给 adapter VLM 提供了不切 tile 也能上高分辨率的 backbone 选项；OV-1.5 部分变体启用 NaFlex 模式（[SigLIP-2 paper §3.2](https://arxiv.org/abs/2502.14786)）。

外部经验法则（[Lambert interconnects VLM post 2025](https://www.interconnects.ai/)）：**OCR / doc / chart 强相关任务 → Qwen-VL native 或 InternVL tile；普通 VQA → 哪个都行**。

### 4. Video tokenization

视频是 2025 adapter VLM 的主战场，三种处理方式：

- **Qwen2.5-VL / Qwen3-VL**：抽帧 + 2D patch 后用 **3D conv**（temporal kernel=2）合并相邻 2 帧 → 每 2 帧合成一组 visual tokens；加 **absolute time M-RoPE**，模型能直接答\"这件事发生在第几秒\"（Qwen2.5-VL paper §2.3，外部演示中常用的 grounding 能力）。最大原生 ~1 hr 视频，靠 token budget 截断。
- **InternVL 2.5/3 + InternVideo2 接口**：InternVL3 paper §3.4 用均匀抽帧（默认 32-64 帧），每帧独立 tile，无显式 temporal merge；长视频靠 LLM 上下文处理。简单但 token 数线性涨。
- **LLaVA-Video / LLaVA-OV video mode**：抽 32 帧 + SlowFast-like 双速率采样（[LLaVA-Video paper arxiv:2410.02713](https://arxiv.org/abs/2410.02713)）。
- **NVILA \"scale then compress\"**：先高分辨率高帧率过 ViT，再用 token compression 模块压到目标长度，号称同算力下 video 准确率 +5（[arxiv:2412.04468](https://arxiv.org/abs/2412.04468)）。

视频 benchmark（VideoMME、MLVU、LongVideoBench）上 2026-05 排序：**Qwen3-VL-235B ≈ Gemini 2.5 Pro > InternVL3-78B > GPT-4o > LLaVA-Video-72B**（[Artificial Analysis Video](https://artificialanalysis.ai/) + 各家自报）。

## 训练方法核心（外部已知部分）

各家公开的 recipe 收敛模式高度一致，差异在 data scale 和 RL 阶段：

| 家族 | Stage 1 (align) | Stage 2 (pretrain) | Stage 3 (SFT) | Stage 4 (RL) | total tokens |
|---|---|---|---|---|---|
| LLaVA-OV-1.5 | MLP-only on caption 4M | unfreeze all, 16M interleaved | 4M instruction | DPO (small) | ~64B vision tokens (paper §3) |
| InternVL3 | MLP align | **native multimodal pretrain**（**文本 + 多模态混合 from scratch**, paper 主卖点）| 多任务 SFT | MPO + Cascade RL (3.5) | 200B+ |
| Qwen2.5-VL | MLP align | 4 stage 渐进 | SFT | DPO | 未披露 token 总数 |
| Qwen3-VL | 同上 + 视频/agentic data | — | — | RL（推测含 RLVR） | unknown |
| MiniCPM-V 4.x | MLP align | OCR-heavy | SFT | DPO + RLAIF-V | 边端 size，~10B |

外部关注点：

- **InternVL3 的\"native multimodal pretraining\"** ([arxiv:2504.10479](https://arxiv.org/abs/2504.10479) §3) 是 2025 adapter 路线最重要的方法学贡献：**不再从纯文本 LLM 出发**，而是 vision + text 从 pretrain 阶段就联合优化。paper 报告在等算力下相比传统两阶段（先文本 LLM 再贴 vision）有 +3~5 分 MMMU 提升。这模糊了 adapter / native VLM 的界线，外部 ([Raschka 2025](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms)) 认为是\"adapter 范式向 native 范式的中点\"。
- **LLaVA-OV-1.5 的算力开源**：OV-1.5 tech report 明确给出\"8B 模型 ~$16k 公有云训练成本\"，是当前最透明的 adapter VLM recipe，社区复现门槛最低（[github LLaVA-VL/LLaVA-NeXT](https://github.com/LLaVA-VL/LLaVA-NeXT)）。
- **RL on VLM**：InternVL3.5 的 Cascade RL（先 offline MPO → 再 online GRPO）是公开 paper 里最完整的 VLM RL 配方。Qwen3-VL 的 RL 细节**外部完全没披露**（与 LLM 侧的 Qwen3 paper 不同，VL 这边只有 blog）。

## 与 eval / benchmark 的接口

外部第三方独立测试视角：

- **OpenCompass VLM leaderboard** ([opencompass.org.cn/leaderboard-multimodal](https://rank.opencompass.org.cn/leaderboard-multimodal))：2026-05 截止 open-weights 顶部 ≈ Qwen3-VL-235B ≈ InternVL3.5-78B > Qwen3-VL-32B > InternVL3-38B > LLaVA-OV-1.5-8B。
- **MMMU / MathVista / DocVQA / OCRBench**：Qwen3-VL 和 InternVL3.5 在 MMMU 上同 size 互有胜负；**OCRBench 上 Qwen-VL 系全 size 段领先**（native dynamic resolution 优势）。
- **视频**：VideoMME long subset 上 Qwen3-VL 显著领先（M-RoPE 时间编码 + agentic 视频 SFT 数据）。
- **CV-Bench / vision-centric**：Cambrian 提出的 benchmark，多 encoder 路线在这上面仍然占优，但只有 Cambrian/Eagle 自己玩。
- **Contamination 信号**：MMMU 多次被指 train-set leak（[MMMU-Pro paper arxiv:2409.02813](https://arxiv.org/abs/2409.02813)），现在外部更看 MMMU-Pro / MathVerse / MathVision 这类\"加固版\"。InternVL3 paper 主动报 MMMU-Pro。
- **Adapter VLM 与 native VLM 的差距**（外部 [Artificial Analysis 2026-Q1 multimodal report](https://artificialanalysis.ai/)）：纯图文 understanding 上 Qwen3-VL-Max ≈ GPT-5 ≈ Gemini 2.5 Pro，**adapter 路线在 understanding 上没有结构性劣势**；劣势集中在 (a) 音频/长视频流式 (b) any-to-any 生成 (c) 极低延迟实时交互。

## 未知与争议

- **Qwen3-VL ViT 改动细节**：blog 只说\"升级\"，paper 截至 2026-05 未出，外部无法确认 head count / window size。
- **InternVL3 \"native multimodal pretrain\" 的 mix ratio**：paper 给了 high-level 比例但消融不全，外部复现报告（[OpenGVLab github issues](https://github.com/OpenGVLab/InternVL/issues)）显示对 ratio 敏感。
- **LLaVA-OV-1.5 vs InternVL3 同 8B 谁更强**：两边自报数据各胜场景，独立第三方完整对比（如 OpenCompass）显示\"互有 ±1 分\"，结论实质是 tied [推测]。
- **Cambrian/Eagle 多 encoder 路线是否真死**：2026-Q1 之后无大 release，但 Eagle-2.5 仍在更新；外部认为这条路线在\"vision-heavy agent\"（GUI、机器人）场景可能复活 [推测]。
- **Qwen3-VL-Max 是否仍是 adapter 架构**：外部无确认，可能已切 native fusion [unknown — 没找到一手 source]。

## 推荐外部材料

- [Sebastian Raschka, \"Understanding Multimodal LLMs\" 2024-11 + 2025 更新](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms) — adapter VLM 入门最佳，connector / encoder 对比图直接可用。
- [InternVL3 paper (arxiv:2504.10479)](https://arxiv.org/abs/2504.10479) — native multimodal pretraining 的关键 paper，adapter 路线方法学转折点。
- [LLaVA-OneVision-1.5 tech report + github](https://github.com/LLaVA-VL/LLaVA-NeXT) — 完整 recipe + 训练成本透明，复现首选。
- [Qwen2.5-VL paper (arxiv:2502.13923)](https://arxiv.org/abs/2502.13923) + [Qwen3-VL blog](https://qwenlm.github.io/blog/qwen3-vl/) — native dynamic resolution + M-RoPE 时间编码 的最详细公开说明。
- [Cambrian-1 paper (arxiv:2406.16860)](https://arxiv.org/abs/2406.16860) — multi-encoder / connector 的最完整 ablation，做 VLM 评测设计必读。
- [SigLIP-2 paper (arxiv:2502.14786)](https://arxiv.org/abs/2502.14786) — 当前默认 vision encoder，NaFlex 可变分辨率原理。
- [MiniCPM-V github (OpenBMB)](https://github.com/OpenBMB/MiniCPM-V) — 端侧 adapter VLM 的工程参考，LLaVA-UHD 切片方案实现。
- [OpenCompass VLM leaderboard](https://rank.opencompass.org.cn/leaderboard-multimodal) — 第三方综合榜，外部对 adapter VLM 的客观排名主要看这里。
- [Artificial Analysis multimodal](https://artificialanalysis.ai/) — closed vs open VLM 同框对比，含 cost / latency。
