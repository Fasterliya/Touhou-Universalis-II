# Touhou Universalis II — 1.0.0 实施路线图

> 项目: Touhou Universalis II (EU5 完全转换MOD)
> 生成日期: 2026-08-08
> 状态: 待评审后分阶段实施（本文件只记录计划，不包含开工）
> 参考: `todo/TH_IO_P2_P5_PLAN.md` · `todo/th_io_design_document.md` · `todo/TH_1.0.0_FLAVOR.md` · `todo/TH_1.1.0_GUARDIAN_ERA.md` · `reference-library-index.md`

---

## 0. 1.0.0 目标定义

> **幻想乡内部可玩版**。范围 = 幻想乡内部的核心玩法闭环 + 弹幕战竞技层 + 异变接口。
> 不包含：外部世界内容、P5 守护时代完整体系、大量具名事件/任务树。

三层机制：

| 层 | 定位 | 说明 |
|----|------|------|
| **领土扩张闭环** | EU5 常规机制 | 幻想乡内扩张走「宣称 + 战争/CB」，配限制（贤者授权 + 价格 + 上限）与制裁（敌意/恶名 → 惩戒战争 → 审判 → 监管国），并提供玩家规避路径 |
| **弹幕战竞技层** | CK3 比武式 | 独立「弹幕火力值」定胜负，产出贡献度/威望/影响力/buff，**不直接影响领土**；作为异变系统接口 |
| **异变系统** | Situation + 事件链 | 精简版通用异变，是弹幕战与扩张制裁的连接点 |

### 玩家核心循环（1.0.0 目标体验）

```
 弹幕战/宴会 → 赚贡献度 → 投资影响力/取悦贤者 → 获得合法扩张授权
      ↓                                                    ↓
 异变调查/解决（=弹幕战）←———————————  合法扩张（授权价-75%，单地块·5年有效）
      ↓                                                    ↓
 私自扩张（议会宣称/强宣） → 敌意+恶名累积             越界 → 敌意/恶名超标
      ↓                                                    ↓
 异变失控或敌意超标 → 贤者/阎魔宣告惩戒战争（包围网） ←———┘
      ↓
 败 → 阎魔审判 → 监管国(20-30年)/赔款/弃土 ｜ 胜 → 多场扩张宣称
```

---

## 1. 弹幕火力值公式（设计）

```
th_danmaku_firepower_value (script value, country scope)
    base = 10
    add  = ruler.mil                                   # 君主军事能力（已验证 ruler.mil 可读）
    add  = var:th_danmaku_firepower_modifier_var        # 弹幕火力修正（事件/advance/异变 累加）
    # 科技: 相关 advance 授予 modifier → on_action 月度累加进 th_danmaku_firepower_modifier_var
    # 异变: 异变期间 auto_modifier/事件 临时增减同一 var
```

胜负判定（实现时须 Step 2/3 验证自定义 script_value 对比语法）：
`scope:actor.value:th_danmaku_firepower_value > scope:target.value:th_danmaku_firepower_value`
（对标 vanilla `scope:recipient.military_strength > scope:actor.military_strength`，hre.txt:1694）

---

## 2. 分阶段实施计划

### M0 — 前置硬伤修复（半天，无依赖）

| 项 | 文件 | 说明 |
|----|------|------|
| in_game 日文本地化 | `in_game/localization/japanese/` | 缺失整目录（109 key），从英文对齐补齐 |
| 韩文缺 key | `main_menu/localization/korean/th_culture_l_korean.yml` | 补 `th_gensokyo_religion_group` |
| 格式 bug | `th_culture_l_{japanese,simp_chinese}.yml` | `;` 分隔符改回 `:` |
| 空 desc | 各语言 `th_country_l_*.yml` | 36 条 `""` 文化/特质 desc 补实 |
| 重复机构 | `main_menu/setup/start/th_institution.txt` vs `08_institutions.txt` | 去重（TH 机构只保留一份） |
| 残留文件 | `main_menu/localization/*/test.txt`、`fix_*.py` | 清理 |
| 重复 key | `in_game/localization/simp_chinese` | `th_sages_introduce_institution_notification` 去重 |

**验收**：5 语言 key 对齐审计通过；无残留开发文件；实机启动无新增错误。

### M1 — 弹幕战竞技系统（P2.2，依赖 M0）

