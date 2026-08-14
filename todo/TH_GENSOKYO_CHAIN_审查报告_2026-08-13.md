# TH_GENSOKYO_CHAIN 链条系统 全面审查报告

- **审查对象**：Touhou-Universalis-II 幻想乡 IO 链条系统（TH_Gensokyo_Chain）全部代码
- **规格锚点**：`TH_GENSOKYO_CHAIN_交接文档_v4.0_FINAL.txt`（2026-08-07）
- **审查日期**：2026-08-13
- **审查维度**：一致性（文档 vs 代码实况）/ 完整性 / 可执行性，技术正确性为主，数值不评平衡
- **执行方式**：门禁复跑（主进程）+ 4 个并行子 agent 分模块审查 + 主进程跨文件集成串联
- **本报告只审不修**：所有修复须经确认后另行执行

---

## 0. 总览

| 严重度 | 数量 | 含义 |
|---|---|---|
| P0 阻断（引擎加载/启动必炸） | **0** | — |
| P1 高风险（运行时功能失效/错误） | **17** | 其中 3 项为"高置信但需进游戏最终确认" |
| P2 文档与代码不一致 | **14** | 建议修订文档为 v4.1 |
| P3 建议/瑕疵 | **11** | 低风险 |

**核心结论**：代码的**静态门禁是干净的**（LSP 36 文件 0 error、编码 100% 合规、mod_lint 2 error 均为骨架文件），但**运行时正确性存在系统性缺陷**——17 个 P1 中，惩戒战争主链路（提案→辩论→局势→审判）有 4 处会直接断链，效果层有 5 处静默失效，显示层有 4 处恒显 0/隐藏。**文档第 9 章"20+4 项待实测"是诚实且必要的**：几乎所有 P1 都落在这份待测清单的覆盖范围内，但其中 3 项的前提假设（on_battle_won root=unit、财富转移链、释放国家 =yes 形式）已被本报告用 base game 证据推翻，按原假设去实测会得到误导性结论。

---

## 1. 门禁复跑结果 vs 文档第 12 章声称

### 1.1 LSP（eu5_lsp_diagnose_files，36 文件分 3 批）

| 文档第 12 章声称 | 复跑实况 | 判定 |
|---|---|---|
| LSP 全部新增文件 0 error | 36 文件全 0 error | ✅ 完全一致 |
| 剩余 warning 均为引擎内置/故意设计/合并语义 | database.duplicate_entry ×3（on_action 合并语义）、modifier.unknown_name ×1、situation.lifecycle.prefer_on_ending_cleanup ×1 与声称一致；**另有 6 处 localization.missing（BASE_VALUE×5 + th_gensokyo_temp_contribution×4）未在文档"已知可接受 warning"清单中** | ⚠️ 见下 |

未声明警告的定性（已查证，均为**误报**，但文档未记录）：
- `BASE_VALUE`：base game `main_menu/localization/english/general_tooltips_l_english.yml:6` 自带该键，运行时引擎可解析 → lint 盲区误报
- `th_gensokyo_temp_contribution`：纯数学中间变量，从不显示 → 无需 loc，误报

### 1.2 mod_lint（min_severity=warning）

| 文档第 12 章声称 | 复跑实况 | 判定 |
|---|---|---|
| 2 error 全部位于既有骨架文件（thgfx 事件 ID 格式 + 贤者 SGUI bare key） | `event.invalid_id`（th_gfx_error_suppress_events.txt:3）+ `sgui.no_bare_io_key_block`（th_sages_introduce_institution_sgui.txt:1），均为骨架文件 | ✅ 完全一致 |
| 28 新增文件 BOM 正确（GUI 无 BOM） | 17 条 encoding.bom 警告全部落在骨架文件；链条系统 30 文件实测 BOM 全部正确（GUI 无 BOM、start 无 BOM、3 个 yml 有 BOM） | ✅ 完全一致 |
| modifier.unknown_name 声称"字段已在 base game 00_modifier_types.txt 验证" | 字段**存在性**为真（base game `main_menu/common/modifier_type_definitions/00_modifier_types.txt:6271`），但**语义方向**用反了（见 P1-12） | ⚠️ 半真 |

---

## 2. P1 问题清单（18 项，按影响分组）

### A 组：主链路断裂（惩戒战争→审判 4 处断链）

