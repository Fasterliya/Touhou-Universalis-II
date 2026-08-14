# 幻想乡 IO 链条系统（TH_Gensokyo_Chain）— 现状报告

- **报告日期**：2026-08-14
- **MOD**：Touhou-Universalis-II（东方风云）
- **工作副本**：`C:\Users\12494\Documents\Paradox Interactive\Europa Universalis V\mod\Touhou-Universalis-II`
- **游戏版本**：1.3（metadata supported_game_version）
- **激活 playset**："测试"（isActive，含本地 MOD + 2D Portrait Framework；链条系统无 CMF 依赖，全库 0 处 cmf_ 引用）
- **规格锚点**：`TH_GENSOKYO_CHAIN_交接文档_v4.0_FINAL.txt`（v4.0，2026-08-07）
- **本报告配套**：`TH_GENSOKYO_CHAIN_审查报告_2026-08-13.md`（问题全录）+ `TH_GENSOKYO_CHAIN_控制台检测手册.txt`（回归执行指南）

---

## 一、项目概述

幻想乡主国际组织（th_gensokyo_io）的 IO 链条系统，5 大模块：

| 模块 | 核心机制 | 当前状态 |
|---|---|---|
| ① 恶名链 | 非法扩张+8/合法+1/吞自由市×6 → 0-100 隐藏 → 月度-1/宴会-10 → 弃民档(50/75) | 已落地，经 4 轮修复 |
| ② 惩戒战争+审判 | 提案(恶名≥50)→贤者议会 2/3 票→双局势→罪值三源→3 级判决→监管国 40% 贡金 | 已落地，主链修复中验证 |
| ③ 扩张限制 | 配额 4 + 惩罚链 + 代价修正 | 已落地 |
| ④ 自由市保护 | 割让/吞并惩罚 + 三贤者自动参战 | 已落地，本轮修复 |
| ⑤ 团结度 | 月度收入 + 判决扣/审判奖 | 已落地 |

规模：28 个新增文件（27 txt + 1 gui + 2 yml 实际 30 处文件）+ 5 处骨架侵入 + 2 删除项。

---

## 二、总体状态一图流

```
静态门禁：✅ LSP 全 0 error ｜ mod_lint 2 error（均骨架）｜ BOM 全合规
审查阶段：✅ 完成（P0=0 / P1=17 / P2=14 / P3=11）
第一轮修复（8-13）：✅ 16 项 P1 已修 + 1 项用户决策保留（释放国家 =yes 待实测）
第二轮修复（8-14 实测三发实弹 + 日志）：✅ 全部处置
第三轮修复（8-14 悬停刷屏）：✅ modifier mirror 方案
第四轮修复（8-14 点宴会报错）：✅ 首月空窗双保险
人工回归：⏳ 进行中（手册回归项 0、25-55 共 32 项 + 2 个二分待报）
文档 v4.1 修订：⏳ 未开始（14 项 P2 文档偏差已列出）
知识沉淀闭环：⏳ 未开始（rules/维基更新项已列出）
```

---

## 三、完整时间线

| 时间 | 阶段 | 产物 |
|---|---|---|
| 2026-08-06/07 | 骨架开发 + v1.0-v4.0 四版修正（前任会话） | 交接文档 v4.0 FINAL + 检测手册 |
| 2026-08-13 | 全面审查（4 子 agent + 主进程集成串联 + 门禁复跑） | 审查报告：P0=0、P1=17、P2=14、P3=11 |
| 2026-08-13 | 第一轮修复（目标轮）：16 P1 + P2-13 修复；P1-06 用户拍板保留待实测 | 审查报告第 7 章 + 手册十二·补(25-42) |
| 2026-08-14 | 用户进游戏实测，报 3 发实弹；同步日志排查 4 项 | 第二轮修复 + 手册 0.8-0.9.2 + 十二·三(43-52) |
| 2026-08-14 | 悬停"查看声望"刷屏（实为 propose:66 的 var 比较爆炸） | 第三轮修复（modifier mirror）+ 回归 53/54 |
| 2026-08-14 | 点宴会报 S11 家族 empty（变量未初始化首月空窗） | 第四轮修复 + 回归 55 |

