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