**P1-01 `is_at_war = no` 触发器名错误**
- 位置：`common/situations/th_gensokyo_crusade.txt:135`
- 问题：EU5 无 `is_at_war`（不带 with）触发器；正确为 `at_war = yes/no`（base game 370+ 处）。`is_at_war_with = <scope>` 才合法（join_crusade 那处是对的）
- 影响：惩戒局势结束判定失效
- 修复：`is_at_war = no` → `at_war = no`

**P1-02 `end_situation = this` 作用域错误**
- 位置：`common/situations/th_gensokyo_crusade.txt:138`
- 问题：官方 readme（situations/readme.txt:32）明示 `end_situation = this` 仅在**局势自身内**（root=局势）结束自己；此处写在 `scope:crusade_target = { if = {...} }` 国家块内，`this` = 目标国，不是局势。审判局势 `trial.txt:59/71` 的 `end_situation = this` 在 root 上调用是**正确**的——同文档同模式一处对一处错
- 影响：惩戒局势永不结束 → 审判永不启动（主链彻底断）
- 修复：`end_situation = situation:th_gensokyo_crusade`

**P1-03 `trigger_event` 效果不存在**
- 位置：`common/situations/th_gensokyo_trial.txt:50-53`
- 问题：EU5 只有 `trigger_event_silently` / `trigger_event_non_silently`（base game 1250 处，`{ id = X days = N }` 形式与 MOD 用法完全同形）；裸 `trigger_event` base game 0 处
- 影响：玩家为阎魔时手动裁决事件永不弹出 → `th_gensokyo_trial_done` 永不设 → 审判局势卡死
- 修复：`trigger_event` → `trigger_event_non_silently`

**P1-04 反杀标记清理时序颠倒**
- 位置：`common/situations/th_gensokyo_crusade.txt:143-150` vs `:152-160`
- 问题：生命周期 on_ending → on_ended。on_ending 先对 `every_international_organization_member` 移除 `th_gensokyo_crusade_countered`（目标国若为 IO 成员必被清），on_ended 才 `NOT = { any_country = { has_variable = ... } }` 检测反杀 → 检测恒为"无反杀"→ 反杀后仍启动审判、`counter_expansion` 永不解锁
- 修复：countered 清理移到 on_ended 的 else 分支（反杀分支）内；on_ending 只保留非标记类清理

### B 组：效果静默失效（5 处）

**P1-05 财富转移读错 scope（文档待实测 18 提前实锤）**
- 位置：`common/scripted_effects/th_gensokyo_crusade_effects.txt:132-140`
- 问题：`th_gensokyo_temp_gold` 打在目标国（crusade_target），但 `scope:io_leader = { add_gold = var:th_gensokyo_temp_gold }` 里 `var:` 读的是**阎魔自己**的变量（未设）→ 阎魔到手 0 金，而目标国金币已被 `set_gold = 0` 清零
- 修复：`add_gold = scope:crusade_target.var:th_gensokyo_temp_gold`

**P1-06 `create_country_from_cores_in_our_locations = yes` 调用形式无先例（文档风险 3 实锤）**
- 位置：`common/scripted_effects/th_gensokyo_crusade_effects.txt:100`
- 问题：该效果需国家参数，base game **全部 30 处**先例均为 `= c:TAG` 或 `= scope:xxx`，无一 `= yes`；"释放全部"无法用 `= yes` 表达
- 影响：归还三连③（释放国家）失效
- 修复：遍历可释放国家逐个调用（需设计确认释放集合）

**P1-07 `multiply_variable` / `divide_variable` 效果不存在（横跨 4 文件 7 处）**
- 位置：`chain_events.txt:76/265`、`io_monthly.txt:24/33/42`、`crusade_effects.txt:234/238`
- 问题：正确形式是 `change_variable = { name = X multiply = N }` / `divide = N`（官方 events/readme.txt:175 实证；base game character_effects.txt:203 等先例）。四重证据：base game 0 处、CMF 0 处、官方 readme 0 处、维基三角贸易审查明载"不存在"（维基 Variable变量系统页:110 的记载与此矛盾，属维基自身待修正点）
- 影响：弃民系数 ×0.7/×0.4 永不生效、自由市恶名 ×6 永不生效（两处）、刑期"每 10 罪 +1 年"永不生效、骨架贡献 ÷1000 失效（骨架部分）
- 修复：7 处全部改 `change_variable = { name = X multiply/divide = Y }`