---

## 四、已修复问题全清单

### 4.1 第一轮（2026-08-13，审查驱动，17 项）

| 编号 | 问题 | 修复 |
|---|---|---|
| P1-01 | `is_at_war = no` 触发器不存在 | → `at_war = no`（crusade.txt 结束判定） |
| P1-02 | `end_situation = this` 在国家块内（this=国家） | → `end_situation = situation:th_gensokyo_crusade` |
| P1-03 | `trigger_event` 效果不存在 | → `trigger_event_non_silently`（审判裁决事件） |
| P1-04 | 反杀标记 on_ending 先清、on_ended 才检测 | 时序重构：on_start 新惩戒重置 countered；on_ended else 分支保留 countered 供反攻扩张行动使用 |
| P1-05 | 财富转移读错 scope（阎魔到手 0 金） | → `add_gold = scope:crusade_target.var:th_gensokyo_temp_gold` |
| P1-06 | `create_country_from_cores_in_our_locations = yes` 无先例 | ⏸ **用户决策保留待实测**（base game 30/30 先例带国家参数）；代码加醒目注释 + 手册首测项 0 |
| P1-07 | `multiply_variable`/`divide_variable` 效果不存在（7 处） | → `change_variable { multiply/divide }`（弃民系数、恶名×6、刑期加成、贡献÷1000） |
| P1-08 | 扩张代价修正字段语义方向反 | → `antagonism_received_modifier`（percent，-0.75/+0.25/+0.50 = ×0.25/×1.25/×1.5） |
| P1-09 | on_battle_won root 误当军队 | 按 _hardcoded.txt:2783（root=胜利国）重写战斗罪值源 |
| P1-10 | 兵力变量存错 scope（局势/IO/目标国三处漂移） | 统一存局势 scope，求和经 `root = { change_variable add = prev.country_strength }` |
| P1-11 | 罪值卡片展开逻辑失效 | 补齐 bottom_content_onclick/icon_replace_visible_yes/not 三件套（sengoku.gui 先例） |
| P1-12 | 3 行动 potential 裸挂（按钮隐藏） | feast/notorious_view/propose 加 `scope:actor = {}` 包裹 |
| P1-13 | `current_strength` 非实力值 | → `country_strength` |
| P1-14 | counter_expansion 的 can_see_situation 裸挂 + 局势结束后锁死 | 解锁条件 = countered 标记（持久至新惩戒 on_start 重置），CD 12 月 |
| P1-15 | join_crusade 可连点刷贡献 | potential 加 `NOT has_variable = th_gensokyo_crusade_participant` |
| P1-16 | 刑满释放链 `scope:overlord` 无文档支持 | → `overlord ?=`（base game 从附庸取宗主标准写法） |
| P1-17 | `th_sin_tier1_value` 未定义（悬空） | script_values 补 `= 0` 定义 |
| P2-13 | 弃民判定残留裸 var: 比较 | → `root.var:` |

### 4.2 第二轮（2026-08-14，用户实测三发实弹 + 日志排查）

