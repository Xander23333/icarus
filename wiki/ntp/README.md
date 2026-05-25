# NTP — Non-Tokenizable Problems

> A long-running, autonomously-maintained research survey on the **mechanism-level capability boundary of next-token prediction (NTP)**.

## 核心问题

1. **Next-token prediction 是否足以产生真正意义上的智能？**
2. **是否存在机制级 (mechanism-level) 无法由 token-prediction-trained LLM 解决的问题？**
3. **哪些能力必须依赖**：真实世界交互 (interaction) / 在线反馈 (online feedback) / 因果干预 (intervention) / embodied experience —— 而非仅靠更多 token 与更多算力？

## 工作定义

> **NTP (Non-Tokenizable Problem)** ≜ 无法仅通过对 i.i.d. 文本语料的 next-token prediction 训练目标稳定建模或求解的问题集合。

注意区分 (本调研全程严格维护):

- **NTP-mech**：机制上不可由 token prediction 获得的能力（如：需要因果干预的反事实推断、需要 embodied closed-loop 的运动控制）。
- **NTP-cap**：当前训练规模/数据/objective 下尚未获得，但**机制上不排除**未来可由扩展的 token-prediction 训练范式获得的能力。
- **Pseudo-NTP**：表面看是 NTP，实际上只是数据/接口/inference-budget 受限的工程缺口。

> *本调研的最终学术目标：建立一个类似 P/NP 的「LLM 能力分类体系」，把 NTP-mech / NTP-cap / Pseudo-NTP 分开。*

## 目录结构

```
ntp/
├── survey/              # 长期演化的主综述
│   ├── ntp_survey.md    # 主文档
│   ├── timeline.md      # 时间线
│   └── taxonomy.md      # 分类体系
├── topics/              # 8 大子方向
├── papers/paper_notes/  # 单篇精读笔记
├── daily_reports/       # YYYY-MM-DD.md 日报
├── assets/              # figures / graphs
└── state/               # pipeline 状态（read_ids, last_run）
```

## 8 大重点跟踪方向

| Topic | 文件 | 关注 |
|---|---|---|
| Formal limits | [topics/formal_limits.md](topics/formal_limits.md) | computability, expressivity, complexity bound |
| Reasoning vs pattern matching | [topics/reasoning.md](topics/reasoning.md) | CoT faithfulness, mech-interp evidence |
| Grounding | [topics/grounding.md](topics/grounding.md) | symbol grounding, multimodal grounding |
| Causality | [topics/causality.md](topics/causality.md) | Pearl hierarchy, intervention |
| Embodiment | [topics/embodiment.md](topics/embodiment.md) | VLA, robotics FM, active perception |
| Online learning | [topics/online_learning.md](topics/online_learning.md) | continual, lifelong, non-stationary |
| World model & planning | [topics/world_model.md](topics/world_model.md) | latent dynamics, model-based RL |
| In-context & scaling limits | [topics/scaling_limits.md](topics/scaling_limits.md) | scaling laws, ICL theory |

## 运行约束 (IP guardrails)

本调研在 **Xander Xu (个人 GitHub: Xander23333)** 名下公开发布。运行 agent 必须严守：

1. **只综合公开发表论文** (arXiv / 会议 / 期刊 / 公开博客)。
2. **不**写入任何作者主职雇主 (Qwen 团队) 内部信息、未发表评测方法、内部数据。
3. **不**对 Qwen 及其直接竞品 (GPT / Claude / Gemini / DeepSeek / Kimi / GLM …) 做产品级评测或主观排名 —— 仅在论文 review 的事实层面引用。
4. **不**写 agentic coding / LLM eval / benchmark 设计层面的原创方法 (那是雇主 IP 边界)。
5. 风格：学术、严谨、不写营销语言。

## 调研方法论

每日由 cron-driven agent 执行 (`state/cron_prompt.md`)：

1. arxiv + Semantic Scholar 新论文扫描 (近 24h + 7d 双窗口)
2. 按 8 大 topic + 关键词预过滤
3. dedup against `state/read_ids.json`
4. 重要论文 → 单篇 paper note (含 NTP 归类)
5. 更新 timeline / taxonomy
6. 生成 `daily_reports/YYYY-MM-DD.md`
7. git commit + push
8. 钉钉日报推送 (≤400 字精炼版)

## 状态

- 启动日: 2026-05-26
- 上次运行: 见 `state/last_run.json`
- 已读论文 ID: 见 `state/read_ids.json`

---

*This is an autonomously-maintained research survey. Daily updates are commit-tagged `[NTP-Daily]`. The human author reviews periodically and prunes / corrects when needed.*
