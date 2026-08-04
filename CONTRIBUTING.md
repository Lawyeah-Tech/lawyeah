# 贡献指南

## 变更边界

- 业务能力必须归入一个明确的法律业务领域，并在该领域内形成专业闭环。
- 不新增跨领域运行时 Skill，不用共享正文替代领域专业化。
- 不提交用户材料、凭证、访问令牌、原始检索记录或内部蒸馏证据。
- 不在未经确认时新增 MCP 工具名称、参数、端点或权限范围。

## Skill Pack 要求

- 所有运行时路径使用英文 ASCII；目录和稳定 ID 使用小写字母、数字和连字符。
- 每个领域包必须包含一个能力导航 Skill；进入 `active` 前还必须包含至少一个原子 Skill。
- 每个 Skill 独占 `skills/<skill-id>/` 目录，名称以 `lawyeah-` 开头，且 YAML `name` 与目录完全一致。
- 每个 `SKILL.md` 的 YAML frontmatter 只包含 `name` 和 `description`。
- 原子 Skill 必须对应完整用户目标和可验收成果，不得把检索、读取材料或单个流程步骤拆成 Skill。
- Skill 运行时自包含，只能引用本 Skill 目录中的资源；相似 Skill 独立发展，不使用跨 Skill 共享正文或模板。
- 只使用 `depends-on`、`related-to` 和 `excludes` 描述关系；不得新增固定前后链或组合方案。
- `depends-on` 必须说明所需的具体业务成果，不能把其他 Skill 当作知识库。
- 法律文书模板放在所属原子 Skill 的 `assets/templates/`。
- MCP 能力按具体判断节点声明为 `required`、`recommended` 或 `optional`，不得在未经确认时写入工具参数或端点。
- `pack.json` 必须符合 `schemas/pack.schema.json`。
- 只有完成专业内容和评测后，领域状态才能从 `planned` 改为 `active`。

## 领域边界

- 原子 Skill 以用户主要目标和最终专业成果确定唯一主要领域。
- 相似 Skill 可以在不同领域独立发展，但不得共享运行时文件或版本。
- 公开边界结论更新到 `catalog/domains.json` 和 `docs/architecture/domain-boundaries.md`。
- 完整推导、信源、正反例和评测记录保存在被忽略的 `research/`，不得提交。

## 提交前验证

```bash
python3 -m unittest discover -s tests -v
python3 tooling/validate_repository.py --root .
```
