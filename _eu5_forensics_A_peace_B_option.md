# EU5 脚本取证报告：A 和平/战争结束钩子 · B 事件 option 字段
## 取证常量
- `G` = `F:\SteamLibrary\steamapps\common\Europa Universalis V\game\in_game`
- `OA` = `G\common\on_action\_hardcoded.txt`（含 130 个 `on_*` 定义，下列行号均指此文件）
- `D` = `F:\Paradox Interactive\Europa Universalis V\mod\eu5-modding-project\reference_official_defines`
- 等级：**VERIFIED**（原文直证）/ **UNVERIFIED**（证据不足）/ **FAILED**（未找到）

---
# A 和平（战争结束）
## A1 达成和平/停战时触发哪个 on_action
**没有任何 `on_peace` / `on_peace_made` 钩子**（A3 已穷举）。战争终止的权威钩子是配对的两个：
**VERIFIED — `OA:1777-1779`**
```
1777: #root = country  (after winning and losing, for both), scope:winner = country, scope:loser = country, scope:war = war
1778: on_ending_war = {
1779: 	effect = {
```
**VERIFIED — `OA:1718-1720`**（和约条款执行**之前**）
```
1718: #root = country  (after winning and losing, for both, but before peace terms were executed), scope:winner = country, scope:loser = country, scope:war = war
1719: on_pre_ending_war = {
1720: }
```
注意 `on_pre_ending_war` 在 base game 内**函数体为空**（1720 行立闭）——vanilla 自己没用它，但引擎会调用。

## A2 作用域与触发范围
**作用域（VERIFIED，逐字来自 A1 两处注释）**：`root = country`（不是 war）；`scope:winner = country`；`scope:loser = country`；`scope:war = war`。**没有** `scope:actor` / `scope:recipient`（这两个只出现在别的钩子上，见 A3）；"for both" = **胜方与败方各触发一次**，root 分别是双方。
**触发范围（任意和约 vs 特定和约）→ UNVERIFIED**
- 注释只写 `after winning and losing, for both`，**完全未提白和（white peace）**。
- 弱旁证（倾向"白和时 scope:winner/loser 可能不存在"）：同一 `on_ending_war` 块内混用可选操作符 —— `OA:1901: scope:winner ?= {`、`OA:1915: scope:loser ?= {`；而同块他处直接写 `OA:1804: scope:winner = {`、`OA:1810: scope:winner = { trigger_event_non_silently = flavor_ere.3 }`。
- 全 `game\` 根目录 grep `on_ending_war` **仅命中 `OA:1778` 一处定义**，无任何补充文档。
→ **不得断言"白和一定触发/一定不触发"**，必须进游戏实测（打一场白和，在 `on_ending_war` 里跑 `trigger_event_silently` 或写日志）。
**两个易被误当成"停战"的钩子**：`on_enforce_peace_accepted` / `on_enforce_peace_declined` 注释写 `#happens before the war is ended, scope:actor = actor, scope:recipient = recipient, scope:war = war`（`OA:5611`），那是**"强制和平"外交动作**的结果，不是停战本身；`on_took_location_in_peace_treaty` 只在**割地条约逐块领土**执行时触发（`OA:2341-2342`），白和/纯赔款不触发。

