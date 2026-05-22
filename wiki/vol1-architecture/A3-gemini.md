# Gemini 2.5 / 3 家族（含 Deep Think）

## 路线定位

Google DeepMind 的 Gemini 家族在 frontier 三强里走的是**"natively multimodal + 超长上下文 + 自家 TPU 全栈"**的差异化路线。和 GPT-5 比，弱在纯文本 reasoning headline、强在 video / audio / 1M-2M context；和 Claude 比，弱在 alignment / agentic coding 工具链、强在多模态原生与 inference 成本（TPU 自产）。2.5 代（2025-03 起）引入"thinking by default"，把 reasoning 内化为模型固有能力而非独立 SKU，并通过 **Deep Think** 提供 parallel-thinking 高端档；3 代（2025-11 起）继续推 thinking + agentic 工具调用。Pro/Flash/Flash-Lite 三档对应旗舰 / 主力 / 极廉，加上 Deep Think 顶配。参数从 1.5 起就不再披露。

## 代表模型清单

| 模型 | 发布日 | 参数/激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| Gemini 1.5 Pro | 2024-02-15 | 未披露（**MoE 已确认**） | 1M context（research 到 10M）；sparse MoE 首次官方承认 | [1.5 tech report arxiv:2403.05530](https://arxiv.org/abs/2403.05530) |
| Gemini 1.5 Flash | 2024-05-14 | 未披露 | 蒸馏自 Pro 的轻量；1M context | [I/O 2024 keynote](https://blog.google/technology/ai/google-io-2024-100-announcements/) |
| Gemini 2.0 Flash | 2024-12-11 | 未披露 | Multimodal Live API；native image/audio out（preview） | [blog 2024-12-11](https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/) |
| Gemini 2.0 Flash + Pro Experimental | 2025-02-05 | 未披露 | 2.0 正式 GA；Pro Exp 2M context | [blog 2025-02-05](https://blog.google/technology/google-deepmind/gemini-model-updates-february-2025/) |
| Gemini 2.5 Pro (Experimental) | 2025-03-25 | 未披露 | "thinking model by default"；LMArena #1；1M ctx，规划 2M | [blog 2025-03-25](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/) |
| Gemini 2.5 Flash (Preview) | 2025-04-17 | 未披露 | 首个**可调 thinking budget** 的 Flash | [blog 2025-04-17](https://blog.google/products/gemini/gemini-2-5-flash-preview/) |
| Gemini 2.5 Pro / Flash GA + Flash-Lite | 2025-06-17 | 未披露 | GA；Flash-Lite 为最廉档 | [blog 2025-06-17](https://blog.google/products/gemini/gemini-2-5-model-family-expands/) |
| Gemini 2.5 Deep Think | 2025-08-01 (Ultra 订阅) | 未披露 | **parallel thinking**；IMO 2025 金牌级；AI Ultra 限定 | [blog 2025-08-01](https://blog.google/products/gemini/gemini-2-5-deep-think/) |
| Gemini 2.5 Computer Use | 2025-10-07 | 未披露 (基于 2.5 Pro) | 浏览器/UI agent 专用变体 | [blog 2025-10-07](https://blog.google/technology/google-deepmind/gemini-computer-use-model/) |
| Gemini 3 Pro | 2025-11-18 | 未披露 | 3 代旗舰；reasoning + multimodal SOTA 复夺榜首 | [blog 2025-11-18](https://blog.google/products/gemini/gemini-3/) |
| Gemini 3 Deep Think | 2025-11-18 (限定) → 2025-12 GA Ultra | 未披露 | 3 代 parallel thinking 顶配 | 同上 + [3 model card PDF](https://storage.googleapis.com/deepmind-media/gemini/gemini_v3_report.pdf) |
| Gemini 3 Flash / Flash-Lite | 2026 Q1 | 未披露 | 3 代 mainstream / 廉价档 | [unknown — 截至 2026-05 没看到 Flash-Lite 单独 blog；Flash 见 2026 年初更新] |
| "Gemini 3 Ultra" | — | — | [unknown — 2026-05 前未发] |

> 注：Google 从 1.5 起就不再披露参数量、激活参数、训练 token 数。2024 Gemini 1.0 tech report（[arxiv:2312.11805](https://arxiv.org/abs/2312.11805)）也只给定性描述。

## 架构核心

### Native multimodality + early fusion

- 1.0 tech report 第 2 节明确：Gemini **"trained jointly across text, image, audio, and video"**，输入侧 image/audio 直接 tokenize 进同一 transformer，而不是 CLIP 式 late fusion[^10arch]。这一设计 2.x / 3 一直延续，是 Google 反复在 marketing 上强调 "natively multimodal" 的技术指代。
- 1.5 起加入 video（按帧 tokenize + audio track）和 native audio in/out（2.0 Flash Live）。2.5 的 audio dialog 可低延迟双向（[2.5 Flash native audio docs](https://ai.google.dev/gemini-api/docs/live)）。
- 图像生成在 2.0 Flash 起内置（"Native image generation"，2025-03 公开 preview），后续 2.5 Flash Image / "Nano Banana" 是同一 lineage 的图像专用 checkpoint（[blog 2025-08-26](https://blog.google/technology/google-deepmind/gemini-2-5-flash-image/)）。这与 OpenAI 把 image gen 拆给 DALL·E / GPT-Image 不同。

### Sparse MoE

- 1.5 tech report §2 第一次官方承认 sparse MoE：**"Gemini 1.5 Pro is a sparse mixture-of-experts (MoE) Transformer-based model"**[^15arch]。具体 expert 数 / top-k / router 算法 **未披露**。
- 2.x / 3 是否仍 MoE：Google 没有再写 tech report 级别确认。Demis 在 [Dwarkesh 2025-02](https://www.dwarkeshpatel.com/p/demis-hassabis-2) 访谈说 "we're continuing to scale both dense and sparse approaches"，不算明牌。第三方（[SemiAnalysis 2025-04 Gemini 2.5 piece, paywalled](https://www.semianalysis.com/p/google-we-have-no-moat-and-neither-2)）[推测] 2.5 Pro 仍是 MoE，激活量在 Claude 3.5 Sonnet 量级。**确认状态：[推测]**。

### 长上下文

- 1.5 Pro 论文 §4 报告 **10M token research-scale needle-in-haystack 接近完美命中**（near 100% recall at 10M for text；视频测到 ~3h）[^15longctx]。生产 API 1M。
- 2.5 Pro GA 是 **1M context**，公告里说"2M coming soon"，2M 在 2.5 Pro Exp 阶段实际开放过部分早期 access（[blog 2025-02-05](https://blog.google/technology/google-deepmind/gemini-model-updates-february-2025/)）。截至 2026-05，公开 API 上 2M 是否对所有用户 GA：[uncertain]。
- 实现细节：1.5 paper 写 "novel mixture-of-experts architecture and major advances in training infrastructure" 让长 context 可行，**没有写具体 attention 变种**。是否 ring attention / sliding window + global / blockwise [unknown]。Jeff Dean 2024 Stanford CS25 talk 提到 "we use a combination of techniques including local attention and global attention"（[CS25 v4 Jeff Dean lecture](https://www.youtube.com/watch?v=oFtjKbXKqbg)）—— 但没说哪个模型。

### Thinking / Deep Think

- 2.5 起 thinking 是默认行为，不需要切换 SKU（和 Claude 3.7 hybrid 类似，但 Google 不用 "hybrid" 一词，而是叫 "thinking model"）。Flash 上可设 `thinking_budget`（0 = disable，正整数 = 上限 token），是 2.5 Flash preview blog 的核心卖点。
- **Deep Think** = parallel thinking。2.5 Deep Think 公告里写 "uses parallel thinking techniques that generate many ideas at once and consider them in parallel"[^deepthink]，以及一份 2025 IMO 报告显示 IMO 2025 上 Deep Think 达到金牌分数线（[DeepMind IMO 2025 blog 2025-07-21](https://deepmind.google/discover/blog/advanced-version-of-gemini-with-deep-think-officially-achieves-gold-medal-standard-at-the-international-mathematical-olympiad/)）。算法细节（是否 best-of-N + verifier、是否 MCTS-style）未披露，**最接近的公开线索**是 Noam Shazeer / Jack Rae 在 Google 内部演讲转述的"think longer in parallel and aggregate"（无书面 source）。
- 3 Deep Think：3 系 model card（PDF link 上）报告 ARC-AGI-2 / Humanity's Last Exam 等 reasoning bench 上的大跳跃，但 thinking pipeline 仍然不公开实现。

### Tokenizer
- SentencePiece，词表大小 1.5 时报为 256K[^15arch]。2.x/3 [uncertain]。

## 训练方法核心

### Pretrain

- 全部在 **TPU** 上训练。1.0 用 TPUv4 + TPUv5e；1.5 Ultra/Pro 在 "multiple 4096-chip pods of TPUv4 across multiple datacenters" 上（[1.5 paper §3](https://arxiv.org/abs/2403.05530)）。2.x/3 大概率 TPUv5p + TPUv6 (Trillium)，但**没有任何 Google blog 明确写 "Gemini 2.5 用 Trillium 训练"** —— Trillium GA 是 2024-12，时间上对得上；Ironwood (TPUv7) 2025-04 公布，Sundar 在 [Cloud Next '25 keynote](https://blog.google/products/google-cloud/next-2025/) 提 "Ironwood will power our next generation of models"，[推测] 指 Gemini 3。
- Data scale / mixture：未披露。1.5 paper 提到 multimodal data 的训练比例，但没给 token 数。
- 算力：未披露 FLOPs。Epoch AI 在 [2024 frontier compute estimates](https://epochai.org/data/notable-ai-models) 估 Gemini Ultra ~5e25 FLOP，Gemini 1.5 Pro 较小，2.5/3 [unknown]。

### Mid / annealing
- Google 没公开 mid-training 阶段细节。1.5 paper 仅笼统讲 "we performed additional training stages including multimodal alignment"。

### Post-train

- **RLHF + RLAIF 混合**，[1.0 tech report §5.2](https://arxiv.org/abs/2312.11805) 写明使用 reward model + AI feedback。
- 2.5 起 thinking 训练 [推测] 包含 RLVR 风格（math / code / tool-use verifiable reward），但官方从未用 "RLVR" 命名。Jeff Dean 在 [ICML 2024 keynote](https://www.youtube.com/watch?v=lH74gNeryhQ) 提 "self-generated reasoning traces, filtered by correctness, fed back" —— 是 STaR / RFT 套路的公开背书。
- Deep Think 训练：DeepMind 没有给 paper。从 IMO 公告看，[推测] 有专门的 math-heavy fine-tune 和 search-augmented training。
- Agentic / tool use：2.5 起原生支持 function calling、Google Search grounding、code execution。Computer Use 2.5 变体单独 fine-tune（类似 Anthropic 的 Computer Use 思路）。

### 算力披露差距
Google 比 OpenAI / Anthropic 略松一点（1.0 / 1.5 都有 tech report），但 2.5 / 3 没有 tech report，只有 model card PDF（3 代有，2.5 没有完整 tech report，只有 [2.5 model card PDF, 2025-06](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf)）。

## 与 eval / benchmark 的接口

官方 headline benchmark（按 model card / blog）：

| Bench | 2.5 Pro (think) | 2.5 Deep Think | Gemini 3 Pro | 3 Deep Think |
|---|---|---|---|---|
| GPQA Diamond | 84.0 | 87.6 | 91.9 | 93.8 |
| AIME 2025 | 86.7 | 99.2 (with code) | 95.0 | 100.0 (claimed) |
| Humanity's Last Exam | 18.8 | 34.8 | 37.5 | 45.8 |
| MMMU | 81.7 | 84.0 | 81 | — |
| SWE-Bench Verified | 63.8 | 67.2 | 76.2 | — |
| LiveCodeBench | 75.6 | 87.6 | — | — |
| ARC-AGI-2 | — | — | 31.1 | 45.1 |

数字来源：2.5 见 [2.5 model card PDF](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf)；3 见 [Gemini 3 launch blog 2025-11-18](https://blog.google/products/gemini/gemini-3/) + model card。

**注意事项**：
- Gemini 报 SWE-Bench Verified 时常带 "custom agent"（如 Jules / Gemini CLI）—— 比 Claude 的 scaffold 更花。读者团队对比时务必看是不是同一个 harness（Princeton 官方 harness vs Anthropic / Google 自家）。
- AIME 99-100% 这种数字 Deep Think 经常用 "with code execution / with parallel sampling N=8/32"。是否单次 forward pass 要看脚注。
- LMArena：Gemini 2.5 Pro 在 2025-03 首日就拿到 #1（[lmarena.ai leaderboard snapshot via Lambert 2025-03](https://www.interconnects.ai/p/gemini-25-pro)），Gemini 3 Pro 2025-11 再次登顶。LMArena 偏 chat preference，评测 owner 通常已经知道这个 bench 的局限。

**Contamination**：
- 2.5 / 3 model card 都有 "we filtered evaluation benchmarks from training data" 段，但和 Anthropic 一样无第三方独立审计。
- HLE / ARC-AGI-2 这些较新 bench 时间上不太可能 leak，但 GPQA / MMLU 系列已经被业界普遍认为 saturate 或被污染。

## 未知与争议

- **架构**：2.5 / 3 是否 MoE、expert 数、激活量 —— 全未披露；只有 1.5 官方承认 MoE。
- **长 context attention 实现**：1.5 paper 故意 vague，2.5 / 3 完全没说。10M context 是 research demo，生产 1M 实际质量随 depth 衰减程度，[Chroma 2024 "Lost in the middle for long-context"](https://research.trychroma.com/context-rot) 等第三方 study 显示 Gemini 长 context recall 在 200K+ 后明显下滑 —— 不要直接信"1M 都能用"。
- **Deep Think 实现**：parallel thinking 具体 = best-of-N? tree search? consensus? 全未披露。学界（[Snell et al. 2024 "Scaling test-time compute"](https://arxiv.org/abs/2408.03314)）有相关公开方法但 Google 不确认对应关系。
- **TPU 算力**：训练 FLOPs、chip-hours、能耗——未披露。
- **Gemini 3 vs Gemini 2.5 真实代差**：3 Pro 在 reasoning bench 上跳幅显著，但在很多 agentic / 长程任务上和 Sonnet 4.5 / Opus 4.5 还在拉锯（见 [Willison 2025-11-18 Gemini 3 hands-on](https://simonwillison.net/2025/Nov/18/gemini-3/)）。
- **3 代是否独立架构改动还是 scale + better post-train**：Google 没说。[推测] 主要增量在 thinking pipeline + 数据 + scale，架构骨架仍延续 2.x。
- **Gemini Robotics / Gemma 关系**：Gemma 是 open-weight 小模型族（基于 Gemini research），不算 Gemini frontier 线，但共享 tokenizer 和部分技术。读者如果要看 Gemini 架构的"开盒近似品"，Gemma 2 / 3 的 tech report（[Gemma 3 tech report 2025-03](https://arxiv.org/abs/2503.19786)）是最近的窗口 —— Gemma 3 写明用 grouped-query attention + sliding window 5:1 interleave，这是目前关于"Google frontier 系列长上下文怎么做"的最接近公开线索。

## 推荐外部材料

- [Gemini 1.5 tech report (arxiv:2403.05530)](https://arxiv.org/abs/2403.05530) — 唯一一份明确写 sparse MoE + 10M context 的 Gemini paper，必读。
- [Gemini 1.0 tech report (arxiv:2312.11805)](https://arxiv.org/abs/2312.11805) — early fusion multimodal 的奠基描述。
- [Gemini 2.5 model card PDF](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf) / [Gemini 3 model card PDF](https://storage.googleapis.com/deepmind-media/gemini/gemini_v3_report.pdf) — 没有 tech report，model card 是唯一接近的官方信息源。
- [Gemma 3 tech report (arxiv:2503.19786)](https://arxiv.org/abs/2503.19786) — Google 近期 open-weight，间接窥视 frontier attention/长上下文方案。
- [Demis Hassabis @ Dwarkesh 2025-02](https://www.dwarkeshpatel.com/p/demis-hassabis-2) — 长访谈，多次谈到 thinking、scaling、AGI timeline，不给 spec 但给方向。
- [Jeff Dean @ Stanford CS25 v4, 2024](https://www.youtube.com/watch?v=oFtjKbXKqbg) — TPU + MoE + 长上下文的工程视角，比 marketing blog 干货多。
- [Sebastian Raschka, "Noteworthy LLM Research 2025"](https://magazine.sebastianraschka.com/) — 每季度复盘里 Gemini 2.5 / 3 都有架构对比段。
- [Nathan Lambert, "Gemini 2.5 Pro and the new frontier"](https://www.interconnects.ai/p/gemini-25-pro) — post-train / RL 视角看 thinking by default。
- [Simon Willison Gemini tag](https://simonwillison.net/tags/gemini/) — 每个版本第一天的 hands-on 与定价/regression。
- [Chroma "Context Rot" report 2024](https://research.trychroma.com/context-rot) — 第三方独立测的长上下文质量衰减，包含 Gemini 1.5 / 2.0 数据，校准"1M context 真不真"的预期。

[^10arch]: Gemini 1.0 tech report §2 "Model architecture" — "Gemini models are built on top of Transformer decoders ... They are trained to accommodate textual input interleaved with a wide variety of audio and visual inputs ... and can produce text and image outputs." https://arxiv.org/abs/2312.11805
[^15arch]: Gemini 1.5 tech report §2 — "Gemini 1.5 Pro is a sparse mixture-of-experts (MoE) Transformer-based model that builds on Gemini 1.0's research advances and multimodal capabilities." https://arxiv.org/abs/2403.05530
[^15longctx]: 1.5 paper §4.2 needle-in-haystack — text recall ≥99% up to 10M tokens; video ≈100% up to ~3h. https://arxiv.org/abs/2403.05530
[^deepthink]: 2.5 Deep Think launch blog — "Deep Think uses parallel thinking techniques to generate many ideas at once, then evaluate and combine them." https://blog.google/products/gemini/gemini-2-5-deep-think/
