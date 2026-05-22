# OpenAI o-series 与 GPT-5（reasoning 家族）

## 路线定位

OpenAI 的 reasoning 家族是 "test-time compute scaling" 路线的标杆产品线：把 long CoT + RLVR 当作和 pretrain scaling 并列的第二条 scaling 轴。竞争对象是 Anthropic Claude 3.7/4 的 extended thinking、Google Gemini 2.5 Thinking、DeepSeek R1 系列、xAI Grok 4。GPT-5（2025-08）之后该家族与主线 GPT 模型合并成一个 router-based 系统，o-series 品牌停用[^gpt5-launch]。

## 代表模型清单

| 模型 | 发布日 | 参数/激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| o1-preview / o1-mini | 2024-09-12 | [unknown — 未披露] | 首个公开 long-CoT RL 模型，hide thinking tokens | [Learning to reason with LLMs][^o1-launch] |
| o1 (full) | 2024-12-05 | [unknown] | 多模态输入、function calling、structured output | [o1 system card][^o1-card] |
| o1-pro | 2024-12-05 (ChatGPT Pro) / 2025-03 (API) | [unknown] | 同 o1 weights，推理时用更多 compute（self-consistency / parallel）[推测] | [Pro tier 公告][^pro] |
| o3-mini | 2025-01-31 | [unknown] | 三档 reasoning_effort（low/med/high），function calling+structured output；价格低于 o1-mini | [o3-mini blog][^o3mini] |
| o3 | 2025-04-16 | [unknown] | full tool use during reasoning（搜索、Python、图像查看），ARC-AGI-1 突破 | [Introducing o3 and o4-mini][^o3o4mini] |
| o3-pro | 2025-06-10 | [unknown] | 同 o3 + 更高 test-time compute | [o3-pro blog][^o3pro] |
| o4-mini | 2025-04-16 | [unknown] | 小尺寸 reasoning + 全工具，AIME 2024/2025 SoTA-for-size | [Introducing o3 and o4-mini][^o3o4mini] |
| GPT-5 | 2025-08-07 | [unknown] | unified system：router 在 "fast" 主干和 "thinking" 模型间切换；reasoning_effort=minimal 档位 | [Introducing GPT-5][^gpt5-launch] / [GPT-5 system card][^gpt5-card] |
| GPT-5-mini / nano | 2025-08-07 | [unknown] | 小尺寸 GPT-5 系列 | [GPT-5 for developers][^gpt5-dev] |
| GPT-5-Pro | 2025-10-06 | [unknown] | 长 thinking + parallel sampling | [GPT-5 Pro 公告][^gpt5pro] |
| GPT-5-Codex | 2025-09-15 | [unknown] | 针对 Codex agent harness 微调的 GPT-5 变体，"dynamic thinking"——可在单 task 内长达数小时持续工作 | [GPT-5-Codex blog][^codex] |
| GPT-5.1 / GPT-5.1-Codex | 2025-11-12 / 2025-11 | [unknown] | "adaptive reasoning" 自适应分配 thinking budget；warmer 语气 | [GPT-5.1 blog][^gpt51] |

> 截至 2026-05，公开模型卡均未披露参数量、训练数据规模、训练算力。下面所有 "架构核心" 都是 paper / blog 明说的内容，未披露处一律 [unknown]。

## 架构核心

- **没有架构 paper**。OpenAI 自 GPT-4 起未发布 architecture paper。o1/o3/GPT-5 的 system card 只写 capability + safety，不写 layer 数、d_model、head 数、attention 变体[^o1-card][^gpt5-card]。
- **Long CoT 是 model behavior，不是 architecture**。o1 blog 明确："o1 thinks before it answers, producing a long internal chain of thought"，hidden CoT 通过 RL 训练得到，不依赖 prompt[^o1-launch]。
- **Reasoning tokens 计费独立**。API 里 reasoning tokens 算 output tokens，但不返回给用户；这是 product decision，不是 architecture[^o1-api]。
- **GPT-5 是 system 而非单模型**。官方原话："GPT-5 is a unified system with a smart, efficient model… a deeper reasoning model (GPT-5 thinking)… and a real-time router that quickly decides which to use"[^gpt5-launch]。router 本身是一个分类器，根据 conversation type、complexity、tool 需求、显式 "think hard" 触发词路由[^gpt5-launch]。
- **reasoning_effort=minimal**（GPT-5 新增）：几乎零 reasoning tokens，相当于 non-thinking 模式，用于 latency-sensitive 场景[^gpt5-dev]。
- **GPT-5-Codex "dynamic thinking"**：官方说该模型在 codex CLI / IDE 里能根据任务复杂度自调 thinking 时长，简单任务秒级、复杂 refactor 任务持续 7 小时以上[^codex]。具体实现机制（是 RL reward shaping、还是 inference-time controller）未披露。
- **GPT-5.1 "adaptive reasoning"**：进一步细化 thinking budget 的自适应分配，简单 query 比 GPT-5 少 token 一半，难 query 多两倍[^gpt51]。

