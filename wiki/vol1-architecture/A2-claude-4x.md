# Claude 4.x 家族（含 3.5 / 3.7 过渡）

## 路线定位

Anthropic 在 2024-2025 走的是一条**"hybrid reasoning + agentic tool use"** 路线：不像 OpenAI 把 reasoning 单独拆成 o-series，而是把 extended thinking 作为同一模型的可选模式（"hybrid reasoning model" 一词由 Anthropic 在 3.7 Sonnet 公告里首次提出[^37sonnet]）。竞争对手主要是 GPT-5 / o-series（推理）和 Gemini 2.5（长上下文 + 多模态）。差异化卖点：**SWE-Bench Verified 第一档 + Computer Use + MCP 生态** + 偏重 alignment（Constitutional AI / RSP）。模型走 Opus（旗舰）/ Sonnet（主力）/ Haiku（小快好省）三档，参数从不披露。

## 代表模型清单

| 模型 | 发布日 | 参数/激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| Claude 3.5 Sonnet | 2024-06-20 | 未披露 | 新一代基座，artifacts | [anthropic.com/news/claude-3-5-sonnet](https://www.anthropic.com/news/claude-3-5-sonnet) |
| Claude 3.5 Sonnet (new) + Haiku | 2024-10-22 | 未披露 | **Computer Use** beta；SWE-Bench Verified 49% | [anthropic.com/news/3-5-models-and-computer-use](https://www.anthropic.com/news/3-5-models-and-computer-use) |
| MCP (协议，非模型) | 2024-11-25 | — | Model Context Protocol 开源 | [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol) |
| Claude 3.7 Sonnet | 2025-02-24 | 未披露 | 首个 **hybrid reasoning** 模型，extended thinking 可调 token 预算；Claude Code CLI 同步发布 | [anthropic.com/news/claude-3-7-sonnet](https://www.anthropic.com/news/claude-3-7-sonnet) |
| Claude Opus 4 + Sonnet 4 | 2025-05-22 | 未披露 | "Claude 4" 代际；Opus 4 长程 agent（公告里给的 7 小时连续 coding）；SWE-Bench Verified 72.5%/72.7% | [anthropic.com/news/claude-4](https://www.anthropic.com/news/claude-4) |
| Claude Opus 4.1 | 2025-08-05 | 未披露 | Opus 4 增量升级，SWE-Bench 74.5% | [anthropic.com/news/claude-opus-4-1](https://www.anthropic.com/news/claude-opus-4-1) |
| Claude Sonnet 4.5 | 2025-09-29 | 未披露 | "best coding model in the world"；SWE-Bench Verified 77.2%，OSWorld 61.4%（Computer Use SOTA） | [anthropic.com/news/claude-sonnet-4-5](https://www.anthropic.com/news/claude-sonnet-4-5) |
| Claude Haiku 4.5 | 2025-10-15 | 未披露 | 把 Sonnet 4 级 coding 压到 Haiku 价位（$1/$5 per Mtok） | [anthropic.com/news/claude-haiku-4-5](https://www.anthropic.com/news/claude-haiku-4-5) |
| Claude Opus 4.5 | 2025-11-24 | 未披露 | Opus 线最新；强调 agentic + 长程 | [anthropic.com/news/claude-opus-4-5](https://www.anthropic.com/news/claude-opus-4-5) |
| "Claude 4.7" (Sonnet/Opus) | 2026 Q1-Q2? | — | [unknown — 截至 2026-05 我没找到 Anthropic 正式发布 4.7 的一手 source；任务标题提及，但不强行编造] | — |

> 注：所有 Claude 模型 Anthropic 从未公开参数量、激活量、训练数据 token 数、训练算力。以下"架构核心"基本都是 [推测] 或来自第三方推断。

## 架构核心

Anthropic 对架构守口如瓶，比 OpenAI 还要紧。**没有任何 Claude 模型公开过 paper 描述其架构。** 已知或第三方可信推断的点：

- **Dense vs MoE**：Anthropic 从未确认。Dario 在 2024-2025 多次访谈避谈，但提到 "we don't talk about architecture"（[Lex Fridman #452, 2024-11](https://lexfridman.com/dario-amodei)）。第三方（SemiAnalysis 2024 报道）[推测] Claude 3 Opus 是 dense 大模型，3.5 Sonnet 可能是中等规模 dense。4.x 是否 MoE [unknown]。
- **上下文长度**：3.5 起 200K token；Sonnet 4 / 4.5 在 API 上提供 **1M token beta**（[Sonnet 4 1M context 公告 2025-08](https://www.anthropic.com/news/1m-context)）。具体用的是 ring attention / 别的 sparse 方案 [unknown]。
- **Tokenizer**：未公开。第三方 byte-level / BPE 推测都有。
- **Vision**：3 系起原生多模态（图像 in）。Anthropic 没有放出图像生成。
- **Extended thinking 机制**：3.7 起，模型在 reasoning mode 下产生可见的 `<thinking>` block，token budget 由 API 参数 `budget_tokens` 控制（[Extended Thinking docs](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)）。和 OpenAI o-series 把 reasoning trace 隐藏不同，Claude **默认展示**（虽然官方 disclaimer 说不保证忠实于真实计算）。这是 hybrid reasoning 的关键产品差异。

## 训练方法核心

### Pretrain
- Data scale / composition：**完全未披露**。
- 算力：未披露。Dario 在 2024 Davos / 2025 Council on Foreign Relations 访谈里 [口头] 提到 Claude 3 训练成本"in the hundreds of millions"，下一代"$1B+"，再下一代"$10B"（[Dario CFR 2025](https://www.cfr.org/event/conversation-dario-amodei)，无书面 source）。

### Post-train —— 核心壁垒
Anthropic 的 alignment / post-train pipeline 是其公开材料最丰富的部分，必须看：

1. **Constitutional AI (CAI)**：原始论文 [Bai et al. 2022, arxiv:2212.08073](https://arxiv.org/abs/2212.08073)。流程 = SFT on critique-and-revise + **RLAIF**（用 AI 模型按 constitution 打偏好，替代人工 preference label）。这是 Claude 安全训练的 foundation。
2. **Collective Constitutional AI**：2023-10，[blog](https://www.anthropic.com/news/collective-constitutional-ai-aligning-a-language-model-with-public-input)，让 ~1000 公众投票形成 constitution。学术价值大于实用，但说明 constitution 是可替换的。
3. **Character training**：[blog 2024-06](https://www.anthropic.com/news/claude-character) 描述 3.5 起的 "Claude personality" 训练 —— 把 trait 描述喂回 RLAIF。
4. **RLVR (Reinforcement Learning from Verifiable Rewards)**：Anthropic 没有用这个术语命名，但 3.7 Sonnet 公告明确写 "we focused our training on real-world tasks ... particularly in coding"，且 SWE-Bench 大跳水（49% → 62.3%）的来源 [推测] 是 agentic RL on executable code feedback。Lambert 在 [interconnects.ai 2025-03](https://www.interconnects.ai/p/claude-37-and-the-frontier-of-reasoning) 把这归类为 RLVR。
5. **Long-horizon agentic RL**：Opus 4 公告里强调 "sustained performance over hours of agentic work"，且 Sonnet 4.5 公告报告"can maintain focus for 30+ hours on complex multi-step tasks"。具体 RL 算法、reward shaping 都未披露。
6. **RSP (Responsible Scaling Policy)**：[RSP v2.0, 2024-10](https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy) 定义 ASL-2 / ASL-3 thresholds。Opus 4 是 Anthropic **第一个按 ASL-3 部署的模型**（[Claude 4 system card](https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47.pdf)），有额外的 misuse 防护和 weight 安全。

### Computer Use
- 2024-10 首发（3.5 Sonnet new）。模型直接输出 screen coordinates + keystrokes，无 special vision tower（[blog](https://www.anthropic.com/news/3-5-models-and-computer-use)）。
- 训练 [推测] 用合成 GUI trajectories + 真实截图 SFT + RL。
- Benchmark：OSWorld。3.5 Sonnet new 14.9% → Sonnet 4 28% → **Sonnet 4.5 61.4%**（Anthropic 自报，[Sonnet 4.5 blog](https://www.anthropic.com/news/claude-sonnet-4-5)）。

### MCP（Model Context Protocol）
- 2024-11 开源（[spec.modelcontextprotocol.io](https://modelcontextprotocol.io/)）。
- 不是训练方法，是 **tool integration 标准**：把 client（Claude Desktop / Cursor / IDE）和 server（FS / DB / API）解耦。
- 2025 被 OpenAI / Google / Cursor / Zed / JetBrains 全部支持，事实标准化。意义：Anthropic 用协议层把 agent ecosystem 锁在自己定义的接口上 —— 比"模型最强"更长期的护城河。
- 评论：[Willison 2024-11](https://simonwillison.net/2024/Nov/25/model-context-protocol/) 把 MCP 类比为"USB-C for AI tools"。

## 与 eval / benchmark 的接口

官方 headline benchmark（按 Anthropic 报告）：

| Bench | 3.5 Sonnet new | 3.7 Sonnet (think) | Opus 4 | Sonnet 4.5 | Opus 4.5 |
|---|---|---|---|---|---|
| SWE-Bench Verified | 49.0 | 70.3 | 72.5 | **77.2** | 80.9 (claimed) |
| OSWorld | 14.9 | — | 28 | **61.4** | — |
| GPQA Diamond | 65 | 84.8 | 79.6 | 83.4 | — |
| MMMU | 70 | — | 76.5 | 77.8 | — |
| TAU-bench (airline) | — | 58.4 | — | 66 | — |

**SWE-Bench Verified 数字注意事项**：
- Anthropic 报告时常带 "with parallel test-time compute" 或 "with custom scaffold" 脚注 → 不是单次 forward pass。Sonnet 4.5 的 77.2% 是单次，但更高数字（如 82%）用了 n=多 sample + verifier（[Sonnet 4.5 system card 第 3 节](https://www-cdn.anthropic.com/sonnet-4-5-system-card.pdf)）。比较时务必看 scaffold 一致。
- 第三方复现：Princeton SWE-Bench leaderboard 维护，Sonnet 4.5 的官方分基本能复现。Aider polyglot benchmark（[aider.chat/2024/12/21/polyglot.html](https://aider.chat/2024/12/21/polyglot.html)）也是常用第三方 ref。

**Contamination 信号**：
- Anthropic 在 4.x system card 里有 "we filtered SWE-Bench Verified instances from training data" 声明（Opus 4 system card §4），但无第三方独立审计。
- TAU-bench 是 Anthropic 自家出品（Sierra/Anthropic 联合），用它当 agentic eval 有 owner bias，焱拳团队评测时建议交叉用 SWE-Bench Multimodal / SWE-Lancer。

## 未知与争议

- **架构**：参数、激活、MoE/dense、attention 变种、tokenizer —— 全未披露。
- **训练算力**：未披露。
- **训练数据**：未披露；2024 NYT 类似版权诉讼 Anthropic 也有（Bartz v. Anthropic, 2024）涉及 books3 类数据。
- **Extended thinking 的真实性**：Anthropic 自己的 [研究 2025-04 "reasoning models don't always say what they think"](https://www.anthropic.com/research/reasoning-models-dont-say-think) 表明，Claude 的可见 thinking trace 与内部决策只有部分对齐 —— 焱拳如果想用 thinking trace 做 distill 数据，要注意 faithfulness 问题。
- **Sonnet 4.5 vs Opus 4.5 定位混乱**：2025-11 Opus 4.5 出来时，部分 benchmark Opus 4.5 仅比 Sonnet 4.5 高 1-3 pt，但价格 5×。是否真的需要 Opus tier 业界有质疑（见 [Willison 2025-11](https://simonwillison.net/2025/Nov/24/claude-opus-4-5/)）。
- **"Claude 4.7"**：截至 2026-05 我没找到 Anthropic 发布 4.7 命名的一手 source。可能任务上下文里指的是 internal 代号或未来 roadmap，标 [unknown — 没找到一手 source]。

## 推荐外部材料

- [Claude 4 system card (PDF)](https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47.pdf) — 唯一接近 tech report 的官方文档，重点看 §3 capabilities 和 §6 alignment evals。
- [Constitutional AI paper (arxiv:2212.08073)](https://arxiv.org/abs/2212.08073) — RLAIF 起点，所有 Claude 安全训练的 root。
- [Anthropic Interpretability —— transformer-circuits.pub](https://transformer-circuits.pub/) — Olah 团队 monosemanticity / SAE / 2024-05 "Scaling Monosemanticity"（Claude 3 Sonnet 上的 SAE feature 抽取，是目前最深入的 frontier 模型内部 reverse-engineer）。
- [Sebastian Raschka, "Understanding Reasoning LLMs", 2025-02](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms) — 把 Claude 3.7 的 hybrid reasoning 与 o1/R1 放一起对比，分类清晰。
- [Nathan Lambert interconnects.ai —— Claude 系列复盘](https://www.interconnects.ai/t/claude) — 每代 Claude 出来 Lambert 当天就写 post-train 视角的解读，是最快的非官方 RLHF/RLVR analysis。
- [Simon Willison's blog —— claude tag](https://simonwillison.net/tags/claude/) — 每个版本第一时间的 hands-on，包含价格/API 行为/regression notes。
- [Dario Amodei "Machines of Loving Grace", 2024-10](https://darioamodei.com/machines-of-loving-grace) — 不是 tech，是 Anthropic 对 frontier 模型未来 5 年的世界观，理解他们为什么把资源压在 agentic + alignment 上。
- [MCP spec](https://modelcontextprotocol.io/specification) — 想接 Claude agent 必读；理解为什么 2025 后 agent ecosystem 都跑这套协议。

[^37sonnet]: https://www.anthropic.com/news/claude-3-7-sonnet — "Claude 3.7 Sonnet is the first hybrid reasoning model on the market."
