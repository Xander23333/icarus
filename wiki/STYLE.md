# Writing style — vol1 Architecture chapters

读者 = 读者（Qwen agentic coding 数据+评测 owner，benchmark 圈业内知名）。读者懂 transformer 基础和 RL 基础，不要科普 attention 是什么。

## 硬规则
1. **每条非常识结论必须带 source 链接**（arxiv id / 官方 tech report URL / 公司 blog URL / 录像 timestamp）。
2. **不知道就说不知道**，写 `[uncertain]` 或 `[unknown — 没找到一手 source]`。绝不脑补补全。
3. **优先转述+引用**已有好材料（Lilian Weng / Sebastian Raschka / Stanford CS336 讲义 / Sasha Rush / 张俊林 / 苏剑林 / 官方 tech report）。在每节末尾加 "## 推荐外部材料" 列 3-8 条带 1 行点评的链接。
4. 中文写作，技术词保留英文。
5. 一节目标 4-10KB markdown。不要灌水，不要 marketing 腔。

## 每节模板
```
# {家族名}

## 路线定位（1 段，<150 字）
这个家族在当前 frontier 里占什么位置？和谁竞争？

## 代表模型清单
| 模型 | 发布日 | 参数/激活 | 关键变化 | 一手 source |

## 架构核心（按 paper 写的）
- bullet 列。每条带 source 行内引用 [^1]。
- 只写 paper / blog 明写的，不要"业界推测"。

## 训练方法核心
- pretrain（data scale, tokenizer, MuP, RoPE base 等只要 paper 写了就列）
- mid / annealing
- post-train（SFT / RLHF / RLVR / agentic RL）
- 算力（如果披露了）

## 与 eval / benchmark 的接口
- 官方报的 benchmark
- 第三方独立复现 / 质疑
- 已知的 contamination / overfit 信号

## 未知与争议
- 明确列出"这家公司没披露 X"
- 第三方 reverse-engineer 的推测（标 [推测]）

## 推荐外部材料
- [链接](url) — 1 行点评
```

## 路径与命名
- 输出目录：`/root/research-book/vol1-architecture/`
- 文件名：`{partLetter}{id}-{slug}.md`，例：`A1-gpt5-o-series.md`
- 引用统一用 markdown footnote 或行内 `[name](url)`
