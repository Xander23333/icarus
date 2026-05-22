# 语音 / 音频 LLM 家族（speech-in / speech-out，截至 2026-05）

## 路线定位

语音 LLM 的 frontier 在 2024-2026 完成了两次范式跳跃：第一跳是从 **ASR→LLM→TTS 三段 cascade** 切到 **端到端 speech-in/speech-out**；第二跳是从 **半双工 turn-based** 切到 **full-duplex streaming**（用户和模型可同时说话、可被打断）。GPT-4o Realtime（OpenAI）、Moshi（Kyutai）定义了 full-duplex 的工程基线；Qwen2-Audio / Qwen3-Omni、Step-Audio、GLM-4-Voice 是中文圈把 speech 接入 frontier text LLM 的代表；Llama-Omni 是开源研究端最被引用的 adapter 路线 baseline。架构上所有 frontier 都收敛到 **离散 audio token + decoder-only transformer**，分歧点集中在 (a) tokenizer 是 semantic-only / acoustic-only / 双流分层，(b) 是否真双工（连续 listen + 连续 speak）还是 half-duplex VAD-based，(c) audio head 是 LM 内 multi-codebook 并行预测还是外挂 flow-matching/diffusion vocoder。

## 代表模型清单

| 模型 | 发布日 | 参数/激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| GPT-4o (Realtime) | 2024-05-13 (announce) / 2024-10-01 (Realtime API beta) / 2025-08-28 (GA) | [unknown] | 首个 product-tier 端到端 speech-in/speech-out + 真双工 | [Hello GPT-4o][^gpt4o] / [Realtime API GA][^realtime-ga] |
| GPT-Realtime (gpt-realtime) | 2025-08-28 | [unknown] | Realtime API 正式 GA，新 voice、MCP、image input | [Realtime GA blog][^realtime-ga] |
| Moshi | 2024-09-17 (paper) | 7B text backbone (Helium) + Mimi codec | 真双工、**Inner Monologue**、120ms 理论延迟 | [arXiv 2410.00037][^moshi] |
| Mimi (codec) | 同 Moshi paper | 80M | semantic + acoustic 蒸馏混合 RVQ codec, 12.5 Hz / 1.1 kbps | [arXiv 2410.00037][^moshi] |
| Qwen2-Audio | 2024-07-15 | 7B (Qwen2-7B + Whisper-large-v3 encoder) | audio-in / text-out，instruction-tuned audio understanding | [arXiv 2407.10759][^qwen2audio] |
| Qwen2.5-Omni | 2025-03-27 | 7B (Thinker-Talker dual-track) | 同模型支持 text/image/audio/video in + text/audio out，**TMRoPE** 时间对齐 | [arXiv 2503.20215][^qwen25omni] |
| Qwen3-Omni | 2025-09-22 | 30B-A3B MoE (Thinker) + Talker | 119 语言文本 / 19 语言 speech-in / 10 语言 speech-out，211ms 首包延迟 | [arXiv 2509.17765][^qwen3omni] |
| Step-Audio | 2025-02-17 | 130B (text) + 3B audio tokenizer + 3B vocoder | 双 codebook（linguistic 16.7Hz + semantic 25Hz），中英方言+情感 | [arXiv 2502.11946][^stepaudio] |
| Step-Audio 2 | 2025-07 | [unknown] | 端到端 reasoning + tool use over speech | [arXiv 2507.16632][^stepaudio2] |
| GLM-4-Voice | 2024-10-25 | 9B (GLM-4-9B base) + speech tokenizer + flow-matching decoder | 中英双语 speech-in/out，supervised speech tokenizer from Whisper-encoder + VQ | [arXiv 2412.02612][^glm4voice] / [GitHub][^glm4voice-gh] |
| Llama-Omni | 2024-09-10 | Llama-3.1-8B + Whisper encoder + streaming speech decoder | 开源研究 baseline，226ms 延迟，4 GPU 3 天训练 | [arXiv 2409.06666][^llamaomni] |
| Llama-Omni 2 | 2025-05 | 0.5B–14B 系列 | autoregressive streaming TTS + LLM joint，延迟更低 | [arXiv 2505.02625][^llamaomni2] |
| Kimi-Audio | 2025-04 | 7B base | audio understanding + generation 统一，hybrid input (continuous + discrete) | [arXiv 2504.18425][^kimiaudio] |
| MiniCPM-o 2.6 | 2025-01 | 8B | 端侧 omni（vision+audio+text），streaming voice | [HF model card][^minicpm-o] |
| SNAC (codec) | 2024-10 | — | multi-scale RVQ，44.1kHz 0.98 kbps，TTS 主流 codec | [arXiv 2410.14411][^snac] |
| EnCodec | 2022-10 | — | Meta 早期 neural audio codec，RVQ baseline，仍被多数 paper 用作对照 | [arXiv 2210.13438][^encodec] |