## A3 与 war / peace 相关的 on_action 全名单（逐条 VERIFIED）
**战争终止 / 胜负（核心）**
| 行号 | 名字 | vanilla 注释原文 |
|---|---|---|
| 1719 | `on_pre_ending_war` | `#root = country  (after winning and losing, for both, but before peace terms were executed), scope:winner = country, scope:loser = country, scope:war = war` |
| 1778 | `on_ending_war` | `#root = country  (after winning and losing, for both), scope:winner = country, scope:loser = country, scope:war = war` |
| 1356 | `on_winning_war` | `#root = country, scope:winner = country, scope:loser = country, scope:war = war`（`OA:1355`） |
| 1723 | `on_pre_winning_war` | `#root = country, scope:winner = country, scope:loser = country, scope:war = war`（`OA:1722`） |
| 1694 | `on_losing_war` | `#root = country, scope:winner = country, scope:loser = country, scope:war = war`（`OA:1693`） |
| 1774 | `on_pre_losing_war` | `#root = country, scope:winner = country, scope:loser = country, scope:war = war`（`OA:1773`） |
**战争开始 / 加入**
| 行号 | 名字 | vanilla 注释原文 |
|---|---|---|
| 2011 | `on_pre_war_declared` | `#root = country, scope:actor = country who declares the war, scope:recipient = country who gets declared on - fires before the war is actually created`（`OA:2010`） |
| 2055 | `on_war_declared` | `#root = country, scope:actor = country who declares the war, scope:recipient = country who gets declared on, scope:war = war`（`OA:2054`） |
| 1647 | `on_join_war` | `#root = country`（`OA:1646`） |
| 2283 | `on_accepted_call_to_arms` | `#scope:actor = caller, scope:recipient = callee, scope:war = war`（`OA:2282`） |
| 2312 | `on_rejected_call_to_arms` | `#scope:actor = caller, scope:recipient = callee, scope:war = war`（`OA:2311`） |
**和约内容（≠ 停战本身）**
| 行号 | 名字 | vanilla 注释原文 |
|---|---|---|
| 2342 | `on_took_location_in_peace_treaty` | `#root = winner, scope:location = location, scope:winner = new owner, scope:loser = old owner`（`OA:2341`） |
| 5612 | `on_enforce_peace_accepted` | `#happens before the war is ended, scope:actor = actor, scope:recipient = recipient, scope:war = war`（`OA:5611`） |
| 5621 | `on_enforce_peace_declined` | `#scope:actor = actor, scope:recipient = recipient, scope:war = war`（`OA:5620`） |
| 5648 | `on_truce_broken` | `#root = actor, scope:recipient = country actor broke the truce with, scope:war = war that broke the truce`（`OA:5647`） |
**内战（war 语义，独立命名）**：`OA:992 on_civil_war_start`（`# root = original country which gets targeted by the civil war, scope:target = rebel country which declares the war, scope:war = the civil war, scope:rebel is the rebel`，`OA:991`）、`OA:604 on_civil_war_annex`、`OA:754 on_civil_war_annexed`、`OA:1161 on_civil_war_lost`（`# root and scope:winner = winner, scope:loser = loser`，`OA:1160`）、`OA:1312 on_civil_war_won`（同注释，`OA:1311`）
**战争副作用（占领/攻陷/吞并）**：`OA:278 on_siege_won`（`# When a location with fort changes controller after a siege.` + `# root = country, scope:target = location, scope:character = leading general character`，`OA:276-277`）、`OA:351 on_siege_lost`、`OA:399 on_location_occupied`（`# When a location without fort changes controller after an occupation process`，`OA:397`）、`OA:481 on_location_lost`、`OA:539 on_military_annex`、`OA:569 on_diplomatic_annex`、`OA:636 on_colonize_annex`、`OA:641 on_annex`、`OA:748 on_military_annexed`、`OA:751 on_diplomatic_annexed`、`OA:757 on_annexed`、`OA:960 on_annexation_start`、`OA:980 on_annexation_cancel`
**官方文档佐证（很弱，只列"新增项"）**：`D\changes_script_docs.md:161-167`（`## On Actions` 表）全文仅 4 条 —— `164: | Added | \`on_new_age_global\` | \`none\` |`、`165: | Added | \`on_estate_culture_changed\` | \`none\` |`、`166: | Added | \`on_estate_religion_changed\` | \`none\` |`、`167: | Added | \`on_pre_war_declared\` | \`none\` |`；且 `D\changes_script_docs.md:13`：`* The on action scope is based on the script documentation, for more information see the \`common/on_actions\` directory` → **权威名单只能是 `OA`**。
**反向排除（"不存在"也是 VERIFIED）**：全 `game\` 根目录 grep `on_ending_war|on_peace_made|on_war_end|on_peace_` → `on_ending_war` 仅 `OA:1778`，其余三个**零命中**；`G\common\on_action\` 全目录 grep `(?i)peace` → 只命中 `OA` 内部（599/1718/1789/1796/1935/2342/2344/2456/3851/3868/5612/5615/5621/5624）与无关的 `treasure_voyage.txt:13 chi_expedition_war_support_pulse`；同目录 grep `(?i)truce` → 只有 `OA:5647-5648`。

## A4 "战争结束" vs "和平"的区别与证据
1. **"和平"没有独立钩子**：A3 反向排除已证（无 `on_peace*` / `on_war_end`）。
2. **"战争结束"只有 `on_ending_war` / `on_pre_ending_war`**，语义是"胜负双方各跑一次"，**不是"签署了和约"这一动作**。
3. **割地和平**另有 `on_took_location_in_peace_treaty`（`OA:2342`），但它**逐 location** 触发、只覆盖"转移领土"型条约；白和、赔款、附庸、羞辱**不触发**它。
4. **和约类型本身是可脚本化的数据对象，不是 on_action**：`D\types\peace_treaties.txt:1`: `# script your own peace treaties!`；`:3`: `# potential = trigger, scope:winner = taker, scope:loser = giver, scope:war = war they're in, scope:target = location/country/province specified`；`:5`: `# effect = effect when the treaty is executed, scope:winner = taker, scope:loser = giver, scope:war = war they're in, scope:target = location/country/province specified`。base game 实机 `G\common\peace_treaties\` 有 50+ 个 `.txt`（实测含 `force_convert.txt`、`humiliate.txt`、`subjugate_neighbor_native.txt`、`religious_supremacy.txt` 等）——**这是"特定和约"级别的钩子，`on_ending_war` 做不到**。
5. **判断建议**（结论，非原文）：要"任意 peace treaty 都触发" → `on_ending_war`（白和是否触发待实测）；要"割走领土时触发" → `on_took_location_in_peace_treaty`；要"某一类条约专属效果" → 自写 `common\peace_treaties\*.txt` 的 `effect`。

