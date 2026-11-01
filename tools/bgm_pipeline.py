#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bgm_pipeline.py — 东方风云 II 的 BGM 全链路脚本（mp3 → Wwise 库 → EU5 mod）。

命名约定：工程/段/事件/bank 一律 th_ 前缀，不沿用模板作者的 acgv_ 前缀。

六个子命令：
  doctor    环境自检（ffmpeg / WwiseConsole / 原版音效库目录 / mod 目录）
  convert   tools/music_src 里的 mp3/flac/m4a/ogg → 44.1kHz 16bit 立体声 WAV
  add       把 WAV 克隆进 Wwise 工程（克隆 th_ 模板段：MusicSegment + Event + bank 登记）
  build     用 WwiseConsole verify + generate-soundbank 生成 sb_music_media_touhou
  install   把 .bnk / Media/*.wem 投放进 mod，并把本库合并进 SoundbanksInfo.json
  data      生成 mod 侧数据：曲目库 / 播放器分类 / 本地化（按 manifest 幂等重建）
  all       convert → add → build → install → data

依赖：Python 3.9+ 标准库；ffmpeg（自动找 imageio_ffmpeg 自带的，再找 PATH）；
      Wwise 2025.1.12 Authoring（生成 .bnk 必需，SchemaVersion 133）。

来源说明：克隆模板段的 XML 逻辑改写自道武帝的 ACGV_Music_Wwise 模板包 tools/ai_add_songs.py（本工程已整套改成 th_ 命名），
        本脚本加了 mp3 转换、bank 生成、SoundbanksInfo 合并、mod 投放与数据生成。
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import shutil
import subprocess
import sys
import uuid
import wave

# ─────────────────────────── 配置 ───────────────────────────
TOOLS = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(TOOLS)

PROJECT_DIR = os.path.join(TOOLS, "wwise2", "TH_MUSIC")       # Wwise 官方 create-new-project 生成的工程（模板工程的工作单元是坏的）
SOURCE_DIR = os.path.join(TOOLS, "music_src")                # 放 mp3/flac 源
WAV_DIR = os.path.join(TOOLS, "music_wav")                   # 转换后的 wav
META_PATH = os.path.join(TOOLS, "music_meta.json")           # 曲名/作者（可手改）
MANIFEST = os.path.join(PROJECT_DIR, "song_manifest.json")   # add 写的清单

BANK = "sb_music_media_th"                     # 自己的音效库名（不要动原版库）
PROJECT_FILE = "TH_MUSIC.wproj"               # Wwise 工程文件名
SEG_PREFIX = "th_"                            # Wwise 段名前缀（mod 统一 th_）
EVENT_BASE = "MusicPlayer_th_t"                # 事件名基串，后接两位序号
CATEGORY_ID = "th_music_category_touhou"       # 播放器分类 id（同时当 loc key）
VANILLA_CATEGORY_ID = "th_music_category_vanilla"

BANK_DEST = os.path.join(MOD, "loading_screen", "sound", "banks", "windows")
TRACKS_FILE = os.path.join(MOD, "in_game", "common", "music_player_tracks", "th_music_tracks.txt")
CATEGORY_FILE = os.path.join(MOD, "main_menu", "music", "music_player_categories", "th_music_categories.txt")
LOC_DIR_SCH = os.path.join(MOD, "main_menu", "localization", "simp_chinese")
LOC_DIR_ENG = os.path.join(MOD, "main_menu", "localization", "english")

TEMPLATE_SEGMENT = "th_Song_Template"
TEMPLATE_EVENT = "MusicPlayer_th_TEMPLATE"

# 工程里必须原样保留的 ID（总线 / 转换设置 / 工作单元）
MUSIC_BUS_ID = "{3C7A1E52-9B41-4E77-8F1D-2A4C6E8B0D13}"
BUS_WU_ID = "{1994BBAA-9376-4BCA-A075-B3AFC73D46CB}"
VORBIS_ID = "{53A9DE0F-3F4F-4B59-8614-3F9E3C7358FC}"
CONV_WU_ID = "{F6B2880C-85E5-47FA-A126-645B5DFD9ACC}"
CONTAINERS_WU_ID = "{8D686ADF-6AA5-41E3-8873-D77C9A16801F}"
EVENTS_WU_ID = "{646223E3-4F7C-4C75-947D-8FDC2D9CE485}"
PRESERVE = {MUSIC_BUS_ID, BUS_WU_ID, VORBIS_ID, CONV_WU_ID, CONTAINERS_WU_ID, EVENTS_WU_ID}

GUID_RE = re.compile(r"\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
                     r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}")

VANILLA_BANK_CANDIDATES = [
    r"F:\SteamLibrary\steamapps\common\Europa Universalis V\game\loading_screen\sound\banks\windows",
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game\loading_screen\sound\banks\windows",
    r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game\loading_screen\sound\banks\windows",
]


def say(msg=""):
    print(msg)


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    raise SystemExit(code)


# ─────────────────────── 通用小工具 ───────────────────────
def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def write_text(path, text, bom=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="\n") as f:
        f.write(text)


def sanitize(stem):
    """Wwise 对象名合法化：去掉点/引号/斜杠，& → and；保留中日文。"""
    s = stem.replace("&", " and ")
    s = re.sub(r"[^0-9A-Za-z\u3040-\u30ff\u3400-\u9fff]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "song"


def wav_ms(path):
    with wave.open(path, "rb") as w:
        if w.getsampwidth() != 2:
            die("%s: 只支持 16-bit PCM WAV（先跑 convert）" % path)
        return int(round(w.getnframes() * 1000.0 / w.getframerate()))


def find_ffmpeg():
    env = os.environ.get("FFMPEG")
    if env and os.path.isfile(env):
        return env
    try:                       # imageio-ffmpeg 自带的静态版
        import imageio_ffmpeg
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if p and os.path.isfile(p):
            return p
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    return p if p else None


def find_wwise():
    env = os.environ.get("WWISE_CONSOLE")
    if env and os.path.isfile(env):
        return env
    # 官方安装器：...\Wwise 2025.1.x.xxxx\Authoring\win-x64\Release\bin\
    # 网盘/绿色包：...\Wwise_2025.1.x.xxxx\Authoring\x64\Release\bin\
    roots = [
        r"C:\Program Files (x86)\Audiokinetic", r"C:\Program Files\Audiokinetic",
        r"D:\Program Files\Audiokinetic", r"D:\Program Files (x86)\Audiokinetic",
        r"E:\Program Files\Audiokinetic", r"F:\Program Files\Audiokinetic",
        r"D:\Audiokinetic", r"E:\Audiokinetic", r"F:\Audiokinetic",
        r"E:\BaiduNetdiskDownload", r"D:\BaiduNetdiskDownload", r"F:\BaiduNetdiskDownload",
        r"C:\Audiokinetic", "D:" + os.sep, "E:" + os.sep, "F:" + os.sep,
    ]
    pats = []
    for r in roots:
        for arch in ("win-x64", "x64"):
            pats.append(os.path.join(r, "Wwise *", "Authoring", arch, "Release", "bin", "WwiseConsole.exe"))
            pats.append(os.path.join(r, "Wwise_*", "Authoring", arch, "Release", "bin", "WwiseConsole.exe"))
    hits = []
    for p in pats:
        hits += glob.glob(p)
    return sorted(hits)[-1] if hits else None


def find_vanilla_banks():
    env = os.environ.get("EU5_GAME_DIR")
    cands = list(VANILLA_BANK_CANDIDATES)
    if env:
        cands.insert(0, os.path.join(env, "game", "loading_screen", "sound", "banks", "windows"))
    for c in cands:
        if os.path.isfile(os.path.join(c, "SoundbanksInfo.json")):
            return c
    return None


def find_vanilla_tracks():
    """原版 common/music_player_tracks/00_music_player_tracks.txt（用来镜像『游戏自带』页签）。"""
    env = os.environ.get("EU5_GAME_DIR")
    roots = [env] if env else []
    for c in VANILLA_BANK_CANDIDATES:
        roots.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(c)))))
    for r in roots:
        p = os.path.join(r, "in_game", "common", "music_player_tracks", "00_music_player_tracks.txt")
        if os.path.isfile(p):
            return p
    return None


def bkhd_version(path):
    """读 Wwise bank 头的版本号（BKHD 里的第一个 uint32）。"""
    try:
        with open(path, "rb") as f:
            head = f.read(12)
        if head[:4] != b"BKHD":
            return None
        return int.from_bytes(head[8:12], "little")
    except Exception:
        return None


def vanilla_bank_version():
    vb = find_vanilla_banks()
    if not vb:
        return None
    return bkhd_version(os.path.join(vb, "Init.bnk"))


def load_manifest():
    if not os.path.isfile(MANIFEST):
        return {"tracks": []}
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def load_meta():
    if os.path.isfile(META_PATH):
        with open(META_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"tracks": {}}


def save_meta(meta):
    write_text(META_PATH, json.dumps(meta, ensure_ascii=False, indent=2), bom=False)


# ─────────────────────── 0) doctor ───────────────────────
def cmd_doctor(_a):
    say("== 环境自检 ==")
    ff = find_ffmpeg()
    say("ffmpeg        : " + (ff or "缺失（convert 会失败）"))
    ww = find_wwise()
    say("WwiseConsole  : " + (ww or "缺失（build 会失败，见文末安装说明）"))
    vb = find_vanilla_banks()
    say("原版音效库目录: " + (vb or "未找到（可用 EU5_GAME_DIR 指定游戏根目录）"))
    vv = vanilla_bank_version()
    if vv:
        gen = ""
        pi = os.path.join(os.path.dirname(vb), "ProjectInfo.json")
        if os.path.isfile(pi):
            try:
                with open(pi, encoding="utf-8-sig") as f:
                    gen = json.load(f)["ProjectInfo"]["Project"].get("Generator", "")
            except Exception:
                pass
        say("原版 bank 版本: %d（0x%04X）%s" % (vv, vv, ("  生成器 Wwise " + gen) if gen else ""))
        say("              → build 会用同代 Wwise（2025.1.x）生成，版本须一致，否则引擎报 result: 15")
    say("mod 根        : " + MOD)
    say("Wwise 工程    : " + ("OK" if os.path.isfile(os.path.join(PROJECT_DIR, PROJECT_FILE)) else "缺失 " + PROJECT_DIR))
    gen = os.path.join(PROJECT_DIR, "GeneratedSoundBanks", "Windows", BANK + ".bnk")
    say("已生成音效库  : " + ("OK " + gen if os.path.isfile(gen) else "尚未生成"))
    if os.path.isfile(gen):
        bv = bkhd_version(gen)
        say("              生成库 bank 版本 %s" % (bv if bv else "读不到"))
    say("mod 内已装库  : " + ("OK" if os.path.isdir(BANK_DEST) and glob.glob(os.path.join(BANK_DEST, "*.bnk")) else "尚未投放"))
    return 0


# ─────────────────────── 1) convert ───────────────────────
def cmd_convert(a):
    ff = find_ffmpeg()
    if not ff:
        die("找不到 ffmpeg。装一个（winget install Gyan.FFmpeg）或设环境变量 FFMPEG=<路径>")
    os.makedirs(WAV_DIR, exist_ok=True)
    srcs = []
    for ext in ("*.mp3", "*.flac", "*.m4a", "*.ogg", "*.wav"):
        srcs += glob.glob(os.path.join(a.src or SOURCE_DIR, ext))
    if not srcs:
        die("源目录没有音频文件：%s" % (a.src or SOURCE_DIR))
    for src in sorted(srcs):
        stem = os.path.splitext(os.path.basename(src))[0]
        out = os.path.join(WAV_DIR, sanitize(stem) + ".wav")
        cmd = [ff, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
               "-vn", "-ar", "44100", "-ac", "2", "-sample_fmt", "s16",
               "-c:a", "pcm_s16le", out]
        say("转换 %s → %s" % (os.path.basename(src), os.path.basename(out)))
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            die("ffmpeg 失败：%s\n%s" % (src, r.stderr.strip()[:800]))
        say("   时长 %.2f 秒" % (wav_ms(out) / 1000.0))
    say("\n完成。下一步：python tools\\bgm_pipeline.py add")
    return 0


# ───────────────────── 2) add（进 Wwise 工程） ─────────────────────
class Ids:
    def __init__(self, texts):
        blob = "\n".join(texts)
        self.guids = set(GUID_RE.findall(blob))
        self.shorts = {int(x) for x in re.findall(r'ShortID="(\d+)"', blob)}
        self.media_ids = {int(x) for x in re.findall(r'<MediaID ID="(\d+)"', blob)}

    def guid(self):
        while True:
            g = "{%s}" % str(uuid.uuid4()).upper()
            if g not in self.guids:
                self.guids.add(g)
                return g

    def short(self):
        while True:
            v = random.randint(100_000_000, 2_100_000_000)
            if v not in self.shorts:
                self.shorts.add(v)
                return v

    def media(self):
        while True:
            v = random.randint(1_000_000, 4_000_000_000)
            if v not in self.media_ids:
                self.media_ids.add(v)
                return v


def remap_ids(block, ids):
    mapping = {g: ids.guid() for g in GUID_RE.findall(block) if g not in PRESERVE}
    block = GUID_RE.sub(lambda m: mapping.get(m.group(0), m.group(0)), block)
    return re.sub(r'ShortID="\d+"', lambda _m: 'ShortID="%d"' % ids.short(), block)


def cut(text, start, end):
    i = text.index(start)
    j = text.index(end, i) + len(end)
    return text[i:j]


def cmd_add(a):
    proj = os.path.abspath(a.project or PROJECT_DIR)
    if not os.path.isfile(os.path.join(proj, PROJECT_FILE)):
        die("找不到 Wwise 工程：%s" % proj)
    containers = os.path.join(proj, "Containers", "Default Work Unit.wwu")
    events = os.path.join(proj, "Events", "Default Work Unit.wwu")
    banks = os.path.join(proj, "SoundBanks", "Default Work Unit.wwu")
    originals = os.path.join(proj, "Originals", "SFX")
    for p in (containers, events, banks):
        if not os.path.exists(p):
            die("缺少工作单元：%s" % p)

    c_txt, e_txt, b_txt = read_text(containers), read_text(events), read_text(banks)
    for name, txt, marker in (("Containers", c_txt, "<!--SONGS-->"),
                              ("Events", e_txt, "<!--EVENTS-->"),
                              ("SoundBanks", b_txt, "<!--BANKREFS-->")):
        if marker not in txt:
            die("%s 工作单元里没有 %s 占位标记" % (name, marker))
    # 库名对齐
    b_txt = re.sub(r'<SoundBank Name="[^"]+"', '<SoundBank Name="%s"' % BANK, b_txt, count=1)

    seg_tpl = cut(c_txt, '<MusicSegment Name="%s"' % TEMPLATE_SEGMENT, "</MusicSegment>")
    evt_tpl = cut(e_txt, '<Event Name="%s"' % TEMPLATE_EVENT, "</Event>")

    audio_dir = a.audio or WAV_DIR
    wavs = sorted(f for f in os.listdir(audio_dir) if f.lower().endswith(".wav")) \
        if os.path.isdir(audio_dir) else []
    if not wavs:
        die("没有 WAV：%s（先跑 convert）" % audio_dir)

    ids = Ids([c_txt, e_txt, b_txt])
    existing_events = set(re.findall(r'<Event Name="([^"]+)"', e_txt))
    used_segments = set(re.findall(r'<MusicSegment Name="([^"]+)"', c_txt))
    used_files = set(os.listdir(originals)) if os.path.isdir(originals) else set()

    nums = [int(n) for n in re.findall(re.escape(EVENT_BASE) + r"(\d+)", e_txt)]
    index = a.start if a.start else (max(nums) + 1 if nums else 1)

    os.makedirs(originals, exist_ok=True)
    segs, evts, refs, added = [], [], [], []

    for wav_name in wavs:
        src = os.path.join(audio_dir, wav_name)
        title = sanitize(os.path.splitext(wav_name)[0])
        seg_name = SEG_PREFIX + title
        base, n = seg_name, 2
        while seg_name in used_segments:
            seg_name = "%s_%d" % (base, n); n += 1
        used_segments.add(seg_name)

        event_name = "%s%02d" % (EVENT_BASE, index)
        while event_name in existing_events:
            index += 1
            event_name = "%s%02d" % (EVENT_BASE, index)
        existing_events.add(event_name)

        dst_name = seg_name + ".wav"
        n = 2
        while dst_name in used_files:
            dst_name = "%s_%d.wav" % (seg_name, n); n += 1
        used_files.add(dst_name)
        duration = wav_ms(src)

        seg = remap_ids(seg_tpl, ids)
        seg = seg.replace('Name="%s"' % TEMPLATE_SEGMENT, 'Name="%s"' % seg_name)
        seg = re.sub(r'(<Property Name="EndPosition" Type="Real64" Value=")\d+(")',
                     r"\g<1>%d\g<2>" % duration, seg, count=1)
        seg = re.sub(r'(<Property Name="EndTrimOffset" Type="Real64" Value=")\d+(")',
                     r"\g<1>%d\g<2>" % duration, seg, count=1)
        seg = re.sub(r'(<Property Name="TimeMs" Type="Real64" Value=")\d+(?:\.\d+)?(")',
                     r"\g<1>%d\g<2>" % duration, seg, count=1)
        seg = re.sub(r"<AudioFile>[^<]*</AudioFile>", "<AudioFile>%s</AudioFile>" % dst_name, seg, count=1)
        seg = re.sub(r'<MediaID ID="\d+"', '<MediaID ID="%d"' % ids.media(), seg, count=1)
        seg_id = re.search(r'<MusicSegment Name="[^"]*" ID="(\{[^}]+\})"', seg).group(1)

        evt = remap_ids(evt_tpl, ids)
        evt = evt.replace(TEMPLATE_EVENT, event_name)
        evt = re.sub(
            r'<ObjectRef Name="%s" ID="\{[^}]+\}" WorkUnitID="\{[^}]+\}"' % TEMPLATE_SEGMENT,
            '<ObjectRef Name="%s" ID="%s" WorkUnitID="%s"' % (seg_name, seg_id, CONTAINERS_WU_ID),
            evt, count=1)
        if 'Name="%s"' % seg_name not in evt:
            die("事件重定向失败，工程可能被改坏：%s" % seg_name)
        evt_id = re.search(r'<Event Name="[^"]*" ID="(\{[^}]+\})"', evt).group(1)

        refs.append('<ObjectRef Name="%s" ID="%s" WorkUnitID="%s" '
                    'Origin="Manual" Filter="7"/>' % (event_name, evt_id, EVENTS_WU_ID))
        segs.append(seg)
        evts.append(evt)
        added.append({"index": index, "event": event_name, "segment": seg_name,
                      "audio": dst_name, "duration_ms": duration})
        if not a.dry_run:
            shutil.copy2(src, os.path.join(originals, dst_name))
        index += 1

    if a.dry_run:
        for m in added:
            say("%-22s %-40s %8.2f s" % (m["event"], m["segment"], m["duration_ms"] / 1000.0))
        say("\n(dry run：未写入)")
        return 0

    c_txt = c_txt.replace("<!--SONGS-->", "\n".join(segs) + "\n<!--SONGS-->", 1)
    e_txt = e_txt.replace("<!--EVENTS-->", "\n".join(evts) + "\n<!--EVENTS-->", 1)
    b_txt = b_txt.replace("<!--BANKREFS-->", "\n".join(refs) + "\n<!--BANKREFS-->", 1)
    write_text(containers, c_txt); write_text(events, e_txt); write_text(banks, b_txt)

    man = load_manifest()
    have = {t["event"] for t in man.get("tracks", [])}
    man.setdefault("tracks", []).extend([m for m in added if m["event"] not in have])
    man.update({"project": "TH_MUSIC", "author": "Touhou Universalis II", "generated_by": "bgm_pipeline.py"})
    write_text(MANIFEST, json.dumps(man, ensure_ascii=False, indent=2), bom=False)

    total = len(re.findall(r"<AudioFileSource", c_txt))
    say("已加入 %d 首；工程现有 AudioFileSource %d 个（Wwise 未授权上限 200）" % (len(segs), total))
    if total > 200:
        say("警告：超过 200 个媒体项，需按 README_AI.md §8 拆工程", file=sys.stderr)
    say("下一步：python tools\\bgm_pipeline.py build")
    return 0


# ─────────────────────── 3) build ───────────────────────
def cmd_build(a):
    ww = a.console or find_wwise()
    wproj = os.path.join(os.path.abspath(a.project or PROJECT_DIR), PROJECT_FILE)
    if not ww:
        die("找不到 WwiseConsole.exe。\n"
            "  1) 装 Wwise Launcher：https://www.audiokinetic.com/download/\n"
            "  2) 在 Launcher 里装 Wwise 2025.1.12（工程 schema 133，低版本打不开）\n"
            "  3) 重跑本命令，或传 --console \"<...>\\WwiseConsole.exe\"，或设环境变量 WWISE_CONSOLE", 3)
    say("WwiseConsole: " + ww)
    say("verify …")
    r = subprocess.run([ww, "verify", wproj, "--abort-on-load-issues"], capture_output=True, text=True)
    say((r.stdout or "").strip()[-2000:])
    if r.returncode != 0:
        die("verify 失败（exit %s）：\n%s" % (r.returncode, (r.stderr or "").strip()[:2000]))
    say("generate-soundbank %s …" % BANK)
    r = subprocess.run([ww, "generate-soundbank", wproj, "--platform", "Windows",
                        "--bank", BANK, "--save"], capture_output=True, text=True)
    say((r.stdout or "").strip()[-2000:])
    if r.returncode != 0:
        die("生成失败（exit %s）：\n%s" % (r.returncode, (r.stderr or "").strip()[:2000]))
    out = os.path.join(os.path.dirname(wproj), "GeneratedSoundBanks", "Windows")
    bnk = os.path.join(out, BANK + ".bnk")
    if not os.path.isfile(bnk):
        die("生成目录里没有 %s（检查 bank 名与工程里的 SoundBank 对象名是否一致）" % bnk)
    bv, vv = bkhd_version(bnk), vanilla_bank_version()
    say("OK: %s (%.1f KB)  bank version=%s" % (bnk, os.path.getsize(bnk) / 1024.0, bv))
    if bv and vv and bv != vv:
        say("警告：生成库 bank version %s ≠ 原版 %s —— 引擎会报 Could not load sound bank ... result: 15，"
            "请换与原版同代的 Wwise（2025.1.x）重新生成" % (bv, vv), file=sys.stderr)
    say("下一步：python tools\\bgm_pipeline.py install")
    return 0


# ─────────────────── 4) install（投放 + 合并总表） ───────────────────
def merge_soundbanks_info(base_json, mine_json, out_json, bank_name):
    with open(base_json, encoding="utf-8-sig") as f:
        base = json.load(f)
    with open(mine_json, encoding="utf-8-sig") as f:
        mine = json.load(f)
    src = [b for b in mine["SoundBanksInfo"]["SoundBanks"] if b.get("ShortName") == bank_name]
    if not src:
        die("自生成的 SoundbanksInfo.json 里没有 %s" % bank_name)
    banks = base["SoundBanksInfo"]["SoundBanks"]
    banks[:] = [b for b in banks if b.get("ShortName") != bank_name] + src
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    tmp = out_json + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(base, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, out_json)
    return [b.get("ShortName") for b in banks]


def cmd_install(a):
    proj = os.path.abspath(a.project or PROJECT_DIR)
    gen = os.path.join(proj, "GeneratedSoundBanks", "Windows")
    bnk = os.path.join(gen, BANK + ".bnk")
    jsn = os.path.join(gen, "SoundbanksInfo.json")
    if not os.path.isfile(bnk):
        die("没找到 %s，先跑 build" % bnk)
    if not os.path.isfile(jsn):
        # 工程未开启 "Generate all banks metadata" 时不会写总表，只有本库片段；
        # 片段本身就是完整的 SoundBanksInfo 结构，可直接当来源用。
        frag = os.path.join(gen, BANK + ".json")
        if os.path.isfile(frag):
            say("（没有 SoundbanksInfo.json，改用本库片段 %s.json）" % BANK)
            jsn = frag
        else:
            die("没找到 %s 也没有 %s.json" % (jsn, BANK))

    os.makedirs(BANK_DEST, exist_ok=True)
    shutil.copy2(bnk, os.path.join(BANK_DEST, BANK + ".bnk"))
    say("+ %s.bnk" % BANK)
    mine_frag = os.path.join(gen, BANK + ".json")
    if os.path.isfile(mine_frag):
        shutil.copy2(mine_frag, os.path.join(BANK_DEST, BANK + ".json"))
        say("+ %s.json" % BANK)
    media_src = os.path.join(gen, "Media")
    if os.path.isdir(media_src):
        media_dst = os.path.join(BANK_DEST, "Media")
        os.makedirs(media_dst, exist_ok=True)
        n = 0
        for f in os.listdir(media_src):
            if f.lower().endswith(".wem"):
                shutil.copy2(os.path.join(media_src, f), os.path.join(media_dst, f)); n += 1
        say("+ Media/*.wem × %d" % n)

    vb = a.vanilla or find_vanilla_banks()
    if not vb:
        die("找不到原版音效库目录，用 --vanilla 指定（里面应有 SoundbanksInfo.json）")
    out_json = os.path.join(BANK_DEST, "SoundbanksInfo.json")
    if os.path.isfile(out_json) and not a.force:
        say("检测到 mod 里已有 SoundbanksInfo.json —— 默认以它为基底合并（--force 改回原版基底）")
        basesrc = out_json
    else:
        basesrc = os.path.join(vb, "SoundbanksInfo.json")
    names = merge_soundbanks_info(basesrc, jsn, out_json, BANK)
    say("合并完成：%d 个库 → %s" % (len(names), out_json))
    say("  含 " + ", ".join(n for n in names if n in (BANK, "sb_music_logic", "sb_music_media")) +
        " …（共 %d）" % len(names))
    say("下一步：python tools\\bgm_pipeline.py data")
    return 0


# ─────────────────── 5) data（曲目库/分类/本地化） ───────────────────
def ensure_meta(meta):
    man = load_manifest()
    changed = False
    for t in man.get("tracks", []):
        ev = t["event"]
        if ev not in meta["tracks"]:
            title = re.sub("^" + SEG_PREFIX, "", t["segment"]).replace("_", " ")
            meta["tracks"][ev] = {"label": "00-th%02d" % t["index"], "title": title,
                                  "composer": "", "performer": "", "flavour": ""}
            changed = True
    if changed:
        save_meta(meta)
    return meta


def cmd_data(a):
    """生成 mod 侧数据：引擎曲目库 + 曲名本地化（游戏自带播放器直接可点播）。"""
    man = load_manifest()
    tracks = man.get("tracks", [])
    if not tracks:
        die("song_manifest.json 是空的，先跑 add / TSV 导入")
    meta = ensure_meta(load_meta())

    # ① 引擎曲目库：键必须是 Wwise 事件名，否则点播会报 Could not play music player track
    lines = ["# 由 tools/bgm_pipeline.py 生成；改曲名改 tools/music_meta.json 后重跑 data",
             "# 键必须与 bank 里的 Wwise 事件名一致", ""]
    for t in tracks:
        m = meta["tracks"].get(t["event"], {})
        lines.append("%s = {" % t["event"])
        if m.get("composer"):
            lines.append("\tcomposer = %s" % sanitize(m["composer"]))
        if m.get("performer"):
            lines.append("\tperformer = %s" % sanitize(m["performer"]))
        lines.append("}")
        lines.append("")
    write_text(TRACKS_FILE, "\n".join(lines))
    say("+ 曲目库：%d 首 → %s" % (len(tracks), TRACKS_FILE))

    # ② 曲名 / 作者本地化
    def loc_block(lang_prefix):
        en = lang_prefix == "english"
        out = ["l_%s:" % lang_prefix, " # 东方风云 II · 曲目名"]
        people = {}
        for t in tracks:
            m = meta["tracks"].get(t["event"], {})
            title = (m.get("title_en") if en else "") or m.get("title") or t["segment"]
            if m.get("label"):
                title = "%s-%s" % (m["label"], title)
            out.append(' %s: "%s"' % (t["event"], title.replace('"', "'")))
            flav = ((m.get("flavour_en") if en else "") or m.get("flavour") or "").replace('"', "'")
            if flav:
                out.append(' %s_flavour: "%s"' % (t["event"], flav))
            for field in ("composer", "performer"):
                if m.get(field):
                    people[sanitize(m[field])] = m[field].replace('"', "'")
        for ident, display in sorted(people.items()):
            out.append(' %s: "%s"' % (ident, display))
        return "\n".join(out) + "\n"

    write_text(os.path.join(LOC_DIR_SCH, "th_music_l_simp_chinese.yml"), loc_block("simp_chinese"))
    write_text(os.path.join(LOC_DIR_ENG, "th_music_l_english.yml"), loc_block("english"))
    say("+ 曲名/作者本地化")

    # ③ 清掉可能残留的自建页签文件（已弃用路线）
    for rel in (os.path.join("in_game", "gui", "music_player_lateralview.gui"),
                os.path.join("in_game", "common", "scripted_guis", "th_music_player.txt")):
        fp = os.path.join(MOD, rel)
        if os.path.isfile(fp):
            os.remove(fp)
            say("- 已删除弃用的自建页签文件：" + rel)
    return 0


def cmd_all(a):
    for step in (cmd_convert, cmd_add, cmd_build, cmd_install, cmd_data):
        say("\n===== %s =====" % step.__name__.replace("cmd_", ""))
        rc = step(a)
        if rc:
            return rc
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("doctor", help="环境自检")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("convert", help="源音频 → 44.1k/16bit WAV")
    p.add_argument("--src", help="源目录（默认 tools/music_src）")
    p.set_defaults(func=cmd_convert)

    p = sub.add_parser("add", help="WAV → Wwise 工程")
    p.add_argument("--audio", help="WAV 目录（默认 tools/music_wav）")
    p.add_argument("--project", help="Wwise 工程目录")
    p.add_argument("--start", type=int, help="起始编号")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("build", help="生成音效库")
    p.add_argument("--project")
    p.add_argument("--console", help="WwiseConsole.exe 路径")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("install", help="投放 + 合并 SoundbanksInfo.json")
    p.add_argument("--project")
    p.add_argument("--vanilla", help="原版 banks/windows 目录")
    p.add_argument("--force", action="store_true", help="强制以原版总表为基底")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("data", help="生成曲目库/分类/本地化")
    p.add_argument("--mirror-vanilla", action="store_true", help="额外生成『游戏自带』分类页签")
    p.set_defaults(func=cmd_data)

    p = sub.add_parser("all", help="convert → add → build → install → data")
    p.add_argument("--src"); p.add_argument("--audio"); p.add_argument("--project")
    p.add_argument("--console"); p.add_argument("--vanilla"); p.add_argument("--force", action="store_true")
    p.add_argument("--mirror-vanilla", action="store_true")
    p.set_defaults(func=cmd_all)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
