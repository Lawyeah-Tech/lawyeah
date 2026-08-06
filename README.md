# Lawyeah 法律技能体系

Lawyeah 面向中国大陆执业律师、律师助理和企业法务建设可安装的专业法律 Skill Pack。仓库以 22 个律师业务领域组织，每个领域包独立安装、使用、评测和发布，并在领域内部形成完整、专业化的工作闭环。

## 核心原则

- 一个领域包包含一个窄触发的能力导航 Skill 和多个可独立触发的原子 Skill；具体任务无需先经过导航 Skill。
- 领域包是安装、版本和卸载单位，`pack.json` 是能力范围、Skill 清单、关系和 MCP 依赖的结构化事实源。
- 原子 Skill 对应完整用户目标和可验收专业成果，不按工作步骤拆分，也不预设固定 Skill 组合。
- 不发布跨领域的通用法律 Skill；相似能力在各领域内结合具体规则、证据和程序重新实现。
- Skill 方法可以独立工作，Lawyeah MCP 按判断节点提供法规、案例和专业知识增强。
- 用户凭证由 AI 宿主或 Lawyeah 授权服务管理，不进入 Skill、Git 仓库或模型上下文。
- 用户电脑只接收静态 Skill 文件，不安装更新器、守护进程或后台可执行程序。
- 正式安装包由发布白名单生成；研发测试、构建工具和内部证据不进入安装包。

## 业务领域

完整清单位于 [`catalog/domains.json`](catalog/domains.json)，包含 8 个 P0、8 个 P1 和 6 个 P2 领域。一级归属原则见 [`docs/architecture/domain-boundaries.md`](docs/architecture/domain-boundaries.md)。领域处于 `planned` 状态时只代表规划入口，不代表已经发布可用内容。

## 仓库结构

```text
catalog/        领域、组合包和目标平台目录
packs/          已进入建设或发布阶段的领域包
schemas/        Pack、MCP能力和平台适配契约
templates/      领域包开发模板，不进入用户安装包
tooling/        校验与静态发布构建工具
tests/          仓库契约和发布边界测试
docs/           架构与实施记录
```

私有研究、原始检索结果和蒸馏证据不进入本公开仓库。

## 架构与治理

- [仓库架构](docs/architecture/repository.md)
- [22 个领域边界](docs/architecture/domain-boundaries.md)
- [专家评审治理](docs/architecture/expert-review.md)
- [劳动用工与劳动争议体系](docs/domains/labor-employment.md)
- [劳动领域 Skill 路线图](docs/domains/labor-employment-skills.md)

一个运行时领域包使用以下结构：

```text
packs/<domain-id>/
├── pack.json
└── skills/
    ├── lawyeah-<domain>-guide/
    │   ├── SKILL.md
    │   └── agents/openai.yaml
    └── lawyeah-<domain>-<task>/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/
        ├── scripts/
        └── assets/templates/
```

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 tooling/validate_repository.py --root .
```

开发中的 `planned` Pack 使用 `--pack <domain-id>` 单独执行完整校验。

## 许可

仓库内容依据 [Apache License 2.0](LICENSE) 发布。Lawyeah 远程 MCP 服务、账号权限、订阅和数据使用由对应服务条款独立管理。
