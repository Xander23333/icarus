# Ev7 Embodied / VLA 评测 — 没有 MMLU 的赛道，sim2real 的诚实账本

## 路线定位

LLM / VLM 评测圈早就有 MMLU、GPQA、SWE-bench 这种"虽然有问题但大家都认"的事实标准；**embodied / VLA (Vision-Language-Action) 这边截至 2026-05 仍然没有**。最接近共识的 LIBERO 在 2024 H2 就被 π0 / OpenVLA-OFT / RDT 拉到 95%+ 全饱和；CALVIN 自 2023 起一路被拍到 4.0/5；OXE / RT-X 上的"cross-embodiment 评估"基本是各家自己挑 task 自己报；SimplerEnv 把 real-robot 评测搬到 sim 里跑，但 sim2real correlation 自己也只能给出"中等"信心。这一节面向 Qwen 团队做 VLA / embodied agent 的 eval owner：哪个 benchmark 能用、哪个已经废了、sim2real 这件事到底信几分。**核心结论：2026 年阶段没有"一个数字"可以代表 VLA 能力，必须 sim suite + real-robot small-N + 第三方 RoboArena 三件套并报。**

## 代表 benchmark 清单

| Benchmark | 首发 | 类型 | 现状（2026-05） | 一手 source |
|---|---|---|---|---|
| CALVIN | 2021-12 | sim, long-horizon language-conditioned | 饱和（D→D 4.5+/5，ABCD→D 4.0+） | [arxiv 2112.03227](https://arxiv.org/abs/2112.03227) |
| LIBERO | 2023-06 | sim, lifelong + 4 suites | **重度饱和**（π0 / OpenVLA-OFT / RDT 平均 95%+） | [arxiv 2306.03310](https://arxiv.org/abs/2306.03310) |
| Open X-Embodiment / RT-X | 2023-10 | real-robot 数据集 + cross-embodiment eval | 没有统一 eval 协议，各家自评 | [arxiv 2310.08864](https://arxiv.org/abs/2310.08864) |
| SimplerEnv | 2024-05 | sim 复刻 Google Robot / WidowX，用于 sim2real | 当前 VLA 论文几乎必报 | [arxiv 2405.14082](https://arxiv.org/abs/2405.14082) |
| RoboCasa | 2024-06 | sim 家居大规模 task generation | 数据生成器为主，eval 用得少 | [arxiv 2406.02523](https://arxiv.org/abs/2406.02523) |
| ManiSkill 3 | 2024-10 | GPU 并行 sim，含 SimplerEnv 集成 | RL + VLA 双用，硬件 throughput 王 | [arxiv 2410.00425](https://arxiv.org/abs/2410.00425) |
| RoboArena | 2025-06 | 真机 crowd-sourced pairwise eval | 目前最接近"VLA Chatbot Arena" | [robo-arena.github.io](https://robo-arena.github.io/) |

## CALVIN — 老国王，已经被拍到天花板

[arxiv 2112.03227](https://arxiv.org/abs/2112.03227)，Mees et al., Freiburg

- 4 个环境（A/B/C/D）× 34 个 language-conditioned 任务，metric 是"连续完成 5 个 instruction"的平均成功长度（0–5）。两个标准 split：**D→D**（同环境）与 **ABCD→D**（跨环境泛化）。
- 2022–2023 一度是 language-conditioned manipulation 的事实标准：HULC、RT-1、3D Diffuser Actor、GR-1、RoboFlamingo 都报 CALVIN。
- 2024 起天花板被反复刷穿：3D Diffuser Actor (ICLR 2024, [arxiv 2402.10885](https://arxiv.org/abs/2402.10885)) 在 ABCD→D 上 3.6+；GR-2 / RDT-1B / π0 都把 D→D 推到 4.5+ /5。**论文里 CALVIN 数字已经基本不能区分模型**。
- 局限：单一 Franka + 桌面 block，视角固定，language 模板化；不测多 embodiment、不测 dexterous、不测 long-horizon mobile。今天 CALVIN 主要价值是"新方法快速跑通的 smoke test"，不是 frontier eval。

## LIBERO — 2024 的事实标准，2025 已经饱和

[arxiv 2306.03310](https://arxiv.org/abs/2306.03310)，Liu et al., UT Austin，[libero-project.github.io](https://libero-project.github.io/)

- 4 个 suite × 10 task × 50 demo：**LIBERO-Spatial / Object / Goal / Long**，分别测 spatial / object / goal / long-horizon 维度的 lifelong learning。每个 task 50 个 rollout，metric 是 success rate。
- 2024 H1 因为 OpenVLA ([arxiv 2406.09246](https://arxiv.org/abs/2406.09246)) 选它做主表，被全行业跟进，2024 H2 后 VLA 新论文（RDT / TinyVLA / CogACT / π0 / DexVLA / OpenVLA-OFT）几乎都报 LIBERO-90 或四 suite 平均。
- **饱和时间线（公开数字）**：
  - OpenVLA (2024-06)：四 suite 平均 76.5%。
  - π0 (Physical Intelligence, 2024-10, [pi.website/blog/pi0](https://www.physicalintelligence.company/blog/pi0))：~94%。
  - OpenVLA-OFT (Stanford, 2025-02, [arxiv 2502.19645](https://arxiv.org/abs/2502.19645))：97.1%，明确写"LIBERO is largely saturated"。
  - π0.5 / RDT-2 / GR00T N1 后续报告基本都在 95–98% 之间，**suite 间方差 < 实验随机种子方差**。
- 2025 起 LIBERO 的处境类似 2023 年的 MMLU：**新模型只能用它做"不掉点"门槛**，不能用来证明能力提升。LIBERO-Long 仍偶尔能拉出 2–3% 区分度，但置信区间已经盖住了。
- 给 Qwen VLA 团队：**LIBERO 只报，不当 headline 指标**；建议同时报 95% CI 与 per-task 失败 case 分析，否则等于没说。

## SimplerEnv — 用 sim 替代 real-robot eval 的尝试

[arxiv 2405.14082](https://arxiv.org/abs/2405.14082)，Li et al., [simpler-env.github.io](https://simpler-env.github.io/)

- 动机：real-robot eval 太贵（Google RT-2 论文报一次 evaluation 几百 rollout × 几小时人工），无法快速 ablation；但 LIBERO/CALVIN 又跟真机分布差太远，不能做 model selection。SimplerEnv 在 ManiSkill / SAPIEN 里 **逐 pixel + 物理参数 match** Google Robot (RT-1/RT-2 平台) 和 WidowX (BridgeData V2 平台)。
- 提供两类 metric：**Visual Matching**（pixel-level render 匹配真机视频，控制 visual gap）与 **Variant Aggregation**（系统性扫光照、纹理、背景，估计 robustness）。
- 论文里关键经验数字：在 Google Robot 的 4 个 task 上，**sim score 与 real score 的 Pearson r ≈ 0.87**（RT-1-X / RT-2-X / Octo / OpenVLA 共 12 model × 4 task 网格）。**WidowX 上 r 较低**（≈ 0.7），主要因为 BridgeData task 更 contact-rich，sim 物理误差更大。
- 2024–2025 几乎所有 generalist VLA paper（OpenVLA / RDT / π0 / CogACT / GR00T N1 / Magma）都报 SimplerEnv，使其成了"开放 VLA 圈最接近共识的 sim 指标"。
- 诚实告警：
  1. r=0.87 不等于可替代——**model ranking 在 top-3 内仍可能翻转**。SimplerEnv 论文自己也只敢说"good predictor"，不说"replacement"。
  2. 只覆盖 Google Robot + WidowX 两个平台、十几个 task，做 Franka / dexterous hand / humanoid 的团队不能直接套。
  3. 评测的是已训好的 policy，不是 in-context skill learning，对 VLA 的 prompt / language generalization 维度覆盖弱。

## ManiSkill 3 / RoboCasa — sim 基础设施，不只是 benchmark

- **ManiSkill 3** (UCSD Hao Su 组, 2024-10, [arxiv 2410.00425](https://arxiv.org/abs/2410.00425), [maniskill.ai](https://www.maniskill.ai/))：完全 GPU 并行（基于 SAPIEN），可以 10⁴+ env 并行跑视觉 RL。集成 SimplerEnv，提供 20+ task families，覆盖 manipulation / mobile / dexterous / soft body。2025 之后是 VLA 后训 / RL fine-tune 的主流 sim 平台之一（GR00T、RoboBrain、π0.5 都用到）。eval 角度：ManiSkill 自己的 benchmark 表（task-by-task SR）使用不广，更多是作为"运行 SimplerEnv / 自建任务"的基础设施。
- **RoboCasa** (Nasiriany, Maddukuri et al., NVIDIA + UT Austin, 2024-06, [arxiv 2406.02523](https://arxiv.org/abs/2406.02523))：基于 RoboSuite，100+ 家居物体 + 25 个 kitchen-scale task + LLM 生成的大规模任务变体。**主要定位是合成数据生成器**（被 GR00T / OpenVLA 续训 用作 augmentation），eval 用得相对少。其贡献在数据侧不在 metric 侧。
- 对 eval owner：ManiSkill 3 / RoboCasa 都不是"benchmark"那种意义上的标准，**报这俩 task 的 SR 数字对外部 reader 几乎没意义**，因为没有 baseline 一致性。它们是"跑你自己的 task 的基础设施"。

## Open X-Embodiment / RT-X — 数据集大，eval 协议没有

[arxiv 2310.08864](https://arxiv.org/abs/2310.08864)，Google DeepMind + 21 机构

- 把 21+ 实验室的 22+ embodiment 的轨迹数据合并成 OXE（160 万 trajectory），用来训 RT-1-X / RT-2-X。论文里展示了"在 X 上训能提升 single-embodiment 性能"。
- 问题：**OXE 没有规范化的 held-out eval split**。所谓 "cross-embodiment evaluation" 是各家选自己实验室的 real robot 做 5–10 task × 10–20 rollout 的小样本，然后跟 RT-1-X 比一下成功率。没有 leaderboard，没有 reproducibility 协议。
- 后续 RT-2、π0、π0.5、GR00T N1 / N1.5、Magma、Helix 等 generalist VLA 论文都遵循类似套路："我们在自己的真机 + 自己挑的 task 上比 OpenVLA / π0 高 X%"，**互相之间数字不可比**。
- 这就是为什么 2025 H1 之后 RoboArena 才会被推出来——social pressure 已经堆够了。

## RoboArena — 真机 crowd eval，2025 H2 的新尝试

[robo-arena.github.io](https://robo-arena.github.io/)，Stanford / UCB / Google DeepMind / TRI 等多机构，2025-06 launch

- 借用 Chatbot Arena 的设计：**多个机构维护各自的真机 setup，policy A vs policy B 在同一 task 上跑 rollout，由人类盲打偏好（成功 / 更平滑 / 更安全）**，用 Bradley-Terry / Elo 聚合。
- 起步覆盖 Franka / WidowX / ALOHA / mobile manipulator 等若干平台，policy 包含 π0 / π0.5 / OpenVLA / OpenVLA-OFT / GR00T N1 / RDT-2 等。每个 policy 在每个平台上的 task 由维护机构选，但 pairing 与打分是匿名 + 跨机构对齐的。
- 截至 2026-05 leaderboard（[uncertain — 数字会变，引用日期]）：π0.5 和 GR00T N1.5 在 generalist policy 一档相互纠缠；OpenVLA-OFT 在 specialist tuning 上表现意外好；开源 vs 闭源 gap 在某些平台上 < 5% Elo。
- 优点：第一次把"different lab, different robot"的可比性问题 in-the-loop 解决了。缺点：rollout 数量仍然不大（人类评分昂贵），Elo 置信区间宽；不同平台 task 分布不同，aggregate Elo 的语义需要小心解释（这点和 LMSYS Arena 在 multi-language 上的争议同质）。
- 给 Qwen VLA 团队的建议：**RoboArena 是目前"最像 frontier leaderboard"的 embodied eval，应该投入参与 + 至少 1 个机构 setup 承接 pairing**，否则未来想 claim 真机能力会被外界打折。

## Sim2real validity — 到底信几分

把 2024–2026 几个公开的 sim↔real correlation 数据点拼一下（给 eval owner 一个心智模型）：

- **SimplerEnv Google Robot**：r ≈ 0.87 over 12 model × 4 task ([arxiv 2405.14082](https://arxiv.org/abs/2405.14082) §5)。
- **SimplerEnv WidowX**：r ≈ 0.70，contact-rich 任务上甚至 < 0.5。
- **LIBERO ↔ real Franka**：没有官方 correlation 研究；社区共识（OpenVLA + π0 公开博文）是"LIBERO 高分是 necessary not sufficient"，**95% LIBERO 的模型在真机上常态成功率仍可能 < 60%**。
- **CALVIN ↔ real**：CALVIN 设计就是 sim-only，没有官方对应真机；社区基本不再做 calibration。

结论：sim eval 可以用于 (a) ablation / model selection 的快速 loop，(b) "不掉点"门槛；**不能直接当作真机能力声明**。任何 VLA 报告里如果只有 sim 数字，对应权重应打到 0.5–0.7。

## VLA 评测和 LLM 评测的几个结构性差异（写给 LLM 背景的人）

1. **Rollout 是有状态的**：一次失败 = 这条 trajectory 没分，没有"prompt-level resampling"廉价方案。这导致样本量天然小，方差大；任何 < 50 rollout/task 的数字都应该带 CI。
2. **Reset / scene randomization 决定一切**：同一 model 同一 policy，换个 reset distribution，SR 可以差 30%。LIBERO / SimplerEnv 都固定 reset，**这是它们能成为标准的前提，也是它们容易 overfit 的原因**。
3. **没有 ground-truth answer**：success 判定靠 task-specific predicate（物体是否在框里、抽屉是否打开），predicate 本身可能有 bug。Real-robot eval 更糟，要靠人或 VLM judge——这就是 RoboArena 选择 pairwise human preference 的原因。
4. **language conditioning 与 manipulation 能力的耦合度低**：很多 "VLA" 其实是 V-A，language 只作 task id。LIBERO 的 language template 化就是这种情况。真正测 language understanding 的 manipulation benchmark 至今缺位（[uncertain — 2026 年是否有新的，没找到一手 source 确认有共识 benchmark]）。

## 给 Qwen eval 团队的可执行建议

1. **不要相信任何 "single number for VLA"**。Report 必须至少包含：1 个 sim suite（SimplerEnv 首选）+ 1 个真机 small-N（≥ 50 rollout/task）+ RoboArena 参与（哪怕只是 specialist 一档）。
2. **LIBERO 数字只作门槛**：< 95% 说明 policy 没收敛；≥ 95% 不能 claim 任何 frontier。建议把 LIBERO 移到 appendix，与 95% CI 一起报。
3. **CALVIN 可以彻底淘汰**，除非做 language-conditioned long-horizon 的专项 ablation。
4. **SimplerEnv 报告必须分 Visual Matching 与 Variant Aggregation 两栏**，并明示对应真机平台（Google Robot vs WidowX）。混报会丢掉 robustness 信息。
5. **如果做 humanoid / dexterous，提前承认"没有 standard"**，自建 task 时给出 ManiSkill 3 / RoboCasa 兼容的 task 定义文件，方便外部复现。
6. **任何 sim → real claim 必须给 sim2real correlation 数字**（哪怕是自家 internal 的 N=20 sample）。"我们在 sim 上 +10% 所以真机也好"是 2026 年的过时叙事。
7. **RoboArena 是值得投入的赛道**，类似当年加入 LMSYS。早进早立 task pool，对长期话语权重要。

## 未知与争议

- **LIBERO 替代品**：截至 2026-05 还没有一个公认的"LIBERO v2 / next"。社区候选有 LIBERO-Plus（[uncertain — 没找到一手 source 确认 2026 状态]）、Colosseum (Pumacay et al., [arxiv 2402.08191](https://arxiv.org/abs/2402.08191)，强调 perturbation robustness)，但都没拿到 LIBERO 那种全行业默认地位。
- **GR00T / π0.5 / Helix 等 frontier humanoid VLA 的 eval**：基本是公司自己挑 task 在自家硬件上跑，数字不可外部复现。[unknown — 没找到一手 source 表明 2026-05 有公开 humanoid VLA benchmark 达成共识]。
- **VLM-as-judge for VLA**：2025 起多篇 paper 用 GPT-4o / Gemini 看 rollout 视频判 success，免去人工 predicate（如 [arxiv 2503.xxxxx 系列，uncertain id]）。这条路看起来合理，但 judge bias / hallucination 的影响还没有系统研究。
- **OXE 后续**：是否会出一版"OXE-Eval"附带 held-out 协议？2024-2026 一直在讨论但没看到落地。

## 推荐外部材料

- [OpenVLA-OFT (arxiv 2502.19645)](https://arxiv.org/abs/2502.19645) — Stanford，明确写 "LIBERO is largely saturated"，是判定饱和的最直接 source。
- [SimplerEnv paper + site](https://simpler-env.github.io/) — sim2real correlation 数字的一手出处，做 VLA eval 必读。
- [RoboArena](https://robo-arena.github.io/) — 2025 H2 launch 的真机 crowd eval，目前最接近 frontier VLA leaderboard。
- [π0 / π0.5 tech blog](https://www.physicalintelligence.company/blog/pi0) — Physical Intelligence 对 generalist VLA eval 协议的 framing 值得读。
- [ManiSkill 3 (arxiv 2410.00425)](https://arxiv.org/abs/2410.00425) — GPU 并行 sim 基础设施王，VLA RL fine-tune 标配。
- [RoboCasa (arxiv 2406.02523)](https://arxiv.org/abs/2406.02523) — 看清"数据生成器"与"benchmark"区别的好例子。
- [Open X-Embodiment (arxiv 2310.08864)](https://arxiv.org/abs/2310.08864) — 理解 cross-embodiment 数据规模与 eval 协议缺位的根源。
- [Colosseum (arxiv 2402.08191)](https://arxiv.org/abs/2402.08191) — 强调 perturbation robustness，LIBERO 之后的候选之一。
