# 当前能力地图

| 用户入口状态 | 原子 Skill | 独立成果 | 最近邻排除 |
| --- | --- | --- | --- |
| 已识别具体债务及主张主体 | `lawyeah-family-assess-marital-debt-liability` | 逐债务责任表、抗辩与证据方案 | 目标是全面资产盘点而非债务责任 |
| 一方已提出结束婚姻的明确目标 | `lawyeah-family-assess-divorce-route-and-claims` | 离婚路径评估、请求与行动清单 | 双方已达成完整共识仅需起草协议 |
| 双方同意离婚且可安全、自主协商 | `lawyeah-family-draft-divorce-settlement` | 离婚协议、登记与履行事项表 | 核心事项存在争议需要谈判或诉讼 |
| 已确定诉讼立场、主要请求和拟受理法院 | `lawyeah-family-file-divorce-action` | 离婚起诉状、原告证据目录与程序申请清单 | 目标是双方共同起草协议离婚文件 |
| 亲子身份基本明确且争议是由谁直接抚养 | `lawyeah-family-assess-child-custody` | 子女利益因素表、抚养方案与证据缺口 | 已有抚养安排且出现变更事由 |
| 存在明确抚养费给付、欠付或调整争议 | `lawyeah-family-handle-child-support-claim` | 抚养费测算表、起诉材料包 | 双方可协商形成新的完整协议 |
| 未成年人被抢夺、藏匿、拒绝交接或存在迫近风险 | `lawyeah-family-recover-concealed-child` | 子女安全与位置核验表、紧急申请和协同处置材料 | 子女人身安全稳定，仅有长期抚养权争议 |
| 现有监护人涉嫌侵害、失职或无法履职 | `lawyeah-family-remove-or-replace-guardian` | 监护风险与资格评估、撤销变更申请材料 | 尚未首次确定行为能力和监护人 |
| 存在正在发生、重复或现实迫近的家庭暴力风险 | `lawyeah-family-plan-domestic-violence-safety` | 即时危险与安全计划、报警求助和后续法律路径表 | 人身危险已稳定且目标仅为申请保护令 |
| 即时安全已得到初步保障，现需法院作出具体人身安全保护措施 | `lawyeah-family-apply-personal-safety-protection-order` | 保护措施请求表、保护令申请与证据目录 | 危险正在发生且首先需要撤离报警和即时救助 |
| 继承已经开始且需识别主体和遗产边界 | `lawyeah-family-identify-heirs-and-estate` | 继承关系图、遗产债务与证据台账 | 主体遗产已明确且目标是具体分割 |
| 继承已开始且核心争议是继承资格、继承权或遗嘱遗赠效力 | `lawyeah-family-file-inheritance-status-action` | 身份效力争点与请求表、起诉材料包 | 身份和效力无争议，仅争遗产范围或分割 |
| 遗产管理主体已确定，现需识别遗产、形成清册、通知利害关系人并采取占有控制或保全措施 | `lawyeah-family-administer-estate` | 遗产清册、通知保全与管理日志 | 债权申报核查、债务清偿与管理费用转债务管理原子；最终分配转遗产分配原子 |
| 遗嘱人当前能够表达真实意愿并拟处分个人财产 | `lawyeah-family-draft-will` | 遗嘱文本、订立执行与保管清单 | 核心目标是交换持续扶养义务 |

当前安装包只包含表中 14 个 P0 原子 Skill。未安装能力必须输出 `unavailable`，不得由名称相近的 Skill 代做。
