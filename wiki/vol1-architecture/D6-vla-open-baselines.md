# 开源 VLA / 视觉运动策略基线（OpenVLA / RDT-1B / Diffusion Policy / Octo）

> **范围**：本节覆盖 2023-03 (Diffusion Policy) → 2026-05 期间，学术圈被反复当作 baseline 引用的四个**开源** VLA / visuomotor 策略：Diffusion Policy (Chi et al.)、Octo (Berkeley/Stanford)、OpenVLA (Stanford/UW + Toyota)、RDT-1B (清华 TSAIL)。这四家的共同点：**论文 + 权重 + 训练代码全开**，是当下做 VLA 评测 / ablation / Qwen 类 multimodal-action 团队入门必跑的 reference。本节不重讲 PI / Helix / Gemini Robotics（见 D1–D4），不重讲 sim benchmark 细节（见 D7 [若有]）。读者 = Qwen agentic eval owner，假设已读过 D1 π0 节。

## 路线定位（1 段）

如果说 π-series 是 2024-25 闭源公司路线里的"事实标准"，那 **OpenVLA / Octo / Diffusion Policy / RDT-1B 就是学术界的事实标准**——几乎所有 2024-26 的 VLA paper 都至少把这四家里的两个当 baseline。四者分两类：(1) **Diffusion Policy + Octo** 代表"小参数 + diffusion / flow head + 多任务 BC" 早期路线，参数量 80M–100M 级，CPU 都能跑，是 manipulation 社区 2023-24 的主力工具；(2) **OpenVLA (7B) + RDT-1B (1.2B)** 代表"VLM backbone + 大参数" 路线，是 RT-2 思想的第一批开源化产物。到 2026-05，这四家已不再是 SOTA（被 π0.5 / GR00T N1 / Gemini Robotics 全面超过），但仍是**唯一允许学术 paper 公平 ablation 的 reference**——闭源模型不接受第三方 eval API。

## 代表模型清单

