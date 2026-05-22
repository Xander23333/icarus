# Ev3 — 非 agentic 代码评测（截至 2026-05）

## 路线定位

读者是 Qwen agentic-coding 的 eval+数据 owner，本节只覆盖**非 agentic** 的部分 — 即 single-turn / single-file / 离线评测，作为 Ev4 (SWE-Bench 等 agentic) 的前置。这条线的核心议题在 2024-2026 已经从 "做新难题" 转向 **(a) 抗 contamination（release-date 过滤是事实标准）、(b) 跨语言泛化（避免 Python-only over-optimization）、(c) repo-level long-context（接近真实编辑）**。本节六个 benchmark — **LiveCodeBench、BigCodeBench、Aider polyglot、USACO、HumanEval-Pro / MBPP-Pro、CRUXEval、RepoBench** — 各自占这三条议题里的一格，读者用它们应当是搭组合而不是看单榜。

## benchmark 清单

| 名称 | 主体任务 | 规模 | 关键特性 | 一手 source |
|---|---|---|---|---|
| LiveCodeBench | 竞赛题（LeetCode / AtCoder / CodeForces），按发布日切片 | ~1000+ 题滚动更新 | **release-date filter** 抗 contamination；分 generation / self-repair / test-output-pred / exec | [arxiv 2403.07974](https://arxiv.org/abs/2403.07974)、[livecodebench.github.io](https://livecodebench.github.io/) |
| BigCodeBench | 实用任务，调真实库（pandas、sklearn、requests…） | 1140 题（complete / instruct 两 split） | 测库调用组合，139 个库覆盖；test 平均 5.6 条 branch | [arxiv 2406.15877](https://arxiv.org/abs/2406.15877)、[bigcode-bench.github.io](https://bigcode-bench.github.io/) |
| Aider polyglot | 真实 edit 任务，跨 6 语言 | 225 题（Exercism 改造） | 测 **diff-format edit** 能力，不只是 from-scratch 生成；多语言 | [aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/)、[github.com/Aider-AI/polyglot-benchmark](https://github.com/Aider-AI/polyglot-benchmark) |
| USACO bench | USA Computing Olympiad，4 难度等级 | 307 题（bronze→platinum） | 真正的算法题；含官方 analysis + 隐藏 test | [arxiv 2404.10952](https://arxiv.org/abs/2404.10952)、[princeton-nlp.github.io/USACOBench](https://princeton-ardilab.github.io/usaco-bench/) |
| HumanEval-Pro / MBPP-Pro | 在 HE / MBPP 上加 self-invoking sub-problem | 164 / 378 | 测 "调用自己刚写的函数" 的组合能力，contamination-resistant | [arxiv 2412.21199](https://arxiv.org/abs/2412.21199) |
| CRUXEval | 给代码 + 输入 → 预测输出；或给代码 + 输出 → 预测输入 | 800 函数 × 2 task | 测**执行/推理**而非生成；高 contamination 警觉度 | [arxiv 2401.03065](https://arxiv.org/abs/2401.03065)、[cruxeval.github.io](https://cruxeval.github.io/) |
| RepoBench | repo-level code completion（cross-file context） | 多 split，Python+Java | retrieval + completion + pipeline 三档；测 long-range cross-file 依赖 | [arxiv 2306.03091](https://arxiv.org/abs/2306.03091) |

> SWE-Bench、SWE-Lancer、Multi-SWE-Bench 在 Ev4。本节只覆盖**不需要 agent loop** 的离线评测（最多 self-repair 一两轮）。

---

## LiveCodeBench

Jain et al. (Berkeley + MIT) [arxiv 2403.07974](https://arxiv.org/abs/2403.07974)。读者已经在用，三件值得明确：

- **release-date filter 是 contamination 的事实标准**：题按 platform 公布日期打 timestamp，评测时只取 model cutoff **之后** 的题。这是 2024 以来 frontier lab 报代码分数最常被要求的协议；HumanEval / MBPP 类不带 timestamp 的 benchmark 报分已经不被严肃读者采信。Qwen3-Coder、DeepSeek-V3、GPT-5、Claude 4.5 在自家 tech report 里都用 "LCB v5/v6, date range YYYY-MM~YYYY-MM" 的报法。
- **四个 sub-task 解耦能力**：generation（写题）、self-repair（给 failing test 修）、test-output prediction（执行推理，类 CRUXEval-O）、code execution（trace）。frontier 模型这四个分数不同步 — generation 90+ 的模型可能 execution 仅 60，这是判断 "RL 优化得过头 / 推理能力实在弱" 的探针。
- **inflation 模式**：(1) cutoff 报得宽（"2024 全年"）覆盖到训练数据，应坚持 cutoff **之后 ≥ 2 周** 的窗口；(2) Pass@1 vs Pass@5 不一致披露；(3) 部分团队报 "v5 hard subset" 不报 full — hard subset variance 大，可被 cherry-pick。
- **v5 → v6 (2025-末)** 主要扩 problem pool 和加 CodeForces edu round，没有 grading 重构。

---

## BigCodeBench

Zhuo et al. (BigCode) [arxiv 2406.15877](https://arxiv.org/abs/2406.15877)。和 LCB 互补的另一条线：**不是竞赛 puzzle，而是"调一堆库做实际事"**。

- **任务画像**：每题给 docstring + function signature，要求生成函数 body；测试用 pytest 跑，平均 5.6 个 branch。139 个库，重点是 data science / web / file IO 类。covers 真实工程里 "把 pandas + requests + json 拼起来" 的能力。
- **complete vs instruct split**：complete 给 docstring 让模型补全（base model 友好），instruct 给自然语言任务（chat model 友好）。同模型两 split 经常差 5-10 点；报分时必须声明哪一个。
- **抗 contamination 的设计**：BigCode 团队手写 + 改造，**不来自公开题库**。短期 contamination 风险低，但 leaderboard 公开 traj 后已开始有泄漏 [推测]。
- **inflation 模式**：(1) 调库版本敏感 — pandas 2.x vs 1.x 让 test 行为不同，BigCodeBench 锁了 requirements.txt 但很多团队没复用官方 docker；(2) Pass@1 平均掩盖 long-tail 题，BCB-Hard split (148 题) 是必看的次级指标，frontier 在 Hard 上常掉 20+ 点。
- **EvalPlus 系（HumanEval+, MBPP+）是 BCB 的前身路线** — 加强 test 让 HE/MBPP 的 saturation 推迟，但题本身仍 contamination；BCB 是题+test 都新写，方向更彻底。

---

## Aider polyglot

[aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/) 维护，从 Exercism 改造 225 题，覆盖 **C++ / Go / Java / JavaScript / Python / Rust**。Aider 作者 Paul Gauthier 维护，更新频繁。

- **它测的不是"写代码"是"编辑代码"**：每题给已有 stub + 失败的 unit test，模型必须输出符合 aider 支持的 diff/edit format（whole-file / udiff / search-replace）的 patch。**diff 解析失败也算输** — 这把 "模型能写对但格式坏" 的失败模式独立出来，是 frontier 模型容易吃亏的一条。Claude 系在 udiff 上稳，GPT 系在 whole-file 上稳，open-source 在两边都常碎。
- **跨语言**：这是少数公开榜里把六语言 weighted 算总分的 benchmark。Qwen / DeepSeek / Llama 系往往 Python 强、Rust / Go 弱 15-25 点；frontier closed-source 跨语言更平。读者关心 cross-lang transfer 时这是第一档信号。
- **inflation 与限制**：(1) Exercism 题是公开的 — 题面 contamination 在所有模型上都存在，所以这榜测的更多是 "edit fidelity + 多语言"，纯生成能力部分已饱和；(2) 榜按 cost-per-task 同时报，是少见的把 $ 放主榜的代码 benchmark；(3) Aider 自己的 prompt scaffold 是隐变量，diff format 选错会大跌。

---

## USACO bench

Shi et al. (Princeton) [arxiv 2404.10952](https://arxiv.org/abs/2404.10952)。307 题分 bronze / silver / gold / platinum，每题带官方 editorial 和隐藏 test。

- **和 LiveCodeBench 的区别**：LCB 大量是 LeetCode-style，USACO 是奥赛风 — 难题需要构造性算法（DP on tree、segment tree、flow），platinum 题 frontier 仍 <10% pass rate，是真正没饱和的 hard reasoning 信号。
- **多种 prompt 协议**：zero-shot、retrieval (editorial)、self-reflection、episodic memory。论文做了完整 ablation — retrieval editorial 能给 GPT-4 在 silver 上 +20 点。读者要复用时必须报协议。
- **contamination 角度**：USACO 题面在 usaco.org 公开，editorial 也在；GPT-4o / Claude 都对 2023 前题面有记忆。论文用 **过去 vs 未来题** 切分，但 2024 后增量小，长期 freshness 是问题。如要严肃用 USACO 评 reasoning，应当只看 model cutoff 后的 contest（每年 ~12 场）。
- **inflation 模式较低**：grading 是真 USACO judge（all-or-nothing per test case），没 LM-as-judge。但**给 editorial 当 retrieval = 给答案**，多团队混用这条不声明。

---

## HumanEval-Pro / MBPP-Pro

Yu et al. (M-A-P + 中科院) [arxiv 2412.21199](https://arxiv.org/abs/2412.21199)。2024-12 提出，目标是把已经饱和的 HE / MBPP 救活一轮。

- **机制**：对每个 HE / MBPP 原题，构造一个 **self-invoking** 子问题 — 新题要求模型先解原题，**再调用自己写的函数** 解一个组合任务。例如原题是 `is_prime`，Pro 题是 "返回 1 到 n 中所有 prime 之和"。
- **为什么这能抗 contamination**：原题答案 LLM 都记得，但 self-invoking 的组合形态没在训练集里。论文报 GPT-4o 在 HumanEval 90+ → HumanEval-Pro 65 区间，掉 20-30 点。这条 gap 是判断"模型是真懂还是记答案"的便宜测度。
- **限制**：(1) self-invoking 子问题构造的多样性有限，可能本身收敛到几个模式；(2) 仍是 Python-only；(3) 2025 内已被部分模型针对性优化，Pro 分数也开始爬升 — 任何 closed eval 都有半衰期。
- **读者用法**：作为 HE / MBPP 的 drop-in 替代写在 Qwen tech report 的 "为什么不报 HE" 那一栏，比解释更省事。

---

## CRUXEval

Gu et al. (MIT + Meta) [arxiv 2401.03065](https://arxiv.org/abs/2401.03065)。800 个短 Python 函数，每个出两道题：

- **CRUXEval-I**：给函数 + 输出，预测能产生该输出的输入。
- **CRUXEval-O**：给函数 + 输入，预测输出。

读者关心的几点：

- **它测的是"心算执行"不是生成**：分数和 generation benchmark 相关但不重合 — GPT-4 在 HumanEval 高、CRUXEval-O 当年仅 ~60，提示 generation benchmark 没充分测 execution / trace 能力。这正是 LCB 后续加 execution sub-task 的动机。
- **chain-of-thought 在这里效果大**：CoT 能让 GPT-4 涨 ~15 点，这是少数 CoT 收益清晰可量的 code benchmark。RL on CoT 之后 frontier 已接近饱和（90+），论文价值更多在 **诊断**：分 CRUXEval 子类别（循环、递归、字符串、嵌套数据）看哪类执行最弱，对设计 mid-train data 有指导。
- **contamination**：函数是程序合成 + 人筛，没在 GitHub 上原样存在；但 traj 公开后弱模型可能 distill。CRUXEval-X / CRUXEval-2（社区 2025 扩展）尝试加多语言版本 [uncertain — 还没看到正式 paper]。

---

## RepoBench

Liu et al. (UCSD) [arxiv 2306.03091](https://arxiv.org/abs/2306.03091)。这是 **repo-level long-context** 评测最早的一个，Python + Java，三档 task：

- **RepoBench-R**：cross-file retrieval — 给当前文件 + 下一行要 import 的符号，从 repo 里找出正确的 source file。
- **RepoBench-C**：给 in-file context + cross-file snippet，做 next-line completion。
- **RepoBench-P**：完整 pipeline — 先 retrieve 再 complete。

- **它解决的是 HumanEval 完全不测的事**：真实代码补全 80% 的 token 在 cross-file 依赖里。RepoBench 是第一个把这条工程化为 metric 的公开 benchmark，后续 CrossCodeEval / RepoEval / SWE-Bench 都受它影响。
- **contamination 与 freshness**：原版用 GitHub 2023-03 之前的 repo，**对 2024 后模型几乎全部 contaminated**。需要看 RepoBench-v1.1（按 commit date 滚动）或后继 CrossCodeEval 这种带新数据的版本。
- **读者用法**：作为 long-context code 子项的标准参考之一，但报分时必须配 (a) 用的版本（commit cutoff）、(b) retrieval policy（oracle vs BM25 vs embedding）、(c) context length。三个变量不报，跨家无可比性。
- **当前局限**：题只到 next-line 粒度，远短于 SWE-Bench 的 multi-file patch。RepoBench 是 "long-context capability" 的诊断信号，不是 "工程能力" 的终评。

---

## 跨 benchmark 横切观察

1. **release-date filter 已成 contamination 抗性的事实标准**：LCB / RepoBench-v1.1 / USACO 都按时间切；任何不能按时间切的 code benchmark（HE、MBPP、原版 RepoBench、Aider polyglot 题面公开）报分时都该加 "+Pro / +Live / 题面新写" 的免疫层。读者在自家 Qwen eval 里强制 cutoff+N 周窗口，是省事且对外可信的协议。
2. **single-file → repo-level → agent** 的连续谱：HE/MBPP → LCB/USACO（单文件、强算法）→ BigCodeBench（多库 API 组合）→ RepoBench / CrossCodeEval（cross-file 上下文）→ SWE-Bench（多文件多步编辑）→ SWE-Lancer / agentic（多 turn）。本节 6 个 benchmark 覆盖前四段，Ev4 接后两段。报分时应该跨段各报一个，避免单段过拟合。
3. **execution / reasoning 子能力独立测**：CRUXEval + LCB-execution + LCB-test-output-pred 共同构成 "模型能否在脑子里跑代码" 的探针。这条分数对 RL-trained code model 比 generation 更难刷，是 base capability 的真信号。
4. **跨语言 ≠ 多语言加权**：Aider polyglot 是少数把 6 语言主榜并列的；多数 benchmark 仍 Python-only。Qwen-coder 已经在 self-eval 里加 Rust / Go / TS — 但要对外说服，需要在第三方榜（Aider polyglot、MultiPL-E、Multi-SWE-Bench）拿分。MultiPL-E（Cassano et al.）是 HE 多语言移植，contamination 已重，仍是基线参考。
5. **诊断 vs 排名**：BigCodeBench-Hard、LCB-execution、CRUXEval-I、USACO-platinum、HumanEval-Pro — 这些是诊断信号（识别 model 弱点），不该上排名宣传；LCB-generation、BCB-complete、Aider 总分适合做主榜数字。两类要分开报。
6. **public leaderboard 的半衰期 = 12-18 月**：HumanEval 2021 → 2023 饱和，MBPP 2022 → 2024 饱和，LCB v1 2024 → 2025 饱和必须 roll v5/v6。任何 static code benchmark 都该当一次性消耗品规划，不要 commit 五年指标。

## 未知与争议

- **Qwen / DeepSeek / GPT-5 在 LCB 报分用的具体 cutoff 窗口是否互可比**：公开 tech report 写得粗，需要看 supplementary，多数没披露 [unknown]。
- **BigCodeBench-Hard 在 2026 是否已被 RL 针对**：social signal 上似乎有，但没看到 ablation [uncertain]。
- **Aider polyglot 的 edit-format 选择对榜上排名影响**：Paul Gauthier 在 blog 里有提，但没 head-to-head 表 [uncertain]。
- **RepoBench-v1.1 的更新频率**：repo 似乎在维护但 cadence 不规律 [unknown — 待核 commit log]。
- **CRUXEval 在 RL-on-CoT 后是否真的 saturate**：frontier 报 90+，但社区有质疑认为是 test set leak [推测]。

## 推荐外部材料

- [LiveCodeBench paper, arxiv 2403.07974](https://arxiv.org/abs/2403.07974) + [livecodebench.github.io](https://livecodebench.github.io/) — release-date filter 的标准参考，所有 Qwen-coder tech report 报 LCB 都该指向这里。
- [BigCodeBench paper, arxiv 2406.15877](https://arxiv.org/abs/2406.15877) + [bigcode-bench.github.io](https://bigcode-bench.github.io/) — 实际库调用的复杂度评测，配 Hard subset 看 frontier gap。
- [Aider leaderboards](https://aider.chat/docs/leaderboards/) — 唯一把 edit-format 失败独立计入的榜，且 cost 在主榜，多语言主榜。
- [USACO bench paper, arxiv 2404.10952](https://arxiv.org/abs/2404.10952) — 奥赛级 reasoning，platinum 题至 2026 仍未饱和，hard reasoning 标杆。
- [HumanEval-Pro paper, arxiv 2412.21199](https://arxiv.org/abs/2412.21199) — self-invoking 构造是延寿旧 benchmark 的最便宜手段，方法论可借鉴。
- [CRUXEval paper, arxiv 2401.03065](https://arxiv.org/abs/2401.03065) — execution 子能力的诊断标杆，看它的 category breakdown 比看总分有用。
- [RepoBench paper, arxiv 2306.03091](https://arxiv.org/abs/2306.03091) — repo-level 评测起点，配 CrossCodeEval (Ding et al., 2023) 看后续演化。
- [EvalPlus / HumanEval+ / MBPP+](https://github.com/evalplus/evalplus) — 同方向的 test-augmentation 路线，和 Pro 系互补。
- [MultiPL-E](https://nuprl.github.io/MultiPL-E/) — HE 跨 18 语言移植，多语言 capability 的便宜基线（contamination 注意）。

[^lcb_cutoff]: LCB v5 协议见 livecodebench.github.io/leaderboard，cutoff 选择是 reporter 责任。
[^bcb_hard]: BigCodeBench-Hard split, BigCode 2024-09 release notes.
[^aider_fmt]: Paul Gauthier, "Code editing benchmark" series, aider.chat/blog, 2024.