**P1-08 扩张代价修正字段语义方向相反（核心机制静默失效）**
- 位置：`common/static_modifiers/th_gensokyo_expansion_cost_modifiers.txt:10/17/24`，挂载在 `th_gensokyo_expansion_effects.txt:51-78`
- 问题：`antagonism_taking_land_giving_modifier` = "本国对**他人**夺地**产生**的敌意量"（base game societal_values/00_default.txt:203/221 注释实锤："we don't care too much if **others** take land"）。挂到扩张者身上只改变扩张者对外反应的强弱，对"扩张者承受的代价"（授权 ×0.25/异变 ×1.25/私自 ×1.5）零作用。IO 级正解字段是 `antagonism_modifier_for_taking_land_from_fellow_member`（HRE=1.25 先例）族
- 影响：文档 2.3/5.10 的"扩张代价修正"整套机制静默不生效，且不报错
- 修复：需设计确认——改用国家级"承受"方向字段（如 antagonism_received_modifier）或重构为 IO 级字段的成员差异实现

**P1-09 on_battle_won 的 root 模型错误（文档待实测 7 前提被推翻）**
- 位置：`common/on_action/th_gensokyo_chain_events.txt:102-121`
- 问题：base game `on_action/_hardcoded.txt:2783` 明示 **root = 胜利国（actor），scope:actor = 胜利军队**。MOD 与文档 5.3 都假设 root=unit、用 `owner = {...}` 从"军队"取国家——`owner` 是国家取不到的链接 → 战斗罪值源（三源之一）静默失效或月度报错
- 修复：trigger/effect 直接落在 root（胜利国）：`has_variable = th_gensokyo_crusade_target_mark` + `change_variable = { name = th_gensokyo_sin_var add = scope:war_score }`（scope:war_score 存在性已由 _hardcoded.txt:2789 确认）

### C 组：显示/交互缺陷（4 处）

**P1-10 面板双方兵力变量存储 scope 三处错位**
- 位置：GUI `gui/panels/situation/th_gensokyo_crusade.gui:52/69`（从**局势** scope 读）vs `crusade.txt:113-118`（累加到 **IO** scope）vs `:121-126`（存到**目标国** scope）
- 问题：GUI 统一 `SituationView...MakeScope.GetVariable('x')` 从局势 scope 读；supporter 求和写在 IO、target 写在目标国 → 联军兵力恒 0、目标兵力读空
- 修复：两个变量全部在局势 root 上 set/change（求和时在成员遍历内用 `prev` 回指局势或 IO 块改为局势 scope 累加）

**P1-11 罪值卡片展开逻辑失效**
- 位置：`gui/panels/situation/th_gensokyo_crusade.gui:79-96`
- 问题：header_button_onclick 改用 `LateralView.Vars.Toggle('requirements_toggled')`，但 `situation_card_expandable` 基类（cards.gui:2555-2600）的正文可见性/图标替换 3 个块仍默认绑定 `GetVariableSystem['toggled']`（另一套变量系统+另一键名）→ 正文恒折叠、点击无反应。base game sengoku.gui:43-73 全部卡片都同步 override 这 3 块
- 修复：照 sengoku.gui 补齐 `bottom_content_onclick`/`icon_replace_visible_yes`/`icon_replace_visible_not` 三个 blockoverride，统一用 `[LateralView.Vars.Exists('requirements_toggled')]`

**P1-12 potential 裸触发器致行动按钮隐藏（3 个行动）**
- 位置：`th_gensokyo_feast.txt:12-14`、`th_gensokyo_notorious_view.txt:14-16`、`th_gensokyo_propose_crusade.txt:13-15`
- 问题：type=internationalorganization 行动的 potential 顶层 root 为 empty scope（S5 实证过），`is_member_of_international_organization`/`is_leader_of...` 裸挂会恒 false；base game 全部同类行动都用 `scope:actor = { ... }` 包裹（middle_kingdom.txt:14、japanese_shogunate.txt:13 实拍）
- 影响：宴会/查看声望/惩戒提案按钮在面板上不显示（控制台执行不受影响，故 S6 时代控制台测试未暴露）
- 修复：三处 potential 改 `scope:actor ?= { ... }` 包裹

**P1-13 `current_strength` 不是国家实力值**
- 位置：`common/situations/th_gensokyo_crusade.txt:111/124`
- 问题：`current_strength` 只是 subject_type 比率字段/关系权重 key；国家实力正解是 `country_strength`（trigger_localization/country_triggers.txt:3212 注册 + script_values/io_policy.txt:737 `value = country_strength` 先例）
- 影响：即使 P1-10 修复 scope，取值仍是 0/报错
- 修复：两处 → `country_strength`（与 P1-10 一并修）

