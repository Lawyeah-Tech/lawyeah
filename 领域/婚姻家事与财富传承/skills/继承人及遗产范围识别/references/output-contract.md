# 输出合同

## 固定字段

所有成果固定包含 `scopeAndRole`、`identityAndAuthority`、`procedureState`、`factRows`、`ruleRows`、`counterMaterials`、`evidenceGaps`、`actionRows`、`deadlineRows`、`uncertainties`、`privacyRedactions`、`humanReviewRequired`。

`identityAndAuthority` 记录用户身份、代表主体、授权依据、信息披露权限、利益冲突和核验状态。`procedureState` 记录机关、案号或无案号、程序类型、审级与阶段、当前节点、关键文书及送达凭证。

事实行至少包含事项、来源、材料名称、页码或记录标识、取得方式、日期、核验状态和链条断点。规则行至少包含 `jurisdiction`、`lawVersionOrEffectiveDate`、`citation`、`applicability`、`checkedAt` 和 `ruleStatus`。

## 正常输出

每项成果绑定事实、证据、反向材料、法源状态、限制与下一步。

1. **继承开始与主体关系图**
2. **继承依据和状态表**
3. **遗产、他人财产与债务台账**
4. **证据缺口、保全风险和后续入口**

任何期限行必须单独记录机关、程序阶段、期间类别（实体请求权期间／诉讼程序期间／执行救济期间或其他）、启动事件及来源、起算日期和时区、期间口径、届满、延长补救、提交方式与回执；关键字段不明时不得计算截止日。

每项程序行动必须记录法定入口、申请主体、申请对象、受理主体、必要材料、提交方式、回执、适用法源和失败升级路径；关键字段缺失时不得指定程序路径。

## 停止输出

按“停止原因 → 成果状态：因停止条件未形成 → 已核实的非法律事实索引 → 最小补充事项 → 安全转介”输出。法源工具不可用时不得填写确定法律结论、截止日、机关路径或结果概率。

## 人工复核

任何可能用于协商、登记、诉讼、保全、履行、财产处置或人身安排的成果均标记 `humanReviewRequired: true`。合格中国大陆法律专业人员复核前只能作为核验表和条件性草案，不得直接提交、签署或实施。