## 训练方法核心

### Pretrain
- 数据规模、tokenizer、context length 训练细节、RoPE base、MuP 使用情况——全部 [unknown — 未披露]。
- Context window 公开值：o1 = 128k input / 32k output（o1）/ 100k output（o1-pro API）；o3 / o4-mini = 200k / 100k；GPT-5 = 400k total / 128k output[^gpt5-dev]。

### Reasoning post-train（核心创新）
- o1 blog 明说："Our large-scale reinforcement learning algorithm teaches the model how to think productively using its chain of thought in a highly data-efficient training process"[^o1-launch]。
- 这是 **RLVR（RL with verifiable rewards）**：在数学/代码/逻辑等有 ground-truth 的 domain 上用 RL 训练 long CoT。OpenAI 没用 "RLVR" 这个词，但 DeepSeek-R1 paper 之后业界统一用此命名[^r1]。
- **scaling law（test-time）**：o1 blog 给出双 log 图——performance 随 train-time RL compute 和 test-time thinking compute 都呈 log-linear 上升[^o1-launch]。这是该家族的核心 thesis。
- **RL 算法细节**：[unknown]。Noam Brown（o1 核心作者）在 2024-10 MIT 演讲只说 "it's reinforcement learning"，不透露是否 PPO/GRPO/其它[^noam-mit]。Sasha Rush 的 "Speculations on Test-Time Scaling" 列了四种可能 search/RL hybrid，但都是 outsider 猜测[^rush-talk]。
- **process reward model (PRM) vs outcome reward model (ORM)**：OpenAI 2023 "Let's Verify Step by Step" 用 PRM800K 训 PRM[^prm800k]；但 o1 / o3 是否仍用 PRM，**官方未确认**。DeepSeek-R1 paper 明确说 PRM 在他们的实验里 reward hacking 严重、放弃了[^r1]——这是社区对 o1 同样可能仅用 ORM 的间接证据 [推测]。

### Mid-train / annealing
- [unknown]。OpenAI 从未公开任何 mid-train 配方。

### Agentic RL（GPT-5-Codex 时代）
- GPT-5-Codex blog："trained on real-world software engineering tasks… code review, building projects from scratch, adding tests"[^codex]。
- 具体 environment、reward、trajectory 长度——[unknown]。
- 与 Anthropic Claude Code、Cursor composer agent、Cognition Devin 是同一波 agentic RL 浪潮，但没有任何一家公开 training stack。

### 算力
- [unknown]。GPT-5 system card 未给 FLOPs。第三方估算（Epoch AI）认为 GPT-5 thinking pretrain compute 与 GPT-4.5（≈10^26 FLOPs 量级）同级或略低，节省的预算花在 RL[^epoch-gpt5][推测]。

## 与 eval / benchmark 的接口

### 官方报的数字
- **o1**：AIME 2024 = 83.3%（pass@1，cons@64 ≈ 93%）、Codeforces ELO 1807（89th percentile）、GPQA Diamond 78%[^o1-launch]。
- **o3**：ARC-AGI-1 semi-private 87.5%（high compute setting，单 task >$1000 推理成本）、76% (low compute)；SWE-bench Verified 71.7%；Codeforces 2727[^o3-arc][^o3o4mini]。
- **o4-mini**：AIME 2025 99.5%（with Python tool）、92.7% (without)[^o3o4mini]。AIME 接近饱和。
- **GPT-5**：SWE-bench Verified 74.9%、Aider Polyglot 88%、AIME 2025 94.6% (no tools)、HMMT 2025 96.7%[^gpt5-launch]。
- **GPT-5-Codex**：SWE-bench Verified 74.5%（与 GPT-5 持平），但 code refactoring eval 上 51.3% vs GPT-5 33.9%[^codex]。

