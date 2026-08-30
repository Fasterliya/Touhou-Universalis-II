# EU5 GUI 名词悬停 tooltip 教程（文化图鉴适用）

> 适用：Europa Universalis V（EU5 / Project Caesar）mod 开发
> 场景：给界面上的名词 / 图标加"鼠标悬浮显示介绍"（本地化子条目）
> 关联文件：`in_game\gui\panels\situation\th_gensokyo_culture_chronicle.gui`、`main_menu\localization\*\th_culture_chronicle_desc_l_*.yml`

---

## 1. 原理（一句话）

**本地化 yml 里加一个条目（key），GUI 控件上挂 `tooltip = "KEY"` 属性，鼠标悬浮即显示该条目文本。**

- `tooltip` 是 EU5 GUI 的通用 widget 属性：`icon`、`text_single`、`button_regular`、`widget` 等都能挂。
- 属性值有两种写法：
  - **写死 loc key**：`tooltip = "TH_CC_HINT_TH_VAMPIRE"`（最常用，静态）
  - **表达式**：`tooltip = "[Culture.GetName]"`（动态求值，返回字符串）

原版先例（可在游戏目录自查）：
| 文件 | 写法 |
|---|---|
| `main_menu\gui\shared\icons.gui` 第 11/21 行 | 性别图标 `tooltip = "GENDER_MALE_TOOLTIP"` ← 图标悬停名词介绍的标准样板 |
| `main_menu\gui\mod_tools.gui` 第 365 行 | `tooltip = "MOD_CREATE_MOD_STUB_TOOLTIP"` |
| `in_game\gui\ai_settings_menu.gui` 第 77 行 | `tooltip = "AI_SETTINGS_TOOLTIP"` |
| `in_game\gui\panels\situation\reformation.gui` 第 401 行 | `tooltip = "[ReformationPieSliceItem.GetReligion.GetName]"`（表达式） |
| `in_game\gui\panels\situation\black_death.gui` 第 81 行 | `tooltip = "[...GetDeathsTooltip()]"`（函数返回） |

---

## 2. 基础三步（静态写法）

### 第 1 步：本地化加子条目

在任意 loc yml 里加一行（本模组惯例放 `main_menu\localization\<语言>\` 下）：

```yaml
l_simp_chinese:
 th_cc_hint_th_vampire_culture:0 "吸血鬼文化：源自雾之湖对岸红魔馆的夜行血族。\n$BULLET$昼伏夜出，畏惧阳光\n$BULLET$由斯卡雷特一族统率"
