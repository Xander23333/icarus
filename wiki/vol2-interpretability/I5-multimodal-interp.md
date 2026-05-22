# Multimodal / VLM Interpretability

## 路线定位
比起纯文本 mech-interp（SAE、circuits、attribution graph 一整套 stack），多模态可解释性整体落后 2-3 年。绝大多数工作仍停在 "neuron-level probing + attention map 可视化 + cross-modal alignment 分析"，circuit-level 的因果级证据非常稀少。Anthropic 2024 起把 SAE 推到 Claude vision 上、DeepMind / OpenAI 在 CLIP/ViT 上做了多模态 neuron 字典，但 VLM（LLaVA、Qwen-VL、InternVL、GPT-4V/4o）这一支至今没有像 GPT-2 small 那样被彻底拆解过。读者如果做 Qwen-VL 评测，需要清楚：现在能拿来的工具基本都是 diagnostic（看哪里坏了），还做不到 mechanistic（解释 *为什么* 这样算）。

## 几条主线

### 1. CLIP / 视觉编码器侧：multimodal neurons
- **Multimodal Neurons in Artificial Neural Networks** (Goh et al., OpenAI/Distill 2021) — 在 CLIP RN50x4 里发现单个神经元对 "Spider-Man 的照片 / 卡通 / 文字 'spider'" 同时激活，给出了多模态抽象概念存在的第一份证据 [distill.pub/2021/multimodal-neurons](https://distill.pub/2021/multimodal-neurons/)。
- 后续 typographic attack（贴 "iPod" 标签让 CLIP 把苹果当 iPod）就是这套表征的直接攻击面。
- **Multimodal Neurons in Pretrained Text-Only Transformers** (Schwettmann et al., 2023, arxiv [2308.01544](https://arxiv.org/abs/2308.01544)) — 在 LiMBeR 里把 image patch 投到 frozen GPT-J，找到 image→text 之间起翻译作用的 MLP 神经元，证明 "多模态对齐" 大量发生在 LM 的 MLP 而不是 projection layer。
- **Sparse Autoencoders on CLIP / SigLIP**：2024-2025 多组工作（Bhalla et al. "Interpreting CLIP with Sparse Linear Concept Embeddings" arxiv [2402.10376](https://arxiv.org/abs/2402.10376)，Rao et al. "Discover-then-Name" 等）把 SAE 套到 ViT residual stream，能拆出 "条纹"、"医院 logo"、"夕阳" 这类 monosemantic 概念，已用于 CLIP debias 与 zero-shot 分类的特征归因。

### 2. VLM 内部：LLaVA 一系的拆解
- **LLaVA** 架构 = ViT(CLIP/SigLIP) + MLP projector + LLM（Vicuna/Qwen），可解释性研究多在这套 stack 上做 [arxiv 2304.08485](https://arxiv.org/abs/2304.08485)。
- **Logit Lens for VLM**：把每一层 residual 投到 unembedding 看 token 分布。Jiang et al. "Interpreting and Editing Vision-Language Representations to Mitigate Hallucinations" (arxiv [2410.02762](https://arxiv.org/abs/2410.02762)) 用 logit lens 发现 LLaVA 在中间层就已经决定要不要 hallucinate 某 object，并据此做 representation editing 降幻觉。Neo et al. "Towards Interpreting Visual Information Processing in VLMs" (arxiv [2406.16320](https://arxiv.org/abs/2406.16320)) 类似结论：object token 信息在 LM 中段被 register 化到少数 image token 上，后段几乎只读这几个 summary token。
- **LLaVA-MoLE / sparse experts 可视化**：MoE 化的 VLM（LLaVA-MoLE arxiv [2401.16160](https://arxiv.org/abs/2401.16160)，CuMo，MoVA）让 expert routing 自然成为可解释信号——可以看 OCR query vs caption query 走的 expert 是否分化。目前只有 routing entropy / load balance 级别的报告，没有 mechanistic claim [uncertain]。
- **Patchscopes-VL / cross-modal patching**：Patchscopes (Ghandeharioun et al., arxiv [2401.06102](https://arxiv.org/abs/2401.06102)) 原本是纯文本 hidden state→自然语言 decode 的框架，2024-2025 多篇把它扩到 VLM：把 image patch 的 hidden state patch 到一个纯文本 prompt（"this represents:"）让 LM 自己说出语义。相关工作如 "Towards Vision-Language Mechanistic Interpretability: A Causal Tracing Tool for BLIP" (Palit et al., arxiv [2308.14179](https://arxiv.org/abs/2308.14179)) 把 ROME causal tracing 搬到 BLIP。这些方法严格说还停在"诊断单 token 语义"层面，没有形成 circuit。

### 3. Cross-modal attention / attribution
- **Attention rollout / relevancy maps**（Chefer et al. CVPR 2021 [arxiv 2103.15679](https://arxiv.org/abs/2103.15679)）至今仍是 VLM 可视化默认 baseline。
- VLM 的 "modality gap"：text token 和 image token 在 LM 中后期被对齐到同一子空间，可以用 linear probe / CKA 度量。Modality gap 现象首报见 Liang et al. NeurIPS 2022 [arxiv 2203.02053](https://arxiv.org/abs/2203.02053)，VLM 内部版本散见 2024 各 hallucination 论文。
- **Image token pruning 作为副产品**：FastV (arxiv [2403.06764](https://arxiv.org/abs/2403.06764)) 发现 LLaVA 第 2 层之后 image token 的 attention weight 急剧衰减，可以剪掉 50% image token 几乎无损——这是一个非常强的 mechanistic 信号：LM 在浅层就把 visual 信息抽干压到少数 token 里。后续 SparseVLM、VisionZip 都基于此。读者做评测时这条同时意味着：很多 vision benchmark 的实际有效输入远小于声称的 token 数。

### 4. Anthropic / OpenAI / DeepMind 的官方多模态工作
- **Anthropic vision circuits**：Claude 3 / 3.5 是原生多模态，Anthropic 2024-2025 transformer-circuits 月报有 vision 相关 stub（如对 image-conditioned features 的 SAE 训练）但远不如纯文本 "Scaling Monosemanticity"、"Circuit Tracing" / attribution graph 系统 [transformer-circuits.pub](https://transformer-circuits.pub/)。截至 2026-05 仍未见 VLM 版本的 attribution graph 论文 [uncertain — 可能在内部 demo 阶段]。
- **DeepMind Gemma Scope / vision** ：Gemma Scope (arxiv [2408.05147](https://arxiv.org/abs/2408.05147)) 是纯文本 SAE suite，PaliGemma 的 SAE 公开版本未见 [unknown — 没找到一手 source]。
- **OpenAI GPT-4o / 4V**：没有公开 interpretability 报告。

## 综述与一手 source
- **A Survey on Multimodal Large Language Model Interpretability** / **Explainability for Large Vision-Language Models**（多篇 2024-2025 survey，质量参差）— 比较系统的一篇是 Dang et al. "Explainable and Interpretable Multimodal Large Language Models: A Comprehensive Survey" arxiv [2412.02104](https://arxiv.org/abs/2412.02104)，把 saliency、probing、causal tracing、SAE、mech-interp 在 VLM 上的进展按 input/internal/output 三层组织，可作 entry point。
- **Anthropic "Scaling Monosemanticity"** [transformer-circuits.pub/2024/scaling-monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/) — 虽是 Claude 3 Sonnet 纯文本，但其方法论是 VLM SAE 工作的直接模板。

## 对 Qwen-VL 评测的实用启示
1. **Hallucination 诊断**：用 logit lens + object token 的中间层 logit 可以在解码前预测 hallucination，比事后 metric (POPE/CHAIR) 更早。参考 arxiv 2410.02762 的方法。
2. **Visual token budget 评估**：跑 FastV-style pruning 曲线（保留 100% / 50% / 25% image token 的 accuracy）能直接看出该模型究竟有多依赖 visual evidence vs 文本先验。很多 VQA 高分模型在 25% token 下分数几乎不掉——意味着 benchmark 在测语言先验。
3. **Modality gap probe**：在 Qwen-VL hidden state 上跑 linear probe (image vs text token 分类)，看在第几层降到 chance；这个 layer index 与 grounding 类任务表现相关 [推测 — 没有 cross-model 系统报告]。
4. **不要相信 attention map 作为解释**。Jain & Wallace "Attention is not Explanation" 的结论在 VLM 上同样适用，relevancy map / gradient-based 也只是 plausible，不是 faithful。

## 未知与争议
- VLM 里是否存在像 IOI circuit 那种端到端可验证的视觉任务 circuit？截至 2026-05 **没有**公开范例 [unknown]。
- SAE 在 CLIP / SigLIP 上 monosemanticity 评价标准还在吵（automated interp score vs 人工 vs downstream 任务效果）。
- 原生多模态（早融合，如 Chameleon、4o、Gemini）vs late-fusion（LLaVA 系）的可解释性结构是否本质不同？理论上早融合应使 modality gap 消失，但缺乏对照实验 [uncertain]。

## 推荐外部材料
- [Distill: Multimodal Neurons (Goh et al.)](https://distill.pub/2021/multimodal-neurons/) — VLM 可解释性的"创世"文章，看图就够。
- [Anthropic transformer-circuits.pub](https://transformer-circuits.pub/) — 看其 vision-related monthly updates，是目前 frontier-lab 唯一持续公开的 VLM 内部工作。
- [arxiv 2410.02762 — Interpreting and Editing VL Representations to Mitigate Hallucinations](https://arxiv.org/abs/2410.02762) — logit lens + hallucination 干预，方法可直接复刻到 Qwen-VL。
- [arxiv 2403.06764 — FastV](https://arxiv.org/abs/2403.06764) — image token pruning，间接但很强的 mech 证据。
- [arxiv 2406.16320 — Towards Interpreting Visual Info Processing in VLMs](https://arxiv.org/abs/2406.16320) — Neo et al.，LLaVA 内部 visual info flow 系统分析。
- [arxiv 2412.02104 — Explainable/Interpretable MLLM Survey](https://arxiv.org/abs/2412.02104) — 唯一比较完整的多模态可解释性 survey。
- [arxiv 2402.10376 — SpLiCE: Sparse Linear Concept Embeddings for CLIP](https://arxiv.org/abs/2402.10376) — CLIP SAE-like 分解。
- [arxiv 2401.06102 — Patchscopes](https://arxiv.org/abs/2401.06102) — 框架本身是文本，但向 VLM 推广的 baseline。
