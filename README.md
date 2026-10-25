# 个人 Codex 配置

保存个人 skills、通用协作 Prompt 和精选配置，用于更换服务器后恢复。

## 新服务器安装

需要 Git、已配置好的 GitHub SSH 访问，以及 Python 3.11+。Python 3.10 可在自己的 Python 环境中安装 `tomli`，并通过 `CODEX_CONFIG_PYTHON` 指定解释器。

```bash
git clone git@github.com:boyangshen/codex-config.git ~/codex-config
cd ~/codex-config
./install.sh --dry-run
./install.sh
```

安装会合并 `codex/shared-config.toml` 中的设置，保留本机其他配置及项目路径。冲突的旧文件会先备份到 `~/.codex/backups/codex-config/`；登录信息不进入本仓库。无法安全合并的 TOML 布局会报错，不覆盖原配置。

自定义 skill 通过软链接加载到 `~/.agents/skills/`，并兼容 `~/.codex/skills/`。原 skills 先备份，不影响内置 `.system`。

```text
$plan-implement-review 帮我规划这个需求，并输出给 Gemini 的完整 Prompt。
```

## 自动拉取后启动

```bash
~/.local/bin/codex-personal
```

启动器先执行快速前进拉取并重新安装，再启动原来的 `codex`。仓库有未提交改动、网络或认证不可用时，明确提示并使用本机已有配置启动，不自动覆盖或提交。Linux 有 `timeout` 时，网络拉取最多等待 20 秒；安装阶段不会被该超时中断。

普通 `codex` 命令仍使用本机当前配置，不会自动拉取。可以自行将 `~/.local/bin` 加入 PATH，使用 `codex-personal` 作为常用入口。临时跳过自动同步：

```bash
CODEX_CONFIG_AUTO_SYNC=0 ~/.local/bin/codex-personal
```

## 修改与上传

skill 链接直接指向本仓库，修改 `skills/plan-implement-review/` 即可。修改本机模型偏好或 `/presets` 后，可以重新导出白名单内的设置：

```bash
./install.sh --capture
git diff
git add skills codex docs
git commit -m "Update personal Codex preferences"
git push
```

`--capture` 仅导出模型/推理设置、界面主题和输入 presets 等明确允许的字段；不导出项目 trust、MCP 凭据、服务地址或主机路径。当前初始快照没有配置 `/presets` 槽位，因此不虚构槽位内容。

presets 采用合并方式：更新仓库中存在的槽位，保留本机额外槽位。删除仓库中的槽位不会自动删除其他服务器的本地槽位。

其他服务器执行 `./sync.sh`，或通过 `codex-personal` 启动时拉取。多机编辑产生分叉时，停止自动拉取并由用户处理，不自动 reset、rebase 或 push。

## 包含内容

- `skills/plan-implement-review/`：规划、实现交接与独立审查；每次规划/审查附可直接复制给 Gemini 的完整 Prompt。
- `skills/experiment-analysis/`：读取已有实验结果，整理对比、消融和 Markdown 报告；可结合科研可视化画图。
- `codex/shared-config.toml`：白名单导出的可迁移偏好。
- `docs/`：通用协作方案与 Prompt。
- `install.sh`、`sync.sh`、`bin/codex-personal`：安装、同步和启动入口。
- `tests/`：合并、备份、重复安装和白名单验证。

账号登录、SSH 私钥、`auth.json`、聊天历史、数据库、日志和缓存不在本仓库中。新服务器仍需完成自己的 Codex 登录和 GitHub 认证。

## 验证

```bash
python3 -m unittest discover -s tests -v
```

官方行为参考：[本地 skill 与软链接](https://learn.chatgpt.com/docs/build-skills)、[用户配置](https://learn.chatgpt.com/docs/config-file/config-basic)。


## 推荐 Skills

精选编程、科研和实验整理技能及采用度、许可证说明见 [技能目录](docs/skills-catalog.md) 与 [第三方来源记录](THIRD_PARTY_SKILLS.md)。这些技能会随仓库现有安装器同步。