```

要点：
- 文件头 `l_simp_chinese:`（中文）/ `l_english:`（英文）/ `l_japanese:` / `l_korean:` / `l_russian:`，**UTF-8 带 BOM 编码**（与现有 yml 一致）
- 每行 = `key:0 "文本"`，行首一个空格缩进
- `\n` 换行；`$BULLET$` 等 `$XXX$` 是 loc 内建变量，tooltip 里同样生效
- **多语言**：只写中文+英文即可，其他语言缺 key 时自动回退英文；要完整就 5 个 yml 都加

### 第 2 步：GUI 控件挂属性

```clausewitz
icon = {
	size = { 120 180 }
	texture = "gfx/interface/illustrations/situation/chronicle/th_vampire_culture.dds"
	tooltip = "th_cc_hint_th_vampire_culture"   # ← 新增这一行
	visible = "..."
}
```

### 第 3 步：重启游戏验证

EU5 的 GUI 与纹理在启动时加载，**改完必须重启游戏**（运行中热改不生效）。

---

## 3. 文化图鉴实例（本模组落地）

### 3.1 直接复用已有描述条目（零新增 loc）

模组已有 `th_cc_desc_th_vampire_culture` 等 **113 个描述子条目**（5 语言齐全，位于 `th_culture_chronicle_desc_l_*.yml`）——内容本身就是"这个名词是什么"的介绍。**悬停立绘直接引用它即可**：

```clausewitz
icon = {
	size = { 120 180 }
	texture = "gfx/interface/illustrations/situation/chronicle/th_vampire_culture.dds"
	tooltip = "th_cc_desc_th_vampire_culture"      # ← 复用描述条目
	visible = "[EqualTo_CFixedPoint(GetPlayer.MakeScope.GetVariable('th_cc_row_5_adopted').GetValue, '(CFixedPoint)1')]"
}
icon = {
	size = { 120 180 }
	texture = "gfx/interface/illustrations/situation/chronicle/unknown.dds"
	tooltip = "th_cc_desc_unknown"                 # ← 占位版也有对应条目
	visible = "[EqualTo_CFixedPoint(GetPlayer.MakeScope.GetVariable('th_cc_row_5_adopted').GetValue, '(CFixedPoint)0')]"
}
```

批量：每行两个 icon 各加一行 `tooltip = "th_cc_desc_th_<文化>"` / `tooltip = "th_cc_desc_unknown"`，113 行 × 2 处，脚本可批量。

### 3.2 给"文化名"挂 tooltip 的注意点

文化名当前是 `text = "[GetCultureByKey('th_vampire_culture').GetName]"`——**GetName 生成的文本自带游戏内导航 tooltip**（悬停已有文化信息）。此时再给该 text_single 挂 `tooltip = "..."` 可能互相覆盖（引擎行为未验证）。**推荐做法：自定义介绍挂立绘 icon（3.1），文化名保留原生导航**，两者互不冲突。

### 3.3 想要独立"名词解释"（比描述更短）

新增独立条目（如 `th_cc_hint_th_vampire_culture`），在 3.1 的 icon 上引用新 key，文案由内容组提供。

---

## 4. 进阶写法

### 4.1 表达式 tooltip（动态取条目）

```clausewitz
tooltip = "[GetCultureByKey('th_vampire_culture').Custom('th_cc_desc')]"
```

- `GetCultureByKey('key')` 取文化 scope（引擎 GUI 函数）
- `.Custom('th_cc_desc')` 按可定制本地化返回对应条目（`in_game\common\customizable_localization\th_culture_chronicle.txt`）
- 动态场景（如列表项）用表达式；静态行直接写 loc key 更简单

### 4.2 样式化 tooltip（标题 + 正文 + 图标）

用 `tooltipwidget` 子元素（原版样板：`in_game\gui\ui_library.gui` 第 12810-12845 行）：

```clausewitz
icon = {
	texture = "..."
	tooltipwidget = {
		ContextualTooltipType = {
			blockoverride "tooltip_title" {
				ConceptTooltipHeader = {
					blockoverride "title_text" { text = "TH_CC_HINT_TITLE_TH_VAMPIRE" }
				}
			}
			blockoverride "tooltip_content" {
				TooltipTextBlock = {
					blockoverride "text" { text = "th_cc_hint_th_vampire_culture" }
				}
			}
		}
	}
}
```

（datacontext 缺失时部分块需 blockoverride 置空，参照 ui_library 样板注释）

### 4.3 文本内联概念链接（`[概念key|E]`）

在 `raw_text` / `text` 里写 `[unit_type|E]`、`[situation|E]` 这类**概念链接**，悬停词条本身即显示概念介绍：

```clausewitz
raw_text = "[th_vampire_culture|E] 是幻想乡的夜行种族"
```

- 概念定义：`main_menu\common\game_concepts\00_game_concepts.txt`（自带概念），自定义概念需在此注册 + 对应 loc
- 适用：正文里嵌名词解释（百科式）；单纯"悬停图标出介绍"用 2 节方案更轻

---

## 5. FAQ

| 问题 | 答案 |
|---|---|
| 改了 loc 不生效？ | 重启游戏；确认 yml 为 UTF-8 带 BOM、`l_xxx:` 头正确、行首一个空格 |
| key 缺失时显示什么？ | 显示 key 字符串本身（如 `th_cc_hint_th_vampire_culture`）——看到裸 key = loc 没加载 |
| 其他语言没加条目？ | 自动回退英文；英文也缺才显示裸 key |
| tooltip 与 GetName 导航冲突？ | GetName 文本自带链接 tooltip；再挂 widget tooltip 可能覆盖——实测确认，推荐挂图标 |
| `$BULLET$`、`$COUNTRY$` 是什么？ | loc 内建/参数变量，tooltip 内可用；自定义参数需在表达式上下文传入 |
| 运行中热替换 dds/gui/loc？ | 全部需要重启游戏 |
| 一个控件能挂多个 tooltip 吗？ | 一个 `tooltip` 属性；复杂内容用 `tooltipwidget` |