---
# B 事件 option 字段
## B1 option 顶层字段清单（对 `G\events\**.txt` 全量 8881 个 option 块机械扫描）
| 字段 | 次数 | 首个逐字样例（路径:行号 + 原文） |
|---|---|---|
| `name` | 14136 | `G\events\ages.txt:15`: `name = ages_of_eu.adm` |
| `custom_tooltip` | 2666 | `G\events\civil_war.txt:54`: `custom_tooltip = civil_war_game_over` |
| `historical_option` | 2279 | `G\events\earthquake_events.txt:303`: `historical_option = yes` |
| `trigger` | 1430 | `G\events\colonial_federation_events.txt:113`: `trigger = { is_ai = no }` |
| `ai_chance` | 1124 | `G\events\hre.txt:60`: `ai_chance = {` |
| `show_as_tooltip` | 380 | `G\events\free_cities.txt:39`: `show_as_tooltip = {` |
| `ai_will_select` | 178 | `G\events\ages.txt:19`: `ai_will_select = {` |
| `high_risk_option` | 73 | `G\events\civil_war.txt:23`: `high_risk_option = yes` |
| `fallback` | 1 | `G\events\imperial_circles_events.txt:131`: `fallback = yes` |
| `evil_option` / `high_reward_option` / `moral_option` | 各 1 | 仅 `G\events\debug\000_johan_debug.txt:230 / 283 / 245`（debug 专用，勿当正式字段） |
**`trigger` 两种形态**：单行 `G\events\colonial_federation_events.txt:113 → trigger = { is_ai = no }`；多行 `G\events\free_cities.txt:240-242`
```
240: 		trigger = {
241:             has_variable = fc_help_flag
242: 		}
```
（条件不满足则该 option **不显示**；`free_cities.5` 的 a/b 两个 option 各带互斥 flag）
**`ai_chance`（乘算权重：`factor` + `modifier`）— `G\events\hre.txt:60-66`**
```
60: 		ai_chance = {
61: 			factor = 10
62: 			modifier = {
63: 				factor = 0
64: 				NOT = { has_variable = voted_for_privilegia }
65: 			}
66: 		}
```
**`ai_will_select`（脚本值：`value`）— `G\events\ages.txt:19-26`**
```
19: 		ai_will_select = {
20: 			if = {
21: 				limit = {
22: 					has_or_had_tag = TUR
23: 				}
24: 				value = 1000
25: 			}
26: 		}
```
另：`ai_will_select` 裸值 `G\events\character\noble_marriage.txt:186: ai_will_select = { value = 0 }`；`ai_chance` 裸值 `G\events\character\dynastic.txt:1571: ai_chance = 1`、`:1619: ai_chance = 0`。
**FAILED: 未找到 `highlight` 作为 event option 字段。** `^\s*highlight\s*=` 在全 `G` 只命中 7 处，全部在 `G\common\missions\generic_capital_economy_mission_pack.txt:273/375/513/587/620/639/720`（mission 字段）；option 级扫描 `highlight` 出现 **0 次**。
**FAILED: 未找到 option 级 `tooltip = <key>` 字段。** option 级扫描 `tooltip` 出现 **0 次**（自定义 tooltip 只有 `custom_tooltip` 与 `show_as_tooltip`）。