| # | 现象 | 根因 | 修复 |
|---|---|---|---|
| 实弹 1 | `add_antagonism` 指令方向反了（用户实测） | 效果语义 = **target 对 root 增加敌意**（与直觉相反） | 3 处对调：自由市割让/自由市吞并/非法扩张惩罚链改为在扩张者处执行、target=受害方 |
| 实弹 2 | 惩戒局势应由恶名启动（用户设计指令） | 原设计提案入口=敌意阈值 | 拍板：**恶名≥50 过滤选国列表**（阈值复用弃民一档）；实现见第三轮 modifier mirror |
| 实弹 3 | 非人类村落宣战人类村落不触发三贤者保护 | ①on_war_declared root 语义未证 ②join_war_as_defender 带无先例参数 ③席位分配未验证 | ①宣战国判定改显式 `scope:actor`（protection+invasion 两处）②参数收敛 `{ war = scope:war }` ③手册 0.9.1 二分命令前置验证 |
| 日志 1 | 1179 次 `Undefined event target 'th_target_country'` + `Event target link 'scope' returned an unset scope` | 二选 `name = "choose_crusade_target"` 是自造名——**name 是引擎内置选择器模板 ID**（base game 65 处选国行动无一自造） | → `name = "choose_country"` + `target_flag = target_country`（high_kingship_of_ireland 完整先例）+ effect 加 `exists = scope:target_country` 守卫 |
| 日志 2 | `law_to_policy_map.cpp:57: International Organization law/policy invalid or duplicated: th_gensokyo_judgment_law` | IO 定义 laws 块用裸键列表，引擎格式 = **`law = 默认policy` 键值对**（base game 5/5 实锤），且审判法未登记 | laws 块改键值对 + 登记 `th_gensokyo_judgment_law = th_judgment_order_policy` + 保留 seat_unlock；骨架 3 个未定义法律移除待补 |
| 日志 3 | 1478 次 `Trying to add a location to an IO that doesn't have a land ownership rule` | start 文件 regions 块给无 land_ownership_rule 的 IO 加领土 | regions 块注释停用（骨架如需持地先补规则） |
| 日志 4 | start 文件裸键席位预分配（`th_gensokyo_io_yama_special_status = { T25 }` 等） | 无 base game 先例（setup 目录 0 处），静默无效 | 注释停用；实际分配由 on_game_start 双保险（th_gensokyo_io_assign_special_statuses_effect）承担 |

### 4.3 第三轮（2026-08-14，悬停刷屏）

| 现象 | 根因 | 修复 |
|---|---|---|
| 打开 IO 面板悬停"查看声望"屏幕刷屏（1756 次/秒 ×2 条） | 全部报错来自 `propose_crusade.txt:66`（第二轮 B2 的 `root.var:` 恶名比较）——**interaction_source_list 的 limit 上下文不吃 var: 数值比较**（新实证爆炸上下文）；"查看声望"的 GetValue desc 函数本身零错误 | modifier mirror 方案：①新增纯标记修正 `th_gensokyo_notorious_pariah_modifier`（三语言 loc 已补）②月度脉冲在已验证安全的 on_action 上下文做恶名≥50 比较、落成修正标记 ③提案选国过滤与 ai_will_do 改 `has_country_modifier`（普通触发器，无 var） |

### 4.4 第四轮（2026-08-14，点宴会报错）

| 现象 | 根因 | 修复 |
|---|---|---|
| 13:41:13 点宴会 → `change_variable/clamp_variable effect [ Variable not of the 'value' scope type. Type: empty ]` | 恶名变量只有月度兜底补设，**开局首月存在空窗**；S6/S8 时代同签名被误诊为 script_value 参数问题（数字化后复发），真因一直是变量未初始化 | 双保险：①`th_gensokyo_chain_init_effect` 开局补设恶名/贡献/影响力 3 变量 ②feast effect 内 has_variable 防御守卫 |

---

## 五、关键设计变更（vs 交接文档 v4.0，修订 v4.1 时需同步）

1. **提案入口**：敌意≥50 → **恶名≥50**（modifier mirror：月度落修正标记 + has_country_modifier 过滤；1 月滞后属设计内）
2. **add_antagonism 方向**：实测 = target 对 root 增加敌意；3 处调用已对调
3. **反杀标记生命周期**：反杀条约打标 → 持久解锁反攻扩张至下一次惩戒 on_start 重置（原"on_ending 清理"时序颠倒已修）
4. **counter_expansion 解锁**：去掉 can_see_situation（局势结束会锁死行动）
5. **IO laws 块格式**：裸键列表 → `law = 默认policy` 键值对；审判法已登记
6. **席位分配**：start 文件裸键语法（无效）注释停用，完全依赖 on_game_start 双保险效果
7. **regions 块**：注释停用（无 land_ownership_rule）
8. **势力计算**：current_strength → country_strength；变量统一局势 scope
9. **on_battle_won**：root=胜利国（原误当军队）
10. **join_war_as_defender**：收敛为 `{ war = scope:war }`（去掉 reason/ignore_rules）
11. **刑满释放**：scope:overlord → overlord ?=
12. **审判裁决事件**：trigger_event → trigger_event_non_silently
13. **惩戒局势结束**：at_war + end_situation = situation:X
14. **propose 选择器**：name="choose_country"（内置模板）+ target_flag=target_country
15. **变量初始化**：恶名/贡献/影响力开局即设（消除首月空窗）