### 第三方独立复现 / 质疑
- ARC-AGI 团队（François Chollet）独立验证了 o3 87.5% 数字，并强调高 compute setting 单题成本极高、不能简单类比传统 benchmark[^arc-blog]。
- **ARC-AGI-2** 上同样 o3 配置降到 4%，3 月又升级到 ~6%[^arc-blog]。
- Epoch AI FrontierMath：o3 announce 时 25.2%，但 Epoch 后来披露 OpenAI 资助了 dataset 构建并能访问大部分题目，引发 contamination 质疑[^epoch-frontiermath]。
- METR：GPT-5 在 "50% time horizon" benchmark 上达到 ~2h17min，比 o3 的 ~1h30min 长[^metr-gpt5]。
- Aider polyglot leaderboard：GPT-5 (high) 88% 是 2025-08 SoTA，被 Claude Sonnet 4.5 / GPT-5.1 后续超越[^aider]。

### 已知 contamination / overfit 信号
- FrontierMath 资助关系（见上）。
- AIME 已接近饱和（>95%），区分度下降，社区开始用 HMMT、Putnam、USAMO 替代[^lambert-evals]。
- SWE-bench Verified 数字在不同 harness / scaffold 下差异巨大；OpenAI 报 74.9% 用的是 "high reasoning + retry"，与 Anthropic 直接 single-attempt 数字不可直接比较[^swebench-note]。

## 未知与争议

OpenAI 未披露的（截至 2026-05）：
- 任何 o-series / GPT-5 模型的参数量、激活参数、layer/dim 配置。
- pretrain 数据组成、tokenizer 变化、context 扩展方法（YaRN? NTK? 自研？）。
- RL 算法（PPO / GRPO / REINFORCE++ / 自研？）、reward model 架构、CoT length distribution。
- GPT-5 router 的训练方式（监督？bandit？）、failure mode、用户能否绕过。
- GPT-5-Codex "dynamic thinking" 的控制接口——是 model-internal 决策、还是 harness-side controller。

第三方 reverse-engineer 推测 [推测]：
- Nathan Lambert：o1 大概率是 "single autoregressive model trained with RL on CoT"，不是 MCTS / tree search[^lambert-o1]。R1 出来后此推测被广泛接受。
- Sebastian Raschka：把 o1/R1 类方法归纳为 "RL on CoT with verifier"，并指出 OpenAI 与 DeepSeek 在算法 family 上几乎确定是同一族[^raschka-r1]。
- Simon Willison：GPT-5 router 实战中经常把 hard prompt 路由到 fast model 导致质量下降，可通过 "think hard about this" 或选 "GPT-5 Thinking" 显式触发[^simonw-gpt5]。
- 关于 GPT-5 是否是 "GPT-5 = orchestrator + GPT-4.5-distill + o3-successor"——OpenAI 否认是简单 ensemble，强调是 jointly trained system，但联合训练细节 [unknown]。

## 推荐外部材料