### D 组：防呆/悬空/存疑（4 处）

**P1-14 counter_expansion 的 can_see_situation 裸挂 potential**
- 位置：`th_gensokyo_counter_expansion.txt:18`
- 问题：base game 同类（stop_segregate_the_infected）都是 `scope:actor ?= { can_see_situation = ... }` 包裹；裸挂与 S5 修复模式冲突。且与 P1-02 耦合：修好局势结束 bug 后，反杀后局势已结束 → can_see_situation 恒 false → 行动永久锁定，与注释"局势存在期间可重复使用"矛盾
- 修复：包 scope:actor ?=，并重审反杀后的解锁条件（改为 countered 标记 + 独立 CD，不依赖局势可见性）

**P1-15 join_crusade 无防重，可刷贡献**
- 位置：`th_gensokyo_join_crusade.txt:35-65`
- 问题：potential 只查成员+非目标；effect 只在 `is_at_war_with` 时跳过宣战，但 +5 贡献与参战标记**每次点击都执行**，且无 cooldown → 连点刷贡献
- 修复：potential 加 `NOT = { has_variable = th_gensokyo_crusade_participant }`（或加 cooldown）

**P1-16 监管国刑满释放链 scope:overlord 无文档支持（文档待实测 2 风险强化）**
- 位置：`common/subject_types/th_gensokyo_regulated_state.txt:73-75`
- 问题：subject_types readme 第 23 行明确 on_monthly root = subject，全篇只给 can_attack/monthly_favor_gain/ai_wants 文档化 `scope:overlord`，on_monthly 未文档化；base game 从附庸 root 取宗主的标准写法是直接链接 `overlord ?= { }`（100+ 先例）
- 影响：若 scope:overlord 在 on_monthly 为空 → 刑满永不释放
- 修复：`scope:overlord = { cancel_subject = prev }` → `overlord ?= { cancel_subject = prev }`（另注意 overlord_can_cancel=no 是否拦截脚本 cancel_subject 需实测）

**P1-17 `th_sin_tier1_value` 未定义（悬空引用）**
- 位置：`common/scripted_triggers/th_gensokyo_io_chain_triggers.txt:48/52`
- 问题：`th_gensokyo_sin_low_trigger`/`th_gensokyo_sin_mid1_trigger` 引用 `th_sin_tier1_value`，全 MOD 未定义（script_values 只有 tier2=50/tier3=75）；4 个 sin 档位触发器全 MOD 零调用（死代码）
- 影响：当前不炸（无人调用，LSP 不查 script_value 引用）；未来一旦接线即报错
- 修复：删除 4 个死触发器，或补 `th_sin_tier1_value = { value = 0 }` 并同步文档第 6 章

---

## 3. P2 文档与代码不一致清单（建议修订 v4.1）