---

## 六、当前门禁与日志状态

### 6.1 静态门禁（2026-08-14 最新复跑）

| 门禁 | 结果 |
|---|---|
| LSP（eu5_lsp_diagnose_files） | 全部改动文件 **0 error**；warning 仅为已定性项（BASE_VALUE 引擎内置键误报、modifier.unknown_name 白名单陈旧、database.duplicate_entry 合并语义、situation.lifecycle 故意设计） |
| mod_lint | **2 error 维持骨架文件不变**（`thgfx.0001` 事件 ID 格式 + 贤者 SGUI bare key）——非链条产物；27 warning 与基线一致；localizationKeys 4282（新增 2 键已登记） |
| 编码 | 30 文件 BOM 全部合规（common/ 有 BOM、GUI 无 BOM、start 无 BOM）；历次编辑剥 BOM 均已恢复并 lint 复验 |

### 6.2 已知日志噪音（骨架侧，非链条）

- audio culturetype 图形文化未配置 ×N
- ruler-term 引用不存在 ×1（10_countries.txt:75343）
- government invalid reform（th_gensokyo_government_reform）
- 宗教/文化人口主导比例警告 ×N
- 骨架 17 个文件缺 UTF-8 BOM
- 文化编年史 100+ 处裸 var: 数值比较（触发即炸风险，S10 同族）

### 6.3 引擎变量静态分析良性警告

- `th_gensokyo_crusade_defeated` / `enabled_situation_*`：set but never used（预留接口/引擎内部）
- `th_gensokyo_trial_done` / `th_gensokyo_expansion_authorized`：used but never set（事件选项内设值不被静态分析追踪 / 小卖铺接口预留）

---

## 七、待人工回归清单（优先级排序）

> 全部命令与步骤见 `TH_GENSOKYO_CHAIN_控制台检测手册.txt`。**重开新局后**执行。

### ★ P0 首测

- **项 0**：归还三连③释放国家（`create_country_from_cores_in_our_locations = yes`）——若报错/无效 → 改硬编码 tag 名单或删除该步骤（用户已拍板保留待实测）

### P1 本轮修复直接验证（第三/四轮，回归项 53-55）

- 53 打开 IO 面板悬停任意行动 → 零刷屏
- 54 弃民标记镜像：恶名 60 → tick_day 30 → `has_country_modifier = th_gensokyo_notorious_pariah_modifier` → yes
- 55 开局不推进时间 `trigger c:T25 = { has_variable = th_gensokyo_notorious_reputation_var }` → yes；立即点宴会 → 零报错

### P1 第二轮修复验证（回归项 43-52）

- 43/44 敌意方向（受害方对扩张者 +50/+1250）
- 45/46 提案选国列表只含恶名≥50 成员；点击全程零 Undefined event target
- 47 提案 → 议会 → 局势启动全流程
- 48 席位前置验证三连 trigger（0.9.1）
- 49/50 自由市保护四场景 + 外界入侵团结扣
- 51 重开新局零 "law/policy invalid or duplicated"
- 52 零 land ownership rule 刷屏

### P1 第一轮修复验证（回归项 25-42，17 项）

主链（25-28）、效果（29-34）、显示交互（35-37）、防呆（38-42）。

### P2 二分待报（测试时顺手跑）

