# In-context & Scaling Limits

> Scaling laws 上界, ICL theory, sample complexity。

## 核心问题与 NTP 假设

跟踪：(a) 经典单调 scaling law 失效的反例与新法则（catastrophic overtraining、quantization degrade）；(b) 把"模型能力"沿容量 × 数据 × 任务三轴拆解的精细化 law；(c) NTP 在长 horizon imitation 下的样本复杂度紧界。这些都属于 **NTP-cap** 范畴——它们不主张 NTP 学不到某事，而是钉死 finite-resource 下的可达边界。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-22 | Shannon Scaling Law (Ouyang et al.) | LLM 训练 = noisy channel；SNR 不足时性能呈 U-shape；外推 12B/307B token 仍 R²=0.847 | cap | [2605.23901](../papers/paper_notes/2026-05-26-2605.23901-shannon-scaling-law.md) |
| 2026-05-18 | Predictable Confabulations (Smith et al.) | factual recall 在 (log params, log topic freq) 上 sigmoid；族内 R²=74–94% | cap | [2605.18732](../papers/paper_notes/2026-05-26-2605.18732-predictable-confabulations.md) |
| 2026-05-12 | Joint-KL AR Learning (Xu et al.) | approximation horizon-free；estimation 有 Ω(H) 信息论下界与 Õ(H) 上界匹配 | cap | [2605.12316](../papers/paper_notes/2026-05-26-2605.12316-joint-kl-autoregressive.md) |

## 当前共识 / 争议

- **共识浮现**：单调幂律不足以描述 LLM 训练；至少需要引入 SNR / U-shape / sigmoid 的非单调结构；hallucination 与 long-tail recall 是可预测的 SNR 现象。
- **争议**：长 horizon NTP 的 Ω(H) 是否能通过 RL/critic / planning loss 真正绕过——理论上界与算法实践的落差仍未量化。
- 仍待澄清：Shannon Scaling Law 假定的 Gaussian 噪声是否能覆盖 SFT 引入的结构化漂移。

## Open problems

- 把 Shannon SNR 视角与 superposition / knowledge capacity scaling 统一成一个 SNR-superposition 法则。
- 在 joint-KL Ω(H) 下界条件下，找出可使 estimation error 不再线性增长的额外结构（e.g. local Markov、context compression）。
- 长尾事实的 "频率代理" 度量改良——离开 web-frequency 后该 sigmoid 是否仍成立。