## 架构核心

### speech tokenization：semantic vs acoustic 的分裂与统一

这是整个领域最关键的设计轴。**acoustic token**（EnCodec、SoundStream、SNAC、DAC）目标是 reconstruct waveform，码本对 phonetic 内容并不直接对齐；**semantic token**（HuBERT、w2v-BERT、Whisper encoder 输出离散化）目标是承载语义，但丢失说话人/情感/背景声。两者各自不够：纯 acoustic 给 LM 当输入会让 LM 浪费容量学声学细节；纯 semantic 给 LM 当输出无法重建可听音频。

frontier 的三种合流方式：

1. **双流分层**（Moshi / Step-Audio）。Moshi 的 **Mimi** 是 RVQ-8，**第 0 码本被蒸馏对齐到 WavLM 的 semantic 表示**，第 1-7 码本承担 acoustic 重建——这是把 semantic 与 acoustic 塞进同一个 codec 的代表设计，12.5 Hz 帧率、1.1 kbps[^moshi]。Step-Audio 直接用两条独立 codebook：linguistic tokenizer (Paraformer-based, 16.7Hz, 1024 vocab) + semantic tokenizer (CosyVoice-based, 25Hz, 4096 vocab)，LM 端 interleave 输入[^stepaudio]。
2. **supervised semantic + 外挂 vocoder**（GLM-4-Voice）。用 Whisper-large-v3 encoder 后接一个 VQ，码本 size 16384、12.5 Hz，**显式监督训练让 token 承载语义**；语音生成由 LM 输出 semantic token，再接一个 CosyVoice-style **flow-matching decoder** 还原 waveform[^glm4voice]。优点是 LM 只需学 12.5 Hz 单流序列，劣势是音色/情感由 decoder 端注入，LM 控制力弱。
3. **continuous encoder + discrete output**（Qwen2-Audio / Qwen2.5-Omni / Qwen3-Omni / Llama-Omni / Kimi-Audio）。**输入侧**直接用 Whisper-style continuous features 投影进 LM（避免输入侧 tokenization 损失），**输出侧**才用离散 audio token + vocoder。Qwen3-Omni 把这套做到最完整：Thinker（reasoning LM）输出 text，Talker（轻量 LM）并行预测多 codebook audio token，由 Code2Wav 模块流式还原[^qwen3omni]。

> Qwen 角度的 takeaway：Qwen3-Omni 的 **Thinker-Talker** 解耦本质是承认"audio generation 与 reasoning 应该用不同参数预算"，这与 GPT-4o Realtime 单 transformer 端到端是相反路线。如果做 audio agent eval，要分清楚是评 Thinker 的 reasoning 还是 Talker 的 prosody。

### full-duplex streaming：Moshi 与 GPT-4o Realtime 是两套解法

**Moshi**（开源、有 paper）：把双工建模成 **multi-stream LM**——同一 transformer 同时预测 (a) 模型自己的语音 token 流、(b) 用户语音的 transcribed token 流、(c) 模型自己的 **inner monologue** 文本 token 流。每一帧 12.5Hz 推进，相当于 LM 始终在 listen+speak+think 三件事并行 next-token-predict，**没有 VAD、没有 turn-taking 状态机**，沉默由专门的 silence token 表达。理论端到端延迟 160ms（Mimi 80ms + transformer 80ms），实测 200ms[^moshi]。

