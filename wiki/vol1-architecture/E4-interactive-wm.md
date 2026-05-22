# 交互式 / 游戏 World Model（GameNGen → Oasis → Genie 2/3 → Muse → Mirage 2）

> **范围**：本节覆盖 2024-08 到 2026-05 这条**实时、action-conditioned、neural-rendering** 路线的游戏 / 交互世界模型。和 E2（Sora / Veo / 离线视频生成）的区别是：这里**每一帧都被一个 controller 实时调用**（键鼠 / 手柄 / 触屏），latency 是一等约束，trace 长度（temporal consistency）是核心评测维度。和 E3（机器人 world model，V-JEPA 2-AC / 1X / Cosmos 等）的区别是：本节模型的目标分布是**人类可玩的视觉世界**而不是 robot manipulation latent。读者 = Qwen agentic 评测 owner，熟 diffusion / DiT / video gen 基础。

## 路线定位（1 段）

2024 年下半年起，"用一个 neural net **替代**整个游戏引擎"从 demo 变成了一个有连续 milestone 的子赛道。GameNGen（Google 2024-08）证明 **20 FPS 跑 DOOM** 不需要游戏代码；Oasis（Decart × Etched，2024-10）把它推到 Minecraft 浏览器实时可玩；DeepMind Genie 2（2024-12）第一次给出**单图 → 可玩 3D 世界**且支持 minute 级一致性；Microsoft Muse（Nature 2025-02）是第一篇被 Nature 接收的 game world model 工作（Xbox/Bleeding Edge）；DeepMind **Genie 3**（2025-08）把分辨率推到 720p / 24 FPS 且把可玩时长拉到\"分钟级 + promptable events\"，这是该家族目前的事实 SOTA；Dynamics Lab **Mirage 2**（2025 末–2026 初）把这个范式从游戏扩展到 **user-uploaded image → 实时可玩世界** 的 consumer 产品。这条线的工程意义是：**生成模型第一次同时满足"实时 + 可控 + 长时一致"三角约束**，因此它既是 agentic RL 的潜在 simulator 后端，也是 LLM 评测圈即将面对的一个新 environment 来源（"用 neural world model 当 agent benchmark sandbox"）。

## 代表模型清单

