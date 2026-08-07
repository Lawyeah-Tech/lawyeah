# 贡献指南

## 变更边界

- 业务能力必须归入一个明确的法律业务领域，并在该领域内形成专业闭环。
- 不新增跨领域运行时 Skill，不用共享正文替代领域专业化。
- 不提交用户材料、凭证、访问令牌、原始检索记录或内部蒸馏证据。
- 只引用项目工具目录中已经稳定命名的 MCP 或宿主工具，不写入端点、凭证、内部字段或未经确认的参数。

## Skill Pack 要求

- 所有运行时路径使用英文 ASCII；目录和稳定 ID 使用小写字母、数字和连字符。
- 每个领域包必须包含一个能力导航 Skill；进入 `active` 前还必须包含至少一个原子 Skill。
- 每个 Skill 独占 `skills/<skill-id>/` 目录，名称以 `lawyeah-` 开头，且 YAML `name` 与目录完全一致。
- 每个 Skill 必须包含 `agents/openai.yaml`；顶层只允许 `SKILL.md`、`agents/`、`references/`、`scripts/` 和 `assets/`。
- 每个 `SKILL.md` 的 YAML frontmatter 只包含 `name` 和 `description`。
- 原子 Skill 必须对应完整用户目标和可验收成果，不得把检索、读取材料或单个流程步骤拆成 Skill。
- Skill 运行时自包含，只能引用本 Skill 目录中的资源；相似 Skill 独立发展，不使用跨 Skill 共享正文或模板。
- 只使用 `depends-on`、`related-to` 和 `excludes` 描述关系；不得新增固定前后链或组合方案。
- `depends-on` 必须说明所需的具体业务成果，不能把其他 Skill 当作知识库。
- 法律文书模板放在所属原子 Skill 的 `assets/templates/`。
- MCP 或宿主工具按具体判断节点条件引用，并说明业务用途、最小逻辑输入、结果使用和不可用行为；Skill 开发与发布不要求实际 MCP 注册、联调或真实调用。
- `pack.json` 必须符合 `schemas/pack.schema.json`。
- 只有完成专业内容和评测后，领域状态才能从 `planned` 改为 `active`。

## 领域边界

- 原子 Skill 以用户主要目标和最终专业成果确定唯一主要领域。
- 相似 Skill 可以在不同领域独立发展，但不得共享运行时文件或版本。
- 公开边界结论更新到 `catalog/domains.json` 和 `docs/architecture/domain-boundaries.md`。
- 完整推导、信源、正反例和评测记录保存在被忽略的 `research/`，不得提交。
- 不得把 `research/`、`evals/`、`tests/`、研发 Retrieval 地址、私有库标识或本地绝对路径复制进任何运行时 Skill；发布构建会阻断此类内容。

## 专家评审质量门

- 每个领域体系和每个原子 Skill 都必须遵守 `docs/architecture/expert-review.md`。
- 采用“统一质量标准，差异化验证强度”；风险分级只调整验证证据的强度，不降低专业、边界、来源、输出、安全和重大异议关闭标准。
- 领域体系进入原子清单设计前，至少完成业务实务、程序证据和 Skill 架构三个独立视角评审。
- 原子 Skill 评审必须覆盖实体规则、程序证据、反方立场、原子性、来源效力、安全权限和成果可用性。
- 评审人先独立提出意见，再处理分歧；有证据的重大法律、安全或不可逆程序异议不能用多数票覆盖。
- 检索记录、少数意见、隐藏评测和修订证据保存在被忽略的 `research/`，不得进入发布 Skill。
- 真实数据不是 Skill 开发或发布的必需验收材料；使用构造、合成、组合和对抗场景验证方法、边界、输出与安全合同，并由当前专家组独立评审收口。
- 领域共用研究形成内部研发基线，原子 Skill 只补充特有判断；运行时仍须自包含，不引用内部基线。
- 每个原子 Skill 只维护一份权威候选，Pack 内容由构建生成，不手工同步候选镜像。
- 修订先做变更影响分级；只有核心合同变化才要求原子级全量回归，局部变化执行定向回归和领域公共回归。

## 提交前验证

```bash
python3 -m unittest discover -s tests -v
python3 tooling/validate_repository.py --root .
```

开发 `planned` 领域包时，还必须显式校验该包：

```bash
python3 tooling/validate_repository.py --root . --pack <domain-id>
```
