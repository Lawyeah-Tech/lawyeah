# 刑事领域 Skill 发布清单

当前公开安装包：[`领域/刑事辩护与刑事代理/`](../../领域/刑事辩护与刑事代理/)（56 个原子 + 1 个入口）。本文保留历史 `0.1.0` / P0 清单，**不是**当前安装范围。

安装、版本和卸载单位是整个领域 Pack；原子 Skill 独立发现和触发，不表示固定组合或执行顺序。

## 领域总 Skill

| Skill ID | 名称 | 作用 |
| --- | --- | --- |
| `lawyeah-conduct-criminal-defense` | 刑事辩护与刑事代理导航 | 说明当前能力、边界并按角色、程序状态、目标和成果定位入口 |

## 0.1.0 原子 Skill

| Skill ID | 名称 | 独立成果 |
| --- | --- | --- |
| `lawyeah-criminal-screen-engagement-authority-conflicts` | 刑事接案资格与冲突筛查 | 客户授权图、冲突结论及接受或拒绝转介范围 |
| `lawyeah-criminal-emergency-defense-response` | 刑事紧急响应方案 | 程序状态、首轮权利保护、期限和材料行动方案 |
| `lawyeah-criminal-prepare-first-custody-meeting` | 首次在押会见与权利处置 | 会见提纲、事实程序核验记录和会后处置清单 |
| `lawyeah-criminal-apply-bail` | 取保候审申请 | 取保条件评估、申请书草案和证明材料包 |
| `lawyeah-criminal-prepare-arrest-review-opinion` | 审查逮捕辩护意见 | 审查逮捕意见、社会危险性反证目录和听取意见要点 |
| `lawyeah-criminal-review-case-file-evidence` | 刑事阅卷与证据体系审查 | 卷宗索引、证据矩阵、矛盾缺口和后续核证清单 |
| `lawyeah-criminal-prepare-non-prosecution-opinion` | 审查起诉不起诉辩护意见 | 不起诉路径评估、专项辩护意见和附件目录 |
| `lawyeah-criminal-assess-plea-leniency` | 审查起诉认罪认罚决策评估 | 证据自愿性和程序条件核验、具结或不具结决策意见 |
| `lawyeah-criminal-assess-criminal-accusation` | 刑事控告可行性评估 | 可追诉性、刑民行政边界、证据缺口和控告路径意见 |
| `lawyeah-criminal-prepare-criminal-accusation` | 刑事控告材料包 | 刑事控告书、证据线索目录和提交留痕清单 |
| `lawyeah-criminal-prepare-victim-prosecution-agency` | 审查起诉阶段被害人代理意见 | 被害人代理争点、代理意见和证据损失附件目录 |
| `lawyeah-criminal-assess-criminal-appeal` | 刑事判决或裁定上诉评估 | 裁判生效与送达核验、上诉争点期限和是否上诉意见 |
| `lawyeah-criminal-challenge-non-filing-or-delay` | 不予立案或逾期未立案救济 | 状态期限核验、复议复核或检察立案监督材料 |

## 当前发布边界

尚未列入本版本的刑事能力不视为已经安装，包括案件总体评估、侦查阶段一般辩护、羁押必要性审查、庭前和庭审辩护、二审辩护、刑事申诉、刑罚执行、附带民事、涉案财物和特别程序等。遇到这些目标时应明确输出 `unavailable`，不得让当前 Skill 越界代做。