| # | 位置 | 文档声称 | 代码/磁盘实况 |
|---|---|---|---|
| 1 | 4.1 | "28 个新增文件" | 4.1 列表实为 27 txt + 1 gui + 2 yml = **30**（标题计数不含 2 个 yml） |
| 2 | 4.1 | 本地化路径 `[in_game/localization/]` | 实际在 `localization/simp_chinese|english|russian/` 子目录 |
| 3 | 4.1/第 7 章 | "中英双语" | 存在未记录的俄语文件（90 键、机翻、键集完整） |
| 4 | 4.2 | 席位 "power=200" | 实际字段名 `special_status_power`（数值 200/0 与代码一致，仅文档用简称） |
| 5 | 5.9/5.10 | 钩子 "on_took_location" | base game 无此钩子；正确名 `on_took_location_in_peace_treaty`（代码用的正确） |
| 6 | 第 6 章 | 数值表列 `th_sentence_base_years_value`/`th_sentence_max_years_value` 为平衡入口 | 代码硬编码 240/360 **月**（数值=20/30 年，但单位与 script_value 命名"年"不一致），两 script_value 死值且未加"※代码联动"注记（与 feast/join/clamp 注记风格不一致） |
| 7 | 第 6 章 | 代价 1.5/1.25/0.25 为平衡入口 | 3 个 `th_expansion_cost_*_value` 全 MOD 零引用（死值），实际生效是 static_modifiers 硬编码 -0.75/+0.25/+0.50 |
| 8 | 第 6 章 | （缺） | 漏列 `th_sin_tier1_value`（触发器引用但未定义，P1-17） |
| 9 | 第 7 章 | 5 个行动"各含 key/desc/PERFORM_/WE_PERFORM_/OTHER_PERFORMS_/ACTION_PERFORMED_ON_US" | `notorious_view` 缺 4 个反馈键（三语言全缺），且 action 未设 `show_message = no` → 点击后消息栏引用缺失键 |
| 10 | 第 7 章 | （缺） | 漏列 3 个已存在键：`th_gensokyo_feast_price`、`subject_pays_regulated`、`TH_CRUSADE_INITIAL_SUPPORT` |
| 11 | 第 8 章 S7 | "base game favor_heir_ct 先例格式" | favor_heir_ct 是 CK3 出处；EU5 真实先例是 settle_the_frontier_l_english.yml:58、flavor_chi_l_english.yml:3（函数本身验证有效） |
| 12 | 5.1 注释 | crusade_issue.txt:3 / propose_crusade.txt:3 "power 均分 800" | 现行数学 combined=600（贤者 200×3），"800"为旧版残留注释 |
| 13 | S10 | "裸 var: 数值比较全线修正" | 弃民系数段 `th_gensokyo_io_monthly.txt:31/40` 仍残留裸 `var:` 数值比较（on_action if-limit 上下文）。注：base game 在显式 scope 块内有 25+ 处裸 var: 比较反证（country_monthly.txt:118/132 等），故定性为"约定不一致 + 未证实风险"而非必炸；保守修复改 `root.var:` |
| 14 | S11/第 6 章 | "on_game_start init 空转 → 月度兜底补 5 组变量" | 表述欠准：init 实际已设 quota/quota_used/sin_var 并清 judged/authorized，仅恶名/贡献/影响力 3 组靠月度兜底；另 `th_feast_notorious_reduction_value` 为死值（feast effect 硬编码 subtract=10，该 script_value 仅注释引用），文档"平衡入口唯一"承诺对其不成立 |

---

## 4. 完整性缺口与可执行性评价

### 4.1 文档第 9 章 20+4 待实测清单的核对结论

| 清单项 | 本报告结论 |
|---|---|
| 7 罪值折算（on_battle_won unit root） | **前提已被推翻**（root=胜利国，P1-09），按原假设实测必得出误导结论 |
| 18 财富转移 | **已提前实锤为 bug**（P1-05），实测必然失败 |
| 9 归还三连（create_country =yes） | **已提前实锤**（P1-06），实测必然失败 |
| 13 局势面板渲染 | 双 P1（P1-10/P1-11）已定位，实测前应先修 |
| 6 反杀全流程 | P1-04 + P1-14 双重断链，实测必失败 |
| 19 弃民系数 | P1-07 已判失效 |
| 8 join_crusade 防呆 | P1-15 已定位（防呆只防了宣战没防贡献） |
| 12 三贤者参战四场景 | 代码语义与 F1 一致，可测；注意 P3-1（root=attacker 假设未证实） |
| 其余（1/2/3/4/5/10/11/14/15/16/17/20-24） | 仍为真实待测项，清单诚实 |

### 4.2 文档第 11 章 7 项风险核对

| 风险 | 结论 |
|---|---|
| 1 scope:war_score | 存在性已确认（_hardcoded:2789）；但真正的坑是 root 模型（P1-09），风险 1 未点到要害 |
| 2 数值显示函数 | 函数有效（EU5 先例实证）；退路成立 |
| 3 create_country =yes | **已实锤**（30/30 先例带参数），非"待测" |
| 4 join_war reason | 仍无先例（27 处 base game 无一用 reason/ignore_rules for as_defender；ignore_rules 仅在 join_war_with/against 有 2 处先例）；"忽略 reason 也可"的退路成立 |
| 5 on_battle_won 频率 | 频率问题真实存在；叠加 P1-09 后该源当前完全失效 |
| 6 恶名 x6 激进 | 数值问题保留；但乘算本身已因 P1-07 失效 |
| 7 数字化联动 | 真实（feast=10/join=5/clamp=4 已核实）；但同文件内 base_years/max_years/cost×3 死值未加同款注记 |

### 4.3 可执行性总评（下一位 agent 接手视角）

