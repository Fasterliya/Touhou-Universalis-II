# 幻想乡 IO 链条 — error.log 分析 + 修复计划（2026-08-23 运行）

> 日志来源: `F:\Paradox Interactive\Europa Universalis V\logs`（error.log / game.log）
> 运行时间: 2026-08-23 22:47–22:55（新档加载 + 扩张请求链路实测）
> 修复状态: 2026-08-23 全部静态修复完成，待游戏内复测

---

## 一、错误分类统计（error.log 9326 行）

| 错误 | 次数 | 来源 | 归属 |
|---|---|---|---|
| `Could not find spline network strip` | 3910 | jomini_spline_network_graphics_old.cpp | 原版地图噪音（无视） |
| `Event target link 'modifier' returned an unset scope` | 951 | script_values:106 | **Bug A（本 mod）** |
| `Value of wrong type ... Got value of type 'none'` | 951 | special_statuses:31/56/83/119/201 | **Bug A 下游** |
| `Undefined event target 'expansion_requester'` | 38 | expansion_effects:93/115 | **Bug B（本 mod）** |
| `Event target link 'scope' returned an unset scope` | 38 | expansion_effects:93/115 | **Bug B 下游** |
| `add_casus_belli ... Type: none` | 19 | expansion_effects:94 | **Bug B 下游（CB 从未授予）** |
| `Data error in loc 'THIRD_TRIGGER_EVENT_EFFECT'` + `Promote 'COUNTRY' nullptr` | 38 | — | Bug B 下游（scope 未设置 → tooltip 渲染失败） |
| `There is no column to display in select-interaction-target` assertion | 1 | pdx_assert | **Bug C（本 mod）** |
| culture/dialect/languages 系列 | 4+ | 原版文件 | 原版/既有（非本次） |
| `add_to_variable_list ... Scope: empty` | 1 | 原版 io_effects:543 | call_io_parliament 空 scope（本次未复现源） |
| `*_can_participate_in_parliament must exist in DB` | 12 | modifier_type.cpp:1193 | 引擎信息性提示（vanilla 同样不定义，无需处理） |

**已验证修复生效（本次日志中 0 次）**：
- THIRD_ENABLE/DISABLE_SITUATION_EFFECT 渲染错误 → F8/F9/F12 ✓
- `Scoped object of type 'country' is not valid` → F15（删 subject on_monthly）✓
- `event target link 'th_gensokyo_io'` → F3 ✓
- `Failed to fetch variable` → F3/F5 兜底 ✓
- `Non-existent modifier type 'country_tax_base'` → F3 ✓

---

## 二、Bug A：`th_gensokyo_io_influence_modifier` 未注册进 in_game 阶段（951+951 次）

**现象**：`Non-existent modifier type 'th_gensokyo_io_influence_modifier'`（event_target_links.cpp:1389，chain_values:106）
→ 951 次 `modifier` 链接 unset → `th_gensokyo_io_vote_power_value` 公式返回 none
→ 4 个特殊席位 + 普通成员席位的 `special_status_power` 全部失效（议会投票权重 = 0，投了没票）。

**根因**：`th_gensokyo_io_influence_modifier` 只定义在
`main_menu/common/modifier_type_definitions/th_gensokyo_societal_value_modifiers.txt`（08-21 新增），
而 `in_game/common/modifier_type_definitions/` 同名副本仍是 08-19 旧版（只有两个 monthly_towards_*）。
in_game 阶段修饰符类型库由 in_game 副本构建（同名相对路径遮蔽 main_menu 副本）→ 类型缺失。
本文件头注释自述「双目录注册（MEIOU 3735059838 同款模式）」—— 包更新 main_menu 副本时漏同步 in_game 副本。

**修复（已完成）**：`in_game/common/modifier_type_definitions/th_gensokyo_societal_value_modifiers.txt`
补入 `th_gensokyo_io_influence_modifier` 定义（category = country，与 main_menu 副本一致）。

**验证方式**：重启游戏 → error.log 不应再有 `modifier returned an unset scope` /
`Value of wrong type` at special_statuses；`trigger international_organization:th_gensokyo_io = { ... }`
议会面板投票权重应为影响力公式值（非 0）。

---

## 三、Bug B：save_scope_as 跨 scripted_effect 不可靠（F24 未落地，38+38+19 次）

**现象**：事件 option 内 `save_scope_as = expansion_requester` → 调用
`th_gensokyo_expansion_grant_cb_effect` → 效果内 `scope:expansion_requester` 解析为
「Undefined event target」（**运行时**实测，非校验期）→ scope unset →
`add_casus_belli` target none（CB 从未授予）→ `trigger_event_non_silently` 的
`[COUNTRY.GetName]` 渲染失败（THIRD_TRIGGER_EVENT_EFFECT 38 次）。

