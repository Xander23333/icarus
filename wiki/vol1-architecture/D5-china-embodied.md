# 中国 embodied / humanoid VLA 群像（2024-2026.05）

> **范围**：本节梳理 2024-2026.05 期间在公开材料里能查到一手 source 的中国 humanoid / embodied VLA 玩家：智元 AgiBot、银河通用 Galbot、宇树 Unitree、小鹏 Iron、优必选 Walker S、以及以中科院自动化所 / 北大-BAAI 为代表的院校-机构平台（RoboBrain、RDT-1B、UniVLA）。读者 = Qwen 评测 owner，目的是 **快速分辨"谁有 paper / 谁有权重 / 谁只有展会视频"**，避免被 PR 节奏带偏。本节凡是仅有发布会/抖音视频支撑的陈述一律标 [marketing] 或 [uncertain]。

## 路线定位（1 段）

中国侧 humanoid VLA 玩家可粗分三档：(1) **有 paper + 开权重 + 公开数据**——只有 **智元 AgiBot World / GO-1**（[arxiv:2503.06669](https://arxiv.org/abs/2503.06669)）和 **北大-BAAI 系的 RDT-1B / UniVLA**（[arxiv:2410.07864](https://arxiv.org/abs/2410.07864)），是和 π0 / OpenVLA 真正处在同一对话层的工作；(2) **有 paper 或 tech 细节但权重闭源** —— **Galbot GraspVLA / TrackVLA**、**RoboBrain 2.0**（[arxiv:2502.21257](https://arxiv.org/abs/2502.21257)）属于这一档，可读但不可复现；(3) **几乎只有发布会 + demo 视频**——**Unitree G1/H1 上的 VLA 工作、小鹏 Iron、优必选 Walker S2、Fourier GR-2、星动纪元 Star1** 都属于这档，硬件可买可看，"VLA 大脑"则基本是黑箱（往往是接第三方 GraspVLA / GO-1 / Qwen2-VL fine-tune）。本节按这三档展开，重点说**谁是大脑、谁只是身体**。

## 玩家清单（截至 2026-05）

| 玩家 | 类型 | 代表 VLA / 模型 | 权重 | paper / 一手 source |
|---|---|---|---|---|
| **智元 AgiBot** 智元机器人 | 整机 + 模型 + 数据 | AgiBot World Colosseo 数据集；**GO-1**（Genie Operator-1）VLA | 数据集开源；GO-1 部分 checkpoint 开源 | [arxiv:2503.06669](https://arxiv.org/abs/2503.06669)；[agibot-world.com](https://agibot-world.com)；[GitHub OpenDriveLab/AgiBot-World](https://github.com/OpenDriveLab/AgiBot-World) |
| **Galbot 银河通用** | 整机（轮式双臂 G1）+ 模型 | **GraspVLA**（pre-train on synthetic）、**TrackVLA**（导航）、**GroceryVLA** | 闭 | [galbot.com](https://galbot.com)；[GraspVLA arxiv:2505.03233](https://arxiv.org/abs/2505.03233)；[TrackVLA arxiv:2505.23189](https://arxiv.org/abs/2505.23189) |
| **Unitree 宇树** | 整机硬件为主（G1 / H1 / H1-2 / R1） | 自研 VLA 暂无公开 paper；2025 发布 **UnifoLM-WMA-0**（world-model + action） | UnifoLM 部分开源 | [unitree.com](https://www.unitree.com)；[UnifoLM GitHub](https://github.com/unitreerobotics/unitree_rl_gym) [uncertain repo]；[Unitree HF org](https://huggingface.co/unitreerobotics) |
| **Xpeng 小鹏 Iron** | 整机 | "端到端大模型"（与汽车 XNGP 共享 backbone 声称） | 闭 | [小鹏 1024 科技日 2024-11-06](https://www.xiaopeng.com)；[1024 2025-11](https://www.xiaopeng.com) [marketing 为主] |
| **Ubtech 优必选 Walker S / S2** | 整机 + 工厂落地 | "BrainNet" / Walker 大脑（与百度 / 腾讯 / 华为合作多版本） | 闭 | [ubtrobot.com](https://www.ubtrobot.com)；车厂 demo 视频 [marketing 为主] |
| **Fourier 傅利叶 GR-2 / N1** | 整机 | 无自研 VLA 公开；OEM 平台为主 | — | [fftai.com](https://www.fftai.com) |
| **星动纪元 Robot Era Star1 / XBot-L** | 整机 | ERA-42（自研 VLA，5 指灵巧手） | 闭 | [robotera.com](https://www.robotera.com)；[Star1 100m run 2024-10 视频](https://www.youtube.com/@RobotEra) |
| **BAAI / 北大 RDT-1B** | 学术-机构模型 | **RDT-1B**（双臂 diffusion VLA, 1.2B） | **全开权重** | [arxiv:2410.07864](https://arxiv.org/abs/2410.07864)；[rdt-robotics.github.io](https://rdt-robotics.github.io)；[HF robotics-diffusion-transformer/rdt-1b](https://huggingface.co/robotics-diffusion-transformer/rdt-1b) |
| **BAAI RoboBrain (2.0)** | 学术-机构模型 | RoboBrain 1.0 / 2.0 = embodied reasoning VLM（不直接出动作） | 开权重 | [arxiv:2502.21257](https://arxiv.org/abs/2502.21257)；[FlagOpen/RoboBrain GitHub](https://github.com/FlagOpen/RoboBrain) |
| **UCAS / 自动化所 UniVLA** | 学术 | UniVLA（latent action codebook） | 开 | [arxiv:2505.06111](https://arxiv.org/abs/2505.06111) [uncertain id]；[OpenDriveLab UniVLA](https://github.com/OpenDriveLab/UniVLA) |
| **Pi Square π² / X-Square** | 创业 | WALL-A / WALL-OSS（开源 embodied LLM） | 开 | [x-humanoid.com](https://www.x-humanoid.com) [uncertain url] |

下面只对**有真技术内容**的三档前两档展开。

## 1. 智元 AgiBot World + GO-1（第一档，最值得读）

智元（AgiBot）是这一波里**唯一一家像 PI 那样"先把数据和 paper 摆出来"**的中国公司。

### 数据集 AgiBot World Colosseo（2025-03）
- 规模：**>1M episodes，217 任务，100+ 真机数据采集，5 个不同 embodiment**（轮式 + 双足 + 双臂台式 + Franka），公开数据 ~80 TB。比 Open X-Embodiment（~1M episodes 但来自 22 个学术机构、质量不齐）质量上更一致——单一公司、统一采集 SOP。[^agibot-paper]
- 采集 setup：自建 **"数据采集工厂"** 在上海，雇 100+ 全职 teleoperator，VR + leader-follower 双模式。这是国内目前最接近"机器人版数据标注厂"的实例（对比 PI 是分布式合作，DeepMind 是内部 + Aloha 学术）。
- 任务分布：家务（折叠/擦拭/收纳）+ 厨房 + 办公 + 零售货架。语言指令是事后人工补标，**不是采集时实时说出的**——这点 paper 在 §3.2 明确说了，对 instruction-following 训练有偏差影响。

### 模型 GO-1（Genie Operator-1, 2025-03 同期发布）
- 架构：**ViLLA**（Vision-Language-Latent-Action）三段式。前端 InternVL-2.5 系 VLM 做视觉 + 语言编码 → "Latent Planner"（自回归出 latent action token，类似 UniVLA 的离散 codebook） → "Action Expert"（diffusion head，出连续控制）。[^agibot-paper §4]
- 这是一个**典型的"S2 latent → S1 action"** 思路（和 Helix / GR 1.5 同代），但智元的特殊点是**显式 latent action codebook**——latent 是 discrete token，可以监督学习，可以做 chain-of-thought-style 中间推理（paper 给了 latent planner 单独 fine-tune 的实验）。
- 训练 pipeline：
  1. VLM backbone 用 InternVL2.5-2B/8B 初始化；
  2. Latent action codebook 通过 **VQ-VAE on action sequences** 预训练（在 AgiBot World + Open X-Embodiment 上）；
  3. 整体 BC fine-tune；**没用 RL**。
- 报数：paper Table 4-5 在自建 200 任务 benchmark 上对 OpenVLA / RDT-1B / π0 都有 head-to-head，GO-1 平均 success rate 比 RDT-1B 高 ~12 pp、比 OpenVLA 高 ~30 pp[^agibot-paper]。**但 benchmark 是智元自建、自跑**——存在 home-field advantage，第三方独立复现尚无。
- 开源情况：数据集完全开；GO-1 **部分 checkpoint 开**（Latent Planner 单独权重 + tokenizer），完整 end-to-end checkpoint 截至 2026-05 [uncertain] 是否全开。

### 后续（2025 下半年 - 2026.05）
- 2025-08 智元 X1 / G1 整机量产，主打**金融 / 商场导览**场景，搭载 GO-1。
- 2026-Q1 公开"GO-2" 路线图（[marketing] 来源仅有发布会），声称引入 RL post-training，无 paper。
- **对 Qwen 团队的可参考度**：⭐⭐⭐⭐⭐——AgiBot 是国内 VLA 最能严肃引用的工作，paper + 数据 + 部分权重三件齐，benchmark 数字虽然 home-field 但实验设计是规范的。

## 2. Galbot 银河通用（第二档，paper 多但权重闭）

- 团队背景：北大王鹤组 spin-off，**强烈押注"synthetic data + sim2real"** 路线，和 PI / Figure 的真机 teleop 路线明确分叉。
- 主力机型：**G1**（轮式底盘 + 双 7-DoF 臂 + 灵巧手），非双足。Galbot 公开说"双足不是优先级，仓储零售场景轮式更稳"。
- 代表模型：
  - **GraspVLA**（[arxiv:2505.03233](https://arxiv.org/abs/2505.03233)）：**纯合成数据预训练**的抓取 VLA。生成 ~1B 帧合成数据（NVIDIA Isaac + 程序化场景），声称 zero-shot 真机泛化。这是和 PI / 智元最大的方法论差异——**赌 sim2real 而非 teleop scaling**。
  - **TrackVLA**（[arxiv:2505.23189](https://arxiv.org/abs/2505.23189)）：行人/目标跟随导航 VLA。
  - **GroceryVLA / 美团零售场景**（2025 美团投资后落地）：[uncertain] 仅有发布会，无 paper。
- benchmark：GraspVLA paper 在自建合成 + 真机 hold-out 上报数，第三方独立测试**尚无**。
- 权重：**全闭源**。这点决定了 Galbot 在学术圈的可参考度远低于智元/RDT。
- **对 Qwen 团队**：⭐⭐⭐——paper 值得读（sim2real 路线方法论参考），权重不可用。

## 3. RDT-1B / RoboBrain / UniVLA（学术-机构档，最干净）

- **RDT-1B**（[arxiv:2410.07864](https://arxiv.org/abs/2410.07864)，清华 TSAIL + BAAI）：1.2B diffusion transformer，**双臂统一动作空间**，在 46 个数据集上预训练后在 6k+ 自采 episode 上 fine-tune。**全权重开源**（HF），是中国侧第一个能和 OpenVLA 真正对标的"开源 baseline" VLA。架构上的关键贡献：**物理可解释 unified action space**（处理不同机器人 DoF 不一致的归一化方案），后续 GO-1 / UniVLA 都借鉴。
- **RoboBrain 2.0**（[arxiv:2502.21257](https://arxiv.org/abs/2502.21257)，BAAI）：**不是 VLA**，是 embodied reasoning VLM——输出空间是文本（task plan、affordance、reference point），不直接出动作。定位类似 Gemini Robotics 的 ER 模型。和 GO-1 / RDT 是**互补关系**：RoboBrain 做 S2，下游接一个 action policy 做 S1。BAAI 公开了 RoboBrain + RDT 的组合 demo。
- **UniVLA**（[OpenDriveLab arxiv:2505.06111](https://arxiv.org/abs/2505.06111) [uncertain id]）：核心贡献是 **latent action 的无监督学习**——从未标注视频里学 latent action codebook，再 condition 一个轻量 action head。这个 latent codebook 思路 GO-1 直接采用。
- **对 Qwen 团队**：⭐⭐⭐⭐——这三个是国内 VLA **唯一能 reproduce 的学术 baseline 组合**。要在 robotics-related eval 上立 baseline，第一选择是 RDT-1B（开权重 + 中等规模 + 双臂 + paper 清楚）。

## 4. 整机厂商（第三档，硬件 ≫ 模型）

这一档**几乎没有可独立评估的 VLA 工作**，大部分公司的"大脑"是接智元 / 银河 / Qwen-VL fine-tune 的中间层或干脆是脚本 + 单任务 BC，统称"VLA"是 marketing 修辞。

- **Unitree 宇树**：G1（2024-05 发布，~9.9 万）+ H1 / H1-2 + R1 是国内**事实标准 humanoid 硬件平台**，被几乎所有学术组用来做 VLA 研究。Unitree 自己 2025-11 公开了 **UnifoLM-WMA-0**（[HF unitreerobotics/UnifoLM-WMA-0](https://huggingface.co/unitreerobotics) [uncertain 具体 model id]），是 world-model + action policy 的开源尝试，但**规模和成熟度均低于 GO-1 / RDT**。Unitree 的核心定位仍是硬件供应商。
- **Xpeng Iron**：小鹏 1024 科技日两届的核心展示，2025-11 第二代 Iron 走路 demo 在国内媒体刷屏，但**关于"大脑"只有一句话**："和 XNGP 自动驾驶共享端到端 backbone"——这是技术上**说不通**的（自驾 backbone 输出是车辆控制空间，和 30+ DoF 双足机器人没有可共享的 action head）。可信的解读：**共享的是视觉感知前端**（VLM / BEV encoder），action 部分独立。[uncertain — 小鹏从未发 paper 或 tech report]
- **Ubtech 优必选 Walker S2**（2025-Q4）：主打"工厂落地"（蔚来、富士康、东风），demo 视频里 Walker S 在车厂分拣零件。"BrainNet" 是 Ubtech 给"软件栈"的统称，包含和**百度文心 / 腾讯混元 / 华为盘古**的多版本合作。**没有自研 VLA paper**。可信解读：Walker 的运动控制是传统 MPC + RL，"大脑"是接外部 LLM 做任务编排，**不是 end-to-end VLA**。
- **Fourier GR-2 / N1**：明确定位 OEM 硬件平台，不做大脑。
- **星动纪元 Star1 / Robot Era**：2024-10 跑步 demo 出圈（H100m 户外越野跑），自研 **ERA-42**（5 指灵巧手 VLA），但**无 paper、无权重**，[marketing] 评估为主。

## 与 eval / benchmark 的接口

- **国内 VLA 没有公认 benchmark**。最接近的是 AgiBot 自建的 200 任务真机 eval、Galbot 的 GraspVLA 合成 eval、以及社区零散用的 LIBERO / SimplerEnv（清华几个组在跑）。**没有国内版的"OpenVLA leaderboard"**。
- 学术圈引用最多的还是 **LIBERO / CALVIN / SimplerEnv**（美国学术 benchmark）+ **Open X-Embodiment**（DeepMind 主导但中国数据贡献少）。
- contamination 信号：GO-1 / RDT 都在 Open X-Embodiment 上预训练过，所以**任何在 OXE 子集上的 eval 数字都要打折看**。
- **第三方独立复现**：截至 2026-05，公开能找到的中国 VLA 第三方复现报告**几乎为零**——这一点和 LLM 圈"评测复现是基本功"的成熟度差距很大，是 Qwen 团队潜在的入场机会（做一个"中文 VLA leaderboard"）。

## 未知与争议

1. **真机数据规模 vs 质量**：智元 1M episode 是国内最大但仍小于 PI 内部数据规模（PI 未公开但根据 π0 paper 推算 >10k 小时），数据质量层级**未公开**（什么比例是 cherry-picked successful、什么比例是 raw 含失败）。
2. **sim2real 路线（Galbot）vs teleop scaling 路线（智元 / PI）哪个赢**：2026-05 仍未分晓。Galbot 的 zero-shot 真机数字是自报，第三方无法验证。
3. **整机厂的"VLA 大脑"实质**：小鹏 / 优必选 / 星动声称的"端到端 VLA"在没有 paper 的情况下**默认应当视为 marketing**，直到出 tech report。这不是偏见而是基线判断。
4. **算力**：所有中国 VLA 玩家都**未披露**预训练算力。智元 GO-1 paper 给了 GPU-hours 估计 [uncertain 数字]，其他全无。
5. **和大模型公司的关系**：阿里 Qwen、字节 Doubao、智谱 GLM、月之暗面 K2 截至 2026-05 **均未公开 VLA / 机器人方向工作**。Qwen-VL 是大量第三方 VLA 工作的 backbone 选择（包括智元 / Galbot 的某些消融），但 Qwen 团队自己尚未做 robotics。**这是潜在的空白市场**。
6. **政策驱动**：2025 工信部 humanoid 路线图、2026 上海/北京/深圳数据采集补贴，导致大量"项目制 VLA"涌现——评估时要区分"真技术"与"政策套利"。

## 快速对照表（中国 vs 美国同代）

| 维度 | 中国侧最强（智元 GO-1 + AgiBot World） | 美国侧 PI π0 / π0.5 |
|---|---|---|
| paper | 有，arxiv | 有，arxiv |
| 数据规模 | ~1M episode（公开） | ~10k 小时 teleop（声称，未公开数据） |
| 数据开源 | **公开** | **不公开** |
| 模型权重 | 部分开 | π0 base 开 |
| 架构 | VLM + latent action + diffusion expert | VLM + flow-matching head |
| 训练方法 | BC only | BC + flow matching；π0.5 加 co-training |
| benchmark | 自建 200 task + LIBERO | LIBERO + 多个真机 |
| 第三方复现 | **基本无** | 多个（LeRobot 社区） |

**结论**：智元在**数据开放度**上反超 PI，在**模型成熟度 + 社区生态**上仍落后 6-12 个月。其他中国玩家与 PI / Figure / DM 差距更大，且主要差在**披露透明度**而非纯技术。

## 推荐外部材料

- [AgiBot World paper, arxiv:2503.06669](https://arxiv.org/abs/2503.06669) — 国内 VLA **必读第一篇**。重点看 §3 数据采集 SOP 和 §4 ViLLA 架构。
- [agibot-world.com 数据集页](https://agibot-world.com) — 想做中文 VLA eval 的起点。
- [RDT-1B paper, arxiv:2410.07864](https://arxiv.org/abs/2410.07864) + [HF 权重](https://huggingface.co/robotics-diffusion-transformer/rdt-1b) — 国内**唯一可复现的开源 VLA baseline**。
- [GraspVLA, arxiv:2505.03233](https://arxiv.org/abs/2505.03233) — sim2real 路线的代表作，方法论参考价值高于其工程价值。
- [RoboBrain 2.0, arxiv:2502.21257](https://arxiv.org/abs/2502.21257) — 想理解"embodied reasoning VLM"（而非 VLA）的国内代表。
- [LeRobot HF 社区中文 VLA 复现讨论](https://huggingface.co/lerobot) — 第三方复现的零散讨论集中地。
- [机器之心 / 量子位 humanoid 年度盘点 2025](https://www.jiqizhixin.com) — 中文媒体里 PR 过滤后最靠谱的两家，看完整生态用。
- [Unitree HF org](https://huggingface.co/unitreerobotics) — 想用国产硬件 + 开源 stack 做实验的入口。

---

[^agibot-paper]: AgiBot World Team, "AgiBot World Colosseo: A Large-scale Manipulation Platform for Scalable and Intelligent Embodied Systems", arxiv:2503.06669, 2025-03-09. §3 数据采集；§4 GO-1 ViLLA 架构；Table 4-5 benchmark 数字。
