# EU5 Touhou Universalis II — 报错分析报告（2026-09-04 21:34 场次）

> 日志来源：`F:\Paradox Interactive\Europa Universalis V\logs\error.log`（21:31:13–21:34:19，4643 行）
> 分析基准：1.3.11 / playset「优化」= workshop 3599699279 + Touhou Universalis II（最高优先级）

---

## 1. 总览结论

- **本次会话没有崩溃**：`crashes/` 无当日记录；debug.log 正常写至 21:34:38（干净退出）。
- error.log 中 **约 95% 行来自 4 个刷屏源**：

| 刷屏源 | 行数 | 占比 | 时间 |
|---|---|---|---|
| 道路样条 strip 缺失（jomini_spline_network_graphics_old） | 1248 | 27% | 21:33:34（1 秒内爆量） |
| Could not find flag recipient（interaction_target） | 1151 | 25% | 21:34:00–19（退出前持续） |
| unknown area for discoveries（country.cpp:6277） | 634 | 14% | 21:31:21–22（启动一次性） |
| 文化图鉴 chronicle 贴图 + GUI（texture/validation） | ~430 | 9% | 21:31:13–16（启动） |

其余为启动期一次性脚本/DB 校验、localization、配色冲突等噪音。

---

## 2. A 组｜贴图 / GUI / 配色 —— 可立即修、风险低

### 2.1 chronicle 贴图 106×2 行报错（图鉴立绘不显示）
- **报错**：`gfx_texture_loader.cpp:470 … Expected more data in the texture mipmaps…` + `pdx_gui_texture.cpp:61 Missing file … for texture property`
- **根因（已用 DDS 头解析证实）**：
  - `main_menu/gfx/interface/illustrations/situation/chronicle/` 下 111 个 `*_culture.dds` 长度 **86524B 且 111 个内容完全相同**（同一张占位图，MD5 一致）。
  - 其 DDS 头**非标准**：mip 数 = 0、caps 不含 COMPLEX/MIPMAP、像素格式字段偏移异常、数据区比 120×180×32bit 期望值少 4 字节 → 引擎判定文件截断。
  - 对照：`unknown.dds / th_maid_fairy_culture.dds / th_vampire_culture.dds / chronicle_bg.dds`（115228B 等）为标准头 + 完整 mip 链（mip=8, caps=0x401008），引擎正常加载、无报错。
- **修复**：按 `unknown.dds` 的结构（标准 128B 头 + 120×180 BGRA32 + 7 级降采样 mip 链）重编码占位图，回写全部 111 个文件；未来导入正式立绘时统一用同一导出规范（见 §6 wiki 要点）。

### 2.2 chronicle GUI 百分比 size（113 行）
- `in_game/gui/panels/situation/th_gensokyo_culture_chronicle.gui`
- 每行文化卡片外框 `size = { 100% 192 }`（113 处，行 84/145/206/…）—— 引擎明确禁止：*"Unsupported property: size with a percentage on widgets that are a child of a vbox/hbox. Consider using layout policies and stretch factors instead."*
- **修复**：113 处统一 `size = { 100% 192 }` → `size = { -1 192 }`（每行已有 `layoutpolicy_horizontal = expanding`，宽度交给布局策略）。

### 2.3 sages IO 面板非法属性（22 行）
- `in_game/gui/panels/organization/th_sages_council_io.gui` 行 113/120/121/122/123/125/218/248/260
- `margins_top` / `margins_bottom` —— **EU5 GUI 全库无此属性**（原版 0 处）；合法写法是子控件上的 `margin = { x y }`（如 vanilla `area.gui` 中 `margin = { 10 0 }`）。
- `divider_horizontal_bg = {}` —— 不是合法属性。EU5 分隔线做法：`type divider_xxx = icon { using = bg_divider_xxx }`（参考 vanilla `advances_lateralview.gui`），或直接用块级 `widget` + 背景贴图。
- **修复**：删除/改写上述行的三类写法；分隔线若保留则改用 EU5 分隔线类型。

### 2.4 attribute_columns 语法（约 8 行）
- `gui/attribute_columns/th_gensokyo.gui:11-12` 顶层直接写 `type th_country_flag = widget {`。
- 原版格式为 **`types XxxColumns { type … = … { … } }` 包裹块**（对照 vanilla `attribute_columns/country.gui` 的 `types CountryColumns`）。
- **修复**：整文件用 `types … { … }` 包住全部 `type` 定义（DB 侧 `common/attribute_columns/zz_th_gensokyo.txt` 的 `widget = th_country_flag` 引用保持不变）。

