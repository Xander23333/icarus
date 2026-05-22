# 空间 / 3D World Model（World Labs Marble · Odyssey · Wayve GAIA-2 · Niantic Spatial）

> **范围**：本节聚焦**显式带几何**（3D Gaussian splat / mesh / NeRF / occupancy / 显式 pose 与 metric）的 world model，时间窗口至 2026-05。和 [E3 video-as-WM](./E3-video-as-wm.md)（Sora / Veo / Cosmos 类纯 pixel autoregressor）的根本区别是：**这里的 latent 不是 frame，而是 scene**——给定视角变化要能给出几何一致的多视图，而不是\"再生成一段相关 video\"。和 [E4 交互式 game WM](./E4-interactive-wm.md)（Genie 3、Oasis、Mirage 2）的区别是：E4 的 \"3D-ness\" 是模型隐式涌现的（无 explicit 几何，靠 token 一致性维持），本节模型则**显式输出可用的 3D 表示**（splat / mesh / camera pose），下游可直接接传统 renderer、SLAM、地图、driving stack。读者 = Qwen agentic eval owner，熟 diffusion / VLM，但对 3DGS / NeRF / SLAM 不一定深入，所以下文会带必要 1 句术语。

## 路线定位（1 段）

如果说 E4 想用 neural net 替代 game engine，本节这条线想替代的是**地图 + 摄影测量 + 场景重建 pipeline**。2024 下半年起，三条子分支同时起飞：(1) **scene-generation 派**——Fei-Fei Li 创办的 World Labs 2024-09 浮出水面，2025 末发布消费者产品 **Marble**，主张\"single image → persistent navigable 3D world\"；同期 Odyssey 从自驾出身转向 \"interactive video × 3D\" 路线。(2) **驾驶 world model 派**——Wayve **GAIA-2**（2025-03）是这条线公开 tech report 最厚的代表，把 multi-camera + ego action + 语义条件统一在一个 latent diffusion 里，定位是自驾的 closed-loop simulator。(3) **真实世界先验派**——Niantic 2024-11 公开 **Large Geospatial Model (LGM)** 设想，2025 年把 AR/地图 business 拆分为 **Niantic Spatial**，把 Pokémon GO / Ingress 多年扫描出的 **Lightship VPS** 数据 (~10M+ scanned locations) 当作 \"geospatial foundation model\" 的 pretraining corpus；这是\"空间 WM\"里**唯一**自带 city-scale 真值的玩家。三条线的共同信念：**视频 token autoregressor 没有 geometry inductive bias，等于在每一帧重新发明 3D**，scale 再大也低效；显式 3D 表示 + neural prior 才是空间智能的正确底座。这条赌注是否成立将在 2026-2027 与 Sora / Veo / Genie 类纯 video WM 的产品对撞中见分晓。

## 代表系统清单

