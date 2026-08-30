# 弹幕战系统 — 接口与脚本用法文档
# Danmaku Battle System — Interface & Script Usage Guide

> 项目: Touhou Universalis II (EU5 完全转换MOD) · 子系统: 弹幕战竞技层（路线图 M1）
> 状态: 已实现（D0–D4）· 平衡数值待调
> 相关: `todo/TH_1.0.0_ROADMAP.md`（M1）· `todo/th_io_design_document.md`（§4 异变接口）
> 参考实现: `..\ACGV\in_game\...\acgv_touhou_danmaku_*`（ACGV 模组弹幕战参照）
> 2026-08-28 六点改版：新火力公式 / 对决两段确认（确认挑战·接受） / 遭遇五结局（含平手） /
>   对决五档结果 / 命中率战术体系 / 移除挑衅

---

## 1. 弹幕火力水平（核心数值）

### 1.1 公式

```
th_danmaku_firepower_value（脚本值，国家 scope 读取）=
    基础 10
  + 统治者军事能力 ×10（ruler_or_regent.mil × 10；1 军事 = 10 火力，100 军事 ≈ 1000）
  + 正统信仰容忍 ×100（modifier:tolerance_own × 100）
  + 稳定度 ×2（stability × 2）
  + 弹幕火力值（th_danmaku_firepower_base_modifier，平加修正字段）
  × (1 + 弹幕火力值修正 th_danmaku_firepower_modifier%)
```

类比：**弹幕火力值 ≈ CK3 勇武值**。全库事件/行动/接口统一读 `th_danmaku_firepower_value`，
不要在别处重复实现公式。平加来源（科技/增益）按同一口径 ×10 缩放以保持占比。

### 1.2 两个新修正

| 修正 | 类型 | 显示名 | 来源示例 |
|---|---|---|---|
| `th_danmaku_firepower_base_modifier` | country，平加 | 弹幕火力值 | 科技：符卡规则 +30 / 符卡改革 +50 / 妖妖之梦 +30；事件/异变 `add_country_modifier` |
| `th_danmaku_firepower_modifier` | country，percent | 弹幕火力值修正 | 科技：异变新叙事 +10% |

类型定义双目录注册（内容必须一致）：
- `main_menu/common/modifier_type_definitions/th_danmaku_modifiers.txt`
- `in_game/common/modifier_type_definitions/th_danmaku_modifiers.txt`

### 1.3 如何增减火力

- **永久**（科技）：在 `in_game/common/advances/th_gensokyo_common_advances.txt` 的 advance 块内加
  `th_danmaku_firepower_base_modifier = N` 或 `th_danmaku_firepower_modifier = 0.xx`。
- **临时**（事件/异变）：`add_country_modifier = { modifier = <静态修正> years = N mode = add_and_extend }`，
  静态修正定义在 `in_game/common/static_modifiers/th_danmaku_modifiers.txt`
  （已含 `th_danmaku_champion_modifier`（冠军，对决胜利）/ `th_beast_rampage_modifier`（妖兽作乱，地点修正 -10%））。
- **跨国家比对**：先 `th_danmaku_firepower_snapshot_effect = yes`（写入
  `var:th_danmaku_firepower_self_var`），再按需在对手 scope 内写另一变量，最后 `var:` 对比
  （ACGV 已验证模式；`scope:X.value:自定义脚本值` 对比语法未在参考库找到先例，勿直接使用）。

---

## 2. 外部调用接口（随时可调）

### 2.1 触发遭遇战

```
th_danmaku_encounter_trigger_effect = { enemy_fp = <脚本值/数值> }
```
- 国家 scope 调用；`enemy_fp` 传 `th_danmaku_youkai_firepower_value`（**随机 500~1000**）即默认随机，
  传任意脚本值/数值即指定对手火力（2026-08-28 接口化，事件/异变可注入特定敌人）。
- 作用：快照我方火力 → 写 `var:th_danmaku_encounter_youkai_fp_var` → 触发 `th_danmaku_events.1`。

