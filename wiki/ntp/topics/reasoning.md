# Reasoning vs Pattern Matching

> CoT faithfulness, mech-interp, 多步推理可靠性。

## 核心问题与 NTP 假设

核心 NTP 争议点之一：CoT/reasoning 模型是否在做"真计算"，还是仅在 amplify 模式匹配？两条路径：(a) 机制可解释性证据；(b) corruption / 干预实验。后者的方法论稳健性本身是 meta-level 议题。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-26 | ProFIL: Probe-Filtered RL for Faithful CoT | frozen-base probe + GRPO advantage masking 把 post-commitment CoT theater 减 11–100%；prior 预测的 RL-obfuscation 失败模式没出现；CoT-theater 可被 readout-side 干预修掉 | counter-evidence | [2605.11467](../papers/paper_notes/2026-05-28-2605.11467-profil-probe-filtered-rl.md) |
| 2026-05-26 | Causal Tongue-Tie | linear probe 在 anti-commonsense CLadder 上 0.97 准确，但 yes/no 输出 0.5；≈+0.5 gap 全部来自 verbal-readout 失败；output-only causal benchmark 的对/错都不可读为 mechanism 结论 | counter-evidence | [2605.25891](../papers/paper_notes/2026-05-28-2605.25891-causal-tongue-tie.md) |
| 2026-05-13 | Conditional Attribute Transformers | NTP local objective 在序列级 attribute 估计上偏差大；联合训练 (p(token), E[attr]) 双 head 把方差和成本降一个数量级；说明部分"NTP 不会全局规划"是 head 设计问题 | cap (弱化 mech 论据) | [2605.14004](../papers/paper_notes/2026-05-27-2605.14004-conditional-attribute-transformers.md) |
| 2026-05-06 | Semantic-Loss Anti-Collapse (Causal FT) | Gemma 270M 纯 CE FT 在 transitivity/d-sep 上 100% collapse，accuracy 73.9% 掩盖；semantic loss + 动态 λ 消除 collapse；"NTP 学不到因果"的部分论据是 collapse 假阳性 | counter-evidence | [2605.05438](../papers/paper_notes/2026-05-27-2605.05438-semantic-loss-causal-collapse.md) |
| 2026-05-11 | Last Word Often Wins (Garcia) | GSM8K/MATH 上 CoT corruption 测出的"重要 step"主要是 answer-line **readout** 效应；删末行后 suffix sensitivity 塌缩 19× | counter-evidence | [2605.10799](../papers/paper_notes/2026-05-26-2605.10799-cot-format-confound.md) |

## 当前共识 / 争议

- 此前 CoT-faithfulness 文献（Lanham 2023、Turpin 2023 等）的 effect size 可能被 answer-text-following 这一 format confound 严重高估。
- 这并**不**等于说 CoT 一定忠实——而是当前测量协议不足以分辨 "中间步骤是真的在算" vs "模型在 consumption 时跟随末尾 answer text"。
- **新增 (2026-05-27)**：因果 fine-tune 类经验论据存在第二个 confound——**model collapse**（恒答 Yes/No 但 aggregate accuracy 仍高）。任何用单一 accuracy 论证"NTP 学不会因果/推理"的工作都需补 per-class / 输出分布漂移检查。同时 (Conditional Attribute Transformers) 提醒："NTP 不会全局规划"中至少一部分是 readout/objective 缺 attribute head 的工程问题，不构成机制级证据。
- **新增 (2026-05-28)**：Readout-side 主导假设再添两条直接证据。Causal Tongue-Tie ([2605.25891](../papers/paper_notes/2026-05-28-2605.25891-causal-tongue-tie.md)) 在 anti-commonsense CLadder 上把 probe-vs-output 差距量化到 ≈+0.47；ProFIL ([2605.11467](../papers/paper_notes/2026-05-28-2605.11467-profil-probe-filtered-rl.md)) 用 frozen probe + GRPO advantage masking 在四域上把 post-commitment CoT theater 减少 11–100%，且 prior 预测的 RL-obfuscation 失败模式没出现。前者证伪 yes/no 准确率作为 mechanism proxy；后者证伪 CoT theater 的 mech 解读。"reasoning vs pattern matching" 这场 mech-level 辩论已被迫迁入双轨证据（probe + 干预）协议。

