# NVIDIA GR00T + Cosmos (Robotics Foundation Models)

## 路线定位（1 段）
NVIDIA 在 humanoid / general robotics 这条线上押的是「foundation model + 合成数据 + 仿真」三件套：**GR00T**（Generalist Robot 00 Technology）是面向 humanoid 的 VLA（Vision-Language-Action）基础模型族，**Cosmos** 是面向物理世界的 world foundation model（WFM），负责把少量真机数据 + 仿真 rollout 放大成可训练 video/trajectory 数据集，**Isaac Lab / Isaac Sim** 是 GPU 加速的 RL 仿真环境。竞争对象在算法侧是 Physical Intelligence (π0/π0.5)、Google DeepMind RT-2/Gemini Robotics、Figure Helix、1X 的 in-house VLA；在 stack 侧 NVIDIA 是少数同时卖 chip + sim + model 的，定位类似机器人界的 CUDA + Llama。

## 代表模型清单
| 模型 | 发布日 | 参数/形态 | 关键变化 | 一手 source |
|---|---|---|---|---|
| GR00T (announce) | 2024-03 GTC | 未公开 | Jensen 首次提 humanoid foundation model 计划 | [GTC 2024 keynote](https://www.nvidia.com/en-us/on-demand/session/gtc24-s62816/) |
| **GR00T N1** | 2025-03-18 (GTC) | 2.2B (System2 Eagle VLM + System1 DiT action expert) | 首个 open-weight humanoid VLA, dual-system, 16-step action chunk | [arxiv 2503.14734](https://arxiv.org/abs/2503.14734), [HF nvidia/GR00T-N1-2B](https://huggingface.co/nvidia/GR00T-N1-2B) |
| GR00T N1.5 | 2025-06 | 2.2B | 改进 VLM grounding，新增 language-conditioned grasping，flow-matching action head | [NVIDIA blog](https://developer.nvidia.com/blog/accelerate-generalist-humanoid-robot-development-with-nvidia-isaac-gr00t-n1-5/) |
| GR00T N2 / "GR00T-Dreams" | 2025-08 (SIGGRAPH) | 未完全披露 | 与 Cosmos-Predict2 耦合：用 dream video 当 neural trajectory, 减真机数据 | [NVIDIA blog](https://developer.nvidia.com/blog/building-foundations-for-humanoid-robots-with-new-nvidia-isaac-gr00t-cosmos-and-robotics-libraries/) |
| GR00T N3 | 2026-03 GTC [uncertain — 仅 keynote 提及, paper 未放出] | [unknown] | 报称多 embodiment 通用 manipulation + 长程任务 | [GTC 2026 keynote](https://www.nvidia.com/gtc/keynote/) [uncertain — 链接需核对] |
| Cosmos-1.0 (WFM) | 2025-01-07 CES | 4B / 12B (diffusion) + 4B/13B (autoregressive) | Physical AI 用 video WFM，开源 weights + tokenizer | [arxiv 2501.03575](https://arxiv.org/abs/2501.03575) |
| Cosmos-Predict2 | 2025-06 | 2B / 14B | 改进物理一致性 + action-conditioned 生成 | [NVIDIA blog](https://research.nvidia.com/labs/dir/cosmos-predict2/) |
| Cosmos-Reason1 | 2025-03 | 8B VLM | 物理常识 reasoning 评测 + 模型，配 benchmark | [arxiv 2503.15558](https://arxiv.org/abs/2503.15558) |
| Cosmos-Transfer1 | 2025-03 | — | sim→real 风格迁移，做 domain randomization | [arxiv 2503.14492](https://arxiv.org/abs/2503.14492) |

## 架构核心（按 paper 写的）

### GR00T N1 dual-system （arxiv 2503.14734）
- **System 2 = VLM**：基于 NVIDIA Eagle-2 VLM（SmolLM2 1.5B + SigLIP vision），输入 RGB 多视角 + language instruction，约 ~10Hz 跑一次，输出 latent token 序列。论文 §3.1。
- **System 1 = Diffusion Transformer (DiT) action expert**：cross-attend 到 System 2 的 latent + 当前 proprioception，输出 **16 步 action chunk**，约 120Hz 控制频率。flow-matching loss（不是 DDPM ε-pred）[^1]。
- **Embodiment-aware projector**：每个机器人本体（Fourier GR-1, Unitree H1, 双臂桌面 setup, …）有独立 state/action encoder & decoder，共享中间 transformer trunk，类似 RT-X / Octo 的 multi-embodiment 设计。论文 §3.2。
- 参数总量 **2.2B**，其中 VLM ~1.7B，action expert ~0.5B [^1]。
- 训练数据金字塔（论文 Fig.2）：底层 **web video + human video**（Ego4D 等）→ 中层 **synthetic（Isaac + Cosmos 生成）** → 顶层 **真机 teleop**。比例上 synthetic >> real，作者声称这是降数据成本关键。
- N1.5 把 action head 从 DDPM 风格换成 **flow matching**，并加强 language conditioning（[blog](https://developer.nvidia.com/blog/accelerate-generalist-humanoid-robot-development-with-nvidia-isaac-gr00t-n1-5/)）。

### Cosmos WFM（arxiv 2501.03575）
- 两条 backbone 并行：
  - **Cosmos-Predict (diffusion)**：DiT，3D causal video VAE tokenizer（8×16×16 压缩比），text+image+video 条件生成未来 frames。
  - **Cosmos-Predict (autoregressive)**：把 video 离散化成 token 后用 LLaMA 风格 transformer 做 next-token，便于和 LLM stack 复用 infra。
- **Cosmos Tokenizer** 单独发布：continuous & discrete 两版，号称比同压缩率 baseline 重建质量更高（[github](https://github.com/NVIDIA/Cosmos-Tokenizer)）。
- 训练数据：~20M hours 视频，经物理/动作过滤管线降到 ~100M clips（paper §4）。**没有完全披露 dataset composition**，只给类别比例。
- 用法：给 robot policy 一个 (image, action) 条件，让 Cosmos rollout 未来 video，再用 inverse dynamics / 现成 policy 提 action label → 合成 trajectory。这就是 GR00T-Dreams pipeline ([blog](https://developer.nvidia.com/blog/building-foundations-for-humanoid-robots-with-new-nvidia-isaac-gr00t-cosmos-and-robotics-libraries/))。

[^1]: GR00T N1 tech report, arxiv:2503.14734, §3.

## 训练方法核心
- **Pretrain (GR00T N1)**：dual-system 联合训练，loss = flow-matching action loss + auxiliary VLM 语言 loss（保 grounding 不退化）。数据按金字塔采样，真机数据 oversample。算力未明说，仅提"H100 cluster"。
- **Mid-train**：在 high-fidelity synthetic（Isaac Lab + Cosmos transfer 后的 photo-realistic frames）上做大批 trajectory imitation。
- **Post-train**：用户在自己 embodiment / 任务上 SFT 几小时 teleop 数据。论文 §5 给的下游评测大多是 SFT 后的结果，不是 zero-shot。
- **RL**：N1 论文里 RL 部分很少，主要是 IL；Isaac Lab 提供 GPU 并行 PPO，但 GR00T-N* 主线还是 imitation + synthetic scale-up。
- **Cosmos pretrain**：diffusion 模型用 rectified flow 训练；AR 模型 next-token CE。算力披露上 Cosmos-1 用了 "thousands of H100 weeks" 量级（paper §4.3，没给精确数字）。

## 与 eval / benchmark 的接口
- 官方报：
  - **GR00T N1**：在 Fourier GR-1 humanoid 上的 pick-and-place / pouring / bimanual tasks，相对 BC baseline 提 ~30-50% success（论文 Table 2-3）。
  - **Cosmos-Reason1**：自建 *Physical AI benchmark*（intuitive physics QA），SOTA over GPT-4o / Gemini 2.0 on subset（[arxiv 2503.15558](https://arxiv.org/abs/2503.15558) Table 2）。
- 第三方：
  - HuggingFace LeRobot 团队把 GR00T N1 跑过 SO-100 桌面臂，社区报告 fine-tune 后比 ACT/Diffusion Policy baseline 有 margin，但没有 peer-reviewed 复现 [uncertain]。
  - 学术界对 humanoid VLA 的独立 benchmark 还非常少（不像 LIBERO / SimplerEnv 之于桌面臂），所以横向对比 π0 / Helix / Gemini Robotics 基本靠各家自报。
- Contamination：synthetic-heavy training 的失败模式是 sim2real gap 而非数据污染；NVIDIA 自己也承认 cosmos rollout 在接触动力学（contact-rich）任务上仍不稳（N2 blog 中明说）。

## 未知与争议
- **真机数据规模 unknown**：N1 论文反复强调"少量真机"，但没给小时数 / episode 数的精确表。社区估算 Fourier GR-1 部分在 1k-10k 小时量级 [推测]。
- **GR00T N3 没有 paper**：截至 2026-05 只在 GTC keynote 出现，技术细节、weights 是否开放都 [unknown]。
- **Cosmos 训练集来源**：是否包含 YouTube/版权视频，NVIDIA 没明说，只说"licensed + permissively-licensed sources"，业内对此持怀疑 [推测]。
- **dual-system 是否必要**：π0 用单 backbone + action expert head 也能做到类似 frequency 分离，并未显式分 System1/System2；这是设计选择差异，目前缺 head-to-head ablation。
- **N1.5 → N2 的 flow matching vs DDPM 切换**没有公开 ablation 数字。

## 推荐外部材料
- [GR00T N1 paper (arxiv 2503.14734)](https://arxiv.org/abs/2503.14734) — 真要看 dual-system / data pyramid 细节就读这篇，30 页够清楚。
- [Cosmos WFM paper (arxiv 2501.03575)](https://arxiv.org/abs/2501.03575) — Physical AI 视角的 video generative model 综述 + NVIDIA 自家实现。
- [NVIDIA Isaac GR00T GitHub](https://github.com/NVIDIA/Isaac-GR00T) — 有 inference / fine-tune 脚本，能在单 H100 上跑，工程细节比 paper 直观。
- [HuggingFace LeRobot blog: GR00T integration](https://huggingface.co/blog/lerobot-goes-to-driving-school) — 第三方视角，看 GR00T 在非 NVIDIA 硬件上怎么落地 [uncertain — 标题确认中]。
- [Physical Intelligence π0 / π0.5 报告](https://www.physicalintelligence.company/blog/pi0) — 必须对照看的竞品，了解为什么有人不走 dual-system。
- [Chelsea Finn lecture on Robot Foundation Models (CS231n guest 2025)](https://cs231n.stanford.edu/) — 把 RT-2 / Octo / π0 / GR00T 放一起讲的好课件 [uncertain — 录像是否公开待确认]。
- [Cosmos Tokenizer GitHub](https://github.com/NVIDIA/Cosmos-Tokenizer) — 想理解 video tokenizer 工程选择（continuous vs discrete, 压缩比）的最佳入口。
