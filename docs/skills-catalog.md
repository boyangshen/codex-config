# 精选 Skills

这些技能按用途挑选，源代码固定到审查过的上游 commit；安装时不额外安装 Python 包。仓库 star 和技能下载量用于衡量采用度，不能证明技能在每个任务上都有效。

## 中文显示名称

| 显示名称 | 调用名称 |
|---|---|
| 协作预设：规划与审查 | `$plan-implement-review` |
| 系统化调试 | `$systematic-debugging` |
| 完成前验证 | `$verification-before-completion` |
| 简洁编程准则 | `$karpathy-guidelines` |
| 科研可视化 | `$scientific-visualization` |

## 编程

- **systematic-debugging**：先复现并沿数据/调用链找原因，再做小范围修复。用于 bug、测试失败和异常行为。已调整成按问题复杂度调查，并移除上游测试提示样例和无关的多层校验建议。
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

## 官方实验分析模板

官方 `artifact-template-experiment-analysis` 用于把假设、方法、结果、解释、局限和下一步整理成实验报告。它来自已安装的官方模板插件，生成成品文档需要客户端提供文档生成功能。实验图表可结合本仓库的科研可视化技能。