| 项 | 文件（新建） | 说明 |
|----|------|------|
| 火力值脚本值 | `in_game/common/script_values/th_danmaku_firepower_value.txt` | base + ruler.mil + var |
| 火力修正维护 | `in_game/common/auto_modifiers/th_danmaku_firepower_auto.txt` | advance/异变修正累加进 var |
| 竞技比武 | `in_game/common/country_interactions/th_danmaku_challenge.txt` | 对 IO 成员发起（默认，见 §3 待确认） |
| 决斗事件链 | `in_game/events/th_danmaku_events.txt` | 挑战→接受/拒绝→对决→胜负奖励（贡献/威望/影响力/buff，**无领土**） |
| 应战行动 | `in_game/common/generic_actions/th_danmaku_respond.txt` | 被挑战方接受/拒绝 |
| 科技挂钩 | 扩展 `in_game/common/advances/th_gensokyo_common_advances.txt` | 选 3–5 条 advance 加火力修正 modifier |
| 本地化 | 5 语言（英/中/日/韩/俄） | 全部新 key |
| AI 权重 | 全部新互动/行动 | `ai_will_do` 填实 |

**验收**：两名 IO 成员可完成一次完整弹幕战；胜负按火力值判定；奖励入账；不改变任何领土。

### M2 — 扩张限制与制裁闭环（核心，依赖 M1）

| 项 | 文件 | 说明 |
|----|------|------|
| 扩张授权 T5 | `country_interactions/th_gensokyo_expansion_request.txt` + SGUI | 玩家选**一个目标地块** + 选**一位亲近的贤者**（两级 select_trigger）→ 按所选贤者**原版好感度/AI 倾向**直接结算 → 同意：该地块授权生效（购宣称价 −75%）· **5 年有效**；拒绝：申请费不退还（待平衡：建议 5团结+300金） |
| 请求宣称互动 | `in_game/common/country_interactions/th_gensokyo_request_claims.txt` | select_trigger 选地块；`price_modifier`：授权 -75% / 未授权 +50% / 异变中 +25% / 多省上浮 |
| 人间之里保护 (P2.3) | 扩展 `th_human_village_io.txt` + special_statuses | 自由市范式：不可吞并、敌意+500%、贤者地块禁宣称 |
| 敌意/恶名累积 | 扩展 `in_game/common/on_action/th_gensokyo_io_monthly.txt` | 阈值：敌意 60 / 恶名 70 |
| 惩戒战争 (P4 精简) | `casus_belli/th_gensokyo_punishment_cb.txt` + `situations/th_gensokyo_punishment_war.txt` | `add_enemy_to_international_organization` 触发 + 罪计数/时长/参战贡献 |
| 审判 | `situations/th_gensokyo_judgment.txt` + `subject_types/th_gensokyo_supervised_state.txt` | 败者结算 + 监管国（has_limited_diplomacy/can_be_annexed=no/allow_declaring_wars=no） |
| 审判法律 | 扩展 `in_game/common/laws/th_gensokyo_io_laws.txt` | 三级：劝善/有序/因果必尝 |
| 规避路径 | 事件/议题 | 合法授权、弹幕战赚贡献、异变贡献、恶名削减事件 |
| 本地化 + AI 权重 | 5 语言 + 全部新定义 | — |

#### 贤者议会扩容（M2 部分 — 行动类）

| 行动 | 文件 | 说明 |
|------|------|------|
| 谕令·强行通过 A1 | `generic_actions/` 或事件 | 耗 **10 威望**跳过投票直接执行（威望可花 → 议会政治核心张力） |
| 惩戒宣告 A4 | `country_interactions/` | 敌意达标 → 对违规国 `add_enemy_to_international_organization`（全员获 CB，已验证） |
| 御守授予 A5 | `generic_actions/` + static modifier | 贤者亲赐御守（耗小威望） |
| 论功行赏 A7 | `generic_actions/` | 目标国贡献+影响力+（P1 现成效果） |
| 御前宴 A8 | `events/` + 宴会行动 | 贤者主持宴会，奖励更丰（接 B7 宴会主题化） |
| 御守大赦 T6（+B5 合并） | 事件 + static modifier + 变量 | 统一「御守」= **恶名 −10（仅赦免）**；三来源：神社自购(B5) / 议会大赦(T6) / 贤者亲赐(A5) |
| 贤者议会内建修复 | 扩展 `th_sages_council_effects.txt` 等 | 发起者私利（贡献+10/影响力+5/首都优先）/ 三贤者分工(B8) / AI 主动发起 / 贤者非法扩张→威望−10~20 |

**验收**：玩家可体验完整闭环——授权低价扩张（T5 单地块·5年）、私自扩张遭敌意/恶名、超标被惩戒战争（A4）、败后进审判/监管国、刑满释放；贤者行动可运行且成本与存在感联动；AI 会使用授权与规避路径。

### M3 — 异变接口（P3 精简，依赖 M2）