**GPT-4o Realtime**（闭源）：官方 blog 称端到端语音延迟均值 232ms、最低 320ms 不到[^gpt4o]。Realtime API 暴露的接口是 **server-side VAD + 可被打断的 streaming audio in/out**，从 API 行为上看更像 **半双工 + 快速打断检测**，并非 Moshi 那种持续双流并行预测。OpenAI 未公开任何架构 paper；Realtime GA blog 强调 "single model handles audio directly without converting to text"[^realtime-ga]，但不披露 tokenizer / 是否多 codebook / 是否 MoE，全部 [unknown]。

**Qwen3-Omni** 的 streaming 通过 Talker + Code2Wav 的 chunk-wise inference 做到 211ms 首包延迟（单 turn），架构上仍是 turn-based 而非 Moshi 式连续双流[^qwen3omni]。

**Step-Audio** 的 chat 模式声明 "supports real-time speech interaction"，但具体是否真双工、如何处理打断未在 paper 详述[^stepaudio]。

### in-context audio reasoning：从"听清"到"听懂+推理"

- **Qwen2-Audio** 是首个把 audio 当成 instruction-tuneable modality 的 frontier 开源模型：audio captioning、SER、SQA、scene classification、music understanding 都在同一模型 chat interface 下完成[^qwen2audio]。
- **Qwen2.5-Omni** 的 **TMRoPE (Time-aligned Multimodal RoPE)** 把 video 帧与 audio 帧按真实时间戳交错插入 LM 序列，让 LM 真正"看着画面听声音"——这是音视频联合理解的关键位置编码改动[^qwen25omni]。
- **Qwen3-Omni** 把 audio understanding benchmark（如 MMAU、AIR-Bench Chat）上的 SOTA 推到接近闭源水平，paper 自报 32 个 audio benchmark 上 22 个开源 SOTA、32 个里 SOTA on 32 个之中 22 个[^qwen3omni]。
- **Step-Audio 2** 显式做 audio agentic 任务：电话场景下听用户语音→调用 tool→语音回复，paper 提出针对 audio 的 RL 微调流程[^stepaudio2]。
- 局限：当前 audio LLM 在 **long-form audio reasoning**（30min+ 会议、长音乐）上仍弱，Whisper-style encoder 的 30s 窗口是硬约束，多数实现靠 chunk + 重叠摘要绕过 [推测]。

### codec scaling：bitrate 与 LM 友好度的权衡

| Codec | 帧率 | 码本数 | 比特率 | LM 友好度 | 主要用户 |
|---|---|---|---|---|---|
| EnCodec | 75 Hz | 8 | 6 kbps | 低（序列太长） | 早期 paper baseline |
| SoundStream | 50/75 Hz | 4-16 | 3-12 kbps | 中 | AudioLM |
| SNAC | 12/23/47 Hz multi-scale | 3 | 0.98 kbps @ 44.1kHz | 高（多尺度，TTS 友好） | Orpheus-TTS、若干开源 TTS |
| DAC | 86 Hz | 9 | 8 kbps | 低 | 通用音频研究 |
| Mimi | 12.5 Hz | 8 (1 semantic + 7 acoustic) | 1.1 kbps | 高（专为 LM 设计） | Moshi |
| GLM-4-Voice tokenizer | 12.5 Hz | 1 (semantic only) | ~175 bps | 极高（单流） | GLM-4-Voice |

低帧率 + 少码本是 LM 友好的方向，但纯 semantic 单流（GLM-4-Voice）需要外挂强 vocoder 才能保住音色一致性。Mimi 12.5 Hz × 8 codebook 是当前被最多人参考的 sweet spot[^moshi]。

## 训练方法核心

### pretrain
- **Moshi**：Helium 7B text 预训练 2.1T tokens，再在 ~7M hours unsupervised speech 上做 audio pretraining，最后 ~170 hours 多说话人对话 + Fisher 数据 fine-tune full-duplex[^moshi]。
- **Qwen3-Omni**：从 Qwen3 text checkpoint 出发，加入大规模 audio/video 对齐预训练，具体小时数未完全披露但 paper 称 "millions of hours"[^qwen3omni]。
- **Step-Audio**：claims ~5T tokens text + audio joint training，audio token 数量级 [uncertain][^stepaudio]。
- **GLM-4-Voice**：基于 GLM-4-9B 继续预训练 1T 多 audio-text 混合 tokens[^glm4voice]。

