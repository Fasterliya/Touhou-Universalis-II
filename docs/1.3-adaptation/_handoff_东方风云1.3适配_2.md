# 交接文档：东方风云 MOD 1.3 适配（第二轮）

> 生成时间：2026-08-02 | 上一份交接：`_handoff_东方风云1.3适配.md`
> 本轮目标：定位"走时间闪退"根因。已完成 6 项根因修复，**残余 1 个未解决问题（AI 无效命令 buffer 崩溃）**

---

## 1. 当前状态（重要）

### 1.1 MOD 文件
| 位置 | 状态 |
|------|------|
| `C:\Users\12494\Documents\Paradox Interactive\Europa Universalis V\mod\Touhou-Universalis-II\` | **当前工作版**（含全部本轮修复，TH 国家 1 tab 缩进）|
| `...\mod\_Touhou_adapted_1.3_test\` | 早期适配版备份（缩进修复前）|
| `...\mod\Touhou-Universalis-II\main_menu\setup\start\10_countries.txt.pre_indent_fix` | **缩进修复前**的 10_countries.txt（含 2tab 错误缩进的 TH 段）|
| `...\mod\_backup_Touhou_1.2copies\` | 1.2 原版关键文件备份（defines/goods/setup）|
| `I:\工作站\Touhou-Universalis-II\` | GitHub 克隆（1.2.3 原版，git 干净）|

### 1.2 关键环境
- 游戏 1.3.11；playset"测试" = 本地版 + 3599699279（2D Portrait）
- **2D Portrait 立绘依赖，测试时不要移除**（移除会破坏角色立绘，但崩溃与它无关——用户已确认"只启用 2D 不崩、只启用 TH 崩"）

### 1.3 崩溃现状
- **仍会闪退**（走时间后数秒，AI 无效命令刷屏 → buffer 崩溃）
- TH 国家**已正确初始化**（capital/government/继承制全部有效）——缩进修复生效
- 残余问题：**AI 无效命令**（change_trade_capacity ×40 / diplomaticactioncommand / perform_generic_action / production_methods）

---

## 2. 本轮已确认的根因与修复（共 6 项）

| # | 根因 | 修复文件 | 修复内容 |
|---|------|---------|---------|
| 1 | 1.2 defines 与 1.3 不兼容（除零崩溃）| `loading_screen/common/defines/th_defines.txt` | 删 1.2 拷贝，建 44 值覆盖集 |
| 2 | 模板引用萌陆风云 key | `main_menu/setup/templates/th_gensokyo_monarchy.txt:65` | `dop_favor_the_ruler_miku_ver` → `dop_favor_the_ruler` |
| 3 | **TH 段缩进深 1 级**（核心）| `main_menu/setup/start/10_countries.txt` | TH 段（T00-T94）tab 减 1：2tab→1tab（与 base 同级）|
| 4 | 领地冲突 ×3 | 同上 | T08/T09、T25/T40、T81/T82 地块去重 |
| 5 | T51/T52 重复 include | 同上 | 删除重复的 `include = "th_gensokyo_monarchy"` |
| 6 | T93 首都是他国地块 | 同上 | `th_synthesizer_avenue`（属 T03）→ `th_crossroads_teahouse` |

**缩进修复的来历**（重要认知，勿再改回）：
- 1.2 原版 TH 段用**空格**（国家 6 空格、字段 9 空格），与 1.2 base 段一致 → 1.2 正常
- 1.3 base 用 **tab**（国家 1 tab、字段 2 tab），**国家与内层 countries 同级**
- 早期合并用 `spaces/3`（6→2）→ TH 段 2 tab → 引擎不识别 → 95 国全废
- 修复后 1 tab，95 国全部正常初始化

---

## 3. 未解决问题：AI 无效命令 → buffer 崩溃

### 3.1 现象
```
ai.log: 76 条 [AI Warning] AI tried to execute invalid command
  change_trade_capacity: 40 | diplomaticactioncommand: 21 | perform_generic_action: 12 | production_methods: 2