| 项 | 文件（新建） | 说明 |
|----|------|------|
| 通用异变 Situation | `in_game/common/situations/th_gensokyo_incident_generic.txt` | 烈度(0-100)/阶段/发起国/参与者/解决者 |
| 事件链 | `in_game/events/th_incident_events.txt` | 发起/调查/解决/失控 |
| 贤者行动 | `in_game/common/generic_actions/` | 调停/指定解决者（精简） |
| 接口接线 | 弹幕战火力 + 扩张价格 | 异变中火力修正、异变中扩张 +25%、解决获贡献度、失控→惩戒战争入口 |

#### 贤者议会扩容（M3 部分 — 议题类）

| 议题 | 文件 | 说明 |
|------|------|------|
| 引进外界人口 T1 | `parliament_issues/th_sages_introduce_population_issue.txt` + SGUI | 20团结+1000金 → 三贤者首都 `add_pop` 迁移；发起者首都优先+私利（复用引入思潮样板） |
| 指定异变解决者 T2 | 议题 + 事件 | 10团结 → 指定国获「解决者」buff+特殊事件（异变主导权起点，接 1.1.0 守护弧） |
| 赌局注资 T3 | IO 变量列表 | 5团结 → 贤者押注入 `global_variable_list`，异变结算比对 |
| 异变 EX 面 T4 | Situation 变量 + 事件链 | 15团结 → 异变进入 EX 阶段（烈度续涨+新参与者） |
| 调停 A2 | `generic_actions/` | 关系↑+调解金（1.0.0 不做 script 停战，停战待验证后补） |
| 暗中干涉 A3 | `generic_actions/` + static modifier | 小团结 → 指定国短 buff（符卡偏袒） |

**验收**：异变可按事件链发起并走完调查→解决/失控；期间弹幕战火力与扩张价格正确联动；失控可转入惩戒流程；贤者议会议题（T1–T4）可投票通过并生效。

### M4 — 填平与发布（依赖 M1–M3）

1. **AI 权重全开**：55 条 advance + 所有新互动/议题/Situation/事件/法律。
2. **全部 `# TODO: 后续人工填写` 数值**：IO 修正/席位修正/贤者五档/法律/审判时长(20-30年)/赌局奖励/烈度曲线。
3. **实机验证**：启动无红字 → `error.log` 归零 → 5 语言 key 对齐审计 → 兼容性检查（参考库 `docs/technical/EU5_Multi_Mod_Compatibility.md`）。
4. **平衡 pass**：授权价格公式、敌意/恶名阈值、贡献度→影响力换算率、弹幕火力数值。

**验收（1.0.0 Release Checklist）**：
- [ ] AI 权重全开，AI 会研究科技、参与弹幕战、申请授权、惩戒违规国
- [ ] 扩张闭环三态可完整游玩（合法/私自/被惩戒）
- [ ] 弹幕战不影响领土，胜负由火力值决定
- [ ] 异变系统与弹幕战/扩张/惩戒全部接线
- [ ] 无 `TODO`/`占位`/空壳文件残留
- [ ] 5 语言 key 对齐，无缺失/重复
- [ ] 实机 30 分钟无红字，error.log 干净
- [ ] 兼容性：与参考库兼容性规则核对通过

---

## 3. 待确认项（开工前逐项确认）

| # | 问题 | 默认建议 | 影响里程碑 |
|---|------|----------|-----------|
| 1 | 弹幕战参与者范围 | 仅幻想乡 IO 成员 | M1 |
| 2 | 比武形式 | 1.0.0 先一对一挑战；周期「弹幕祭」多国赛事留后续 | M1 |
| 3 | 授权有效期 | ✅ 已确认：T5 单地块授权·**5 年有效**；结算 = 按所选贤者原版好感度/AI 倾向直接决断 | M2 |
| 4 | 胜负奖励 | 贡献度/威望外，加短期「弹幕战冠军」buff | M1 |

> 贤者议会扩容（T1–T6 / A1–A5 / A7 / A8）与守护主线（1.1.0）已确认，详见本文件 M2/M3 与 `todo/TH_1.1.0_GUARDIAN_ERA.md`。

---

## 4. 编码铁律（沿用 P2-P5 计划）

- `.txt` / `.yml` → UTF-8 BOM；`main_menu/setup/start/` 例外 → 无 BOM；`.gui` / `.csv` → 无 BOM
- 修饰符数值 ≤5 位小数；变量读用 `var:`；`change_variable` 用 `add =` 不用 `value =`
- 带值 modifier 放 `main_menu/common/static_modifiers/`（不放 modifier_type_definitions）
- 新 modifier 写前核对 `reference_game_files/.../00_modifier_types.txt`
- 事件必须含 `outcome = ...`；事件 ID 用 `namespace.integer (1-9999)`
- 写前对存疑语法输出 **Verification** 行（Step 2/3 + path + quote）
- 本地化 key 用 `th_` 前缀；新内容五语言同步

---

*计划文档 v1.1 / 已评审 · 本文件仅记录计划，实施另起任务*