调用示例：
```
# 在某事件/行动中（国家 scope）
th_danmaku_encounter_trigger_effect = {
    enemy_fp = th_danmaku_youkai_firepower_value
}
# 指定强敌（例如异变 BOSS）
th_danmaku_encounter_trigger_effect = {
    enemy_fp = 1200
}
```

### 2.2 随机选对手并开始对决

```
th_danmaku_duel_trigger_effect = { challenger = <发起方国家> }   # 行动内 challenger = scope:actor；事件内 challenger = ROOT
```
选人优先级：异变参与者（`global_variable_list:th_gensokyo_incident_participant_list`）
→ 退治者（`has_variable = th_gensokyo_incident_resolver_mark`）→ 幻想乡 IO 成员（兜底）。
列表/标记为 M3 异变系统预留，未填充时自动回落，不报错。

### 2.3 指定双方开始对决

```
th_danmaku_duel_start_effect = { challenger = <发起方国家> target = <对手国家> }
```
守卫：双方存在 + 均非对决中，否则安全退出。流程：
发起方持全部状态（self FP / 对手 FP 拷回 / **隐藏终点** / 分数 / 回合）；
对手持标记 + 双方火力副本（供 `.11` 确认预览）→ 触发 `.10` 第 1 轮。
调用示例：
```
# 行动内（发起方 = 行动国/玩家，对手 = 选择器目标）
th_danmaku_duel_start_effect = { challenger = scope:actor target = scope:target }
# 事件内（发起方 = 事件触发国）
th_danmaku_duel_start_effect = { challenger = ROOT target = scope:some_country }
```

### 2.4 作用域模型（2026-08-28，务必遵守）

| 上下文 | 隐式当前 scope（ROOT） | 用法 |
|---|---|---|
| 事件（option/immediate） | 事件触发国 ✅ | 效果可直接用裸操作（事件在发起方/对手身上触发，即该方） |
| on_action 国家脉冲 | 国家 ✅ | 可直接用裸操作 |
| **generic action 的 effect 顶层** | **空 ❌** | **禁用隐式 ROOT/裸操作；必须 `scope:actor` 或显式参数** |
| 入口效果（duel/beast trigger） | 不确定（取决于调用方） | **一律显式参数**：`challenger = scope:actor` / `target = scope:target` |

- 跨国家数据访问：`scope:X.var:Y` / `prev.var:Y`（参考库已验证）；**不要**依赖跨块/跨 scripted effect 的 `save_scope_as`（模组 F24 教训），事件内用标记 + `every_country` 找回。

**事件 loc 动态取值（2026-08-28 修复，重要）**：
- **禁用 `[ROOT.MakeScope.GetVariable(...)]` / `[ROOT.MakeScope.ScriptValue(...)]`**——全库无先例，事件 loc 中解析不到值（ERROR 实证）。
- **行动上下文事件（对决链 .10/.11/.12/.20/.21/.22）**：用 `[actor.MakeScope.GetVariable('x').GetValue]` / `[actor.MakeScope.ScriptValue('x')]` / `[target.MakeScope.ScriptValue('x')]` / `[actor.GetName]` / `[target.GetName]`（settle_the_frontier / ACGV 弹幕战先例；actor=发起方，target=对手，贯穿事件链）。
- **非行动上下文事件（遭遇 .1-.6 / 妖兽 .30-.34、.40）**：用 `[ROOT.GetCountry.MakeScope.ScriptValue('x')]` / `[ROOT.GetCountry.MakeScope.GetVariable('x').GetValue]`（vanilla hook_and_cod_wars 同款）。
- **数值显示精度（2026-08-29）**：loc 命令支持 `|N` 管道后缀控制小数位——`[X.MakeScope.ScriptValue('x')|1]` = 1 位小数、`|0` = 四舍五入整数、`|0-` = 向下取整、`|2+` = 向上取整 2 位（ACGV `acgv_silk_work_total_amount|2+` 与 vanilla `iw_tension.GetValue|2` 实证）。命中率/弹幕火力显示用 `|1`；整数量（妖兽火力、概率%、分数、金币）不加管道，避免显示 "512.0"。

