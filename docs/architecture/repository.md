# 仓库与发布架构

## 分层

Lawyeah 使用一个公开源码仓库管理 22 个法律业务领域包。领域包是安装、版本、卸载和评测单元；原子 Skill 是包内独立触发的专业能力单元。

```text
catalog → 领域边界、组合包和渠道目录
packs → 自包含领域包
schemas → 可执行契约
templates → 研发脚手架
tooling/tests → 源码质量与发布边界
static release archive → 用户实际安装内容
```

私有研究、原始检索结果、边界评测和内部证据链保存在受 Git 忽略的 `research/`。公开 Skill 只包含已经完成蒸馏、能够直接指导任务的方法与资源。

## 领域包系统

每个领域包包含：

1. 一个能力导航 Skill：说明领域能力、边界和原子 Skill 全貌；
2. 一个或多个原子 Skill：分别完成边界明确的用户目标；
3. 一个 `pack.json`：记录包级范围、Skill 清单、关系和 MCP 判断节点依赖。

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

能力导航 Skill 默认只在用户需要了解包的全貌、确认边界或定位能力时使用；具体请求可以直接触发原子 Skill。导航 Skill 不承担具体法律成果，也不成为强制总控入口。

## 原子 Skill

原子 Skill 必须同时满足：

- 对应用户可以直接提出的一项完整业务目标；
- 产生独立、可验收的专业成果；
- 具有明确触发条件、输入和成功标准；
- 不是另一个 Skill 内部的普通步骤；
- 即使依赖其他 Skill 或 MCP，也能说明所需结果和降级方式。

Skill 之间只使用三类关系：

- `depends-on`：完成当前 Skill 确实需要另一个 Skill 的特定业务成果；
- `related-to`：业务相邻但可以独立完成；
- `excludes`：边界容易混淆但不应共同处理同一成果。

不记录固定 `before`、`after` 或运行时组合方案。相似 Skill 在不同领域独立发展，不共享运行时方法、知识文件、模板或版本。

## 渐进披露与文件边界

每个 Skill 使用 Agent Skills 的三级渐进披露：名称和描述用于发现，`SKILL.md` 在触发后加载，`references/`、`scripts/` 和 `assets/` 按需使用。

运行时路径全部使用英文 ASCII。每个 Skill 只能引用自身目录内的文件，不通过 `../` 跨 Skill 读取资源。法律文书格式资产放在所属原子 Skill 的 `assets/templates/`；仓库根目录 `templates/` 只用于研发脚手架，不进入安装包。

## `pack.json` 事实源

`pack.json` 是领域包唯一结构化事实源，至少定义：

- 领域目标、纳入范围、排除范围和主要交付物；
- 能力导航 Skill 和原子 Skill 清单；
- 每个 Skill 的定位、排除事项和成果；
- `depends-on`、`related-to`、`excludes`；
- MCP 契约兼容范围和判断节点依赖。

构建校验确保声明目录、YAML 名称、关系目标和运行时文件一致。公开目录只包含蒸馏后的一级边界；详细推导和评测保存在私有研究层。

## MCP 边界

MCP 依赖定义到原子 Skill 的具体判断节点，并分为：

- `required`：工具不可用时，不形成依赖该节点的最终专业结论；
- `recommended`：继续完成基本成果，并标明未获得工具增强的判断；
- `optional`：仅用于补充，不影响基本成果。

领域包只汇总包内判断节点，不统一强制所有 Skill 使用相同工具。Skill 不保存服务端点、用户 ID、密钥或令牌；授权与凭证由 AI 宿主和 Lawyeah MCP 服务负责。

## 安装与更新

构建发生在 Lawyeah 的 CI 或发布环境。不同平台接收静态目录或静态插件包，客户电脑不安装更新器、守护进程或后台程序。

领域包是最小安装、版本和卸载单位，原子 Skill 不单独分发。安装后，包内各 Skill 在宿主支持的范围内独立发现和触发。更新通过重新安装完成，同名官方领域目录整体替换，不逐文件合并。

## 版本

- 领域包使用独立语义化版本；
- 原子 Skill 使用稳定 ID，不独立公开版本；
- 目录使用 `YYYY.MM` 版本；
- MCP 契约独立版本化，并由领域包声明兼容范围；
- 完整版和 P0 包只记录所选择的领域，不复制专业内容。

## 发布边界

`release-manifest.json` 是用户安装包的白名单。每个领域包只允许包含 `pack.json` 和 `skills/**`；仓库测试、构建工具、脚手架、CI、实施计划、全库边界文档、私有研究及任何凭证不进入用户安装包。

发布构建会拒绝未在 `pack.json` 声明的 Skill，仓库校验还会拒绝名称错配、非 ASCII 运行路径、跨 Skill 引用、无效关系和缺失的 MCP 降级说明。
