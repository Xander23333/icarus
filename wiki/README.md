# Wiki — 当前所有模型的架构、可解释性与评测

研究报告，三卷本。截至 2026-05。

## 目录

### [第一卷 · 架构](./vol1-architecture/) — 30 节
按当前还在迭代的活跃模型家族切片，不按教科书分类。
- **A** LLM 家族（10 节）：GPT-5/o-series、Claude 4.x、Gemini、Grok、Llama 4、DeepSeek、Qwen3、Kimi K2、GLM、edge-active
- **B** 非 Transformer（3 节）：SSM/Mamba、Diffusion LLM、Linear/Hybrid
- **C** 多模态（5 节）：Native multimodal、Adapter VLM、Video gen、Audio LLM、Any-to-any
- **D** 具身（6 节）：π0、Figure Helix、NVIDIA GR00T、Gemini Robotics、中国具身、VLA open baselines
- **E** 世界模型（5 节）：JEPA、Dreamer、Video-as-WM、Interactive WM、Spatial/3D WM
- **F** 类脑（1 节）：合写 SpikingBrain / Loihi / NorthPole 等

### [第二卷 · 可解释性](./vol2-interpretability/) — 8 节
- **I1** Mech interp 主线（SAE → transcoders → attribution graphs）
- **I2** RepE / activation steering
- **I3** Probing / logit lens / tuned lens / Patchscopes
- **I4** 工具链（TransformerLens / nnsight / SAELens / Neuronpedia / Goodfire）
- **I5** 多模态 / VLM 可解释性
- **I6** 具身与世界模型可解释性（坦诚承认空白）
- **I7** Reasoning / CoT 可解释性（faithfulness / steganography / monitorability）
- **I8** Safety-relevant interp（sleeper agents / alignment faking / MASK）

### [第三卷 · 评测](./vol3-evaluation/) — 11 节
- **Ev1** 通用知识与推理（MMLU-Pro、GPQA、HLE、ARC-AGI）
- **Ev2** 数学（AIME、MATH-500、FrontierMath、Putnam-AXIOM）
- **Ev3** 代码（LiveCodeBench、BigCodeBench、Aider polyglot、CRUXEval）
- **Ev4** Agentic + tool use（SWE-Bench Verified、Terminal-Bench、TAU-Bench、BrowseComp、GAIA、OSWorld）
- **Ev5** 多模态（MMMU/Pro、MMBench、Video-MME、OmniBench）
- **Ev6** 长上下文（RULER、HELMET、NoCha、Fiction.LiveBench，NIAH 之死）
- **Ev7** 具身（CALVIN、LIBERO、SimplerEnv、RoboArena）
- **Ev8** 世界模型（VBench、VBench-2.0、Physics-IQ、WorldModelBench）
- **Ev9** 安全（HarmBench、AIR-Bench、MASK、Sorry-Bench、StrongREJECT、WMDP、AgentHarm）
- **Ev10** 评测元问题（contamination、Goodhart、saturation、judge bias）
- **Ev11** 公开 leaderboards（LMArena、Artificial Analysis、OpenCompass、SEAL）

## 写作规范

见 [STYLE.md](./STYLE.md)。核心原则：**宁可无知，不要不准确**。每条非常识结论带 source 链接（arxiv id / 官方 blog / tech report）；找不到 source 一律标 `[unknown]` / `[uncertain]` / `[推测]`。

## 全卷大纲

见 [OUTLINE.md](./OUTLINE.md)。