## B2 option 的 tooltip 自定义（三种写法，全 VERIFIED）
**写法 1：`custom_tooltip = <loc key>`（纯文本替换，隐藏真实效果）— `G\events\civil_war.txt:52-55`**
```
52: 	option = {
53: 		name = civil_war.1.b
54: 		custom_tooltip = civil_war_game_over
55: 	}
```
**写法 2：`custom_tooltip = { text = <loc key> ...effects... }`（自定义文本；块内 effect 只显示不额外执行）— `G\events\DHE\flavor_ENG.txt:21924-21929`**
```
21924: 	option = {
21925: 		name = flavor_eng.217.b
21926: 		trigger = { modifier:has_a_parliamentary_system = yes }
21927: 
21928: 		custom_tooltip = {
21929: 		text = flavor_eng.217.b.custom
```
（21930 起块内即为 effect：`region:great_britain_region = {` …）
另一种单行块形式：`G\events\character\personality_events.txt:2475: custom_tooltip = { text = personality_events.58.a.tt}`
**写法 3：`show_as_tooltip = { ...effects... }`（效果真实执行，并额外作为 tooltip 展示）— `G\events\free_cities.txt:257-263`**
```
257: 		show_as_tooltip = {
258: 			add_opinion = { 
259:                 target = scope:hre_leader 
260:                 modifier = opinion_sent_help
261:             }
262: 		}
263: 		remove_variable = fc_help_flag
```
**结论**：option 里**没有** `tooltip = ...`，**没有** `show_as_tooltip = <key>` 取值形式；自定义文案只能走 `custom_tooltip`（key 或 `{ text = key ... }`）。

