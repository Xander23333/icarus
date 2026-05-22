# Brain-inspired / Neuromorphic / Predictive-coding

> **范围**：本节覆盖三条**离 frontier LLM 最远但仍在严肃推进**的非主流路线，截止 2026-05：
> - **F1** Spiking Neural Network LLM（SpikeGPT / Spikformer / SpikingBrain-7B 等）
> - **F2** 神经形态硬件（Intel Loihi-2、BrainChip Akida-2、IBM NorthPole）
> - **F3** Predictive coding / Active inference（Karl Friston / VERSES AI、Numenta Thousand Brains）
>
> 读者 = Qwen agentic 评测 owner。**先说结论：这三条线 2026-05 之前都没有任何模型 / 芯片在 LLM 主流 benchmark 上接近 SOTA**。本节存在的意义是给评测 owner 一个"为什么不必把测试预算分给它们、以及未来 12–24 月该盯哪些信号"的最小完备 picture，而不是 hype。

## 路线定位（1 段）

三条线共享一个反主流命题——"**dense FP transformer + GPU 不是终局**"——但选了不同维度去反对：F1 在算子上换成 binary spike / event-driven 以追功耗，F2 在硅上把 memory 和 compute 物理合一去掉 von-Neumann bottleneck，F3 在算法目标函数上用 free-energy / hierarchical generative model 取代 next-token CE。2024–2026 三条线**都没有出现可比 GPT-4o / Claude 4 / Gemini 2.5 的产出**：SNN LLM 最大的 SpikingBrain-7B (2025-09) 只能对标 Llama-2-7B 量级且推理硬件仍是 GPU；neuromorphic 芯片全部停留在 sub-watt edge sensing / keyword-spotting demo（Loihi-2 单芯片 1M neurons、NorthPole 22B 参数纯整数推理上限），**无 frontier-scale training**；VERSES 的 "Genius" 平台和 Numenta 的 Thousand Brains 在 2025 都公开了产品/开源[^verses-genius][^numenta-tbp]，但**没有任何独立第三方 reproduce 在 MMLU / SWE-bench / ARC-AGI 级别基准上的结果**。所以本节定位是 **watchlist，不是 buylist**。

## 代表工作清单