### 2.5 玩家主动入口

`th_danmaku_challenge`（generic action，`type = internationalorganization`）：
幻想乡 IO 面板内选目标 → 走 2.3（`challenger = scope:actor target = scope:target`）。CD 5 年（60 个月）；AI 权重 0（AI 对决走事件/异变接口）。

### 2.6 封装接口教程（2026-08-28 新增）

战斗奖励统一走一个封装效果，**不要在事件里散写 `add_gold` / `add_prestige`**。
分档数值集中在 `th_danmaku_values.txt`，事件/效果不硬编码数值。

```
### 结局奖励统一封装（国家 scope）
### 用法:
th_danmaku_battle_reward_effect = {
    type = <战斗类型：duel|encounter|beast>          # 语义参数（供文档/调用点选档）
    tier = <结局档：great_victory|victory|draw|defeat|rout>
    gold = <值>        prestige = <值>    research = <值>
    stability = <值>   contribution = <值> influence = <值>    investigation = <值>
}
```
- `type` / `tier` 只作语义标注（不同战斗/场景可给不同奖励），实际入账的是数值参数。
- 入账项：金币 / 威望 / 研究点数 / 稳定度 / 幻想乡 IO 贡献度 / 影响力；异变中额外累加调查进度（`investigation`）。
- 惯例示例（取自本系统实现）：
  - 遭遇战大胜：`type = encounter tier = great_victory`，数值传 `th_danmaku_encounter_great_victory_*_value`（研究/稳定/贡献/影响为 0）。
  - 对决大胜：`type = duel tier = great_victory`，数值传 `th_danmaku_duel_great_victory_*_value`；胜利档额外 `add_country_modifier` 冠军增益（在 `th_danmaku_duel_finish_effect` 内，勿在外部重复）。
  - 妖兽胜利：`type = beast tier = victory`，金/研究用固定常量（500/5），`investigation` 由调用方传入。

三大入口接口速查：

| 接口 | 签名 | 何时用 |
|---|---|---|
| `th_danmaku_encounter_trigger_effect` | `{ enemy_fp = <脚本值/数值> }` | 触发一场遭遇战；`enemy_fp = th_danmaku_youkai_firepower_value` 为默认随机 |
| `th_danmaku_duel_start_effect` | `{ challenger = <发起方> target = <对手> }` | 指定双方开始对决（行动内 `scope:actor`/`scope:target`，事件内 `ROOT`） |
| `th_danmaku_battle_reward_effect` | `{ type tier + 7 个数值参数 }` | 结局奖励统一入账（见上） |

---

## 3. 遭遇战（无名妖怪）

### 3.1 触发方式

1. 月度随机：`in_game/common/on_action/th_danmaku_chain_monthly.txt`
   仅 `is_human` + 非对决中，`random = { chance = 2 }`（2%/月，字面量；常数
   `th_danmaku_encounter_monthly_chance_value` 供未来改造），调用
   `th_danmaku_encounter_trigger_effect = { enemy_fp = th_danmaku_youkai_firepower_value }`。
2. 脚本接口：2.1 随时调用（可指定敌人火力）。

`.1` 选项：**战斗**（TT 公示五结局概率）/ **回避**（威望 -5，`th_danmaku_cowardice_prestige_value`，可调）。

### 3.2 结算算法

火力比（我方×100÷妖怪，整数%）五档 → 五结局权重 `random_list`（与概率公示完全一致）：

| 比值带 | 大胜 | 胜利 | 平手 | 败北 | 大败 |
|---|---|---|---|---|---|
| ≥160 | 35 | 35 | 20 | 8 | 2 |
| ≥120 | 25 | 35 | 25 | 12 | 3 |
| ≥90 | 15 | 30 | 30 | 18 | 7 |
| ≥60 | 8 | 20 | 32 | 28 | 12 |
| <60 | 3 | 12 | 25 | 35 | 25 |

### 3.3 奖惩（结局事件 .2/.3/.6/.4/.5 immediate 经 `th_danmaku_battle_reward_effect` 结算）

