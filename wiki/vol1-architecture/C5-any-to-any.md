# Any-to-Any / Unified Understanding+Generation

## 路线定位

C1 讲的是 frontier 闭源 omni（GPT-4o / Gemini / Qwen-Omni）的 early-fusion 大方向，C5 这节专门聚焦一个更狭窄但学术上更活跃的子问题：**单一 transformer backbone 同时做 multimodal understanding 和 multimodal generation**——尤其是 image in & image out 这一对。它和 C1 的区别在于：C1 是产品级 omni（含 audio / video / realtime），C5 是\"unified model\"研究路线，主战场是开源、目标是\"用一个模型替换掉 LLaVA-理解 + SDXL/Imagen-生成 两个独立 stack\"。代表玩家：DeepSeek (Janus / Janus-Pro)、字节 (Show-o, BAGEL)、智源 / BAAI (Emu3)、Meta (Transfusion / Chameleon)。到 2026-05，这条线仍未出现一个能同时在 understanding (MMMU) 和 image-gen (GenEval / DPG) 上都赢过专业模型的开源 ckpt，但 BAGEL / Janus-Pro 已经把 gap 收到 \"可商用\" 级别。

## 代表模型清单

| 模型 | 发布日 | 参数 | image-token 策略 | 一手 source |
|---|---|---|---|---|
| Chameleon 7B / 34B | 2024-05-16 | 7B / 34B | union vocab + VQ-VAE (8192 codebook) + 单 softmax，纯 AR | [arxiv:2405.09818](https://arxiv.org/abs/2405.09818) |
| Transfusion (Meta) | 2024-08-20 | 0.16–7B | **单 backbone，text 走 next-token CE，image 走 diffusion (continuous latent patches)**，两 loss 在同一序列加权求和 | [arxiv:2408.11039](https://arxiv.org/abs/2408.11039) |
| Show-o (ByteDance / NUS) | 2024-08-22 | 1.3B | text=AR (causal mask) + image=MaskGIT-style discrete diffusion (full attention)，**单模型双 loss 双 attention mask** | [arxiv:2408.12528](https://arxiv.org/abs/2408.12528) |
| Emu3 (BAAI) | 2024-09-27 | 8B | **纯 next-token prediction，全模态都离散化**（image / video / text 共用一个 vocab），坚持\"AR-only is enough\" | [arxiv:2409.18869](https://arxiv.org/abs/2409.18869) |
| Janus (DeepSeek) | 2024-10-17 | 1.3B | **understanding 走 SigLIP encoder（连续 feature），generation 走 VQ tokenizer（离散）**，两条 vision path 解耦但共享 LLM backbone | [arxiv:2410.13848](https://arxiv.org/abs/2410.13848) |
| JanusFlow (DeepSeek) | 2024-11-12 | 1.3B | 把 Janus 的 generation 侧从 AR 换成 **rectified flow**，仍解耦 understanding/generation encoder | [arxiv:2411.07975](https://arxiv.org/abs/2411.07975) |
| Janus-Pro (DeepSeek) | 2025-01-28 | 1B / 7B | Janus 架构 scale up + 数据洗牌；GenEval 0.80（超过 SD3-Medium / DALL·E 3 公开数） | [arxiv:2501.17811](https://arxiv.org/abs/2501.17811) |
| BAGEL (ByteDance Seed) | 2025-05-20 | 7B-A1.5B (MoE / MoT) | **Mixture-of-Transformers**：understanding expert + generation expert 各一份 transformer 权重，共享 self-attention；image gen 走 latent diffusion head | [arxiv:2505.14683](https://arxiv.org/abs/2505.14683) |
| Show-o2 | 2025-06-?? | 1.5B / 7B | 升级到\"双 tokenizer + 双 head\"，image-gen 改用 flow matching；3D / video 扩展 | [arxiv:2506.15564](https://arxiv.org/abs/2506.15564) [uncertain 日期] |
| MetaQuery (Meta, follow-up of Transfusion) | 2025-?? | — | [unknown — 截至 2026-05 Meta 没放 Transfusion 后继公开 ckpt] | — |

> 范围说明：不收纯 image-gen 模型（SD3 / FLUX / Qwen-Image），不收纯 VLM（LLaVA / InternVL / Qwen-VL）。收的是**一个 ckpt 同时能 text→text、image→text、text→image，最好还 image→image** 的模型。

## 架构核心

### 三种 image-token 策略（这节最重要的分类）

任何 unified model 都要回答：**图像在序列里以什么形式存在？loss 怎么算？** 2024-2026 的开源工作给出了三种代表性答案：

**(A) 纯离散 AR / 单 softmax**（Chameleon, Emu3）
- 图像 → VQ token → 与 text token concat → 单 transformer + 单 next-token CE
- 优点：极简、和 LLM training infra 完全兼容、scaling law 清晰
- 缺点：VQ 重建损失上限制约图质，AR 解码慢（1024 token / 512² image）
- Emu3 是这条路线最激进的捍卫者：[\"Next-Token Prediction is All You Need\"](https://arxiv.org/abs/2409.18869)，paper §1 明确反对 diffusion，并在 GenEval 上对标 SDXL[^emu3]

**(B) 离散 + 非 AR mask diffusion**（Show-o）
- text 仍 AR，image 用 **MaskGIT-style** discrete diffusion：训练时随机 mask image token，模型并行预测被 mask 的位置
- 关键 trick：**同一 transformer 内部用两种 attention mask**——text 段 causal，image 段 full bidirectional，在 forward 里按段切换[^showo]
- 优点：image 解码步数从 1024 降到 ~16-50 步，速度大幅好于纯 AR；同时保留单模型单 vocab
- 这是\"用 LLM 长相做 MaskGIT\"，思路上承自 [Muse (Google 2023)](https://arxiv.org/abs/2301.00704)

**(C) 离散 + 连续 hybrid / 双 head**（Transfusion, Janus, BAGEL）
- text 走离散 next-token，image 走**连续** latent + diffusion / flow head
- Transfusion[^trans]：image 是 continuous latent patch 序列，position 上和 text token 拼一起；image 段的 loss 是 diffusion denoising loss，text 段是 CE；两个 loss 加权求和；attention 同样 text 段 causal、image 段 bidirectional
- Janus / Janus-Pro[^janus][^jpro]：更彻底地解耦——**understanding 用 SigLIP 连续 feature**（保信息），**generation 用 VQ 离散 token**（兼容 AR）。两条 vision path 在 input 侧就分开，只在 LLM backbone 内汇合。DeepSeek 的论文核心论点是\"理解和生成对 visual representation 的需求根本不同，强行用同一个 encoder 会两边都吃亏\"
- BAGEL[^bagel]：把解耦推到 transformer 内部，**Mixture-of-Transformers (MoT)**——understanding 和 generation 各一份 FFN/attention 权重，但共享 self-attention 上下文。image gen 用 latent diffusion head（不是 VQ AR），这点比 Janus 更接近 Transfusion 的连续 side

三种策略的取舍可以浓缩成一张表：

| 维度 | (A) 纯 AR 离散 | (B) 离散 mask diffusion | (C) 连续 + diffusion head |
|---|---|---|---|
| 代表 | Chameleon / Emu3 | Show-o | Transfusion / Janus / BAGEL |
| Image 解码步数 | ~1024 (AR) | ~16-50 | ~20-50 (diffusion) |
| Tokenizer | VQ-VAE/GAN | VQ-VAE/GAN | latent (continuous) 或 SigLIP+VQ 双路 |
| 与现有 LLM stack 兼容性 | 最高 | 中（要双 attention mask） | 低（要 diffusion loss + 双 head） |
| GenEval 公开最佳 | Emu3 ~0.66 | Show-o ~0.68 | Janus-Pro-7B **0.80** / BAGEL 0.88 |
| 文本能力代价 | 大（Chameleon < Llama2 同 size） | 中 | 小（Janus / BAGEL 接近同 size LLM）|

注：GenEval 数字来自各自 paper / leaderboard，**注意它是 paper 自报，第三方独立复现见下文 contamination 段**。

### Emu3 的极端\"AR-only\"立场

Emu3 paper 第一节标题就是 \"Next-Token Prediction is All You Need\"。它的论点：
1. 图像、视频、文本统一离散化后，一个 8B AR transformer 就能在 image-gen / video-gen / VLM 三项上对标专业模型（SDXL / Sora-mini / LLaVA-1.6）
2. 不需要 diffusion、不需要 CLIP encoder、不需要任务特定 head

工程实现：自训 image tokenizer（vocab 32768，downsample 8×），video 按帧 tokenize（temporal context 极长），训练 token 数未完整披露。**它的价值不在于 SOTA，而在于给后续工作一个干净的 baseline**——证明纯 AR 路线在 8B 规模可行。BAGEL / Janus 系列在 paper 里都会和 Emu3 对比。

### Janus → Janus-Pro 的演化（最值得焱拳精读的一条线）

- **Janus (1.3B)**: 提出\"decoupled visual encoding\"。Understanding 用 SigLIP-L (~400M)，generation 用 LlamaGen-style VQ tokenizer。两侧 token / feature 都进同一个 1.3B LLM。Image gen 仍是 AR。
- **JanusFlow (1.3B)**: 把 image 生成侧换成 rectified flow（连续 latent，不再 VQ），证明 decoupled encoder 思想和 flow matching 可结合
- **Janus-Pro (1B / 7B)**: 数据 + scale。Pretrain 数据三阶段化、SFT 数据精挑、scale 到 7B。GenEval 0.80、DPG-Bench 84.19，understanding 侧 MMBench 79.2（接近同 size LLaVA-1.6）。DeepSeek 主张这证明\"decoupled\"路线在 unified model 上是 Pareto 占优[^jpro]
- 局限：image-out 仍是 384² 起步，1024² 高清需要外挂上采样；视频完全不支持

### BAGEL: MoT + diffusion head

BAGEL 是字节 Seed 团队 2025-05 的 7B-A1.5B 模型，关键设计：
- **Mixture-of-Transformers**：和常规 MoE 在 FFN 路由不同，MoT 是\"每个 token 按模态/任务路由到不同 transformer block 的整套权重\"，understanding token 进 understanding expert，generation token 进 generation expert，self-attention 上下文共享
- **Image gen 用 latent diffusion head**（不是 VQ AR、也不是 mask diffusion），所以严格属于 (C) 类
- BAGEL paper 报 GenEval 0.88、WISE / GEdit-Bench 上 image editing 也强，且支持 image→image 编辑、in-context generation 等\"emergent\"行为
- 与 GPT-4o image gen 的对比是它营销的重点：在多数 in-context image edit case 上接近 4o，是 2026-05 开源里最强的 unified-gen 之一[^bagel]

### Transfusion: diffusion 直接焊在 LLM 上

- Meta FAIR 2024-08。**单 transformer，text 段算 CE，image 段算 diffusion denoising loss**（连续 latent patch）
- 关键 ablation: 直接对比同 size Chameleon（纯 AR / VQ）vs Transfusion（diffusion / 连续），Transfusion 在 image gen 上 FID 远低，同时 text perplexity 不退化[^trans]
- 训练 stability 上 Transfusion 比 Chameleon 友好得多（不需要 QK-Norm / z-loss 那一套），因为 image 段没有 logit-on-huge-vocab 的爆炸源
- 影响力：Transfusion 之后基本所有新 unified model 都重新评估了 \"是否还要走 VQ\"，这是 (C) 路线兴起的导火索
- Meta 没放权重，后续也没看到公开 follow-up ckpt

## 训练方法核心

### Pretrain
- **数据比例**：Chameleon / Emu3 是 text+image+(video) 大致均衡几 T token；Janus-Pro 走\"三阶段\"（先 text adapter 训 vision encoder → 加入 unified pretrain → image-gen heavy\"；BAGEL 没完整披露
- **Tokenizer 选择**就是上面 (A)(B)(C) 三选一，是 unified model 设计的第一根桩
- **Loss balancing**：Transfusion / Show-o 都强调 text CE 和 image diffusion / mask loss 的权重比要扫，Transfusion paper §4 给了 ablation；BAGEL / Janus-Pro 没完整披露权重

### Mid / Annealing
- Janus-Pro §3 描述了一个\"image-gen heavy cooldown\"阶段，专门提升 GenEval
- Emu3 paper 没单列 anneal，但 video 部分是分段加入的

### Post-train
- SFT: instruction-format 的 image gen + image understanding 混合数据
- **RL on image gen** 是 2025-2026 一个新方向（reward 来自 GenEval / CLIP score / aesthetic predictor / GPT-4V 评分），Janus-Pro / BAGEL 都用了类似 RLHF，细节都没全披露
- 还没有公开 unified model 用 RLVR 系（math / code）训练的报告，[uncertain] 是否被故意回避

### 算力
- Janus-Pro-7B: pretrain 描述\"512 H800 × 14 天\"，约 172K H800-hour（paper §3.1）[^jpro]
- BAGEL: \"trained on 2T+ multimodal tokens\"，具体 FLOPs 未公开
- Emu3 / Show-o / Transfusion: 算力未披露完整

## 与 eval / benchmark 的接口

- **Image generation 主榜**：GenEval, DPG-Bench, T2I-CompBench
  - 2026-05 开源 unified 第一梯队：BAGEL (0.88 GenEval) > Janus-Pro-7B (0.80) > Show-o2 (~0.76 [uncertain]) > Emu3 (0.66)
  - 与专业 image-gen 对比：SD3-Medium ~0.74、FLUX.1-dev ~0.66、Qwen-Image (2025-08) ~0.85；**unified 已能压过纯 image-gen 一档**，是 2025 后半年才发生的反转
- **Image understanding**：MMMU / MMBench / MMStar / ChartQA。Janus-Pro-7B MMBench ~79，BAGEL MMBench ~85，离顶级 VLM（InternVL3-78B ~88, Qwen2.5-VL-72B ~88）还有一档差距——**unified 在 understanding 侧仍未追平专业 VLM**
- **In-context image editing / multi-turn image**：[GEdit-Bench](https://arxiv.org/abs/2502.20172), [ImgEdit-Bench], [WISE]——这是 unified model 相对专业 image-gen 的真正优势区，BAGEL paper 在这里和 GPT-4o image gen 直接对位
- **Contamination / 复现疑点**:
  - GenEval 已经被多家指认有 prompt 集合泄露的问题（[2025 GenEval-Hard 论文](https://arxiv.org/abs/2510.18387) [uncertain 准确 id]）——所有 0.80+ 的开源数字都要打个折扣
  - Janus-Pro 的 GenEval 0.80 被 [社区独立复测]([uncertain — 没找到一手 link])在某些 prompt 上低于 paper 报告 [推测]
  - BAGEL 的 GPT-4o-image-edit 对比是 paper 自评，独立人评未公开

## 未知与争议

- **离散 vs 连续 image token：路线之争未收敛**。Emu3 论\"离散+AR 就够\"，Transfusion / BAGEL 论\"连续+diffusion 才能上高分辨率\"。2026-05 看，连续路线在 image-gen 质量上**已经领先**，但离散路线在与 LLM stack 兼容性、video 长序列上仍有不可替代性。焱拳做评测时这两类不该混在一个榜上比
- **\"Decoupled visual encoding\" 是否必要**：Janus 系的核心 claim。BAGEL 走了类似但不同的解耦（MoT vs 双 encoder）。Show-o / Emu3 不解耦也活得下来。**这是 2026 unified model 设计最大的开放设计点**，没有定论
- **Understanding 侧为什么追不上专业 VLM**：unified model 在 MMMU / MMBench 上始终比同 size 专业 VLM 低 5-10 分。Janus-Pro paper §5 把原因归于\"image-gen 数据稀释了 understanding 训练\"，但没给精确 ablation。[uncertain] 是否可以通过更激进的 data curriculum 解决
- **GPT-4o image gen 到底是哪类策略**：闭源黑盒。[Tang et al. 2025](https://arxiv.org/abs/2504.02782) 推测是 (C) 类（AR token + diffusion decoder），与 BAGEL 路线一致；这是\"BAGEL 是开源 4o image gen 的最佳近似\"这条 narrative 的依据
- **Gemini 2.5 Flash Image 路线**：[unknown — Google 没公开],推测仍是 diffusion-side 而非 AR，因为 image quality 明显非 token-grid 特征
- **Video unified**：Emu3 是唯一公开做了 video token 的 unified ckpt，其余都没认真做 video gen。这是 2026 接下来最可能爆发的方向（参考 [C3-video-gen.md](./C3-video-gen.md)）
- **Scaling law**：unified model 的 scaling law 没人画过完整曲线。Transfusion paper 给了 0.16B-7B 几个点，[uncertain] 是否能外推到 70B+

## 推荐外部材料

- [Transfusion paper (arxiv:2408.11039)](https://arxiv.org/abs/2408.11039) — \"diffusion + LLM 焊一起\"的奠基工作，必读，paper 简洁可一晚读完
- [Show-o paper (arxiv:2408.12528)](https://arxiv.org/abs/2408.12528) — discrete mask diffusion + AR 的混合 attention mask 设计，工程细节最具体
- [Emu3 paper (arxiv:2409.18869)](https://arxiv.org/abs/2409.18869) — \"AR-only is enough\" 立场的最完整辩护，反着读才能体会其他路线的取舍
- [Janus-Pro paper (arxiv:2501.17811)](https://arxiv.org/abs/2501.17811) — DeepSeek 的 unified model 收官之作，decoupled encoder 思想 + 数据 / scale 工程细节
- [BAGEL paper (arxiv:2505.14683)](https://arxiv.org/abs/2505.14683) — 2026-05 开源 unified gen 最强 ckpt，MoT + diffusion head 设计
- [Chameleon paper (arxiv:2405.09818)](https://arxiv.org/abs/2405.09818) — early-fusion + 单 softmax 的开盒样本，C1 也推荐
- [Sebastian Raschka, \"Unified Multimodal Models 2025\" 综述](https://magazine.sebastianraschka.com/) — 把 Transfusion / Show-o / Janus / BAGEL 放在一张图比较，最快的入门读物
- [张俊林知乎专栏 2025 unified model 系列](https://www.zhihu.com/people/zhang-jun-lin-76) — 中文圈对 Janus / BAGEL 拆解最细，对 image token 策略对比有独到见解 [uncertain 准确 URL]
- [Lilian Weng \"Diffusion + LLM\" 2024](https://lilianweng.github.io/) — 概念框架层面把 diffusion 和 AR 的统一性讲透

[^trans]: Transfusion paper §3-4 — 单 transformer，text 段 next-token CE + image 段 diffusion denoising，attention text 段 causal / image 段 bidirectional；ablation 显示同 size 下 image FID 远低于 Chameleon 且 text PPL 不退化。 https://arxiv.org/abs/2408.11039
[^showo]: Show-o paper §3 — text=causal-AR, image=full-attention discrete diffusion (MaskGIT 风)，同一 transformer 内 forward 时按段切换 attention mask + 双 loss。 https://arxiv.org/abs/2408.12528
[^emu3]: Emu3 paper §1, §3 — image/video/text 共用一个 vocab，纯 next-token prediction；自训 image tokenizer (vocab 32768, 8× downsample)；8B scale；明确反对 diffusion。 https://arxiv.org/abs/2409.18869
[^janus]: Janus paper §2 — decoupled visual encoding: understanding 走 SigLIP-L 连续 feature，generation 走 LlamaGen-style VQ 离散 token，两路在 LLM backbone 处汇合。 https://arxiv.org/abs/2410.13848
[^jpro]: Janus-Pro paper §3 — 数据三阶段 (adapter warmup → unified pretrain → image-gen cooldown) + scale 到 7B；GenEval 0.80、DPG-Bench 84.19、MMBench 79.2；512 H800 × 14 天。 https://arxiv.org/abs/2501.17811
[^bagel]: BAGEL paper §2-3 — Mixture-of-Transformers (understanding expert + generation expert 各一份权重，共享 self-attention)，image gen 走 latent diffusion head；GenEval 0.88，支持 in-context image editing，对位 GPT-4o image gen。 https://arxiv.org/abs/2505.14683
