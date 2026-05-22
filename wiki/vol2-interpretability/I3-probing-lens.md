# I3 — Probing & Lens techniques（截至 2026-05）

## 路线定位

「lens」家族是 interp 里最便宜、最先上手的一类技术：不训 SAE，不挖 circuit，只在 residual stream 的每一层上**做一次线性/近线性投影**，问一个问题——「这一层此刻的 hidden state 已经『想到了』什么 token / 什么概念？」。从 2020 nostalgebraist 的 logit lens 一路演化到 2024 的 Patchscopes，这条线的核心叙事是：**把 hidden state 翻译成人能读的 token 分布**，工具越来越准，但解释边界也越来越清楚。给评测视角的价值：(1) 调 reasoning / agentic 模型时，看「答案 token 在第几层就 lock-in」是判断 CoT 是不是装饰的最便宜信号；(2) Patchscopes 提供了一种**不挖 circuit 就能验证 hidden state 含义**的范式，做 contamination / memorization 取证非常顺手。

---

## 1. Logit Lens — nostalgebraist, 2020

- 原帖：[interpreting GPT: the logit lens](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens)（LessWrong, 2020-08）。
- 做法：把第 ℓ 层的 residual stream `h_ℓ` 直接乘上**最终的 unembedding 矩阵 `W_U`**（先过 final LayerNorm），得到 logits，看 top-k token。
- 直觉：GPT-2 的 residual stream 是「在最终 vocab basis 上的迭代修正」（iterative inference），每一层都在「往输出空间推一点」，所以中层投影出来的 token 往往是「中间假设」。
- 经验现象（nostalgebraist 帖里 + 后续多人复现）：
  - 早 1/3 层投出来基本是 garbage（与输入 token 相关的字面拷贝）。
  - 中层（GPT-2-XL ≈ 20-35 / 48 层）开始出现「semantically related 但还不对」的 token，比如最终要说 "Paris"，中层是 "France" "capital"。
  - 末 3-5 层 lock-in 到真正的 top-1。
- 致命弱点：**representational drift**。Logit lens 隐含假设「中间层的 basis 和最终 unembedding basis 一致」。这在 GPT-2 上勉强成立，在 LLaMA / Pythia / Qwen 等更现代模型上**经常失败**——中间层 norm scale 不对、basis 旋转过——导致中层投出来全是 `\n`、`the`、`<unk>` 这类 high-norm token。这是 Tuned Lens 要解决的核心问题。

## 2. Tuned Lens — Belrose et al., 2023