- **文档可信度**：文件清单/编码/数值表/决策历史/S1-S11 修复声称的**静态层面**全部可信（本报告逐项实证通过率高）；**运行时行为层面**的系统性缺陷与文档"LSP 通过"带来的安全感形成落差，接手者不应以"门禁过了"推断"功能能用"
- **接手顺序建议**：先修 P1 A 组（主链）→ B 组（效果）→ C 组（显示）→ D 组（防呆），每修一批跑 LSP + 对应检测手册章节回归；修复后第 9 章清单需按本报告第 4.1 节修正测试前提
- **文档修订**：P2 十二项建议随修复一并落 v4.1（含俄语文件补记、路径修正、死值注记统一）

---

## 5. P3 建议（低风险，修复时顺手处理）

1. `crusade_effects.txt:184-212` 审判奖励段绕过 unity 统一接口（直接改 IO 变量），与扣减段走接口不一致
2. `crusade_cb.txt:18-22` `ai_cede_location_desire = { add = { add = -50 } }` 冗余嵌套，可直接 `= -50`（base game 00_hardcoded.txt:55 先例）
3. 俄语 yml 全篇 `key:"value"` 冒号后缺空格（中英为 `key: "value"`；LSP 0 error 说明引擎宽容）+ 头部残留英文注释段
4. 2/3 票数学依赖恰好 3 贤者在位（max_countries=3），贤者缺位时单票权重漂移（需要保护性设计）
5. `propose_crusade` 未显式 `set_parliament_issue_support`（base game propose_parliament_issue 必设；当前因阎魔 power=0 恰好可用，属脆弱点）
6. 自由市被成员和约割让时双重惩罚叠加（恶名 8+48、团结 2+10）语义未定义，需设计确认是否互斥
7. `expansion_effects.txt:37-46` 三层 `$param$` 文本转发无 base game 先例，实测首月非法扩张确认
8. 面板缺"结束条件"卡（与维基铁律 5 不符；因 can_end=always no 属可接受偏离）
9. yml 3 对仅大小写不同的键共存（TH_CRUSADE_* 面板标题 vs th_crusade_* 变量名），需实测引擎 loc 键大小写敏感性
10. 骨架侧 17 个文件缺 UTF-8 BOM（mod_lint 17 条 encoding 警告），文档第 10 章交接事项未列此风险
11. feast `ai_will_do` 平坦 `value = 1`：AI 会在无恶名需求时以极低概率白花 50 金办宴会（文档已声明"AI 主动举办宴会留待后续研究"，属已知功能降级，仅记录）

---

## 6. 知识沉淀建议（修复完成后执行，非本次范围）

- `eu5-rules.json` 候选新规则（可静态检测）：
  - 裸 `is_at_war =`（无 with）→ 应 `at_war =`
  - `multiply_variable`/`divide_variable` 效果名 → `change_variable { multiply/divide }`
  - 裸 `trigger_event =` → `trigger_event_non_silently/silently`
  - `end_situation = this` 出现在 scope 块内 → `situation:X`
  - `value = current_strength` → `country_strength`
- 维基修正点：`维基参考_Variable变量系统.md:110` 记载的 `multiply_variable` 与 base game/CMF/官方 readme 证据矛盾，需更正
- `on_battle_won` root=胜利国（非 unit）应写入维基 On_actions 页

---

## 7. 2026-08-13 修复执行记录（P1 全部处置完毕）

### 7.1 修复清单（16 项已修 + 1 项用户决策保留）

