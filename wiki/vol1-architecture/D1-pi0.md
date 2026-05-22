# Physical Intelligence π-series（π0 / π0-FAST / π0.5 / π0.6）

> **范围**：本节覆盖 Physical Intelligence (PI) 自 2024-10 首次公开 π0 起，到 2026-05 的所有公开模型线。重点是 **flow-matching action expert + 预训练 VLM** 这一架构范式，跨 embodiment 训练策略，以及 π0.5 引入的 open-world 泛化和 π0.6 / RECAP 的 RL post-train。读者 = Qwen agentic 评测 owner，熟悉 VLM、diffusion / flow matching、RLHF；本节不解释 flow matching 基础，只讲 PI 怎么用。

## 路线定位（1 段）

Physical Intelligence（2024 年 Karol Hausman + Sergey Levine + Chelsea Finn + Brian Ichter 等创立）是当下 generalist robot policy 赛道里**第一个把 \"VLM + flow-matching action head\" 完整跑通并开权重**的公司。π-series 是 Figure Helix、Google DeepMind Gemini Robotics、NVIDIA GR00T 同代的直接对照对象，但与 Figure 的全闭源 demo-only 路线相反，PI **每代都出 paper + 同期开 base 权重到 HuggingFace `lerobot`**[^lerobot-pi0]，是这一波 VLA 里学术可引用性最高的一家。差异化卖点：(1) **flow-matching action expert** 而非 RT-2 风格的离散 action token；(2) 单一权重跨 **8+ embodiment**（双臂、单臂、移动底座、双手灵巧手）；(3) π0.5 系统性研究 **co-training with web data → open-world 泛化**；(4) π0.6 / RECAP 把 RL 加进 post-train 闭环。

## 代表发布清单