| 工作/事件 | 发布日 | 类别 | 关键变化 | 一手 source |
|---|---|---|---|---|
| SpikeGPT | 2023-02 | F1 SNN | 第一个 generative SNN LM，~260M 参数，基于 RWKV-style recurrence + binary spike | [arxiv:2302.13939](https://arxiv.org/abs/2302.13939) |
| Spikformer | 2022-09 / ICLR 2023 | F1 SNN | Spiking Self-Attention (SSA)，避免 softmax，全 spike 运算 | [arxiv:2209.15425](https://arxiv.org/abs/2209.15425) |
| Spike-driven Transformer V2 / V3 | 2024 / 2025 | F1 SNN | scaling 到 ImageNet-1k SOTA-for-SNN（80%+ top-1），但仍远低于 ViT/DINOv2 | [arxiv:2404.03663](https://arxiv.org/abs/2404.03663) |
| **SpikingBrain-7B** | 2025-09 | F1 SNN | 中科院自动化所，宣称"首个 7B spike-based LLM"；hybrid linear + spike，长上下文友好 | [arxiv:2509.05276](https://arxiv.org/abs/2509.05276) |
| Intel **Loihi-2** | 2021-09 发布；Hala Point 1152 芯片 system 2024-04 | F2 HW | 7nm，1M neurons/chip；Hala Point 1.15B neurons、20 PetaOPS @ 2.6 kW | [Intel newsroom 2024-04-17](https://www.intel.com/content/www/us/en/newsroom/news/intel-builds-worlds-largest-neuromorphic-system.html) |
| BrainChip **Akida 2.0** IP | 2023-03；Akida Pico 2024-10 | F2 HW | event-based，目标 always-on edge（mW 级），支持 TENNs (temporal CNN) | [BrainChip Akida 2.0 page](https://brainchip.com/akida-generations/)；[Akida Pico 2024-10 PR](https://brainchip.com/brainchip-introduces-akida-pico/) |
| IBM **NorthPole** | 2023-10 Science 论文；2024-2025 后续 LLM demo | F2 HW | 12nm，22B-param 整数推理；on-chip SRAM 取消 DRAM bottleneck；功耗效率宣称 25× 比同期 GPU | [Science 2023-10-19](https://www.science.org/doi/10.1126/science.adh1174)；[IBM Research blog 2023-10](https://research.ibm.com/blog/northpole-ibm-ai-chip) |
| Friston et al. "free energy principle" 综述 | 2023-2024 持续 | F3 算法 | active inference 数学框架更新；主推 hierarchical generative model | [Nat Rev Neurosci 2010 原始](https://www.nature.com/articles/nrn2787)；[arxiv:2306.10874 (2023 综述)](https://arxiv.org/abs/2306.10874) |
| VERSES AI "Genius" 平台 beta | 2025-03 | F3 商业 | active-inference based agent platform，宣称 sample efficiency >> deep RL | [VERSES blog 2025-03](https://www.verses.ai/blog)；论文 [arxiv:2405.19076](https://arxiv.org/abs/2405.19076) (Genius white paper) |
| VERSES vs DeepMind "Mastermind" 实验 | 2024-08 | F3 验证 | VERSES 自报在 Mastermind benchmark 上击败 DeepMind 的 RL baseline；**未经独立复现** | [VERSES PR 2024-08](https://www.verses.ai/press/verses-ai-announces-genius-beats-deepminds-ai) |
| Numenta **Thousand Brains Project** 开源 | 2024-10 alpha；2025 持续 | F3 算法 | 基于 cortical column 假设的 sensorimotor learning 框架（monty）；非 deep learning | [thousandbrainsproject.org](https://www.thousandbrainsproject.org/)；[GitHub thousandbrainsproject/tbp.monty](https://github.com/thousandbrainsproject/tbp.monty) |
| 2026-05 状态 | — | — | 三条线**均未进入** frontier LLM/agent 评测视野；SpikingBrain-7B 是 SNN 侧最接近"可用 LLM"的产出，但仍需 GPU 训练并在 GPU/CUDA 上推理 | — |

## F1 SNN LLM：算子换了，故事没换

### 1. SNN 的基本机制（背景一句话）

每个 neuron 维护 membrane potential $V(t)$，到阈值发 binary spike 后 reset。Loss 通过 surrogate gradient（如 fast sigmoid）反传——本质是把不可导的 step 函数在 backward 阶段换成光滑近似[^spikformer]。这让 SNN 训练**仍然在 GPU/PyTorch 里跑**，跟"低功耗"完全无关，低功耗只在推理部署到 neuromorphic 芯片才兑现。

### 2. SpikeGPT (2023-02)

[arxiv:2302.13939](https://arxiv.org/abs/2302.13939)：

- 借 RWKV 的 time-mix / channel-mix（避免 softmax attention），把激活替换为 spike。
- 参数最大 260M，Enwik8 / WikiText-103 上 BPC 接近 GPT-2 small 同规模，**远未到 GPT-2 medium**。
- 主卖点是宣称推理时 FLOPs ↓ 20×（前提：部署在支持 event-driven 的硬件上，论文只在 GPU 评测）。

### 3. Spikformer 系列

[arxiv:2209.15425](https://arxiv.org/abs/2209.15425) 提出 Spiking Self-Attention：Q/K/V 都是 spike tensor，**用 element-wise 乘 + 累加替代 softmax(QK^T)V**。V2/V3 上 ImageNet 80%+ top-1[^spikedriven-v2]，但同期 DINOv2 ViT-L 已经 86%+。在 LLM 任务上 Spikformer 路线**没有出 frontier-scale 模型**。

### 4. SpikingBrain-7B (2025-09)

[arxiv:2509.05276](https://arxiv.org/abs/2509.05276)：

- 中科院自动化所 + 鹏城实验室。架构是 **hybrid linear attention + spike activation**，号称"脑启发"，但本质更接近 Mamba/RWKV 加 spike 化激活。
- 训练数据 ~2T tokens（公开 corpus），benchmark 报告对标 **Llama-2-7B**，不是 Llama-3 / Qwen2.5。
- MMLU 报告 ~55（论文 Table 4），CMMLU 60+；**和 2023-Q3 模型同档**，落后 2025 同尺寸 SOTA（Qwen2.5-7B MMLU 74+）约 20 点。
- 硬件：训练在国产 GPU 集群（MetaX C500），**推理也仍在 GPU**——neuromorphic 部署被作为 future work。

### 5. 为什么 SNN 在 LLM 上落后

- **训练算力没省**：surrogate gradient 训练 cost 与同规模 dense transformer 同量级甚至更高（时间步 T 倍）。
- **数据/scaling 没省**：仍需 T-级 token 预训练，没人有钱在 SNN 上烧 GPT-4 级别预算去验证 scaling law。
- **推理硬件链路断裂**：理论低功耗只在 neuromorphic 芯片兑现，而 Loihi-2 / Akida 单芯片 neuron / 参数容量**不足以承载 7B+ LLM**——一片 Loihi-2 只有 1M neurons，Hala Point 整柜 1.15B neurons 也只在 demo SNN 上跑（Intel 自己的 case study 仍是 vision / robotics 推理，不是 LLM）[^hala-point]。
- **生态**：没有 vLLM/SGLang/FlashAttention 等量级的工程栈。

## F2 神经形态硬件：研究里程碑，部署 niche

### Intel Loihi-2 / Hala Point

- 单芯片 1M neurons、120M synapses，7nm[^loihi2]。
- Hala Point (2024-04) 1152 chips：1.15B neurons / 128B synapses，2.6 kW，宣称在某些 sparse workload 上能效 **15× over conventional GPU**[^hala-point]。注意：(a) 比较 baseline 是 V100 时代而非 H100/B200；(b) workload 是 sparse coding / optimization，不是 transformer。
- 2025 Intel 内部 Neuromorphic Computing Lab 重组传闻较多，**Intel 整体战略下放神经形态优先级**[uncertain — 没有 Intel 官方 confirm 的关停声明]。

### BrainChip Akida 2 / Akida Pico

- IP 授权模式（不是自家流片大芯片），主打 always-on edge：keyword spotting、vibration anomaly、health wearable，功耗 sub-mW – mW[^akida-pico]。
- Akida 2.0 引入 TENN（Temporal Event-based Neural Network），把 1D 时序 CNN 转成 event 流。
- **没有任何 LLM workload 路线图**；定位就是 MCU 级 AI co-processor 竞争 Syntiant / Ambiq。

### IBM NorthPole

- 12nm，256 cores，每 core 本地 SRAM；**全片整数算术，没有 off-chip DRAM**[^northpole]。
- Science 2023 论文展示 ResNet-50 ImageNet 25× 能效 over GPU；后续 IBM Research blog 报告**最多到 3B param LLM** 单卡推理 demo（2024 内部），未在 frontier scale 复现。
- 2025 IBM 把 NorthPole 主要包装进 enterprise inference 故事，但 watsonx 平台公开 SKU 仍是 GPU。

### 共同问题

1. **训练不在神经形态硬件上做**——所有 SNN 都仍然在 GPU 用 surrogate gradient 训。
2. **memory capacity 跟不上 LLM**：把 7B param 塞进单芯片 on-chip SRAM 物理上做不到（7B × INT8 = 7 GB，远超任何 neuromorphic chip on-chip SRAM）。多片互联又会重新引入数据搬运瓶颈，部分抵消优势。
3. **编程模型割裂**：没有 PyTorch/CUDA 级生态，Lava (Intel)、MetaTF (BrainChip)、NorthPole SDK 互不兼容。

## F3 Predictive coding / Active inference：理论强，工程弱

### Karl Friston / Active Inference

free-energy principle：agent minimize variational free energy $F = \mathrm{KL}(q(s)\|p(s\mid o)) - \log p(o)$，统一感知（perception = inference）和行动（action = inference on policies）。数学优雅[^friston-2023]，但**把它 scale 到 GPT-4 级别 task 的工程路径不清楚**——hierarchical generative model 的精确推断在高维状态空间下计算量爆炸，所有现实实现都得做大量近似。

### VERSES AI "Genius"

- 商业公司，Friston 是 Chief Scientist。
- 2024-08 PR 宣称在 Mastermind 游戏上击败 DeepMind RL baseline[^verses-mastermind]——**注意这是公司自报，没有独立第三方在 NeurIPS/ICLR 复现**；Mastermind 也不是 community benchmark。
- 2025-03 Genius beta，定位 "智能体平台"，强调 sample efficiency 和可解释性。**截至 2026-05 没有 LLM / agentic-coding benchmark（SWE-bench、GAIA、τ-bench）数据**。
- 评测 owner 视角：**目前没有可纳入对比的 number**，但值得 watchlist——一旦有第三方在标准 benchmark 复现就该重新评估。

### Numenta Thousand Brains Project

- Jeff Hawkins 多年下注。核心假设：新皮层由数千个 cortical column 并行学习同一个 object 的不同 reference frame，最后投票[^numenta-tbp]。
- 2024-10 开源 **Monty** 框架（github thousandbrainsproject/tbp.monty）。完全**不是 deep learning**：sensorimotor learning，feature-at-location，agent 主动探索。
- 当前 demo 规模：3D 对象识别 / 操控，~77 YCB-like 对象。**和 LLM 任务无直接接口**，也未在视觉 SOTA 榜上出现。
- Numenta 自己 2023 也发过 transformer sparsity 论文走 mainstream 路线[^numenta-sparse]，说明他们也清楚 TBP 短期内不会替代 transformer。

## 与 eval / benchmark 的接口

- **不要分配 frontier benchmark 预算**给这三条线，截至 2026-05 没有任何模型能进 MMLU/SWE-bench/GPQA/AIME top-50。
- **可以分配的精力**：
  - 跟踪 SpikingBrain 后续版本（如果出 30B+ 且在 standard benchmark 上接近 Llama-3 同规模，是信号）。
  - 跟踪 NorthPole 是否出可购买的 inference SKU 并给出 transformer LLM 推理能效数字。
  - 跟踪 VERSES 是否进 GAIA / τ-bench / SWE-bench 榜——这是它从 PR 走向严肃 AI 圈的必要步骤。

## 未知与争议

- **SpikingBrain-7B 的"脑启发"成分有多少是 marketing**：[推测] 架构主体是 hybrid linear attention，spike 激活的实际增益（vs 同样架构用 ReLU/SiLU）论文没有完整 ablation。
- **Loihi-2 / Hala Point 2025-2026 路线图**：[unknown — Intel 公开材料 2024 之后明显减少，没有第三方 confirm 是否还在持续投入]。
- **VERSES Mastermind 结果可信度**：DeepMind 没有公开回应；独立学界没有 reproduce。建议保持怀疑直到第三方复现。
- **NorthPole 商业化形态**：IBM 公开 SKU 仍是 GPU/CPU，NorthPole 是否会作为 cloud inference 实例公开售卖 [unknown]。

## 推荐外部材料

- [Eshraghian "Training Spiking Neural Networks Using Lessons From Deep Learning"](https://arxiv.org/abs/2109.12894) — SNN + surrogate gradient 入门 review，SpikeGPT 作者写的。
- [Intel Lava framework docs](https://lava-nc.org/) — 想动手摸 Loihi-2 / Hala Point 的唯一可行入口。
- [IBM NorthPole Science 2023 paper (preprint mirror)](https://research.ibm.com/publications/neural-inference-at-the-frontier-of-energy-space-and-time) — 一手能效数字。
- [Karl Friston 2023 active inference textbook (MIT Press, free PDF)](https://mitpress.mit.edu/9780262045353/active-inference/) — 想认真看 F3 数学的最快路径。
- [Numenta Thousand Brains 介绍 talk (Jeff Hawkins 2024)](https://www.youtube.com/@Numenta) — 比论文更快理解 TBP 的世界观。
- [BrainChip Akida technical reference](https://brainchip.com/wp-content/uploads/2023/04/BrainChip-Akida-Neural-Processor-IP.pdf) — Edge SNN 部署的现实约束清单。
- [Yann LeCun 2025 多次 talk 强调 "JEPA, not SNN"](https://www.youtube.com/results?search_query=lecun+jepa+2025) — 主流 deep learning 阵营对 SNN 的态度（不看好），可作 sanity check。

[^spikformer]: Zhou et al., "Spikformer: When Spiking Neural Network Meets Transformer", [arxiv:2209.15425](https://arxiv.org/abs/2209.15425).
[^spikedriven-v2]: Yao et al., "Spike-driven Transformer V2", [arxiv:2404.03663](https://arxiv.org/abs/2404.03663).
[^hala-point]: Intel, "Intel Builds World's Largest Neuromorphic System", 2024-04-17, [intel.com newsroom](https://www.intel.com/content/www/us/en/newsroom/news/intel-builds-worlds-largest-neuromorphic-system.html).
[^loihi2]: Intel, "Taking Neuromorphic Computing to the Next Level with Loihi 2", 2021, [intel.com](https://www.intel.com/content/www/us/en/research/neuromorphic-computing-loihi-2-technology-brief.html).
[^akida-pico]: BrainChip, "BrainChip Introduces Akida Pico", 2024-10, [brainchip.com](https://brainchip.com/brainchip-introduces-akida-pico/).
[^northpole]: Modha et al., "Neural inference at the frontier of energy, space, and time", Science 382, 329 (2023), [DOI:10.1126/science.adh1174](https://www.science.org/doi/10.1126/science.adh1174).
[^friston-2023]: Parr, Pezzulo, Friston, *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior*, MIT Press 2022; 2023 综述 [arxiv:2306.10874](https://arxiv.org/abs/2306.10874).
[^verses-genius]: VERSES AI, "Introducing Genius", 2025-03, [verses.ai/blog](https://www.verses.ai/blog).
[^verses-mastermind]: VERSES AI press release, 2024-08, [verses.ai/press](https://www.verses.ai/press/verses-ai-announces-genius-beats-deepminds-ai).
[^numenta-tbp]: Thousand Brains Project, [thousandbrainsproject.org](https://www.thousandbrainsproject.org/) and [github tbp.monty](https://github.com/thousandbrainsproject/tbp.monty).
[^numenta-sparse]: Numenta, "Sparsity Enables 50x Performance Acceleration in Deep Learning Networks", 2023, [numenta.com blog](https://www.numenta.com/blog/).