| 结局 | 金币 | 威望 | 异变调查进度（异变中） |
|---|---|---|---|
| 大胜 | +30 | +5 | +4 |
| 胜利 | +15 | +2 | +2 |
| 平手 | 0 | 0 | 0 |
| 败北 | −10 | −2 | 0 |
| 大败 | −25 | −5 | 0 |

数值键见 §6。异变中时大胜/胜利事件额外显示"调查进度推进"选项（.b，仅异变中可见）。

---

## 4. 对决战（CK3 比武式）

### 4.1 流程时序（2026-08-28：两段确认 + 五档结果）

```
th_danmaku_duel_trigger_effect / th_danmaku_duel_start_effect
  → .10 第 1 轮·发起方确认（确认挑战 / 怯战 -5 威望并取消，TT 预览双方火力）
      确认 → .11 第 2 轮·对方应战（接受 85 / 投降 15；投降 -5 威望，发起方收 .12 取消）
      怯战 → 清理对决状态（无 .12 通知，发起方自己作罢）
      接受 → .20 回合循环（root = 发起方）
  → .20 我方回合（4 战术，desc 内嵌记分板，终点隐藏）
      选项 → 掷分入账 → 终局? → .22 结果
                            否 → .21 对手回合（静默，1 天后）
  → .21 对手回合（AI 本地模拟：强者求稳 / 弱者搏冷门）
      掷分入账 → 终局? → .22 结果
                 否 → 回合数+1 → .20（非静默，1 天后）
  → .22 结果（五档分流确认：大胜/胜利/平手/败北/满目疮痍 + 兜底，清理变量）
```

### 4.1.1 状态变量落位（2026-08-28 修复）

- **发起方（对决状态持有者）**：`th_danmaku_firepower_self_var`、`th_danmaku_duel_challenger_fp_var`、
  `th_danmaku_duel_enemy_fp_var`（开局从对手拷回）、`th_danmaku_duel_goal_var`、分数/回合/骰子/命中率/分差快照变量、`th_danmaku_duel_challenger_mark`。
- **对手**：`th_danmaku_duel_enemy_fp_var`（自身火力）、`th_danmaku_duel_challenger_fp_var`（发起方火力，`.11` 预览用）、`th_danmaku_duel_opponent_mark`。
- 跨国家拷回用 `scope:X.var:Y` / `prev.var:Y`（参考库已验证语法），**不要再把对手火力只存在对手身上**（曾导致 goal 公式读空变量 → 决斗永不结束 + loc ERROR）。
- 清理 `th_danmaku_duel_cleanup_effect` 覆盖双方全部残留（含 mark、火力副本、骰子/命中率/分差快照；挑衅变量已随挑衅机制删除）。

### 4.2 胜负终点（隐藏，玩家不可见）

```
th_danmaku_duel_goal_var = 固定 100（th_danmaku_duel_goal_value，2026-08-28 定案）
```
回合预估（平均单回合 8~14 分）：常规混合 8~12 轮。**终点不再依赖双方火力**——火力只影响
战术命中率（§4.3）/ AI 对手战术倾向 / 展示值。
终局判定 `th_danmaku_duel_finished_trigger`：任一方分数 ≥ 终点；双方同轮达标时分数高者胜。
修改入口：`th_danmaku_values.txt` 的 `th_danmaku_duel_goal_value`（改本键即调整对决时长）。

### 4.3 四战术（保守 → 激进；2026-08-28 命中率体系）

```
命中率% = clamp(50 + 领先%×0.25 + 战术修正, 10, 90)
领先%   = (我方火力 − 对方火力) × 100 ÷ 对方火力（劣势方命中率可低至 ~13%）
```

| 选项 | 战术 | 战术修正 | 命中得分 | 未命中得分 |
|---|---|---|---|---|
| a | 守势布阵 | +10% | 6~10 | 2~4 |
| b | 稳健进攻 | +5% | 8~14 | 3~6 |
| c | 全力弹幕 | −5% | 10~20 | 4~8 |
| d | 搏命一击 | −15% | 12~26 | 5~10 |

