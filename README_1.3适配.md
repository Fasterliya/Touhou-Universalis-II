# Touhou-Universalis-II — 1.3 适配分支（1.3-adaptation）

> 本分支基于 main（1.2.3 原版），包含 **1.3.11 引擎适配的全部修改** + **崩溃排查文档**。
> 目的：展示适配过程、问题定位与当前状态，供审阅。

---

## 快速导航

| 内容 | 位置 |
|------|------|
| 📋 **崩溃排查报告**（先读这个）| [docs/1.3-adaptation/崩溃排查报告.md](docs/1.3-adaptation/崩溃排查报告.md) |
| 📦 **崩溃日志包**（含 error/ai/game/debug 日志 + exception）| [docs/1.3-adaptation/东方风云1.3适配_崩溃日志包.zip](docs/1.3-adaptation/东方风云1.3适配_崩溃日志包.zip) |
| 📝 **交接文档**（当前状态 + 未决问题 + 下一步）| [docs/1.3-adaptation/_handoff_东方风云1.3适配_2.md](docs/1.3-adaptation/_handoff_东方风云1.3适配_2.md) |

---

## 本分支包含的 1.3 适配修改

### 已修复（4 类根因）
1. **1.2 defines 与 1.3 不兼容** → 删除 1.2 拷贝 `loading_screen/common/defines/00_defines.txt`，新建最小覆盖集 `th_defines.txt`（保留 MOD 自定义值，如 `MAX_CHARACTER_AGE = 1000000`）
2. **setup 模板引用其他 MOD 的 key** → `main_menu/setup/templates/th_gensokyo_monarchy.txt`：`dop_favor_the_ruler_miku_ver` → `dop_favor_the_ruler`
3. **TH 国家段缩进深 1 级**（核心根因）→ `main_menu/setup/start/10_countries.txt`：T00-T94 从 2 tab 修正为 1 tab（与 base 1.3 国家同级），95 国恢复正确初始化
4. **TH 国家数据错误** → 领地冲突 ×3 去重、T51/T52 重复 include 删除、T93 首都归属修正

### 其他适配
- 事件格式改为 namespace 式（`th_culture_chronicle_events.txt`）、静默事件规范（hidden/empty_text）
- `thgfx.0001` → `thgfx.1`（前导零）
- `description_category = economic` → `administrative`（41 处）
- create_character 语法修正（estate/birth_location/ethnicity）
- institution_birth 静态修饰符
- setup 编号文件更新为 base 1.3 版 + TH 数据拆分（th_markets.txt 等）
- 文化图鉴 113 个动态 trigger 改块形式（wiki 记录的坑）

### ⚠️ 未解决
- **AI 无效命令 → buffer 崩溃**（TH 国家初始化成功后仍闪退）
  - 症状：`ai.log` 大量 `AI tried to execute invalid command`（change_trade_capacity ×40 等）→ `Tried to reallocate a pre-allocated buffer` → ACCESS_VIOLATION
  - 候选方向：TH 市场 AI 操作 / 2D Portrait 基因缺失 / TH 文化人口不匹配
  - 详见交接文档

---

## 环境

- 游戏版本：1.3.11
- playset「测试」= 本 MOD + 2D Portrait Framework（workshop 3599699279）
- 源码基于 main 分支（1.2.3 原版）适配

---

## 目录说明

- `in_game/` / `loading_screen/` / `main_menu/`：MOD 正文（1.3 适配版）
- `.metadata/`：MOD 元数据
- `docs/1.3-adaptation/`：本次适配的全部文档与日志
- 未包含：`psd/`（设计源文件）、`todo/`（未完成内容）
