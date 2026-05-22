# Ev11 — 公共 leaderboard 全景（截至 2026-05）

## 路线定位

读者是 Qwen 评测 owner，平时打交道的不是某个孤立 benchmark，而是「我们这次 release 要上哪几个公榜、怎么解释 delta」。本节梳理 2026-05 还活着的八个主流公榜 — **LMArena / Artificial Analysis / OpenCompass / SEAL / Vellum / HF Open LLM Leaderboard v2 / Aider Polyglot / Princeton HAL** — 加 Nathan Lambert 的 *Index* 作为 meta 视角。每个榜回答四问：methodology、coverage、bias、什么时候可信。结论先写在前面：**没有一个榜可以单独信**；frontier ranking 在 2026 已经事实上由「LMArena + AA + HAL + Aider」四件套交叉验证决定，单榜 SOTA 几乎一定是被 game 过的。

## 总表

| 名字 | 类型 | signal 主源 | 当前可信度 | 一手 URL |
|---|---|---|---|---|
| LMArena (Chatbot Arena) | 人类 pairwise 偏好 | crowdsourced votes | 偏好类金标准，但有 style/length bias | [lmarena.ai](https://lmarena.ai/) |
| Artificial Analysis | 自动 benchmark + price/speed | 自跑标准化 eval | 价格/吞吐最权威；intelligence 分是 composite | [artificialanalysis.ai](https://artificialanalysis.ai/) |
| OpenCompass (司南) | 大规模自动评测 + CompassRank | 中文+多任务覆盖最全 | 中文 / 闭源国产覆盖最好；contamination 受质疑 | [rank.opencompass.org.cn](https://rank.opencompass.org.cn/) |
| SEAL (Scale) | 私有 holdout benchmark | 专家+私题，不公开题 | adversarial robustness / agentic tool 最干净 | [scale.com/leaderboard](https://scale.com/leaderboard) |
| Vellum LLM Leaderboard | aggregator | 转引官方+第三方 | 给 PM 看的入门表；不要拿来下结论 | [vellum.ai/llm-leaderboard](https://www.vellum.ai/llm-leaderboard) |
| HF Open LLM Leaderboard v2 | 开源模型自动跑 | 6 个 benchmark，全开源 | 开源 base/SFT 模型挑选有用；frontier 不在上面 | [huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) |
| Aider Polyglot | 真编辑任务 pass-rate | 225 Exercism 跨 6 语言 | code edit format 唯一公榜；diff vs whole 区分严 | [aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/) |
| Princeton HAL | agent meta-榜 | cost-vs-accuracy frontier | agentic / cost-aware 比较的金标准 | [hal.cs.princeton.edu](https://hal.cs.princeton.edu/) |
| Interconnects *Index* | 主观汇总 | Nathan Lambert 月更 | 不是榜，但是 frontier narrative 校准 | [interconnects.ai](https://www.interconnects.ai/) |

> Note: v2 之后 HuggingFace 在 2025 把 Open LLM Leaderboard 改成 archive 状态，新提交转入 [Open LLM Arena](https://huggingface.co/spaces/lmarena-ai/chatbot-arena-leaderboard) 镜像与各 task-specific board，详见下文。

---

## LMArena (Chatbot Arena)

### methodology

- 用户在 [lmarena.ai](https://lmarena.ai/) 输入一个 prompt，平台同时调用两个匿名模型，用户选哪个更好（或 tie / both bad），结果喂给 Bradley-Terry / Elo 风格的 rating[^arena1]。2024-08 起官方切到 BT-MLE 而非裸 Elo，rating CI 更稳[^arena1]。
- 2024-11 起按 category 拆榜：Hard Prompts、Coding、Math、Longer Query、Multi-turn、Vision、WebDev Arena、Style-Control。Style-Control 是关键 — 它显式回归掉 markdown 量、response length、bullet 数，再算 rating，2024-Q4 后大家看 frontier 都改看 Style-Control 列[^arena-style]。
- 2025 起 LMArena 独立成公司（前身 LMSYS Arena），引入 *Prompts-to-Leaderboard* (P2L) 做 prompt-conditioned ranking[^arena-p2l]。

### coverage

frontier 闭源（OpenAI / Anthropic / Google / xAI）+ Meta / Mistral / DeepSeek / Qwen / Zhipu 等开源大头基本都在。2025 后期 Search Arena、Vision Arena、WebDev Arena、Copilot Arena（IDE 内）各自独立。

### bias / 已知问题

- **Style / length bias**：长答案、bullet 多、加 emoji 更容易赢，2024 已被 Cohere 团队 quantify（"Style Outweighs Substance"，[arxiv 2407.10457](https://arxiv.org/abs/2407.10457)）。Style-Control 部分修了但不完全。
- **prompt 分布偏 chatty**：crowdsourced prompt 偏 ChatGPT-like 通用问题，缺乏 long-context、agentic、严格 grading 信号。
- **The Leaderboard Illusion (Singh et al., 2025)**：[arxiv 2504.20879](https://arxiv.org/abs/2504.20879) 指控 Arena 给部分 provider 私下 A/B 多个 variant 再挑最好那个上榜，等价于 best-of-N 测试集污染。Arena 团队公开回应过部分条款，但模型 retraction policy 与 private testing 数仍是争议焦点[^arena-illusion]。
- **non-IID voter**：voter 不是随机抽样的 LM 用户，是会主动来打榜的 power user。

### 什么时候信

- 信：「这俩模型谁更讨喜 + 对话面更广」的相对感觉、style-control 后的 frontier 顺序。
- 不信：绝对差距、agentic / 长任务 / hard reasoning 排名（这些 category 样本量比 overall 小一个量级）、新发布模型一周内的 rating（CI 很宽）。

---

## Artificial Analysis (AA)

### methodology

- 自跑一组固定 benchmark（MMLU-Pro、GPQA Diamond、AIME、LiveCodeBench、SciCode、HLE 子集、Terminal-Bench、τ²-bench 等），加价格/吞吐/TTFT 实测，合成一个 **Intelligence Index**[^aa1]。2025 起切到 Intelligence Index v2 → v3，加入 agentic 任务权重。
- 价格 / throughput / latency 是 AA 的真正护城河：他们对每家 provider endpoint 周期性打点，是目前 inference 经济性 single source of truth。

### coverage

闭源 + 主流开源 + 主流 inference provider（Together、Fireworks、Groq、Cerebras、DeepInfra、SambaNova 等），覆盖到 host-level 差异。

### bias

- composite score 的权重是 AA 自己定的，2024 → 2026 改过多次，导致历史曲线不可严格纵比。
- benchmark 选择偏 STEM/coding，writing / multilingual / safety 几乎不进 index。
- HLE 等部分 benchmark 只跑子集（cost），与官方满分集不可严格对照。

### 什么时候信

- 信：price-vs-intelligence Pareto 图、provider-level latency/throughput、open-weight 在不同 host 上的实测速度。
- 不信：Intelligence Index 的绝对值差 < 3 分；用它判定哪个 frontier 模型「最聪明」。

---

## OpenCompass / CompassRank (司南)

### methodology

- 上海 AI Lab 开源的 [opencompass](https://github.com/open-compass/opencompass) 框架 + 闭榜 CompassRank。覆盖语言、知识、推理、代码、agent、长文本、多模态、安全等[^oc1]。
- 子榜很多：CompassAcademic / Compass Arena（含人评对战）/ CompassBench（私题集，季度更新）/ MathBench / CIBench / T-Eval / NeedleBench / OpenCompass-Multimodal（VLMEvalKit）等。

### coverage

- 中文 + 国产闭源（豆包 / GLM / Qwen / Kimi / DeepSeek / 文心 / 混元 / 阶跃 / MiniMax / Doubao-Seed 系列）覆盖最全。海外模型也跑但通常落后版本一两周。
- VLMEvalKit 是 vision-language 评测事实标准之一。

### bias

- 题库部分公开 → contamination 风险高，CompassBench 加私题集是回应。
- 评分脚本对 prompt template 敏感，国产模型常报「OpenCompass 复现 + 我自己的 system prompt」分。
- 中文 native 模型 vs 英文 native 模型在某些子任务上 prompt translation 公平性争议。

### 什么时候信

- 信：中文场景下模型选型、VLMEvalKit 的多模态横评、Compass Arena 的中文 pairwise（独立于 LMArena）。
- 不信：英文 frontier 排名直接看 CompassRank — 用 AA / LMArena 交叉。

---

## SEAL Leaderboards (Scale AI)

### methodology

- Scale AI 的 *Safety, Evaluations and Alignment Lab* 维护，最大卖点是 **private holdout** — 题目从不公开，由 Scale 内部 expert annotator 出题与评分[^seal1]。
- 子榜含：Humanity's Last Exam (HLE，与 CAIS 联运)、Multichallenge（多轮指令遵循）、Enigma Eval（puzzle）、VISTA（vision）、Tool Use、Agentic Tool Use、Multilingual、Adversarial Robustness、Coding 等。

### coverage

主要 frontier 闭源 + 头部开源；提交需要 API 访问（Scale 来跑），所以更新比 AA 慢。

### bias

- 私题 → contamination 风险最低，但也意味着「不能被独立复现」，要信 Scale 的评分员。
- expert 出题趋向 hard tail，frontier 之间区分度好，二三档模型容易扎堆。
- HLE 等榜的 grading rubric 部分披露，但 prompt 模板与 sampling 设置 frontier vendor 间不完全统一。

### 什么时候信

- 信：adversarial / tool-use / multilingual 这类容易 game 的方向 — SEAL 的私题是少数可信信号。
- 不信：把 SEAL 单榜数字当模型综合能力代理。

---

## Vellum LLM Leaderboard

- aggregator：从各家官方 tech report / system card / 第三方榜抓数字汇总成一张大表，加 price 与 context window 列[^vellum1]。
- 优点：给非研究读者（PM / 选型工程师）一个入口；price/context 一栏更新及时。
- 缺点：原始 benchmark 数字混合不同 prompt、不同 N、不同 scaffold，**横向相减没有意义**。Vellum 自己也在文档里说这是 reference table 不是 ranking。
- 什么时候信：你需要在 5 分钟内告诉一个 stakeholder「Claude 4.5 上下文多少 / 价格多少 / MMLU 大概什么档」。其它一律去看一手 system card。

---

## HuggingFace Open LLM Leaderboard v2

### methodology

- v2（2024-06 上线）替换 v1，原因是 v1 的 ARC / HellaSwag / MMLU 在 frontier 开源模型上已经被 saturate / contaminated[^hfv2]。v2 用 6 个更硬的 benchmark：**IFEval、BBH、MATH-Lvl5、GPQA、MUSR、MMLU-Pro**，全部 lm-eval-harness 自动跑、normalize 后求平均。
- 2025 中 HF 把主榜置为「archived / read-only」，原因是 (a) 算力补贴退坡 (b) frontier 已经不主要靠这种 closed-form benchmark 区分。新提交转向 task-specific leaderboard（如 [BigCodeBench leaderboard](https://huggingface.co/spaces/bigcode/bigcodebench-leaderboard)、[Chatbot Arena 镜像](https://huggingface.co/spaces/lmarena-ai/chatbot-arena-leaderboard)）和社区维护的 fork。

### coverage

只跑 open-weight 模型，主要是社区提交的 7B–70B SFT / merge / DPO 变体，frontier 闭源不在上面。

### bias

- IFEval 容易被 instruction-tune 直接刷分，过去一年通胀严重。
- MMLU-Pro / GPQA 的 5-shot vs 0-shot 设定对小模型影响巨大。
- merge / soup 模型 game 平均分的现象 2024 已被多篇 blog 记录（Maxime Labonne 等）。

### 什么时候信

- 信：在一堆开源 7B/14B SFT 变体里粗筛、确认某个 fine-tune 没明显 regress。
- 不信：用它判断「这个开源模型 vs Claude 4.5 谁强」 — 根本不在一个评测范式。

---

## Aider Polyglot

### methodology

- Aider 作者 Paul Gauthier 维护，用 225 道 Exercism 题，跨 C++ / Go / Java / JavaScript / Python / Rust 六种语言，模型必须以 *实际编辑 format*（whole-file replace / unified diff / search-replace block）输出，pass test 才算[^aider1]。
- 同时报 **pass rate** 与 **edit format success rate** — 后者衡量「模型是不是连 diff 格式都打不对」。

### coverage

frontier 闭源 + 主流 code-strong 开源（Qwen2.5/3-Coder、DeepSeek-Coder / V3 / R1、GLM-4.6 等）。更新很快，一般大模型发布当周就有数。

### bias

- Exercism 题偏 leetcode 风格小函数，离 SWE-Bench 那种 repo-scale 编辑差很远 — Aider 高分 ≠ 真实 codebase 强。
- diff format 的失败模式严重惩罚不熟悉 Aider 模板的模型；让模型 fine-tune 一下 diff 格式分数能跳很多。
- 题集公开 → contamination 不可避免，2025 起 Paul 加了私题 holdout 但占比不大。

### 什么时候信

- 信：「这个模型生成 patch 时格式稳不稳、小代码题对不对」。
- 不信：把 Aider 分当 agentic coding 能力上限 — 那是 SWE-Bench Verified / Terminal-Bench 的事。

---

## Princeton HAL (Holistic Agent Leaderboard)

### methodology

- Princeton CITP 的 Sayash Kapoor / Arvind Narayanan 组维护，**cost-controlled** 评测：同一个 agent benchmark（SWE-Bench Verified、Cybench、AppWorld、ScienceAgentBench、CORE-Bench 等）上同时报 accuracy 与 **\$ cost per task**，画 Pareto frontier[^hal1]。
- 立项动机就是反 best-of-N inflation：在 cost-normalize 之后，frontier 排名跟裸 accuracy 排名经常颠倒。

### coverage

agentic benchmark 为主，模型 × scaffold 组合都收。比 AA / LMArena 慢但更深。

### bias

- cost 是 API 报价口径，对自部署 / 量化推理不公平。
- benchmark 选择偏 academic agent 任务，离生产 agent 仍有距离。
- task-level cost 估计依赖 vendor 公布的 token 用量，部分 reasoning model 的 hidden CoT token 计费规则差异未完全 normalize。

### 什么时候信

- 信：「我有 \$X 预算 / task，选哪个 model+scaffold 最划算」。
- 不信：HAL 单榜的绝对 accuracy 数字 — 它的目的是 ranking 不是 SOTA。

---

## Interconnects *Index*（Nathan Lambert）

- 严格说不是 leaderboard，是 Nathan 在 [interconnects.ai](https://www.interconnects.ai/) 月度更新的 frontier model 主观 tier list（含 reasoning / non-reasoning / open-weight 三档）。
- 价值：作为「圈内人共识」的校准锚 — 当你看到一个公榜结果跟 Index 严重背离时，要先怀疑那个公榜被 game 了。
- 不要拿它去说服 stakeholder，但 release 前自己心里要有一份对照表。

---

## 实操建议（给 Qwen release）

1. **frontier-vs-frontier 主张**：必须同时在 LMArena Style-Control + AA Intelligence Index + HAL（agentic 任务）+ SEAL（私题）四处都能 hold；任何一个掉太多都需要解释。
2. **中文 / 国产对比**：CompassRank + Compass Arena 是绕不开的，但要附自己跑的 contamination 检查（n-gram overlap、canary string）。
3. **code release**：Aider Polyglot 报 pass rate + edit-format rate 两栏；SWE-Bench Verified 单独写，不要混到「leaderboard 列表」里。
4. **避免单榜 SOTA narrative**：2026 frontier 圈对单榜第一的可信度已经很低，pitch 应该写成「在 N 个独立榜上 top-K」。
5. **cost / latency**：AA 提供的 host-level 数据可以直接引用，不必自己再跑。

---

## 已知未解 / 争议

- LMArena 的 private testing policy 与 Cohere *Leaderboard Illusion* 的反复至今没有所有 party 都满意的 closure[^arena-illusion]。
- HLE（Humanity's Last Exam）跨 SEAL / AA / 各家 system card 报分口径不统一，sampling 设置披露不全。
- OpenCompass 闭题集 (CompassBench) 的更新频率与题源公平性外部无法审计。
- HF Open LLM Leaderboard 之后开源 frontier 模型缺一个**公认**的自动评测榜，目前事实上由 Aider + LiveCodeBench + 各家 task board 拼凑。

---

## 推荐外部材料

- [Chatbot Arena: An Open Platform for Evaluating LLMs (arxiv 2403.04132)](https://arxiv.org/abs/2403.04132) — Arena 原始 paper，BT 模型细节都在这。
- [Style Outweighs Substance (arxiv 2407.10457)](https://arxiv.org/abs/2407.10457) — 量化 Arena 的 style bias，Style-Control 的动机文献。
- [The Leaderboard Illusion (arxiv 2504.20879)](https://arxiv.org/abs/2504.20879) — Cohere 对 Arena 私下 A/B 的指控，必读。
- [HF Open LLM Leaderboard v2 blog](https://huggingface.co/spaces/open-llm-leaderboard/blog) — v1 为什么退役、v2 选 benchmark 的逻辑。
- [HAL paper / blog (Kapoor et al. 2024)](https://hal.cs.princeton.edu/) — cost-controlled agent eval 的方法论。
- [Artificial Analysis methodology pages](https://artificialanalysis.ai/methodology) — Intelligence Index 怎么算、版本变化。
- [Aider Leaderboards docs](https://aider.chat/docs/leaderboards/) — edit format 与 pass rate 的区分。
- Nathan Lambert, ["The state of frontier model evaluations"](https://www.interconnects.ai/) — 月度 frontier 观察，订阅一下省时间。

[^arena1]: Chiang et al., "Chatbot Arena: An Open Platform for Evaluating LLMs", [arxiv 2403.04132](https://arxiv.org/abs/2403.04132).
[^arena-style]: LMArena blog, "Does Style Matter?", [lmsys.org/blog/2024-08-28-style-control](https://lmsys.org/blog/2024-08-28-style-control/).
[^arena-p2l]: Frick et al., "Prompt-to-Leaderboard", [arxiv 2502.14855](https://arxiv.org/abs/2502.14855).
[^arena-illusion]: Singh et al., "The Leaderboard Illusion", [arxiv 2504.20879](https://arxiv.org/abs/2504.20879)；LMArena 官方回应 [lmarena.ai/blog](https://lmarena.ai/blog).
[^aa1]: Artificial Analysis methodology, [artificialanalysis.ai/methodology](https://artificialanalysis.ai/methodology).
[^oc1]: OpenCompass docs, [opencompass.readthedocs.io](https://opencompass.readthedocs.io/) ；CompassRank [rank.opencompass.org.cn](https://rank.opencompass.org.cn/).
[^seal1]: Scale SEAL leaderboards, [scale.com/leaderboard](https://scale.com/leaderboard).
[^vellum1]: Vellum LLM Leaderboard, [vellum.ai/llm-leaderboard](https://www.vellum.ai/llm-leaderboard).
[^hfv2]: HuggingFace, "Open LLM Leaderboard v2", [huggingface.co/spaces/open-llm-leaderboard/blog](https://huggingface.co/spaces/open-llm-leaderboard/blog).
[^aider1]: Aider leaderboards, [aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/).
[^hal1]: Kapoor et al., HAL — Holistic Agent Leaderboard, [hal.cs.princeton.edu](https://hal.cs.princeton.edu/).