### 2.5 同色冲突（5 处）
| 冲突 | 文件 |
|---|---|
| 国家 T72(月之都·绵月丰姬) = T52(心绮楼·秦心) `rgb{227 112 225}` | `in_game/setup/countries/th_gensokyo_countries.txt`（T72 行 713、T52 行 533） |
| 国家 T89 = TSM | 同上 |
| language th_gensokyo_language = south_italian_language | `common/languages` |
| religion th_gensokyo_lunar_religion = th_gensokyo_tenma_mount | `common/religions` |
| culture th_yama_culture = th_goblin_culture | `common/cultures` |

修复：各改其中一方的 `color = rgb { … }`。

### 2.6 Button missing tooltip（3+ 处）
- `th_gensokyo_culture_chronicle.gui:32/47/7161`、`th_sages_council_io.gui:184`：给 button 补 tooltip 或 `tooltip_enabled = no`。

---

## 3. B 组｜脚本 / 数据库缺失（位置明确，照原版补）

| # | 报错 | 位置 | 修复 |
|---|---|---|---|
| 3.1 | missing static modifier `th_heavenly_artifact_institution_birth` / `th_kagura_and_matsuri_institution_birth` / `th_all_things_as_one_institution_birth`（×15） | 5 个自建 institution（`common/institution/th_gensokyo_institutions.txt`），引擎惯例要求 `<inst>_birth`；`main_menu/common/static_modifiers/th_institutions.txt` 只定义了 2 个 | 补 3 个 static modifier（照已有 2 个的结构） |
| 3.2 | `modifier_type` must exist in DB（×14）+ assert | IO special status 自动引用 `…_can_participate_in_parliament` / `…_agenda_impact`（yama/guardian 等） | 在 modifier_type_definitions 补这些 type |
| 3.3 | `price_database` missing `<price>_cost_modifier`（×4） | 新增 4 个 price：`th_gensokyo_feast_price` / `subject_pays_regulated` / `th_hakurei_change_statue_price` / `th_hakurei_change_minor_aspect_price`（`common/prices/th_*.txt`） | 补 4 条 `<key>_cost_modifier` 定义（仿 vanilla `00_modifier_types.txt` 的 `embrace_institution_cost_modifier`） |
| 3.4 | Else/else_if not following if（×2） | `common/scripted_effects/th_gensokyo_expansion_effects.txt:64,73` | 修脚本结构（缺 if / 括号错位） |
| 3.5 | No on_action with tag … cannot link（×8） | `th_gensokyo_sin_refusal_check` 等 8 个 tag 被引用无定义 | 补 on_action 定义或改引用 |
| 3.6 | Failed to find message type `PERFORM_…_ACTION`（×14） | 4 个行动：danmaku_challenge / subjugate_beast / counter_expansion / crusade_declare。官方 readme：行动自动消息名 `PERFORM_<Key>_ACTION` / `WE_PERFORM_…` / `OTHER_PERFORMS_…` | 与行动 select_trigger/price/可交互目标注册一起检查（见 §4.2） |
| 3.7 | `culture_group:acgv_touhou_group` 找不到（×4） | `common/customizable_localization/th_gensokyo_country_ranks.txt:3143/3150/3158/3165` | ACGV 不在 playset 但内容被挂载 → 确认 ACGV 启用状态；否则改用已存在的文化组或删除该 4 个文本块 |
| 3.8 | custom_tooltip PostValidate false（×3+） | `generic_actions/th_gensokyo_io_sages_diagnostic.txt:41`、`international_organizations/th_gensokyo_io.txt:139`、`wargoals/th_gensokyo_crusade_war_goal.txt` | custom_tooltip 引用的 loc key 不存在 → 补 loc |
| 3.9 | 议会 / IO 相关 | parliament issue 无 special_status（resolution_1/2/3 空壳；trial_issue 无）；IO 缺 `io_opinion_*`（/biases/）；law_to_policy 报 `th_gensokyo_judgment_law/barrier_law` 无效/重复 | 空壳议题删除或补全；trial 补 `special_status`（参照 sages 议题）；补 biases、law 条目 |
| 3.10 | Variable set but never used（×7） | 图鉴 scripted GUI 变量 `th_cc_row_*_adopted` | 删除或加用法 |
| 3.11 | 缺 localization | **144 个独立 th_ key** 无文本 + 一批 `"TODO : Write a desc"` 空文本（IO 名称/描述、diplomatic_status、war_goal、opinion、policy、MODIFIER_TYPE_NAME/DESC、LEAD_/AM_ 等） | 在 `localization/` 补全 |

---

## 4. C 组｜需要设计决策

