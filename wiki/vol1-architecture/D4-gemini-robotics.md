# Gemini Robotics（Google DeepMind 机器人线）

> **范围**：DeepMind 把 Gemini 多模态主干迁到机器人的整条线，包括 RT-2 → RT-X → RT-H 旧 PaLI/PaLM-E 时代到 2025-03 起的 **Gemini Robotics / Gemini Robotics-ER / Gemini Robotics 1.5**。读者 = Qwen eval lead，已熟 transformer / VLM / RL；这里重点是 VLA（vision-language-action）作为 frontier multimodal 的延伸，以及 ER（embodied reasoning）变体的方法学位置。截至 2026-05。

## 路线定位（1 段）

到 2026-05，VLA frontier 实质是\"两家半\"：**DeepMind Gemini Robotics**（闭源、和 Apptronik / ALOHA / Franka 多本体绑定）、**Physical Intelligence π0 / π0.5**（开源权重，OpenPI）、半家 **NVIDIA GR00T N1/N2**（开源 + Isaac sim 生态）。DeepMind 的差异化是**直接复用 Gemini 2.0/2.5 多模态 backbone**，不另起 vision encoder；并把推理拆成 **ER（embodied reasoning，纯 VLM 输出空间/物理 plan）** + **VLA（action head 直出 motor token）** 两层，让\"通用云上 Gemini 推理 + 边端小动作模型执行\"成为产品架构。Carolina Parada（DeepMind robotics 负责人）多次在 talk 里把这条路线定位为 **\"Gemini 作为 robotics 的 GPT moment\"** 而非另开一个 robotics 模型族（[DeepMind blog 2025-03](https://deepmind.google/discover/blog/gemini-robotics-brings-ai-into-the-physical-world/)）。

## 代表模型清单

