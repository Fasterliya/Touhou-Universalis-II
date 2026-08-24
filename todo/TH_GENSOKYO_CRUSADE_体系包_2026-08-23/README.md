# 幻想乡 IO 议会 + 惩戒战争体系包（2026-08-23）

> **MOD**：Touhou-Universalis-II
> **目标**：完整部署「IO 议会辩论（开会）→ 惩戒战争 → 审判 → 监管国」全链路体系
> **性质**：体系部署包（含全部配套文件，非仅修复增量）；基于 2026-08-23 多轮修复与验证的稳定版本
> **配套文档**：`docs/TH_GENSOKYO_CHAIN_交接文档_v5.1_2026-08-23.txt`（交接基线）+ `docs/复盘报告_特殊附庸_2026-08-23.md`（附庸 BUG 精华知识）

## 一、体系架构

```
【开会】提案（th_gensokyo_propose_crusade，仅阎魔/贤者）
  → select_trigger ×2（选 IO → 选目标国，好战≥50 过滤，column 必填）
  → 内联开会（set_parliament_* + call_io_parliament）
  → 规则投票（th_gensokyo_crusade_debate_start_effect：全员预投 no + 赞成组翻转 yes + 锁定）
  → 议会通过（on_debate_passed）→ leader_country 内 enable+activate 激活局势
【惩戒战争】th_gensokyo_crusade（局势）
  → on_start：阎魔 declare_war_with_cb 宣战目标
  → 成员加入（th_gensokyo_join_crusade：any_current_war 目标国 scope 定位 → 加入同一战争）
  → 罪值累积（on_battle_won / on_enforce_peace_declined 钩子）
【结算】条约（triumph 阎魔胜=价值观归 0 / counter 反杀=20 年免制裁）
  → 局势结束 → 启动审判局势
【审判】th_gensokyo_trial（4 档：赔款破产/归还/削弱/监管国）
  → 玩家手动裁决事件 / AI 按有效罪值自动判
【监管国】th_gensokyo_regulated_state（20-30 年刑期，40% 贡金）
  → country pulse 倒计时 → 刑满「脱离彼岸」事件释放
  → 阎魔保护义务（overlord_protects_external + on_war_declared 兜底）
```

## 二、文件清单（53 个，按目录结构覆盖即可）

| 子系统 | 文件 |
|---|---|
| IO 定义/席位 | `in_game/common/international_organizations/th_gensokyo_io.txt`、`international_organization_special_statuses/th_gensokyo_io.txt`、`international_organization_land_ownership_rules/th_gensokyo_land_ownership.txt`、`biases/th_gensokyo_io_biases.txt` |
| 议会 | `parliament_types/th_gensokyo_io_parliament.txt`、`parliament_issues/th_gensokyo_crusade_issue.txt`、`parliament_issues/th_gensokyo_io_parliament_issues.txt`（空壳） |
| 提案/投票 | `generic_actions/th_gensokyo_propose_crusade.txt`、`scripted_effects/th_gensokyo_crusade_effects.txt`（debate_start/judge 系列） |
| 局势 | `situations/th_gensokyo_crusade.txt`、`situations/th_gensokyo_trial.txt` |
| 战争 | `casus_belli/th_gensokyo_crusade_cb.txt`、`generic_actions/th_gensokyo_join_crusade.txt`、`generic_actions/th_gensokyo_trial_vote.txt`、`peace_treaties/th_gensokyo_crusade_triumph.txt`、`peace_treaties/th_gensokyo_crusade_counter.txt` |
| 监管国 | `subject_types/th_gensokyo_regulated_state.txt`、`prices/th_gensokyo_regulated_pays.txt` |
| 审判法 | `laws/th_gensokyo_judgment_law.txt`、`laws/th_gensokyo_io_laws.txt` |
| 事件 | `events/th_gensokyo_trial_events.txt`、`events/th_gensokyo_trial_vote_events.txt` |
| on_action | `on_action/th_gensokyo_chain_events.txt`、`th_gensokyo_chain_monthly.txt`、`th_gensokyo_chain_start.txt`、`th_gensokyo_io_monthly.txt` |
| 数值/效果 | `script_values/th_gensokyo_io_chain_values.txt`、`scripted_effects/th_gensokyo_io_effects.txt`、`th_gensokyo_io_init_setup.txt`、`th_gensokyo_io_assign_special_statuses.txt`、`th_gensokyo_notorious_effects.txt`、`scripted_triggers/th_gensokyo_io_chain_triggers.txt`、`societal_values/th_gensokyo_values.txt`、`static_modifiers/th_gensokyo_expansion_cost_modifiers.txt`（weakness/bankruptcy）、`modifier_type_definitions/th_gensokyo_societal_value_modifiers.txt`（main_menu）、`generic_action_ai_lists/th_gensokyo_io_list.txt` |
| SGUI/GUI | `scripted_guis/th_gensokyo_io_member_vars_sgui.txt`、`gui/panels/organization/th_gensokyo_io.gui`、`gui/panels/situation/th_gensokyo_crusade.gui`、`gui/panels/situation/th_gensokyo_trial.gui` |
| 本地化 | `localization/*/th_gensokyo_chain_l_*.yml`（sc/en/ru）、`localization/*/th_gensokyo_io_l_*.yml`（sc/en/ru/kr）、`main_menu/localization/*/th_io_l_*.yml`（sc/en/ru/kr） |
| 开局 | `main_menu/setup/start/th_gensokyo_io.txt` |
| 调试辅助 | `generic_actions/th_gensokyo_io_sages_diagnostic.txt` |

