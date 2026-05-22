# Dreamer 家族与 latent world model for RL（DreamerV1–V3 / IRIS / TWM / STORM）

> **范围**：本节覆盖以 Danijar Hafner 为核心的 **Dreamer 系列**（PlaNet → DreamerV1/V2/V3 → DayDreamer），以及 2022–2025 内出现的 transformer-based latent world model（**IRIS / TWM / STORM / Δ-IRIS** 等），截止 2026-05。和 E1-JEPA 不同：JEPA 是 representation pretraining，Dreamer 路线的 latent world model **从一开始就是为 model-based RL 服务**——learn-a-model + plan-in-latent + actor-critic on imagined rollouts 的三件套。读者 = Qwen agentic 评测 owner，熟 RL 基础（A2C/PPO/SAC、value bootstrap、GAE），不科普 actor-critic。

## 路线定位（1 段）

Dreamer 路线在 2026 frontier 的位置很尴尬但很重要：它是**单一架构、单一超参跨 150+ 任务都 work** 的当下唯一 SOTA model-based RL agent（DreamerV3, [arxiv:2301.04104](https://arxiv.org/abs/2301.04104)），也是 Minecraft 里 from-scratch 拿到钻石的第一个 agent；但它**完全停留在学术 benchmark 圈**——没有任何 production agent / robotics 系统 / LLM-agent 训练 loop 把 DreamerV3 当主架构用。这条路线真正进入主流视野的方式是**间接**的：(1) Sora / Genie / V-JEPA 2 等 "video / world model" 浪潮把 Hafner 2018 PlaNet 的 latent dynamics 思路抬上 keynote； (2) agentic RL 圈（OpenAI o-series、DeepSeek R1、Kimi K1.5 的 RL infra）反复讨论 "要不要做 world model rollouts 来省 env step"，DreamerV3 是这个问题的现成参考实现；(3) IRIS / STORM 这条 **transformer world model + discrete latent + imagination rollout** 的支线，是 2024–2025 学术界对 "如果把 Dreamer 的 RSSM 换成 transformer 会怎样" 的系统性回答，对 Qwen / 其他做 long-horizon agent RL 的团队是直接 relevant 的方法论。

## 代表模型清单

| 模型/事件 | 发布日 | 关键变化 | 一手 source |
|---|---|---|---|
| **PlaNet** | 2018-11 | 第一个 pixel-based latent dynamics + CEM planning；引入 **RSSM**（Recurrent State Space Model，deterministic + stochastic 混合 latent） | [arxiv:1811.04551](https://arxiv.org/abs/1811.04551) |
| **DreamerV1** | 2019-12 | 把 PlaNet 的 planner 换成 **actor-critic learned in imagination**；DMC continuous control SOTA | [arxiv:1912.01603](https://arxiv.org/abs/1912.01603) |
| **DreamerV2** | 2020-10 | latent 改为 **categorical (discrete) latent + straight-through gradient**；Atari200M 上首个超人类平均分的 world model agent | [arxiv:2010.02193](https://arxiv.org/abs/2010.02193) |
| **DayDreamer** | 2022-06 | DreamerV2 直接上真实机器人（四足、机械臂、轮式）做 online learning；展示 world model 的 sample efficiency 在 real robot 上可用 | [arxiv:2206.14176](https://arxiv.org/abs/2206.14176) |
| **DreamerV3** | 2023-01；JMLR/Nature 版 2025 | **同一套超参跨 150+ tasks**；symlog reward/critic、two-hot 分类 critic、free bits、percentile return normalization；**Minecraft from-scratch 拿钻石**（首例） | [arxiv:2301.04104](https://arxiv.org/abs/2301.04104)；[Nature 2025-04 (Hafner et al.)](https://www.nature.com/articles/s41586-025-08744-2) [uncertain DOI；以 nature.com Hafner 2025 为准] |
| **IRIS** | 2022-09 | 第一个把 world model 换成 **discrete autoencoder (VQ) + Transformer dynamics** 的 Atari agent；Atari100k 上 SOTA（媒介人类 1.046） | [arxiv:2209.00588](https://arxiv.org/abs/2209.00588) |
| **TWM (Transformer-based World Model)** | 2022-12 / ICLR 2023 | Atari100k 上 transformer world model + Dreamer-style actor-critic；与 IRIS 同期独立工作 | [arxiv:2202.09481](https://arxiv.org/abs/2202.09481) [uncertain 该 id 对应早期版本，正式 TWM 是 Robine et al. ICLR 2023] |
| **STORM** | 2023-10 | "Stochastic Transformer-based wORld Model"；类似 IRIS 但用 categorical latent + 更轻 transformer；Atari100k 上 0.42→0.55 mean human-normalized | [arxiv:2310.09615](https://arxiv.org/abs/2310.09615) |
| **Δ-IRIS** | 2024-06 | 在 IRIS 基础上引入 **delta token / continuous residual**，Crafter / Atari100k 提升；同组（Vincent Micheli 等） | [arxiv:2406.19320](https://arxiv.org/abs/2406.19320) |
| **DIAMOND** | 2024-05 | 用 **diffusion model** 当 world model 替代 transformer/RSSM，在 Atari100k 上拿到新 SOTA（mean HNS 1.46） | [arxiv:2405.12399](https://arxiv.org/abs/2405.12399) |
| **Genie / Genie 2 / Genie 3** | 2024-02 / 2024-12 / 2025-08 | DeepMind 把 latent-action world model 思路放大到 internet video，输出 playable world model（非 RL agent，但和 Dreamer 同源） | [Genie arxiv:2402.15391](https://arxiv.org/abs/2402.15391)；[Genie 2 blog 2024-12](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/)；[Genie 3 blog 2025-08](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) |
| **PWM / 后 Dreamer 衍生** | 2024–2025 多篇 | sample efficient model-based + offline RL 改进，本节不逐个列 | [unknown — 没有单一权威 survey] |
| 2026-05 状态 | — | **DreamerV3 仍是 single-architecture-many-tasks 的事实 SOTA**；transformer world model 一支以 DIAMOND / Δ-IRIS 为最强 Atari100k 参考；尚无公开 "DreamerV4" 论文 [uncertain — Hafner 2025-下半年 talk 多次预告下一代但未发布] | — |

## 架构核心（按 paper 写的）

### 1. RSSM——Dreamer 路线的共同 backbone（PlaNet → DreamerV3）

Dreamer 系列的 world model 始终是 **Recurrent State Space Model (RSSM)**[^planet]：

```
h_t = f(h_{t-1}, z_{t-1}, a_{t-1})        # deterministic recurrent state (GRU)
z_t ~ q(z_t | h_t, x_t)                    # posterior (encoder), 用真实 obs
ẑ_t ~ p(ẑ_t | h_t)                         # prior (dynamics), 不看 obs
x̂_t ~ p(x̂_t | h_t, z_t)                   # decoder（pixel reconstruction）
r̂_t ~ p(r̂_t | h_t, z_t)                   # reward head
```

训练 loss = recon + reward + KL(q || p)。**KL 项是 dynamics model 的训练信号**——让 prior（不看 obs）逼近 posterior（看 obs）。DreamerV2 之后 `z_t` 改成 **32×32 categorical**（32 个 categorical 变量，每个 32 类），用 straight-through gumbel-softmax 反传梯度[^dv2]——这是 Hafner 反复强调的 trick：**discrete latent 让 multimodal future 比 Gaussian latent 好建模得多**，尤其在 Atari 这种 deterministic-but-branching 环境。

DreamerV3 没有动 RSSM 的结构，但加了一组 **工程化稳定 tricks**[^dv3]：
- **symlog transform** 对 reward / value / observation 做 `sign(x)·log(1+|x|)`；避免不同 task reward scale 差 10^6 倍导致 critic 难训；
- **two-hot encoded critic**：value 不回归标量，回归一个 bucket 分布（类似 C51），符合 symlog 后的 scale；
- **percentile return normalization**：用 returns 的 5%–95% 分位差做 advantage 归一化；
- **free bits**：KL 项每维加 1 nat 下限，防 dynamics collapse；
- **unimix categorical**：posterior/prior 与均匀分布混合 1%，防 KL 爆炸。

paper Table 1 的关键 claim：**所有 task（Atari / DMC / Crafter / Minecraft / ProcGen）共享一套超参**——这是 Dreamer 之前所有 RL 算法（包括 PPO / SAC / Rainbow）做不到的。

### 2. Imagination rollout actor-critic

DreamerV1 起的核心训练循环（在 DreamerV3 完全保留）[^dv1]：

1. 从 replay buffer 采 trajectory，更新 world model（recon + reward + KL）；
2. 从 buffer 起点 latent state 出发，用 prior dynamics **在 latent 空间 rollout 15–16 步**（不与真实 env 交互）；
3. 在 imagined rollout 上算 λ-return，更新 **actor + critic**（critic 是 two-hot 分布，actor 是策略）；
4. actor 用真实 env 跑一步，新 transition 进 buffer。

这个 "imagine in latent" 让 **每条真实 env step 反复利用** 来训 policy——sample efficiency 是同代 model-free（PPO/SAC）的 10–100×。DreamerV3 paper Fig.3 在 Atari200M 比 IMPALA / Rainbow 用 1/10 step 达到同分。

### 3. IRIS / TWM / STORM——把 RSSM 换成 transformer

2022 后的研究主线：**dynamics 改成 transformer，latent 改成 token 序列**[^iris]：

- **encoder** 是 VQ-VAE / discrete autoencoder，把 obs 编成 K 个 token（IRIS：64 tokens / frame，每个 vocab=512）；
- **dynamics** 是 GPT-style decoder-only transformer，序列形如 `[obs_tok_1..K, action, reward, obs_tok'_1..K, action', ...]`，autoregressive 预测下一帧 tokens + reward + termination；
- **actor-critic** 仍在 latent 空间 imagine rollout，方式同 Dreamer。

关键差异：
- **没有 RSSM 那种 deterministic/stochastic split**——transformer 用 attention 显式建 long context（IRIS 上下文 ~20 步，STORM ~16）；
- **替换 GRU 的动机**：long-horizon Atari（Pong/Breakout 没问题，Frostbite/Krull 这种 reward 稀疏 + 长依赖）transformer 更稳；
- **代价**：transformer world model 每步推理慢，imagine rollout throughput 显著低于 RSSM；STORM paper 明列 "训练 wall-clock 仍比 DreamerV3 慢 2–3×"。

DIAMOND ([arxiv:2405.12399](https://arxiv.org/abs/2405.12399)) 走得更远——dynamics 用 **diffusion** 直接在像素空间生成下一帧；优点是视觉细节保留好（"world model 真的像 game"），缺点是 imagine cost 更高。DIAMOND Atari100k 平均 HNS = 1.46，是这条线当前最高分。

## 训练方法核心

- **Pretrain？不存在**：Dreamer/IRIS/STORM 都是 **online RL**——world model 与 policy 同步从 buffer 学，没有 LLM 那种独立 pretrain 阶段。这是 Dreamer 路线和 LLM-agent 路线最大的方法论分歧。
- **唯一例外是 Genie 系列**：Genie 1/2/3 是用 internet video 离线 pretrain 的 latent-action world model，但**没有 agent**——它输出 playable demo，不做 RL。把 Genie 算 Dreamer 家族属于宽泛归类。
- **算力（DreamerV3）**：paper §B 给出 Atari200M 用 **单卡 V100 / A100 训 ~12 天**（每 task），Minecraft Diamond 用 **16 GPU × ~17 天**[^dv3]。和当代 LLM 比是极廉价。
- **算力（IRIS / STORM）**：IRIS Atari100k 每 task **单 V100 7 天**；STORM 同量级。Atari100k 设定是 **100k env step ≈ 2 小时 game time**——重点是 sample efficiency，不是算力。
- **没有 SFT / RLHF / RLVR**：reward 来自 env，不是 human / verifier。

## 与 eval / benchmark 的接口

### 官方报告

- **DreamerV3 主 benchmark**：Atari 200M（55 games）、Atari 100k、DeepMind Control Suite (proprio + visual)、Crafter、Minecraft (MineDojo Diamond)、ProcGen、BSuite、DMLab。**150+ task 同一套超参**是 V3 paper 的标志性 claim。
- **IRIS / TWM / STORM / DIAMOND**：基本只报 **Atari100k**（26 games subset）+ 偶尔 Crafter。这是 sample-efficient RL 的事实标准 benchmark。
- **Crafter** ([arxiv:2109.06780](https://arxiv.org/abs/2109.06780)) 是 Hafner 自己设计的 procgen Minecraft-lite，DreamerV3 和 IRIS-family 都常用。

### Atari100k 历年大概分数（mean human-normalized）

| 方法 | Mean HNS | source |
|---|---|---|
| EfficientZero (2021) | 1.94 | [arxiv:2111.00210](https://arxiv.org/abs/2111.00210) |
| IRIS (2022) | 1.046 | IRIS paper |
| TWM (2023) | 0.96 | TWM paper |
| DreamerV3 (2023) | 1.12 | DV3 paper Table |
| STORM (2023) | 1.27 | STORM paper |
| Δ-IRIS (2024) | 1.25 | Δ-IRIS paper |
| **DIAMOND (2024)** | **1.46** | DIAMOND paper |

注：EfficientZero（MuZero 变体）历史 HNS 数字最高但**不是 single-architecture-many-tasks**，且复现成本极高；这是 Hafner 反复在 talk 里区分的点——"高分但脆弱" vs "全 task 都 work"。

### 第三方复现 / 质疑

- DreamerV3 在社区 (clean-rl style) **有多个独立复现**，主要的 caveat 是 Minecraft Diamond 的 success rate 高度 variance——原 paper 报 50 seed 平均 successful in ~30%，社区复现 number 略低。
- **Crafter score** 在 Dreamer paper 与第三方 (Plan2Explore / Director) 之间偶有 small disagreement，但量级一致。
- IRIS / STORM 复现门槛高（transformer world model 训练不稳），github 上 unofficial pytorch reimpl 偶有 OOM / NaN 报告 [uncertain 具体 issue]。

### 已知 contamination / overfit 信号

- Atari100k 是 fixed 26-game subset，**超参 tune on this subset 后的过拟合** 是公开秘密——MuZero / EfficientZero / DreamerV3 都被怀疑做过此事；最干净的方式是看 DreamerV3 的 **Atari200M (全 55 games)** 数字。
- Hafner 在 ICML 2023 talk ([youtube](https://www.youtube.com/watch?v=vfpZu0R1s1Y) [uncertain 具体 URL]) 公开强调："V3 的 superhuman 是不调参的——我们就跑了一次"，这个 claim 至今没有被反例打破。

## 未知与争议

1. **DreamerV4 / Hafner 下一代**：2024–2025 Hafner 多次 talk（NeurIPS、Google DeepMind retreat）提 "next-gen 会引入 transformer dynamics + scale"，但**截至 2026-05 没有公开 paper / weight** [uncertain]。
2. **是否会和 LLM-agent / agentic RL 融合**：Hafner 2024 起任 DeepMind research scientist，外界普遍猜测 Dreamer 思路会被纳入 Gemini agent / Genie 后续；但 Genie 3 paper 没有 actor-critic component，**两条路线在 DeepMind 内未公开融合**。
3. **真实机器人**：DayDreamer 2022 的真机 demo 之后，**DreamerV3 没有公开的 real-robot 后续**——所有 Dreamer 系 robotics 论文都停留在 sim。π0 / Gemini Robotics / GR00T 这类 VLA 路线**完全没采用** Dreamer 风格 latent world model。
4. **Discrete latent vs continuous latent 之争**：DreamerV2 论证 categorical latent 优于 Gaussian；但 DIAMOND 的 diffusion-in-pixel 路线又把 "continuous + 高维" 路线带回 SOTA。**正确的 latent 设计还没收敛**。
5. **LLM scale 上的 Dreamer**：没有人公开做过 "DreamerV3 dynamics 模型放大到 1B+ 参数" 的实验。原因可能是（a）online RL 在 1B+ 模型上 wall-clock 不现实；（b）world model 没有 obvious 的 internet-scale pretrain corpus（Genie 是个尝试但没接 RL）。
6. **JMLR/Nature 版 DreamerV3 (2025)**：paper Nature 转 publish 后是否有实质内容更新 [uncertain — 多数复述 arxiv，但附录扩了一些 ablation]。

主要争议：

- **"world model rollout 在 agentic LLM RL 里有用吗？"** —— 这是 2025 圈内最活跃的 open question。o1 / R1 / Kimi K1.5 都没用 world model（纯 model-free RLVR on real verifier），但 (a) verifier 是 expensive，(b) 多轮 tool-use 的真实 env step 也 expensive，理论上 imagine rollout 能省。**截至 2026-05 没有公开 frontier LLM agent 用 Dreamer-style world model 训练**。这是一个"理论 attractive、工程未兑现"的状态。
- **"single-architecture-many-tasks" 真有意义吗？** —— DreamerV3 的 150 task 同超参很 impressive，但每个 task 仍然是 **从零 online 训练**——不是 zero-shot generalization，不是 in-context adaptation。和当代 LLM-agent 那种 "一个 model 解很多 task" 是完全不同的 generality。

## 与 JEPA / Genie / LLM-agent 的快速对照

| 维度 | Dreamer 家族 | JEPA (E1) | Genie 系列 | LLM agent + RLVR |
|---|---|---|---|---|
| world model 用途 | imagine rollout 训 policy | representation pretraining | playable demo 生成 | **不显式建** |
| latent 类型 | RSSM categorical / VQ tokens / diffusion | EMA feature (cosine target) | latent action + token frames | text token |
| 有 actor / policy | **有**（actor-critic in latent） | 否（V-JEPA 2-AC 是补丁） | 否 | LLM 自己当 policy |
| pretrain corpus | 无（pure online RL） | internet image/video | internet video | internet text + code |
| sample efficiency | **高**（Atari100k 是主战场） | N/A | N/A | 低（需大量 RLVR step） |
| production 采纳 | 几乎零 | 几乎零 | 接近零（demo 性质） | **frontier 主流** |

**核心 takeaway for Qwen eval lead**：

1. **Dreamer 不是给 Qwen 当下 frontier model 用的工具**——它的 sweet spot 是 sample-efficient online RL on small env，和你们做的 agentic coding RL 训练 loop 没有直接接口。
2. 但 DreamerV3 的几个 **engineering trick 值得 borrow**：symlog transform、two-hot critic、percentile return normalization——这些在 LLM agent RLVR critic 训练里（如果你们用 value model）是 first-principles 改进。Hafner 反复强调"这些不是 RL trick，是 deep learning hygiene"。
3. **transformer world model（IRIS/STORM/DIAMOND）值得放进 "未来一年要追的 paper" 清单**——如果 agentic RL 走到 multi-step tool use 成本不可接受、需要 imagined rollout 的那一天，这条线就是现成参考。
4. **Crafter / Minecraft Diamond / Atari100k 是 RL 圈的 "MMLU"**——做 eval 设计时知道它们的限制就够了，不需要追求在上面拿分。
5. Dreamer / JEPA / Genie 三条 "world model" 路线 **在 2026-05 仍未合流**，谁先把 world model 接进 frontier LLM agent 训练 loop 谁就拿到下一个 sample efficiency × generality 的红利——这是这条 narrative 最值得关注的赌注。

## 推荐外部材料

- [DreamerV3 paper, arxiv:2301.04104](https://arxiv.org/abs/2301.04104) — 该家族最重要的一篇，§B 工程 trick 列得最全，要把 symlog/two-hot/percentile 读懂。
- [Danijar Hafner 个人主页](https://danijar.com/) — Dreamer 全系列 paper / code / talk 一站式，他自己整理。
- [Hafner ICLR 2024 invited talk "Mastering Diverse Domains through World Models"](https://www.youtube.com/results?search_query=hafner+iclr+2024+dreamerv3) [uncertain 具体 URL] — DreamerV3 的最佳口述版本。
- [IRIS paper, arxiv:2209.00588](https://arxiv.org/abs/2209.00588) — transformer world model 入门最干净的 reference。
- [DIAMOND paper, arxiv:2405.12399](https://arxiv.org/abs/2405.12399) — 把 world model 路线和 diffusion 桥接，2024 最有意思的一篇。
- [Sergey Levine, "Deep RL Bootcamp / CS285" model-based 章节](https://rail.eecs.berkeley.edu/deeprlcourse/) — 把 PlaNet/Dreamer 放进 MBRL 大图里讲，是最系统的 lecture。
- [Lilian Weng, "World Models" blog (2018, 仍是 baseline reference)](https://lilianweng.github.io/posts/2018-06-23-model/) — Schmidhuber/Ha world model 之后到 PlaNet 的连续脉络。
- [Genie 3 blog (DeepMind 2025-08)](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) — Dreamer-adjacent 路线在大规模 video pretrain 上的另一个端点，对比读有助理解"world model"这个词在 2025–26 的多义性。

---

[^planet]: Hafner et al., "Learning Latent Dynamics for Planning from Pixels" (PlaNet), arxiv:1811.04551, 2018-11；§3 定义 RSSM 的 deterministic GRU + stochastic latent 混合结构。
[^dv1]: Hafner et al., "Dream to Control" (DreamerV1), arxiv:1912.01603, 2019-12；§3 imagination rollout actor-critic。
[^dv2]: Hafner et al., "Mastering Atari with Discrete World Models" (DreamerV2), arxiv:2010.02193, 2020-10；§3.1 categorical latent + straight-through gradient。
[^dv3]: Hafner et al., "Mastering Diverse Domains through World Models" (DreamerV3), arxiv:2301.04104, 2023-01；§3-4 列 symlog / two-hot / percentile / free bits / unimix 全部工程 trick；§5 跨 150+ task 同超参实验。
[^iris]: Micheli, Alonso, Fleuret, "Transformers are Sample-Efficient World Models" (IRIS), arxiv:2209.00588, 2022-09；§3 定义 discrete autoencoder + GPT-style dynamics。
