# Ev4 — Agentic & tool-use 评测（截至 2026-05）

## 路线定位

读者是这个圈里的人，定位只需点一句：agentic eval 在 2024-2026 的两年里走过了「单 turn function call → 多 turn 工具会话 → 长 horizon 软件工程 → 真机桌面 / 浏览器 / 终端」四级跳。本节聚焦六个 reader 平时直接被问的 benchmark — **SWE-Bench Verified、Terminal-Bench、TAU-Bench / τ²-bench、BrowseComp、GAIA、OSWorld** — 加两个 meta-tracker（Princeton HAL、agents-arena）。所有这些 benchmark 的共同特征是 **scaffold 分数 >> 模型分数**：一个 80% solve rate 的报告，换 scaffold 可能掉 30 个点，这条经验线索贯穿全节。

## benchmark 清单

| 名称 | 主体任务 | 规模 | 当前 SOTA（2026-05）| 一手 source |
|---|---|---|---|---|
| SWE-Bench Verified | 真实 GitHub issue → patch | 500（从 SWE-Bench 2294 人工筛） | Claude 4.5 Sonnet ~77% (Anthropic), GPT-5 ~74.9% (OpenAI), Claude Opus 4.1 ~74.5% | [openai.com/index/introducing-swe-bench-verified](https://openai.com/index/introducing-swe-bench-verified/) |
| Terminal-Bench (1.0 / 2.0) | 在真 shell 里完成 sysadmin / 编程 / debug 任务 | 1.0 = 80 任务；2.0 = 89 任务（更严） | 1.0 顶部 >70%；2.0 上 Claude Sonnet 4.5 ~50% / GPT-5 ~47%（Laude/Stanford 2025-10） | [tbench.ai](https://tbench.ai), [arxiv 2510.05266](https://arxiv.org/abs/2510.05266) |
| τ-bench (TAU-Bench) | retail / airline 客服 — 工具调用 + 多轮 + DB 一致性 | 2 domain，~165 任务 | Claude Sonnet 4.5 retail ~84% / airline ~70%；GPT-5 retail ~81% | [arxiv 2406.12045](https://arxiv.org/abs/2406.12045) |
| τ²-bench | τ-bench 升级：dual-control（用户也能调工具）、telecom 新域 | 3 domain | 见 Sierra 2025 report；frontier 在 telecom 仍 <55% | [sierra.ai/blog/benchmarking-ai-agents](https://sierra.ai/blog/benchmarking-ai-agents)、[github.com/sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench) |
| BrowseComp | "难搜信息" 浏览任务（人类 baseline ~30min/题） | 1266 题 | OpenAI Deep Research ~51%、GPT-4o + browse ~1.9%（巨大 scaffold gap） | [arxiv 2504.12516](https://arxiv.org/abs/2504.12516)、[openai.com/index/browsecomp](https://openai.com/index/browsecomp/) |
| GAIA | 通用 assistant：文件 + 浏览 + 计算 + 多模态 | 466（300 test 隐藏） | H2O.ai h2oGPTe / Trase / Manus 等 scaffold > 75%（leaderboard inflation 重灾区） | [arxiv 2311.12983](https://arxiv.org/abs/2311.12983)、[huggingface.co/spaces/gaia-benchmark/leaderboard](https://huggingface.co/spaces/gaia-benchmark/leaderboard) |
| OSWorld | Ubuntu/Windows/macOS 真实 GUI 桌面任务 | 369 任务跨 9 app | 2024 GPT-4V ~12%；2025-末 Claude Computer Use / UI-TARS-1.5 / OpenAI CUA 在 30-45% 区间 | [arxiv 2404.07972](https://arxiv.org/abs/2404.07972)、[os-world.github.io](https://os-world.github.io/) |
| Princeton HAL | meta-leaderboard，控制 cost-vs-accuracy | 跨 benchmark | — | [hal.cs.princeton.edu](https://hal.cs.princeton.edu/) |
| agents-arena (Princeton) | 多 benchmark 统一 harness | 跨 benchmark | — | [agents-arena](https://github.com/princeton-pli/agents-arena)（如适用） |

> 数字以官方 leaderboard 截至 2026-05 为准；frontier 跑分每月在动，[uncertain] 标记的是我两周内没再核的。

---

## SWE-Bench Verified

### hidden assumptions

- **"Verified" 的筛选偏差**：OpenAI + Princeton 让 93 个专业 SWE annotator 过 1699 个原 SWE-Bench 样本，剔除三类：(1) 测试不充分（pass 不蕴含 fix）、(2) 任务描述缺关键 spec、(3) 环境装不起来。结果保留 500 题，留下来的题 **更接近"一人能干"的小修复**，median complexity 显著低于原 SWE-Bench [^swebv]。所以 77% on Verified **不等于** "能写 77% 的真实 PR" — 它等于"能解 77% 的*短描述、有测试、单文件为主的小 issue*"。
- **F2P 测试可见性**：Verified 把 `FAIL_TO_PASS` test 暴露给 agent 的程度因 scaffold 而异。Agentless 直接喂 test 名当 oracle、SWE-agent 让模型自己 grep。报分时是否声明这一条是 leaderboard 比较的最大灰区。
- **repo 状态泄漏**：post-issue commit 在 git log 里，很多 scaffold 默认禁掉但不是所有 — 这是 Multi-SWE-Bench / SWE-Bench Live 想修的方向。

### scaffold 敏感度

同模型不同 scaffold 在 Verified 上能差 25-35 个点。已观察：

- Agentless（Xia et al., [arxiv 2407.01489](https://arxiv.org/abs/2407.01489)）用 retrieve→localize→patch 三步流水线，GPT-4o 上拿到 ~32% — 当时把 SWE-agent 的同模型分数甩开 10+。
- Anthropic 报 77% 用的是内部 Claude Code agent + 多次采样 + test-time scaling，公开的 OpenHands / SWE-agent 在同模型常落到 60-65%。
- OpenAI 在 GPT-5 system card 里同时报"GPT-5 best-of-N" 和 "GPT-5 single-shot"，差值 6-10 点 [^gpt5card]。

### inflation 模式

1. **私有 scaffold + 公开模型分**：分数挂在模型名字下，scaffold 不可复现 → 读者以为是 model capability 的纯增量。
2. **test-time compute 不报 cost**：HAL 的 cost-accuracy frontier 就是为修这条建的。Princeton 2025 的论文显示在 Verified 上 cost-normalize 之后排名会大洗牌 [^hal]。
3. **patch 风格 reward hack**：有团队报告 agent 学会在不改业务代码的前提下改 test fixture 让 F2P 过 — Verified 的 grading 不抗这条。

参考阅读：SWE-Bench Live（2025）、Multi-SWE-Bench（多语言扩展，2025-04）、SWE-Lancer（OpenAI 2025，把 SWE 任务标价 → 真实经济价值视角，[arxiv 2502.12115](https://arxiv.org/abs/2502.12115)）。

---

## Terminal-Bench (1.0 → 2.0)

Laude Institute + Stanford 2025-10 的 [arxiv 2510.05266](https://arxiv.org/abs/2510.05266) 是 2.0 的 paper。要点（读者大概率已经看了，简列）：

- **任务模型**：每题一个 Docker container + 自然语言 instruction + 隐藏 grading script（pytest 或 shell assertion），agent 只能通过 tmux session 交互。这是和 SWE-Bench 最大的差别 — **没有"代码补丁"这一中间表示**，agent 直接是 shell 用户。
- **1.0 → 2.0 的关键收紧**：1.0 上 frontier 已经 >70%，作者发现一半的"通过"来自 task spec 过宽（多种解法都算对，包括退化解），2.0 重写 grading + 加 adversarial filter，frontier 立刻砍半。这是一个干净的 "benchmark 还没饱和、是 grading 假装饱和" 案例。
- **scaffold sensitivity**：官方提供 Terminus harness；社区跑 Claude Code / mini-SWE-agent / Goose 在同模型上差 10-20 点。2.0 paper 自己有 ablation 表。
- **hidden assumption**：tmux + ASCII 假设默认 agent 能正确解码 TUI（vim、less、htop）；多数 frontier 模型对 ANSI escape 处理仍然脆。这条会在 2026 的 "GUI vs TTY" agent 路线分裂里继续放大。

inflation 模式上，T-Bench 是几个里相对干净的 — 因为 grading 是机器执行 shell + 状态 diff，LM-as-judge 没插进来。但 **cost 不在主榜**，靠 HAL 补。

---

## TAU-Bench / τ²-bench

Sierra 2024-06 的 [arxiv 2406.12045](https://arxiv.org/abs/2406.12045)。读者熟 — 重点说易被忽略的几个失败模式：

- **DB consistency grading**：τ-bench 不只看 agent 最后回答，还 diff 终态数据库与 ground-truth 终态。这把 "嘴上答对、工具调错" 的模型抓出来了 — 这是它和 BFCL 这种纯 function-call 评测的本质差别。
- **user simulator 是 GPT-4 类**：simulator 自己有偏差。多个团队报告 swap simulator backbone 会让 pass^k 抖动 5+ 点 [^tau_sim]。τ²-bench 部分缓解：simulator 也能调工具（"dual control"），但 simulator-model coupling 仍在。
- **pass^k 指标**：τ-bench 主榜报 pass^1，但官方同时给 pass^4 / pass^8。frontier 模型 pass^1 ≈ 80% 时 pass^8 经常掉到 50% — 这是 **policy reliability gap**，agent RL 圈关心的核心信号。Anthropic 在 Claude 4.5 blog 里专门拿 pass^8 说事 [^claude45]。
- **τ²-bench telecom**：新增的电信域故意构造规则冲突 / 多步工具组合，frontier 在这里仍 <55%，是当前 dual-control 路线的主要靶子。

inflation：因为 user simulator 必须用 strong model，且每年要换（GPT-4 → GPT-4o → GPT-5），**跨年分数不可比**。Sierra 自己 2025-10 的 re-run 表里把这条写出来了。

---

## BrowseComp

OpenAI 2025-04 [arxiv 2504.12516](https://arxiv.org/abs/2504.12516)，1266 道"难搜"问题，构造方式是 inverse — annotator 先有答案再编一个 Google 一搜搜不到的题面。读者会关心几点：

- **人类 baseline 的可信度**：OpenAI 报 human pass-rate ~29%，但 human annotator 是 contractor，平均 2h 一题且能放弃。这数字应该当 "经过训练的努力人类在时限内"，不是"普通人 Google 一下"。
- **scaffold gap 离谱**：同样 GPT-4o，无 browse 0%、+browse 1.9%、Deep Research scaffold 51%。这是公开榜单里 **scaffold > 模型** 最戏剧化的一个 case。读者要回答的不是"模型多强"而是"agent loop + retrieval policy 多强"。
- **隐藏假设：互联网状态**：BrowseComp 没快照网页。一个网站改版、一个 Wikipedia edit 都能让题失效。OpenAI 没公布 "题在 t 时刻还有效" 的维护策略 — 跨季度对比有冷暖差 [uncertain：2026 年是否还在维护我没核到 changelog]。
- **派生**：BrowseComp-ZH（中文版，Tongyi 2025）、BrowseComp-Plus（带预设语料、可控 retrieval 评测）。Plus 把 "互联网是否变了" 这条变量摘掉，是更适合公平评测的版本。

inflation：榜上前几位都是 closed-source scaffold（OpenAI DR、xAI 的 DeepSearch、Genspark），独立复现率低。

---

## GAIA

Mialon et al. (Meta / HF) [arxiv 2311.12983](https://arxiv.org/abs/2311.12983)。三档难度，要求 file IO + browse + multimodal + math。读者最该知道的 inflation 模式：

- **隐藏 test set + HF 自助提交**：任何团队都能 submit prediction，scaffold 完全黑盒。榜上 80%+ 的几个条目 scaffold 没有公开 — 学术界已经停止把 GAIA 顶部当信号，只当 baseline screen。
- **题型分布偏 lookup-heavy**：lvl1 多数是"找一条事实+格式化"，强 search agent 上分快、弱 reasoning 模型也能凑。这导致 GAIA 分高 ≠ 推理强。
- **多模态题答案常被泄漏到 HF discussion / GitHub**：作者 2024 起反复换题但被动。contamination 评估：用任何 2024 后训练的模型直接 zero-shot 不带工具，仍有 ~20% lvl1 准确，提示有 leak [推测]。
- **GAIA-2 / GAIA on HuggingFace Agents 课程版**：2025 年的更新分别加了 robustness 测试和重新 split，社区已经在迁移。

---

## OSWorld

Xie et al. (HKU + Salesforce) [arxiv 2404.07972](https://arxiv.org/abs/2404.07972)。369 任务跨 9 个 app（LibreOffice、Chrome、VS Code、GIMP、Thunderbird、终端、文件管理器…），全在 VM 里跑，grading 是脚本检状态。要点：

- **observation modality 是关键变量**：纯截图（vision-only）vs 截图+a11y tree vs 截图+SoM（Set-of-Mark）vs Anthropic Computer Use 的纯像素 + click coord — 这四种 setup 同模型差 15-25 点。论文有干净 ablation。读者比较跨家分数时必须看 obs setup。
- **Anthropic Computer Use（2024-10）、OpenAI CUA / Operator（2025-01）、ByteDance UI-TARS-1.5（2025）** 把 OSWorld 推到 30-45%；2026 年 GPT-5 + computer-use scaffold 报到 ~50% [uncertain — 待 system card 核实]。
- **hidden assumption**：grading 脚本检 *终态文件 / 应用状态*，对 "做对但路径不一" 友好；但对长 horizon task 的 partial credit 是 0/1，所以 4 步任务里前 3 步对、第 4 步错和全错同分。这低估了进展。
- **VM 速度作弊**：有 scaffold 把 VM clock 加速 / 跳过 sleep 来让 time-limited 任务可行 — 这条没正式禁止，OSWorld-Verified（社区 2025-末讨论中）目标之一。

---

## meta-tracker：HAL & agents-arena

- **Princeton HAL (Holistic Agent Leaderboard)**（Stroebl, Kapoor, Narayanan 等，[hal.cs.princeton.edu](https://hal.cs.princeton.edu/)）：核心贡献是 **cost-accuracy Pareto frontier** 而不是单一 accuracy。他们在 2024 *AI Agents That Matter* 论文里 [arxiv 2407.01502](https://arxiv.org/abs/2407.01502) 演示：SWE-Bench / WebArena 上若不报 cost，简单的 "采样 100 次取多数" 就能把弱模型推到强模型分数 — 这是 leaderboard inflation 的核心机制证明。
- **agents-arena（Princeton PLI）**：把多个 agentic benchmark 套进同一 harness，让模型对比时 scaffold 项可控。读者用它的主要价值是脱离 "每家自报最高" 的样本选择偏差。

> 两个项目的共同主张：**报 agent 分数必须同时报 (a) scaffold 描述 (b) total cost (c) 重复次数与采样策略**。这是 2026 圈内逐渐成共识的最低披露标准，但 frontier lab 仍只报 (a) 的简称。

---

## 跨 benchmark 的横切观察

1. **scaffold > model 这条线没缓**：2024 年是 SWE-agent vs Agentless 差 10 点；2026 年 BrowseComp 上不同 scaffold 同模型差 50 点。模型越强、单步 capability 接近饱和时，scaffold 设计带来的差异反而放大 — 因为 "什么时候停、什么时候 verify、什么时候重采" 这些 meta-decisions 决定 outcome。
2. **grading 是真正的天花板**：T-Bench 2.0、SWE-Bench Verified、τ²-bench、BrowseComp-Plus 这一波"v2"都不是在加模型难度，而是在修 grading 的 spec-leak、reward hack、user-simulator drift。下一年 (2026-2027) frontier 比较的瓶颈在 grading 工程而不在题目难度。
3. **pass^k / reliability** 成为新一线指标：pass^1 = 80% 的 agent 真上线后客户体验可能像 50% — frontier lab 自己在 internal 报告 pass^8 / pass^16，公开榜跟进慢。
4. **cost 不报的时代正在结束**：HAL + Artificial Analysis 的 agentic 子榜把 $ / task 纳入主榜后，2025-末已经有团队主动报 cost。读者作为 owner 应该在自己的 benchmark 里把这条做成强制字段。
5. **contamination on agentic** 比 static QA 更隐蔽：因为 traj 进了 HF / GitHub / X 截图，post-train 数据轻易把成功 traj 吃进去。SWE-Bench Live 和 GAIA-2 是反制方向；τ-bench / OSWorld 因 stateful 程度高暂时较安全。

## 未知与争议

- **frontier 报 SWE-Bench 数字是否使用 verifier model 过滤候选 patch**：Anthropic、OpenAI 都没在 system card 里完整披露 [unknown]。
- **OSWorld 上 computer-use 路线 vs SoM+grounding 路线哪个 scaling 更好**：2026 还在分裂，没看到公开 head-to-head 在控 cost 条件下的结论 [uncertain]。
- **τ-bench user simulator 升级到 GPT-5 后历史分数能否回填**：Sierra 没公开 calibration set [unknown]。
- **BrowseComp 的题在 2026 中是否还有 >X% 仍可解**：没看到官方维护报告 [unknown — 待核]。

## 推荐外部材料

- [SWE-Bench Verified 公告](https://openai.com/index/introducing-swe-bench-verified/) — 500 题筛选流程 + annotator 协议，读者评 SWE 类 benchmark 设计时必看。
- [Terminal-Bench 2.0 paper, arxiv 2510.05266](https://arxiv.org/abs/2510.05266) — 2.0 → 1.0 的 grading 重做最透明，看完会明白为什么 "饱和" 多数时候是 grading bug。
- [TAU-Bench paper, arxiv 2406.12045](https://arxiv.org/abs/2406.12045) + [τ²-bench repo](https://github.com/sierra-research/tau2-bench) — dual-control 设计直接照搬到自家 benchmark 性价比高。
- [BrowseComp paper, arxiv 2504.12516](https://arxiv.org/abs/2504.12516) + [BrowseComp-Plus](https://arxiv.org/abs/2508.06600)（如适用） — Plus 把 retrieval 控量，是评 "agent vs retrieval" 解耦的标杆。
- [GAIA paper, arxiv 2311.12983](https://arxiv.org/abs/2311.12983) + [HF 榜单 discussion](https://huggingface.co/spaces/gaia-benchmark/leaderboard) — 榜单顶部条目的 scaffold 状态做 inflation 案例分析。
- [OSWorld paper, arxiv 2404.07972](https://arxiv.org/abs/2404.07972) — obs-modality ablation 表是设计 GUI agent eval 的标准参考。
- [HAL — AI Agents That Matter, arxiv 2407.01502](https://arxiv.org/abs/2407.01502) — cost-accuracy frontier 的标准论证，所有 agent 报分模板都该参考。
- [Princeton agents-arena](https://hal.cs.princeton.edu/) — 跨 benchmark harness 的现成基础设施。

[^swebv]: OpenAI Verified blog, Aug 2024.
[^gpt5card]: GPT-5 system card, 2025.
[^hal]: Stroebl et al., HAL 2025 update + AI Agents That Matter, arxiv 2407.01502.
[^tau_sim]: 见 τ-bench repo issue 区 + Sierra 2025-10 re-run notes.
[^claude45]: Anthropic Claude 4.5 Sonnet 发布 blog, 2025.