## 三、部署步骤

1. 解压后按目录结构**完整覆盖**到 MOD 根（`C:\Users\12494\Documents\Paradox Interactive\Europa Universalis V\mod\Touhou-Universalis-II`）；
2. 若对方副本有本地改动：以 `docs/TH_GENSOKYO_CHAIN_交接文档_v5.1_2026-08-23.txt` 第 2 章 F1-F20 清单为准手动合并（每文件有 `### 2026-08-23` 注释标记）；
3. 编码：common/events/localization = UTF-8 BOM；gui/ = 无 BOM；README = 无 BOM；
4. 游戏内需**新档**验证开局初始化（on_game_start 链路：IO 预分配/席位/价值观 100）。

## 四、验证结果（已执行）

| 门禁 | 结果 |
|---|---|
| LSP（本会话改动 19 文件） | **0 error**（warning 全为既有类别） |
| mod_lint（全 MOD 180 文件） | **0 error**（warning 全为既有债务） |
| 体系文件核对 | 53 个全部存在且复制成功 |
| 运行时实证（16:41 会话） | F15 修复生效（regulated_state 错误归零）、F8 链路无 THIRD_ENABLE 刷屏 |
| 特殊附庸 BUG | ✅ 用户实测已修复（参考 yky_shinju_guard 三件套对齐，详见 docs/复盘报告_特殊附庸） |

## 五、人工实测清单（部署后请执行）

1. **开会**：tag T25 → IO 面板 → 发起惩戒战争提案 → 选目标（好战≥50）→ 投票通过 → **局势立即启动**
2. **宣战**：`trigger situation:th_gensokyo_crusade = { situation_is_active = yes }` + `trigger c:T31 = { is_at_war_with = c:T25 }`
3. **加入同一战争**：其他成员点「加入战争」→ error.log `DBG_JOIN_IF_PASS`+`DBG_JOIN_AFTER`（无 `DBG_JOIN_ELSE`）
4. **条约**：战争结束 100 分时 triumph（阎魔胜，目标价值观归 0）/ counter（反杀，20 年免制裁）
5. **审判**：惩戒平息 → 审判局势启动 → 玩家手动 4 档 / AI 自动
6. **监管国**：档 3 → 跨月类型保持「彼岸监管国」；`effect c:T31 = { set_variable = { name = th_gensokyo_sentence_months value = 1 } }` → 过月触发「脱离彼岸」事件释放
7. **保护义务**：外部国宣监管国 → T25 自动加入防御方
8. **日志**：无 `Scoped object of type 'country' is not valid` / `THIRD_ENABLE_SITUATION_EFFECT` / `Promote COUNTRY nullptr` / `Unexpected token` 刷屏

## 六、注意事项 / 交接

- **游戏需重启**；月度相关建议新档（旧档 on_action 合并可能不生效——引擎问题）
- **DBG_JOIN_* 标记**（join_crusade.txt 3 处）为临时调试标记，全链路实测通过后删除
- **监管国须保持 IO 成员**（pulse 倒计时依赖；judge 不除名 + IO 不可脱离）
- **bias 敌意动态项**为「与目标交战者必赞成」近似（原敌意≥50 需目标 scope，bias 内不可得）
- **遗留债务**：40 文件缺 BOM、3 空壳议题、韩文 chain 缺失、law/policy 重复警告、`th_gensokyo_io_sages_diagnostic` 为调试行动
- **模板**：本体系的关键模式已沉淀为 eu5-mcp 模板（io_parliament_debate 已更新 / subject_type 已重写，重启 opencode 会话生效）

## 七、文档资产（本包 docs/）

| 文件 | 说明 |
|---|---|
| `TH_GENSOKYO_CHAIN_交接文档_v5.1_2026-08-23.txt` | 根因库 1.11-1.19 + 改动清单 F1-F20 + 测试命令 + 待办 |
| `复盘报告_特殊附庸_2026-08-23.md` | 附庸降级 BUG 精华知识（K-S1~K-S5）+ 模板落地 |