掷骰：`th_danmaku_duel_dice_var`（1~100）≤ 该战术命中率 → 命中，取高区间；否则取低区间
（**低区间恒 > 0**，不再有 0 分/落空）。事件 TT 实时显示本回合命中率与命中/未命中得分区间。

### 4.4 怯战 / 投降 / 回避（2026-08-28 起替代挑衅）

- `.10` 怯战：发起方威望 -5（`th_danmaku_cowardice_prestige_value`）+ 清理对决状态。
- `.11` 投降：应对方威望 -5 + 发起方收到 `.12` 取消通知 + 清理对决状态。
- `.1` 回避（遭遇战）：威望 -5 + 清理遭遇状态。
- 数值集中在一个键（当前 -5，待调）：`th_danmaku_cowardice_prestige_value`。

### 4.5 胜负奖惩（五档；经 `th_danmaku_battle_reward_effect` 结算）

| 档 | 判定（分差% = (我方−对方)×100÷终点） | 金币 | 威望 | 研究点数 | 稳定度 | 贡献度 | 影响力 | 调查进度(异变中) |
|---|---|---|---|---|---|---|---|---|
| 大胜 | >35 | +80 | +16 | +20 | +10 | +20 | +10 | +5 |
| 胜利 | 5<..≤35 | +40 | +8 | +15 | +5 | +10 | +5 | +5 |
| 平手 | \|..\|≤5 | 0 | 0 | +10 | 0 | +5 | 0 | 0 |
| 败北 | −35≤..<−5 | −15 | −6 | +5 | 0 | 0 | 0 | 0 |
| 满目疮痍 | <−35 | −40 | −14 | +5 | −5 | 0 | 0 | 0 |

大胜/胜利额外获得 `th_danmaku_champion_modifier`（弹幕战冠军：弹幕火力值 +30、月度威望 +0.10，1 年）。

---

## 5. 异变预留接口（M3 异变系统落地前全部安全 no-op）

| 接口 | 本阶段 | M3 落地后由异变系统接管 |
|---|---|---|
| `th_gensokyo_in_incident_trigger`（已有） | `always = no` | 换成异变判定 |
| `th_gensokyo_incident_add_investigation_effect = { value = X }` | 非异变时 no-op；异变时累加 `th_gensokyo_investigation_progress_var` | 消费该变量更新调查进度 |
| `global_variable_list:th_gensokyo_incident_participant_list` | 不写入（对决选人自动回落） | 异变 on_start 填充参与者 |
| `th_gensokyo_incident_resolver_mark`（变量标记） | 不写入 | 指定解决者时打标 |
| `th_gensokyo_is_incident_resolver_trigger` | `always = no` | `has_variable = th_gensokyo_incident_resolver_mark` |

---

## 6. 平衡数值表（集中 `in_game/common/script_values/th_danmaku_values.txt`）

### 火力公式

| 键 | 初值 | 说明 |
|---|---|---|
| `th_danmaku_firepower_value` | — | 火力公式（§1.1；军事×10、容忍×100、稳定×2） |

### 遭遇战

| 键 | 初值 | 说明 |
|---|---|---|
| `th_danmaku_encounter_monthly_chance_value` | 2 | 遭遇月度概率%（当前 on_action 用字面量） |
| `th_danmaku_youkai_firepower_min/max_value` | 500 / 1000 | 无名妖怪火力 = 随机 500~1000（接口默认） |
| `th_danmaku_encounter_{great_victory,victory,draw,defeat,great_defeat}_{gold,prestige}_value` | 见 §3.3 | 遭遇五档奖惩 |
| `th_danmaku_encounter_{victory,great_victory}_investigation_value` | 2 / 4 | 异变调查进度 |

### 对决战