**根因**：交接文档 v5.2 F24 声称已修（「定位移入 effect 内按标记重新 save」），
但 mod 内 `th_gensokyo_expansion_effects.txt`（8/21 版）仍是旧写法 —— 修复从未真正落地。
同款隐患扩散至整个审判链：`th_gensokyo_trial_judge_core_effect` / `tier_effect` /
`effective_sin_effect` / `return_lands_effect` / `sentence_duration_effect`
全部引用跨效果的 `scope:crusade_target` / `scope:io_leader`（审判流程未测，运行必炸）。

**修复（已完成，5 文件）**：
1. `th_gensokyo_expansion_grant_cb_effect`：效果内 `every_country + has_variable` 重新定位
   `expansion_requester`（th_gensokyo_expansion_requester_mark）与 `expansion_target`
   （th_gensokyo_expansion_target_owner_mark）+ CB 授予加 target exists 守卫。
2. `th_gensokyo_expansion_decline_effect`：同上按标记重定位 requester。
3. `th_gensokyo_trial_effective_sin_effect` / `tier_effect` / `return_lands_effect` /
   `judge_core_effect` / `sentence_duration_effect`：效果开头按
   `th_gensokyo_trial_target_mark` 重定位目标国 + `is_leader_of_international_organization`
   重定位阎魔（同 debate_start_effect 既有正确模式）。
4. `th_gensokyo_expansion_request_events.txt` 头注释更正（旧注释声称已验证的模式被运行时证伪）。
5. 编辑文件 BOM 全部补回（edit 工具剥 BOM 已复验）。

**验证方式**：重启游戏 → 走一遍请求扩张（选贤者 → 同意）→ error.log 不应再有
`expansion_requester` / `add_casus_belli` 错误，且请求者获得 sage_expansion CB；
审判流程（惩戒战争 → 审判）同样不应再有 `crusade_target` 错误。

---

## 四、Bug C：select_trigger 缺 column → assertion（1 次）

**现象**：22:55:05 `Important assertion failed: There is no column to display in this stage of select-interaction-target`。
**根因**：`th_gensokyo_request_expansion.txt` 的贤者选择器（choose_country）缺 `column` 块
（F21 只修了 propose_crusade；location 选择器 vanilla 本身不带 column，无需补）。
**修复（已完成）**：`th_gensokyo_request_expansion.txt` 贤者 select_trigger 补
`column = { data = name }`（对齐 japanese_shogunate 先例）。
**验证方式**：点开「请求扩张」→ 选 IO → 选贤者列表应正常显示国家名，无 assertion。

---

## 五、其余观察（无需处理 / 待办）

| 项 | 结论 |
|---|---|
| `*_can_participate_in_parliament` / `*_agenda_impact` 类型提示 | 引擎信息性（vanilla 特殊席位同样不定义），忽略 |
| call_io_parliament "Scope: empty"（1 次） | 本次仅 1 次且无时间上下文可定位，F21+Bug C 修复后复测观察 |
| culture/dialect（culture_religion_events / languages） | 原版文件行为，非本 mod |
| `th_gensokyo_trial_events.1` 玩家手动 4 档路径 | 未实测（本次 AI 自动路径），复测重点 |
| 惩戒战争 join 链路（DBG_JOIN_*） | 本次日志无 DBG 标记 → 未测，复测重点 |

## 六、复测命令（控制台）

```
【Bug A】trigger c:T25 = { has_country_modifier = th_gensokyo_io_influence_modifier }
         （或观察 IO 面板投票权重非 0）
【Bug B】tag T25 → 请求扩张（th_gensokyo_request_expansion）→ 选贤者 → 同意
         → trigger c:请求者 = { has_casus_belli = casus_belli:th_gensokyo_sage_expansion_cb }
【Bug C】同 B 的选贤者步骤（应正常显示列表）
【审判链】effect c:T31 = { set_variable = { name = th_gensokyo_sentence_tier value = 3 }
         set_variable = th_gensokyo_trial_target_mark }
         effect c:T25 = { th_gensokyo_trial_judge_core_effect = yes }
         → error.log 无 crusade_target 错误，T31 变监管国
【回归】error.log 检查：modifier unset / Value of wrong type / expansion_requester /
        THIRD_TRIGGER / add_casus_belli none / assertion 全部清零
```

## 七、本次修改文件清单

| 文件 | 修改 |
|---|---|
| `in_game/common/modifier_type_definitions/th_gensokyo_societal_value_modifiers.txt` | +th_gensokyo_io_influence_modifier（Bug A） |
| `in_game/common/scripted_effects/th_gensokyo_expansion_effects.txt` | F24 落地：效果内按标记重定位（Bug B） |
| `in_game/common/scripted_effects/th_gensokyo_crusade_effects.txt` | 审判 5 效果内按标记重定位（Bug B 同源隐患） |
| `in_game/common/generic_actions/th_gensokyo_request_expansion.txt` | 贤者选择器补 column（Bug C） |
| `in_game/events/th_gensokyo_expansion_request_events.txt` | 头注释更正（Bug B 记录） |
