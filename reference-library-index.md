# EU5 PDX Script 参考库索引与用法指南
# EU5 PDX Script Reference Library — Index & Usage Guide

> 本文件是 EU5 PDX script 编码教程库的**索引与用法**。参考库本体位于
> `..\eu5-modding-project\`（下称"库"）。AI 工具和人类用户在编写 EU5 脚本时，
> 先读本索引定位目标参考文件，再打开对应文件取用真实语法。
>
> This file indexes the EU5 PDX script coding-tutorial library located at
> `..\eu5-modding-project\` (the "library"). Before writing EU5 scripts, use this
> index to locate the right reference file, then open it for the exact syntax.
>
> 库目标版本：EU5 1.3.x（Jomini 引擎）· 参考库含原版脚本、官方类型定义、33 个社区模组。
> Library target version: EU5 1.3.x (Jomini engine) — vanilla scripts, official type
> definitions, and 33 community mods.

---

## 目录 Table of Contents

1. [库总览 Overview](#1-库总览-overview)
2. [用法指南 Usage Guide](#2-用法指南-usage-guide)
3. [reference_official_defines — 官方定义](#3-reference_official_defines--官方定义)
4. [reference_game_files — 原版游戏文件](#4-reference_game_files--原版游戏文件)
5. [reference_mods — 社区模组](#5-reference_mods--社区模组)
6. [docs — 项目文档](#6-docs--项目文档)
7. [data/index — 生成符号索引](#7-dataindex--生成符号索引)
8. [AI 快速速查表 Quick Cheat Sheet](#8-ai-快速速查表-quick-cheat-sheet)

---

## 1. 库总览 Overview

库 `..\eu5-modding-project\` 的参考部分由 5 块组成（`src/` 是 SOL 模组本体源码，仅作"本库如何自举"的最佳实践范例）：

| 目录 Directory | 内容 Contents | 何时用 When to use |
|---|---|---|
| `reference_official_defines\` | 官方类型定义 + 引擎脚本/GUI 数据类型文档 | 语法**权威验证**（Step 2） |
| `reference_game_files\` | 原版 EU5 全部脚本/事件/GUI 源码镜像 | 找真实可用范例（Step 3） |
| `reference_mods\` | 33 个社区模组，覆盖经济/UI/机制/兼容性 | 找复杂/兼容性范例 |
| `docs\knowledge\` | 已验证的坑点(BRIEF/anti_patterns/valid_enums) | 写码前**必读**防坑清单 |
| `data\index\` | 生成器产出的符号索引（触发器/效果/修饰符/图标） | 快速查名称是否已存在 |

库中还有 `scripts\`（代码生成 + 校验工具，含 `validate.py` 预检）与 `tools\`，
供开发本库/生成脚本使用，参考 `docs\knowledge\PROJECT_OVERVIEW.md` 的 Script Reference 表。

---

## 2. 用法指南 Usage Guide

### 2.1 三步判定规则 The 3-Step Resolution Rule

> 写任何 EU5 脚本时按此顺序，命中即停：

1. **直接写 Direct Edit** — 仅当你对语法 100% 确定（如标准 Jomini 逻辑）。
2. **查官方文档 Consult Docs** — 先查 `reference_official_defines\`。
3. **查源码 Consult Source** — 再查 `reference_game_files\` 与 `reference_mods\`。

### 2.2 禁止直接写（必须先查证）Mandatory Reference Categories

以下类别 **禁止凭记忆直接写**，必须进入 Step 2/3 验证，且写码前输出验证行：

| 类别 Category | 查证位置 Where to verify |
|---|---|
| `blockoverride` 块名及子属性 | `reference_game_files\game\in_game\gui\shared\cards.gui` 及各类 `cards.gui` |
| `custom_tooltip` 键格式 | 任一事件 `.txt`（如 `reference_game_files\game\in_game\events\*.txt`） |
| `situation_card_common` / `card_common` 模板结构 | `reference_game_files\game\in_game\gui\shared\cards.gui` |
| `location_rank:*` 枚举 | `docs\knowledge\valid_enums.yaml`（仅 `rural_settlement`/`town`/`city`） |
| 任何 static/country/location modifier 名称 | `reference_game_files\game\main_menu\common\modifier_type_definitions\00_modifier_types.txt` |
| 非本模组定义的 scripted_trigger / scripted_effect | `reference_game_files\game\in_game\common\scripted_triggers\` / `scripted_effects\` |
| 本地化 YAML 编码与引号 | 见 `data\index\loc_keys_en.txt`；规则见 `docs\knowledge\BRIEF.md` |
| GUI 表达式语法（`GetVariable`/`.IsSet`/`MakeScope`） | `reference_official_defines\docs\data_types_gui.txt` + 任意 `.gui` 范例 |
| 任何 GUI 图标显示 | 先查 `reference_game_files\game\main_menu\gui\shared\font_icons.gui` 的 `@xxx!` 内联语法 |

验证行格式（写码前必须输出）：
> **Verification** — Step [2/3], Reference: `path:line`, Quote: `"exact source text"`

### 2.3 按需求查哪里 Quick category → path map

| 我要写 What I need | 去查 Look here |
|---|---|
| 一个事件（event） | `reference_game_files\game\in_game\events\`（如 `ages.txt` 含 `outcome =` 范例） |
| 效果/触发器名称 | `reference_official_defines\docs\data_types_script.txt`（3872 行全表） |
| GUI 控件/表达式 | `reference_official_defines\docs\data_types_gui.txt` |
| scripted_effect 写法 | `reference_game_files\game\in_game\common\scripted_effects\country_effects.txt` 等 |
| script_value 写法 | `reference_game_files\game\in_game\common\script_values\`（注意 5 位小数、`var:` 前缀坑） |
| 修饰符（static/location/country） | `reference_game_files\game\main_menu\common\static_modifiers\` + `modifier_type_definitions\` |
| 商品定义 / pop 需求 | `reference_game_files\game\in_game\common\goods\`、`goods_demand\pop_demands.txt` |
| on_action 钩子 | `reference_game_files\game\in_game\common\on_action\` |
| situation（事件型界面） | `reference_game_files\game\in_game\common\situations\` + `gui\panels\` |
| 地图模式 / 图标 DDS | `reference_game_files\game\in_game\gfx\map\map_modes\`（实际该目录需在库内确认） |
| 兼容性 INJECT/REPLACE 规则 | `docs\technical\EU5_Multi_Mod_Compatibility.md` + 各 compat 模组 |
| 防踩坑清单 | `docs\knowledge\BRIEF.md`（先读！） |

---

## 3. reference_official_defines/ 官方定义

官方/引擎文档，**语法验证的第一站（Step 2）**。

### 3.1 docs/ — 引擎数据类型文档

| 文件 File | 行数 Lines | 内容 Contents |
|---|---|---|
| `data_types_script.txt` | 3,872 | 触发器/效果/作用域/迭代器/event targets 全表 |
| `data_types_gui.txt` | 4,498 | GUI 表达式、widget、datacontext、函数 |
| `data_types_common.txt` | 1,395 | 通用类型 |
| `data_types_internalclausewitzgui.txt` | 12,836 | 内部 Clausewitz GUI 类型 |
| `data_types_uncategorized.txt` | 90,037 | 未分类杂项（量大，先 grep 后读） |

### 3.2 types/ — 官方类型定义（对象属性白皮书）

`ai_scripted_expansion_score.txt`, `ai_scripted_expansion_target.txt`, `artist_types.txt`,
`building_types.txt`, `casus_belli.txt`, `gui_filters.txt`, `institutions.txt`,
`international_organizations.txt`, `international_organization_land_ownership_rules.txt`,
`international_organization_payments.txt`, `laws.txt`, `peace_treaties.txt`, `tests.txt`,
`unit_types.txt`

每个文件以 `# 属性名: <类型> 说明` 列出该类对象的全部可用字段（如 `building_types.txt`
列出 `build_time`/`modifier`/`allow`/`on_built` 等）。写新对象定义前对照。