| 键 | 初值 | 说明 |
|---|---|---|
| `th_danmaku_duel_goal_value` | 100 | 胜负终点（固定；改本键即调整对决时长） |
| `th_danmaku_duel_draw_gap_value` / `rout_gap_value` | 5 / 35 | 分档阈值（≤5% 平手，>35% 大胜/满目疮痍） |
| `th_danmaku_duel_gap_pct_value` | — | 分差%脚本值（(我方−对方)×100÷终点；供 .22 分档；定义于本文件） |
| `th_danmaku_duel_hit_base/coef/min/max_value` | 50 / 0.25 / 10 / 90 | 命中率公式常数 |
| `th_danmaku_tactic_{1..4}_hit_adj_value` | +10 / +5 / −5 / −15 | 四战术命中修正 |
| `th_danmaku_tactic_{1..4}_{high,low}_value` | 见 §4.3 | 命中/未命中得分区间 |
| `th_danmaku_duel_{great_victory,victory,draw,defeat,rout}_{gold,prestige,research,stability,contribution,influence}_value` | 见 §4.5 | 对决五档奖惩 |
| `th_danmaku_duel_victory_investigation_value` | 5 | 异变调查进度（大胜/胜利） |
| `th_danmaku_duel_buff_years_value` | 1 | 冠军修正时长（年） |
| `th_danmaku_duel_stale_months_value` | 12 | 对决断链强清阈值（月） |

### 通用 / 妖兽

| 键 | 初值 | 说明 |
|---|---|---|
| `th_danmaku_cowardice_prestige_value` | −5 | 怯战/投降/回避 威望惩罚（可调） |
| `th_danmaku_beast_victory_{gold,research}_value` | 500 / 5 | 退治妖兽胜：500 金 + 5 研究点数（大胜/胜利同值） |
| `th_danmaku_beast_rampage_years_value` | 10 | 妖兽作乱修正时长（年；效果内用字面量 10） |
| `th_danmaku_beast_monthly_chance_value` | 2 | 妖兽爆发月度概率%（on_action 用字面量 2） |

---

## 7. 文件清单

| 文件 | 内容 |
|---|---|
| `main_menu/common/modifier_type_definitions/th_danmaku_modifiers.txt` | 修正类型（main_menu 副本） |
| `in_game/common/modifier_type_definitions/th_danmaku_modifiers.txt` | 修正类型（in_game 副本，须同步） |
| `in_game/common/static_modifiers/th_danmaku_modifiers.txt` | 冠军临时修正 + 妖兽作乱地点修正（挑衅修正已删除） |
| `in_game/common/script_values/th_danmaku_values.txt` | 火力公式 + 全部平衡常数 |
| `in_game/common/scripted_triggers/th_danmaku_triggers.txt` | 共享触发条件 |
| `in_game/common/scripted_effects/th_danmaku_effects.txt` | 全部接口实现（§2–§5） |
| `in_game/events/th_danmaku_events.txt` | 事件链（namespace `th_danmaku_events`） |
| `in_game/common/on_action/th_danmaku_chain_monthly.txt` | 随机遭遇 + 妖兽爆发 + 断链清理 |
| `in_game/common/generic_actions/th_danmaku_challenge.txt` | 玩家主动挑战 |
| `in_game/common/advances/th_gensokyo_common_advances.txt` | 追加 4 条科技火力挂钩 |
| `in_game/localization/{simp_chinese,english,japanese,korean,russian}/th_danmaku_l_*.yml` | 5 语言本地化 |

---

## 8. 注意事项

- 编码：全部 `.txt`/`.yml` 为 **UTF-8 BOM**；事件 ID 用 `namespace.integer`。
- 对决对手为 **AI 本地模拟**（开局捕获火力驱动随机），不依赖跨国事件链；
  如需真人交互，将 `.21` 改为 `trigger_event_non_silently` 到对手国家即可扩展。
- 对决采用**两段确认**（发起方确认挑战 → 对方接受），怯战/投降扣威望并清理；`.12` 取消通知对
  投降/对手缺失通用（desc 已去 [target] 强依赖，防 scope 缺失 ERROR）。
- 新变量一律 `has_variable` 守卫读取，防旧档 "not being set" 刷屏。
- 平衡改动只改 `th_danmaku_values.txt`，事件/效果不硬编码数值。
- 待验证（实机/参考库 Step 2/3）：`scope:X.value:自定义脚本值` 触发侧对比语法
  （当前全部走快照变量对比，验证通过后可替换为路线图原始公式）。

