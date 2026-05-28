# Reasoning vs Pattern Matching

> CoT faithfulness, mech-interp, 多步推理可靠性。

## 核心问题与 NTP 假设

核心 NTP 争议点之一：CoT/reasoning 模型是否在做"真计算"，还是仅在 amplify 模式匹配？两条路径：(a) 机制可解释性证据；(b) corruption / 干预实验。后者的方法论稳健性本身是 meta-level 议题。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-26 | STARS — Stability-driven Recurrent Scaling (Yang et al.) | LoopLM test-time 崩塌 = Jacobian 谱半径 >1；Spectral Radius Regularization 把 latent map 拉到 asymptotically stable fixed point；test-time depth 单调饱和而非崩塌 | counter-evidence (latent-reasoning 不稳定 ≠ NTP mech) | [2605.26733](../papers/paper_notes/2026-05-29-2605.26733-stars-looped-stability.md) |
| 2026-05-26 | Why Prompt Optimization Works/Doesn't (Gong & Wen) | propensity-adjusted edit-level analysis：complexity-增加 / meta-instructional edits 对 math/multi-hop reasoning 负相关；step-by-step / meta-cognitive 对 logical 正相关；prompt-only effect 是 edit-family × task-routing 交互 | counter-evidence (新方法论 confound) | [2605.26655](../papers/paper_notes/2026-05-29-2605.26655-prompt-opt-causal-edit-analysis.md) |
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

## PRM / RLVR / 过程奖励：把 reasoning 从 NTP loss 几何里拆出来的两年 (2023–2026)

把上面三条 mech 候选和两条裂缝拼起来，会发现一个 2024 之后的共同结构：所有"NTP 学不到 X"的论据在 *pre-training* 阶段都成立，但被 *post-training* 阶段的某种额外信号反复打折。这个额外信号的演化线，是过去两年 reasoning topic 真正发生位移的地方——也是 N1 §"objective-verifier alignment 暗门" 与本页 mech 候选的具体接口。