- Paper: [Eliciting Latent Predictions from Transformers with the Tuned Lens](https://arxiv.org/abs/2303.08112)（Belrose, Furman, Smith 等，EleutherAI，2023-03）。
- 做法：在每一层 ℓ 训练一个**affine probe `A_ℓ`（一个 d×d 矩阵 + bias）**，目标是让 `LayerNorm(A_ℓ · h_ℓ) · W_U` 的输出分布尽量逼近**最终 logits**（KL divergence loss）。训练数据用预训练 corpus 的子集，每层独立 probe，参数量 ≈ d²（对 7B 模型每层约 16M 参数，全部层加起来 ≈ 0.5B，比 SAE 便宜得多）。
- 关键 claim：
  - 在 Pythia / GPT-NeoX / OPT / LLaMA 上，tuned lens 的**中间层 perplexity 单调下降**（logit lens 经常非单调甚至中段爆炸）。
  - tuned lens 投出的 top-k token **更 semantically coherent**，不再被 high-norm junk token 主导。
  - 可以用作 **anomaly detection**：prompt injection / OOD 输入下，某些层的 tuned-lens KL 会突然飙高。
- 局限：(1) probe 是 per-model 训的，换模型要重训；(2) affine 仍然是线性假设，遇到非线性几何（如 RoPE 旋转、MoE expert switch）会失真；(3) 训练目标是「逼近最终 logits」，所以它**只能看到「最终会输出的东西」**，看不到中间被擦除的假设——这是 Future Lens / Patchscopes 想补的。
- 复现工具：官方 [EleutherAI/tuned-lens](https://github.com/EleutherAI/tuned-lens)，已支持到 LLaMA-3、Qwen-2.5、Pythia 全家。2024-2025 社区给 Mistral、DeepSeek-V2 等也训了 lens 上传到 HF Hub（搜 `tuned-lens`）。

## 3. Direct Logit Attribution（DLA）— Nanda, 2022→

- 主参考：Neel Nanda 的 [A Comprehensive Mechanistic Interpretability Explainer & Glossary](https://www.neelnanda.io/mechanistic-interpretability/glossary)，以及 [TransformerLens DLA tutorial](https://github.com/TransformerLensOrg/TransformerLens)。原始 idea 在 Anthropic [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)（Elhage et al., 2021）。
- 做法：residual stream 是**所有层 / 所有 head / 所有 MLP 输出的线性和**（pre-final-LN 时）。把每个 component 单独乘 `W_U` 投到某个目标 token 方向上，得到「这个 component 对最终 logit 贡献了多少」。
- 与 logit lens 关系：logit lens 是「**所有 component 累加到第 ℓ 层**之后投影」，DLA 是「**单个 component 的增量**投影」。前者看「现在到哪儿了」，后者看「这一步走了多少」。
- 经典用例：
  - IOI（Indirect Object Identification）circuit 里识别 "name mover heads"——这些 head 的 DLA 对正确名字 token 是大正数，对错误名字是大负数。
  - 在做 reasoning 模型 debug 时，看「最终答案 token 的 logit 主要由哪几层、哪几个 head 贡献」——经验上 reasoning model 的贡献会更分散到深层 MLP，而非 attention head。[uncertain, 没有公开 paper 直接说这点，是社区 anecdote]。
- 注意 caveat：DLA **只看「直接经过 unembedding 的路径」**，忽略了「这个 head 写入 residual → 后续 layer 又对它做了非线性处理」的间接贡献。所以 DLA 低估了早层 component 的作用，对 attention pattern「搬运信息给后层处理」的 head 几乎看不到。要补这块得用 attribution patching 或 path patching。

## 4. Future Lens — Pal et al., 2023

- Paper: [Future Lens: Anticipating Subsequent Tokens from a Single Hidden State](https://arxiv.org/abs/2311.04897)（Pal, Sun, Yuan, Wallace, Bau，EMNLP 2023）。
- 核心问题：第 ℓ 层、第 t 个 token 的 hidden state，**已经编码了多少关于 t+1, t+2, …, t+k 的信息？**
- 三种探针方法（论文里都跑了）：
  1. **Linear probe**：直接学一个 W 把 `h_ℓ,t` 映到 t+k token 的 one-hot。
  2. **Causal intervention**：把 `h_ℓ,t` patch 到一个**全新 prompt** 的某个位置上，看后续解码是否带出原 prompt 的 future token。
  3. **Soft prompt**：训一个 prefix，让模型「读」`h_ℓ,t` 然后输出 future token。
- 主要发现（在 GPT-J 6B 上）：
  - 第 t 个 token 在中后层的 hidden state **可以预测 t+1 到 t+3** 的 token，准确率显著高于 random（t+1 接近 48%，t+2 接近 25%，t+3 ≈ 10%）。
  - 这说明 transformer 在 next-token prediction 训练目标下，**自发学到了 multi-token 的「计划」**，不只是局部一步。
  - 这个 finding 后来被 Meta 的 multi-token prediction（[Gloeckle et al. 2024, arxiv 2404.19737](https://arxiv.org/abs/2404.19737)）作为动机引用之一。
- 对评测的意义：在做 speculative decoding / draft model 评估时，Future Lens 提供了一个 **upper-bound 估计**——「base model 的 hidden state 里到底有多少 future 信息可以被 draft 抽出」。

## 5. Patchscopes — Ghandeharioun et al., 2024

- Paper: [Patchscopes: A Unifying Framework for Inspecting Hidden Representations of Language Models](https://arxiv.org/abs/2401.06102)（Ghandeharioun, Caciularu, Geva, Pearce, Reingold，Google DeepMind, ICML 2024）。
- 核心 trick：**不再训 probe，也不依赖 unembedding basis**。要解释某个 hidden state `h*`（取自源 prompt `P_src`，层 ℓ_src，位置 i_src），就把它 **patch 进一个目标 prompt `P_tgt`** 的某个位置（层 ℓ_tgt，位置 i_tgt），然后让模型**自然语言地解释 / 续写**这个位置代表什么。
- 典型 target prompt 模板：`"cat → cat; 135 → 135; ? →"`，patch 到最后一个 `?` 上，让模型自己 decode 出「这是什么」。本质是**用模型自己当 decoder**，所以不受 representational drift / 早层 basis 不对齐的影响。
- 论文 demo 出来的能力：
  - **Early-layer decoding**：logit lens 在第 1-10 层完全 decode 不出有意义的 token，Patchscopes 可以在第 5 层就还原出「这个 hidden state 对应 entity Madonna」。
  - **Multi-hop reasoning inspection**：在 "the CEO of the company that makes iPhone" 这种 query 里，能看到中间层先 resolve 出 "Apple" 再 resolve 出 "Tim Cook"，比 logit lens 清楚得多。
  - **Cross-model patching**：源 prompt 在 Llama-2-13B 上抽出来的 hidden state，patch 到 Llama-2-7B 的对应位置，仍能被「翻译」出来——证明同家族不同 size 模型共享一定的 representation geometry。
  - **Error correction**：发现某些 hallucination 案例下，正确答案其实在中间层已经存在，但被后续层「擦掉」了——这给「per-layer early exit decode」提供了机制证据。
- 局限与注意：
  - target prompt 选择**非常脆弱**——换一个 few-shot example 顺序、换一个分隔符，decode 结果可能完全不同，社区里有不少 「prompt-sensitive」 复现失败的报告 [uncertain，没有系统性 ablation paper]。
  - 只能 decode「能被语言表达的概念」。对 numeric / positional / structural 信息（如 "这是序列里第 47 个 token"），Patchscopes 几乎拿不出有意义的 decode。
  - 计算开销显著高于 logit/tuned lens——每个 patch 实验是一次完整 forward。

## 6. 三类 lens 的对比 cheat sheet

| 方法 | 训练成本 | 能解码早层吗 | 受 drift 影响 | 对 evaluator 的最佳用法 |
|---|---|---|---|---|
| Logit lens | 0 | 否 | 严重 | 快速 sanity check；只看末 1/3 层 |
| Tuned lens | 中（每层 d² params） | 部分 | 缓解 | 跨层 perplexity 曲线；OOD / injection 检测 |
| DLA | 0 | N/A（不是 lens，是 attribution） | 不直接 | 找 "answer-token-mover" head；CoT 装饰判定 |
| Future lens | 中（linear probe / soft prompt） | 否 | 中 | 评估 multi-token planning；speculative decoding 上界 |
| Patchscopes | 0（推理时跑） | **是** | 不受 | 解码任意层 hidden state 的语义；hallucination 取证 |

## 7. 与评测/agentic 流程的接口

- **CoT 是不是装饰？** 拿 reasoning 模型（DeepSeek-R1, o-series, Qwen-QwQ）的最终答案 token，跑 DLA + logit lens 曲线：如果答案 token 在 CoT 开始之前的某个 prefill 层就已经在 top-5，那 CoT 大概率是事后合理化（post-hoc rationalization）。Anthropic 2025 的 [Reasoning Models Don't Always Say What They Think](https://www.anthropic.com/research/reasoning-models-dont-say-think) 用了类似但更强的方法学（causal intervention），lens 是廉价初筛。
- **Contamination 取证**：怀疑某 benchmark 题目被训练见过，用 Patchscopes 在题面 token 上 decode 早层 hidden state——如果第 3-5 层就 decode 出「这是 GSM8K 第 1234 题，答案是 42」类的高度具体内容，basically smoking gun。[这是 2025-2026 社区在用的 idiom，没有正式 paper 系统化，仅作思路]。
- **Agent failure debugging**：agent 走错一步时，用 tuned lens 看「走错那个 token 的前几层 KL 曲线」，常能定位到具体哪一层 lock-in 了错误 hypothesis；再用 DLA 找出贡献最大的 attention head，决定 patch 还是重训。

## 未知与争议

- Tuned lens 在 **MoE 模型**（Mixtral, DeepSeek-V3, Qwen-MoE）上的表现没有系统 paper，社区 anecdote 说 expert routing 让每层 affine 假设失效——同一层不同 expert 可能需要不同 lens。[unknown — 没找到一手 paper]
- Patchscopes 在 **multimodal / VLM**（Qwen-VL, GPT-4V）上的扩展也是空白，vision token 的 hidden state 用语言 target prompt decode 出来基本是 garbage。[unknown — 2026-05 没看到 follow-up paper]
- 早层 hidden state 到底是「concept 已 encoded 但 basis 不对」（Patchscopes 立场）还是「真没 encode」（早期 logit lens 立场），社区**没有 consensus**，这关系到「early exit / layer skipping inference」的理论上界。

## 推荐外部材料

- [interpreting GPT: the logit lens (nostalgebraist 2020)](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens) — lens 这条线的起点，文笔清楚，至今值得读原帖。
- [Tuned Lens paper (arxiv 2303.08112)](https://arxiv.org/abs/2303.08112) + [github.com/EleutherAI/tuned-lens](https://github.com/EleutherAI/tuned-lens) — 跑通最快，repo 直接 `pip install tuned-lens` 就能在 LLaMA / Qwen 上出图。
- [A Mathematical Framework for Transformer Circuits (Elhage et al. 2021)](https://transformer-circuits.pub/2021/framework/index.html) — DLA 与 residual stream 概念的原始论述。
- [Future Lens paper (arxiv 2311.04897)](https://arxiv.org/abs/2311.04897) — multi-token planning 假设的实证证据，篇幅短，一晚上能读完。
- [Patchscopes paper (arxiv 2401.06102)](https://arxiv.org/abs/2401.06102) — 2024 之后做 representation 解释基本绕不开，强烈推荐配着官方 [代码 demo](https://github.com/PAIR-code/interpretability) 跑一遍。
- [Neel Nanda 的 mech interp glossary](https://www.neelnanda.io/mechanistic-interpretability/glossary) — DLA / activation patching / path patching 等术语的最权威 informal 定义。