### 4.1 unknown area for discoveries：inner/south_baltic_sea_area（×634，启动一次）
- 根因链：
  1. mod **自带整套地图**（`in_game/map_data/definitions.txt` 13.8k 行），其中**没有** `inner_baltic_sea_area` / `south_baltic_sea_area` 两个原版海域 area 键（mod 0 处 vs vanilla 2 处）。
  2. 原版探索模板仍发放这两个 area：`main_menu/setup/templates/expl_eastern_europe.txt`、`expl_christian_caucasus.txt`、`expl_mediterranean.txt`、`expl_mongols.txt`、`expl_muslim_mediterranean.txt`。
  3. 每个受影响国家启动校验报一次「unknown area for discoveries」。
- 修复三选一：
  - (a) 地图里按原版恢复这两个 area 键（与地图实际海域归属一致为前提）；
  - (b) 在 mod 中 override 这 5 个模板文件，删除/改写这两个键（若波罗的海海域已重组，这是正解）；
  - (c) 忽略（纯日志、无功能影响，可加入 `eu5-modding-project/vanilla_error_filters.txt` 过滤）。

### 4.2 Could not find flag recipient（×1151，退出前 19 秒高密度）
- 25 个 th 行动/宣战文件使用 `target_flag = recipient / target` 的两段式选择（IO → 成员），如 `th_danmaku_challenge.txt`（select_trigger 1: IO=recipient；select_trigger 2: country=target, source=recipient）。
- 刷屏 = 行动在未选定 recipient 状态下被反复求值（AI 月度 tick / 玩家打开行动面板时）。
- 修复方向：
  - 给行动补 `potential / allow` 前置（`exists = scope:recipient` 或存在候选人才允许求值）；
  - 或改为单步选择；
  - 排查手段：逐个禁用 25 个行动二分定位是哪个在刷。
- 备注：vanilla `change_autocephalous_patriarchate` 同为「两步选择」但结构完整（每个 select_trigger 带独立 visible/enabled 守卫），可作为对照范本。

### 4.3 道路样条 / 定位点（1248 + ~3 行）
- `jomini_spline_network_graphics_old.cpp:1428`：都柏林–纳斯等爱尔兰锚点对间缺 type-0 道路条 → 自建地图的样条/锚点数据与省份/邻接不一致。
- `game_object_locators.cpp:1307`：引擎建议游戏内执行 `MapObjects.GenerateGameLocator dock` 重新生成港口定位点；城市定位点提示 incomplete。
- 9-1 生成过一批（`in_game/gfx/map/map_objects/` 有备份），地图再改动后需用工具链重跑（`tools/update_locators.ps1`、nodes/ports/邻接重生成）。

### 4.4 启动初始化校验组（量大、多为静态 start 快照与原版/引擎漂移）
- 现象：无统治者 164、随机统治者 18、invalid policy/reform/privilege 移除 ~90（含 `th_hundred_youkai_banquet` for T00）、accepted/tolerated 文化超限或重复（T04/T14/T28/T46/T50/T79 等）、建筑超等级（trakai 酿酒坊 level 2/max 1）、"Culture has no pops"×15、关系超上限、`th_zealot_village` 无效 location（`setup/start/th_town_setup.txt:372`）。
- 背景：mod **整包替换** `main_menu/setup/start/10_countries.txt`（1.7MB）、`07_cities_and_buildings.txt`、`08_institutions.txt`、`th_pops.txt`（13MB）等静态文件；副本与 1.3.11 数据存在漂移。
- 处理：逐条对照原版同日期写法修正；体量大，建议单独开一轮专项。

---

## 5. 验证流程

每改一批 → 重开一局（约 1 分钟可进）→ 检查 error.log：
- 启动期应只剩 C 组校验项；
- 重点确认图鉴页立绘显示、sages/IO 面板正常、无每秒刷屏；
- 用 `eu5-modding-project/error_log_filter.py`（其 `vanilla_error_filters.txt` 已收录大量原版噪音）辅助区分。

---

## 6. Wiki / 官方依据与待补要点

- 本报告对照了官方引擎数据本身（优先级高于第三方 wiki）：
  - `generic_actions/readme.txt`（消息命名：`PERFORM_<Key>_ACTION` 等）
  - `prices/readme.txt`
  - 原版 `attribute_columns/*.gui`（`types … {}` 格式）
  - 原版 GUI 全库（确认不存在 `margins_top/bottom` 属性）
  - `main_menu/common/modifier_type_definitions`（modifier type 写法）
  - `main_menu/setup/templates/expl_*.txt`（探索发放源）
- 外部 wiki（eu5.paradoxwikis.com 等）的 GUI/DDS/脚本专项调研已并行完成，结论要点将追加到本文档末尾（DDS 导出推荐设置、GUI 布局策略官方措辞等）。
