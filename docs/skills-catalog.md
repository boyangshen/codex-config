# 精选 Skills

这些技能按用途挑选，源代码固定到审查过的上游 commit；安装时不额外安装 Python 包。仓库 star 和技能下载量用于衡量采用度，不能证明技能在每个任务上都有效。

## 中文显示名称

| 显示名称 | 调用名称 |
|---|---|
| 协作预设：规划与审查 | `$plan-implement-review` |
| 完成前验证 | `$verification-before-completion` |
| Ponytail：极简编程 | `$ponytail` |
| 实验分析 | `$experiment-analysis` |
| 科研可视化 | `$scientific-visualization` |

## 编程

- **verification-before-completion**：让修复、测试、构建等结论对应到实际检查结果；未运行时直接说明。
- **ponytail**：优先复用现有代码、标准库和平台能力，以最小改动完整完成任务，保留必要的验证、错误处理、安全和可访问性。支持 lite、full（默认）、ultra 三档；本仓库安装独立 skill，不包含上游插件 hooks 和配套命令。

## 科研与实验

- **experiment-analysis**：本地自定义实验分析技能，读取日志、CSV/JSON 与消融结果，核对比较口径并输出 Markdown 报告；按需使用普通 Python 脚本，不要求 Notebook 或客户端文档工具。
- **scientific-visualization**：帮助设计诚实、可读、可复查的科研图表。可选工具示例需 Python 3.11+；目标期刊的实时要求仍需核验。

## 使用

已有 `install.sh` 会自动把 `skills/` 下的目录链接到 Codex 用户级 skills。新服务器克隆仓库后运行：

```bash
./install.sh --dry-run
./install.sh
```

来源、固定版本、许可证与本地改动见 [THIRD_PARTY_SKILLS.md](../THIRD_PARTY_SKILLS.md)。

```text
$ponytail 用最小的完整改动实现这个需求，优先复用项目现有能力。
```

## 实验分析使用示例

```text
使用 $experiment-analysis 分析当前项目已有实验结果，比较基线与改进方案，输出包含数据来源、对比表、结论和局限的 Markdown 报告；需要画图时结合 $scientific-visualization。
```