| 模型 / 系统 | 发布日 | 关键变化 | 一手 source |
|---|---|---|---|
| **GameNGen** | 2024-08-27 (arxiv) | 第一个 ≥20 FPS、可交互、单 TPU 跑的 neural game engine；目标游戏 DOOM；human raters 难以区分 short clip | [arxiv:2408.14837](https://arxiv.org/abs/2408.14837)；[项目页](https://gamengen.github.io/) |
| **Oasis** (Decart × Etched) | 2024-10-31 | 首个浏览器内实时可玩的 open-world 生成模型（Minecraft-like）；500M base, 后续到 ~10B；Etched **Sohu** ASIC 推理 | [Decart blog](https://www.decart.ai/articles/oasis-interactive-ai-video-game-model)；[Etched 公告](https://www.etched.com/blog-posts/oasis) |
| **DeepMind Genie 2** | 2024-12-04 | 单张图像 prompt → 可玩 3D 世界；支持 keyboard / mouse；分钟级 memory & consistency；agent (SIMA) 可在其中行动 | [DeepMind blog](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/) |
| **Microsoft Muse** (WHAM) | 2025-02-19 (Nature) | 1.6B; Xbox *Bleeding Edge* 7 年 7 人玩家数据 (~500k 局)；image + controller 双模态；侧重 **divergent / creative** 生成评测，而非单纯保真 | [Nature paper](https://www.nature.com/articles/s41586-025-08600-3)；[MSR blog](https://www.microsoft.com/en-us/research/blog/introducing-muse-our-first-generative-ai-model-designed-for-gameplay-ideation/) |
| **DeepMind Genie 3** | 2025-08-05 | 720p / 24 FPS 实时；多分钟一致性；自然语言 **promptable world events**（实时改变天气、添加 NPC 等） | [DeepMind blog](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) |
| **Dynamics Lab Mirage 2** | 2025-末 / 2026-初 | 消费者产品；用户上传任意图像 → 实时可玩世界；持续在线 demo | [Dynamics Lab](https://www.dynamicslab.ai/) [uncertain — 公司页面与 demo 链接为主，正式 tech report 截至 2026-05 未见 peer reviewed] |
| Pearl / The Matrix / NPC-3D 等社区复现 | 2025 全年陆续 | 多个团队以 GameNGen / Oasis 思路复现到 GTA、CS、其它 first-person 游戏；质量参差 | [unknown — 没有统一一手 source，多为 X / itch.io demo] |
| 2026-05 状态 | — | Genie 3 仍是研究侧 SOTA（未开放公测）；Mirage 2 是 consumer 产品侧 SOTA；**没有 Genie 4 / Muse 2 一手 source** | — |

## 架构核心（按 paper / blog 写的）

四个模型的 architecture 可以放在一个统一的轴上：**(a) backbone = diffusion or autoregressive；(b) action conditioning 怎么注入；(c) 怎么解决 temporal drift / long-horizon consistency**。

### 1. GameNGen — diffusion + RL agent 数据

[arxiv:2408.14837](https://arxiv.org/abs/2408.14837) §3：

- Backbone：**Stable Diffusion 1.4 改造的 image diffusion model**。把 SD v1.4 改成 frame-by-frame generator，每帧 condition 在 **过去 N 帧 latent + 过去 N 个 action**（N=64，约 3 秒上下文）。
- Action conditioning：把 DOOM controller 的离散动作（move / turn / shoot 等）embed 后 concat 到 cross-attention key/value。
- 数据生成：先训练一个 **PPO agent** 在 VizDoom 上玩 ~900M frames，拿到 (state, action, reward, next_state) trajectory，再用这个 trajectory 监督 diffusion model。**整个 dataset 是 agent 玩出来的，不是人类玩出来的**——这是 GameNGen 区分后续工作（Muse 用人类，Oasis / Genie 用 mixed）的关键。
- 解决 drift：**noise augmentation**——训练时对 conditioning frames 加随机噪声并把 noise level 一并作为 condition 输入。inference 时这能把 \"context 已经偏离训练分布\"的影响摊掉，让 trajectory 可以稳定跑数十秒。
- 推理：**单张 TPU v5e ≈ 20 FPS @ 320×240**；4 步 DDIM sampling，配合 LoRA-shrunk decoder。

paper 关键实验：human raters 看 1.6s / 3.2s clip，**对 \"哪个是真 DOOM / 哪个是 GameNGen\" 接近随机猜**。但只在 short clip——长 trajectory 仍有累积漂移。

### 2. Oasis — DiT + 定制硬件

[Decart blog](https://www.decart.ai/articles/oasis-interactive-ai-video-game-model)：

- Backbone：**Diffusion Transformer (DiT)**，500M 起步，后续模型规模到 ~10B [uncertain 具体值，blog 只说 \"scaled\"]。
- 数据：Minecraft 自动播放 + 人类玩家录像 mixed。Decart 没公开数据规模细节。
- Action：键鼠事件 → token，与 visual tokens 串在同一序列由 DiT 处理。
- **关键工程**：在 Etched 的 **Sohu** ASIC 上做推理——Sohu 是\"transformer-only\"加速器，把 attention 与 KV-cache 全部固化电路化，blog 报\"a single Sohu node ≈ 10 H100\" 的等价吞吐 [marketing 数字，未经第三方复现]。这是把 \"实时可玩\" 从\"研究 demo\"推到\"浏览器开放试玩\"的关键。
- 长时一致性问题：Oasis 早期 demo 也有显著 drift——走两步回头世界变了。这是该家族**所有 model 共同的未解问题**直到 Genie 3。

### 3. DeepMind Genie 2 / Genie 3

[Genie 2 blog](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/)：

- 定位：**foundation world model**——区别于上面 2 个的\"单一游戏 specialist\"，Genie 2 训练分布是大规模 internet video，主张 \"a single model that can generate an endless variety of action-controllable, playable 3D environments\"。
- Architecture：**autoregressive latent diffusion**——先把 video frames token 化（learned tokenizer），再用 transformer 自回归预测下一帧 latent，最后 latent decoder 解码到 pixel。
- Action：键盘/鼠标输入也 token 化，和 video tokens 同一 sequence；blog 强调\"模型自己学会了 \\<action\\> → 一致 3D 视角变化\"，包括\"first/third person\"、\"水的物理\"、\"NPC 行为\"。
- 一致性：blog 报\"up to a minute\" 的 memory——视角离开再回来物体大致保留。这是 GameNGen / Oasis 当时做不到的。Genie 2 没披露具体技术，但学界普遍认为是 **(a) tokenizer 引入 spatial structure + (b) 长 context window + (c) 训练目标包含\"go-back-and-look\" 类增广**[推测]。
- 算力 / 模型规模 / 数据：**未披露**。
- 已知用法：DeepMind 同时披露 **SIMA agent 可以在 Genie 2 生成的环境里行动**——这是**用一个 neural world model 当 RL training ground** 的最早公开 demo 之一。

[Genie 3 blog](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) 是这条线**目前的事实 SOTA**：

- **720p / 24 FPS** 实时（Genie 2 是 360p / 帧率未明示）；
- 一致性\"a few minutes\"（vs Genie 2 \"up to a minute\"）；
- **Promptable world events**：跑动过程中可以打字\"start raining\" / \"add a deer\"，模型在不重置 trajectory 的情况下注入这个事件——blog 强调这是 \"world model 第一次真正可被自然语言交互式编辑\"，不是 prompt-then-generate；
- **agent 同框**：DeepMind 同期 demo SIMA-2 在 Genie 3 世界里完成 navigation / object interaction 任务，这是**第一次正式把\"neural world model + 通用 agent\"打通**作为一个 product 级演示；
- 仍 closed model、未开放 API（截至 2026-05）。

### 4. Microsoft Muse (WHAM) — Nature 的版本

[Nature paper](https://www.nature.com/articles/s41586-025-08600-3) + [MSR blog](https://www.microsoft.com/en-us/research/blog/introducing-muse-our-first-generative-ai-model-designed-for-gameplay-ideation/)：

- 名字：内部 codename **WHAM (World and Human Action Model)**，对外品牌 **Muse**。
- 数据：**Bleeding Edge** 单一 Xbox 游戏，7 人玩家、7 年累计 ~500k matches、~1B controller actions、~7 年游戏时间。这是迄今 **action-conditioned video model 用过最干净的真人 controller 数据集**。
- 模型：**1.6B decoder-only transformer**；image patches + controller actions 串成一个统一 token sequence (VQ-VAE 编码图像)；标准 next-token prediction。
- 三个能力 axis（Nature paper §3）：**consistency / diversity / persistency**——和 Genie 3 的"长时一致"不同，Muse 的 paper 主张评测维度应该是 \"生成的 trajectory 是否在游戏机制上 plausible\"，并提出 \"creative-use score\" 让设计师评判生成内容的**多样性而非保真度**。
- 定位差异：Microsoft 把 Muse **定位为 \"gameplay ideation tool\"**，不是 \"replace game engine\"——这与 DeepMind Genie / Decart Oasis 的\"取代渲染管线\"叙事不一样。这点对评测圈很关键：Muse 是\"design tool\"，Genie 是\"environment\"。
- 开放性：weights + 部分 data 在 Azure AI Foundry 释放（Muse 是该列表里**唯一在 Nature 发表并部分开权重**的）。

### 5. Dynamics Lab Mirage 2

公开材料 [Dynamics Lab 官网](https://www.dynamicslab.ai/)：

- Consumer product：上传任意图像 → 实时浏览器内可玩世界；强调 \"any image → playable\"；
- 技术细节**几乎完全未披露**——没有 paper、没有 model card。从公开 demo 看，分辨率 / 帧率介于 Oasis 与 Genie 3 之间 [uncertain]；
- 商业模式：B2C 试玩 + B2B \"world-as-API\"；
- 截至 2026-05，**Mirage 2 是这条家族里第一个走完\"消费者使用→订阅付费\"闭环**的产品 (Oasis 是免费 demo)。技术领先性低于 Genie 3，但**产品化领先**。

## 训练方法核心（横向比较）

| 维度 | GameNGen | Oasis | Genie 2/3 | Muse |
|---|---|---|---|---|
| backbone | image diffusion (SD-style) | DiT | autoregressive latent diffusion | decoder-only transformer (next-token) |
| 数据来源 | RL agent 自玩 | mixed (auto + human) [uncertain] | 大规模 internet video [推测] | 单游戏 7 年人类数据 |
| 数据量 | ~900M frames | 未披露 | 未披露 | ~1B actions / 500k matches |
| action 注入 | cross-attn key/value | token concat | token concat | token concat |
| 训练 loss | denoising | denoising | next-latent-token | next-token (VQ patches) |
| 长时一致 trick | noise augmentation on context | 未披露 | tokenizer + long context [推测] | 长 sequence + 大数据 |
| 分辨率 / 帧率 | 320×240 / 20 FPS | 浏览器实时 / ~20 FPS [uncertain] | 720p / 24 FPS (G3) | 300×180 / 10 FPS (paper) |
| 推理硬件 | 1× TPU v5e | Etched Sohu ASIC | 未披露 (TPU 推测) | 未披露 |

几个 cross-cutting observation：

1. **GameNGen 的 noise augmentation 是这条线的核心 trick**，被后续多家复用 / 重发明——任何 action-conditioned video 生成只要做\"自回归推 next frame\"，都必须处理\"训练分布 = clean context / 推理分布 = self-generated context\"的 distribution shift，noise augmentation 是最便宜的解法。
2. **数据规模 ≠ 体验质量**：Muse 用了 \"1B action\" 级数据但分辨率 / 帧率最低；Genie 系列数据规模没披露但产品体验最好——说明 **architecture + tokenizer + 训练目标**对该任务的回报可能高于纯数据 scaling。
3. **\"用谁的数据\"是评测圈最容易被忽视的轴**：
   - GameNGen：RL agent → 生成分布偏 \"机器最优策略\"，覆盖人类罕见 trajectory 少；
   - Muse：真人玩家 → 长尾覆盖好，但 7 人样本社会化偏差；
   - Genie 3：internet video → 覆盖最广但 action label 来自哪里 [unknown，blog 没说明]。
4. **算力披露程度极差**——这 5 家**没有一家明列 GPU/TPU-hour**。这是该方向当前的信息不对称重灾区。

## 与 eval / benchmark 的接口

- **GameNGen**：human A/B (1.6s / 3.2s clip)、PSNR、LPIPS。这套 benchmark **过短**，不能衡量 long-horizon。
- **Muse**：Nature paper 自己提出 \"consistency / diversity / persistency\" 三轴评测——这是该家族**第一个被同行评议的评测协议**，建议 Qwen 评测组关注，原因是它把 \"creative gameplay generation\" 与 \"frame-level 保真\" 解耦。
- **Genie 2/3**：blog 只展示 video demo + qualitative description，**没有定量 benchmark 公开**。这是 DeepMind 在 video / world model 领域一贯的 \"trust the videos\" 风格，第三方无法定量复现或对比。
- **第三方评测/复现**：
  - 学界尚无统一 \"interactive world model benchmark\"。社区 (HuggingFace、X) 偶有把 GameNGen / Oasis / Genie demo 放在一起做 side-by-side 的非正式对比；
  - 一个新兴方向是 **\"用 LLM agent 在 neural world model 里跑 task → 看 success rate\"**——SIMA-2 × Genie 3 是 DeepMind 自己的版本；学界等价物 [unknown]。

### 与 LLM agent / RL 评测的潜在融合

对 Qwen agentic eval 组的直接 relevance：

1. **作为 RL environment**：如果 neural world model 能跑 ≥30 FPS 且 horizon 足够长，它可以**替代部分 game emulator / sim engine 作为 RL rollout 后端**。这条路的瓶颈不是 quality 而是**reproducibility**——同样 action sequence 必须给同样 trajectory，目前几个 model 都是 stochastic，**不可重放**。这是一个 RL 评测的硬伤，blog/paper 均未讨论。
2. **作为 agent benchmark sandbox**：用 Genie 3 类模型给 LLM agent 出\"无穷多新的 first-person 任务\"是一个被多方提及的设想（DeepMind blog 暗示，OpenAI / Anthropic 未公开表态）。但 \"world model 自己也会幻觉\" 让 benchmark 信号污染——任务失败到底是 agent 失败还是 world model 帮倒忙，**几乎无法解耦**。这是评测设计的开放问题。
3. **可控性 vs 一致性的 tradeoff**：Genie 3 的 promptable events 实际上**牺牲了部分一致性**（事件注入瞬间会引起 trajectory 不连续）。任何想拿这类模型做 agent eval 的实验设计都得显式声明 \"是否启用 promptable events\"。

## 未知与争议

明确未披露（截至 2026-05）：

1. **Genie 2 / 3 的模型规模、训练数据规模、训练算力** —— DeepMind 一律未披露。
2. **Genie 系列的 action label 来源** —— internet video 通常没有 controller action ground truth，DeepMind 必然有一个 \"action labeler\" 或 inverse dynamics model，**完全没公开**。
3. **Oasis 的数据规模、Sohu ASIC 的真实 FLOPs / 能效** —— 都是 marketing 数字，无第三方复现。
4. **Mirage 2 的全部技术细节** —— 没有 tech report。
5. **是否有 \"Muse 2\" / \"Genie 4\" / 类似的下一代** —— 截至 2026-05 **没有一手 source**。
6. **真实 long-horizon (>5min) 一致性数据** —— Genie 3 blog 给的是\"a few minutes\"，没有定量误差累积曲线。

主要争议：

- **\"neural game engine 是否会替代传统引擎\"**：业内分裂明显。Carmack / 一些游戏工程师认为 deterministic + 可编辑性是不可放弃的 (neural engine 都做不到)；DeepMind / Decart 主张\"长尾内容生成成本 → 0\" 的革命性会压倒。两边都没决定性证据。
- **算力效率**：GameNGen 用 1 块 TPU 跑 DOOM；Genie 3 跑 720p 需要的资源量级\"显著高于消费级\" [推测] 但具体多少 unknown。如果一个用户 session 需要专用 GPU/TPU，consumer 经济性存疑——Mirage 2 实际运行成本是这条 line 未来 12 个月的关键检验点。
- **\"world model for agent\"叙事的兑现**：SIMA × Genie 3 demo 是首次公开 closed-loop，但**SIMA 是 DeepMind 自家 agent，Genie 是 DeepMind 自家 world model**——一切都是同公司内部产物，**没有第三方 agent 在 Genie 上跑 benchmark 的可复现 paper**。这和 V-JEPA 2-AC robot demo 的处境类似（见 [E1-jepa.md](./E1-jepa.md)）：叙事先行，第三方验证缺位。
- **数据合法性**：用 internet video 训练 game world model 会复刻 video 中可识别游戏的 visual style——任天堂 / 索尼等 IP 持有者**几乎一定会有 lawsuit 来**。这是该方向 2026 年下半年最可能的外部冲击。

## 与 E2 (Sora/Veo)、E3 (robot world model) 的边界

| 维度 | E2 离线 video gen | **E4 交互式 game WM (本节)** | E3 robot WM (V-JEPA 2-AC / Cosmos / 1X) |
|---|---|---|---|
| 是否实时 | 否 | **是 (>20 FPS)** | 通常否 (planning 用) |
| 输入 | text / image prompt | **每帧 controller action** | robot proprioception + action |
| 输出 | 数秒 ~ 1 分钟 video | **无限延伸 trajectory** | latent state 或视频，用于 MPC |
| 评测 focus | 单 clip 视觉质量 | **trajectory 一致性 + 可控性** | downstream task success |
| 主要 user | 内容创作者 | **玩家 / agent / 游戏设计师** | 机器人 + RL agent |

这三条线**底层 architecture 在收敛**（都在用 DiT-style 或 latent autoregressive），分化点在**约束三角：实时 / 长一致 / 可控**哪个被牺牲。E4 是三者都不能放弃的最难子集。

## 推荐外部材料

- [GameNGen paper, arxiv:2408.14837](https://arxiv.org/abs/2408.14837) — 这条线的奠基论文，noise augmentation trick 必读。
- [GameNGen 项目页 (含视频)](https://gamengen.github.io/) — paper 看完一定要看视频感受 latency。
- [DeepMind Genie 2 blog (2024-12)](https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/) — 第一次提出 \"foundation world model\" framing。
- [DeepMind Genie 3 blog (2025-08)](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) — 目前该家族 SOTA，promptable events 是质变。
- [Muse / WHAM Nature paper (2025-02)](https://www.nature.com/articles/s41586-025-08600-3) — 唯一同行评议的 evaluation framework (consistency/diversity/persistency)；评测组直接可参考。
- [MSR Muse blog](https://www.microsoft.com/en-us/research/blog/introducing-muse-our-first-generative-ai-model-designed-for-gameplay-ideation/) — 含 Azure 上的开放权重链接。
- [Decart Oasis blog](https://www.decart.ai/articles/oasis-interactive-ai-video-game-model) + [Etched Sohu blog](https://www.etched.com/blog-posts/oasis) — 软硬协同视角，理解\"为什么需要专用推理硬件才能 consumer 化\"。
- [Jim Fan twitter 关于 Genie 3 + SIMA 的解读](https://twitter.com/DrJimFan) — Nvidia GEAR lead 长期 narrate world model + embodied agent 的融合视角，比较中立。
- [Sander Dieleman, \"Generative modelling in latent space\" (2025)](https://sander.ai/2025/04/15/latents.html) — 解释为什么 game WM 普遍走 latent diffusion / latent AR，理解架构选型动机。

---

[^gamengen]: Valevski et al., \"Diffusion Models Are Real-Time Game Engines\", arxiv:2408.14837, 2024-08。§3 architecture, §4 noise augmentation, §5 human eval。
[^genie3]: DeepMind, \"Genie 3: A new frontier for world models\", 2025-08-05, https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/。720p/24FPS、promptable events、SIMA-2 集成均出自该 blog。
[^muse]: Kanervisto et al., \"World and Human Action Models towards gameplay ideation\", Nature 638, 2025-02。1.6B model, Bleeding Edge dataset, consistency/diversity/persistency 评测。
[^oasis]: Decart & Etched, \"Oasis: A Universe in a Transformer\", 2024-10-31, https://www.decart.ai/articles/oasis-interactive-ai-video-game-model 与 https://www.etched.com/blog-posts/oasis。