| 系统 | 发布日 | 输出表示 | 关键变化 | 一手 source |
|---|---|---|---|---|
| **World Labs (stealth → 公开)** | 2024-09-13 公司亮相 | 3D scene (内部) | Fei-Fei Li + Justin Johnson + Christoph Lassner + Ben Mildenhall (NeRF 一作) 联合创办；\"Large World Models / spatial intelligence\" framing | [worldlabs.ai about](https://www.worldlabs.ai/about)；[Fei-Fei 公告 medium/twitter](https://www.worldlabs.ai/blog) |
| **World Labs first demo** | 2024-12-02 | 可在浏览器漫游的 3D scene from single image | 单图 → 持久 3D 环境，浏览器内 WASD 漫游；明确声明\"生成的是 3D 不是 video\" | [worldlabs.ai blog 2024-12](https://www.worldlabs.ai/blog/generating-worlds) |
| **World Labs Marble** | 2025-末 [uncertain — 具体日期取决于读者拿到的 worldlabs blog 时间戳] | 3D Gaussian splat 类表示 [推测] | 第一个 consumer 产品；image / text → 可导出 splat 的 3D 世界；定位 \"world building tool\" | [worldlabs.ai/marble](https://www.worldlabs.ai) [uncertain — 截至 2026-05 官方页面持续迭代，未见 peer-reviewed paper] |
| **Odyssey Explorer / Odyssey-2** | 2024-2025 多次迭代 | interactive video + 3D Gaussian splat | 早期是 photorealistic 3D scene gen；2025 转向 \"interactive video model\"（输入 prompt → 实时可控视频），与 E4 路线模糊重叠但仍主打\"underlying 3D representation\" | [odyssey.systems](https://odyssey.systems/)；[Odyssey blog: explorer](https://odyssey.systems/introducing-explorer) |
| **Wayve GAIA-1** | 2023-09 (arxiv) | 多视角驾驶 video | 9B；driving WM 第一代，纯 video | [arxiv:2309.17080](https://arxiv.org/abs/2309.17080) |
| **Wayve GAIA-2** | 2025-03-26 | multi-camera driving video + 显式 ego/scene 条件 | latent diffusion；5 camera 同步；ego action、road layout、weather、time of day 全部 conditional；2025 driving WM 的事实参考实现 | [Wayve blog GAIA-2](https://wayve.ai/thinking/gaia-2/)；[tech report PDF](https://wayve.ai/wp-content/uploads/2025/03/GAIA-2.pdf) |
| **Niantic Large Geospatial Model (LGM)** | 2024-11-12 公告 | 隐式几何先验 (vision foundation model) | 用 Lightship VPS 累计 ~10M+ 扫描点 / 数十亿图像训练 \"geospatial foundation model\"，目标 \"locally grounded, globally generalizing\" | [Niantic blog LGM](https://nianticlabs.com/news/largegeospatialmodel) |
| **Niantic Spatial (公司)** | 2025-03 spin-off | — | Niantic 把 Pokémon GO / Monster Hunter Now 等游戏 IP 出售给 Scopely，剩下的 AR / mapping / LGM 业务独立为 **Niantic Spatial Inc.**；融资 + 转 B2B AR 平台 | [Niantic 公告 2025-03](https://nianticlabs.com/news/niantic-spatial) |
| **Lightship VPS (持续运营)** | 2022 起 | 城市级 6-DoF localization | >1M public locations、>10M scans 累计 [uncertain — 数字以 Niantic 最新发布为准] | [lightship.dev/vps](https://lightship.dev/products/visual-positioning-system/) |
| 周边参照：CAT4D、Cosmos-1 spatial、DUSt3R / MASt3R、Splat-VLM | 2024-2025 | 各异 | 学界 / 其它玩家在\"feed-forward 3D\" 这条线上的快速跟进 | [CAT4D arxiv:2411.18613](https://arxiv.org/abs/2411.18613)；[MASt3R arxiv:2406.09756](https://arxiv.org/abs/2406.09756) |
| 2026-05 状态 | — | — | World Labs Marble 是 consumer 侧最显眼产品；GAIA-2 是垂类 (driving) 最完整 tech report；Niantic Spatial / LGM 仍是\"宣布了但没放 weights / 没放 paper\"的最大期权 | — |

## 架构核心（按 paper / blog 写的）

### 1. World Labs — \"single image → persistent 3D\"

公司层面的 thesis 由 Fei-Fei Li 在 [World Labs blog](https://www.worldlabs.ai/blog) 与多次访谈中表述：**Large World Model (LWM)** 是和 LLM 平行的另一类 foundation model，输入 / 输出是\"world\"，不是 token 也不是 frame。技术细节披露**很少**，公开能确认的：

- **2024-12 demo**：单张图 → 浏览器里**自由 WASD 漫游**的小型 3D 场景，**视角离开再回来对象保持**——这是 distinguishing feature vs Sora。blog 明确写 \"the output is a real 3D scene, not a video\" [^worldlabs-dec24]。
- 输出表示**未明示**，业界从 demo 表现推测是 **3D Gaussian splat 或类似 explicit 场景表示**[推测]——理由：(a) 帧率高 & 视角自由说明不是 per-view neural render；(b) demo 中明显的\"边缘伪影 / 远处糊\"是 3DGS 的典型 artifact。
- **Marble**：2025 末发布的 consumer 产品。worldlabs.ai 官网定位为 \"world model for creators\"，支持 image-to-world / text-to-world，可导出 splat 或类似 asset [^worldlabs-marble]。**官方没发 paper，没披露模型规模、训练数据规模、训练算力**——这是这家公司目前的 information asymmetry。
- 团队信号强：Justin Johnson (Stanford → World Labs CTO) + Ben Mildenhall (NeRF 一作) + Christoph Lassner (Pulsar / 3DGS 早期工程) 同时在，**这个组合的 prior 几乎必然是 \"learned 3D representation + diffusion-style prior over 3D\"**[推测 / 基于成员历史 paper]。
- 与 E4 的边界：World Labs 反复强调\"我们不是做 video\"。但从 user 体验看，Marble 与 Genie 3 / Mirage 2 在 consumer 端**会被直接比较**——\"我能不能在里面跑动 / 互动 / 改东西\"。**Marble 当前的弱项是 dynamics**（场景是静态 / 准静态的），Genie 系列弱项是**几何可导出性**。两者会逐步互相蚕食对方的弱项。

### 2. Odyssey — 从 photorealistic 3D 到 \"interactive video\"

[odyssey.systems](https://odyssey.systems/) 的产品定位经历过明显转向：

- 早期 (~2024)：photorealistic 3D scene generation，目标是给影视 / 游戏供 asset；强调 underlying mesh / splat 可导出。
- **Explorer** (2025)：\"interactive video model\"，输入 text / image，输出可实时控制视角的 video stream。和 Genie 系列的 framing 几乎一致，但 Odyssey blog [^odyssey-explorer] 反复强调\"模型内部有 3D structure\"——具体什么结构没公开。
- 2026-05 状态：**没有 peer-reviewed paper，没有 tech report**。所有 \"3D-ness\" 主张靠 demo video 自证。这是 Odyssey 与 World Labs 共同的问题——**\"我们是 3D 不是 video\" 这个 claim 在没有 explicit 3D 输出 API 的情况下不可证伪**。

如果 Qwen 评测组要参考 Odyssey，**只能依赖产品级 hands-on**，不要用 blog 数字。

### 3. Wayve GAIA-2 — 垂类最完整 tech report

[GAIA-2 tech report](https://wayve.ai/wp-content/uploads/2025/03/GAIA-2.pdf) §3-4：

- **任务**：driving world model—给定历史多视角图像 + 未来 ego action（方向盘 / 油门 / 刹车）→ 生成未来若干秒的多视角 driving video，作为自驾 stack 的 closed-loop simulator。
- **Architecture**：**latent diffusion**。两阶段：
  1. **Video tokenizer**：把 5 路 camera × T 帧压缩到 spatio-temporal latent；continuous latent (不是 VQ)。
  2. **World model**：在 latent 上做 **conditional diffusion**，条件包括：past video latents、ego action sequence、相机 pose、HD map / road layout、weather、time-of-day、country—**全部都是显式 condition**，不是 prompt。
- **5 camera 同步**：这是 GAIA-2 与单视角 video model 的根本区别。模型在 attention 层做 cross-view 一致性，保证生成的 5 路视频在几何上对齐（同一辆车在前置和侧置相机里位置合理）。这是\"显式空间一致\"在 driving 这个垂类的具体实现。
- **数据**：Wayve 自己车队 + 合作伙伴在英 / 美 / 德等地路采的数据；规模未具体披露 \"thousands of hours\"。
- **训练**：tech report 报 ~8.4B 参数，多阶段训练 + classifier-free guidance 用于条件强度调节。
- **Eval**：FID / FVD (perceptual)、**多视角几何一致性 metric**、condition adherence（让它生成 \"夜间 + 雨 + 转向\" 看是否服从）、**ego action controllability**（开环 vs 闭环）。这是该家族里**唯一系统化的定量评测协议**，结构上和 Muse 的 consistency/diversity/persistency 类似但维度不同。
- 与本节其它系统的差异：GAIA-2 **不直接输出 3D 几何**（没 splat / 没 depth）；它的\"空间性\"体现在**显式 ego pose + 多 camera 同步 + 地图条件**——这是一种\"行为级\" spatial WM，而 World Labs / Odyssey 是\"表征级\" spatial WM。这两条思路在 driving 子领域**有可能合并**（已有 Cosmos / Nvidia 的 Drive 类工作在尝试 splat-based driving WM），但 2026-05 还没有统一胜者。

### 4. Niantic Spatial / Lightship VPS / Large Geospatial Model

Niantic 这条线**严格说不是 generative world model**，而是\"空间先验 foundation model + 真实世界 localization\"。但它和 World Labs / Odyssey 在 consumer + 长期市场上**正面竞争**，所以放在本节：

- [Lightship VPS](https://lightship.dev/products/visual-positioning-system/)：基于 Pokémon GO / Ingress 多年 \"wayspot\" 用户扫描积累的视觉定位服务。给一张手机照片 → 输出 6-DoF 位姿（精度 cm 级 in 已扫描地点）。截至 2024 年 Niantic 公告称已覆盖 >1M public locations，数十亿张图像；这是**消费级移动设备能用上的、规模最大的 city-scale 视觉地图**。
- [LGM blog 2024-11](https://nianticlabs.com/news/largegeospatialmodel)：Niantic 提出 \"我们要做 Large Geospatial Model\"，论点是\"局部 3D 重建已经被 NeRF/3DGS 解决了，下一步是 **跨地点泛化**——看到从未扫描过的新街道也能推理出合理几何\"。technical details 极少；可以理解为 \"vision foundation model with geometry-aware pretraining objectives, trained on Lightship\"。
- **2025-03 拆分**：Niantic 把游戏业务 ~$3.5B 卖给 Scopely，AR / mapping / LGM 业务独立为 [Niantic Spatial Inc.](https://nianticlabs.com/news/niantic-spatial)，定位 B2B 空间计算平台。这意味着 LGM 项目**从游戏的副产品变成主营业务**——值得长期追踪。
- 与 World Labs 的差异是根本性的：World Labs 训练\"如何**生成**一个 plausible world\"，Niantic 训练\"如何**识别 / 定位**真实 world\"。前者擅长 hallucinate 不存在的地方，后者擅长把 robot / phone / AR 设备**锚定到真实地球坐标系**。两者长期会**互补**——下游 spatial agent 既需要 \"想象未见地方\" 也需要 \"在真实地方找路\"。

## 训练方法核心（横向比较）

| 维度 | World Labs / Marble | Odyssey Explorer | Wayve GAIA-2 | Niantic LGM |
|---|---|---|---|---|
| 输出 | 3D scene (splat 推测) | interactive video (+\"内部 3D\") | 多视角 driving video | localization / 几何先验 |
| backbone | 未披露 (diffusion-based 推测) | 未披露 | latent diffusion (8.4B) | vision FM (未披露) |
| 数据 | 未披露 | 未披露 | 自驾路采 thousands of hr | Lightship 用户扫描 ~10M+ 点 |
| 条件 | image / text | text / image | ego action + map + weather + camera | 图像 → 位姿 |
| 是否实时 | 浏览器漫游 (静态 scene 渲染) | 是 | 否（offline 模拟用） | 是（手机 ms 级） |
| 几何 ground truth | 无 | 无 | ego pose / map | Lightship 真值 |
| 算力 / 规模披露 | **无** | **无** | 部分 (8.4B) | **无** |

观察：

1. **\"几何 ground truth 在哪里\"是这条线的核心分水岭**。GAIA-2 有 ego pose 与 HD map 作为强 supervision；Niantic 有 Lightship scan 作为真值；World Labs / Odyssey 走 \"image-only self-supervised 3D learning\" 路线（应该是从 [DUSt3R](https://arxiv.org/abs/2312.14132) / [MASt3R](https://arxiv.org/abs/2406.09756) 这条 feed-forward 3D reconstruction 学界路线拓展出来的）[推测]。
2. **披露程度极差**比 E4 还严重：World Labs 至今**零 paper**，Odyssey **零 paper**，Niantic LGM **零 paper**。GAIA-2 是该家族**唯一一份完整 tech report**——所以本节实际可考的硬技术内容大头在 GAIA-2。
3. **垂类 WM 比通用 spatial WM 商业兑现快**：Wayve GAIA-2 已经在内部 closed-loop 训自家 driver agent；Niantic Lightship 已经是付费 API；World Labs / Odyssey 还在 \"找 product-market fit\" 阶段。这与 E4 的现状相反（E4 通用的 Genie 3 反而比垂类更亮眼）。
4. **未见 RL post-training**：本节四家**都没有公开 RL / preference learning 后处理**。这与 E1-E4 的 robot WM、game WM 形成对比——空间 WM 目前还是纯 supervised generative 学习。

## 与 eval / benchmark 的接口

- **World Labs Marble**：**无公开定量 benchmark**。可参考的代理 benchmark 是学界 feed-forward 3D recon 圈的 [DTU](https://roboimagedata.compute.dtu.dk/) / [Mip-NeRF 360](https://jonbarron.info/mipnerf360/) 上的 PSNR/SSIM/LPIPS——但 Marble 是 generative 不是 reconstructive，对应不上。**唯一可用的评测维度是\"single image → 漫游一致性\"的 user study**，目前无标准化协议。
- **Odyssey**：同上，**无定量 benchmark 可参考**。
- **Wayve GAIA-2**：tech report 自报多维 metric (FID / FVD / 多视角一致 / action controllability)，但**数据集 closed**，第三方无法复现。学界对照参考是 [nuScenes](https://www.nuscenes.org/) / [Waymo Open Dataset](https://waymo.com/open/) 上的 driving video gen benchmark；学界工作（如 DriveDreamer、MagicDrive、Vista）在这些公开 dataset 上对比，但**Wayve 的 8.4B 模型从未在公开 set 上比过**——典型\"自家数据自家最好\"叙事。
- **Niantic LGM**：**没有任何定量 release**。Lightship VPS 自己有内部 localization 准确率指标（米 / cm 级 recall），但 LGM 作为 foundation model 的 evaluation 没公开。
- **学界对照参考**（如果 Qwen 评测组要建立 spatial WM benchmark）：
  - **Feed-forward 3D recon 端**：DUSt3R / MASt3R / Splatt3R / NoPoSplat 系列，benchmark = DTU / RealEstate10K novel-view PSNR。
  - **Scene generation 端**：CAT4D、ReconX、ViewCrafter 等学术工作，benchmark = LPIPS + multi-view consistency。
  - **Driving 端**：nuScenes + nuPlan + CARLA closed-loop。
  - **Mapping 端**：Lightship-类竞品有 Google Geospatial API、Snap Spectacles 用的 [Snap LGM 等价物 — uncertain]。

### 对 Qwen agentic eval 的直接 relevance

1. **spatial WM 是 agent benchmark 的 \"环境一致性保证\"**：当用 Genie 3 / Mirage 2 类 neural environment 跑 agent，最大问题是 \"world model 自己产生 hallucination\"（E4 已讨论）。如果 environment 自带显式 3D 表示（Marble / GAIA-2 路线），**agent 决策对应的物理几何是固定的**，benchmark 信号干净——这是空间 WM 对 agent eval 最大的潜在贡献。
2. **\"localization in generated world\" 是一类新评测**：把 agent 放进 Marble 生成的 scene，让它解 \"找到红色门\" / \"导航到房间 B\" 等任务，可同时考察 (a) VLM perception、(b) spatial reasoning、(c) tool use（如果允许调用 SLAM tool）。截至 2026-05 **无公开此类 benchmark**——一个空白机会。
3. **driving WM 是 RL 评测最现实的工业级 sandbox**：GAIA-2 已经在 Wayve 内部当 RL training environment；如果 Wayve 放开 API，将是 Qwen 类 agent eval 圈的现成 closed-loop env。**但目前 closed**。
4. **不要相信 \"我们的输出是 3D\" 的口头声明**：评测设计上要求**模型 expose 一个可被传统 3D tool 消费的输出**（splat .ply / mesh .obj / depth map），并用 SfM / MVS pipeline 独立校核。这是当前唯一可证伪 \"3D vs video\" 的方法。

## 未知与争议

明确未披露（截至 2026-05）：

1. **World Labs / Marble 的模型规模、训练数据、训练算力、内部表示** —— 全部 unknown。**没有任何 paper**。
2. **Odyssey 的模型 / 训练细节** —— 全部 unknown。
3. **Niantic LGM 的架构 / 训练目标 / 模型规模 / 是否已上线生产** —— 全部 unknown，仅有 2024-11 blog 一篇。
4. **GAIA-2 的数据集组成 / 多少小时 / 多少 km** —— tech report 仅 qualitative \"thousands of hours\"。
5. **统一 spatial WM benchmark** —— 学界 / 业界都没有，这是 2026-2027 最可能补齐的一块。

主要争议：

- **\"显式 3D vs 隐式 3D\" 路线之争**：World Labs / Niantic 阵营主张几何 inductive bias 不可省，否则 scale 浪费；Sora / Genie / Veo 阵营赌 \"video token scale 足够大就涌现几何\"。两边都没决定性证据。Genie 3 的 \"a few minutes\" 一致性是隐式派的最强证据；Marble 的 \"single image → 持久漫游\" 是显式派的最强证据。**这场赌注预计 2026-2027 见分晓**。
- **\"是不是真 3D\" 的可证伪性**：World Labs / Odyssey 都未提供 splat / mesh / depth 的 standard 导出格式（截至 2026-05），用户无法独立用 Blender / Unity / Open3D 验证几何质量。这导致**所有 \"我们是 3D\" 的 marketing claim 在第三方视角下不可证伪**——这是该方向 credibility 的最大空洞。Marble 是否在 GA 时提供导出 API 是关键检验点。
- **数据合法性**：World Labs / Odyssey 的训练数据来源**完全不透明**；如果使用互联网图像 / video 训练 \"生成可漫游真实场景\"，将面对的不仅是 IP 诉讼，还有**真实地点的隐私问题**（生成某地真实样貌等于把某地数字孪生化，未经业主同意）。Niantic 路线靠 ToS 已经规避，但生成派玩家没有同等防护。
- **Niantic Spatial 的商业可持续性**：拆分后失去 Pokémon GO 现金牛，B2B AR / spatial 市场过去 5 年反复被验证\"故事大、买单少\"。LGM 是不是一个\"找不到客户的 foundation model\"是 12 月内的核心检验点。
- **GAIA-2 vs Nvidia Cosmos (driving 变体) vs Tesla \"world model\" 的相对位置**：三家都在做 driving WM，但披露 / 评测标准完全不互通。Wayve 是公开材料最充分的，**不代表技术最强**——Tesla / Cosmos 的实际能力 [unknown]。

## 与 E1-E4 的边界

| 维度 | E1 JEPA | E2 Dreamer | E3 video-as-WM (Sora/Veo/Cosmos) | E4 交互式 game WM | **E5 spatial 3D WM (本节)** |
|---|---|---|---|---|---|
| 表示 | latent (predictive) | latent (RSSM) | pixel / video latent | video token | **显式 3D (splat/mesh) 或 显式 ego/map** |
| 几何 | 隐式 | 隐式 | 隐式 | 隐式 | **显式** |
| 实时 | — | 是 (RL) | 否 | 是 | scene 是预生成的，渲染实时；driving 通常非实时 |
| 主要 user | RL / robot | RL agent | 内容创作 | 玩家 / agent | **AR / 自驾 / 世界编辑 / mapping** |
| 评测难点 | downstream task | reward | clip 质量 | trajectory 一致 | **几何正确性 + localization 准确性** |

显式几何的代价是**生成能力 / 多样性弱于纯 video 路线**（World Labs 至今没 Sora 那种 \"任意场景任意镜头\" 的多样性 demo）；收益是**下游可接传统 pipeline**（SLAM、Unity、自驾 stack、Blender）。这是 spatial WM 与 video WM 长期共存的根本理由。

## 推荐外部材料

- [World Labs about + blog](https://www.worldlabs.ai/blog) — 公司全部官方 narrative；除此之外目前没有更深 source 可参考。
- [World Labs 2024-12 \"Generating Worlds\" 首个 demo blog](https://www.worldlabs.ai/blog/generating-worlds) — 看 demo 视频体感 \"3D vs video\" 的区别。
- [Wayve GAIA-2 blog](https://wayve.ai/thinking/gaia-2/) 与 [tech report PDF](https://wayve.ai/wp-content/uploads/2025/03/GAIA-2.pdf) — 本节**唯一**完整 tech report，driving WM 必读。
- [Wayve GAIA-1 paper, arxiv:2309.17080](https://arxiv.org/abs/2309.17080) — 前作，理解 GAIA-2 的演化路径。
- [Niantic LGM blog (2024-11)](https://nianticlabs.com/news/largegeospatialmodel) — \"geospatial foundation model\" thesis statement。
- [Niantic Spatial spin-off 公告 (2025-03)](https://nianticlabs.com/news/niantic-spatial) — 理解 Niantic 转型。
- [Lightship VPS 产品页](https://lightship.dev/products/visual-positioning-system/) — 唯一规模化运营的 city-scale localization service。
- [DUSt3R arxiv:2312.14132](https://arxiv.org/abs/2312.14132) / [MASt3R arxiv:2406.09756](https://arxiv.org/abs/2406.09756) — 学界 feed-forward 3D 路线，是 World Labs / Odyssey 技术底座的最可能来源。
- [3D Gaussian Splatting 原 paper, SIGGRAPH 2023](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) — 不熟 3DGS 的读者必看，本节几乎所有产品都默认这是输出格式。
- [Fei-Fei Li TED talk \"With spatial intelligence, AI will understand the real world\" (2024)](https://www.ted.com/talks/fei_fei_li_with_spatial_intelligence_ai_will_understand_the_real_world) — 理解 World Labs 的 founding thesis。

---

[^worldlabs-dec24]: World Labs, \"Generating Worlds\", 2024-12-02, https://www.worldlabs.ai/blog/generating-worlds。Demo 强调输出是可漫游 3D 而非 video。
[^worldlabs-marble]: World Labs, Marble 产品页 https://www.worldlabs.ai (截至 2026-05 持续更新；无 peer-reviewed paper 对应)。
[^odyssey-explorer]: Odyssey, \"Introducing Explorer\", https://odyssey.systems/introducing-explorer。无 tech report，技术细节均为 blog 级。
[^gaia2]: Wayve, \"GAIA-2: A Controllable Multi-View Generative World Model for Autonomous Driving\", 2025-03-26, https://wayve.ai/thinking/gaia-2/ 与 tech report PDF。8.4B 参数、5 camera、latent diffusion、多条件 controllability。
[^niantic-lgm]: Niantic, \"Building a Large Geospatial Model to Achieve Spatial Intelligence\", 2024-11-12, https://nianticlabs.com/news/largegeospatialmodel。