| 模型 | 发布日 | 参数 | 关键变化 | 一手 source |
|---|---|---|---|---|
| **Diffusion Policy** | 2023-03-07 | ~80M (CNN/Transformer 变体) | 用 conditional DDPM 预测 action chunk；首次系统证明 diffusion ≫ Gaussian/MSE BC | [arxiv:2303.04137](https://arxiv.org/abs/2303.04137); [project](https://diffusion-policy.cs.columbia.edu/) |
| Diffusion Policy 升级 (IJRR) | 2024 | 同 | 期刊版加 robomimic / real-world push-T | [IJRR 2024](https://journals.sagepub.com/doi/10.1177/02783649241273668) [uncertain 卷号] |
| **Octo-Small / Octo-Base** | 2024-05-20 | 27M / 93M | Transformer policy + diffusion action head；在 800k OXE trajectory 上预训练；支持 language + goal-image 双 conditioning | [arxiv:2405.12213](https://arxiv.org/abs/2405.12213); [octo-models.github.io](https://octo-models.github.io/) |
| **OpenVLA-7B** | 2024-06-13 | 7B | Prismatic-7B VLM + autoregressive discretized action tokens（RT-2 风格）；970k OXE 训练；首个 7B 量级开源 VLA | [arxiv:2406.09246](https://arxiv.org/abs/2406.09246); [openvla.github.io](https://openvla.github.io/) |
| OpenVLA 权重 + 代码 | 2024-06 | — | HF `openvla/openvla-7b`；LoRA finetune 脚本 | [HF openvla/openvla-7b](https://huggingface.co/openvla/openvla-7b) |
| **RDT-1B** | 2024-10-10 | 1.2B | Diffusion Transformer (DiT) action head，专为**双臂 (bimanual)** 设计；多机器人预训练 + ALOHA finetune | [arxiv:2410.07864](https://arxiv.org/abs/2410.07864); [rdt-robotics.github.io](https://rdt-robotics.github.io/rdt-robotics/) |
| **OpenVLA-OFT** (Stanford 后续) | 2025-02 [uncertain 精确日] | 7B | OpenVLA + Optimized Fine-Tuning：parallel decoding + L1 regression head + FAST tokenizer 选项；推理 25× 加速 | [arxiv:2502.19645](https://arxiv.org/abs/2502.19645) [uncertain 编号] |
| Octo / Diffusion Policy 持续维护 | 2024-26 | — | 社区 fork（lerobot、ManiSkill 集成） | [HF lerobot](https://github.com/huggingface/lerobot) |
| 2026-05 状态 | — | — | 四家权重均仍可下载；OpenVLA 是 OXE 学术 baseline 引用最多的；RDT-1B 在中国 / 双臂场景使用最多 | — |

## 架构核心（按 paper 写的）

### 1. Diffusion Policy（Chi et al. 2023）

[arxiv:2303.04137](https://arxiv.org/abs/2303.04137) §3 / §4：

- **观测编码**：ResNet-18 (或 ViT) 编码 1–2 个 RGB 视角，concat low-dim proprioception。
- **Policy = conditional DDPM**：把 action chunk $A_t = (a_t, a_{t+1}, \dots, a_{t+H-1})$（H=16 是默认）当成图像一样扩散；conditioning = 观测 embedding。
- **两种 backbone 变体**：(a) **CNN-based** (1D UNet over time axis)，对短 horizon 稳定；(b) **Transformer-based**，对长 horizon / 复杂任务更好。paper 表 V 显示 Transformer 在 robomimic 大部分任务上略胜。
- **Receding horizon control**：每次预测 H 步 action，**只执行前 k 步**（通常 k=8），然后重新预测——这是 diffusion policy 解决 \"diffusion 推理慢\" 的关键工程 trick。
- **关键发现**：在 robomimic / push-T / kitchen 上，diffusion BC 对 multimodal demonstration（同一状态下专家有多种合理 action）显著优于 Gaussian / MSE BC，**因为 diffusion 本质上 model 的是分布**[^dp-paper]。

### 2. Octo（Ghosh, Walke et al. 2024）

[arxiv:2405.12213](https://arxiv.org/abs/2405.12213)：

- **架构**：纯 transformer policy（不复用 VLM backbone，从头训练）。Tokenize：image patches (ViT) + language tokens (T5 encoder) + readout tokens。
- **Action head = diffusion**（continuous，conditional DDPM），与 Diffusion Policy 思路一致，但 conditioning 来自 transformer readout 而非 ResNet。
- **多模态 conditioning**：同时支持 **language** 和 **goal image** 两种任务规约——这点比 OpenVLA / RDT-1B 更灵活（后者主要是 language）。
- **预训练数据**：**Open X-Embedding (OXE) ~800k trajectory**，跨 9 家机构、20+ embodiment。这是 OXE 的第一次大规模可下载预训练 demonstration。
- **参数量**：Octo-Small **27M** / Octo-Base **93M**。**小！** 这是 Octo 的卖点也是局限：跑得快、适合 finetune，但 capacity 不够吃下 OXE 全部多样性，到 OpenVLA 出来后 Octo 在 OXE 各 split 的平均 success rate 被反超 [^octo-vs-openvla]。
- **finetune 接口**：paper §5 提供 \"add new embodiment / new sensor\" 的 token-level finetune recipe——这是 Octo 设计哲学：**pretrain once, lightweight finetune everywhere**。

### 3. OpenVLA-7B（Kim, Pertsch, Karamcheti et al. 2024）

[arxiv:2406.09246](https://arxiv.org/abs/2406.09246)：

- **Backbone = Prismatic-7B**（Karamcheti 2024，[arxiv:2402.07865](https://arxiv.org/abs/2402.07865)）：dual-vision encoder (SigLIP + DINOv2) + Llama-2-7B。这是当时开源 VLM 里 visual grounding 最强的之一。
- **Action representation = RT-2 风格离散化**：连续 7-DoF action（end-effector Δpose + gripper）每维离散成 256 bins，复用 Llama tokenizer 里最少用的 256 个 token id 作为 \"action token\"。然后**用标准 LM next-token-prediction loss** 训练。
- **训练数据**：OXE 970k trajectory（比 Octo 用得多，因为 OpenVLA 加入了 RT-2 同期没公开的 Mobile ALOHA / DROID 子集）。
- **训练算力**：**64 × A100, 14 天** = ~21,500 A100-hour。是当时**最贵的开源 VLA 训练**（Octo ~5k TPU-hour 量级）。
- **finetune**：官方支持 **LoRA**（rank 32 默认）+ **full finetune**；LoRA 在单张 A100 80GB 上可做。这是 OpenVLA 被学术圈广泛采用的关键。
- **限制（paper §6 自承）**：(1) **推理慢**——7B autoregressive 每 action chunk 需 ~250ms (RTX 4090)，远低于 10 Hz；(2) **single-arm 7-DoF only**，不支持 bimanual；(3) **action 离散 256 bins** 精度有限。

### 4. OpenVLA-OFT（2025）

[arxiv:2502.19645](https://arxiv.org/abs/2502.19645) [uncertain 编号确认]——同一组人对 OpenVLA 的工程级升级：

- **Parallel decoding**：放弃 autoregressive，一次 forward 出全部 action chunk → ~25× 推理加速。
- **L1 regression head**（continuous action）替代离散 token：精度提升，且与 FAST tokenizer 路线兼容。
- **Action chunk H=8**（OpenVLA 原版每次只出 1 步）。
- 结论：**OpenVLA 架构本身没问题，瓶颈是 action 表达 + 解码方式**；OFT 在 LIBERO 上把 OpenVLA 从 ~76% 拉到 **~97%**[^oft-libero]，与 π0 / RDT-1B 同档。

### 5. RDT-1B（Liu et al., 清华 TSAIL 2024）

[arxiv:2410.07864](https://arxiv.org/abs/2410.07864)：

- **架构 = Diffusion Transformer (DiT) + 大型预训练**：
  - Text encoder = **T5-XXL**（frozen，4.7B 参数但不参与训练，只取 embedding）；
  - Vision encoder = **SigLIP** (frozen)；
  - Policy backbone = **1.2B DiT**（diffusion transformer，借鉴 Sora / Stable Diffusion 3 设计）；
  - Action head：DiT 直接输出 64-step action chunk 的 noise prediction。
- **为双臂量身设计**：unified action space = 128 维（覆盖 bimanual + 灵巧手 + mobile base），用 mask 处理不同 embodiment 的 DoF 缺失。这是 RDT 与 OpenVLA 最大区别——OpenVLA 是 7-DoF only。
- **两阶段训练**：
  1. **Pretrain**：46 个公开数据集（OXE + RH20T + 自采）共 **~1M+ episodes**；
  2. **Finetune**：**6k+ 双臂 (ALOHA + Mobile ALOHA) episodes**（自采，是 paper 重点贡献之一）。
- **算力**：48 × H100 训了约一周（paper §4），~8k H100-hour 级，比 OpenVLA 便宜约一半。
- **2026-05 的实际地位**：RDT-1B 是**中文 robotics 社区 / 双臂任务 baseline 引用最多**的开源 VLA；GR00T N1 / Unitree / 银河通用等多家都在内部 fork RDT 做产品级 finetune（公开承认或暗示）。

## 训练方法核心（共性 + 差异）

| 项 | Diffusion Policy | Octo | OpenVLA | RDT-1B |
|---|---|---|---|---|
| Backbone 是否复用 VLM | 否 (ResNet from scratch) | 否 (from scratch transformer) | **是 (Prismatic-7B)** | 部分 (T5 + SigLIP frozen, DiT from scratch) |
| Action head | DDPM (UNet/Transformer) | DDPM (continuous) | Autoregressive discrete token | DiT (diffusion) |
| Pretrain data | 单任务 demo (~200 demo) | OXE 800k traj | OXE 970k traj | OXE + RH20T + 自采 1M+ ep |
| Post-train | 任务级 BC | finetune recipe (token-level) | LoRA / full finetune | 6k bimanual finetune |
| RLHF / RLVR | 无 | 无 | 无（OpenVLA 本体）；社区有 [SERL 改造](https://arxiv.org/abs/2401.16013) | 无 |
| 算力披露 | ~1 GPU day / task | ~5k TPU-hour | 14d × 64 A100 ≈ 21.5k h | ~8k H100-hour [uncertain 精确] |

**关键共性**：到 2026-05，**这四家都没有公开 RL post-train**。RL on top of 开源 VLA 是活跃研究方向（SERL、RLPD、SimplerEnv-RL、ConRFT），但官方权重都还停在 pure BC。这正是 π-series RECAP（D1）和 Gemini Robotics 1.5（D4）的差异化卖点。

## 与 eval / benchmark 的接口

四家 paper 的 eval 重叠度极高，主要在两个 sim + 自采 real：

- **LIBERO** [arxiv:2306.03310](https://arxiv.org/abs/2306.03310) — 130 任务，4 个 suite (Goal / Object / Spatial / Long)。**当下 VLA 圈的"MMLU"**：几乎所有 paper 都报。OpenVLA-OFT / π0 / RDT-1B finetune 后都能到 90%+ 平均成功率，**已经接近饱和**。
- **ManiSkill2 / ManiSkill3** ([maniskill.ai](https://www.maniskill.ai/))，[arxiv:2410.00425 (MS3)](https://arxiv.org/abs/2410.00425) — GPU 并行 sim，主要做 single-arm + 灵巧手。Octo / Diffusion Policy 在这里被引用最多。
- **SimplerEnv** ([arxiv:2405.05941](https://arxiv.org/abs/2405.05941)) — 把 Google RT 系列的真机 setup 在 sim 中复刻，专门做 \"sim eval 能否代理 real eval\" 研究；OpenVLA / Octo 是主要被评对象。
- **CALVIN** ([arxiv:2112.03227](https://arxiv.org/abs/2112.03227)) — language-conditioned long-horizon BC；2023-24 主力，2025 后被 LIBERO 取代。
- **自采 real-world**：每家 paper 都有，互相不可比；这是 robotics eval 的老大难。

**已知 contamination / overfit 信号**：

- **LIBERO 饱和** → 几乎所有新 VLA 都报 LIBERO 90%+，已无区分度。社区开始转向 LIBERO-Plus / LIBERO-Long / 自定义 OOD eval。
- **OXE 训练数据与 SimplerEnv 评测场景重叠**：SimplerEnv paper §5 自己承认 RT-1/2 / OpenVLA 训练数据里就有 Google Robot setup，相当于"训练集 sim 替身"。这点对 Octo / OpenVLA 不公平地利好。
- **RDT-1B 的"零样本 bimanual"**：实际 finetune 用了 6k 双臂 demo，paper marketing 里偶尔被引用成"通用双臂模型"，要小心区分 pretrain capability vs finetune-after。

**第三方独立复现**：

- HuggingFace `lerobot` ([github](https://github.com/huggingface/lerobot)) 把 Diffusion Policy / Octo / OpenVLA / π0 / RDT-1B 全部纳入统一框架，公开了在 SO-100 / ALOHA / Koch 等低成本臂上的复现结果。这是 2025 年最重要的中立 reference。
- Stanford / Berkeley 多次报告：OpenVLA 在**完全 unseen 物体**上 zero-shot 表现远不如 paper 表 1 所示，需要 LoRA 适配几小时 demo 才能用。Octo 同样问题。这是开源 VLA 与 π0.5 (D1) \"unseen home\" 结果差距的根源。

## 未知与争议

明确没披露 / 不清楚的点（2026-05）：

1. **Octo / OpenVLA / RDT-1B 在 2025-26 是否还在主动维护**？OpenVLA-OFT 算 v2，但原作者团队（Pertsch、Karamcheti、Finn）多数已转向 π-series 或 Stanford 内部新项目；RDT 团队（清华 TSAIL）有跟进但 v2 没有显式发布。Diffusion Policy 已被 Chi 本人在多次 talk 中称 \"a 2023 method, please move on\" [uncertain 具体引用]。
2. **OpenVLA / Octo / RDT pretraining 的精确 data mixture 比例**——三家 paper 都给了\"用了哪些数据集\"，但没给\"各占多少 batch\"。这对想复现的人是黑盒。
3. **RL post-train 在这些 base 上能不能稳定 work**：社区有 SERL / RLPD / ConRFT 论文报 yes，但都没有像 RECAP 那样的"咖啡店 6 个月持续部署"级别证据。
4. **\"开源 VLA 真的能商用吗\"**：到 2026-05，明确基于这四家做出商业部署的案例 = **极少**（多数公司选择 fork π0 或自研）。原因 [推测]：OpenVLA latency 太高、Octo capacity 太小、RDT 数据偏中国双臂场景、Diffusion Policy 不是 generalist。
5. **Diffusion Policy 与 π0 flow matching 在 inference 上的真实差距**：π0 paper 说 flow matching 10 步够，DP 论文说 DDPM 100 步、DDIM 16 步够；公平 benchmark **没人做过**。

主要争议：

- **离散 action token (OpenVLA) vs continuous diffusion (Octo / RDT / DP) vs flow matching (π0)**——四家代表三条路线，2024-25 圈里争论不休。π0-FAST (D1) 的实验给出当下最被接受的答案：\"**表达形式不是性能瓶颈，data 和 backbone capacity 才是**\"。OpenVLA-OFT 用 L1 regression 把 OpenVLA 从离散切到连续也支持这个结论。
- **\"VLM backbone 到底有没有用\"**：Octo (no VLM, 93M) vs OpenVLA (Prismatic 7B) 在 LIBERO finetune 后差距不大，但在**zero-shot language understanding** 和 **unseen object generalization** 上 OpenVLA 明显更强。社区共识渐向 \"**有用，但前提是有足够 robot data 配合，否则 VLM 部分 over-fit 后退化**\"——这正是 π0.5 KI 想解决的问题（见 D1）。

## 对 Qwen eval lead 的实用 takeaway

如果你要做 VLA / multimodal-action 评测体系，**只需要这四家就能搭出 90% 的学术 baseline**：

1. **快速 sanity check baseline**：Diffusion Policy（80M，几小时训完）+ LIBERO。
2. **OXE 预训练泛化对照**：Octo-Base（93M）。
3. **大模型 VLA 对照**：OpenVLA-7B 或 OpenVLA-OFT。
4. **双臂 / DiT-style 对照**：RDT-1B。
5. 配合 π0 (D1)、Gemini Robotics (D4)、GR00T (D3) 三个**闭源 / 半开** SOTA 做上限对照。

最重要的事：**LIBERO 已饱和，不能只看 LIBERO**。2026 起做 VLA eval 必须配 OOD 真机 + SimplerEnv + 至少一个 unseen-object / unseen-scene split，否则报出来的 95% 没有区分度。

## 推荐外部材料

- [Diffusion Policy paper, arxiv:2303.04137](https://arxiv.org/abs/2303.04137) — 仍是入门 visuomotor policy 必读，写作清晰。
- [Octo paper, arxiv:2405.12213](https://arxiv.org/abs/2405.12213) + [octo-models.github.io](https://octo-models.github.io/) — 小参数 generalist policy 的 reference 实现。
- [OpenVLA paper, arxiv:2406.09246](https://arxiv.org/abs/2406.09246) — RT-2 思路的第一个开源版本，必读。
- [OpenVLA-OFT, arxiv:2502.19645](https://arxiv.org/abs/2502.19645) — OpenVLA 工程升级，给"action 离散 vs 连续"争论提供 ablation 证据。
- [RDT-1B paper, arxiv:2410.07864](https://arxiv.org/abs/2410.07864) + [project page](https://rdt-robotics.github.io/rdt-robotics/) — DiT-based VLA 模板，中文 robotics 圈引用最多。
- [Prismatic VLM paper, arxiv:2402.07865](https://arxiv.org/abs/2402.07865) — OpenVLA 的 backbone 来源，理解 SigLIP+DINOv2 dual-encoder 的设计选择。
- [HuggingFace `lerobot`](https://github.com/huggingface/lerobot) — 把四家放一个统一 API 下，是当下复现 / 二次开发的最低门槛入口。
- [LIBERO paper, arxiv:2306.03310](https://arxiv.org/abs/2306.03310) — 当下 VLA 的事实 benchmark。
- [SimplerEnv, arxiv:2405.05941](https://arxiv.org/abs/2405.05941) — sim-vs-real eval 对齐，做评测必读。
- [Open X-Embodiment, arxiv:2310.08864](https://arxiv.org/abs/2310.08864) — Octo / OpenVLA / RDT 共同的数据基础，了解 OXE 各 split 性质后再读其他 paper 会通透很多。

---

[^dp-paper]: Chi et al., "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion", arxiv:2303.04137, 2023-03; §4.3 multimodal demo experiment 是核心论据。
[^octo-vs-openvla]: OpenVLA paper §5 表 4 在 BridgeData V2 / RT-1 eval split 上直接报 Octo vs OpenVLA，OpenVLA 在多数任务上 +10–20% success rate；这是社区采用 OpenVLA 替代 Octo 作为首选 baseline 的关键证据。
[^oft-libero]: OpenVLA-OFT arxiv:2502.19645 [uncertain 编号] 表 1 / 表 2 报 LIBERO suite 平均 success rate；OpenVLA 原版约 76.5%，OFT 约 97%。具体数字以最终 arxiv v2 为准。