| 编号 | 修复内容 | 状态 |
|---|---|---|
| P1-01 | `is_at_war = no` → `at_war = no`（crusade.txt:135） | ✅ 已修 |
| P1-02 | `end_situation = this` → `end_situation = situation:th_gensokyo_crusade`（crusade.txt:138） | ✅ 已修 |
| P1-03 | `trigger_event` → `trigger_event_non_silently`（trial.txt:50-53） | ✅ 已修 |
| P1-04 | 反杀标记时序：on_ending 清理移除；on_ended else 分支保留 countered；on_start 新惩戒重置 countered | ✅ 已修 |
| P1-05 | 财富转移 `add_gold = scope:crusade_target.var:th_gensokyo_temp_gold` | ✅ 已修 |
| P1-06 | `create_country_from_cores_in_our_locations = yes` | ⏸ **用户决策保留待实测**（2026-08-13 拍板）；已加醒目注释 + 检测手册首测项 0 |
| P1-07 | 7 处 `multiply_variable`/`divide_variable` → `change_variable { multiply/divide }`（chain_events ×2、io_monthly ×3、crusade_effects ×2） | ✅ 已修 |
| P1-08 | 扩张代价修正字段 `antagonism_taking_land_giving_modifier` → `antagonism_received_modifier`（数值 -0.75/+0.25/+0.50 不变，语义方向修正） | ✅ 已修 |
| P1-09 | on_battle_won 按 root=胜利国重写（去 owner 链） | ✅ 已修 |
| P1-10 | 兵力变量统一存局势 scope（supporter 求和经 `root = { change_variable add = prev.country_strength }`） | ✅ 已修 |
| P1-11 | 罪值卡片补 3 个 blockoverride（照 sengoku.gui:65-73，统一 LateralView.Vars） | ✅ 已修 |
| P1-12 | feast/notorious_view/propose_crusade 三行动 potential 加 `scope:actor = { }` 包裹 | ✅ 已修 |
| P1-13 | `current_strength` → `country_strength`（并入 P1-10 重写） | ✅ 已修 |
| P1-14 | counter_expansion 移除 can_see_situation（解锁 = countered 标记，随新惩戒 on_start 重置） | ✅ 已修 |
| P1-15 | join_crusade potential 加 `NOT has_variable = th_gensokyo_crusade_participant` 防重复点击 | ✅ 已修 |
| P1-16 | `scope:overlord` → `overlord ?=`（regulated_state 刑满释放链） | ✅ 已修 |
| P1-17 | `th_sin_tier1_value = { value = 0 }` 补定义（script_values） | ✅ 已修 |
| P2-13 | 弃民判定裸 var: → `root.var:`（io_monthly:31/40） | ✅ 已修 |

### 7.2 修复后门禁复跑

- **LSP**（14 个改动文件）：0 error；warning 全部为已定性项（BASE_VALUE ×6 误报、temp_contribution ×4 误报、duplicate_entry ×1 合并语义、modifier.unknown_name ×1 白名单陈旧、situation.lifecycle ×1 故意设计）
- **eu5_mod_lint**：2 error 维持骨架文件不变（thgfx 事件 ID + 贤者 SGUI bare key），27 warning 与基线完全一致——**修复未引入任何新告警**
- **编码**：修复过程中编辑工具剥离了 13 个文件的 UTF-8 BOM，已全部恢复并 lint 复验通过（链条文件 BOM 全部合规）

### 7.3 待人工实测项（检测手册"十二·补"新增回归清单）

- ★首测：归还三连③释放国家（= yes 语义，检测手册项 0）
- 17 项修复回归（手册项 25-42）+ 原 20+4 项清单
- 检测手册已更新：`TH_GENSOKYO_CHAIN_控制台检测手册.txt`（十二·补章）

---

## 8. 2026-08-14 第二轮修复记录（人工实测三发实弹 + 日志排查）

### 8.1 用户实测发现（3 项）

| # | 现象 | 根因定性 | 处置 |
|---|---|---|---|
| 1 | `add_antagonism` 指令"反了"（T25 执行 target=T00 → T00 获得对 T25 敌意） | 效果语义 = **target 对 root 增加敌意**，链条 3 处按反方向写 | ✅ 3 处对调（在扩张者处执行、target=受害方） |
| 2 | 惩戒局势应由恶名启动 | 原设计提案入口 = 敌意阈值；用户改设计：**恶名≥50 驱动** | ✅ interaction_source_list + ai_will_do 改 `root.var:th_gensokyo_notorious_reputation_var >= th_notorious_pariah_threshold_value`；文档与检测手册同步 |
| 3 | 非人类村落宣战人类村落不触发三贤者保护 | 三嫌疑：①on_war_declared root 语义未证 ②join_war_as_defender 的 reason/ignore_rules 无 as_defender 先例 ③席位分配未验证 | ✅ ①root→显式 scope:actor（protection+invasion 两处）②参数收敛为 `{ war = scope:war }`（27 处先例公共子集）③手册 0.9.1 二分命令给用户前置验证 |

### 8.2 error.log 排查发现（2 项实弹 + 骨架风险清单）

