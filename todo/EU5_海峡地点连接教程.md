# EU5 海峡（跨水地点连接）添加教程

> 适用：Europa Universalis V（EU5 / Project Caesar）mod 开发
> 场景：让两个被水域隔开的陆地点之间可以通过海峡通行（陆军横渡 + 过海动画）
> 关联文件：`in_game\map_data\adjacencies.csv`（本 mod 已有，当前为原版副本，无 `th_*` 条目）、`in_game\map_data\locations.png`（16384×8192，取坐标用）、`in_game\map_data\default.map`（加载声明 + 可选 `sound_toll`）、`in_game\map_data\definitions.txt`（地点名）、`in_game\map_data\ports.csv`（海岸归属核对）
> 参考：EU5 官方 wiki [Map modding](https://eu5.paradoxwikis.com/Map_modding)（adjacencies 一节）；原版文件镜像 `..\eu5-modding-project\reference_game_files\game\in_game\map_data\adjacencies.csv`（184 条记录，本文范例出处）

---

## 1. 原理（一句话）

**在 `in_game\map_data\adjacencies.csv` 里追加一行 `Type = sea` 的记录，就在两个陆地地点之间生成一条双向海峡。**

- 地图加载时 `default.map` 中的 `adjacencies = "adjacencies.csv"` 指向该文件——本 mod 的 `default.map` 已配置好，**无需改动**。
- **一条记录 = 双向连通**（A→B 与 B→A 都能走），不要重复写反向行。
- 原版 184 条记录**全部**是 `Type = sea`（即都是海峡）；EU4 里常见的 `land`/`canal` 类型在 EU5 原版中未使用。

---

## 2. 格式与列含义

首行是表头，之后每行一条连接：**分号分隔、无引号、无逗号**。

```csv
From;To;Type;Through;start_x;start_y;stop_x;stop_y;Comment
messina;reggiocal;sea;strait_messina;8396;5518;8404;5519;xxx
```

| 列 | 含义 | 取值要求 |
|---|---|---|
| `From` | 连接的一端 | **陆地**地点名（见 `definitions.txt`） |
| `To` | 连接的另一端 | **陆地**地点名 |
| `Type` | 连接类型 | 海峡写 `sea`（原版唯一使用的类型） |
| `Through` | 海峡穿过的海区 | **海区**地点名；必须夹在 From/To 之间、与两岸海岸相接 |
| `start_x` / `start_y` | 线段起点像素 | 地图像素坐标（取法见 §4） |
| `stop_x` / `stop_y` | 线段终点像素 | 同上 |
| `Comment` | 备注 | 原版全部为 `xxx`；游戏不读取，可写任意标记 |

（wiki 对该文件的描述原文片段："From and To are the connected locations"，即 From/To 为被连接的两个地点，以地点标识填写。）

---

## 3. 原版范例注释

以下记录摘自参考库 `..\eu5-modding-project\reference_game_files\game\in_game\map_data\adjacencies.csv`（行号为该文件行号，本会话逐条核对）：

| 行 | 记录 | 注释 |
|---|---|---|
| 2 | `messina;reggiocal;sea;strait_messina;8396;5518;8404;5519;xxx` | 墨西拿海峡：西西里岛墨西拿 ↔ 卡拉布里亚雷焦 |
| 19 | `gallipoli;canakkale;sea;dardanelles;8892;5651;8894;5650;xxx` | 达达尼尔海峡：加里波利 ↔ 恰纳卡莱 |
| 22 | `constantinople;uskudar;sea;gulf_izmit;9012;5708;9019;5708;xxx` | 君士坦丁堡 ↔ 于斯屈达尔，穿过海区 `gulf_izmit` |
| 30 | `hormuz;bandar_khamir;sea;strait_hormuz;10229;4855;10229;4857;xxx` | 霍尔木兹海峡 |
| 34 | `johor_lama;temasek;sea;eastern_singapore_strait;12417;3429;12417;3426;xxx` | 新加坡海峡：柔佛 ↔ 淡马锡 |
| 77 | `helsingor;helsingborg;sea;oresund;8264;6698;8268;6700;xxx` | 厄勒海峡：丹麦赫尔辛格 ↔ 瑞典赫尔辛堡 |
| 125 | `nakatsu;toyoura;sea;shimonoseki_strait;13649;5265;13649;5267;xxx` | 关门海峡：本州中津 ↔ 九州丰浦 |

从原版数据可归纳的惯例：
- 线段两端点相距仅 **4–16 像素**，横跨整条海峡水面，两端分别贴近 From 侧与 To 侧海岸；
- `Through` 永远是该海峡所在的海区地点名，且该海区在 `definitions.txt` 中位于两陆地之间；
- 坐标都是整数像素，与 `locations.png` / `ports.csv` 同一坐标系。

> 注：本 mod 的 `adjacencies.csv` 是独立副本（184 行含表头），个别行坐标与参考库 1.3.x 版本略有出入——以本 mod 文件为准，范例仅用于理解格式。

---

## 4. TH 地图实操步骤

**坐标系**：地图像素坐标，原点左上角，x 向右、y 向下；本 mod 地图尺寸 **16384×8192**。
TH 区域大致范围：**x 14177–15806，y 4757–6002**（由 `ports.csv` 全部 569 条 `th_*` 港口坐标统计得出）。

1. **查地点名**：在 `in_game\map_data\definitions.txt` 确认两个陆地地点名与夹在中间的海区名（`th_*`）。要求：
   - From / To 是陆地地点；
   - Through 是海区地点，且与 From、To 的海岸都相接——用 `ports.csv` 核对：某陆地地点有指向某海区的港口（`LandProvince;SeaZone;x;y`），即说明两者海岸相接。
2. **开图取点**：用 Photoshop / GIMP / Paint.NET 打开 `in_game\map_data\locations.png`，放大到目标海峡：
   - 在海峡水面上取两个点：一个贴近 From 侧海岸、一个贴近 To 侧海岸，两点连线横跨水面；
   - **两点都必须落在 Through 海区的水域像素上**（不要点到别的海区或陆地）；
   - 记下两点坐标 (x, y)（图像编辑器状态栏会显示光标坐标）。
   - ⚠️ **y 轴翻转陷阱（2026 实测踩坑）**：若编辑器显示的光标 y 值很小（如 2000–3000）而地点实际在图中下部，说明该视图的 y 轴是**自下而上**的（与 locations.png 相反）。换算公式：**地图 y = 8192 − 编辑器 y**（本 mod 地图高度 8192）。验证方法：换算后坐标应落在该地点港口（ports.csv 的 x;y）附近；若直接用编辑器 y，坐标会偏到地图上方数千像素、落在完全错误的位置。x 轴方向通常一致、无需换算。
3. **追加行**：在 `in_game\map_data\adjacencies.csv` 末尾追加（**保留原版所有行**，本 mod 也还没有任何 `th_*` 条目）：

   ```csv
   th_location_a;th_location_b;sea;th_through_sea;start_x;start_y;stop_x;stop_y;xxx
   ```

   编码 UTF-8（与现有文件一致即可）；只加分号，不加引号/逗号。
4. **游戏内验证**（见 §5）。

> 本 mod 的 TH 海区中已有多处以 `*_strait_sea` / `*_channel_sea` 命名的地点（如 `th_fog_channel_stratts_sea`、`th_dragon_scale_strait_sea`、`th_purification_strait_sea`、`th_river_of_forgetfulness_strait_sea`、`th_lost_light_strait_sea`），设计上就是给海峡当 `Through` 用的，优先选用。

---

## 5. 游戏内验证

EU5 的地图数据在**启动时**加载，改完必须重启游戏（运行中热改不生效）。

- **观察**：海峡处出现过海连接动画/图标；选中陆军后能沿海峡横渡（无需海军）。
- **日志**：`文档\Paradox Interactive\Europa Universalis V\logs\error.log`（主日志文件）——地点名拼错、地点不存在会在这里报错，按日志中的行号定位。
- **缓存**：`in_game\map_data\nodes.dat` 是地图拓扑缓存，正常情况下由游戏自动重建；若出现"旧连接仍在 / 新连接不生效"的异常，可删除该文件后重启让游戏重新生成。

---

## 6. 常见错误与排查

| 现象 | 可能原因 | 排查 |
|---|---|---|
| 启动报错 / error.log 提到地点名 | From/To/Through 拼错或不存在于 `definitions.txt` | 与 definitions.txt 逐字核对（注意 mod 内既有拼写如 `th_norh_bank_of_misty_lake`、`th_fog_channel_stratts_sea`） |
| 海峡不显示 / 不能走 | Through 海区与 From/To 不相接 | 用 `ports.csv` 核对海区归属；确认线段两点落在 Through 水域内 |
| 过海动画位置不对 | 线段坐标不在海峡水面 | 重取坐标：两点贴近两岸、都落在 Through 海区 |
| **海峡能走（功能生效）但无过海贴图**（本 mod 2026 实测） | start/stop 坐标不在 Through 海区水域内（本 mod 曾写入镜像坐标，点落在太平洋深处，连接逻辑照常生效但引擎无法绘制跨海图形） | 把线段两点移到 Through 海区水域内；本 mod 坐标换算：**地图 y = 8192 − 编辑器 y**（见 §4 翻转陷阱） |
| 改了没效果 | 没重启 / nodes.dat 缓存 | 重启游戏；必要时删 nodes.dat |

> ⚠️ **ports.csv 不可全信（2026 实测，作者已确认文件本身有误）**：ports.csv 的 `SeaZone` 列与实际地图常有出入（本 mod 155 个 TH 海区中大量港口的锚点像素并不落在其声明海区内，甚至 5 个海区共用同一色块），且**无港口的海区**（如 `th_waning_corner_sea` 亏月海）没有色块样本。作者用第三方程序读取也确认了 ports.csv 存在错误。判定线段所在海区时，应以**地图作者确认 + 游戏实测**为准，ports.csv 仅作参考。

> ⚠️ **事实标注**：`Type=sea` 机制、列含义、坐标与线段惯例均以**原版文件**为准（参考库 adjacencies.csv 184 条记录 + default.map，本会话逐条核对）。wiki 页面因网络原因仅能引用搜索片段（"From and To are the connected locations"），未能全文核对。"坐标必须落在 Through 水域"、"From/To 必须与 Through 海岸相接"等为原版数据惯例 + 社区共识，**以游戏实际行为为准**——每加一条就进游戏验证一次最稳妥。

---

## 7. 参考资料

- EU5 官方 wiki：[Map modding](https://eu5.paradoxwikis.com/Map_modding)（adjacencies / 地图文件一节）
- 原版文件镜像：`..\eu5-modding-project\reference_game_files\game\in_game\map_data\adjacencies.csv`（184 条 sea 记录，本文全部范例出处）
- 本 mod 现状：`in_game\map_data\adjacencies.csv` 为原版副本（无 `th_*` 条目）；`default.map` 已声明 `adjacencies = "adjacencies.csv"`
- 可选联动：`in_game\map_data\default.map` 的 `sound_toll` 块可给特定海峡加通行税（原版例：`oresund = helsingor`、`gulf_izmit = constantinople`、`strait_hormuz = hormuz`），非必需
- 社区工具：[Eu5_LocationDefinitionTool](https://github.com/JammingEnd/Eu5_LocationDefinitionTool)（地图绘制 / 地点定义辅助工具，绘制 `locations.png` 与核对颜色时可用）