## 关键证据线 (chronological)

把"reasoning vs pattern matching"这场争论按时间排开，可以看清它在 2022–2026 这四年间的几次相位翻转。每一次翻转都不是某一篇论文一锤定音，而是某一类**测量方法**被证伪或被加强。

- **2022-01 — Wei et al., *Chain-of-Thought Prompting* ([arxiv:2201.11903](https://arxiv.org/abs/2201.11903))**。Jason Wei（当时在 Google Brain）把"让模型先写步骤再答"做成 prompt-engineering 默认操作。从此 "CoT 提升 reasoning" 成为业内常识，但论文本身并未声称中间 step 与最终答案有因果关系——它只是观测到 accuracy 同时上升。后续大半文献误把这种 correlation 读成 mech-level 证据。
- **2023-05 — Turpin et al., *Language Models Don't Always Say What They Think* ([arxiv:2305.04388](https://arxiv.org/abs/2305.04388))**。引入"bias-augmented prompt"：在 few-shot 例子里偷偷把答案都设成 A，模型最终答 A 的频率剧增，但 CoT 里完全不提"我看到例子都是 A"。这是第一份在 GPT-3.5 / Claude 1 上系统量化 CoT 不忠的工作。
- **2023-07 — Lanham et al. (Anthropic), *Measuring Faithfulness in CoT Reasoning* ([arxiv:2307.13702](https://arxiv.org/abs/2307.13702))**。设计 truncate / corrupt / paraphrase 三种 CoT 扰动，发现小模型 CoT 改了答案也变，大模型反而对 CoT 内容不敏感——"大模型越不忠"成为之后两年最常被引的反直觉结论。
- **2023-05 — Dziri et al., *Faith and Fate* ([arxiv:2305.18654](https://arxiv.org/abs/2305.18654))**。在三位数乘法、动态规划、逻辑谜题上证明 GPT-4 在 compositional depth 增加时 accuracy 断崖式下跌，且 fine-tune 也救不回来。这一篇成了 NTP-mech 派引用最多的"上界证据"。
- **2023-09 — Berglund et al., *The Reversal Curse* ([arxiv:2309.12288](https://arxiv.org/abs/2309.12288))**。"A is B" 训练后不能答 "B is A"。极简、可复现、跨模型规模稳定——这是 mech-interp 派至今最难被解释掉的现象之一。
- **2024-09 — OpenAI o1 / 2025-01 — DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948))**。RL-on-CoT 系统把 AIME / Codeforces 推到人类高分。但 R1 论文也罕见地承认 reasoning trace 中存在大量"伪推理"（自我重复、跳步、最终答与推理矛盾），并把它当 reward hacking 来分析——这是工业界第一次正面承认"长 CoT ≠ 忠实 CoT"。
- **2025 中期 — mech-interp 一侧**：Anthropic 的 *On the Biology of a Large Language Model* (transformer-circuits.pub, 2025-03) 在 Claude 3.5 Haiku 上用 attribution graph 显示**多步算术确实由可识别的中间特征逐级合成**，不是 lookup。这是迄今最强的"CoT 不全是表演"的 mech 证据，但作者也明确写明：只在 ≤3 步、训练分布密集的题型上成立。
- **2026-05 — Garcia, *Last Word Often Wins* ([2605.10799](../papers/paper_notes/2026-05-26-2605.10799-cot-format-confound.md))**。把 Lanham / Turpin 这一脉的 corruption 协议拆开，证明此前测出的"重要 step"绝大部分是 answer-line **readout** 伪影——删末行后 suffix sensitivity 塌缩 19×。这一击对"CoT 不忠"派的伤害比对"CoT 忠"派更大：它说过去三年的测量本身分不清楚两边。
- **2026-05 — Semantic-Loss Anti-Collapse ([2605.05438](../papers/paper_notes/2026-05-27-2605.05438-semantic-loss-causal-collapse.md))** + **Conditional Attribute Transformers ([2605.14004](../papers/paper_notes/2026-05-27-2605.14004-conditional-attribute-transformers.md))**。两篇互相独立的工作同时指出：把"NTP 学不到 X"做为 mech 结论时，至少要排除 (i) output-distribution collapse、(ii) readout head 缺 attribute 通道这两个工程 confound。Dziri 2023 这一类 compositional-failure 论据中至少有一部分会缩水。

## 当前最强的 mech 候选 (NTP 视角)

把上面证据线翻译成 mech-level 假设，目前留下来还没被 2026-05 的清洗冲掉的有三条：

- **C-REAS-1：Reversal Curse 类的方向不对称**。这是少数在 controlled synthetic data 上仍稳健的现象，且与 NTP 的左到右因果掩码直接相关。可证伪条件：bidirectional pre-training（如 prefix-LM 或 UL2 mixture）应使该效应在 matched data 上显著弱化；目前 [arxiv:2309.12288](https://arxiv.org/abs/2309.12288) 附录 D 的 prefix-LM 实验已给出初步支持，但尚未在 ≥7B 规模复现。
- **C-REAS-2：Depth-bounded composition（Faith-and-Fate 的硬核版本）**。在 no-CoT、固定生成长度下，TC⁰ 类 depth 下界（见 [formal_limits](formal_limits.md) 中 Deterministic Horizon、Measure-Theoretic Reasoning）给 C-REAS-2 提供了理论靠山。**但加 CoT 后该上界基本被打开**——所以 C-REAS-2 只在 no-CoT setting 下成立，这一限定常被忽略。
- **C-REAS-3：Long-horizon multi-hop 上的 Ω(H) estimation 下界**。来自 [arxiv:2605.12316](https://arxiv.org/abs/2605.12316) (Joint-KL AR Learning) 的信息论结果：sample complexity 在 horizon 上线性下界，匹配 Õ(H) 上界。这是目前唯一同时给出**下界**和**匹配上界**的 NTP-cap 结论，强度远高于经验 scaling 推断。

## 反例与上界突破

NTP-mech 派必须直面的三个反例：

1. **Anthropic 2025-03 attribution graph** 直接观察到多步算术的内部 step-wise 合成，不是 surface lookup。这把"CoT 全是表演"这种强 mech 主张钉死了——至少 Claude 3.5 Haiku 上不成立。
2. **DeepSeek-R1 / o1 在 AIME 2024、IMO 几何子集上的 pass@1**[unverified 具体数字 — 见原报告] 已超过 90 分位 IMO 选手。即便其中部分是 trace pollution / 训练集污染，剩余部分仍远超 2023 年任何人对"NTP-only 模型能做到的数学"的预测。这构成 NTP-cap 边界的事后修正。
3. **Low-Prec Softmax + Summarized CoT** ([arxiv:2605.18079](https://arxiv.org/abs/2605.18079))：即使在 fp8 / int4 + 对数生长 depth 下，softmax-attn + summarized CoT 仍 Turing-complete。这意味着任何"架构 + 精度"组合下的硬 mech 上界都会被一个足够长且 summarized 的 CoT 抹掉。

## Reversal Curse 修复尝试线 (2023–2026)

C-REAS-1 在三条 mech 候选里是唯一一条**同时**满足 (i) controlled synthetic data 可复现、(ii) 与 NTP 的左到右因果掩码直接耦合、(iii) 有明确可执行的 falsifier (\"换 prefix-LM / 双向训练 / reverse-order 数据后效应若消失则降级\")。正因为这三条同时满足，2023–2026 围绕它的修复尝试也最密集，值得单独抽出一条时间线——因为每一次失败的修复都进一步**收窄** C-REAS-1 的可证伪 setting，而每一次成功的修复都在向 \"NTP-cap 而非 NTP-mech\" 的方向推。

- **2023-09 — Berglund 等原文附录 D ([arxiv:2309.12288](https://arxiv.org/abs/2309.12288))**。作者本人尝试用 GPT-3 175B + bidirectional fine-tune（在同一对 \"A is B\" / \"B is A\" 同时出现的小数据集上微调）测试是否消解。结果：accuracy 提升但仍远低于 forward direction。这是修复线的第一个数据点：**简单地把双向看到一遍不够**，要么需要更深结构变化，要么 Reversal Curse 并非纯掩码 artifact。
- **2024-03 — Golovneva 等，*Reverse Training to Nurse the Reversal Curse* ([arxiv:2403.13799](https://arxiv.org/abs/2403.13799))**。Meta 的 Sainbayar Sukhbaatar 组提出在预训练阶段同时喂 forward 序列与 token-reversed 序列（entity-preserving word-level reverse），1.4B 规模复现实验显示在 Berglund 原任务上 reverse accuracy 从 ~0 拉到 ~80%；但 standard benchmarks (MMLU, HellaSwag) 的 perplexity 也有轻微退化。这是第一个 *在预训练目标层面* 给出实质改善的工作——但代价是 token budget 翻倍且通用能力非零成本。
- **2023-09 — Allen-Zhu & Li, *Physics of Language Models 3.2: Knowledge Manipulation* ([arxiv:2309.14402](https://arxiv.org/abs/2309.14402))**。在 fully-controlled biography 合成数据上证明：单纯 inverse 检索 (B→A) 在 NTP 训练下接近 0%，与 Berglund 原观察吻合；但加入 \"知识在多个语境/句式下被重复见到\" (knowledge augmentation) 后 inverse accuracy 显著提升。这等于把 C-REAS-1 的边界从 \"NTP 学不到 B→A\" 改写为 \"NTP 在 single-context exposure 下学不到 B→A\"——一个更弱、但仍然非平凡的命题。
- **2024 中—2025 — 工程派 workaround**。RAG + entity-canonical id + symmetric relation extraction（典型如 Letta/Mem0 这类 memory store 的双向边设计）几乎完全绕过 Reversal Curse，但代价是把推理转成显式查询，本质是\"承认 NTP 学不到，所以外接\"——这恰好与 N6 / N7 提到的 \"把状态外置\" 是同一模式。从 mech 论据角度看，这条修复路线 *并不* 反驳 C-REAS-1，反而加强它。
- **2025 — 反向证据缺口**。截至 2026-05，公开文献里**没有**在 ≥7B 规模、纯 prefix-LM 或 UL2 ([arxiv:2205.05131](https://arxiv.org/abs/2205.05131)) 预训练目标下对 Reversal Curse 做的干净复现实验。Golovneva 的 reverse-training 是 *augmentation* 不是 *objective change*；DeepSeek-R1 / o1 这类 reasoning model 虽在某些反向问答上经 long-CoT 间接答出，但无法分离 \"模型学会了反向关系\" 与 \"模型在 inference time 显式 enumerate 候选\" 两种解释。这正是 open problems 第五条留下的真正空白。

**对 C-REAS-1 的净影响**：三年修复尝试下来，Reversal Curse 的可证伪 setting 已从 \"任何 NTP 模型在任何规模下都学不到反向\" 收窄到 \"在 standard left-to-right NTP objective、single-context exposure、≥7B 规模下，反向检索 accuracy 显著低于正向\"。这一限定窗口比 2023 年小得多，但**仍未被证伪**——这是它在 2026-05 仍然是 mech 候选第一名的原因。下一步实质性进展只能来自两个方向之一：(a) 在 ≥7B 规模训一个纯 prefix-LM / UL2-mix base model 并复现 Berglund 协议，若效应消失则 C-REAS-1 降级为 NTP-cap (\"标准 NTP 的工程 artifact\")；(b) 在 mech-interp 层面（Anthropic attribution graph 风格）直接定位 \"forward A→B\" 与 \"reverse B→A\" 在 circuit 上的不对称结构。两条路线都未见公开尝试。

## Latent / pause / continuous CoT — readout-主导假设的实验性裂缝 (2024–2026)

Garcia 2026 / ProFIL 2026 / Causal Tongue-Tie 2026 这一波清洗工作的共同结论是：当前 mech-vs-pattern-matching 辩论里大约一半的"经验论据"是 verbal-readout 伪影。一个干净的后续问题是：**如果把"verbal readout"这个环节本身去掉，剩下的还是不是 reasoning？** 2024–2026 围绕 latent / pause / continuous-token CoT 的几条工作线，就是这个问题的 *实验性* 答案，也是 Open problems 第三条的现状盘点。

- **2023-10 — Goyal et al., *Think Before You Speak* ([arxiv:2310.02226](https://arxiv.org/abs/2310.02226))**。在 1B 规模 pre-training 阶段插入可学习的 `<pause>` token，模型在 commonsense reasoning / SQuAD 上 zero-shot 提升 ~1–5pp。关键不是数字，而是 **pause token 不携带任何 verbal content**——按 readout-主导假设，它本不该有 effect。该论文是后续 latent-CoT 路线的实验起点。
- **2024-12 — Hao et al., *Coconut: Training Large Language Models to Reason in a Continuous Latent Space* ([arxiv:2412.06769](https://arxiv.org/abs/2412.06769))** [unverified ID]。Meta FAIR 的 Shibo Hao 把 CoT 中间步骤替换为 last-hidden-state 直接 feedback（不解码、不 verbal），在 ProsQA / GSM8k 子集上达到与显式 CoT 接近的 accuracy，但 token 预算减半。**对 readout 假设的伤害是直接的**：如果中间 step 完全不经过 vocab projection 而 accuracy 仍立得住，那 Garcia 2026 测出的 format confound 至少在 latent setting 下不构成上界。
- **2024-04 — Pfau, Merrill, Bowman, *Let's Think Dot by Dot* ([arxiv:2404.15758](https://arxiv.org/abs/2404.15758))**。NYU 一组在合成 3SUM / 2SUM 任务上把 CoT 替换为无意义的 `.....` filler token，发现 filler 在某些任务上也能达到 CoT-equivalent accuracy——但他们同时给出关键限定：**只在 dense supervision (per-step parallel labels) 下成立**，pre-trained model 不能 zero-shot 从 filler 中受益。这把 Goyal 2310.02226 的 pause-token 效应往下推了一层：filler 本身不是 reasoning carrier，它只是给计算腾时间。
- **2025 — Quiet-STaR / latent reasoning 后续**。Eric Zelikman 等 ([arxiv:2403.09629](https://arxiv.org/abs/2403.09629)) 把每一个 token 后强制采样多条 latent rationale 再 marginalize，在 GSM8k 上 zero-shot 提升非平凡（数字 [unverified]）；这条线与 Coconut 不同的是 latent 仍然解码到 vocab，但只在 inference time 边缘化掉。对 readout 假设的判定是 *中间地带*：rationale 仍走 vocab，但训练目标不再奖励"被人读懂"。
- **2026-05 — N2 §6 三道暗门 / Schuurmans-Dai-Zanini 2410.03170 [unverified ID] universality 结果**。把 latent-CoT 与 TC⁰ 之墙的关系第一次明确：Merrill-Sabharwal ([arxiv:2310.02309](https://arxiv.org/abs/2310.02309)) 上界的 "discrete token per step" 假设在 latent / continuous setting 下 *不成立*，所以 latent CoT 同时 escape (i) readout confound、(ii) TC⁰ depth 上界。两条线在 2026 才被同时识别为同一道"门"。

**对 mech vs pattern matching 辩论的净影响**：把这五个数据点放在一起，2026-05 后的合理立场是——readout-主导假设是 **verbal CoT setting 下**的强解释，但在 latent / continuous-token setting 下需要重新测量。这给两派各留了一道窗：

- mech 派必须接受：Garcia / Causal Tongue-Tie / ProFIL 的清洗结果在 verbal CoT 上几乎没有可争辩空间，C-REAS-1 / C-REAS-2 / C-REAS-3 的 verbal-CoT 部分证据都要重做。
- pattern-matching 派必须接受：Goyal 2310.02226 + Coconut 2412.06769 [unverified] 的 pause / latent 效应在 *没有任何 verbal carrier* 的前提下仍存在；如果坚持"reasoning = verbal readout artifact"则无法解释这部分 accuracy。

**判断 (2026-05-28)**：latent-CoT 这条裂缝是未来 12–18 个月 mech 辩论真正会移动的位置。具体可证伪预测：(i) 若在 ≥7B 规模、纯 latent-CoT (Coconut-style) 设置下，C-REAS-2 的 Faith-and-Fate compositional depth 失败模式 *消失*，则 NTP-mech 的"depth 上界 → 实际能力上界"链条被打开（路径同 N2 §6 三道暗门 (1)）；(ii) 若 latent-CoT 在 controlled synthetic reverse-retrieval 上同样表现 Reversal Curse，则 C-REAS-1 的强度不依赖 verbal readout——这会是 mech 派 2026 后最重要的正面证据。两个实验 *都没有公开做过*。这是 Open problems 第三条目前的真实状态：不是没人想到，是没人做。

## 判断 (2026-05-27)

我目前的立场：**"CoT faithfulness" 作为一个二值问题已经走到死路**。Garcia 2026 的 format-confound + Anti-Collapse 2026 的 output-distribution confound 一起说明：过去三年大约一半"CoT 不忠"和近一半"NTP 学不到 X"的论文，**effect size 都需要打折重做**。但这不构成对 NTP 派的胜利——它只是把球踢回原点：唯一存活的强 mech 证据是 Reversal Curse 类的方向不对称、Ω(H) 信息论下界，以及 no-CoT setting 下的 TC⁰ depth 上界。

换句话说：**reasoning 这一 topic 上 NTP-mech 派的"经验论据"在 2026-05 后已大幅缩水，但"理论论据"反而被 formal_limits 一侧加强了**。下一步关键不在再做一篇 CoT corruption——而在 (a) 把 Anthropic 的 attribution-graph 方法扩到 ≥3 步、对抗污染样本；(b) 在 7B+ 规模复现 prefix-LM 是否真能消解 Reversal Curse；(c) 把 Ω(H) 下界落到具体 multi-hop benchmark 上做 sample-size 预测。

## Open problems

- 在三步 protocol (question-only control + format characterization + all-position sweep) 下复现已有 CoT (un)faithfulness 结论，看哪些幸存。
- 区分 generation-time vs consumption-time 因果：是否需要双向干预（同时改 prompt 和 sampling rollout）才能干净识别 reasoning locus。
- 在 latent / summarized CoT 设置下，readout 效应是否同样主导。
- 把 C-REAS-3 的 Ω(H) 下界翻译成 GSM-Hard / MATH-500 / FrontierMath 上的可证伪 sample-complexity 预测。
- 在 ≥7B 规模复现 prefix-LM 对 Reversal Curse 的消解效应；若失败，C-REAS-1 升级为强 mech 证据。

## 交叉引用

- [formal_limits](formal_limits.md)：Deterministic Horizon、Measure-Theoretic Reasoning 给 C-REAS-2 提供 no-CoT 上界；Low-Prec Softmax + CoT 给反例 3。
- [causality](causality.md)：Semantic-Loss Anti-Collapse 同时对 reasoning 和 causality 两条 mech 论据扣分。
- [scaling_limits](scaling_limits.md)：Joint-KL AR Learning 的 Ω(H) 是 C-REAS-3 的理论根基。
- [N1 — 这个问题为什么突然变重要了](../samples/N1-the-ntp-question.md) §3 已引用 Reversal Curse / Faith-and-Fate 作为 NTP-mech 入口案例。