| # | 错误 | 根因 | 处置 |
|---|---|---|---|
| 1 | 1179 次 `Undefined event target 'th_target_country'` + `Event target link 'scope' returned an unset scope`（propose_crusade.txt:88） | 二选 `name = "choose_crusade_target"` 是自造名；**name 是引擎内置选择器模板 ID**（base game 65 处选国行动无一自造名）→ 选国 UI 不绑定 target_flag | ✅ name→"choose_country"、target_flag→target_country（high_kingship 先例）、effect 加 exists 守卫 |
| 2 | `law_to_policy_map.cpp:57: International Organization law/policy invalid or duplicated: th_gensokyo_judgment_law` | IO 定义 laws 块用裸键列表，引擎格式 = **`law = 默认policy` 键值对**（base game 5/5 实锤）；且审判法未登记 | ✅ laws 块改键值对 + `th_gensokyo_judgment_law = th_judgment_order_policy` + 保留 `th_gensokyo_seat_unlock_law = th_gensokyo_seat_unlock_policy`；骨架 3 个未定义法律移除待补 |
| 3 | 1478 次 `Trying to add a location to an IO that doesn't have a land ownership rule` | start 文件 regions 块给无 land_ownership_rule 的 IO 加领土 | ✅ regions 块注释停用（骨架如需持地先补规则） |
| 4 | start 文件裸键席位预分配（`th_gensokyo_io_yama_special_status = { T25 }` 等） | 无 base game 先例（setup 目录 0 处），静默无效 | ✅ 注释停用；实际分配由 on_game_start 双保险效果承担 |
| 5 | 骨架内容错误（audio culturetype ×N、ruler-term 不存在、invalid reform、宗教/文化比例警告等） | 骨架历史内容问题 | 📋 记录于骨架风险清单，不在链条修复范围 |

### 8.3 门禁复跑（第二轮）

- LSP：5 个改动文件 0 error（1 条 BASE_VALUE 已知误报）
- mod_lint：2 error 维持骨架不变、27 warning 与基线一致，**无新增**
- BOM：4 个 common/ 文件剥离后已恢复；start 文件保持无 BOM ✓
- 触发器方向二分（antagonism trigger）留给用户两条控制台命令（手册 0.8 节），结果决定 join_crusade ai_will_do 是否对调

### 8.4 2026-08-14 悬停刷屏修复（modifier mirror 方案）

- **现象**：打开 IO 面板悬停"查看声望"屏幕刷屏报错；error.log 1756 次/秒 ×2 条
- **根因**：全部报错来自 `propose_crusade.txt:66`（第二轮 B2 加的 `root.var:...>=50` 恶名比较）——**interaction_source_list 的 limit 上下文不吃 var: 数值比较**（新实证爆炸上下文：`Invalid left side during comparison 'var'` + `Event target link 'root' returned an unset scope`）；"查看声望"的 GetValue desc 函数本身零错误（悬停仅触发面板重渲染）
- **修复**（modifier mirror）：①新增纯标记修正 `th_gensokyo_notorious_pariah_modifier`（三语言 loc 已补）②`th_gensokyo_notorious_monthly_effect`（on_action 上下文 root.var: 已验证安全）按月把恶名≥50 落成修正标记 ③提案选国过滤与 ai_will_do 改 `has_country_modifier`（普通触发器，无 var）
- **门禁**：LSP 0 error、lint 基线不变、localizationKeys 4280→4282、BOM 全恢复
- **知识沉淀项**：新爆炸上下文（interaction_source_list limit）与 modifier mirror 规避模式待写入维基错误签名库（修复完成后执行）

### 8.5 2026-08-14 宴会点击报错修复（S11 家族首月空窗）

- **现象**：13:41:13 点宴会 → `change_variable/clamp_variable effect [ Variable not of the 'value' scope type. Type: empty ]`（feast.txt:43/47）
- **根因**：恶名变量只有月度兜底补设，**开局首月存在空窗**——用户重启加载修复后、首月脉冲前点击 → 变量未设 → 报错。S6/S8 时代同签名的"点宴会报 empty"被误诊为 script_value 参数问题（数字化后复发），真因一直是变量未初始化
- **修复**（双保险）：①`th_gensokyo_chain_init_effect` 开局补设恶名/贡献/影响力 3 变量（消除空窗）②feast effect 内 has_variable 防御守卫
- **门禁**：LSP 0 error、BOM 恢复
- **知识沉淀项**：维基 S11 条目待补记"S6/S8 数字化修复未治本，真因=变量未初始化；标准解法=开局初始化+行动守卫双保险"

---

*报告完（含两轮修复执行记录）。剩余工作 = 按检测手册 十二·三 进游戏人工回归。*
