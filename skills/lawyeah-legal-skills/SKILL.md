---
name: lawyeah-legal-skills
description: Navigate Lawyeah open Agent Skills for Chinese mainland legal practice. Use when the user needs PRC lawyer workflows, case intake, litigation or contract review/draft packs, or asks for 律页法律技能. Routes to one Chinese pack under 领域/ or 合同/; does not itself produce legal opinions, filings, or signed contracts.
---

# 律页法律技能导航

本技能只做分流。办案和出稿去中文整包，不要在这里写诉状、意见或合同终稿。

仓库：https://github.com/Lawyeah-Tech/lawyeah  
官网与 MCP：https://www.lawyeah.cn  
完整对照表：[SKILLS.md](../../SKILLS.md)

## 安装单位

一次只装一个包目录（`领域/<中文名>/` 或 `合同/<中文名>/`），整包安装、整包卸载。不要拆原子。拖进 Agent 后用 `/` 召唤包内技能。

```bash
git clone --depth 1 https://github.com/Lawyeah-Tech/lawyeah.git
```

## 分流

先问清：争议已经发生，还是还在写/改合同。已经形成争议 → `领域/`。待签、审查、起草 → `合同/`。法域不是中国大陆 → 说明本库不适用。

常用办案包：人身损害与侵权赔偿、劳动用工与劳动争议、合同争议解决、公司治理与股权、刑事辩护与刑事代理、婚姻家事与财富传承。  
常用合同包：买卖、劳动用工合同、公司股权与合伙、租赁、服务委托中介承揽。

具体英文 id 与路径以 [SKILLS.md](../../SKILLS.md) 为准。相邻领域看起来像同一件事时，转出到对应包，不在本导航里硬做。

## 边界

- 技能不是法律服务，不出庭，不出具法律意见。
- 律页 MCP 可选。未核验的法条、期限、管辖保持待核。
- 禁止把本导航升格成「全能法律助手」。