## B3 事件顶层字段（全量扫描 4534 个事件块）
**字段与出现次数**：`option` 8881 · `outcome` 4536 · `type` 4534 · `title` 4516 · `desc` 4515 · `immediate` 4081 · `trigger` 3424 · `illustration_tags` 3119 · `fire_only_once` 1767 · `dynamic_historical_event` 1566 · `historical_info` 879 · `image` 849 · `hide_portraits` 578 · `category` 572 · `after` 208 · `major` 127 · `major_trigger` 121 · `orphan` 85 · `hidden` 7 · `on_trigger_fail` 2 · `weight_multiplier` 2
**`outcome` 枚举实测（全 `G` 扫描 7508 次赋值）**：`neutral 7331` / `negative 126` / `positive 50` → **VERIFIED 只有这 3 个取值**。**FAILED: 未找到 `outcome = good` / `outcome = bad`**（base game 零命中；工作区旧笔记 `eu5-modding-project\docs\knowledge\BRIEF.md:249` 声称 5 个取值，**以实机为准**）。**1.2+ 是否必填 → UNVERIFIED（工作区旁证）**：`eu5-modding-project\docs\guides\AI_Tool_Workflow_Prompt.md:131` 记录 1.2 新增校验器（引 `event_database.cpp:648`）要求顶层 `outcome`，但非 base game 原文。官方快照 `D\changes_script_docs.md` grep `outcome` **零命中**。
**`type` 枚举实测**：`country_event 7216` / `exploration_event 36` / `location_event 20` / `age_event 1`（`G\events\ages.txt:4`）/ `omens_event 1`。
**FAILED: 未找到事件顶层 `on_end`。** `^\s*on_end\s*=` 全 `G` 命中 36 处，**全部在 `G\common\disasters\*.txt`**（disaster 字段），events 目录零命中；事件用的是 `after`（208 次）。
**完整 vanilla 国家事件例子（15 行，逐字，`G\events\innovativeness_events.txt:305-319`）**
```
305: innovativeness_events.13 = {
306: 	type = country_event
307: 	title = innovativeness_events.13.title
308: 	desc = innovativeness_events.13.desc
309: 	outcome = neutral
310: 	image = "gfx/interface/illustrations/institutions/scientific_revolution.dds"
311: 	trigger = {
312: 		has_embraced_institution = institution:renaissance
313: 	}
314: 
315: 	option = {
316: 		name = innovativeness_events.13.a
317: 		add_research_progress = research_progress_mild_bonus
318: 	}
319: }
```
**其余字段的逐字行证（短事件装不下全部）**
- `namespace` + `trigger` + `immediate` — `G\events\estates\nobles_estate_events.txt:1-20`
```
1: namespace = nobles_estate_events
3: 	type = country_event
8: 	trigger = {
9: 		"estate_power(estate_type:nobles_estate)" >= 0.25
10: 		NOT = { has_estate_privilege = estate_privilege:noble_leaders_only }
11: 	}
18: 	immediate = {
19: 		event_illustration_estate_effect = { foreground = estate_type:nobles_estate background = estate_type:nobles_estate }
20: 	}
```
- `after`（写在 option 之后的事件收尾）— `G\events\civil_war.txt:57-64`
```
57: 	after = {
58: 		hidden_effect = {
59: 			if = {
60: 				limit = { scope:winner = { is_revolutionary = yes } }
61: 				scope:winner = { trigger_event_silently = revolution_disaster.4 }
62: 			}
63: 		}
64: 	}
```
- `on_trigger_fail`（trigger 不满足时的补救）— `G\events\DHE\flavor_chi_pap.txt:158-167`
```
158: 	on_trigger_fail = {
159: 		if = {
160: 			limit = {
161: 				scope:target_character = {
162: 					is_alive = yes
163: 				}
164: 			}
165: 			kill_character_silently = scope:target_character
166: 		}
167: 	}
```
- `category`：`G\events\disaster\reform_society.txt:5: category = disaster_event`
- `hidden` / `fire_only_once`：`G\events\ai_area_conqest_events\hidden_events_for_ai_conquest.txt:9: hidden = yes`、`:11: fire_only_once = yes`
- `major` / `major_trigger`：`G\events\colonial_federation_events.txt:8-9`