### 3.3 changes_*.md — 1.3 版本变更记录

`changes_data_types.md`, `changes_files.md`, `changes_script_docs.md`, `changes_types.md`
（记录 EU5 1.3 相对旧版新增/修改的 trigger/effect/type/文件，`changes_script_docs.md` 含
"Added" 标记的新增项）。

> 提示：`data_types_uncategorized.txt` 超大，务必先 `Select-String`/`rg` 精确搜索再读取。

---

## 4. reference_game_files/ 原版游戏文件

原版 EU5 脚本完整镜像（Step 3 主战场），目录 `game\` 下按 DLC/加载阶段划分。

### 4.1 顶层结构 Top-level layout

| 目录 | 文件数 | 说明 |
|---|---|---|
| `in_game\common\` | 1,846 | 游戏机制脚本（核心参考区） |
| `in_game\events\` | 349 | 原版事件 |
| `in_game\gui\` | 408 | 游戏内 GUI |
| `in_game\setup\` | 46 | 开局/设置脚本 |
| `in_game\localization\` | 2 | （主本地化在 main_menu） |
| `main_menu\common\` | 56 | 修饰符/图标/规则等定义 |
| `main_menu\gui\` | 89 | 主菜单/共享 GUI（含 font_icons.gui） |
| `main_menu\localization\` | 1,058 | 全部本地化 YAML（含简体中文） |
| `loading_screen\` | 80 | 启动/defines（`common\defines\`） |
| `dlc\` | — | DLC 增量（D008 凤凰之命运等） |

### 4.2 in_game/common/ 关键子类索引（按脚本类型）

| 子目录 Subdir | 用途 | 代表文件 |
|---|---|---|
| `goods\` | 商品定义（demand_add/development_threshold） | `00_raw_materials.txt`, `01_plantation_goods.txt`, `02_produced_goods.txt`, `03_food.txt` |
| `goods_demand\` | 需求组（pop/军队/建筑） | `pop_demands.txt`, `army_demands.txt`, `building_construction_costs.txt` |
| `scripted_effects\` | 效果脚本范例 | `country_effects.txt`, `location_effects.txt`, `situation_effects.txt`, `global_effects.txt` |
| `scripted_triggers\` | 触发脚本范例 | `country_triggers.txt`, `location_triggers.txt`, `pop_triggers.txt`, `goods_triggers.txt` |
| `script_values\` | 数值计算范例 | `monthly_income.txt`, `define_values.txt`, `diplomatic_values.txt` |
| `situations\` | situation 定义（含数据地图） | `black_death.txt`, `little_ice_age.txt`, `great_pestilence.txt` |
| `on_action\` | 脉冲/钩子 | `country_monthly.txt`, `country_yearly.txt`, `country_biyearly.txt` |
| `prices\` | 价格对象 | `00_hardcoded.txt`, `01_buildings.txt`, `02_units.txt` |
| `auto_modifiers\` | 自动修饰符（注意 location 不可用） | `country.txt`, `byzantium.txt` |
| `static_modifiers` 见 `main_menu\common\` | — | — |
| 其他 90+ 子类 | 机制对象定义 | `building_types\`, `laws\`, `government_reforms\`, `disasters\`, `estates\`, `missions\`, `wargoals\`, `religions\`, `cultures\` 等 |

> 提示：`goods_demand\pop_demands.txt` 含 goods group 的权威写法（`upper` 组在 1.3.11
> 包含 nobles/clergy/burghers/laborers/soldiers）；写 pop 需求前对照。

### 4.3 in_game/gui/ 关键文件

- `shared\cards.gui` — situation_card_common / card_common / blockoverride 权威模板。
- `shared\*_tooltips.gui` — 各作用域 tooltip 模板（`location_tooltips.gui`, `economy_tooltips.gui`,
  `country_tooltips.gui`, `pop_tooltips.gui`, `market_tooltips.gui`, `modifier_tooltips.gui` 等）。
- 顶层视图 `*.gui` — 每个 UI 面板一个文件（`location_window.gui`, `goods_overview.gui`,
  `situation_view.gui`, `eventwindow.gui`, `economy_lateralview.gui` 等），需整窗/整面板范例时查。
- `panels\` — situation 面板。

### 4.4 main_menu/gui/ 关键文件

- `shared\font_icons.gui` — **180+ 内联图标 `@xxx!` 权威清单**（GUI 图标显示第 1 优先）。
- `shared\icons.gui`, `shared\labels.gui`, `shared\tables.gui`, `shared\window_components.gui` — 基础控件模板。
- `shared\goods_details.gui`, `shared\goods_market_price_tooltip.gui`, `shared\trade_tooltips.gui` — 经济 UI。

### 4.5 main_menu/common/ 关键子类

| 子目录 | 用途 |
|---|---|
| `modifier_type_definitions\00_modifier_types.txt` | 全部修饰符名权威清单（**写任何 modifier 先查**） |
| `static_modifiers\` | static modifier 范例（`country.txt`, `location.txt`, `estates.txt` 等） |
| `modifier_icons\00_modifier_icons.txt` | 修饰符图标映射范例（keyed 数据库，勿重复键） |
| `script_values\` / `scripted_triggers\` / `scripted_lists\` | 主菜单域脚本范例 |

### 4.6 loading_screen/common/defines/ — 引擎 Defines

`00_defines.txt` + `graphic\`、`jomini\` 子目录（`00_tooltips.txt`, `adjacencies.txt`,
`fog_of_war.txt`, `icons.txt`, `roads.txt` 等）。所有 `Define` 数值调参看这里
（如 SOL 用的 `NPop.POP_NEEDS_INCOME_SCALE`）。

### 4.7 dlc/ — DLC 增量范例

`D000_shared\`, `D008_fate_of_the_phoenix\`, `D015_ancient_monuments_pack\`,
`D017_sacred_sites_pack\` — 展示"增量文件如何添加而不覆盖"的官方做法。

---

## 5. reference_mods/ 社区模组

按 Workshop ID 列出。价值：真实世界的复杂/兼容性范例（INJECT/REPLACE、GUI 整窗覆盖、

| ID | 模组名 | 值得借鉴的写法 |
|---|---|---|
| **3613232232** | **Prosper or Perish** | 深度经济/需求改写，static_modifier 增量、价格覆盖 |
| **3735059838** | **MEIOU and Taxes** | 超大系统模组，建筑/税收/内部经济 + 自带工具链 |
| **3692202776** | **Community Mod Framework (CMF)** | 设置注册、回调、mod 生命周期 API |
| **3601047146** | **Glorp UI** | GUI 整窗覆盖、vanilla type 提取、zoom 按钮 |
| 3736668860 | Construction Manager | UI 模组 + CM 集成 |
| 3698931463 | Standard of Living | 本库作者的 SOL（参考 `..\eu5-modding-project\src\`） |
| 3599116549 | Europa Expanded | 大规模内容扩展（事件/任务/机构） |
| 3603092142 | Historical Tweaks | 平衡/修正文件组织 |
| 3605031777 | Historic Decentralization & Control | 治理/控制机制 |
| 3629022149 | Market Stockpiles | 市场/贸易 |
| 3739393770 | Dynamic Market Stockpiles and Demand | 动态需求市场 |
| 3649381461 | Improved Trade & Buildings | 贸易/建筑平衡 |
| 3663502217 | Economic Overhaul（经济大修） | 经济平衡大改 |
| 3683328614 | War Momentum | 战争/士气机制 |
| 3686272563 | VI's TOTAL REALISM MOD | 综合平衡+UI |
| 3662193478 | Faster Universalis | 性能优化（触发简化范例） |
| 3633816300 | OGAS Optimized | 修正/优化 |
| 3605677866 | Better Road Builder | 道路 UI/地图 |
| 3674846072 | Traderoads and canals | 道路/运河机制 |
| 3606278744 | Mission Trees - Ambi | 任务树事件组 |
| 3668193813 | National Destinies | 玩法系统 |
| 3626895335 | More stable HRE | 神罗平衡 |
| 3696243603 | Autonomous Diplomats | 外交 AI |
| 3701484098 | Balance of Power | 大国平衡 |
| 3599735023 | The Idea Variation 2 | 理念扩展 |
| 3601937478 | Dense Tech Tree | UI 技术树 |
| 3610757528 | Expanded Build View | UI 建造视图 |
| 3681899116 | Unique Events Tab | UI 事件页 |
| 3599706198 / 3599957897 / 3600570317 | 汉化/翻译模组 | 本地化 YAML 范例 |
| 3698931463 | (见上) | — |

> 部分模组自带 `.cursor\rules` / `.continue\rules`（如 3606278744、3613232232），是他人给 AI 的规则文件，可参考其约定。

---

## 6. docs/ 项目文档

| 路径 | 用途 |
|---|---|
| `docs\knowledge\BRIEF.md` | **自动生成的紧凑速查**（anti-patterns + enums + 项目结构 + 脚本表）— 每次任务先读 |
| `docs\knowledge\anti_patterns.yaml` | 已知坑点机器化清单（validate.py 直接消费） |
| `docs\knowledge\valid_enums.yaml` | 已验证枚举白名单 |
| `docs\knowledge\PROJECT_OVERVIEW.md` | 项目全貌/目录结构/Script Reference 表 |
| `docs\guides\AI_Tool_Workflow_Prompt.md` | AI 工作流提示词 + 历史违规记录（踩坑学习库） |
| `docs\technical\EU5_Modding_Knowledge_Base.md` | 引擎/脚本入门知识库（背景阅读） |
| `docs\technical\EU5_Mod_Framework_Guide.md` | 社区模组模式/复杂度分级 |
| `docs\technical\EU5_Multi_Mod_Compatibility.md` | **INJECT/REPLACE/加载顺序规则**（兼容性必备） |
| `docs\technical\SOL_*` | SOL 系兼容/审计文档（作复杂工程范例） |
| `docs\design\`, `docs\wiki\`, `docs\archive\` | 设计/功能清单/历史归档 |

---

## 7. data/index/ 生成符号索引

由 `..\eu5-modding-project\scripts\gen_index.py` 生成（`gen_brief.py` 会自动调用）。
用于快速判断"某个名称是否已存在/是否冲突"：

| 文件 | 内容 |
|---|---|
| `static_modifiers.txt` | 全部 static modifier 名称（7 万+ 字节，grep 用） |
| `scripted_effects.txt` | 全部 scripted effect 名称 |
| `scripted_triggers.txt` | 全部 scripted trigger 名称 |
| `icons.txt` | 全部 `@xxx!` 内联图标名 |
| `loc_keys_en.txt` | 本地化键 |

重新生成：`$env:PYTHONUTF8='1'; & $env:EU5_PYTHON ..\eu5-modding-project\scripts\gen_index.py`

---

## 8. AI 快速速查表 Quick Cheat Sheet

### 8.1 常用搜索命令（在库根 `..\eu5-modding-project` 下执行）

```powershell
# 搜触发器/效果名是否存在于引擎文档（带行号）
rg -n "change_variable|has_global_variable" reference_official_defines/docs/data_types_script.txt

