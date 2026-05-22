# 多模态评测 (Multimodal Benchmarks)

## 路线定位

到 2026-05，多模态 eval 基本分三层：(1) **图像理解学术 suite**（MMMU/MMMU-Pro、MMBench、MM-Vet、MathVista、BLINK、OCRBench、ChartQA）—— 大厂 tech report 必报；(2) **视频/全模态**（Video-MME、OmniBench、MVBench 等）—— 仍在快速迭代，每家测法不一致；(3) **真实世界 / 用户向**（RealWorldQA、LMArena Vision、WildVision）—— 接近线上口碑。前沿 GPT-5、Gemini 2.5、Claude 3.7/4、Qwen2.5-VL/Qwen3-VL、InternVL3 在主流静态集已饱和（MMMU 80+、MMBench 88+），讨论价值正在快速转向 video / agentic / robustness 子轴，以及 contamination 与 prompt sensitivity。读者做 Qwen-VL 评测可直接以本节为「先报哪几个、能信哪几个」清单。

## 代表 benchmark 清单

| Benchmark | 出处 | 规模 | 测什么 | 当前 SOTA (2026-05, [uncertain] 标注以一手 source 为准) |
|---|---|---|---|---|
| MMMU | arxiv [2311.16502](https://arxiv.org/abs/2311.16502), CVPR'24 | 11.5K 大学考题, 30 学科 | college-level multimodal reasoning | GPT-5 / Gemini 2.5 Pro ~82–84%，人类专家 88.6% |
| MMMU-Pro | arxiv [2409.02813](https://arxiv.org/abs/2409.02813) | 过滤纯文本可解 + 10-choice + vision-only | 抗 shortcut MMMU | top model 比 MMMU 下降 16–27pt，Gemini/GPT-5 ~65–70% |
| MMBench (v1.1 / dev) | arxiv [2307.06281](https://arxiv.org/abs/2307.06281) | ~3K 多选 EN/CN, 20 能力维度 | 细粒度能力诊断 + circular eval | 头部 90+，已基本饱和 |
| MM-Vet v1 / v2 | arxiv [2308.02490](https://arxiv.org/abs/2308.02490), v2 arxiv [2408.00765](https://arxiv.org/abs/2408.00765) | 218 / 517 开放问答 | 6 (v1) → 6+sequence (v2) 能力 GPT-4 judge 打分 | v2: GPT-5/Gemini 2.5 ~75–80 [uncertain] |
| MathVista | arxiv [2310.02255](https://arxiv.org/abs/2310.02255), ICLR'24 | 6141 视觉数学题 | 图表/几何/函数图 reasoning | testmini: 头部 78–82 |
| BLINK | arxiv [2404.12390](https://arxiv.org/abs/2404.12390), ECCV'24 | 3.8K, 14 任务 | 「人类秒答、VLM 翻车」的视觉感知（深度、IQ-test、jigsaw） | 人类 95.7%, GPT-4o 51.3%, 2026 头部 ~65–70 [uncertain] |
| OCRBench | arxiv [2305.07895](https://arxiv.org/abs/2305.07895)（v2 [2501.00321](https://arxiv.org/abs/2501.00321)） | 1000 / v2 10K | OCR + KIE + 手写 + 公式 + 表格 | v1 头部 850–900/1000；v2 头部 50–60% |
| ChartQA | arxiv [2203.10244](https://arxiv.org/abs/2203.10244), ACL'22 | 9.6K 图表问答 (aug+human) | chart reasoning | 头部 88–90+，逼近上限 |
| RealWorldQA | xAI blog [grok-1.5v](https://x.ai/news/grok-1.5v) (2024-04) | 765 真实世界拍摄题 | 物理空间常识 / 驾驶视角 | 头部 75–82，人类 ~95 |
| Video-MME | arxiv [2405.21075](https://arxiv.org/abs/2405.21075) | 900 视频 / 2700 QA, 短/中/长 | full-spectrum 视频理解 (含字幕版与无字幕版) | Gemini 2.5 Pro w/ subs ~85, GPT-5 w/o subs ~78 [uncertain] |
| OmniBench | arxiv [2409.15272](https://arxiv.org/abs/2409.15272) | 1142 三模态（图+音+文） | 必须同时用 image+audio 才能答 | 开源 OmniLLM 大多 <30%，Gemini 1.5 Pro ~47，2026 头部 60+ [uncertain] |

## 各 benchmark 设计要点 + 评测时的坑

### MMMU & MMMU-Pro
- MMMU 把大学六大学科（Art、Business、Science、Health、Humanities、Tech）30 个子学科的真题图配多选/填空，**heterogeneous image type** 是设计核心（图表 / 化学结构 / 乐谱 / 临床影像 / 工程图）[arxiv 2311.16502](https://arxiv.org/abs/2311.16502)。
- **shortcut 问题**：很多题目纯文本 LLM 不看图也能答对（GPT-4 text-only 在 MMMU 上仍能 ~30%）。MMMU-Pro [arxiv 2409.02813](https://arxiv.org/abs/2409.02813) 三步修复：① 删掉纯文本可解题，② 4-choice → 10-choice 降低猜测率，③ 增加 **vision-only setting**——把题干截图嵌入图片里，强迫模型 OCR 后再 reason。结果所有模型掉 16–27 pt，**视觉条件下 CoT 反而经常掉分**（论文 Table 5），说明很多 VLM 的 CoT 实际只对 text-grounded 推理 work。
- 评测建议：报数时**必须同时报 MMMU 和 MMMU-Pro (Vision)**，只报 MMMU 已经基本无信息量。
- contamination：MMMU 题目大量来自公开教材 / quiz 网站，2024 多篇（如 [arxiv 2406.04244](https://arxiv.org/abs/2406.04244) MMStar 论文）显示存在严重 train-time 泄漏；MMMU-Pro 部分缓解但 image 本身可能仍在 LAION-style 抓取里。

### MMBench
- 设计亮点是 **CircularEval**：把多选题 ABCD 选项循环替换 4 次都答对才算对，强行干掉 positional bias [arxiv 2307.06281](https://arxiv.org/abs/2307.06281)。
- 能力分类法 (L-1/L-2/L-3 共 20 类) 比 MM-Vet 更细，做能力差异诊断时优于单一总分。
- 但题目以单图 + 多选为主，**对长 reasoning / 长输出无区分度**，2025 起头部模型 dev 集刷过 88，已进入饱和段。
- 评测建议：把 MMBench 当 regression test 用，不要拿来排名 frontier 模型。

### MM-Vet v1 / v2
- v1 [arxiv 2308.02490](https://arxiv.org/abs/2308.02490) 用 GPT-4 作 judge，对 6 个核心能力（recog/OCR/knowledge/lang gen/spatial/math）开放问答打 0–1 连续分。
- v2 [arxiv 2408.00765](https://arxiv.org/abs/2408.00765) 加 **image-text sequence understanding** 子集，更贴 multi-image / 文档场景。
- 坑：**judge 模型升级 → 分数 drift**。论文官方用 GPT-4-0613，换 GPT-4o 或 Claude 后排名都会变；做 ablation 时务必固定 judge 版本。LM-as-judge bias 见 Ev10。

### MathVista
- 把 28 个已有视觉数学数据集 (含 IconQA, GeoQA, ChartQA, TabMWP 等) 重打包 + 加 3 个新集，testmini 1000 题最常用 [arxiv 2310.02255](https://arxiv.org/abs/2310.02255)。
- 优势是覆盖范围广（function plot / geometry / table）；缺点是**子集异质**——某模型在 ChartQA-style 暴涨能拉高总分但几何仍差。
- 2025 起 frontier 模型 testmini 已到 75–82，进入「靠 OCR + tool 也能刷」阶段。Qwen2.5-VL tech report ([arxiv 2502.13923](https://arxiv.org/abs/2502.13923)) 明确把 MathVista 视为「sanity check」而非 challenge。

### BLINK —— 目前最有区分度的感知 benchmark
- 14 任务（visual correspondence / relative depth / spatial reasoning / forensic detection / jigsaw / multi-view reasoning / IQ test...），人类几秒就能答 [arxiv 2404.12390](https://arxiv.org/abs/2404.12390)。
- 发布时（2024-04）GPT-4V 51.3%、Gemini 1.0 Pro 45.1%、人类 95.7%，**gap 比 MMMU 大得多**。
- 到 2026 头部模型也只爬到 ~65–70 [uncertain]，仍是衡量「模型有没有 actual visual perception」最干净的集。
- 评测建议：把 BLINK 当 **frontier perception** 主指标之一；可视化 per-task radar 比单一总分有用得多（不同模型短板差异极大）。

### OCRBench (v1 / v2)
- v1 800/1000 分制，五个子任务（text recognition / scene text VQA / doc VQA / KIE / handwritten math）[arxiv 2305.07895](https://arxiv.org/abs/2305.07895)。InternVL / Qwen-VL 系列在 v1 上长期 >850，专门为 OCR 优化的模型已基本刷穿。
- v2 [arxiv 2501.00321](https://arxiv.org/abs/2501.00321) 加 element parsing / math 公式 / 多语言 / 长文档，**v2 头部 50–60%**，区分度回来了。
- 评测建议：v1 只用来 sanity check，frontier 比较请用 v2。

### ChartQA
- 来自 Statista/Pew 的真实图表 + 人写 (human) 与模板生成 (augmented) 两批问答 [arxiv 2203.10244](https://arxiv.org/abs/2203.10244)。
- 评分用宽松匹配 (relaxed accuracy ±5%)，**对数字 reasoning 模型有利**；human split 比 aug split 更难。
- 2025 头部模型 ~88–90，**饱和**。新一代 chart benchmark（ChartQAPro [arxiv 2504.05506](https://arxiv.org/abs/2504.05506)、CharXiv [arxiv 2406.18521](https://arxiv.org/abs/2406.18521)）开始替代它做 frontier 评测，差距重新拉到 30+ pt。

### RealWorldQA
- xAI Grok-1.5V 发布时一起放出的 765 题集，全部来自真实拍摄（车载、室内、街景），强调**物理空间常识**（哪辆车先走、楼梯能不能下、门把手在哪）[xAI blog](https://x.ai/news/grok-1.5v)。
- 没有 paper，license 是 CC BY-ND 4.0，数据卡见 [HuggingFace xai-org/RealworldQA](https://huggingface.co/datasets/xai-org/RealworldQA)。
- 已成 GPT-5 / Gemini 2.5 / Claude 4 / Qwen-VL tech report 的默认 real-world 指标。坑：题目偏少 + 单图，方差较高；多种子 / 多 prompt 平均后再报。

### Video-MME —— 视频侧事实标准
- 900 video / 2700 QA，长度分 short (<2min) / medium (4–15min) / long (30–60min)，跨 6 大领域 30 子类 [arxiv 2405.21075](https://arxiv.org/abs/2405.21075)。
- 关键设计：**同时报 with-subtitle 与 without-subtitle**——多数模型字幕版高 8–15 pt，这把「真的看视频」vs「读字幕」拆开来。
- 也用 GPT-4 judge 打多选，contamination risk 低于图像集（视频源筛过且打了水印）。
- 评测时坑：**采样帧率 / 帧数严重影响分数**。1fps、8/16/32/64/128 帧的差距可达 5–10 pt，必须固定 protocol 且与 baseline 对齐（论文官方用 384 帧上限，但很多 open model 受 context 限制只用 16–32 帧）。
- 与 MVBench / LongVideoBench / EgoSchema 互补：MVBench 偏短视频动作识别，LongVideoBench [arxiv 2407.15754](https://arxiv.org/abs/2407.15754) 偏长视频检索式 QA，EgoSchema 偏第一人称长 reasoning。

### OmniBench —— image + audio + text 三模态
- 1142 题，**强制三模态联合**才能答对（如：图里是乐队，音频是 solo，问哪个乐手在 solo）[arxiv 2409.15272](https://arxiv.org/abs/2409.15272)。
- 设计哲学：单独看任一模态都不够 → 测「真 omni」而非 modality-by-modality 拼接。
- 发布时大多数开源 omni-LLM <30%，连 GPT-4o（image+audio 通道分开）也只 ~40–50。Gemini 1.5 Pro 报 ~47.3%。
- 到 2026-05 Gemini 2.5 / GPT-5 / Qwen2.5-Omni（[arxiv 2503.20215](https://arxiv.org/abs/2503.20215)）已能上 60+ [uncertain]，仍是 audio-image-text 联合最干净的 benchmark。
- 与 AV-Odyssey、WorldSense、MMAU 一起构成 audio-aware multimodal 评测最小集。

## Overfit / saturation / contamination 信号（重点）

读者做 Qwen-VL 这一档评测时，必须默认下面这些**已被独立验证**的问题：

1. **MMMU / MMBench / MM-Vet 都存在 text-only shortcut**。MMStar 论文 [arxiv 2406.04244](https://arxiv.org/abs/2406.04244) 系统测了 6 个主流 multimodal benchmark，发现 LLaVA-1.5 / GPT-4V 等不看图也能拿到 35–45% 的分。MMStar 自身就是「过滤掉这类题」的 1500 题精选集，应作为 MMMU 的补充必报项。
2. **CircularEval / option-shuffle 一刷就掉分**。MMBench、SEED-Bench 的 CircularEval 通常比单次评测低 5–15pt，这部分差距就是 positional/letter bias。报数时必须说明用了哪种 protocol。
3. **GPT-4 judge 升级 drift**。MM-Vet、Video-MME、WildVision 系列都受影响；2024 用 GPT-4-0613 vs 2026 用 GPT-5-judge 的绝对分不可比。
4. **训练集泄漏**：Qwen2-VL / InternVL2 等 tech report 都明列把 LLaVA-OneVision、ShareGPT4V、ScienceQA、ChartQA train 全收进来；这些 train 与 MMMU/MathVista/ChartQA test 高度同源。MMMU-Pro 部分缓解但远未根除。
5. **静态集饱和**：MMBench dev、ChartQA、OCRBench v1、MathVista testmini 头部模型差距已 <2pt，进入噪声内。frontier 比较请用 MMMU-Pro Vision、BLINK、OCRBench v2、CharXiv、Video-MME-Long-no-subs、OmniBench。
6. **视频 benchmark 的帧率/帧数偷分**：同模型在 Video-MME 上 16 帧 vs 128 帧能差 8pt 以上。各家 tech report 报的帧数往往不一致——比较时必须 normalize。
7. **「人类水平」标注本身有问题**。BLINK 95.7% 人类 score 来自众包，部分子任务（jigsaw、forensic）人类内部一致性也只有 80–85%；MMMU 的 88.6% 是 college students，不是 domain expert。读者引用「超越人类」时务必区分。

## 推荐 protocol（写在 tech report 里至少报这套）

针对 2026 frontier VLM evaluation，最小可信组合：

- 静态图像感知：MMMU-Pro (Standard + Vision) + BLINK + MMStar
- 文档/OCR：OCRBench v2 + DocVQA + CharXiv
- 数学/图表 reasoning：MathVista testmini + ChartQAPro + CharXiv reasoning split
- 真实世界 / 用户偏好：RealWorldQA + WildVision Arena
- 视频：Video-MME (long, no-subs) + LongVideoBench + EgoSchema
- 全模态：OmniBench + AV-Odyssey

每项报数时附带：(a) prompt 模板、(b) judge 模型版本、(c) 采样温度、(d) 视频帧数/帧率、(e) 是否用 CoT，否则视为不可复现。

## 未知与争议

- **GPT-5 / Claude 4 / Gemini 2.5 在 MMMU-Pro Vision 的具体分数** —— 一手 source 报数有口径差异 [uncertain]，建议引用时直接指 system card 而不是二手 leaderboard。
- **Anthropic 是否已内部 retire MMBench/MMMU**：Claude 4 system card 已大量改用 internal vision evals 与 RealWorldQA / Video-MME，但未明说弃用 [uncertain]。
- **OmniBench 2026 数据**：Qwen2.5-Omni、Gemini 2.5 在论文发布后是否报数 —— [unknown — 没找到一手 source]。
- **video benchmark 的 contamination 量级**：目前没有 MMStar 那种系统审计 [unknown]。

## 推荐外部材料

- [MMMU 官网 leaderboard](https://mmmu-benchmark.github.io/) — 同时收 MMMU 和 MMMU-Pro 最新榜单。
- [OpenCompass VLMEvalKit](https://github.com/open-compass/VLMEvalKit) — 一站式跑 30+ multimodal benchmark，国内外团队事实标准 harness。
- [lmms-eval](https://github.com/EvolvingLMMs-Lab/lmms-eval) — LMMs-Lab 的另一个主流 harness，Video-MME / MMBench / OmniBench 都内置。
- [MMStar paper (arxiv 2406.04244)](https://arxiv.org/abs/2406.04244) — 必读，量化了主流 VLM benchmark 的 shortcut 与泄漏比例。
- [CharXiv (arxiv 2406.18521)](https://arxiv.org/abs/2406.18521) — ChartQA 已饱和后的下一代 chart reasoning，frontier 模型仍掉到 50% 以下。
- [LongVideoBench (arxiv 2407.15754)](https://arxiv.org/abs/2407.15754) — Video-MME 的长视频补充，hour-level reasoning 的较干净测法。
- [Artificial Analysis Vision Arena](https://artificialanalysis.ai/) — 第三方维护的 vision/video model 价格-质量散点图，给商业模型横评最快。