## B4 脚本触发国家事件的确切写法
**FAILED: 未找到 `trigger_event = { id = X }`。** 三条独立取证：全 `game\` 根目录 grep `trigger_event\b`（词边界，排除 `_silently`）**零命中**；全 `G` grep `trigger_event\s*=\s*\{` **零命中**；`D\` 官方快照 grep `trigger_event` **零命中**。→ **EU5 (Jomini) base game 不存在 `trigger_event` 这个 effect**，只有下面两个：
**VERIFIED — `trigger_event_silently`（静默：不发通知/不弹窗）**
| 路径:行号 | 逐字原文 |
|---|---|
| `G\events\character\personality_events.txt:32` | `trigger_event_silently = { id = personality_events.2 days = { 20 200 } }` |
| `G\events\character\dynastic.txt:394` | `trigger_event_silently = { id = dynastic.6001 months = 9 }` |
| `G\events\disaster\turmoil_in_brandenburg.txt:1386` | `trigger_event_silently = { id = turmoil_in_brandenburg.1005 years = 1 }` |
| `G\events\economy\banking.txt:80` | `trigger_event_silently = banking.2`（**裸 id 简写，可省块**） |
| `G\events\character\consort_events.txt:548` | `scope:from = {	trigger_event_silently = { id = consort_events.58 } 	}`（**换作用域 = 让目标国触发**） |
**VERIFIED — `trigger_event_non_silently`（发通知）**
| 路径:行号 | 逐字原文 |
|---|---|
| `G\events\character\court_flavor_events.txt:112` | `trigger_event_non_silently = { id = court_flavor_events.3 days = 15 }` |
| `G\events\character\dynastic.txt:1578` | `scope:target_appanage = { trigger_event_non_silently = dynastic.30 }`（换作用域 = 目标国触发） |
| `G\events\character\dynastic.txt:1380` | `1 = { trigger_event_non_silently = { id = dynastic.25 days = 20 } }`（位于 `random_list` 权重项内） |
| `G\events\disaster\war_of_the_aragonese_union_disaster.txt:63` | `trigger_event_non_silently = { id = war_of_the_aragonese_union_disaster.2 days = 5}` |
**可选字段（实测穷举）**：`id = <namespace.N>`（必需）；延时 `days = N` / `months = N` / `years = N`，**支持二元随机区间** —— `days = { 20 200 }`（`personality_events.txt:32`）、`months = { 50 200 }`（`G\events\disaster\savonarola.txt:526`）、`days = { 720 2000 }`（`G\events\character\consort_events.txt:89`）；**目标国不写在参数里**，而是在 effect 外面套 scope：`scope:<X> = { trigger_event_silently = { id = ... } }`，事件在 `scope:<X>` 的该国触发（`consort_events.txt:548`、`dynastic.txt:1578`）。

---
# FAILED 清单
1. **FAILED: 未找到 event option 字段 `highlight`**（`^\s*highlight\s*=` 只命中 mission 文件 7 处，option 级 0 次）
2. **FAILED: 未找到 option 级 `tooltip = <key>` 字段**（option 全量扫描 `tooltip` 0 次）
3. **FAILED: 未找到 `outcome = good` / `outcome = bad`**（base game 零命中；实机只有 neutral / negative / positive）
4. **FAILED: 未找到事件顶层 `on_end`**（36 处全在 `common\disasters\`，events 目录零命中；事件用 `after`）
5. **FAILED: 未找到 `trigger_event`（含 `trigger_event = { id = X }`）**（全 `game\` 词边界 grep 零命中；只有 `trigger_event_silently` / `trigger_event_non_silently`）
6. **FAILED: 未找到 `on_peace` / `on_peace_made` / `on_war_end`**（全 `game\` grep 零命中）
7. **FAILED: 官方文档快照无 war/peace on_action 全表**（`D\changes_script_docs.md:161-167` 只列 4 条 Added 项）
8. **FAILED: 官方文档快照无 `outcome` 说明**（`D\changes_script_docs.md` grep `outcome` 零命中）
9. **UNVERIFIED：`on_ending_war` 在白和（white peace）时是否触发**。仅有注释 `(after winning and losing, for both)` 与同块内 `OA:1901 scope:winner ?= {` / `OA:1915 scope:loser ?= {` 的弱旁证，**必须实测**。
10. **UNVERIFIED（工作区旁证，非 base game 原文）：`outcome` 是否为 1.2+ 硬校验必填**。来源 `eu5-modding-project\docs\knowledge\BRIEF.md:249` 与 `docs\guides\AI_Tool_Workflow_Prompt.md:131`（后者引 `event_database.cpp:648`），未在 base game 明文确认。