### post-train
- **SFT**：所有家族都构造 (audio_query, text_or_audio_response) 对。Qwen3-Omni 强调跨语言 ASR/S2TT/TTS 数据的混合配比[^qwen3omni]。
- **RLHF / DPO**：Moshi 没用 RL；Qwen3-Omni 用了 reward model 对 talker 输出做 preference optimization [uncertain — paper 描述不全]；Step-Audio 2 显式说用 RL 优化 tool-using behavior[^stepaudio2]。
- **vocoder / Talker joint training**：GLM-4-Voice 的 flow-matching decoder 与 LM 分开训练；Qwen3-Omni 的 Talker + Code2Wav 也是分阶段；Moshi 的 Mimi 与 LM 完全分开训。这与图像 DiT 端到端训练形成对比——音频侧仍倾向 **codec 冻结 + LM 训练 + vocoder 微调** 三段式。

### 算力
- Moshi 训练在 8×H100 节点上完成（具体节点数和总 GPU-hours 未披露，paper 5.4 节）[^moshi]。
- 其余家族算力 [unknown]。GPT-4o / Realtime 全部 [unknown]。

## 与 eval / benchmark 的接口

### 主流 benchmark
- **ASR**：LibriSpeech (test-clean/other)、CommonVoice、FLEURS（多语言）。Qwen3-Omni 在 FLEURS 上自报 SOTA[^qwen3omni]。
- **Audio understanding**：**AIR-Bench**（Chat / Foundation）[^airbench]、**MMAU**（multi-task audio understanding）[^mmau]、**VoiceBench**（spoken instruction following）[^voicebench]。
- **TTS 质量**：SECS（speaker similarity）、WER、UTMOS、CMOS 人评。
- **Full-duplex / latency**：尚无标准 benchmark。Moshi paper 用自定义 turn-taking metric；GPT-4o blog 只报端到端延迟数；这是当前评测最薄弱的环节。
- **Spoken QA / reasoning**：Spoken-SQuAD、Llama Questions、Web Questions audio version，但题目本身偏简单。

### 第三方独立评测
- **Artificial Analysis Speech Arena**（2025 启动）提供闭源 voice model 的人评对比，GPT-4o Realtime、Gemini Live、Sesame、Hume 等在列[^aa-speech]。
- 中文圈对 Step-Audio / Qwen-Omni / MiniCPM-o 的独立评测主要在 OpenCompass audio 子榜，覆盖有限[^opencompass-audio]。

### contamination / overfit 信号
- LibriSpeech 公开十年，**几乎所有 audio LLM 都见过**，0.x% WER 数字已基本无区分度。
- AIR-Bench 与 MMAU prompts 公开，Qwen 系/Step 系自报分均显著高于早期 baseline；是否对 dimension 做了 SFT 对齐 [推测]。
- **跨说话人/跨场景 generalization** 没有标准 hold-out，闭源模型尤其无从核实。

## 未知与争议

1. **GPT-4o / GPT-Realtime 架构全黑盒**：是否是单 transformer、是 multi-codebook 还是 continuous latent、tokenizer 是什么、是否真双工——全部 [unknown]，目前只有 Realtime API 的行为可被 reverse-engineer。
2. **"真双工" 的定义**：Moshi 论文意义上的连续多流预测 vs API 层 VAD+打断检测，两者用户体感相似但 LM 内部计算量差一个量级。市场宣传普遍混用 "full-duplex"，需具体追到 paper 才能区分。
3. **音色/情感控制权**：semantic-only 路线（GLM-4-Voice）把音色交给 vocoder，LM 无法用 prompt 精细控制；双流路线（Moshi）LM 直接输出 acoustic token 可控音色但训练数据需求大。哪条更 scale 尚未有定论。
4. **多语言不平衡**：Qwen3-Omni 自报 19 语言 speech-in / 10 语言 speech-out，但低资源语言（如东南亚语言）的实际 WER 与英文有 10× 差距 [推测，paper 未给完整表]。
5. **audio agentic eval 缺位**：当前没有公认的 "audio + tool use + multi-turn" benchmark。Step-Audio 2 自定义评测难以横比[^stepaudio2]。Qwen agentic 团队若要做 audio agent eval，**需要自建**——这块是 greenfield。
6. **codec choice 是否影响 LM 上限**：Mimi vs SNAC vs supervised semantic 三种 codec 对最终 LM 推理能力的影响，**没有 controlled study**。Moshi paper 做了 Mimi ablation 但只对比 reconstruction quality，不对比下游 LM 智能[^moshi]。
7. **streaming 与 reasoning 的张力**：full-duplex 要求 LM 每 80ms 出一个 token，而 reasoning 要 chain-of-thought。Moshi 的 inner monologue 是当前唯一公开的工程解，但 reasoning 深度有限；GPT-4o Realtime 是否在内部跑长 CoT 再 stream voice 出来未知 [推测可能用 hidden thinking tokens]。