error.log: [pdx_assert] Tried to reallocate a pre-allocated buffer
exception: C0000005 ACCESS_VIOLATION @ 0x00007FF6C2657DF0（每次相同）
```

### 3.2 已排除的候选（不要再重复测试）
- ❌ MERCHANT defines（800/0.5）
- ❌ MAX_CHARACTER_AGE（1000000）
- ❌ situation 文化图鉴 on_start
- ❌ culture chronicle 113 个动态 trigger（已改块形式，wiki 记录的坑，保留修复）
- ❌ NAI 区块 18 个值
- ❌ TH 市场本身（禁用后延迟到 4 分钟，AI 建市场后崩 → 市场是"加速器"）
- ❌ TH 国家初始化（缩进修复后已正常）

### 3.3 下一步候选方向（按优先级）
1. **TH 市场（17 个）的 AI 贸易操作**——禁用 th_markets.txt 后崩溃从 5 秒延迟到 4 分钟，强相关。重点检查：AI 对 TH 市场做 change_trade_capacity 时，市场所在 TH 国家的数据（法律/特权/人口）是否有 AI 依赖的异常
2. **2D Portrait 基因缺失（110 个）**——error.log 大量 `could not find attribute`（2D Portrait 基因文件与 base 1.3 属性不匹配）。TH 角色立绘生成失败可能连锁 AI。可尝试：临时移除 2D Portrait 的 `95_genes_no_portrait.txt` 或核对 `02/03_genes_accessories` 与 base `01_genes_morph.txt` 的属性名
3. **TH 文化/人口不匹配**（T02/T06/T10 无主流文化人口）——次要

### 3.4 推荐调试方法（skill 标准流程）
1. 在 `on_game_start` 效果边界加 `error_log = "DBG_XXX ..."`（**纯 ASCII，禁 `[]`**）
2. 复现崩溃 → 对齐 error.log 的 DBG 标记与 ai.log 命令时间戳
3. 收敛调用链，定位 AI 无效命令来源
4. 删除全部 DBG 标记，`rg "DBG_"` 确认无残留
5. 每轮只加少量节点，按调用链向内收敛

---

## 4. 日志与调试路径

- 日志：`C:\Users\12494\Documents\Paradox Interactive\Europa Universalis V\logs\`（error/ai/game/debug）
- 崩溃：`...\crashes\Europa Universalis V<时间戳>\exception.txt`（栈符号不可靠）
- **debug.log 被游戏进程独占**：读需 `FileShare.ReadWrite`，或等游戏退出
- 本轮日志副本：`I:\工作站\MOD开发\欧陆风云5_EU5\东方风云适配文档\日志备份\`
- 工具：`eu5_mod_lint`、`eu5_lsp_diagnose_file(s)`（MCP 直连）

### 调试循环
改文件 → LSP 0 error → 用户建局测试 → 看 error.log/ai.log/game.log → 再改

---

## 5. 用户操作习惯（重要）

- **迭代式调试**：先跑原版看报错再动手，每次只改一处
- **先确认再执行**：改动前说明计划，用户点头才动手
- **关注日志**：用户会自己看日志（"你不用再向我申请log了，自己看"）
- **保留自定义数值**：MAX_CHARACTER_AGE=1000000、MERCHANT 800/0.5 等是用户想要的，**不要还原**
- 用户会提供关键观察（如"AI 自己建造了市场以后崩溃"）——重视这些线索
- 问"这个值有啥用"时，要解释清楚再动它

---

## 6. 参考文档

- 本轮报告：`I:\工作站\MOD开发\欧陆风云5_EU5\东方风云适配文档\崩溃排查报告.md`
- 维基代码库：`I:\工作站\MOD开发\欧陆风云5_EU5\维基代码库\`
  - `维基参考_Setup_modding开局设定.md`（§12 发展度、编号文件铁律）
  - `维基参考_Country_modding国家系统.md`（国家字段、include 规则）
  - `维基参考_error_log脚本追踪调试.md`（DBG 标记规范）
  - `维基参考_Culture_modding文化系统.md`（§11.3 culture_percentage_in_country 坑）
- skill：`/eu5-mod`（必加载）、`/diagnose`（复杂排错）

---

## 7. 历史崩溃时间线（2026-08-02）

| 时间 | 崩溃 | 原因 | 状态 |
|------|------|------|------|
| 15:06 | INT_DIVIDE_BY_ZERO | 1.2 defines 除零 | ✅ 已修 |
| 15:38~16:07 | ACCESS_VIOLATION buffer | AI 无效命令（有市场 5 秒崩）| ⚠️ 未决 |
| 15:50~16:38 | ACCESS_VIOLATION buffer | AI 无效命令（无市场 4 分钟崩）| ⚠️ 未决 |
| 16:20 | INT_DIVIDE_BY_ZERO | 1.2 原版复测确认 | ✅ 已修 |
| 16:53 | ACCESS_VIOLATION buffer | miku_ver 修复后仍崩 | ⚠️ 未决 |
| 17:00 | ACCESS_VIOLATION buffer | NAI 清空测试 | ⚠️ 未决 |
| 17:29 | ACCESS_VIOLATION buffer | 缩进修复后（TH 国家已正常）| ⚠️ **下一步从这里继续** |
