# 东方风云 Touhou-Universalis-II

《欧陆风云 V》（Europa Universalis V / EU5，1.3 版）东方 Project 主题大型 MOD。

幻想乡的 95 个国家（T00-T94）组成幻想乡国际组织（th_gensokyo_io），以阎魔（T25 彼岸）为领袖、三贤者（T05/T13/T83）共治、人类村落二十席为自由市。本仓库当前主推分支为 **`gensokyo-chain-2026-08-14`**（幻想乡 IO 链条系统全量落地 + 四轮修复版）。

---

## 一、幻想乡 IO 链条系统（TH_Gensokyo_Chain）现状

| 模块 | 核心机制 | 状态 |
|---|---|---|
| ① 恶名链 | 非法扩张+8 / 合法+1 / 吞自由市×6 → 0-100 隐藏 → 月度-1 / 宴会-10 → 弃民档（50/75） | ✅ 已落地，经四轮修复 |
| ② 惩戒战争+审判 | 提案（恶名≥50 驱动）→ 贤者议会 2/3 票 → 双局势 → 罪值三源 → 3 级判决 → 监管国 40% 贡金 | ✅ 已落地，主链修复后待回归 |
| ③ 扩张限制 | 配额 4 + 惩罚链 + 代价修正（授权×0.25 / 异变×1.25 / 私自×1.5） | ✅ 已落地 |
| ④ 自由市保护 | 割让/吞并惩罚（敌意1250/恶名×6/团结-10）+ 三贤者自动参战（神罗式） | ✅ 已落地 |
| ⑤ 团结度 | 月度收入（基础0.1+和平0.2+成员×0.002）+ 判决扣/审判奖 | ✅ 已落地 |

**规模**：新增 30 文件（27 txt + 1 gui + 2 yml）+ 5 处骨架侵入 + 2 删除项，覆盖 biases / script_values / scripted_triggers / scripted_effects / on_action / generic_actions / parliament_issues / situations / subject_types / laws / casus_belli / peace_treaties / prices / static_modifiers / events / gui / localization。

**质量门禁**：LSP 全 0 error；mod_lint 仅 2 error（均为骨架遗留：thgfx 事件 ID + 贤者 SGUI bare key）；全文件编码合规（common/ UTF-8 BOM、GUI/start 无 BOM）。

### 修复历程（2026-08-13 → 08-14，四轮）

1. **第一轮（审查驱动）**：17 项 P1 修复——主链断点（at_war/end_situation/trigger_event/反杀时序）、效果失效（财富转移 scope/释放国家待实测/乘除效果名/代价修正字段/on_battle_won root）、显示缺陷（兵力 scope/GUI 卡片/按钮 potential）、防呆（刷贡献/scope:overlord/悬空引用）
2. **第二轮（实测三发实弹）**：add_antagonism 方向修正（实测=target 对 root）；提案入口改**恶名≥50 驱动**（用户决策）；自由市保护修复（scope:actor 显式化 + join 参数收敛）
3. **日志排查**：提案选国绑定（name 内置模板化）；审判法 laws 键值对格式登记；regions/裸键席位无效语法停用
4. **第三/四轮**：interaction_source_list 不吃 var 比较 → modifier mirror 方案（恶名档位落修正标记）；点宴会报 empty → 变量开局初始化 + 防御守卫双保险

### 已知待办

- ⏳ 人工回归（检测手册回归项 0、25-55）
- ⏳ 交接文档修订 v4.1（14 项文档偏差）
- ⏳ 知识沉淀闭环（eu5-rules 新规则 / 维基错误签名库补记）
- ⏳ 数值平衡（全部初值"待调"）
- ⏳ 骨架风险交接（文化编年史裸 var: 100+、空壳议题、17 文件缺 BOM 等）

---

## 二、仓库结构

```
Touhou-Universalis-II/          ← MOD 根（可直接放入 EU5 mod 目录）
├── .metadata/                  ← metadata.json + 封面图
├── in_game/                    ← 主内容（common/ events/ gui/ gfx/ map_data/ localization/ …）
├── main_menu/                  ← setup/start 开局定义、localization、gfx
├── loading_screen/
├── psd/                        ← 源图素材
└── todo/                       ← 交接文档与过程文档
    ├── TH_GENSOKYO_CHAIN_现状报告_2026-08-14.md   ← 当前状态总览（推荐入口）
    ├── TH_GENSOKYO_CHAIN_审查报告_2026-08-13.md   ← 问题全录 + 四轮修复记录
    ├── TH_GENSOKYO_CHAIN_控制台检测手册.txt        ← 游戏内回归执行指南
    ├── TH_GENSOKYO_CHAIN_交接文档_v4.0_FINAL.txt  ← 系统规格（v4.0）
    └── …（历史版本）
```

## 三、分支说明

| 分支 | 内容 |
|---|---|
| `main` | 早期骨架状态（保留不动） |
| `io` / `io-full` | 历史 IO 工作分支（保留不动） |
| **`gensokyo-chain-2026-08-14`** | **当前推荐：链条系统全量落地 + 四轮修复 + 全部交接文档** |

## 四、安装与使用

1. 将本仓库内容放至 EU5 MOD 目录：
   `C:\Users\<用户>\Documents\Paradox Interactive\Europa Universalis V\mod\Touhou-Universalis-II\`
2. 在游戏启动器 playset（`playsets.json`）中挂载本 MOD（开发环境 playset 名"测试"，含 2D Portrait Framework 辅助 MOD；链条系统本身无 CMF 依赖）
3. 启动参数加 `-debug_mode` 便于测试（回归步骤见 `todo/` 检测手册）

## 五、测试与回归

游戏内回归按 `todo/TH_GENSOKYO_CHAIN_控制台检测手册.txt` 执行：0 章基建 → 0.8-0.9.2 前置验证（敌意方向/恶名提案资格/席位分配/审判法加载）→ 十二·补/三 回归清单（项 0、25-55）。

## 六、技术栈备注

- EU5 1.3 引擎；链条系统为纯脚本实现（common/ + gui/ + localization/），无 .NET 代码
- 开发参考：EU5 官方 readme + base game 可执行用法 + 维基代码库（本机 I:\工作站\MOD开发\欧陆风云5_EU5\维基代码库）
