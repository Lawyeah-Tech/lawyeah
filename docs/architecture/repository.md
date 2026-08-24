# 仓库与发布架构

## 分层

Lawyeah 公开源码仓库按律师查找用中文目录组织：`领域/` 放 21 个办案包，`合同/` 放 11 个审查与起草包。每个包是安装和卸载单位，不再区分专业版 / 升级版。原子 Skill 是包内独立触发的专业能力单元。

```text
领域/     21 个办案领域（中文目录）
合同/     11 个合同审查与起草包（中文目录）
catalog/  机器可读清单（迁移期仍保留）
docs/     架构说明
```

`packs/` 是旧英文路径，迁完即删。私有研究、原始检索和内部证据在 gitignore 的 `research/`，不进入公开仓库。

## 领域包系统

每个领域包包含：

1. 一个能力导航 Skill：说明领域能力、边界和原子 Skill 全貌；
2. 一个或多个原子 Skill：分别完成边界明确的用户目标；
3. 一个 `pack.json`：记录包级范围、Skill 清单、关系和 MCP 判断节点依赖。

```text
领域/<中文领域名>/
├── README.md
├── LICENSE
├── NOTICE
├── pack.json
└── skills/
    ├── <中文入口>/
    │   ├── SKILL.md
    │   └── agents/openai.yaml
    └── <中文原子>/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/
```

合同包同样放在 `合同/<中文套件名>/`。

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

## 专家评审治理

每个领域体系在设计原子 Skill 清单前，必须完成业务实务、程序证据和 Skill 架构三个独立视角的评审。每个原子 Skill 还必须接受实体规则、反方立场、来源效力、安全权限和成果可用性评审。

评审意见先独立形成，再通过补充律页检索、官方网络验证和区分性测试处理分歧。有证据的重大法律、安全或不可逆程序异议可以阻止进入下一阶段，不能以多数票或平均分覆盖。完整规则见[专家评审治理](expert-review.md)。

当前专家组通过独立评审、失败案例和修订回归完成质量收口。真实数据不是开发或发布的必需验收材料；详细报告和证据留在私有研究层，不进入发布 Skill。

## 渐进披露与文件边界

每个 Skill 使用 Agent Skills 的三级渐进披露：名称和描述用于发现，`SKILL.md` 在触发后加载，`references/`、`scripts/` 和 `assets/` 按需使用。每个 Skill 必须提供 `agents/openai.yaml`；Skill 顶层只允许 `SKILL.md`、`agents/`、`references/`、`scripts/` 和 `assets/`。

公开仓库目录使用中文。每个 Skill 只能引用自身目录内的文件，不通过 `../` 跨 Skill 读取资源。法律文书格式资产放在所属原子 Skill 的 `assets/templates/`。

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

Skill 中可以按标准方式条件引用项目工具目录中已稳定命名的 MCP 或宿主工具，并写明用途、最小逻辑输入、结果使用和不可用行为。开发与发布不要求实际 MCP 注册、联调、权限验证或真实调用；未完成运行时接入不阻断 Skill 的专业评审和发布。

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

白名单之外还有内容级硬校验。发布构建与仓库校验使用同一套完整 Pack 规则，拒绝未声明的 Skill、名称错配、缺失 `agents/openai.yaml`、非 ASCII 路径、跨 Skill 引用、无效关系、嵌套 `research/`、`evals/`、`tests/`、隐藏认证目录、本地绝对路径、研发 Retrieval 地址和私有库标识。

领域处于 `planned` 时，仓库全量校验不会把未完成 Pack 当作发布内容；开发者必须显式校验指定草稿包：

```bash
python3 tooling/validate_repository.py --root . --pack <domain-id>
```

## 静态发行目录

安装器只消费三个公开静态对象：

```text
https://downloads.lawyeah.cn/catalog.json
https://downloads.lawyeah.cn/domains/<domain-id>/latest.json
https://downloads.lawyeah.cn/domains/<domain-id>/<version>/pack.zip
```