| 模型 | 发布日 | 主干 | 输出 | 一手 source |
|---|---|---|---|---|
| RT-1 | 2022-12 | EfficientNet + Transformer (35M) | 离散 action token | [arxiv:2212.06817](https://arxiv.org/abs/2212.06817) |
| RT-2 (PaLI-X 55B / PaLM-E 12B co-fine-tune) | 2023-07 | PaLI-X / PaLM-E | action 当文本 token 输出 | [arxiv:2307.15818](https://arxiv.org/abs/2307.15818) |
| RT-X / Open X-Embodiment | 2023-10 | RT-1/RT-2 在 22 个本体 60 数据集上联训 | 同上 | [arxiv:2310.08864](https://arxiv.org/abs/2310.08864) |
| RT-H | 2024-03 | PaLI-X，引入\"language motion\" 中间层 | hierarchical: lang → action | [arxiv:2403.01823](https://arxiv.org/abs/2403.01823) |
| AutoRT / SARA-RT / RT-Trajectory | 2024-01 | — | data collection / 推理加速 / 轨迹条件 | [DeepMind blog 2024-01](https://deepmind.google/discover/blog/shaping-the-future-of-advanced-robotics/) |
| **Gemini Robotics** (VLA) | 2025-03-12 | Gemini 2.0 主干 + action decoder | 双手 ALOHA / Apptronik Apollo 动作 | [DeepMind blog](https://deepmind.google/discover/blog/gemini-robotics-brings-ai-into-the-physical-world/), [tech report PDF](https://storage.googleapis.com/deepmind-media/gemini-robotics/gemini_robotics_report.pdf) |
| **Gemini Robotics-ER** (Embodied Reasoning) | 2025-03-12 | Gemini 2.0 微调，**不出 action**，出空间 plan / pointing / 3D | VLM 文本+坐标 | 同上 |
| **Gemini Robotics On-Device** | 2025-06-24 | 小型 VLA，本地可跑 | action | [DeepMind blog 2025-06](https://deepmind.google/discover/blog/gemini-robotics-on-device-brings-ai-to-local-robotic-devices/) |
| **Gemini Robotics 1.5 + Gemini Robotics-ER 1.5** | 2025-09-25 | Gemini 2.5 主干，agentic / 跨本体迁移 | VLA + ER 双发 | [DeepMind blog 2025-09](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/) |

## 架构核心（按已公开材料）

### 1. 三层抽象：Gemini backbone → ER → VLA

Gemini Robotics tech report (2025-03) §2 把系统拆成：

- **Gemini 2.0 / 2.5 多模态主干**（云端，frontier 全尺寸）—— 不为 robotics 改架构，**直接复用 Gemini 主线 checkpoint**。这是和 π0（基于 PaliGemma-3B）/ GR00T（基于 Eagle-2 VL）的本质区别：DeepMind 把\"frontier multimodal + tool use + long-context\"原生带入 robotics，**不需要单独训机器人主干**。
- **Gemini Robotics-ER（Embodied Reasoning）**：在 Gemini 2.0 上做 SFT，让它**输出空间 grounding 信息**——2D point、bbox、轨迹、抓取姿态、affordance 描述，但**不直接出 motor action**。可以当成\"机器人专用的 spatial CoT VLM\"。tech report §4 把 ER 当成\"通用 brain\"，下游接任何 low-level controller（不一定是 Gemini 自己的 VLA，也可以接 π0 / 传统 motion planner）。
- **Gemini Robotics VLA**：在 ER checkpoint 之上继续微调，**加 action decoder**（tech report 没披露是 diffusion head 还是 autoregressive token，[uncertain — paper 含糊处理]）；输出特定本体的关节空间动作，运行频率 \"50 Hz 级\"（blog 用词），云-边端混合架构。

外部理解（[Chris Paxton 2025-03 blog](https://chrispaxton.com/) 等）：ER + VLA 拆分对应 \"system 2 / system 1\"，**和 π0.5 的 \"high-level VLM + low-level action expert\" 是同一套思路的不同实现**。差异是 DeepMind 把 high-level 直接绑 Gemini frontier，**继承 long-context / tool use / web grounding**。

### 2. 从 RT-2 到 Gemini Robotics 的连续性

- **RT-2 的核心 idea（[arxiv:2307.15818](https://arxiv.org/abs/2307.15818)）：action 当文本 token**——把 7-DoF 离散化成 256 bin 词表，VLM 直接 next-token 预测。这套\"co-fine-tune VLM 同时做 VQA + action\"是 VLA 范式起点，被 OpenVLA / π0 / GR00T / Gemini Robotics 全部继承。
- **RT-X（[arxiv:2310.08864](https://arxiv.org/abs/2310.08864)）**：Open X-Embodiment 数据集（22 本体、527 skill、~100 万 trajectories）证明**跨本体联训正迁移**——同一个 model weights 在没见过的本体上 zero-shot 比单本体训练好。这是 Gemini Robotics 1.5 \"Motion Transfer\" 卖点的数据基础。
- **RT-H（[arxiv:2403.01823](https://arxiv.org/abs/2403.01823)）**：引入 \"language motion\" 中间层（如 \"move arm left\"），把 task → language motion → action 显式分两段。**这是 ER / VLA 拆分的方法学雏形**——RT-H 的 language motion 后来演化成 Gemini Robotics-ER 的空间 plan 输出。
- 中间过渡：**AutoRT** 用 VLM 自主提任务 + 自主采集数据；**SARA-RT** 把 RT-2 推理加速 14×；**RT-Trajectory** 把 2D 轨迹画在图上当条件。这些都被 Gemini Robotics 默默吸收（tech report §3 数据 pipeline 部分提到 \"autonomous data collection\" 但无细节）。

### 3. 多本体支持

Gemini Robotics 默认评测平台：

- **bi-manual ALOHA**（Stanford / Google 自研的双臂遥操平台），原 Mobile ALOHA 论文 [arxiv:2401.02117](https://arxiv.org/abs/2401.02117)。Gemini Robotics 大部分公开 demo（叠衣服、折纸、拉链）跑在 ALOHA。
- **Franka 双臂**（工业臂）。
- **Apptronik Apollo 人形**：2025-03 blog 公开合作，2025-09 1.5 blog 进一步演示 Apollo 上 long-horizon agentic 任务（[Apptronik 2025-03 press](https://apptronik.com/news-collection/apptronik-and-google-deepmind-partner-to-develop-humanoid-robots)）。
- **1.5 引入 Motion Transfer**：DeepMind blog 2025-09 主打 \"同一权重在 ALOHA / Franka / Apollo 间迁移\"，无需 per-embodiment 微调；底层机制 paper 未细写 [uncertain — 推测是 action space 上加 embodiment-id token + 本体描述当 prompt]。

### 4. Gemini Robotics-ER 的能力面

ER 1.0 / 1.5 公开演示的能力（[tech report 2025-03](https://storage.googleapis.com/deepmind-media/gemini-robotics/gemini_robotics_report.pdf) §4, blog 2025-09）：

- **2D pointing**：\"点出杯子的把手\" → 输出像素坐标。和 Molmo (Allen AI) / RoboPoint / Magma 同赛道；ER 的优势是直接继承 Gemini 2.5 的 long-context 和多图。
- **3D bbox / 抓取姿态预测**：从单 RGB 估计 6-DoF grasp pose（无需深度）。
- **trajectory prediction**：在图上画一条运动轨迹给 low-level controller。
- **Code-as-policy**：ER 可输出 python 调用机械臂 API（继承 RT-2 的 chain-of-thought + Code as Policies 思路）。
- **多步 agentic planning（1.5 新增）**：跨任务长 horizon planning，搜索 web 查菜谱 → 拿食材 → 操作。这步把 robotics 接入 Gemini 的 tool use 生态（[blog 2025-09](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/) 主卖点）。

ER 在公开 embodied reasoning benchmark 上的报告分数（ER 1.5 blog 给出 7 个 benchmark 的 leader 位置，但无完整对比表 [uncertain — 部分 benchmark 是 DeepMind 自定义]）。

### 5. On-Device 模型（2025-06）

Gemini Robotics On-Device（blog 2025-06）：小型 VLA，本体上跑（参数量未披露，[unknown — 没找到一手 source]，外部推测 1-3B 级 [推测]），DeepMind 同时发了 SDK 让开发者**在自己数据集上 fine-tune** —— 这是 Google 在 robotics 里**第一次开放微调权限**（仍闭源权重，只能通过 API/SDK 微调）。和 π0 全开源权重对比，Google 路线明显更保守。

## 训练方法核心（外部已知）

DeepMind 在 robotics 上披露程度**显著低于** Gemini 主线 paper。tech report 主要披露：

- **基础**：Gemini 2.0/2.5 multimodal pretraining 已有的 web/视频/图文数据。
- **Robotics co-fine-tune**：在 Open X-Embodiment + DeepMind 内部 ALOHA/Apollo teleoperation 数据上 SFT，**action token 词表与文本词表共享**（RT-2 一脉相承）。
- **数据规模**：未披露具体小时数 / trajectory 数 [unknown]。外部推测 internal teleop 数据已达 10⁴ 小时量级 [推测]。
- **RL**：tech report **不提 RL**。1.5 blog 提 \"agentic\" 但没说是 RL 训出来的还是 SFT + Gemini 自带 reasoning。社区猜测 ER 主要靠 Gemini 2.5 thinking 模式 + spatial SFT，**不依赖 RLVR** [推测]。
- **算力**：完全未披露。

对比 π0 (Physical Intelligence)：π0 paper [arxiv:2410.24164](https://arxiv.org/abs/2410.24164) 给出 \"PaliGemma-3B + 300M action expert，flow matching action head，10k 小时 cross-embodiment data\" 的**完整开放配方**；DeepMind 啥都不给。这是 Google 内部 robotics 的一贯风格。

## 与 eval / benchmark 的接口

robotics 没有 LLM 那样的公认 leaderboard，主要看：

- **DeepMind 自报**（tech report 2025-03 表 1-3）：在内部 ALOHA tasks 上 Gemini Robotics 比 RT-2-X / π0（DeepMind 自跑） 高一截，但**所有对比都是 DeepMind 自实现 baseline**，第三方无法验证。
- **ER benchmark**：tech report 在 ERQA、RoboVQA、Where2Place 等公开 spatial reasoning benchmark 上报分。1.5 时进一步加 ERQA / Point-Bench / Open-RoboBench 等，DeepMind 声称 SOTA。
- **第三方独立复现**：因为权重和 API 都不全开放，**目前没有真正第三方独立 benchmark**。少数学术组通过 Gemini API（ER 1.5 在 AI Studio 开放 [blog 2025-09](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/)）做的对比，多停留在 ER 的视觉 grounding 部分，VLA 完全无法外部验证。
- **contamination 风险**：Open X-Embodiment 是公开数据集，Gemini Robotics 训了之后再在 OXE-derived task 上报分本身就有过拟合嫌疑（同样问题困扰 OpenVLA / GR00T）。

## 未知与争议

- **Action head 架构**：autoregressive token (RT-2 风格) vs diffusion / flow-matching head (π0 风格)？tech report 用 \"action decoder\" 含糊带过 [unknown — 没找到一手 source 明确说明]。
- **Motion Transfer 实现**：1.5 跨本体迁移的具体技术（embodiment embedding？action space 统一？还是只是 ER plan + 本体特定 controller？）blog 未细写 [推测]。
- **是否用 RLVR / RLHF on robot data**：DeepMind 完全沉默；外部推测 ER 是纯 SFT，VLA 可能用 BC + 少量 preference data [推测]。
- **On-Device 模型大小和延迟**：blog 只说 \"small enough to run locally\"，无具体数字 [unknown]。
- **和 Gemini 2.5 主线的算力共享比例**：robotics 团队复用主线 checkpoint 还是 fork 后独立训练？外部完全不知。
- **商业化路径**：Apptronik / Boston Dynamics（早期合作） 之外，是否进入工业自动化客户？2026-05 截止公开信息仍只是 demo / partnership announcement，**无大规模部署证据**。

## 推荐外部材料

- [DeepMind blog: Gemini Robotics + ER (2025-03)](https://deepmind.google/discover/blog/gemini-robotics-brings-ai-into-the-physical-world/) — 路线官宣，必读。
- [Gemini Robotics tech report PDF](https://storage.googleapis.com/deepmind-media/gemini-robotics/gemini_robotics_report.pdf) — 当前唯一一手 paper，虽然技术细节克制但定义了 ER/VLA 拆分。
- [DeepMind blog: Gemini Robotics 1.5 (2025-09)](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/) — agentic + Motion Transfer，1.5 与 Gemini 2.5 主线对齐。
- [RT-2 paper (arxiv:2307.15818)](https://arxiv.org/abs/2307.15818) — VLA 范式起点，action-as-token，理解 Gemini Robotics 必读前置。
- [RT-H paper (arxiv:2403.01823)](https://arxiv.org/abs/2403.01823) — \"language motion\" 中间层，ER/VLA 拆分的方法学源头。
- [Open X-Embodiment / RT-X (arxiv:2310.08864)](https://arxiv.org/abs/2310.08864) — 跨本体数据集，Motion Transfer 的数据基础。
- [π0 paper (Physical Intelligence, arxiv:2410.24164)](https://arxiv.org/abs/2410.24164) — 对照组，开放配方，看 Google 路线 vs 开源路线差异。
- [Carolina Parada talks (RSS 2024 keynote, CoRL 2024)](https://www.youtube.com/results?search_query=carolina+parada+deepmind) — DeepMind robotics 战略叙事一手来源。
- [Chris Paxton 2025-03 blog 评 Gemini Robotics](https://chrispaxton.com/) — 学术圈对 ER/VLA 拆分的第三方解读。
