# Touhou Universalis II — 幻想乡 IO 系统 P2-P5 实施计划

> 项目: Touhou Universalis II (EU5 完全转换MOD)
> 分支: io
> 生成日期: 2026-08-06
> 依赖: P1 基础闭环 ✅ 已完成
> 上游设计: `todo/th_io_design_document.md` §3-§6
> 参考库: `reference-library-index.md` → `..\eu5-modding-project\`

---

## 0. 里程碑总览

| 里程碑 | 主题 | 依赖 | 核心文件 | 状态 |
|--------|------|------|----------|------|
| P1 | 基础闭环（贡献/影响力/恶名/威望/投票权重） | 无 | effects/on_action/auto_modifiers/static_modifiers | ✅ 完成 |
| **P2** | **贤者议题（引进人口/扩张授权/人间之里保护）** | P1 | parliament_issues, country_interactions, human_village_io | ⬜ 待做 |
| **P3** | **异变系统（Situation + 事件链）** | P2 | situations, events, generic_actions | ⬜ 待做 |
| **P4** | **惩戒审判（CB + 审判 + 监管国）** | P3 | casus_belli, situations, subject_types, laws | ⬜ 待做 |
| **P5** | **守护时代（时代3/4 + 守护席位）** | P4 | advances, special_statuses, laws | ⬜ 待做 |

### 关键语法验证结论（已对照 vanilla 实证）

| 能力 | 状态 | 参考 |
|------|------|------|
| `add_pop = { type = pop_type:xxx culture = ... size = ... }` | ✅ | `location_effects.txt` |
| `price_modifier = { if/limit/add }` | ✅ | `italian_wars_country_interactions.txt` |
| country_interactions `select_trigger/price/effect` 全字段 | ✅ | `country_interactions/readme.txt` |
| HRE free_city 保护（`join_defensive_wars_always`） | ✅ | `international_organizations/hre.txt` |
| `add_enemy_to_international_organization` | ✅ | vanilla 7 处使用 |
| `activate_situation` / `on_start/on_monthly/on_ended` | ✅ | `situations/black_death.txt` |
| casus_belli / subject_types 目录 | ✅ | vanilla 完整目录 |
| `start = <值>` IO 变量初始化（P1 用） | ✅ | `middle_kingdom.txt` celestial_authority start=70 |
| IO scope 跳转须 `international_organization:` 前缀 | ✅ | `guelphs_and_ghibellines.txt` |
| `is_member_of_international_organization` trigger 须 `international_organization:` 前缀 | ✅ | vanilla 全量实证 |

### 编码铁律（每次写码强制）

- `.txt` / `.yml` → UTF-8 BOM；**`main_menu/setup/start/` 例外 → 无 BOM**
- `.gui` / `.csv` → 无 BOM
- 修饰符数值 ≤5 位小数；变量读用 `var:`；`change_variable` 用 `add =` 不用 `value =`
- 带值 modifier 放 `main_menu/common/static_modifiers/`（不放 modifier_type_definitions）
- 新 modifier 写前核对 `reference_game_files/.../00_modifier_types.txt`
- 事件必须含 `outcome = ...`
- 写前对存疑语法输出 **Verification** 行（Step 2/3 + path + quote）

---

## P2: 贤者议题

### 2.1 引进外界人口议题

| 项 | 内容 |
|----|------|
| 设计 | 消耗 20团结 + 1000金 → 贤者首都人口迁移；失败不退还（§3.2 议题2） |
| 链路 | 复用「引入思潮」样板：SGUI 存变量 → propose_parliament_issue → 2/3 辩论通过 → on_debate_passed 执行 |
| 效果 | `add_pop` 向三贤者首都添加人口（location 作用域） |
| 文件 | `parliament_issues/th_sages_introduce_population_issue.txt`、`scripted_guis/th_sages_introduce_population_sgui.txt` |
| 本地化 | `th_sages_introduce_population`, `_desc`, `_cost`, `_notification`（三语） |
| 待定 | ① 人口直接 `add_pop` 还是触发事件链？建议先直接 add_pop（简），事件链后续增强 |

### 2.2 扩张授权

| 项 | 内容 |
|----|------|
| 设计 | 玩家取悦贤者获合法扩张资格 → select_trigger 选地点（2-4块）→ price_modifier（未经贤者+50%/异变中+25%/授权-75%/多省上浮）（§3.3） |
| 载体 | country_interaction（旧格式模板已注释于 `th_sages_introduce_institution.txt`） |
| 文件 | `country_interactions/th_gensokyo_expansion_authorization.txt` |
| 授权状态 | 存国家变量（供 P4 惩戒CB价格联动） |
| 本地化 | 交互名/desc/select 标题（三语） |
| 待定 | ② 载体：(a) 授予"合法扩张"标记（联动 P4 惩戒CB价格）(b) 直接"授权吞并"宣称交互 (c) 分阶段；建议 (c) 先 (a) 后 (b) |

### 2.3 人间之里保护

| 项 | 内容 |
|----|------|
| 设计 | 人类村落=自由市：不可外交吞并；强制吞并→敌意+500%；贤者地块宣称限制（§3.4） |
| 范式 | HRE free_city：`join_defensive_wars_always` + `hre_enabled_free_cities_protection` |
| 文件 | `th_human_village_io.txt` 补全、`th_gensokyo_io.txt` 敌意修正、`international_organization_special_statuses/th_gensokyo_io.txt` 席位 modifier |
| 现状 | human_village 席位已定义（20国 T03等已分配）；`th_human_village_io` 为 41 行框架 |
| 本地化 | human_village_io 描述、保护说明（三语） |

### P2 待定决策
1. 引进人口：直接 `add_pop`（推荐）vs 事件链
2. 扩张授权载体：先标记 (a) 后宣称 (b)
3. 范围：一次性做全 3 子项（推荐）vs 先人间之里保护

---

## P3: 异变系统（Situation + 事件链）

### 3.1 触发结构（§4.1）

```
角色发起异变事件(国家事件链) → activate_situation = situation:th_gensokyo_incident_xxx
Situation on_start: 烈度变量(初始10) / 阶段=发生 / 登记发起国
Situation on_monthly: 烈度随机增长(+1~3) / 玩家调查行动 / 贤者观战
结束判定 → on_ended: 结算贡献度 / 团结度回流 / 触发赌局判定
```

### 3.2 Situation 内部结构（§4.2）

| 字段 | 说明 |
|------|------|
| `phase` 变量 | 发生 → 发展 → 解决/失控 |
| `th_incident_intensity_var` | 烈度 0-100 |
| 参与者列表 | global_variable_list 存国家 scope |
| 解决者 | 贤者议会指定（存 scope 引用） |
| EX面 | 贤者决定继续 → 新增参与者 + 烈度继续增长 |

### 3.3 贤者角色（§4.3-4.6）

| 角色 | 机制 | 实现 |
|------|------|------|
| 观战 | 不可直接干预异变 | — |
| 调停 | 消耗团结度控制烈度 | generic_action |
| 指定解决者 | 耗10团结 → buff + 事件 | generic_action |
| 赌局 | 贤者押注目标，on_ended 对比 | 议会变量 |
| 暗中干涉 | 少量团结度 + buff 修正 | generic_action |
| 失控 | 烈度>80 → 触发惩戒战争 | on_monthly 判定 |

### 3.4 文件清单
- `situations/th_gensokyo_incident_generic.txt`（通用模板，可参数化复用）
- `events/th_incident_events.txt`（发起/调查/解决/失控事件链）
- `generic_actions/th_incident_investigate.txt`、`th_incident_mediation.txt`、`th_incident_designate_resolver.txt`
- 本地化（三语）

### P3 待定决策
4. 异变数量：先 1 个通用模板（推荐）vs 多个具名异变

---

## P4: 惩戒审判

### 4.1 敌意累积（§5.1）
- 私自扩张（未经贤者/异变）→ 大量敌意
- 敌意来源：`antagonism_modifier_for_taking_land_from_fellow_member`（现有 0.5）+ 自定义事件
- 敌意超阈值 → 贤者/阎魔可宣告惩戒战争

### 4.2 双重实现（§5.2，用户选定两者结合）
```
【IO敌人】add_enemy_to_international_organization = { country = X } → 成员自动获CB
【惩戒CB】自定义 casus_belli: create_enabled/declare_enabled
【惩戒Situation】th_gensokyo_punishment_war_situation: 罪计数/时长/参战国/敌意显示
```

### 4.3 罪计数（§5.3）`th_gensokyo_crime_var`

| 行为 | 罪值 |
|------|------|
| 屠杀联军军队 | +3~5/场 |
| 拒绝议和请求 | +5/次 |
| 战争持续时间 | +1/月 |

### 4.4 阎魔审判 Situation（§5.4-5.6）
- 败者结算：仅赔款/破产 + 放弃非法扩张领土 + 额外削弱国力
- **20-30年监管国**：`th_gensokyo_supervised_state` subject（`has_limited_diplomacy`/`can_be_annexed = no`/`allow_declaring_wars = no`）
- 刑满自动释放（on_disable / 定时解除）
- 宣判结束 → 幻想乡团结度回流

### 4.5 审判法律（§5.5，三级）
| 法律 | 从严倾向 | 监管时长 | 团结度 |
|------|----------|----------|--------|
| 劝善 | 最低 | 最短 | 最少 |
| 有序 | 中等 | 中等 | 中等 |
| 因果必尝 | 最高 | 最长 | 最多 |

### 4.6 目标国胜出（§5.7）
- 局势期间：特殊行动 + 宣称领土 + 多场扩张

### 4.7 文件清单
- `casus_belli/th_gensokyo_punishment_cb.txt`
- `situations/th_gensokyo_punishment_war.txt`、`situations/th_gensokyo_judgment.txt`
- `subject_types/th_gensokyo_supervised_state.txt`
- `laws/th_judgment_laws.txt`
- 本地化（三语）

---

## P5: 守护时代

### 5.1 时代补全（§6.1）
- 当前 mod 仅 `age_1_traditions` + `age_2_renaissance`
- 补 `age_3`/`age_4`（vanilla 有 `age_3_discovery`/`age_4_reformation` 可对标）
- 文件：`in_game/common/advances/th_gensokyo_common_advances.txt` 扩展

### 5.2 守护席位（§6.2）`th_gensokyo_io_guardian_special_status`
- 第四时代解锁（advance 时代门槛）
- 4-5-6 时代作为统一进程主导
- 按法律不同 1-5 席
- 要求：未接受审判 + 恶名低 + 与贤者关系良好
- 按贡献/权重顺序推举（对标灵梦/早苗）
- 拥有特殊行动（类似特殊列强）

### 5.3 反统一张力（§6.3）
- 贤者/阎魔维护稳定/破碎/传统
- 守护席位统一进程 vs 贤者守序 → 事件/修正冲突

### 5.4 文件清单
- `advances/th_gensokyo_common_advances.txt` 扩展
- `international_organization_special_statuses/th_gensokyo_io.txt` 扩展
- `laws/th_gensokyo_io_laws.txt` 扩展（席位法律选项）
- 本地化（三语）

---

## 遗留问题与待平衡项（汇总）

1. 贡献度→影响力换算率（建议 1:1，P1 已实现待实测）
2. 异变生成频率（monthly_spawn_chance 建议 1%~3%）
3. 烈度增长曲线（建议 +1~3/月）
4. 扩张地点上限（2-4块）与价格上浮公式
5. 赌局奖励具体数值
6. 监管国刑期（20-30年）与释放机制细节
7. 守护席位 1-5 席法律选项设计
8. 敌意/恶名阈值具体数值（敌意 60 / 恶名 70）
9. AI 权重（当前 ai_will_do 为 0，需补）
10. 异变"仅紫"限制实现方式（事件链条件）

---

## 附：P2 实施顺序建议

按依赖强度从低到高（每项完成即入 git 提交）：

1. **P2.3 人间之里保护**（最独立，无议会交互依赖）
2. **P2.1 引进人口议题**（复用引入思潮样板）
3. **P2.2 扩张授权**（依赖 country_interaction + 与 P4 CB 联动设计）

---

*计划文档 v1.0 / 待评审*