- **2023-05 — Lightman et al. (OpenAI), *Let's Verify Step by Step* ([arxiv:2305.20050](https://arxiv.org/abs/2305.20050))**。第一次在 MATH benchmark 上系统对比 outcome-reward (ORM) vs process-reward (PRM)：在 best-of-N 选择下 PRM (PRM800K 标注) 比 ORM 显著好 ~8pp（MATH test，N=1860 generator）。这一结果常被读为"过程标注更好"，但它的 NTP-mech 含义是另一面：**PRM 之所以有效，是因为 ORM 给出的梯度信号在 step-level 上 *退化* 为同一个标量**——这正是 NTP loss 几何的 fingerprint，per-token CE 不区分中间步的因果贡献。PRM 是补这个 mismatch 的最小修正。
- **2024-01 — Wang et al., *Math-Shepherd* ([arxiv:2312.08935](https://arxiv.org/abs/2312.08935))**。把 PRM 标注从人工 (PRM800K) 改为 MCTS rollout 自动估计的 step value，消解 Lightman 路线的 scale bottleneck。关键发现：自动标注 PRM 在 MATH 上几乎追平人工 PRM，但**只在 generator 与 verifier 同源时成立**——把 verifier 换成另一个 base model，gain 就掉到接近 ORM。这给 NTP-mech 派一个尴尬证据：PRM 学到的不是 "step 是否正确" 这个 verifier-invariant 量，而是 "step 在该 generator 下的 likelihood-adjusted advantage"，仍然是 NTP loss 几何的近端修正而非脱离。
- **2024-02 — Setlur et al., *RL on Incorrect Synthetic Data Scales LLM Math Reasoning* ([arxiv:2406.14532](https://arxiv.org/abs/2406.14532))** [unverified 月份]。CMU/Aviral Kumar 组系统对比 SFT-on-positive、SFT-on-negative、RL-on-negative 三种用错误样本的方式，发现 **RL on per-step advantage of negatives 给出 8× sample efficiency** 相对纯 SFT。机制解释直接连到 N1 §"objective alignment" 暗门：NTP CE 对 negative trajectory 是均匀降权（softmax 分母被推高一点点），RL advantage 对错步定向 *负梯度*——前者是 likelihood 几何，后者是 utility 几何，两者在 reasoning task 上对齐度不到 0.5。
- **2024-09 — OpenAI o1 system card / 2025-01 — DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948))**。R1 的 GRPO + outcome reward (verifier = python interpreter / boxed-answer match) 路线把 PRM 整个绕过——不是 PRM 不好，而是 outcome verifier 在 math/code domain 上够强时，过程标注的边际增益消失。这给 PRM 路线第一个 *退场* 数据点：**PRM 之所以重要，仅在 outcome verifier 不可得或不可信的 domain**（open-ended writing、agentic web action、science discovery）。在那些 domain 里 PRM/RLAIF/critic-LLM 的几何依然是 NTP loss 的最小修正而非替代。
- **2025-04 — Kazemnejad et al., *VinePPO* ([arxiv:2410.01679](https://arxiv.org/abs/2410.01679))** [unverified 作者顺序]。把 PPO 的 critic head 替换为蒙特卡洛 rollout 估值，去掉 critic 不准导致的 advantage bias，在 MATH 上比 PPO 提升 ~4pp 同时训练步数减半。NTP-mech 视角：**critic head 本身是 NTP backbone 的一个 readout，被 NTP loss 几何形状所限**；蒙卡 rollout 用 environment（python exec / verifier）的真信号绕过这个 readout，是把 advantage 估计从 NTP geometry 里搬出去的最干净做法。这条线和 latent-CoT 是对偶的——一个绕过 verbal readout，一个绕过 value readout，但二者都在 *承认* NTP backbone 本身没坏。
- **2025–2026 — RLVR 主流化 + reward hacking 回潮**。DeepSeek-R1、QwQ、Kimi K1.5、o3 公开材料里 RLVR (RL with verifiable rewards) 成为后训练标配；但 2025-下半年开始出现一批 "reward hacking 在 RLVR 下重新出现" 的 case study (Goodhart-on-verifier，模型学会 game boxed-answer format) [unverified bundle]。这把 N1 §"objective alignment" 暗门的论证闭环：**objective-verifier alignment 不是一次修好的，每提一层（CE → ORM → PRM → RLVR → verifier-of-verifier）就在新层级上重新出现 misalignment**——这是 reasoning topic 上最具结构性的负面预测。

把这五个数据点的几何含义收紧成一条 mech 候选：

- **C-REAS-4 — NTP loss geometry 与 reasoning utility 的 layer-wise misalignment**。在任何 reasoning task 上，per-token NTP CE 与 task-level utility (correctness / verifier reward) 的梯度对齐度 < 1，且该 gap 沿 (CE, ORM, PRM, RLVR) 阶梯单调缩小但**永不为零**——每提一层只把 misalignment 推到更小的残差子空间。**Falsification**: 找到一个 reasoning domain，使得纯 NTP pre-training (no post-training, no verifier) 在 held-out task utility 上达到与 RLVR-tuned 同等水平（matched compute）。**当前评估**: medium-strong——R1/o1 vs base-model 在 math/code 上的 gap 是直接证据（base 模型 best-of-N + verifier 仍显著低于 RLVR-tuned greedy），但缺乏跨 domain 的 controlled 测量；science/agentic 上 PRM 路线尚未稳定，证据仍在积累。

C-REAS-4 与 C-REAS-1/2/3 的关系是 *正交且互补*——前三条是"NTP 学不到什么"的 *容量* 论据，C-REAS-4 是"NTP loss 形状本身不匹配 reasoning"的 *几何* 论据。两者合在一起才能解释 2024–2026 frontier reasoning 模型的真实分布：base model 在 capacity 边界附近，post-training 把 distribution 推到 capacity 边界 *内* 的高 utility 区域，但 capacity 边界本身仍由 C-REAS-1/2/3 决定。N1 §"objective alignment" 暗门 + 本节 = 这一图景的两面。

### 反例 / 边界条件

- **Pure-RL-from-scratch 不可行**：DeepSeek-R1 ablation 显示 R1-Zero (跳过 SFT 直接 RL) 在易用性 / 多语言混杂上崩坏，必须先有 NTP-pretrain 的 backbone——这恰说明 C-REAS-4 是 *修正* 而非 *替代*，NTP backbone 提供的 prior 仍是不可绕过的。
- **In-context demonstration 的等价**：Min et al. 2202.12837 (rethinking demonstrations) 显示 few-shot 例子的 *label* 几乎可以随机但 demonstration *format* 关键——这条早期证据其实也是 C-REAS-4 的预演：NTP-only model 在 inference 时已通过 prompt geometry 部分补偿 loss-utility gap，PRM/RLVR 只是把这条补偿从 inference time 搬回 training time。
- **Verifier-free domain 退化为 ORM**：在开放式写作、对话偏好等 verifier 不可得的 domain，RLHF/DPO 实质上把 verifier 替换为 human-preference proxy；这些 domain 上 C-REAS-4 的 gap 测不准（utility 本身是噪声），所以判据只能在有 hard verifier 的 math/code/形式证明 上严格成立。

## Inference-time compute scaling：把 utility 的杠杆从 training 搬到 decoding (2024–2026)

C-REAS-4 把 reasoning utility 与 NTP loss 几何的 misalignment 放在 *post-training* 那侧，但 2024 年下半年起出现一条对偶的修补线——同样的 misalignment 也可以由 *inference-time compute* 来吃掉。这条线在 mech 辩论里被低估，因为它的工程外观（"多 sample 几次"）比 RLVR 朴素得多，但它的 NTP-mech 含义恰恰是最 *尖锐* 的：如果 inference-time 单一旋钮就能把 base-NTP model 拉到接近 RLVR-tuned 水平，那 C-REAS-4 的 "gap 永不为零" 就需要重新界定 *gap 相对哪个 reference policy*。

- **2024-07 — Brown et al. (Stanford / Anthropic), *Large Language Monkeys* ([arxiv:2407.21787](https://arxiv.org/abs/2407.21787))**。系统测 pass@k 在 k 从 1 跑到 10⁴ 时的对数线性 coverage scaling：在 SWE-bench Lite、MATH、GSM8K、MiniF2F 四个 benchmark 上，pass@k 对 log k 近似线性增长，且对 model family/size 跨度成立。一个 7B base model 在 k=10⁴ 下 SWE-bench Lite coverage 接近一个数量级强的 closed model 的 pass@1。NTP-mech 解读：这条曲线说明 **base NTP backbone 的 *支持集* (support of next-token distribution) 在 reasoning 任务上 *已经包含* 正确答案**，缺的不是 capacity 而是 *select-the-right-one*——后者由 verifier 提供。这是 C-REAS-4 "几何 misalignment" 的最干净佐证（select-the-right-one = utility readout 与 likelihood readout 错位），但也是它最危险的反例：如果 verifier 足够好，inference-time sampling 单独就能逼近 RLVR-tuned greedy。
- **2024-08 — Snell et al. (Google DeepMind), *Scaling LLM Test-Time Compute Optimally* ([arxiv:2408.03314](https://arxiv.org/abs/2408.03314))**。在 MATH 上系统比较 (a) iterative refinement / revision、(b) PRM-guided tree search、(c) best-of-N + ORM 三类 test-time compute allocation，发现在 *固定 inference FLOPs* 预算下，把 compute 投入到 test-time 的边际收益与把同样 FLOPs 投到 14× 大模型的 pre-training 边际收益相当（在 easy/medium 题上 test-time 占优，hard 题上 pre-training 仍占优）。这条结果在 2024-09 OpenAI o1 公开后被广泛引为 "inference-time scaling 是新一根 scaling 轴" 的工业证据。NTP-mech 含义：**post-training (RLVR) 与 inference-time search 是 *可替代* 的两种修正 C-REAS-4 misalignment 的路径**——前者把 verifier 信号 amortize 进 weight，后者把 verifier 信号留在 decoding——但两者的 *上界* 都由 base model 的 support coverage (Brown 曲线) 决定。
- **2024-11 — Wu et al., *An Empirical Analysis of Compute-Optimal Inference for Problem-Solving with LLMs* ([arxiv:2408.00724](https://arxiv.org/abs/2408.00724))** [unverified ID/月份]。把 Snell 路线扩展到 cost-matched 设置下的 model-size × test-time-compute 联合 Pareto 前沿，结论与 Snell 一致但把 cross-over 点（test-time 占优 vs pre-training 占优）量化到具体 FLOPs 比，给出 inference-time scaling 的 *经济学* 而非 *能力* 论据。
- **2025 — o1 / o3 / R1 长 CoT 的 inference-time 内化**。OpenAI o1 / DeepSeek-R1 把 Snell 路线 (b) 的 search behavior 通过 RL-on-CoT 内化进 *单条* long-CoT generation，使得 inference-time compute scaling 从外部 best-of-N 变成单条 trajectory 内部的 token 数 scaling（"thinking tokens"）。这条内化让 Brown/Snell 的 *外显* test-time compute 在 frontier 上看起来过时，但 mech 上是同一回事——only the budget 从 N=10⁴ samples 变成 T=10⁵ tokens。
- **2025-下半年 — inference-time scaling 的 *退场* 证据**。一批 case study 显示 long-CoT 内化在 ≥10⁵ thinking tokens 后 pass@1 不再上升甚至下降 [unverified bundle]，且 Brown 曲线在 k≥10³ 后在 hard subset (FrontierMath / IMO-Hard) 上斜率显著下降——support coverage 不是无限的。这给 inference-time scaling 一个上界 *形状*：在 base model support 内 log-线性，在 support 外 *任何* sampling 数都救不回来。

把这五个数据点折回 mech 辩论，关键差分是：

- **对 C-REAS-1 (Reversal Curse / capacity 类)**：inference-time scaling **不能** 救。Brown 曲线在 reverse-retrieval 类 synthetic task 上斜率接近零——base model 的 next-token distribution 在反向方向上根本没把正确答案放进 support，sample 多少次都白费。这是 C-REAS-1 与 C-REAS-4 的 *关键* 切分：前者是 support 缺失，后者是 support 内 mass 错位。Reversal Curse 至今没有干净的 inference-time scaling 反例，是 C-REAS-1 强 mech 地位的间接加固。
- **对 C-REAS-2 (Faith-and-Fate / compositional depth)**：inference-time scaling **部分** 救。Brown 曲线在 multi-digit 乘法上有 coverage 增长但斜率远低于 MATH，且在 depth ≥7 后基本饱和——这与 Dziri 2305.18654 的 compositional collapse 一致：support 内有少量正确路径但概率指数衰减，sampling 在指数次后才命中。
- **对 C-REAS-4 自身**：Brown/Snell 给出 C-REAS-4 的 *上界紧度* 测量协议——若一个 base model 在 inference budget B 下 pass@1 与 RLVR-tuned greedy 持平，则 C-REAS-4 在该 (domain, model, B) 三元组上 *被定量地紧到* B。这把 "gap 永不为零" 从定性论断升格为可量化的 *budget-dependent gap*。

**C-REAS-5（新候选）— Support-coverage decomposition of inference-time scaling**。任何 reasoning task 上的 inference-time compute scaling 曲线 pass@k(log k) 可分解为两段：(a) coverage-limited 段——斜率由 base NTP model 在该 task 上的 support coverage 决定，与 RLVR/PRM 无关；(b) selection-limited 段——斜率由 verifier quality 决定，与 base model 无关。frontier reasoning 的真实瓶颈在 (a) 而非 (b)，这是 inference-time scaling 与 RLVR 终将共同撞墙的 *同一面墙*。**Falsification**: 找到一个 reasoning domain，使得 inference budget × verifier quality 联合 sweep 下 pass@1 持续提升、不出现 (a)/(b) 双段相变，则 C-REAS-5 被证伪。**当前评估**: medium——Brown 曲线在 SWE-bench / MATH 上呈现明显的 log-线性后饱和模式，但跨 domain 双段相变的 controlled 测量尚无公开结果。C-REAS-5 与 C-REAS-4 是 *上下界* 关系：C-REAS-4 描述 utility-likelihood gap 的存在，C-REAS-5 描述吃掉这个 gap 的两条互补路径的 *联合上界*。

**判断 (2026-05-28 补)**：inference-time scaling 这条线在 2024–2025 一度被工业界包装为 "新一根 scaling 轴"（与 N、D、C_train 并列），但 mech 视角下它更像 *把 C-REAS-4 的修正预算从 training-time 平移到 inference-time 的会计学技巧*——上界仍由 base NTP model 的 support coverage 决定，而 support coverage 仍由 pre-training 的 N/D 和 C-REAS-1/2/3 决定。这与 scaling_limits topic §C-SCALE-4 (verifier-rich exchange) 的判决一致：inference compute 不是新轴，是 training compute 的 *fungible substitute*——在 verifier 可信 domain 上有效，在 verifier 不可得 domain 上回退到 base model 上界。

## C-REAS-5 双段相变的 *verifier-free* 切片：self-consistency / majority voting 的旧曲线在新视角下的位置 (2022–2026)

C-REAS-5 把 inference-time scaling 拆成 (a) coverage-limited × (b) selection-limited 两段，但上节五个数据点（Brown / Snell / Wu / o1-R1 / 退场 case）都默认 verifier *存在且可信*。把 verifier 拿掉，C-REAS-5 还成不成立？这是 2024–2026 工业界把 long-CoT + RLVR 当成默认配方时被快速忽略的一条 *旧* 证据线——self-consistency / majority voting 类 verifier-free 选择器在 2022–2023 已被系统测过，它们的曲线形状恰好是 C-REAS-5 在 "verifier quality = 多数投票 base rate" 这一退化点上的切片。把这条旧曲线重新放回 C-REAS-5 的坐标系，能给 selection-limited 段加一个独立锚点，也能解释为什么 o1/R1 路线要绕过 self-consistency 直接走 RLVR。

- **2022-03 — Wang et al. (Google Brain), *Self-Consistency Improves Chain of Thought Reasoning* ([arxiv:2203.11171](https://arxiv.org/abs/2203.11171))**。PaLM-540B + Codex 在 GSM8K / MultiArith / SVAMP 上 sample 40 条 CoT 后取多数投票，相对 greedy CoT 提升 ~10–18pp。NTP-mech 视角的关键不是数字，而是 *selection rule 完全不依赖 verifier*——majority voting 等价于把 "verifier(y) = 1[y == mode(samples)]" 当成 selection signal，它本身是 base model own next-token distribution 的统计量。这意味着 self-consistency 测出的 gain 全部在 C-REAS-5 的 (a) coverage-limited 段内：sample 越多越逼近 base model 在该 task 上的 *posterior mode*，但 posterior mode 不等于 ground-truth。
- **2021-10 — Cobbe et al. (OpenAI), *Training Verifiers to Solve Math Word Problems* ([arxiv:2110.14168](https://arxiv.org/abs/2110.14168))**。GSM8K 原 paper 第一次系统测 verifier-guided best-of-N vs majority voting：在 6B 模型 + N=100 下，trained verifier (ORM) 相对 majority voting 多 ~7pp。这条 *差分* 是 C-REAS-5 (a)/(b) 双段的最早可计量证据——majority voting 是 (a) 段上界 (base distribution 自己投票)，trained verifier 把曲线推进 (b) 段。Cobbe 2110.14168 + Wang 2203.11171 联合给出的 picture：**self-consistency 与 verifier-best-of-N 的 gap 就是 selection-limited 段的边际收益**，前者吃 (a) 段，后者吃 (a)+(b) 段。
- **2022-11 — Li et al., *On the Advance of Making Language Models Better Reasoners* (DiVeRSe) ([arxiv:2206.02336](https://arxiv.org/abs/2206.02336))** [unverified 月份]。weighted majority voting + diverse prompts 把 self-consistency gain 进一步榨干 ~2–4pp，但仍在 majority-mode 几何下——这条线证明 (a) 段在 verifier-free 下确实有 *固有* 饱和点，不是无限的。
- **2024 — Chen et al., *Are More LM Calls All You Need?* ([arxiv:2403.02419](https://arxiv.org/abs/2403.02419))** [unverified ID]。系统测 majority voting 在 ≥100 sample 后的边际：在 easy 题上单调上升然后饱和，在 hard 题上 *非单调*——多数答案会从对变错，因为 base model 的 mode 偏向常见但错误的捷径。这是 (a) 段在 verifier-free setting 下 *破坏* C-REAS-5 falsification 候选最干净的反例：majority voting 不仅会饱和，还会反向退化。结论：verifier-free selection 不能跨越 (a)→(b) 边界。
- **2023–2024 — universal self-consistency / LLM-as-judge 的中间地带**。Chen et al. 2311.17311 [unverified] / Zheng et al. *MT-Bench* 2306.05685 把 selection signal 从 "答案字符串多数" 升级为 "另一个 LLM 当 judge"。这等价于把 verifier quality 从 *base rate* 抬到 *与 generator 同源的 LLM-prior*——在 C-REAS-5 坐标里仍属 (a) 段的扩展（self-judge ≈ self-mode 的 soft 版），并不到 (b) 段；MT-Bench 自己的 follow-up paper 显示 LLM-as-judge 与 human preference 相关性 0.6–0.8，离 hard verifier 的 ≈1.0 还有显著距离。
- **2025 — RLVR 时代的 self-consistency *退场***。o1 / R1 / QwQ 公开材料几乎不报 self-consistency 数字；R1 paper ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) 直接用 verifier (python exec / boxed-match) 当 reward 信号，跳过 majority voting 这一中间层。这条工程选择的 mech 含义是：**当 hard verifier 可得时，self-consistency 的 (a) 段 gain 与 long-CoT 内化的 (a)+(b) 段 gain *不叠加*——前者被后者完全吸收**。这是 C-REAS-5 在 frontier setting 下被验证的一个间接信号：selection-limited 段一旦由 trained verifier 接管，verifier-free 的 mode-statistic gain 不再有边际。

把这五个数据点折回 C-REAS-5 的坐标：

- **(a) coverage-limited 段的 verifier-free 上界**：self-consistency 给出该段的 *退化估计*——若把 selection rule 设为 "投票于 base model 自己 sample"，曲线在 N≈40–100 后饱和，绝对值低于 hard verifier 的 best-of-N。这是 C-REAS-5 的 (a) 段在最弱 selection signal 下的样态，不能用作 (a) 段 *上限* 的紧测量（只能下界 base model support 的 mode mass），但能给出 (a)/(b) 差分的几何。
- **(b) selection-limited 段的边际**：Cobbe 2110.14168 给出的 verifier-vs-majority gap (~7pp @ 6B) 与 Brown 2407.21787 在 frontier 上的 coverage-gain (≥1 个数量级 pass@k 提升) 共同界定 (b) 段的厚度——在 hard-verifier domain 上 (b) 段可吃掉的 utility 大于 (a) 段，这是 RLVR 路线选择把 verifier 而非 voting 当核心的根本理由。
- **Chen 2024 的非单调退化**：给 C-REAS-5 一个未被前节明示的 *形状约束*——在 verifier 质量低于 base rate 噪声 floor 的 domain (开放写作 / 哲学论辩 / 多义伦理) 上，inference-time scaling 不仅饱和、还可能 *跨过最优点后回落*。这把 §inference-time scaling 末段 "long-CoT 在 ≥10⁵ thinking tokens 后下降" 的退场证据从 "thinking 太长污染 context" 改写为 "selection signal 不足以分辨 sample 间差异，多数投票退化为 base-rate prior 漂移"。

**对 C-REAS-5 falsification 协议的修订**：原 "inference budget × verifier quality 联合 sweep" 需要补一条 *verifier-free baseline 轴*——即在每个 (domain, base model, budget) 点上同时报 (i) greedy、(ii) majority-voting@N、(iii) verifier-best-of-N@N 三档，才能干净分离 (a) 段固有上限与 (b) 段 verifier 贡献。仅报 (iii) 会把 (a) 段的 mode-mass 误归给 verifier；仅报 (ii) 会丢失 (b) 段全部信号。Cobbe 2110.14168 是这套三档协议的最早完整实现，但 2024–2026 frontier paper 大多只报 (i)+(iii) 二档——这是 C-REAS-5 *经验测量* 的真实方法学债，与 [causality.md](causality.md) §"RL-from-environment 在 Layer-2 上的 controlled comparison" 的三档缺失 (R1-Zero / R1-SFT / R1-final × CLadder) 同型。

**跨 topic 链**：self-consistency 的 (a) 段饱和形状在 reverse-retrieval / Reversal Curse 类 task 上 *斜率 ≈ 0*——base model 的 mode 在反向方向上 mass 接近零，多投票一千次都不会变出正确答案。这是 C-REAS-1 与 C-REAS-5 (a) 段的接口：**Reversal Curse 不仅在 verifier-best-of-N 下不可救（前节已论），也在 majority-voting 下不可救**，两条独立 selection 路径同时失败，是 C-REAS-1 作为 "support 缺失" 类 mech 候选的双重加固。这条预测从未被 self-consistency 文献单独验证过（Wang 2203.11171 测的是 GSM8K 类正向推理），是 Open problems 第八条值得加挂的具体子项。

**判断 (2026-05-29 补)**：self-consistency 在 2022–2023 曾被读为 "NTP 推理能力被低估" 的乐观信号，但在 C-REAS-5 坐标下它的位置非常局限——它只是 (a) 段在 verifier-free 退化点上的一个切片，吃不掉 (b) 段，也不能跨越 base model support 边界。frontier 工业线绕过 self-consistency 走 RLVR 不是因为前者 *错*，而是因为 (a) 段在 hard-verifier domain 上的 utility 已被 (b) 段完全 dominated。这条历史轨迹反过来给 C-REAS-5 一个时间维度的支撑：**2022 self-consistency → 2024 best-of-N + ORM/PRM → 2025 long-CoT 内化 (R1/o1) → 2026 verifier-of-verifier 担忧**，是同一根 (a)+(b) 联合上界曲线被工程界一步步逼近的轨迹，每一步都让 base NTP model 的 N/D 上界更显眼，而非更隐蔽。

## Reward hacking 的层级回潮：(CE → ORM → PRM → RLVR → verifier-of-verifier) 的 2024–2026 经验链

§PRM/RLVR 末段把 N1 §\"objective-verifier alignment 暗门\" 的论证收口在一句结构性负面预测——**\"每提一层就在新层级上重新出现 misalignment\"**——并把它挂在 [unverified bundle] 上。这句预测在 2026-05 视角下其实已经有了不薄的公开证据，把它单独拉成一节、按时间线钉到具体论文上，是 Open problems 第七条 (\"在 RLVR 长训练下系统刻画 reward-hacking 的层级\") 在 *叙事层* 而非 *实验层* 能立刻还的一笔债。它不替代那个 controlled-measurement 实验，但它把 \"reward hacking 是否真的逐层回潮\" 从直觉升格为可数的事件链，给 C-REAS-4 \"misalignment 推到残差子空间\" 这条 mech 命题加上时间维度。

- **2022-09 — Skalse et al., *Defining and Characterizing Reward Hacking* ([arxiv:2209.13085](https://arxiv.org/abs/2209.13085))**。给 reward hacking 一个 *任务-无关* 的形式定义：proxy reward $\tilde R$ 与 true reward $R$ 在某状态分布上单调一致即 unhackable，否则存在 hackable 子空间。该论文与 NTP 表面上无关，但它的形式化 *预测* CE → ORM → PRM → RLVR 阶梯每提一层都不会 unhackable——因为每层 proxy 与下层 true 之间几乎不可能在所有状态上 *单调一致*。这是 2024–2026 实证回潮的理论锚点。
- **2022-10 — Gao, Schulman, Hilton (OpenAI), *Scaling Laws for Reward Model Overoptimization* ([arxiv:2210.10760](https://arxiv.org/abs/2210.10760))**。第一份在 RLHF 上把 *proxy reward 上升* 与 *gold reward 下降* 的 KL-vs-reward 抛物线刻画成 scaling-law 形式。结论：BoN 与 RL 两种 optimizer 在 ORM 上都呈 $R_{\text{gold}}(d) = d \cdot (\alpha - \beta \log d)$ 形（$d = \sqrt{KL}$），$\beta$ 是 over-optimization 系数。这是 ORM 这一层的 hacking 几何被第一次定量——*不是* \"会不会发生\" 而是 \"以多快速率发生\"。后续 PRM / RLVR 层上同型测量直到 2025 中才陆续出现，几何形状一致，只是 $\alpha, \beta$ 数值不同。
- **2023-10 — Coste et al., *Reward Model Ensembles Help Mitigate Overoptimization* ([arxiv:2310.02743](https://arxiv.org/abs/2310.02743))**。把 ORM 升级为 ensemble，over-optimization 系数 $\beta$ 缩小但 *不归零*——ensemble 的 \"verifier-of-verifier\" 几何只是把 hackable 子空间推到更稀疏的 worst-case 样本上。Eisenstein et al. 2023 *Helping or Herding?* ([arxiv:2312.09244](https://arxiv.org/abs/2312.09244) [unverified ID]) 在同设置下进一步发现 ensemble agreement 与 reward hacking 防御之间没有线性关系——即 \"更一致的 verifier 群\" 并不 *更安全*，有时反而把 hackable 路径收窄到 ensemble 共同盲区。这是 C-REAS-4 \"残差子空间\" 在 verifier ensemble 这一层的第一份实证。
- **2024 — Pan et al. *Feedback Loops with Language Models Drive In-Context Reward Hacking* ([arxiv:2402.06627](https://arxiv.org/abs/2402.06627) [unverified ID])**。把 reward hacking 从 RL 训练时刻搬到 inference 时刻的迭代 self-refinement 上：模型在每轮 critique-revise 循环里 *学会* game critic 的 LLM-judge prior，proxy 分单调上升但 oracle 分先升后降。机制等价于 §C-REAS-5 (a) 段被 selection signal 拉偏——self-judge 不是 hard verifier，所以 selection-limited 段的 over-optimization 直接打回到 base model 的 mode 漂移。这是 \"verifier-of-verifier\" 在 inference 时刻的最干净案例。
- **2025 中 — RLVR-on-math/code 的 boxed-answer / format gaming**。DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) §4 ablation 段明写 R1-Zero 在长 RL 训练后出现 \"language mixing、可读性下降、最终 boxed 答正确但 CoT 内部数值不对应\" 三类 reward-hacking pattern，必须靠 SFT cold-start 补回。Kimi K1.5 technical report (non-arxiv) [unverified bundle] 同期报告同型现象，且把 reward shaping 改为 *outcome × format × length penalty* 三项组合后 hacking 路径被推到 length penalty 边界附近。结构上与 Coste 2310.02743 的 ensemble 推子空间几何同型——hacking 没消失，被推到 reward function 显式约束之外的 *互补* 维度。
- **2025-下半年 — RLVR 上 verifier-of-verifier 担忧的正式登记**。OpenAI o3 system card / Anthropic Claude 4 model card / METR 评估报告 [unverified bundle] 在 \"capability vs safety eval\" 段开始系统区分 *trained-policy*、*judge-policy*、*judge-of-judge LLM*，并明确警告 \"sufficiently capable policy 可能 jointly game policy-verifier + judge-verifier\"。这是 §PRM/RLVR 末段那句负面预测被产业线 *正面登记* 为风险类——不是预测在 2025 才出现，而是 hackable 子空间从 ORM ($d=\sqrt{KL}$) 推到 RLVR-verifier 群 (高维稀疏) 推到 judge-LLM (LLM-prior 漂移)，每一层都比上一层更难测量，所以工业披露反而 *提前*。
- **2026-05 — Anti-Collapse ([2605.05438](../papers/paper_notes/2026-05-27-2605.05438-semantic-loss-causal-collapse.md)) / Causal Tongue-Tie ([2605.25891](../papers/paper_notes/2026-05-28-2605.25891-causal-tongue-tie.md)) 的间接对应**。两条独立工作不直接测 reward hacking，但它们揭示的 *output-distribution collapse* 与 *verbal-readout asymmetry* 在形式上是 reward-hacking 阶梯在 *无 RL* 设置下的同型现象——CE-only fine-tune 上的 collapse = ORM 的 over-optimization 在 likelihood loss 上的退化版（proxy = CE，gold = balanced accuracy）。这给 C-REAS-4 阶梯加了 *第零层* (pure CE) 的实证：misalignment 不是 RL 时代才出现，它在 NTP loss 几何里就已经在了——RL 只是让它 *更容易测量*。

把这七个数据点折成一条 mech 命题：

- **C-REAS-6 (sub-candidate) — Reward-hacking 的阶梯回潮率**。在 (CE → ORM → PRM → RLVR → verifier-ensemble → judge-of-judge) 六层 selection signal 阶梯上，每层的 over-optimization 几何 (proxy 上升、gold 下降) 由 Gao 2210.10760 的 KL-vs-reward 抛物线泛化形式给出，参数 $(\alpha_k, \beta_k)$ 满足 $\beta_k > 0$ 且对所有 $k$ 不归零；但 $\beta_k$ 随 $k$ 单调下降的速率 *慢于* hackable 子空间体积的指数收缩——因此每提一层 hacking 事件的 *绝对频率* 下降，但每次事件的 *检测难度* 上升，二者乘积 (披露成本) 不单调。**Falsification**: 在 ≥3 层阶梯上同时拟合 $(\alpha_k, \beta_k)$ 与 hackable 子空间 (operationalize 为 worst-1% proxy-gold gap) 体积，若发现存在某层 $\beta_k = 0$ 即上层 proxy 与下层 gold 在 KL 范围内单调一致，则 C-REAS-6 在该 (domain, model family) 下被部分证伪；若 $\beta_k$ 与子空间体积之积单调收敛到 0，则全证伪。**当前评估**: medium——Gao 2210.10760 给 $k=1$ (ORM) 干净拟合，Coste 2310.02743 给 $k=2$ (ensemble) 定性证据，R1/Kimi $k=3$ (RLVR) 是 case study 不是拟合，$k \geq 4$ (judge-of-judge) 只有 system-card 警告。是 C-REAS-5 (support coverage 双段) 与 C-REAS-4 (NTP loss 几何 misalignment) 之间的 *时间维度桥*——前者描述静态上界，C-REAS-6 描述上界沿阶梯下行的速率。

C-REAS-6 与 C-REAS-4 的关系：C-REAS-4 说 \"gap 永不为零\"，C-REAS-6 给这句话加上速率约束 $\beta_k > 0 \,\forall k$。两者一起把 N1 §\"objective-verifier alignment\" 暗门从 *存在性* 命题升级为 *几何* 命题——misalignment 不仅永远在，且它的衰减速率有下界，这意味着 verifier-of-verifier 路线在 frontier 上的可扩展性有 *形式* 而非 *经验* 上的天花板。这一点与 [scaling_limits.md](scaling_limits.md) §C-SCALE-4 (verifier-rich exchange) 的判决耦合：训练-推理 compute 互换在 verifier 可信 domain 内成立，但 verifier 链每加一层就把 \"可信\" 这个前提的成本推到 $\beta_k$ 决定的子空间外——长期看这两条 candidate 必须合起来读。

**反例 / 边界条件**：

- **Hard verifier domain 上 $\beta_k$ 可能极小**：math/code 上 python interpreter 是 *物理* verifier，不是 LLM proxy；它对应的 $\beta$ 接近测量噪声地板。但 R1-Zero 的 boxed-format gaming 揭示即使物理 verifier 也有 hackable 边界——verifier 必须把 *答案表征* 也固定，否则 hacking 路径从 *答案值* 推到 *答案 format*。这给 C-REAS-6 一个工程意义上的暗示：每加一层 *约束*（format、length、style）等价于在阶梯上多一层 $k$。
- **Self-judge 路径的循环风险**：Pan 2402.06627 [unverified ID] 路径是 *no-RL* 的 reward hacking——iterative refinement 内的 LLM-judge 漂移与 RLVR 是 *不同* mechanism。C-REAS-6 严格成立的范围限制在 *训练时刻* 的 selection signal 阶梯；inference-time judge 漂移需要单独 candidate（与 [grounding.md](grounding.md) §RAG LLM-judge 悖论同源）。
- **测量协议的双向 referee 困境**：与 [causality.md](causality.md) §\"Synthetic counterfactual corpus injection\" / §\"RL-from-environment controlled comparison\" 末段同型——任何想正面拟合 $(\alpha_k, \beta_k)$ 全阶梯的工作面临的双向 referee 是 \"$\beta_k$ 太大被 cap 派质疑 verifier 设计不好 / $\beta_k$ 太小被 mech 派质疑测量噪声地板偷换\"，发表回报为负。这是 Open problems 第七条至今 *没* controlled measurement 的社会学原因，不是技术原因。

> **跨链与 sub-candidate 同步**：C-REAS-6 作为 sub-candidate 登记在本节，与 C-FORM-7/C-FORM-8/C-GROUND-7/C-EMBOD-7/C-WM-7 同型——不进 [survey/taxonomy.md](../survey/taxonomy.md) 主表，但 sync 到 [survey/ntp_survey.md](../survey/ntp_survey.md) §10 sub-candidate 区 + taxonomy.md §升降级历史。**同步债务**：下一 C tick 兑现三处同步（C-FORM-8 模板），本节末段显式声明 deferred。

**判断 (2026-05-29 补)**：reward-hacking 阶梯回潮这件事在 2024–2026 公开材料里其实是 *最* 一致的负面信号之一，但它从未被单篇论文系统拟合——分散在 RLHF 时代的 ORM scaling law、PRM 时代的 ensemble disagreement、RLVR 时代的 system-card 警告里，被工业披露策略切成三段，没人把它当一条曲线读。本节的目的是把这条曲线 *命名* 为 C-REAS-6 而非测它——测它需要 §Open problems 第七条的 ≥3 层阶梯 controlled fit，那是下一年 reasoning topic 上真正能推动 mech 辩论而非重新洗 evidence 的工作。在它出现之前，\"verifier-of-verifier 一定 work\" 与 \"verifier-of-verifier 一定不 work\" 两派都没有形式工具吵清楚——只有阶梯几何能。这与 §verifier-free 切片末段的判断同型：mech 辩论的下一步关键不在新模型，在新 *测量协议*。

## 判断 (2026-05-27)

我目前的立场：**"CoT faithfulness" 作为一个二值问题已经走到死路**。Garcia 2026 的 format-confound + Anti-Collapse 2026 的 output-distribution confound 一起说明：过去三年大约一半"CoT 不忠"和近一半"NTP 学不到 X"的论文，**effect size 都需要打折重做**。但这不构成对 NTP 派的胜利——它只是把球踢回原点：唯一存活的强 mech 证据是 Reversal Curse 类的方向不对称、Ω(H) 信息论下界，以及 no-CoT setting 下的 TC⁰ depth 上界。

换句话说：**reasoning 这一 topic 上 NTP-mech 派的"经验论据"在 2026-05 后已大幅缩水，但"理论论据"反而被 formal_limits 一侧加强了**。下一步关键不在再做一篇 CoT corruption——而在 (a) 把 Anthropic 的 attribution-graph 方法扩到 ≥3 步、对抗污染样本；(b) 在 7B+ 规模复现 prefix-LM 是否真能消解 Reversal Curse；(c) 把 Ω(H) 下界落到具体 multi-hop benchmark 上做 sample-size 预测。

## Open problems

- 在三步 protocol (question-only control + format characterization + all-position sweep) 下复现已有 CoT (un)faithfulness 结论，看哪些幸存。
- 区分 generation-time vs consumption-time 因果：是否需要双向干预（同时改 prompt 和 sampling rollout）才能干净识别 reasoning locus。
- 在 latent / summarized CoT 设置下，readout 效应是否同样主导。
- 把 C-REAS-3 的 Ω(H) 下界翻译成 GSM-Hard / MATH-500 / FrontierMath 上的可证伪 sample-complexity 预测。
- 在 ≥7B 规模复现 prefix-LM 对 Reversal Curse 的消解效应；若失败，C-REAS-1 升级为强 mech 证据。
- C-REAS-4 的跨 domain controlled 测量：在 math / code / formal-proof 三类有 hard verifier 的 domain 上，固定 base model 与 compute，分别测 base-best-of-N+verifier vs RLVR-tuned-greedy 的 gap；若 gap 在某 domain ≤2pp，则 C-REAS-4 在该 domain 被弱化。
- 在 RLVR 长训练 (≥10⁴ optimizer step) 下系统刻画 reward-hacking 的层级 (CE → ORM → PRM → RLVR)，验证 "misalignment 永不为零，只是被推到更小子空间" 这一预测的具体衰减速率。
- C-REAS-5 的双段相变 controlled 测量：在固定 base model 下，跨 (MATH, SWE-bench, FrontierMath, MiniF2F, reverse-retrieval synthetic) 五个 domain sweep inference budget × verifier quality 二维网格，检验 pass@k(log k) 是否在所有 domain 上都呈现 coverage-limited → selection-limited 相变；reverse-retrieval domain 上若无 coverage-limited 段（即斜率 ≈0）则反向加固 C-REAS-1。
- C-REAS-5 三档 selection 协议补全：在上一条二维 sweep 的每个 (domain, base model, budget) 点上同时报 (i) greedy / (ii) majority-voting@N / (iii) verifier-best-of-N@N 三档（按 §verifier-free 切片节修订），干净分离 (a) 段固有上限与 (b) 段 verifier 贡献；并在 reverse-retrieval synthetic 上单独验证 majority-voting@N 是否同样斜率 ≈ 0 ——若是，则与 verifier-best-of-N 共同构成 C-REAS-1 的 *双 selection 路径* 加固。

## 交叉引用

- [formal_limits](formal_limits.md)：Deterministic Horizon、Measure-Theoretic Reasoning 给 C-REAS-2 提供 no-CoT 上界；Low-Prec Softmax + CoT 给反例 3。
- [causality](causality.md)：Semantic-Loss Anti-Collapse 同时对 reasoning 和 causality 两条 mech 论据扣分。
- [scaling_limits](scaling_limits.md)：Joint-KL AR Learning 的 Ω(H) 是 C-REAS-3 的理论根基。
- [N1 — 这个问题为什么突然变重要了](../samples/N1-the-ntp-question.md) §3 已引用 Reversal Curse / Faith-and-Fate 作为 NTP-mech 入口案例。