# 搜真实使用范例（限定具体目录，避免噪音）
rg -n "INJECT|REPLACE" reference_mods/3613232232/in_game
rg -n "blockoverride" reference_game_files/game/in_game/gui/shared/cards.gui

# 搜修饰符名是否合法
rg -n "local_pop_demand" reference_game_files/game/main_menu/common/modifier_type_definitions/00_modifier_types.txt

# 搜图标是否已存在（内联 @xxx! 优先）
rg -n "@wood!|@stone!" reference_game_files/game/main_menu/gui/shared/font_icons.gui

# 搜本地化键
rg -n "KEY_NAME" data/index/loc_keys_en.txt
```

### 8.2 写码前快速决策

```
要写脚本？
  ├─ 防坑清单 → 读 ..\eu5-modding-project\docs\knowledge\BRIEF.md
  ├─ 名称/语法存疑 → grep reference_official_defines\docs\data_types_script.txt
  ├─ 修饰符名 → modifier_type_definitions\00_modifier_types.txt
  ├─ 图标 → font_icons.gui（@xxx!）→ 其次 icons.gui → 最后自建
  ├─ GUI/面板 → in_game\gui\ 对应视图 + shared\*_tooltips.gui + cards.gui
  ├─ 效果/触发/数值 → scripted_effects\ / scripted_triggers\ / script_values\
  ├─ 兼容性/加载顺序 → docs\technical\EU5_Multi_Mod_Compatibility.md
  └─ 找不到范例 → 明确告知用户"无法验证"，禁止猜测
```

### 8.3 关键防坑（高频）

- 修饰符数字 ≤ **5 位小数**；变量引用用 `var:NAME`（不是 `variable:NAME`）。
- `change_variable` 用 `add =`，不用 `value =`；`set_variable` 才用 `value =`。
- `location_rank` 只有 `rural_settlement` / `town` / `city`。
- location 的 `auto_modifier` 无效 → 用 `main_menu/common/static_modifiers/`。
- 本地化 YAML 必须 **UTF-8 BOM**、仅用直引号 `"`。
- 事件块必须有 `outcome = ...`。
- 完整清单见 `docs\knowledge\BRIEF.md` 与 `docs\guides\AI_Tool_Workflow_Prompt.md`。

---

*最后更新 Last updated: 2026-08-06 · 由 opencode 生成 Generated by opencode*
