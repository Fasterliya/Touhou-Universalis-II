# Touhou Universalis II — 校验基准报告

> 生成日期: 2026-08-09（M0 修复完成时归档）
> 校验工具: `tools/th_validate.py`（复用 `..\eu5-modding-project\scripts\validate.py` 的
> anti-patterns / valid_enums / modifier 白名单检查，外加 TH 侧审计）
> 运行方式: `.\tools\run_validate.ps1`（全量）· `--changed`（git 变更）· `--ai-report`（JSON）

## 1. 工具链要点

- **PyYAML**：以 wheel 直装到 `tools/pylibs/`（本机无 `eu5` conda 环境、pip 的临时目录机制被
  沙箱拦截，故绕开 pip 直接解包 wheel；网络走国内镜像源）。
- **validate.py 适配**：包装器 monkeypatch `validate.REPO_ROOT = TH_ROOT` 使 `relative_to`
  对 TH 文件生效；`check_loc_coverage`（SOL 专属）被 TH 版 5 语言对齐审计取代。
- **性能坑（已修复）**：库的 `check_anti_patterns` 对每个匹配执行 `content[:m.start()].count('\n')`
  计算行号，在含 30 万个 6 位小数坐标的 `gfx/map/map_objects/*_locators_*.txt` 上是 O(n²)，
  全量校验 >300s 超时。包装器改为：① 数据目录（`map_data/`、`gfx/map/map_objects/`、
  `main_menu/setup/start/`）只做解码检查；② 脚本文件用预计算换行偏移 + bisect 的快速行号。
  现在全量校验 1.4s。
- **BOM 惯例（已核实 vanilla）**：脚本 `.txt`/`.yml` → UTF-8 BOM；`setup/start/` 与生成数据
  （map_objects/map_data）→ 无 BOM；`.gui`/`.csv` → 无 BOM。
- **审计正则修复**：`^\s+` → `^\s*`（文化/地图 yml 存在大量列 0 键，旧正则漏计导致误报
  "英文缺 2089 地图 key"——经 definitions.txt/location_templates 交叉验证，5 语言地图
  本地化实际全部对齐 2721 key）。

## 2. 基准问题（修复前 599 项）→ 修复后（0 项）

| 类别 | 修复前 | 处理 |
|------|--------|------|
| LOCALIZATION 弯引号 | 362 | 全部替换为直引号（en 地图 356、zh 地图 4、ko 文化 2） |
| LOC key 对齐/重复/空值 | 218 | 见 §3 |
| ENCODING BOM | 14 | 8 个脚本文件补 BOM（4 个生成数据文件按惯例不补） |
| RESIDUAL 残留文件 | 3 | 删除 test.txt + 2 个 fix_*.py |
| PRECISION 6 位小数 | 1 | `loading_screen/.../00_defines.txt` 为 vanilla 原值，加豁免不误报 |
| MODIFIER 未知名 | 1 | `trade_efficiency` → `trade_land_efficiency`+`trade_sea_efficiency`（1.3 官方名） |

## 3. 本地化修复明细

1. **in_game 日文本地化**：新建 `in_game/localization/japanese/th_gensokyo_io_l_japanese.yml`
   （109 key，与英文一一对齐）。
2. **韩文补 key**：`th_culture_l_korean.yml` 加 `th_gensokyo_religion_group`。
3. **分隔符 bug**：ja/zh `th_culture_l_*.yml` 的 `th_gensokyo_religion_group; "..."` → `:`。
4. **空 desc**：`th_country_l_*.yml` 5 语言 × 36 条（34 文化 + 2 特质）全部补实。
5. **重复 key**：`th_lunar_language`（en/ja/zh，保留语言名、删语族重复）、
   `name_th_akizuki/wakaba/shizuku/shirayuki/tsukimori/suzushiro`（en/ja/zh/ru）、
   `th_vampire_culture`（en/ja/zh/ru）、`th_sages_introduce_institution_notification`
   （in_game zh）。
6. **main_menu th_io 补 24 key**：`TH_SAGES_REQ_*`×6、恶名四档 auto_modifier×8、
   `STATIC_MODIFIER_*_th_sages_tier_*`×10，补齐 en/zh/ko/ru（ja 原已有）。
7. **机构去重**：`main_menu/setup/start/08_institutions.txt` 中 2204 个空 `th_*` 占位块删除
   （TH 机构配置唯一来源 = `th_institution.txt`，2026 地点全量配置）。

## 4. 遗留事项（非 M0 范围，记录备查）

- 地图 2205 个 th_ 地点中 179 个（tpl 有、`th_institution.txt` 无）未分配机构——
  TH genesis 机构开局不在其首都，靠传播覆盖；如需开局即全有，后续补 `th_institution.txt`。
- ko/ru 文化文件含 634 行 EU4 风格 `key:0 "value"` 写法（引擎可容忍，未改动）。
- 工具脚本 `tools/*.py` 保留作为可复现资产（fetch_pyyaml / th_validate / 各修复脚本）。
