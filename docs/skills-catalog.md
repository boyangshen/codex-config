# 精选 Skills

这些技能按用途挑选；第三方技能固定到审查过的上游 commit，本地协作技能随本仓库维护。安装时不额外安装 Python 包。仓库 star 和技能下载量用于衡量采用度，不能证明技能在每个任务上都有效。

## 中文显示名称

| 显示名称 | 调用名称 |
|---|---|
| 多步骤实施计划 | `$multi-step-plan` |
| 子代理计划执行 | `$subagent-plan-execute` |
| 完成前验证 | `$verification-before-completion` |
| 简洁编程准则 | `$karpathy-guidelines` |
| 科研可视化 | `$scientific-visualization` |

## 规划与执行

- **multi-step-plan**：本地自定义规划技能，将目标或已有方案写成多步骤 Markdown 计划，明确技术设计、依赖、专属子代理职责、产物、验收和交接；只要求规划时不启动实现或实验。
- **subagent-plan-execute**：本地自定义执行技能，主代理协调、每步专属子代理执行并提交证据，关键结果独立审查。模型和推理强度分别按用户最新指定、本任务已确认设置、环境默认/继承解析，支持按角色覆盖，不固定型号。

```text
$multi-step-plan 为当前任务生成多步骤实施计划，保存为 plan.md，只做规划。
```

准备执行时，模型和推理强度可以在调用中指定；下例仅是一次调用的选择：

```text
$subagent-plan-execute 按 plan.md 执行，子代理使用 gpt-6.1-sol，推理强度 high。
```

## 编程

- **verification-before-completion**：让修复、测试、构建等结论对应到实际检查结果；未运行时直接说明。
- **karpathy-guidelines**：减少臆造抽象、无关改动和不可能场景的防御性处理。小改动按实际需要处理，不强迫完整流程。

## 科研与实验

- **scientific-visualization**：帮助设计诚实、可读、可复查的科研图表。可选工具示例需 Python 3.11+；目标期刊的实时要求仍需核验。

## 使用

已有 `install.sh` 会自动把 `skills/` 下的目录链接到 Codex 用户级 skills。新服务器克隆仓库后运行：

```bash
./install.sh --dry-run
./install.sh
```

来源、固定版本、许可证与本地改动见 [THIRD_PARTY_SKILLS.md](../THIRD_PARTY_SKILLS.md)。

```text
$karpathy-guidelines 用清晰、最小的改动实现这个需求，保留必要验证。
```