| 模型/事件 | 发布日 | 关键变化 | 一手 source |
|---|---|---|---|
| PI 公司成立 / 首轮融资 | 2024-03 | Hausman + Levine + Finn + Ichter，$70M seed | [TechCrunch 2024-03-13](https://techcrunch.com/2024/03/13/physical-intelligence-is-building-foundation-models-for-robots/) |
| **π0** | 2024-10-31 | VLM(PaliGemma-3B) + 300M flow-matching action expert；跨 7 种机器人 + 68 任务 | [arxiv:2410.24164](https://arxiv.org/abs/2410.24164)；[PI blog](https://www.physicalintelligence.company/blog/pi0) |
| π0 权重开源 | 2025-02 [uncertain 精确日] | base + finetuned checkpoints 上 HF；集成进 `lerobot` | [HF lerobot/pi0](https://huggingface.co/lerobot/pi0)；[lerobot PR](https://github.com/huggingface/lerobot) |
| **π0-FAST** | 2025-01-16 | 用 DCT + BPE 把连续动作压成离散 token，autoregressive 训练 5× 提速，质量持平 flow-matching π0 | [arxiv:2501.09747](https://arxiv.org/abs/2501.09747)；[PI blog](https://www.physicalintelligence.company/research/fast) |
| Series B | 2025-04 | $400M @ $2.4B valuation（Bezos / Thrive / Lux） | [Bloomberg 2024-11 / 2025-04 reports](https://www.bloomberg.com/) [uncertain 链接] |
| **π0.5** | 2025-04-22 | knowledge insulation + heterogeneous co-training（web VQA + cross-embodiment + verbal command）→ **open-world 泛化到全新家庭** | [arxiv:2504.16054](https://arxiv.org/abs/2504.16054)；[PI blog](https://www.physicalintelligence.company/blog/pi05) |
| π0.5 + KI 后续 | 2025 年中 | \"Knowledge Insulation\" 单独写为方法 paper，讨论 discrete token loss 不污染 VLM | [PI 2025 follow-up arxiv] [uncertain 链接] |
| **π0.6 / RECAP** | 2025-11 [uncertain 月份, 已发布 blog] | Recap = RL + advantage-conditioned policy，从 π0.5 base 做 on-robot RL post-train；用于咖啡店、装配等真实部署 | [PI blog \"RECAP\" 2025-11](https://www.physicalintelligence.company/blog/recap) [uncertain 链接 slug]；[uncertain 是否已挂 arxiv] |
| 2026-05 状态 | 2026-05 | π0 / π0-FAST / π0.5 base 权重持续开放；π0.6 base 权重 [unknown — 没找到一手 source 证实是否开源] | — |

## 架构核心（按 paper 写的）

### 1. π0：VLM backbone + flow-matching action expert

π0 paper [arxiv:2410.24164](https://arxiv.org/abs/2410.24164) 第 3 节明确：

- **Backbone = PaliGemma-3B**[^pi0-paper]：Google 开源的 SigLIP vision encoder + Gemma-2B 语言塔（合计 ~3B）。PI 选 PaliGemma 而不是更大模型的原因是**推理延迟**——机器人需要 50 Hz 级别 action chunk。
- **Action expert = 300M transformer**，与 backbone **共享 attention**（mixture-of-experts 式：image/text token 走 VLM 权重，action / robot-state token 走 action expert 权重，但在同一个 attention 里互相 attend）。这是 paper 里反复强调的 \"separate expert, shared attention\" 设计——和 RT-2 的 \"动作即文本 token\" 路线**根本不同**。
- **Flow matching head**：action expert 不直接 regress 动作，而是学一个 conditional vector field $v_\theta(A^\tau_t, o_t)$，从噪声 $A^0 \sim \mathcal{N}(0,I)$ 沿 ODE 积分到动作 chunk $A^1$。预测的是 **action chunk**（H=50 步，对应 1 秒 @ 50 Hz），不是单步。flow matching 相对 diffusion 的好处：**few-step 推理**（paper 报 10 步 Euler 就够），latency 友好。
- **输入**：多视角 RGB（1-3 个 cam）+ 当前 robot state（proprioception，连续向量）+ 自然语言指令。Robot state 和 action chunk 都做了**dataset-specific 归一化**（不同机器人 DoF 数不同，用 padding + mask 统一到最大维度）。
- **输出维度**：最多 **18 DoF**（覆盖到双臂 + gripper；π0.5 / 后续扩展到双手灵巧手要再加维度）。

### 2. 跨 embodiment 训练

π0 paper 表 1 列出训练数据：

- **OXE (Open X-Embodiment)** ~ 主体；
- **PI 自采** 跨 7 种机器人平台、68 个任务、~10,000 小时遥操作（数量级，paper 给的是 \"the largest robot interaction dataset to date\" 当时）；
- 平台包含：UR5、Franka、bimanual ARX、bimanual Trossen、mobile Trossen、mobile Fibocom、ALOHA。
- 训练时**所有 embodiment 混在一个 batch 里**，靠 padding + mask 解决 DoF 异质。
- 这是 π0 区别于同期 OpenVLA / RT-2 的关键：单一权重 → 多机器人 zero-shot 或 minimal-finetune 可用。

### 3. π0-FAST：把动作离散化回 autoregressive

[arxiv:2501.09747](https://arxiv.org/abs/2501.09747) 是 π0 的姐妹工作，主张：

- 对 action chunk 先做 **DCT (Discrete Cosine Transform)**，把高频分量压扁；
- 再用 **BPE** 在 DCT 系数上学一个 1024-token 词表（\"FAST tokenizer\"）；
- 然后把这些 token **直接接到 PaliGemma 的 LM head** 做 autoregressive next-token prediction。
- 训练速度**比 flow-matching π0 快 5×**（autoregressive loss 比 flow matching iterative inference 在 training-time throughput 上有优势），real-world success rate 与 π0 基本持平。
- 结论：**离散 vs 连续 action representation 在性能上不是瓶颈**，FAST tokenizer 让 VLA 训练能复用纯 LM 基础设施（DeepSpeed / FSDP / 现成 tokenizer pipeline）。
- 这个 tokenizer 已上 HF（[`physical-intelligence/fast`](https://huggingface.co/physical-intelligence/fast)）并被 OpenVLA-OFT、Gemini Robotics 第二版等多个项目复用。

### 4. π0.5：knowledge insulation + open-world

[arxiv:2504.16054](https://arxiv.org/abs/2504.16054) 是 π0 真正\"破圈\"的论文——它第一次让 VLA 在**完全没见过的家庭**里做家务（折衣服、整理厨房）有可量化的成功率。架构 / 训练改动：

- **Heterogeneous co-training**：训练数据 mixture 同时包含：
  1. PI 自采机器人 trajectory（如 π0）；
  2. **Web VQA / image-caption 数据**（保住 VLM 的视觉-语言泛化）；
  3. **\"verbal commands\" 数据**——人用语言 narrate 机器人下一步要做什么，作为 high-level subtask 监督；
  4. **跨 embodiment** + 多种相机配置。
- **Knowledge Insulation**：核心 trick 是**让 action 相关的 loss 不回传到 VLM backbone 的某些层**（或用极小学习率），防止机器人数据 over-fit 把 VLM 的 web 知识 \"擦掉\"。paper 用 ablation 证明：不做 KI，open-world 物体识别能力会显著退化。
- **Hierarchy in one model**：π0.5 内部隐式有两个 frequency——VLM 处理 high-level \"now I should pick up the towel\"（语言中间表示），action expert 处理 low-level continuous control。这和 Helix S1/S2 是**同一思想的不同实现**：Helix 拆成两个独立模型 + latent vector；π0.5 是一个模型内部隐式分层 + 语言 token 做桥。
- **结果**：在 3 个完全 unseen 家庭里清理厨房 / 卧室，长 horizon 任务成功率非平凡（具体数字见 paper 表 3）。这是 2025 年 generalist robot policy 最有信服力的一次 open-world 评测。

### 5. π0.6 / RECAP：on-robot RL post-train

> 截至 2026-05，π0.6 的主要公开材料是 PI blog [\"RECAP\"](https://www.physicalintelligence.company/blog/recap)；是否已有完整 arxiv paper [uncertain]。下述要点取自 blog + Sergey Levine 在 2025-Q4 / 2026-Q1 几次公开讲座（[Stanford MLSys seminar 2026-01 talk](https://www.youtube.com/) [uncertain 具体链接]）。

- **基线**是 π0.5 权重；**post-train** 阶段引入 **RL**——但不是经典 on-policy PG，而是 PI 自创的 \"**Recap = advantage-conditioned policy**\" 思路：
  - 在 deployment 中收集 trajectory + 自动 / 人工 success 信号；
  - 学一个 value / advantage estimator；
  - 把 advantage 作为**额外的 conditioning token** 喂给 policy，训练时用所有数据（成功+失败），推理时 condition 在 \"high advantage\" 上 → 类似 decision transformer / RvS 的思路，避开了纯 PG 的 sample efficiency 灾难。
- **应用场景**：blog 展示了机器人在**真实咖啡店**做拉花、清洁，以及工厂装配。强调 \"continual improvement from deployment data\" → 闭环 data flywheel。
- 这是 2025 年 VLA 圈第一次有公司声称 **RL post-train 真的在真机器人上带来稳定收益**（Gemini Robotics 1.5 同期也提了类似思路但闭源）。对 Qwen agentic RL 团队的参考价值：advantage-conditioning 是 \"想用 RL 但又怕 reward hacking / sample inefficiency\" 时的一种保守路线。

## 训练方法核心

- **Pretrain**：直接复用 PaliGemma-3B 的 web pretraining，PI 不重新 pretrain VLM。
- **Mid / co-training**（π0.5 之后才显式拆出这个阶段）：web VQA + 机器人 trajectory + verbal commands 混合训练；用 KI 保护 VLM 知识。
- **SFT**：在 base 上 finetune 到具体任务（折衣服、装杯子），通常 ~10-100 小时该任务 demo。
- **RL post-train**（π0.6 / RECAP）：advantage-conditioned policy，用部署回流数据，详见上节。
- **算力**：π0 paper 没给具体 GPU-hour 数字；blog 暗示在 PI 内部集群（[uncertain 规模，社区 [推测] H100 数百卡级别]）上训练 \"weeks\" 量级。π0.5 / π0.6 算力**未披露**。

## 与 eval / benchmark 的接口

- **π0 / π0-FAST**：paper 内报 **LIBERO**、**SIMPL** [uncertain 是否同名] 等 sim benchmark，以及 self-defined real-world tasks (\"fold laundry\", \"bus a table\", \"assemble a box\")。LIBERO 上 π0 显著优于 OpenVLA / Octo。
- **π0.5**：paper 引入的最重要 eval 是 **\"in-the-wild new home\" success rate**，3 个没在训练里出现过的真实家庭，跨任务 long-horizon。这是同代里**唯一**做了 unseen-home eval 的 VLA。
- **第三方复现**：
  - HF `lerobot` team 已经在自己机器人上重新跑了 π0 base + finetune，结果与 paper 大致一致（[lerobot blog 2025](https://huggingface.co/blog/lerobot) [uncertain 链接]）；
  - 多个学术组（CMU、Berkeley）把 π0 base 当作 \"new OpenVLA\" 在用，社区接受度 = 当下事实标准。
- **质疑 / contamination**：尚未看到对 π0 / π0.5 的严肃 contamination 指控。一个温和质疑是 PI 的 \"unseen home\" 评测仍由 PI 自己执行 + 自己定 success criteria，缺第三方双盲（这对所有机器人 paper 都成立，不只是 PI）。

## 未知与争议

明确没披露 / 没说清的项（截至 2026-05）：

1. **π0.6 是否会开权重**——π0 / π0.5 base 都开了，但 π0.6（加 RL post-train + 部署数据）涉及商业价值，[uncertain]。
2. **训练数据精确组成**：π0.5 paper 写了 mixture 的类别，没给精确小时数比例；web VQA 用的是哪个 (LLaVA mix / Cauldron / 自采) 没说清。
3. **RECAP 的 advantage estimator** 具体怎么训的、reward function 怎么定的（特别是 \"咖啡拉花漂不漂亮\" 这种主观 reward）——blog 一笔带过，没有方法细节。
4. **算力 / 训练成本** 全系列基本未披露。
5. **跨 embodiment generalization 的边界**：paper 报的都是\"训练时见过的机器人平台\"上的 finetune 结果。**完全新平台 zero-shot** 性能 [uncertain]，社区零星试验显示不太行（需要至少几小时 finetune）。
6. **Inference latency 实测**：paper 给 10-step Euler ≈ \"real-time\"，但具体 GPU 上 50 Hz 是不是真稳定 [uncertain]。
7. **π0 与 PaliGemma2 / Gemma3 backbone 升级**：到 2026-05 PI 是否已经把 backbone 换成更新版本？[unknown — 没找到一手 source 证实]。

主要争议：

- **flow matching vs autoregressive token**：π0-FAST 自家证明两者性能相当，那 flow matching 的复杂度还值不值？PI 立场是\"flow matching 在 inference latency 上仍有 edge\"，但社区一部分人（Chelsea Finn 自己也在多次 talk 里承认）认为 FAST tokenizer 路线是\"更工程友好的未来\"。
- **\"foundation model for robots\" 叙事**：π0 是不是 robotics 的 GPT-3 时刻？Brooks / Hinton 等持续质疑——核心反驳是 robotics 数据规模仍比 LLM 小 6 个数量级，所谓 foundation 更像 \"strong pretraining + heavy finetune\"。π0.5 的 unseen home 结果稍微回击了这个质疑但远未平息。

## 与同代 VLA 的快速对照（参见 D2 Helix、D3 GR00T、D4 Gemini Robotics 的同表）

| 维度 | π0 / π0.5 | Helix | Gemini Robotics 1.5 | OpenVLA |
|---|---|---|---|---|
| Backbone | PaliGemma-3B | open-source 7B VLM (具体未公开) | Gemini 衍生 | Prismatic-7B |
| Action head | flow matching (300M expert) / FAST autoregressive | 80M cross-attn transformer (BC) | ER + VLA 双模型 | autoregressive discretized action tokens |
| 频率 | ~50 Hz chunk | S1 200 Hz / S2 7-9 Hz | ER 慢思 + VLA 中频 | 1-5 Hz |
| 跨 embodiment | 7+ 平台单权重 | 仅 Figure 02/03 | DM 内部 + Aloha + Apptronik | OXE 训练，泛化弱 |
| 开放度 | base 权重开 + paper 全 | 全闭 | 闭 | 全开 |
| RL post-train | π0.6 RECAP | 无 (BC only) | 暗示但闭源 | 无 |
| 学术可引用性 | **高** | 低 | 中 | 高 |

**核心 takeaway for Qwen eval lead**：在 robot foundation model 这条线上，π-series 是**唯一一个既有完整 paper、又有开源 base 权重、又有清晰 RL post-train 路径**的家族。如果做 robotics 相关评测 / 数据策略，π0 / π0.5 / π0-FAST 是必须读的 \"reference stack\"——它们的数据 mixture、knowledge insulation trick、action tokenizer 都直接可以借鉴到 multimodal agentic RL 的训练流程里（特别是 KI 思想：\"加新任务 fine-tune 时怎么保住原 backbone 知识\" 是 agentic RL 同样头疼的问题）。

## 推荐外部材料

- [π0 paper, arxiv:2410.24164](https://arxiv.org/abs/2410.24164) — VLA 时代的 reference architecture，必读。
- [π0.5 paper, arxiv:2504.16054](https://arxiv.org/abs/2504.16054) — open-world 泛化 + KI；如果只读一篇 PI 的 paper，读这篇。
- [π0-FAST paper, arxiv:2501.09747](https://arxiv.org/abs/2501.09747) — action tokenizer 设计；对 \"action 该不该离散化\" 的争论给出实验答案。
- [Physical Intelligence blog](https://www.physicalintelligence.company/blog) — 每个模型对应一篇 blog，video demo 比 paper 直观。
- [HuggingFace `lerobot/pi0`](https://huggingface.co/lerobot/pi0) — base + finetune 权重 + 推理代码，能在 RTX 4090 跑起来。
- [Sergey Levine, RSS 2025 keynote \"Foundation Models for Robotic Control\"](https://www.youtube.com/) [uncertain 具体链接] — Levine 自己 narrate π0 → π0.5 → RECAP 的设计动机，比 paper 更直白。
- [Chelsea Finn, CoRL 2024 / 2025 talks](https://www.youtube.com/) [uncertain 具体链接] — 互补视角，强调跨 embodiment 数据 strategy。
- [HuggingFace `lerobot` docs](https://huggingface.co/docs/lerobot) — 想自己复现 / finetune π0 的入口。

---

[^lerobot-pi0]: HuggingFace, `lerobot/pi0` model card, https://huggingface.co/lerobot/pi0 — 含 base + finetuned checkpoints + 复现指令。
[^pi0-paper]: Black et al., \"π0: A Vision-Language-Action Flow Model for General Robot Control\", arxiv:2410.24164, 2024-10-31, §3 Architecture. PaliGemma 选型见 §3.1，flow matching 公式见 §3.2，跨 embedding padding 见 §4.1。
