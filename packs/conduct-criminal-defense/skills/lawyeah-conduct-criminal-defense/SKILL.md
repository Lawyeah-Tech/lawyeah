---
name: lawyeah-conduct-criminal-defense
description: Use when a user needs to understand the installed Lawyeah mainland-China criminal defense and representation skill pack, identify which installed criminal atomic skill fits the current role, procedure stage, goal, and deliverable, distinguish neighboring legal domains, or see the pack's current capabilities and limits. Do not use it to perform the selected legal task itself.
---

# 刑事辩护与刑事代理能力导航

## 定位

说明本包的能力、边界和当前原子 Skill 全貌，并根据用户角色、当前程序状态、主要目标和预期成果定位入口。具体法律任务可以直接使用相应原子 Skill，无须先经过本 Guide。

本 Guide 不完成接案筛查、紧急响应、会见、取保、阅卷、辩护意见、认罪认罚评估、控告、被害人代理、上诉或立案监督成果，也不建立固定组合方案。

## 选择方法

读取[选择方法](references/selection-method.md)，先区分被追诉方、被害方或拟委托关系，再核对当前程序状态和要交付的独立成果。每个原子 Skill 独立触发，默认不存在调用顺序；其他律师、机关、用户或其他 Skill 已形成的合格等价成果可以直接作为输入。

混合请求先列出各项可独立验收成果及入口，再只问一个会改变本次入口的问题。用户确认前不规定执行顺序，不把“接案筛查”自动变成其他 Skill 的技术依赖。

## 当前原子能力

读取[能力地图](references/capability-map.md)查找当前安装的 13 个 P0 原子 Skill。只推荐实际安装在本包中的入口；对于尚未安装的刑事能力，明确输出 `unavailable`，不得由最近邻 Skill 代做。

## 领域边界

读取[领域边界](references/domain-boundaries.md)处理企业合规、行政争议、劳动用工、人身损害、数据隐私、涉外和一般民商事事项。一个事项同时需要刑事成果和相邻领域成果时，将其拆成相互独立的专业任务，不在刑事 Skill 内补造相邻领域结论。

## MCP 边界

本 Guide 不依赖 MCP。具体原子 Skill 只在其明确业务判断节点使用稳定命名的标准工具引用，并分别声明最小输入、结果核验、隐私限制和不可用行为。

不得声称工具已连接或已经验证，不要求用户在 Skill 中提供密钥或令牌。工具不可用、无结果或结果冲突时，严格按目标 Skill 的停止或降级规则处理；不得由“无结果”推断不存在法律依据、案件事实或救济路径。

## 输出

单一成果请求只输出：当前角色与程序状态、目标成果、推荐的已安装原子 Skill、选择理由与排除项，以及启动所需的最小输入。

混合请求且本次主要成果不明时，只输出：独立成果与入口清单、各自边界，以及一个最能改变入口的问题；不指定主要 Skill，不规定固定执行顺序。