## 推荐外部材料

- [Moshi paper (arXiv 2410.00037)](https://arxiv.org/abs/2410.00037) — 当前 frontier 唯一详细的 full-duplex speech LM tech report，必读。Mimi codec 设计、inner monologue、多流 LM 三件事都源自此。
- [Qwen3-Omni tech report (arXiv 2509.17765)](https://arxiv.org/abs/2509.17765) — Thinker-Talker 架构定义，audio benchmark 报数最完整的开源模型。
- [Qwen2.5-Omni paper (arXiv 2503.20215)](https://arxiv.org/abs/2503.20215) — TMRoPE 时间对齐编码，做音视频联合 eval 必看。
- [GLM-4-Voice paper (arXiv 2412.02612)](https://arxiv.org/abs/2412.02612) — supervised semantic tokenizer + flow-matching decoder 的最干净 reference 实现。
- [Step-Audio paper (arXiv 2502.11946)](https://arxiv.org/abs/2502.11946) — 双 tokenizer 路线 + 中文方言情感数据 pipeline 描述详尽。
- [Llama-Omni paper (arXiv 2409.06666)](https://arxiv.org/abs/2409.06666) — 开源研究端最易复现 baseline，4 GPU 3 天，理解 audio-LLM 训练最低门槛入口。
- [Kyutai Moshi 在线 demo](https://moshi.chat/) — 唯一可现场体验 Moshi 式真双工的入口，对照 GPT-4o Realtime 体感差异明显。
- [OpenAI Realtime API docs](https://platform.openai.com/docs/guides/realtime) — 不是 paper，但是从 API 行为反推 GPT-4o 双工实现的唯一一手材料。
- [Awesome-Speech-LLM list](https://github.com/ddlBoJack/Awesome-Speech-Language-Model) — 社区维护的 speech LM paper/code 索引，更新到 2026。

[^gpt4o]: https://openai.com/index/hello-gpt-4o/
[^realtime-ga]: https://openai.com/index/introducing-gpt-realtime/
[^moshi]: https://arxiv.org/abs/2410.00037
[^qwen2audio]: https://arxiv.org/abs/2407.10759
[^qwen25omni]: https://arxiv.org/abs/2503.20215
[^qwen3omni]: https://arxiv.org/abs/2509.17765
[^stepaudio]: https://arxiv.org/abs/2502.11946
[^stepaudio2]: https://arxiv.org/abs/2507.16632
[^glm4voice]: https://arxiv.org/abs/2412.02612
[^glm4voice-gh]: https://github.com/THUDM/GLM-4-Voice
[^llamaomni]: https://arxiv.org/abs/2409.06666
[^llamaomni2]: https://arxiv.org/abs/2505.02625
[^kimiaudio]: https://arxiv.org/abs/2504.18425
[^minicpm-o]: https://huggingface.co/openbmb/MiniCPM-o-2_6
[^snac]: https://arxiv.org/abs/2410.14411
[^encodec]: https://arxiv.org/abs/2210.13438
[^airbench]: https://arxiv.org/abs/2402.07729
[^mmau]: https://arxiv.org/abs/2410.19168
[^voicebench]: https://arxiv.org/abs/2410.17196
[^aa-speech]: https://artificialanalysis.ai/text-to-speech
[^opencompass-audio]: https://opencompass.org.cn/
