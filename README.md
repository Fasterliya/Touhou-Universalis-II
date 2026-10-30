# 东方风云 · Touhou Universalis II

EU5（Europa Universalis V）大型东方 Project 主题 Mod。

---

## ⚠️ 协作者必读：地形缓存（terrain cache）

本仓库**不包含** `in_game/gfx/terrain2/terrain_cache/` 下的 4 个大文件。原因是它们单个就超过
GitHub 的 100 MiB 硬限制，任何包含它们的提交都会被 GitHub 拒绝推送。

| 文件 | 大小 |
|---|---|
| `heightmap.bin` | 1167.65 MB |
| `index_map.bin` | 316.02 MB |
| `materials.bin` | 223.55 MB |
| `quadtree_nodes.bin` | 64 MB |

**没有这些文件，3D 地图无法正常运行。**

### 获取方式

1. 打开本仓库的 [Releases](../../releases) 页面
2. 下载 **地形缓存 v1** 的附件 `terrain_cache.zip`（约 1.80 GB）
3. 解压到 mod 根目录下的 `in_game/gfx/`，最终路径必须是：

   ```
   in_game/gfx/terrain2/terrain_cache/heightmap.bin
   in_game/gfx/terrain2/terrain_cache/index_map.bin
   in_game/gfx/terrain2/terrain_cache/materials.bin
   in_game/gfx/terrain2/terrain_cache/quadtree_nodes.bin
   ```

### 校验（可选，强烈建议）

```powershell
Get-FileHash .\terrain_cache.zip -Algorithm SHA256
```

应得到：

```
E920BC29659ADB9DDAA3E2AC7841E66CD58EF08AF2AB5B71A6953C1EBF193597
```

### 为什么不用 Git LFS？

Git LFS 免费额度只有 1 GB 存储 + 1 GB/月流量，而 `heightmap.bin` 单个就是 1.14 GB，
一放进去就爆额度，必须付费购买数据包。Releases 附件上限为 2 GiB 且不计入仓库体积，
是免费方案里唯一装得下它的地方。

---

## 仓库结构

| 目录 | 内容 |
|---|---|
| `in_game/` | 游戏内内容：地图数据、脚本、GUI、gfx |
| `main_menu/` | 主菜单界面与插图 |
| `loading_screen/` | 加载画面 |
| `dlc/` | DLC 元数据与缩略图 |
| `psd/` | 美术源文件 |
| `tools/` | 开发与构建脚本 |
| `.metadata/` | Paradox 启动器元数据 |

> 设计与过程文档（`docs/`、`todo/`）、美术源文件、施工备份**不在版本库中**（见 `.gitignore`）。
> 这些内容只保留在本地，不会出现在 GitHub 上，也不会被打进上传包。

---

## 给维护者：上传 Steam 前的固定动作

mod 目录里同时住着**游戏内容**和**施工材料**（`.git/` 302 MB、`_release_assets/` 1.6 GB、`psd/`、`docs/`…）。
Paradox 启动器打包的是"整个 mod 目录"，直接上传会把这些一起发出去。因此上传只走白名单打包：

```powershell
$P = "F:\Paradox Interactive\Europa Universalis V\mod\_TH_施工文档\tools\pack_release.ps1"

& $P -Mode Audit      # 1) 审计源目录，退出码 0 才继续
& $P -Mode Build -Force   # 2) 生成干净上传包 → mod\_TH_upload\Touhou Universalis II
```

`Build` 末尾会自动跑一次产物复验，打印 `✔ SAFE TO UPLOAD` 才可对该目录上传。
白名单只有：`.metadata\metadata.json`、`.metadata\thumbnail.png`、`dlc\`、`in_game\`、`main_menu\`、`loading_screen\`。

> 正式上传**不要**加 `-SkipTerrainCache`，否则包内缺 1.77 GB 地形缓存，订阅者进图必崩。
> 施工文档与打包工具住在 `mod\_TH_施工文档\`（mod 目录之外），永远不在打包范围内。

---

## 给维护者：如何更新地形缓存

地形缓存被 `.gitignore` 排除。每次重新生成地图后，需要手动发布新版本：

```powershell
# 1. 打包（store 模式，不做无谓压缩——这些数据压不动）
$dir = "in_game\gfx\terrain2"
tar.exe -a -cf "_release_assets\terrain_cache.zip" --options=zip:compression=store -C $dir terrain_cache

# 2. 算校验值，写进 Release 说明
Get-FileHash "_release_assets\terrain_cache.zip" -Algorithm SHA256

# 3. 在 GitHub 上新建 Release，把 zip 拖进附件区（上限 2 GiB）
#    https://github.com/Fasterliya/Touhou-Universalis-II/releases/new
```

上传完成后请删除本地的 `_release_assets/` 目录（它已被 gitignore，但仍会占 1.8 GB 磁盘）。

**不要**试图用 `git add -A` 把 `terrain_cache` 下的 `.bin` 提交进仓库——GitHub 会拒绝整个 push。
