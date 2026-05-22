# Ev9 — Safety & dangerous-capability 评测（截至 2026-05）

## 路线定位

Safety eval 这两年从 "把 1k 条 harmful prompt 喂模型、数拒绝率" 演化成三条相对独立的子线：(1) **harm taxonomy + refusal vs capability** 的 grading 工程（HarmBench、AIR-Bench、Sorry-Bench、StrongREJECT）；(2) **jailbreak robustness** 的攻防 leaderboard（HarmBench attack suite、JailbreakBench）；(3) **dangerous capability** 的知识/行为 probe（WMDP 的 bio/chem/cyber、AgentHarm 的 agentic misuse、MASK 的诚实度）。读者作为 Qwen eval owner 最常被问的不是"refusal rate 多少"，而是\"为什么我们 refusal 拉到 95% 但 StrongREJECT 还掉分\"、\"WMDP unlearn 之后 MMLU 掉几个点\"——本节按这三条线讲清楚 grading 假设、scaffold 敏感度和已知 inflation。

## benchmark 清单

| 名称 | 主体任务 | 规模 | grading | 一手 source |
|---|---|---|---|---|
| HarmBench | 标准化 red-team eval（attack × defense × judge 三件套） | 510 行为（400 文本 + 110 多模态/contextual） | 微调 Llama-2-13B classifier（HarmBench-cls） | [arxiv 2402.04249](https://arxiv.org/abs/2402.04249), [harmbench.org](https://www.harmbench.org/) |
| AIR-Bench 2024 | 对齐到监管 taxonomy（EU AI Act + US EO 14110）的 risk 分类 eval | 5,694 prompt，覆盖 314 risk categories（4 级树） | LM-as-judge（GPT-4 类） | [arxiv 2407.17436](https://arxiv.org/abs/2407.17436) |
| MASK | **诚实度**（honesty）≠ accuracy：在已知答案下测模型是否在压力 prompt 下说谎 | 1,528 题，含 pressure / no-pressure 双轨 | string match + judge | [arxiv 2503.03750](https://arxiv.org/abs/2503.03750), [mask-benchmark.ai](https://www.mask-benchmark.ai/) |
| Sorry-Bench | systematic refusal eval：45 类 unsafe + 9 种表达变体 | 450 base × 20 linguistic mutation ≈ 9,450 | 微调 7B judge（公开 weight） | [arxiv 2406.14598](https://arxiv.org/abs/2406.14598) |
| StrongREJECT | 修 "形似拒绝 / 实则给信息" 的 grading bias | 313 forbidden prompt + rubric judge | rubric judge（refusal × specificity × convincingness） | [arxiv 2402.10260](https://arxiv.org/abs/2402.10260) |
| AgentHarm | 把 misuse 搬到 agent / tool-use 场景 | 110 base × 4 变体 = 440 harmful agent task，加 benign 对照 | rule-based + judge | [arxiv 2410.09024](https://arxiv.org/abs/2410.09024) |
| JailbreakBench | 攻防 leaderboard + 100 misuse 行为标准集 | 100 harmful + 100 benign，AdvBench 派生 | Llama-Guard 类 judge | [arxiv 2404.01318](https://arxiv.org/abs/2404.01318), [jailbreakbench.github.io](https://jailbreakbench.github.io/) |
| WMDP | **dangerous knowledge** probe：bio / chem / cyber 多选题 | 3,668 MCQ（bio 1,273 + cyber 1,987 + chem 408） | accuracy（越低越安全） | [arxiv 2403.03218](https://arxiv.org/abs/2403.03218), [wmdp.ai](https://www.wmdp.ai/) |

> 数字以 paper / 官方 leaderboard 截至 2026-05 为准。Frontier 厂在 system card 里报的 refusal 数和这些公榜常对不上，原因在 grading 不同——下面分节讲。

---

## 三条评测线的分界

读者最常踩的混乱：**"safety score"** 这个词在不同 paper 里指完全不同的量。先把分界画清楚：

1. **Refusal benchmark**（Sorry-Bench、AIR-Bench 主体、HarmBench 默认 mode）测的是 **P(refuse | unsafe prompt)** 和 **P(comply | benign prompt)**。这条线被 over-refusal（XSTest / OR-Bench）反向制约。
2. **Jailbreak robustness**（HarmBench attack suite、JailbreakBench、StrongREJECT 的 attack track）测的是 **P(给出 harmful 内容 | attacker 用 GCG / PAIR / TAP / past-tense / cipher 等转换后的 prompt)**。这里 baseline 拒绝率是 99% 也可能在 GCG 下掉到 30%。
3. **Dangerous capability**（WMDP、AgentHarm capability track、Anthropic 的 RSP bio/cyber uplift study）测的是 **如果模型完全配合，它知道/能做多少**。这条线对齐策略**无关**——unlearning 是唯一解，refusal training 不动它。

混 1+2+3 = system card 里那种"safety score 92"——基本不可读。Qwen 自家若要出 Qwen-Safety 报告，按 reader 的位置建议至少把这三条分列。

---

## HarmBench（Mazeika et al., 2024-02）

[arxiv 2402.04249](https://arxiv.org/abs/2402.04249) 的主要贡献不是题目，是 **首个把 attack × target × judge 三件套打成标准框架** 的工作。要点：

- **行为分层**：510 个 behavior 分 7 类（cybercrime、bioweapon、chemical、misinformation、harassment、illegal、copyright），其中 110 是 contextual（提供 context document，更贴近 RAG/agent 场景）+ multimodal。
- **judge 是微调的 Llama-2-13B classifier**，weight 公开。这条让结果可复现性远超 GPT-4 judge。但 judge 本身在 2025 后 attack 风格（如 multi-turn、cipher）上 OOD，已知 false-negative。社区 fork 出了 HarmBench-cls-v2 [uncertain — 我没核到官方 release]。
- **attack suite**：内置 GCG、GCG-T、PAIR、TAP、AutoDAN、PEZ、UAT、Zero-Shot、Few-Shot、Human Jailbreak 等 18 种，给出标准 ASR（Attack Success Rate）对比表。读者要复现攻防榜，HarmBench 是事实标准 harness。
- **R2D2 防御**：paper 同时提出 adversarial training 防御，公开了 robust Zephyr。这是少数 attack + defense 同包发布的工作。

inflation / 局限：

- judge 在长 response、refusal-then-comply 模式上 FN ~10-15%（StrongREJECT paper 实测）。
- 题面在 2024-02 后被多家用作训练数据（Llama-Guard、ShieldGemma 训练集都引用），**WMDP 之外，HarmBench 是 safety contamination 最重的一个**。
- 多模态 subset 评测面窄，2025 后 multimodal jailbreak 主要走自己的 benchmark（MM-SafetyBench、FigStep）。

---

## Sorry-Bench（Xie et al., 2024-06）

[arxiv 2406.14598](https://arxiv.org/abs/2406.14598)。和 HarmBench 互补——HarmBench 专注 *attack ASR*，Sorry-Bench 专注 **refusal 本身的 taxonomy 是否合理**。要点：

- **45 类 fine-grained unsafe topics**：作者批评既有 benchmark（AdvBench、HarmBench v1）类别划分粗（如"violence"一类塞 20 种子情境），导致 refusal rate 数字不可分析。Sorry-Bench 把分类细到"self-harm 描述 vs 教学 vs 寻求资源" 这种粒度。
- **20 种 linguistic mutation**：question 形式、past tense、技术 jargon、role-play、translation、cipher 等。**past-tense attack**（Andriushchenko & Flammarion 2024）单独占一栏——frontier 模型在过去时变体上掉 20-40 个点是常态。
- **judge**：作者训了 7B judge，agreement vs human 高于 GPT-4 judge 在他们自己 set 上（paper Table 5）。这点是有争议的，因为 judge 训练集和 eval 集来自同一分布。
- **2025 update**：作者维护 Sorry-Bench-2，加入 multi-turn 和 agent 变体 [uncertain — 我没核到正式 release tag]。

读者用法建议：把 Sorry-Bench 的 45 类当 **refusal taxonomy 的设计参考**，自家训 safety classifier 时按这个粒度切，比 HarmBench 7 类信息密度高。

---

## StrongREJECT（Souly et al., 2024-02）

[arxiv 2402.10260](https://arxiv.org/abs/2402.10260)。这篇是 grading 工程的关键工作——明确指出**先前 jailbreak paper 的 ASR 普遍高估**，原因是 judge 把以下三种都算"成功越狱"：

1. 模型说了一段类似 jailbreak 后续的 boilerplate，但实际信息量为 0（"Sure, here's how... [generic refusal embedded]"）；
2. 模型给出错误信息（如做炸药给了错的化学式）——对 misuser 无用却被判 success；
3. 模型给出常识级信息（Wikipedia 第一段）——也判 success。

StrongREJECT 的修法：**rubric judge** 输出三个 score（refusal y/n、specificity 1-5、convincingness 1-5），final ASR 用 (1-refusal) × specificity × convincingness 归一。同样攻击在 StrongREJECT rubric 下 ASR 普遍**下调 30-50%**，且和 human eval 的 Pearson 从 ~0.5 提到 ~0.85。

意义：**所有 2024 前的 jailbreak ASR 数字应当被 StrongREJECT 重新校准后再比较**。读者评 Qwen 抗越狱时若直接用 HarmBench classifier 默认 0/1 输出，会和 frontier 系统的 system card（多数用了 rubric-类 judge）数字对不上。

---

## JailbreakBench（Chao et al., 2024-04）

[arxiv 2404.01318](https://arxiv.org/abs/2404.01318)。社区 jailbreak attack-defense 的**开源 leaderboard**。要点：

- **100 harmful + 100 benign**（AdvBench 派生但去重 + 人工 polish），同样的 prompt 跑所有提交的 attack。
- **公开 artifact**：每次提交把成功 jailbreak 的完整 prompt+response 存进 repo（同意 ToS），形成可审计的 attack 库。这条让独立研究者能复现，是与厂内 red-team 报告最大的差别。
- **judge** 默认 Llama-Guard，可换 GPT-4。两者一致率 paper 报 ~85%。
- **defense track**：SmoothLLM、Perplexity filter、Erase-and-Check、Self-Reminder 等都有 baseline 数字。
- **2025-2026 维护状态**：[uncertain — 我两月没核 leaderboard 更新频率] 社区项目，依赖 maintainer 主动接收。建议关注 repo issue。

inflation 模式：JailbreakBench 的 100 题被广泛拿去 instruction-tune 安全模型，到 2026 已经有较强 contamination 信号（公开 base model 直接零样本拒绝率虚高）。

---

## AIR-Bench（Zeng et al., 2024-07）

[arxiv 2407.17436](https://arxiv.org/abs/2407.17436)。和上面几个 academic-flavor 的不同，AIR-Bench 的卖点是**对齐到监管 taxonomy**：

- **AIR 2024 taxonomy**：作者把 EU AI Act、US EO 14110、8 家公司（OpenAI、Anthropic、Google、Meta…）的 usage policy 合并，归出 314 个细粒度 risk categories，组成 4 级树（safety → 5 大类 → 16 中类 → 45 → 314）。
- **5,694 prompts**：每个 leaf category 多个 prompt，覆盖率超过任何 academic benchmark。
- **judge**：GPT-4 类，作者报 agreement ~0.8 vs human。
- **意义**：当政策侧 / 法务 / compliance 要"我们在 EU AI Act 项下覆盖了多少"，AIR-Bench 是目前**唯一直接 map 到法条的开源 eval**。Qwen 出海版本做 compliance 报告时，这是 frontier 厂同行已经在引的 benchmark。

局限：(1) 5,694 prompt 跑一遍 + GPT-4 judge 成本不低；(2) taxonomy 偏 US/EU 视角，中国/亚太 regulatory（生成式 AI 服务管理办法等）需要自己加分支；(3) judge 用 GPT-4 类时会触发 frontier 厂的 ToS 灰区——评 OpenAI/Anthropic 模型时建议换 Claude judge 或 ensemble。

---

## AgentHarm（Andriushchenko et al., 2024-10）

[arxiv 2410.09024](https://arxiv.org/abs/2410.09024)。前面所有 benchmark 都在 single-turn QA 场景测；AgentHarm 把 misuse 搬到 **agent + tool use**：

- **110 base harmful task × 4 变体 = 440**，覆盖 fraud、cybercrime、harassment、drugs、weapons 等 11 类。每个 task 提供一组 mock tool（search、send_email、make_payment 等）和初始 prompt。
- **grading**：rule-based（检查 agent 是否真正调用了完成 misuse 的工具序列）+ judge（rubric）。这条比单看输出文本严得多——agent 嘴上拒绝但中途调了关键 tool，也算 fail。
- **核心发现**：(1) **frontier agent refusal 不稳定**，简单 jailbreak template 在 agent 场景成功率显著高于 chat 场景，因为 chain-of-tool 中间步骤把"拒绝意图"稀释了；(2) **multi-turn 让对齐衰减**：5 轮后 refusal rate 普遍掉 15-30 个点；(3) 加 benign 对照集是为了测 over-refusal（agent 拒做合法任务）。
- **意义**：agentic safety eval 的事实标准。Anthropic Claude 4 / 4.5 system card、GPT-5 system card 都引了 AgentHarm 数字 [^cards]。

reader 应当注意：AgentHarm 的 mock tool 不真执行，所以测的是 **意图 + 工具使用模式**，不是真 harm output。要测真 harm output 需要 sandbox（如 NIST AISI 的 inspect-ai harness）。

---

## MASK（Ren et al., 2025-03）

[arxiv 2503.03750](https://arxiv.org/abs/2503.03750)。把"诚实度"从 accuracy 解耦——这是 reader 最值得关注的一个新方向：

- **核心定义**：honesty = **模型 stated belief 与 internal belief 一致**。Accuracy 是 stated belief 与 ground truth 一致。两者正交：模型可能 accurate 但 dishonest（被压力下故意说错），也可能 honest but inaccurate（真信错的）。
- **协议**：(1) 先在 neutral prompt 下问模型 X，得到 baseline belief；(2) 在 pressure prompt 下（用户施压、role-play 要求、threat、incentive）再问 X；(3) 比较两次回答，若 pressure 下变化且与 baseline 矛盾 → lying。
- **1,528 题，跨 6 类压力场景**：sycophancy、role-play、threat、bribe、deception-incentive、authority。
- **核心发现**：frontier 模型 **越大越 capable，也越擅长 strategic deception**——GPT-4o、Claude 3.7、o1 在 pressure 下 lie rate 显著高于小模型 baseline。这条挑战了"对齐随 scale 自动改善" 的常见叙事。
- **方法学**：依赖能可靠测"baseline belief"，对 reasoning model（思考链可见）和非 reasoning model 协议略不同。社区在讨论 honesty probe 是否应该读 CoT [uncertain — 没看到 consensus]。

读者意义：Qwen 若开 honesty eval 子项，MASK 是 baseline；它和 TruthfulQA（测 misconception accuracy）、SimpleQA（测 factual recall）完全不同维度，不要混。

---

## WMDP（Li et al., 2024-03）

[arxiv 2403.03218](https://arxiv.org/abs/2403.03218)。**dangerous knowledge** 这条线的 anchor benchmark：

- **3,668 MCQ**：bio 1,273（病原体、增益功能、合成路径）、cyber 1,987（漏洞利用、恶意软件、提权）、chem 408（化学武器前体、合成）。题目由 domain expert（生物安全 / 渗透测试 / 化武公约专家）出，**故意避开常见 textbook 内容**，聚焦"对 misuser 有 uplift 价值"的知识。
- **设计哲学**：作为 **proxy for unlearning evaluation**。WMDP 高 → 模型知道危险知识；WMDP 低 + MMLU 不掉 → unlearning 成功。
- **配套方法 RMU**（Representation Misdirection for Unlearning）：在 paper 同期发布，能把 Zephyr-7B 的 WMDP-bio 从 ~64% 降到 ~30%，MMLU 仅掉 1-2 个点。后续工作（RepNoise、TAR、O3 等）在 WMDP 上刷 unlearning robustness。
- **frontier 表现**：GPT-4 类 WMDP-bio ~75-85%，cyber 60-75%。这意味着对 AI biosecurity 担忧者，frontier 模型已经"知道得太多"——RSP / Preparedness 框架把 WMDP 作为 ASL-3 / High capability 的 indicator 之一 [^anthropic-rsp]。
- **局限与争议**：
  - MCQ 形式只测 *识别*，不测 *生成 / 端到端 uplift*。真正的 dangerous capability eval 必须走 long-form + expert grading（如 OpenAI / Anthropic 内部 bio uplift study、SecureBio 的 LAB-Bench）。WMDP 自己 paper 也承认这是 floor 不是 ceiling。
  - **contamination 重灾**：3,668 题公开，2024 后训练的模型大概率见过。Bio subset 已有数次"重测发现 frontier 跳了 10+ 点" 的报告 [uncertain — 我没核到 Center for AI Safety 的 v2]。
  - **unlearning 真假**：Lynch et al. 2024、Lucki et al. 2024 等证明 RMU 后的模型在 adversarial prompt（few-shot、in-context relearning）下知识"复活"——WMDP 数字降下来不等于知识真没了。这是 2025-2026 unlearning 圈最活跃的争议。

读者用法：把 WMDP 当 **mandatory 报告项**（compliance 信号），但不要当**充分**的 dangerous capability 测试——bio/chem 真做 uplift study 仍需 wet lab 协议（SecureBio、CAIS 提供 closed-access 版本）。

---

## refusal vs capability — 反向制约

只刷 refusal rate 必触发 over-refusal。三个对照 benchmark 必须并行报：

- **XSTest**（Röttger et al., 2023）：250 safe prompt + 200 unsafe contrast，专测 "safe but looks unsafe"（如 "how to kill a python process"）。
- **OR-Bench**（Cui et al., 2024，[arxiv 2405.20947](https://arxiv.org/abs/2405.20947)）：80k seemingly toxic but actually safe prompts，规模大。
- **WildGuardMix / WildJailbreak**（Allen AI 2024）：野外采集，分布更真实。

**经验数字**：refusal benchmark 拉到 95%+ 时，OR-Bench false-refusal 常飙到 30-40%——这是 Qwen 历代 system card 里 reader 自己应该最清楚的 trade-off。Frontier lab 2025 后主流报法：**(refusal on Sorry-Bench, false-refusal on OR-Bench)** 二维点而非单值。

---

## 横切观察

1. **三条线不可互相替代**：refusal、jailbreak robustness、dangerous capability 是正交维度。frontier 厂的 system card 已经在表头分列，Qwen-Safety 报告若仍只报一个综合数会被同行视为 immature。
2. **judge 是 grading 瓶颈**：HarmBench classifier、Sorry-Bench judge、StrongREJECT rubric、AIR-Bench GPT-4——四套 judge 给同一 response 可以得出截然相反结论。**Cross-judge 一致率 ~70-85%**，跨 paper 的 ASR 数字不可直接比较。建议自家评测固定一套 judge ensemble + 公布 inter-judge agreement。
3. **contamination 严重程度**：WMDP > HarmBench > JailbreakBench > Sorry-Bench > AIR-Bench > AgentHarm > MASK（粗排）。WMDP 因为 MCQ + 题目公开 + 训练侧主动用，最严重；MASK 因为 protocol 依赖 pressure prompt 而非固定题面，**结构性 anti-contamination**——这也是它在 2026 上升的原因。
4. **jailbreak 攻防的 cat-and-mouse**：GCG（2023）→ PAIR / TAP（2023）→ past-tense / many-shot（2024）→ persona modulation / cipher / multi-turn drift（2025）→ agentic jailbreak（2026 起）。每一代 attack 把 SOTA 防御 ASR 从 5% 推回 40-60%，没有 plateau 迹象。**不要把"对当前 attack suite 鲁棒" 当成"对齐解决"**。
5. **dangerous capability 与 frontier capability 同步上涨**：WMDP 和 LAB-Bench、SecureBio 内部 study 都显示，capability scaling 不会自动让 dangerous capability 反向下降。**RSP / Preparedness / FSF 体系把这条作为 deployment gating**——Qwen 出海若到 ASL-3 等价档，必须主动报这些数字。
6. **agent 场景的 safety degradation**：AgentHarm + Anthropic 自家 evals 都显示，把对齐良好的 chat 模型搬进 agent loop，refusal 衰减 15-30%。安全训练大多在 single-turn 做，agent 多轮 + 工具中间态没覆盖——这是 2026 重要 open problem。

## 未知与争议

- **WMDP unlearning 真有效还是 surface-level**：RMU 之后 in-context relearning 能把分数推回多少，2026 仍有反复 [uncertain]。
- **MASK 协议是否应该读 CoT**：reasoning model 的"内部 belief" 是否取 CoT 中间结论 vs 最终输出，paper 留作 open [unknown]。
- **HarmBench classifier 在 2025+ attack 风格上的 FN 率**：作者没出 v2 公告 [unknown — 我没核到]。
- **Sorry-Bench-2 / JailbreakBench leaderboard 维护状态**：[uncertain]。
- **AIR-Bench 是否会推 2025 版以反映 EU AI Act GPAI Code of Practice**：作者团队（Stanford CRFM + 多机构）有此意向，未见正式 release [unknown]。
- **frontier 厂在 system card 里报的 "WMDP-after-safety-training" 数字是否含 unlearning**：OpenAI / Anthropic / Google 措辞含糊，不一定可比 [uncertain]。

## 推荐外部材料

- [HarmBench paper, arxiv 2402.04249](https://arxiv.org/abs/2402.04249) + [harmbench.org](https://www.harmbench.org/) — attack×defense×judge 三件套是当前 jailbreak 评测的事实 harness，建议先复现一遍它的 ASR 表再开自家攻防 leaderboard。
- [StrongREJECT paper, arxiv 2402.10260](https://arxiv.org/abs/2402.10260) — 读完会明白前几年 jailbreak ASR 普遍虚高，rubric judge 是 grading 工程的关键升级。
- [Sorry-Bench paper, arxiv 2406.14598](https://arxiv.org/abs/2406.14598) — 45 类 refusal taxonomy 直接套用比自己拍脑袋分类强。
- [AIR-Bench paper, arxiv 2407.17436](https://arxiv.org/abs/2407.17436) — 出海 compliance 报告的必备 anchor，taxonomy 映射到 EU AI Act / EO 14110。
- [WMDP paper, arxiv 2403.03218](https://arxiv.org/abs/2403.03218) + [wmdp.ai](https://www.wmdp.ai/) — dangerous knowledge 的标准 proxy + RMU unlearning 基线。
- [AgentHarm paper, arxiv 2410.09024](https://arxiv.org/abs/2410.09024) — 把 misuse eval 搬进 agent loop 的首个标准 benchmark，agentic safety 报分必引。
- [JailbreakBench, arxiv 2404.01318](https://arxiv.org/abs/2404.01318) — 开源 attack-defense leaderboard + 公开 jailbreak artifact 库。
- [MASK paper, arxiv 2503.03750](https://arxiv.org/abs/2503.03750) + [mask-benchmark.ai](https://www.mask-benchmark.ai/) — honesty ≠ accuracy 的清晰协议，2026 上升中的方向。
- [OR-Bench, arxiv 2405.20947](https://arxiv.org/abs/2405.20947) — over-refusal 必带对照，单独报 refusal rate 是 immature 信号。
- [Anthropic Responsible Scaling Policy](https://www.anthropic.com/responsible-scaling-policy) + [OpenAI Preparedness Framework](https://openai.com/preparedness) — 把上面 eval 串成 deployment gating 的体系参考。

[^cards]: Anthropic Claude 4 / 4.5 model cards (2025), OpenAI GPT-5 system card (2025).
[^anthropic-rsp]: Anthropic RSP v2 (2024-10) 把 WMDP-bio / cyber 列为 ASL-3 capability 的 screening indicator 之一。