`catalog.json` 只列出规范领域目录中状态为 `active` 的领域，名称直接取其 `displayName`，不接受发布参数覆盖。`latest.json` 只描述一个稳定语义版本，包含 OSS 与 GitHub 的不可变 ZIP 地址、精确字节数和小写 SHA-256。载荷字段分别由 `schemas/release-catalog.schema.json` 和 `schemas/release-latest.schema.json` 定义，并与安装器的数据结构保持一致。

`tooling/build_release_catalog.py` 读取本地确定性 ZIP，自行检查 `<domain-id>/pack.json`、领域状态和版本，再生成排序键、紧凑分隔符、UTF-8 编码且无尾随换行的规范 JSON 载荷及载荷 SHA-256。工具不读取私钥、不签名、不接收任意下载源，也不接触 OSS 凭据。它可以为本次选择的领域生成 `latest`，同时始终为所有已激活领域生成完整 `catalog`；其他已激活领域继续使用各自已经发布的固定 `latest`。

目录对象使用 Ed25519 信封：

```json
{"payload":{...规范载荷...},"signature":"<base64 Ed25519 signature>"}
```

签名覆盖 `payload` 的原始字节，不覆盖重新序列化后的等价 JSON。私钥只以 GitHub `release-production` 受保护环境 Secret 注入发布作业的临时文件；作业从私钥派生公钥并与安装器内置公钥变量比对，退出时删除临时私钥。私钥和 OSS AccessKey 均不作为命令行参数传递。

## 受保护发布顺序

`.github/workflows/release-domain.yml` 仅手动触发，并要求目标领域已经是 `active`、输入版本与 `pack.json` 完全一致、仓库校验和测试全部通过。所有领域共用一个 `static-release-catalog` 并发锁，任何时刻只能有一个工作流变更全局固定目录。发布事务按以下顺序执行：

1. 构建确定性 ZIP、规范载荷和签名信封；
2. 向 OSS 不可变版本路径写入 ZIP，`PutObject` 使用禁止覆盖；已有对象只允许在下载后逐字节一致时继续；
3. 创建不可变 GitHub Release，已有资产同样必须逐字节一致；
4. 从 OSS 和 GitHub 分别重新下载 ZIP并与本地产物比较，同时逐一下载、验签并比对其他 `active` 领域的主备固定 `latest`；缺少任一对象时停止，避免目录展示尚不可安装的领域；
5. 最后备份主备源现有固定对象，依次更新领域 `latest.json`、完整 `catalog.json` 和 GitHub `static-catalog` 资产，再从两个源回读逐字节比较；任何一步失败都触发恢复原对象或删除本次新建对象。只有 OSS 明确返回 `NoSuchKey` 才按对象不存在处理，其他备份或 API 错误一律在写入前停止；补偿失败会写入 GitHub Actions 错误注解，并把不含凭据的原签名对象作为 30 天恢复 artifact 留存，供人工恢复。

因此，任何发生在第 5 步之前的失败都不会改变安装器正在使用的固定目录对象；第 5 步采用显式补偿回滚并在回读一致后才提交。固定对象是可替换的发布指针，历史版本 ZIP 永不原地更新。GitHub 是自动备用源，图形安装器仅在主源网络或 HTTP 不可用时回退；主源返回但签名或内容完整性错误时不得回退。

GitHub `static-catalog` Release 是一次性、受保护的基础设施前置条件，首次领域发布前由仓库管理员创建空 Release。正式发布工作流不会把 GitHub API、鉴权或网络错误误判为“Release 不存在”并自动创建。

所有 `active` Pack 的 Skill ID 必须全局唯一。仓库校验会拒绝跨领域重名；安装器在多领域下载完成后、写入任何宿主目录前还会再次检查，防止独立目录或异常发布绕过源码校验。

当前发布作业固定并校验官方 ossutil 2.3.0 Linux 包的 SHA-256，凭据仅通过官方支持的 `OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`、`OSS_REGION` 和 `OSS_ENDPOINT` 环境变量提供。对象存储操作依据[阿里云 ossutil 2.0 配置说明](https://help.aliyun.com/en/oss/developer-reference/ossutil-overview/)、[PutObject 禁止覆盖参数](https://help.aliyun.com/en/oss/developer-reference/put-object)执行。