---

## 9. 妖兽作乱 / 退治妖兽（调试行动）

### 9.1 流程

```
月度脉冲（仅玩家）random 2% → .40 妖兽爆发
  .40 选项1 → th_danmaku_beast_outbreak_effect
    → 治下随机陆地地点 + 地点修正「妖兽作乱」（th_beast_rampage_modifier，
      税收/产出效率 -10%，10 年；EU5 无地点税收字段，用 local_production_efficiency）
  .40 选项2 → 无事发生
→ 治下出现带修正地点 → 行动 th_danmaku_subjugate_beast（退治妖兽）可见可用（CD 12 个月，失败后可再战）
行动 → select_trigger 选带修正的治下地点（interaction_source_list 过滤）
  → th_danmaku_beast_trigger_effect = { country = scope:actor location = scope:beast_location }
    守卫（地点存在+带修正+非对决中）→ 清旧标记 → 标本次地点（th_danmaku_beast_location_mark）
    → 快照我方火力 → 掷妖兽火力（th_danmaku_youkai_firepower_value，随机 500~1000）
    → 触发 .30 妖兽遭遇
  .30 选项「应战」→ th_danmaku_beast_resolve_effect（与遭遇战同五档算法）
    → .31 大胜 / .32 胜利 / .6 平手 / .33 败北 / .34 大败
  .31/.32 immediate: th_danmaku_beast_victory_effect = { investigation = Z }
    → 移除标记地点「妖兽作乱」修正 + 奖励（500 金 + 5 研究点数，大胜/胜利同值）+ 异变调查钩子 + 清变量
  .6 immediate: 经 th_danmaku_battle_reward_effect 结算（无得失）+ 清变量
  .33/.34 immediate: th_danmaku_beast_defeat_effect = { gold = X prestige = Y }
    → 金/威望惩罚 + 清变量（修正保留，可再次退治）
```

### 9.2 接口

| 接口 | 签名 | 说明 |
|---|---|---|
| `th_danmaku_beast_outbreak_effect` | 国家 scope | 治下随机陆地地点 +「妖兽作乱」修正 10 年（.40 选项1 与调试共用） |
| `th_danmaku_beast_trigger_effect` | `{ country = <退治国> location = <地点 scope> }` | 开始妖兽战斗（标记地点 + 掷火力 + 触发 .30）；行动内 `country = scope:actor`，事件内 `country = ROOT` |
| `th_danmaku_beast_resolve_effect` | 国家 scope | 五档火力比 → 触发妖兽结局事件（含 .6 平手） |
| `th_danmaku_beast_victory_effect` | `{ investigation = Z }` | 移除标记地点修正 + 奖励（金/研究用固定常量 500/5）+ 清变量 |
| `th_danmaku_beast_defeat_effect` | `{ gold = X prestige = Y }` | 惩罚 + 清变量（修正保留） |

调试方法：
- 随时触发妖兽爆发：任意事件/控制台调用 `th_danmaku_beast_outbreak_effect = yes`（或直接 `trigger_event_non_silently = th_danmaku_events.40`）。
- 临时提高频率：把 `th_danmaku_chain_monthly.txt` 中妖兽爆发的 `random = { chance = 2 }` 改为 `50`。
- 直接开战：`th_danmaku_beast_trigger_effect = { location = <某带修正地点> }`。

### 9.3 边界

- 无治下陆地 → `.40` 事件 trigger 守卫不触发；outbreak 效果空转安全。
- 对决进行中 → `th_danmaku_subjugate_beast` 行动 potential 反守卫（不显示）；`th_danmaku_beast_trigger_effect` 再守卫一次。
- 玩家弃置 `.30` 不点 → 月度孤儿标记清理（标记存在但修正已消失时清除）。
- 多地点妖兽 → 各自独立修正；退治一次只清所选地点（标记法）。
- 妖兽战斗为单阶段（一次遭遇→一次结算）；如需强化多轮可后续接对决链。
