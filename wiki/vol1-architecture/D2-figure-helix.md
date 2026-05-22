# Figure Helix（System 1 / System 2 humanoid VLA）

> **范围**：本节覆盖 Figure AI 在 2025-02 发布的 Helix 通用人形机器人控制模型，到 2026-05 为止的公开信息。Helix 是 humanoid VLA（vision-language-action）路线里最被反复引用的 "S1+S2 双频" 架构样板。读者 = Qwen agentic 评测 owner，对 VLM/VLA 本身熟悉，本节重点是 **System 1 / System 2 解耦 + 频率切分** 这一架构选择，以及对应的"我们究竟知道多少"诚实清单。

## 路线定位（1 段）

Helix 是 Figure AI 与 OpenAI 解约后（2025-02-04 Adcock 宣布[^adcock-split]）**12 天内**对外发布的自研端到端人形通用模型[^helix-launch]。它在 humanoid VLA 赛道里和 **Physical Intelligence π0 / π0.5**（[arxiv:2410.24164](https://arxiv.org/abs/2410.24164)）、**Google DeepMind Gemini Robotics / Gemini Robotics 1.5**（[blog 2025-03](https://deepmind.google/discover/blog/gemini-robotics-brings-ai-into-the-physical-world/)、[blog 2025-09 1.5](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/)）、**1X NEO/Redwood**、**Tesla Optimus（闭源）** 直接竞争。Helix 的差异化卖点只有两个公开点：(1) 完全 **on-board** 跑在双 embedded GPU 上，无云端推理；(2) **S1（200 Hz visuomotor）/ S2（7-9 Hz VLM reasoner）** 双频解耦，号称同一套权重直接控双臂上身 + 手指（35 DoF）。除此之外**几乎没有任何技术细节披露**——没有 paper，没有 tech report，没有模型卡，没有数据规模数字。本节绝大多数"内部细节"都必须标 [uncertain]。

## 代表发布清单

| 事件 | 日期 | 内容 | 一手 source |
|---|---|---|---|
| Figure ↔ OpenAI 解约 | 2025-02-04 | Adcock 推文："we made a major breakthrough on fully end-to-end robot AI, built entirely in-house" | [Adcock tweet](https://x.com/adrian_macneil/status/1886860695090876779) [uncertain 链接 id]；[The Robot Report 2025-02-05](https://www.therobotreport.com/figure-ends-collaboration-agreement-openai/) |
| **Helix 公开发布** | 2025-02-20 | 官方 blog "Helix: A Vision-Language-Action Model for Generalist Humanoid Control"，含双机器人协作整理杂货 demo 视频 | [figure.ai/news/helix](https://www.figure.ai/news/helix) |
| Helix on logistics | 2025-06 [uncertain 月份] | Adcock 展示 Helix 在 BMW Spartanburg 物流场景搬运 | [figure.ai/news](https://www.figure.ai/news)；[Adcock X timeline](https://x.com/adcock_brett) |
| Figure 03 硬件 + Helix | 2025-10-09 | Figure 03 整机发布，强调"为 Helix 重新设计的传感器、手、热管理"，Helix 是默认大脑 | [figure.ai/news/figure-03](https://www.figure.ai/news/figure-03)；[The Robot Report 2025-10-09](https://www.therobotreport.com/figure-unveils-figure-03-humanoid-robot/) |
| Helix 家务长视频 | 2025-Q4 ~ 2026-Q1 [uncertain 具体日期] | 折衣服、装洗碗机等长 horizon demo | Figure YouTube channel |
| 2026-05 状态 | 2026-05 | 仍**无 paper / 无权重 / 无 API**；只有官方 blog + 视频 + Adcock 推文 | [unknown — 没找到一手 source 证实任何技术细节更新] |

## 架构核心（按官方 blog + 三方分析）

官方 blog [figure.ai/news/helix](https://www.figure.ai/news/helix) 是**唯一的 primary source**，下面所有结构性陈述都对应到该 blog 的明示段落，凡 blog 没写的一律标 [uncertain] 或 [推测]。

### 1. System 1 / System 2 双频解耦

这是 Helix 设计中**唯一明确说清楚的架构选择**：

- **System 2 (S2) = "the slow thinker"**：一个 **~7B 参数的开源预训练 VLM**[^helix-blog]，吃机器人头部摄像头多视角 + 当前 robot state + 自然语言指令，输出一个**潜在向量（latent vector）**作为"意图编码"。运行频率 **7-9 Hz**。Figure 官方没说具体用的是哪个 7B VLM backbone，外部 [推测] 是 LLaVA / Qwen2-VL / Prismatic 之一，但**官方拒绝确认**[^figure-vlm-base-unknown]。
- **System 1 (S1) = "the fast reactor"**：一个 **80M 参数的 cross-attention transformer**[^helix-blog]，吃 S2 输出的 latent + 同样的视觉输入 + 本体感知（proprioception），输出 35 DoF 连续动作（上半身 + 双臂 + 双手手指 + 头部 + 躯干）。运行频率 **200 Hz**。
- **两者通过 latent vector 解耦**：S2 不直接出动作，S1 不做语义理解。S2 latent 是 S1 cross-attention 的 KV [推测——blog 没说具体注入方式，只说 "communicates with S1 via a latent vector"]。
- **频率比 ~25:1**：blog 明确把这个频率差对应到 Kahneman "Thinking, Fast and Slow" 的认知双系统比喻——S2 抽象规划、S1 实时反射。这个比喻同期也被 Gemini Robotics 1.5 的 "Embodied Reasoning + VLA" 双模型架构采纳（[DeepMind 2025-09 blog](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/)），但 GR 1.5 的"S2"是 ER 模型，体量更大且部分上云。

### 2. 部署：双 embedded GPU on-board

- Helix 完全跑在机器人**机身内** 2 块 embedded low-power GPU 上[^helix-blog]，型号未公开（[推测] Jetson Orin AGX 级别——Figure 03 hardware blog 提了 "low-power embedded GPUs"，没给型号）。
- 这是 Helix 相对 π0 / Gemini Robotics 的主要差异化卖点：**no cloud inference, no internet required**。π0 论文里 inference 也是 on-board，但 Gemini Robotics 的高层 ER 部分要走云端。
- 频率约束的工程合理性：80M @ 200 Hz 在嵌入式 GPU 上是可行的（参考 ACT / Diffusion Policy 同级模型在 RTX-class 上 100-1000 Hz）；7B VLM @ 7-9 Hz 在 Orin 级硬件上**很紧**——这要么意味着 S2 是激进量化（INT4/INT8）+ 短上下文，要么 7B 数字本身可能是 active params 而非总参数 [推测]。

### 3. 单一权重控双机器人协作

- Demo 视频里两台 Figure 02 共享**同一份 Helix 权重**，分别拿到不同子任务指令，协作完成"把购物袋里的杂货放进冰箱"[^helix-blog]。
- blog 的措辞是 "two robots... running the same Helix model weights"，**不是**两台机器人共享 latent 或通信。每台机器人独立做 S2/S1 推理，协作是通过共同观察 + 各自的语言指令对齐实现的 [推测]。
- 没有任何 multi-agent communication channel 被公开提及，所以这更像是"同一策略的两个实例"而非真正的 multi-robot RL。

### 4. 训练数据与方法 [基本全 uncertain]

官方 blog 只给了一个数字：**~500 小时遥操作（teleoperated）数据**[^helix-blog]，号称比同类 VLA 数据集"小一个数量级"。其他：

- 数据采集方式：[uncertain] blog 没说是 VR teleop / exoskeleton / leader-follower；后续 Adcock 推文偶尔提到 Figure 自建数据中心+遥操作团队，但无规模披露。
- 是否用了仿真：[unknown — 没找到一手 source]。
- 训练目标：blog 说 "trained end-to-end, mapping raw pixels and text commands to continuous actions with a standard regression loss"——即**纯回归 (BC behavior cloning)**，**没用 RL**[^helix-blog]。这点和 π0 一致（π0 也是 flow matching + BC），和 Gemini Robotics 系列 [推测] 也一致。
- 是否用 action chunking / diffusion head：[uncertain]。blog 没明说 S1 输出形式；外部 [推测]（[The Robot Report 2025-02-20](https://www.therobotreport.com/figure-debuts-helix-generative-ai-humanoids/)）可能用了类似 ACT 的 chunk regression，但没有 confirmation。
- 是否复用现成 OpenVLA / RT-2 风格的 action token discretization：[unknown]。Helix 的 latent-vector 解耦明显**反对** RT-2 那种"动作当文本 token 出在 VLM 里"的方案——这是和 RT-2 / OpenVLA / Gemini Robotics 早期架构的最大区别。

## 与 eval / benchmark 的接口

**这是 Helix 最薄弱的地方**：

- **没有 quantitative benchmark**。Helix 没在 SimplerEnv、LIBERO、CALVIN、RoboCasa 等公开 VLA benchmark 上报数。
- **没有第三方独立测试**——因为既无权重也无 API。
- 所有"evidence"都是 Figure 自己剪辑的 demo 视频。Lambert ([Interconnects 2025-02-21 "Figure's Helix"](https://www.interconnects.ai/) [uncertain 标题]) 等评论员公开提醒："we have no way to verify generalization beyond the curated demos"。
- The Robot Report 2025-02-20 报道里 Adcock 自己说 Helix 能 "pick up virtually any small household object including thousands of items it has never encountered before"——但**没有 success rate 数字**，没有 held-out 物体清单。
- 对比基线：π0 / π0.5 至少在 paper 里报了 LIBERO、real-world task success rate；Gemini Robotics 报了 ASIMOV benchmark；Helix **零量化数据**。

## 未知与争议

明确没披露的项（截至 2026-05）：

1. **S2 用的具体 7B VLM backbone**——是 Prismatic / LLaVA-OV / Qwen2-VL / 自研，无人知道。
2. **S1 80M 的具体架构**——是 ACT-style transformer? Diffusion Policy? 还是 Figure 自研？
3. **训练数据规模**只有"~500h teleop"一个数字，没有任务多样性、物体数、场景数。
4. **是否用仿真 / 是否用 RL fine-tune** 完全未披露。
5. **embedded GPU 的型号、功耗、推理延迟分解**——没公开。
6. **泛化能力的量化 evidence**——没有任何 held-out test。
7. **Helix 与 Figure 03 硬件的耦合程度**：Figure 03 blog 暗示新一代手 / 触觉传感器是"为 Helix 设计的"，意味着 Helix 在新硬件上**可能用了触觉模态**，但官方未确认 [uncertain]。
8. **2026 年的 Helix 是否还是 2025-02 的同一模型**：Adcock 推文偶尔提到"Helix v2"、"Helix is now much better at X"，但**从未发布版本号或 changelog**——所以"Helix"实际上是一个滚动开发的内部代号，外界看到的永远是当前快照。

外部主要争议：

- **Brooks / Hinton 路线之争**：Rodney Brooks 多次公开质疑"VLA = AGI for robots"叙事（[Brooks blog 2025](https://rodneybrooks.com/)），认为 Helix demo 是 curated cherry-pick，泛化主张缺乏证据。这是对所有 VLA 通用质疑，不针对 Helix 独有。
- **Cherry-pick 嫌疑**：Helix demo 视频里物体摆放、灯光、相机角度高度一致；社区 ([Hacker News 2025-02-20 thread](https://news.ycombinator.com/)) 普遍要求 Figure 公布 success rate 和失败案例，未得到回应。
- **"on-board" 的定义**：有人质疑 7B VLM 在 embedded GPU 上 7 Hz 是否真做 full-precision inference，[推测] 至少是 INT8/INT4 量化 + 短视觉 token，但 Figure 不确认。

## 与同代 VLA 的快速对照

| 维度 | Helix (2025-02) | π0 / π0.5 (PI, 2024-10 / 2025) | Gemini Robotics 1.5 (DM, 2025-09) | RT-2 / OpenVLA (2023-2024) |
|---|---|---|---|---|
| 架构 | S2 7B VLM + S1 80M, latent-vector 解耦 | 单模型 VLM + flow-matching action head | ER (reasoner) + VLA (actor) 双模型 | 动作 token 直接出在 VLM 里 |
| 频率 | S2 7-9 Hz / S1 200 Hz | ~50 Hz action chunk | ER 慢思 + VLA ~10-50 Hz [uncertain] | 1-5 Hz |
| 部署 | 全 on-board, 2× embedded GPU | on-board | ER 部分上云 | 大多上云 |
| 数据 | ~500h teleop（声称） | ~10k h 跨平台 teleop（[π0 paper 表 1](https://arxiv.org/abs/2410.24164)） | DM 内部 + 学术 + Aloha | RT-2 用 Open X-Embodiment |
| paper | **无** | 有 (arxiv) | 有 tech report | 有 |
| 权重 | 闭 | π0 base 权重已开源 ([HF lerobot/pi0](https://huggingface.co/lerobot/pi0)) | 闭 | OpenVLA 开 |
| benchmark 数字 | **无** | 多个 real + sim | ASIMOV | 多个 sim |

**核心 takeaway**：Helix 的 S1/S2 频率解耦架构是合理且影响后续设计（GR 1.5 跟进了类似双模型思路）的真贡献；但 Figure 的**全闭源 + 零 benchmark + demo-only evidence** 模式，使得 Helix 在学术评估意义上**几乎不可引用**——能引用的只有"Figure 声称 X"。对 Qwen 这种做评测/数据的团队，Helix 的可参考性 ≪ π0（有 paper + 开源权重 + 公开数据 mixture 描述）。

## 推荐外部材料

- [figure.ai/news/helix](https://www.figure.ai/news/helix) — 唯一一手 source。读它+看 demo 视频，是了解 Helix 的所有可靠信息上限。
- [Physical Intelligence π0 paper, arxiv:2410.24164](https://arxiv.org/abs/2410.24164) — 同代 VLA 的**正确披露姿势**对照样本，强烈推荐先读这个再回头看 Helix blog 的信息密度差。
- [Gemini Robotics 1.5 blog, DeepMind 2025-09](https://deepmind.google/discover/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/) — ER + VLA 双模型解耦，看大厂版本的 "S2+S1" 怎么落地。
- [The Robot Report Helix coverage 2025-02-20](https://www.therobotreport.com/figure-debuts-helix-generative-ai-humanoids/) — Eugene Demaitre 的报道，是非官方信息里最准确的整理。
- [Nathan Lambert, Interconnects 2025 humanoid posts](https://www.interconnects.ai/) — 对 Helix / Figure / 1X / Tesla Optimus 商业叙事的批判性年度梳理。
- [Sergey Levine talks on generalist robot policies, 2025](https://www.youtube.com/@SergeyLevine) [uncertain 具体讲座] — 学术视角下 VLA 设计权衡（VLM-as-policy vs. VLM-as-conditioner），帮助理解 Helix 选 "latent conditioner" 而非 RT-2 风格 "action-as-token" 的理由。
- [Brett Adcock, X timeline](https://x.com/adcock_brett) — Figure CEO 几乎所有 Helix 更新都先在这里发，但要会过滤 marketing 含量。

---

[^adcock-split]: Brett Adcock, X post, 2025-02-04: "Today, we made the decision to leave our Collaboration Agreement with OpenAI... we made a major breakthrough on fully end-to-end robot AI, built entirely in-house." 14 天后发布 Helix。
[^helix-launch]: Figure AI, "Helix: A Vision-Language-Action Model for Generalist Humanoid Control", 2025-02-20, https://www.figure.ai/news/helix
[^helix-blog]: 同上，blog 正文第 2-4 段。原文："System 2 (S2): An onboard internet-pretrained VLM operating at 7-9 Hz... System 1 (S1): An 80M parameter cross-attention encoder-decoder transformer... operating at 200 Hz." 7B 数字来自 blog 中 "based on a 7B-parameter open-weight VLM"（措辞 [uncertain]——可能是 ~7B；blog 没给精确数）。
[^figure-vlm-base-unknown]: 截至 2026-05，Figure 在所有公开材料里坚持用 "an open-source pretrained VLM" 描述，从未指名具体模型。社区 [推测] LLaVA-OneVision-7B 或 Qwen2-VL-7B 概率最高（两者是 2024 末开源 7B VLM 中 SOTA），但无 confirmation。