- [Sebastian Raschka — Understanding Reasoning LLMs](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms) — 最清晰的 o1/R1 类方法 taxonomy（SFT-distill / RL-only / SFT+RL / inference-time search）。
- [Nathan Lambert — Interconnects o1/o3/GPT-5 系列](https://www.interconnects.ai/) — 持续 tracking OpenAI RL 路线，含 RLVR 命名来源。
- [Sasha Rush — Speculations on Test-Time Scaling (o1)](https://www.youtube.com/watch?v=6PEJ96k1kiw) — 学术界对 o1 实现的早期推测合集，列了 4 种假设。
- [Simon Willison's Weblog — GPT-5 tag](https://simonwillison.net/tags/gpt-5/) — 第一手 hands-on review，对 router 行为有大量实测。
- [DeepSeek-R1 paper (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — 唯一开放的 o1-class 训练配方，事实上的 reference implementation。
- [ARC Prize blog — OpenAI o3 breakthrough](https://arcprize.org/blog/oai-o3-pub-breakthrough) — Chollet 团队对 o3 ARC 成绩的独立分析与 compute cost 讨论。
- [Epoch AI — Compute estimates for frontier models](https://epoch.ai/) — 第三方 FLOPs 估算的权威来源。
- [METR — Measuring AI ability to complete long tasks](https://metr.org/blog/) — "time horizon" benchmark 是目前最能区分 frontier reasoning 模型的指标之一。

---

[^o1-launch]: OpenAI, "Learning to reason with LLMs", 2024-09-12. https://openai.com/index/learning-to-reason-with-llms/
[^o1-card]: OpenAI, "OpenAI o1 System Card", 2024-12. https://openai.com/index/openai-o1-system-card/
[^o1-api]: OpenAI API docs, "Reasoning models". https://platform.openai.com/docs/guides/reasoning
[^pro]: OpenAI, "Introducing ChatGPT Pro", 2024-12-05. https://openai.com/index/introducing-chatgpt-pro/
[^o3mini]: OpenAI, "OpenAI o3-mini", 2025-01-31. https://openai.com/index/openai-o3-mini/
[^o3o4mini]: OpenAI, "Introducing OpenAI o3 and o4-mini", 2025-04-16. https://openai.com/index/introducing-o3-and-o4-mini/
[^o3pro]: OpenAI, "Introducing o3-pro", 2025-06-10. https://openai.com/index/introducing-o3-pro/
[^gpt5-launch]: OpenAI, "Introducing GPT-5", 2025-08-07. https://openai.com/index/introducing-gpt-5/
[^gpt5-card]: OpenAI, "GPT-5 System Card", 2025-08. https://openai.com/index/gpt-5-system-card/
[^gpt5-dev]: OpenAI, "Introducing GPT-5 for developers", 2025-08-07. https://openai.com/index/introducing-gpt-5-for-developers/
[^gpt5pro]: OpenAI, "Introducing GPT-5 Pro", 2025-10. https://openai.com/index/introducing-gpt-5-pro/
[^codex]: OpenAI, "Introducing upgrades to Codex (GPT-5-Codex)", 2025-09-15. https://openai.com/index/introducing-upgrades-to-codex/
[^gpt51]: OpenAI, "GPT-5.1: A smarter, more conversational ChatGPT", 2025-11-12. https://openai.com/index/gpt-5-1/
[^noam-mit]: Noam Brown, MIT EI seminar, 2024-10. https://www.youtube.com/watch?v=eaAonE58sLU
[^rush-talk]: Sasha Rush, "Speculations on Test-Time Scaling (o1)", 2024-10. https://www.youtube.com/watch?v=6PEJ96k1kiw
[^prm800k]: Lightman et al., "Let's Verify Step by Step", arXiv:2305.20050, 2023. https://arxiv.org/abs/2305.20050
[^r1]: DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL", arXiv:2501.12948, 2025. https://arxiv.org/abs/2501.12948
[^epoch-gpt5]: Epoch AI, "How much compute did GPT-5 use?", 2025-08. https://epoch.ai/
[^o3-arc]: ARC Prize, "OpenAI o3 Breakthrough High Score on ARC-AGI-Pub", 2024-12-20. https://arcprize.org/blog/oai-o3-pub-breakthrough
[^arc-blog]: ARC Prize blog. https://arcprize.org/blog
[^epoch-frontiermath]: Epoch AI FrontierMath 资助披露讨论。https://epoch.ai/frontiermath
[^metr-gpt5]: METR, "Measuring AI ability to complete long tasks". https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
[^aider]: Aider polyglot leaderboard. https://aider.chat/docs/leaderboards/
[^lambert-evals]: Nathan Lambert, "State of frontier model evals", Interconnects. https://www.interconnects.ai/
[^swebench-note]: SWE-bench leaderboard methodology notes. https://www.swebench.com/
[^lambert-o1]: Nathan Lambert, "OpenAI's o1 using 'search' was a PSYOP", Interconnects, 2024-12. https://www.interconnects.ai/p/openais-o1-using-search-was-a-psyop
[^raschka-r1]: Sebastian Raschka, "Understanding Reasoning LLMs", 2025-02. https://magazine.sebastianraschka.com/p/understanding-reasoning-llms
[^simonw-gpt5]: Simon Willison, "GPT-5: Key characteristics, pricing and model card", 2025-08-07. https://simonwillison.net/2025/Aug/7/gpt-5/
