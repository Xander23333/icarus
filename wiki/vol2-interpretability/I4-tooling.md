## I4 — Interpretability tooling 实用目录（截至 2026-05）

## 路线定位

interp 工具链 2024-2026 已经分裂成 **三层 stack**：(1) 底层 hook / activation surgery（TransformerLens, nnsight, Captum），(2) feature-level SAE 训练与分析（SAELens, Neuronpedia），(3) 托管 steering / feature API（Goodfire Ember）。给评测团队的核心建议：**先想清楚要回答的问题在哪一层**——是「这条 prompt 走了哪条 circuit」（层1），还是「模型在 reward hack 时哪些 feature 亮了」（层2），还是「我想在 prod 流量上批量 steer 一个行为」（层3）。选错层会浪费 2-4 周。

下面按层给 cheat sheet，每个工具列：**适合什么 / 不适合什么 / 已知坑**。

---

## 层 1：hook & activation 操作

### TransformerLens（aka HookedTransformer）

- 维护者：Neel Nanda 起家，2024 起社区接管，仓库迁至 [TransformerLensOrg/TransformerLens](https://github.com/TransformerLensOrg/TransformerLens)。
- 设计哲学：把 HF 模型 **重写成统一的 hook 友好结构**（attn 拆成 q/k/v/z/result，MLP 拆成 pre/post），每个张量都有 `HookPoint`，可以 `model.run_with_cache()` 一次抓全。
- 适合：mech interp 论文复现、circuit 找 head、activation patching、attribution patching、small/medium 模型（≤30B，多卡支持差）。
- 不适合：(1) 跑 inference throughput——比 HF 慢 1.5-2×，因为为了 hook 友好牺牲了 fused kernel；(2) 30B+ 模型——多 GPU sharding 一直是痛点，Llama-70B 级别要自己 patch；(3) MoE——Mixtral / DeepSeek / Qwen-MoE 支持滞后官方发布常常 3-6 个月，且 expert routing hook 接口不稳定 [uncertain, 以 2026-05 仓库 issue tracker 为准]。
- 已知坑：版本之间 hook name 偶尔改名（如 `blocks.{i}.attn.hook_result` 默认 off，要 `set_use_attn_result(True)`，开了之后显存爆炸）。

### nnsight

- 主页：[nnsight.net](https://nnsight.net)，David Bau 组（NDIF, Northeastern）+ MIT, 2024 NeurIPS 论文 [arxiv 2407.14561](https://arxiv.org/abs/2407.14561)。
- 设计哲学：**"trace" context manager + 远程执行**。你写的 python 看起来像本地操作 tensor，实际是构造了一个图，发到远端 GPU cluster（NDIF 提供免费 Llama-405B / DeepSeek-V3 级别访问，需要申请）执行。
- 适合：(1) 想在 **不下载 405B 权重** 的前提下做 activation patching / probing；(2) 学术团队没自己的大集群；(3) 比 TransformerLens 更通用——直接 wrap 任意 HF / vLLM 模型，不需要重写 forward。
- 不适合：高 throughput 实验（每次 trace 有网络 round-trip 开销）；需要严格隐私的内部数据（要上传到 NDIF）。
- 与 TransformerLens 关系：nnsight 0.3+ 提供了 `LanguageModel` wrapper 兼容大部分 TransformerLens patching workflow，但 cache 语义和 hook name 习惯不同，迁移要重写。

### Captum

- 维护者：Meta PyTorch 团队，[captum.ai](https://captum.ai)。老牌（2019 起），2024-2026 仍在更新但节奏慢。
- 适合：**经典 attribution**——Integrated Gradients, DeepLIFT, SHAP, LIME, Layer Conductance。视觉 / 表格模型的可解释性。
- 对 LLM：能用但不爽——token-level IG 在长 context 上 OOM，没有原生 KV cache 支持。LLM attribution 更推荐 Inseq。
- 用法定位：如果你的评测涉及 **vision encoder**（Qwen-VL 的 ViT 部分）或者要给 reward model 做 feature attribution，Captum 仍然是最成熟的。

### Inseq

- 仓库：[inseq-team/inseq](https://github.com/inseq-team/inseq)，论文 [arxiv 2302.13942](https://arxiv.org/abs/2302.13942)。
- 定位：**seq2seq / decoder 专用 attribution**，把 Captum 那套 IG / attention rollout / gradient×input 包成 `inseq.load_model("HF_id", "saliency")` 一行调用，返回 token×token 热力图。
- 适合评测场景：翻译 / 摘要任务调试，看模型抄了 source 哪几个 token；RAG 场景看答案哪部分来自 retrieved doc。
- 不适合：mech interp（attribution ≠ causal），circuit-level 分析还是要回 TransformerLens / nnsight。

---

## 层 2：SAE / feature-level

### SAELens

- 仓库：[jbloomAus/SAELens](https://github.com/jbloomAus/SAELens)，Joseph Bloom + Decode Research 维护。
- 功能：(1) **训练** SAE（支持 standard, gated, top-k, jump-ReLU, BatchTopK, Matryoshka 等 2024-2026 出现的所有主要变体）；(2) **加载预训练 SAE**——通过 `SAE.from_pretrained()` 拉 HF 上的 release，覆盖 GPT-2, Pythia, Gemma-2-2B/9B（Gemma Scope 全套）, Llama-3-8B, Qwen2.5 子集。
- 适合：自己模型上训 SAE、跑 feature dashboard、做 feature ablation 评测。和 TransformerLens 深度耦合（hook 上挂 SAE 一行）。
- 不适合：Frontier 闭源模型（GPT-5 / Claude / Gemini-2.5）——这些只能走 Goodfire / Anthropic 内部。
- 已知坑：训 SAE 显存吃得猛，9B 模型 residual stream 上训 16× dictionary 要 80GB×多卡，且超参对 dead feature 比例极敏感（L1 coef / top-k k 选错，30%+ feature 死掉）。Anthropic 2024-06 [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/) 和 DeepMind 2024-08 [Gemma Scope](https://arxiv.org/abs/2408.05147) 的 recipe 是当前 baseline。

### Neuronpedia

- 站点：[neuronpedia.org](https://neuronpedia.org)，Johnny Lin 维护，事实上的 **SAE feature 公共浏览器**。
- 功能：(1) 浏览已训 SAE 的每个 feature——top activating examples, logit attribution, auto-generated explanation（GPT-4 / Claude 自动标注）；(2) **steering playground**——在线对 Gemma-2-2B 等模型调 feature 系数看输出变化；(3) [API](https://www.neuronpedia.org/api-doc) 可以程序化拉 feature 信息、跑 search-features-by-explanation。
- 给评测的价值：当你的模型在某个 benchmark 上失败（比如多步推理 reward hack），可以快速搜「相关 feature」，比从零训 SAE 快得多。
- 局限：覆盖的模型仍以 Gemma / GPT-2 / Llama 小模型为主，Qwen / DeepSeek 的官方 SAE 截至 2026-05 [uncertain — 没找到官方 release，社区有零散 release 但质量参差]。

### Goodfire Ember API

- 公司：Goodfire AI，[goodfire.ai](https://goodfire.ai)，2024 成立，Tom McGrath（前 DeepMind interp）等创办。2024-11 [Series A](https://goodfire.ai/blog/announcing-our-7m-seed-round) [uncertain on round size, double-check] 后开放 Ember API。
- 提供：托管的 **Llama-3-70B / 405B + Llama-4** 上预训好的 SAE feature 接口。SDK 调用方式像 OpenAI——`client.features.search("deception")` 返回 feature id，然后在 chat completion 里 `controller.set(feature_id, 0.5)` 就能 steer。
- 适合：(1) 不想自己训 SAE 又想在 prod 流量上加 steering；(2) red-team / eval——批量扫某 prompt 集合在哪些 feature 上激活异常；(3) 给产品加 "personality" / 内容过滤的替代方案（比 system prompt 鲁棒）。
- 不适合：闭源 frontier（不支持 GPT-5 / Claude / Gemini）；需要 reproducible research——SAE 权重不公开，feature id 可能随 SAE 重训失效。
- 定价 [uncertain — 以官网为准]：按 token + feature 操作计费，比纯 inference 贵 ~2-3×。

### EleutherAI `sae` / `sparsify`

- 仓库：[EleutherAI/sae](https://github.com/EleutherAI/sae) 及后续 `sparsify`。
- 定位：SAELens 的轻量替代，更偏研究用——top-k SAE 训练高度优化，Pythia / Llama 上有 reference run。
- 与 SAELens 取舍：要 **训** 大规模 SAE 选 EleutherAI sparsify（更快、ddp 更稳）；要 **分析 / dashboard / 配 TransformerLens** 选 SAELens。

---

## 层 3：周边

### pyvene（Stanford NLP）

- [stanfordnlp/pyvene](https://github.com/stanfordnlp/pyvene)，论文 [arxiv 2403.07809](https://arxiv.org/abs/2403.07809)。
- 定位：**intervention 框架**，统一表达 activation patching / DAS / ReFT。和 nnsight 有重叠但更声明式（写 config 而不是 trace）。
- 给评测：如果要做 **causal abstraction**（验证模型内部是否真的实现了某个算法），pyvene + DAS 是标准选择。

### TransformerLens 之外的 mech-interp 杂项

- [pyreft](https://github.com/stanfordnlp/pyreft) — ReFT representation finetuning，可以当做 "可控 steering 的低秩版本"。
- [sae_vis](https://github.com/callummcdougall/sae_vis) — Callum McDougall 的 SAE feature dashboard 生成器，被 SAELens / Neuronpedia 内部用。
- [tuned-lens](https://github.com/AlignmentResearch/tuned-lens) / logit lens — 看中间层 readout，老但有用。

---

## 选型 cheat sheet（按评测任务类型）

| 评测场景 | 首选工具 | 备选 |
|---|---|---|
| 复现某 mech interp paper（小模型，circuit-level） | TransformerLens + SAELens | nnsight |
| 大模型 (70B+) 上做 activation patching / probing | nnsight (NDIF) | TransformerLens patched 多卡 |
| 想知道模型在 benchmark fail 时 "在想什么" | Neuronpedia search → SAELens 本地复跑 | Goodfire（如果是 Llama） |
| Prod 上加内容/行为控制 | Goodfire Ember | system prompt + classifier（非 interp 路线） |
| 多模态（VL 模型 vision 侧）attribution | Captum | Inseq（仅文本侧） |
| Token-level "答案来自 prompt 哪里"（RAG eval） | Inseq | Captum |
| Causal abstraction / 验证算法假设 | pyvene + DAS | TransformerLens activation patching |
| 闭源 frontier（GPT-5 / Claude / Gemini） | 厂商 API（基本没有）→ behavioral probing | [unknown — 截至 2026-05 没有公开 SAE/feature API for these] |

---

## 未知与争议

- **Qwen / DeepSeek 系列的官方 SAE 状态** [uncertain]：Anthropic / DeepMind 都放了官方 SAE（Claude internal, Gemma Scope），但中国 lab 截至 2026-05 没看到对应级别的 release。Qwen 团队如果要做内部 interp，目前要么自己用 SAELens 训，要么找学术合作。
- **SAE 是否真的找到了"feature"**：2024 末 [Anthropic critique](https://transformer-circuits.pub/2024/october-update/index.html) [uncertain url—check] 和后续工作显示 SAE feature 有 **feature splitting / absorption** 问题，同一概念在不同 SAE size 下被切成多个，下游评测要谨慎用单 feature 做结论。
- **steering 的 OOD 行为**：Goodfire / Neuronpedia 的 steering 在 demo prompt 上漂亮，但拉到 long-context / agentic trajectory 上经常崩；评测时务必测 steering 强度对 general capability 的 tax。

---

## 推荐外部材料

- [ARENA 3.0 mech interp track](https://www.arena.education/) — Callum McDougall 编的 hands-on tutorial，TransformerLens + SAELens 入门最快路径。
- [Neel Nanda — Concrete Open Problems in Mech Interp](https://www.alignmentforum.org/posts/LbrPTJ4fmABEdEnLf/200-cop-in-mi-introduction) — 想找 research idea 的 starting point。
- [Anthropic — Scaling Monosemanticity (2024-05)](https://transformer-circuits.pub/2024/scaling-monosemanticity/) 和 [Gemma Scope (2024-08)](https://arxiv.org/abs/2408.05147) — 现代 SAE 训练 recipe 的两篇 anchor paper。
- [nnsight tutorials](https://nnsight.net/tutorials/) — 远程大模型 interp 的入门，附 NDIF 申请说明。
- [Neuronpedia blog](https://www.neuronpedia.org/blog) — Johnny Lin 写的 SAE feature analysis 实例，适合给 eval team onboard 用。
- [Goodfire research blog](https://goodfire.ai/research) — 工业界 SAE 应用案例（含失败模式）。
