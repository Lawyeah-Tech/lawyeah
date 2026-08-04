# 贡献指南

## 变更边界

- 业务能力必须归入一个明确的法律业务领域，并在该领域内形成专业闭环。
- 不新增跨领域运行时 Skill，不用共享正文替代领域专业化。
- 不提交用户材料、凭证、访问令牌、原始检索记录或内部蒸馏证据。
- 不在未经确认时新增 MCP 工具名称、参数、端点或权限范围。

## Skill Pack 要求

- 使用小写字母、数字和连字符命名目录。
- 顶层 `SKILL.md` 的 YAML frontmatter 只包含 `name` 和 `description`。
- 从顶层 `SKILL.md` 直接链接任务所需资源，避免引用文件之间多跳加载。
- `pack.json` 必须符合 `schemas/pack.schema.json`。
- 只有完成专业内容和评测后，领域状态才能从 `planned` 改为 `active`。

## 提交前验证

```bash
python3 -m unittest discover -s tests -v
python3 tooling/validate_repository.py --root .
```
