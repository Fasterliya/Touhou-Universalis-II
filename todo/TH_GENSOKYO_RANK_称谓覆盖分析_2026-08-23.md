# 原版国家称谓被覆盖问题 — country_flavor REPLACE 分析（2026-08-23）

> 现象：mod 加入幻想乡等级后缀（领域/国度）后，原版贝伊国、苏丹国、汗国、
> 沙皇国、共和国、神权国等特殊称谓全部变成普通「王国/公国」。
> 状态：**方案 B 已实施（2026-08-23）**，待游戏内实测求值顺序。

---

## 一、机制背景（EU5 国家称谓渲染链）

国家显示名 = 国名 + 等级称谓。称谓由
`in_game/common/customizable_localization/country_ranks.txt` 的顶层对象
**`country_flavor`**（2741 行）提供：对象内是 200+ 个 `text` 块，
每个块 = `localization_key` + `trigger`；**自上而下求值，取第一个
trigger 命中的块**，最后以无条件兜底块（`rank_kingdom` 等，trigger 仅
`country_rank_is_kingdom = yes`）收尾（`fallback = yes` 同理）。

原版特判块示例（本次受影响）：
- 苏丹国：`rank_kingdom_muslim` / `rank_empire_muslim`（穆斯林政府）
- 贝伊国：`rank_duchy_muslim` / `rank_duchy_turkish` 系列
- 汗国：`rank_*_horde`；沙皇国：`rank_empire_tsar`
- 共和国/神权/殖民地/自由市/日本大名/汉萨/条顿等 200+ 块
- 无条件兜底位置：rank_empire@625 / rank_kingdom@1252 / rank_duchy@2006 / rank_county@2553

## 二、根因

`in_game/common/customizable_localization/th_gensokyo_country_ranks.txt`
（698 行）使用了：

```
REPLACE:country_flavor = { ... }
```

按 EU5 数据库操作关键字语义（eu5-modding-project
`docs/technical/EU5_Multi_Mod_Compatibility.md` 权威记载）：

| 关键字 | 语义 |
|---|---|
| `REPLACE:` | **用新定义整体替换现有对象**（原版对象全部丢弃） |
| `INJECT:` | 在现有对象**末尾追加脚本**（不深合并；对 scripted effect/trigger 等同替换） |
| `TRY_*` / `*_OR_CREATE` | 上述语义 + 不存在时跳过/创建 |

→ `REPLACE:country_flavor` 把原版 2741 行对象**整体替换**为 mod 的 698 行版本，
mod 版只含：幻想乡势力特判（has_reform × 20+ 组）→ IO 成员特判
（`rank_*_gensokyo`）→ 通用兜底（rank_empire/kingdom/duchy/county）。
**原版 200+ 特判块全部丢失** → 非幻想乡国家只能命中 mod 版末尾的通用兜底
→ 贝伊国/苏丹国等全部显示为普通王国/公国。与用户观察完全一致。

## 三、为什么不直接改成 INJECT

`INJECT:country_flavor` 会把幻想乡块追加到对象**末尾**——即原版全部块
（含无条件兜底 rank_kingdom@1252）**之后**。按「自上而下第一个命中」求值，
原版无条件兜底会先拦截所有王国级国家 → **幻想乡国家的"国度/领域"也会失效**。
（该求值顺序由 mod 现状佐证：mod REPLACE 版内特判在前、兜底在后且幻想乡侧显示正常；
但跨文件/操作类型的块排序是否为同一规则，**唯一确定方法 = 实测**。）

## 四、mod 内同类写法排查（其余均为安全用法）

| 位置 | 写法 | 判定 |
|---|---|---|
| `customizable_localization/th_gensokyo_country_ranks.txt` | `REPLACE:country_flavor` | ❌ **本次根因**（丢原版 200+ 块） |
| `societal_values/th_gensokyo_values.txt` | `REPLACE:belligerent_vs_conciliatory` | ✅ 安全：完整复制原版字段 + 仅改 allow（注释已声明"非成员行为与 vanilla 完全一致"） |
| `laws/th_gensokyo_laws.txt`（5 处） | `INJECT:feudal_de_jure_law` 等 | ✅ 安全：追加的是**新 law key**（th_old_charter 等新字段），不与原版既有字段冲突 |
| `scripted_triggers/01_acgv_2d_portrait_triggers.txt` | `REPLACE_OR_CREATE:th_portrait_trigger` | ✅ 安全：目标为 mod 自有对象 |

## 五、受影响范围与连带

- 受影响：所有非幻想乡国家的等级称谓（苏丹国/贝伊国/汗国/沙皇/共和/神权/
  殖民地/自由市/日本大名/汉萨 等 200+ 特判）→ 全部退化为 王国/公国/帝国/伯国。
- 未受影响：`country_flavor_heir/regent/courtier/consort`（原版其他 4 个对象，
  mod 未覆盖）；幻想乡国家自身称谓（mod REPLACE 版内正常）。
- 与本次 IO 链条体系包（惩戒战争/审判/监管国）无交互，属独立历史遗留。

## 六、修复方案（待拍板，未实施）

### 方案 A：REPLACE 完整版（行为最可控，推荐兜底）
以原版 `country_ranks.txt` 为基底**完整复制**（5 个对象或至少 country_flavor 全文），
在 4 个通用兜底块**之前**插入现有幻想乡特判块（60+ 块整体迁移），
保留原版全部特判块。
- 优点：顺序完全可控；幻想乡侧显示不变、原版侧完整恢复
- 缺点：文件 ~2900 行；原版后续版本更新称谓时需手动同步（文件头注释记录基线版本）

### 方案 B：INJECT 追加 + 实测求值顺序（✅ 已实施 2026-08-23）
把 `REPLACE:country_flavor` 改为 `INJECT:country_flavor`（并删除 mod 自带兜底块，
避免与原版兜底重复冗余），实测幻想乡国家称谓是否仍显示「国度/领域」。
- 若引擎对 customizable localization 是**后定义优先** → 方案 B 即最优解
  （原版块全保留、幻想乡块优先，仅 1 行改动）
- 若实测幻想乡称谓失效（先定义先命中）→ 回退，实施方案 A
- 改动极小、可快速回退，建议先做
- **已实施内容**：`th_gensokyo_country_ranks.txt` 头部 REPLACE: → INJECT:；
  删除文件尾部 4 个通用兜底块（rank_empire/kingdom/duchy/county，INJECT 后
  排原版兜底之后永不命中）；文件头注释记录回退指引；BOM 已校验。

### 方案 C：称谓改由 government_reform 承载（不动 country_flavor）
若 government_reform 支持覆盖 rank 称谓（需查官方类型定义），势力特判可迁移；
但 IO 成员兜底（rank_*_gensokyo）仍无落点，无法完全脱离 country_flavor。不推荐单独使用。

## 七、验证清单（修复后）

1. 开局任意非幻想乡国家（奥斯曼贝伊/马穆鲁克苏丹/莫斯科公国）→ 称谓应为
   原版特判（贝伊/苏丹/大公 等），不再是「王国/公国」
2. 幻想乡国家（T25 彼岸 / 博丽 / 守矢）→ 称谓仍为 阎魔帝君/神社/领域 系列
3. 幻想乡 IO 成员兜底：非特判势力（普通成员）→ 国度/领域/境界 按 rank 正确显示
4. error.log 无 `localization_key` 相关报错；game.log 称谓解析正常