```
trigger c:T25 = { antagonism = { target = c:T00 value > 0 } }   # 触发器方向二分 A
trigger c:T00 = { antagonism = { target = c:T25 value > 0 } }   # 触发器方向二分 B
```
结果决定 join_crusade 的 ai_will_do 是否对调（手册 0.8 节）。

### P3 原 20+4 项引擎实测（第 9 章，注意 3 项前提已被本报告修正）

- 罪值折算/财富转移/释放国家的测试前提已按修复后语义更新（见审查报告 4.1 节）

---

## 八、已知未决事项

### 8.1 文档修订 v4.1（14 项 P2 文档偏差，已列表）

文件计数（"28"实为 30）、本地化路径、俄语文件补记、"power"字段全名、on_took_location_in_peace_treaty 钩子名、死值注记（feast=10/sentence years/cost×3）、数值表缺 tier1、notorious_view 反馈 4 键、第 7 章漏 3 键、S7 引用的 favor_heir_ct 为 CK3 出处、"800"残留注释、S10 遗漏弃民段、S11 表述欠准——详见审查报告第 3 章。

### 8.2 知识沉淀闭环（eu5-review 复盘，修复稳定后执行）

- eu5-rules.json 候选新规则：裸 `is_at_war =`、`multiply_variable/divide_variable`、裸 `trigger_event =`、`end_situation = this` 在 scope 块内、`value = current_strength`、**interaction_source_list limit 内 var: 数值比较**
- 维基错误签名库补记：S6/S8"点宴会报 empty"数字化未治本（真因=变量未初始化）；interaction_source_list 爆炸上下文 + modifier mirror 规避模式
- 维基修正：Variable变量系统页 multiply_variable 记载与 base game/CMF/官方 readme 矛盾
- 维基补充：on_battle_won root=胜利国（非 unit）
- add_antagonism 方向实证结论（target 对 root）

### 8.3 骨架风险交接（骨架负责人）

- 3 个空壳议题（resolution_1~3）仍在议题池
- IO laws 块中 3 个被注释的法律待定义后按键值对格式加回
- regions/裸键席位已注释，骨架如需恢复需先补 land_ownership_rule / 改程序化分配
- 文化编年史 100+ 裸 var: 风险、17 文件缺 BOM、audio culturetype 等日志噪音
- 席位 power 200/0 勿改回（2/3 票数学依赖）

### 8.4 数值平衡

全部数值仍为初值"待调"（本次审查与修复未做平衡判断）；平衡入口 script_values + 数字化联动注记（feast=10/join=5/clamp=4）。

---

## 九、文档资产清单

| 文件 | 位置 | 内容 |
|---|---|---|
| 交接文档 v4.0 FINAL | `I:\工作站\交接文档\TH_GENSOKYO_CHAIN_交接文档_v4.0_FINAL.txt` | 原始规格（待修订 v4.1） |
| 审查报告 | `I:\工作站\交接文档\TH_GENSOKYO_CHAIN_审查报告_2026-08-13.md` | 问题全录（P0-P3）+ 第 7/8 章四轮修复执行记录 |
| 检测手册 | `I:\工作站\交接文档\TH_GENSOKYO_CHAIN_控制台检测手册.txt` | 0.8-0.9.2 前置验证 + 十二·补/三回归清单 0、25-55 |
| 本现状报告 | `I:\工作站\交接文档\TH_GENSOKYO_CHAIN_现状报告_2026-08-14.md` | 当前状态总览 |
| MOD 内 todo 副本 | `Touhou-Universalis-II\todo\` | 交接文档历史副本（已过时，以交接文档目录为准） |

---

## 十、下一步建议

1. **立即**：按第七节清单完成人工回归（重点：项 0 释放国家 + 53/54/55 + 二分两条）
2. **回归通过后**：执行 8.2 知识沉淀闭环（eu5-review）+ 8.1 文档 v4.1 修订
3. **平衡调优**：按 script_values 初值调参（含恶名≥50 提案阈值的实战手感验证）
4. **骨架交接**：8.3 清单交骨架负责人
