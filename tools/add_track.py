#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""add_track.py — 往 Wwise 工程里加一首歌（全部用 Wwise 自己的 TSV 导入，再补线）。

用法示例：
  python tools\\add_track.py --wav tools\\music_wav\\YUMU_Eastern_Dream.wav \
      --segment th_Eastern_Dream --event MusicPlayer_th_t02 \
      --title "紅楼 ~ Eastern Dream" --label 00-th01

做的事：
  1) WwiseConsole tab-delimited-import 建 MusicSegment + Event（格式才是合法的）
  2) 给新段补：OutputBus=Music、Conversion=Vorbis Quality High、Volume=-19.6、Track 不流式
  3) 给新事件补：Stop(Music, ActionType=2, Scope=1) → Play(该段)
  4) 追加 song_manifest.json 与 music_meta.json（label 决定列表里显示的前缀）

之后照旧：
  python tools\\bgm_pipeline.py build && python tools\\bgm_pipeline.py install && python tools\\bgm_pipeline.py data
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import uuid
import wave

TOOLS = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(TOOLS)
PROJECT_DIR = os.path.join(TOOLS, "wwise2", "TH_MUSIC")
WPROJ = os.path.join(PROJECT_DIR, "TH_MUSIC.wproj")
MANIFEST = os.path.join(PROJECT_DIR, "song_manifest.json")
META = os.path.join(TOOLS, "music_meta.json")
BANK = "sb_music_media_th"

WWISE_CANDIDATES = [
    r"E:\BaiduNetdiskDownload\Wwise_2025.1.12.9287\Authoring\x64\Release\bin\WwiseConsole.exe",
    r"C:\Program Files (x86)\Audiokinetic",
]


def rd(p):
    return io.open(p, encoding="utf-8-sig").read()


def wr(p, t):
    io.open(p, "w", encoding="utf-8-sig", newline="\r\n").write(t)


def find_wwise():
    env = os.environ.get("WWISE_CONSOLE")
    if env and os.path.isfile(env):
        return env
    for p in WWISE_CANDIDATES:
        if p.lower().endswith(".exe") and os.path.isfile(p):
            return p
    raise SystemExit("找不到 WwiseConsole，用 --console 或 WWISE_CONSOLE 指定")


def wav_ms(path):
    with wave.open(path, "rb") as w:
        return int(round(w.getnframes() * 1000.0 / w.getframerate()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--segment", required=True, help="Wwise 段名，如 th_Eastern_Dream")
    ap.add_argument("--event", required=True, help="事件名，如 MusicPlayer_th_t02")
    ap.add_argument("--title", required=True, help="列表里显示的曲名")
    ap.add_argument("--label", required=True, help="列表前缀，如 00-th01")
    ap.add_argument("--console", help="WwiseConsole.exe")
    ap.add_argument("--start", type=int, default=2, help="manifest 里的序号（默认 2）")
    a = ap.parse_args()

    wav = os.path.abspath(a.wav)
    if not os.path.isfile(wav):
        raise SystemExit("没有这个 wav：%s" % wav)
    duration = wav_ms(wav)
    ww = a.console or find_wwise()

    # ── 1) TSV 导入 ──
    tsv = os.path.join(TOOLS, "_import_one.tsv")
    io.open(tsv, "w", encoding="utf-8-sig", newline="").write(
        "Audio File\tObject Type\tObject Path\tEvent\r\n"
        "%s\tMusic Segment\t\\Interactive Music Hierarchy\\Default Work Unit\\%s\t%s\r\n"
        % (wav, a.segment, a.event))
    print("import:", a.segment, "->", a.event)
    r = subprocess.run([ww, "tab-delimited-import", WPROJ, tsv], capture_output=True, text=True)
    print((r.stdout or "").strip()[-600:])
    if r.returncode not in (0, 2):
        raise SystemExit("TSV 导入失败：%s" % (r.stderr or "")[:500])

    # ── 2)(3) 补线 ──
    con = os.path.join(PROJECT_DIR, "Containers", "Default Work Unit.wwu")
    evt = os.path.join(PROJECT_DIR, "Events", "Default Work Unit.wwu")
    bus = os.path.join(PROJECT_DIR, "Busses", "Default Work Unit.wwu")
    fac = os.path.join(PROJECT_DIR, "Conversion Settings", "Factory Conversion Settings.wwu")

    BUS_WU = re.search(r'<WwiseDocument[^>]*ID="(\{[^}]+\})"', rd(bus)).group(1)
    MUSIC_BUS = re.search(r'<Bus Name="Music" ID="(\{[^}]+\})"', rd(bus)).group(1)
    FAC_WU = re.search(r'<WwiseDocument[^>]*ID="(\{[^}]+\})"', rd(fac)).group(1)
    VORBIS = "{53A9DE0F-3F4F-4B59-8614-3F9E3C7358FC}"

    t = rd(con)
    i = t.index('<MusicSegment Name="%s"' % a.segment)
    j = t.index("</MusicSegment>", i) + len("</MusicSegment>")
    seg = t[i:j]

    seg = re.sub(r'<ObjectRef Name="[^"]*" ID="\{[^}]+\}" WorkUnitID="\{[^}]+\}"/>(?=\s*</Reference>\s*<Reference Name="OutputBus">)',
                 '<ObjectRef Name="Vorbis Quality High" ID="%s" WorkUnitID="%s"/>' % (VORBIS, FAC_WU), seg, count=1)
    seg = seg.replace('<ObjectRef Name="Main Audio Bus"', '<ObjectRef Name="Music"')
    seg = re.sub(r'(<ObjectRef Name="Music" ID=")\{[^}]+\}(" WorkUnitID=")\{[^}]+\}(")',
                 r"\g<1>%s\g<2>%s\g<3>" % (MUSIC_BUS, BUS_WU), seg)
    if 'Name="Volume"' not in seg:
        seg = seg.replace(
            "</PropertyList>",
            '\t<Property Name="Volume" Type="Real64">\n\t\t<ValueList>\n\t\t\t<Value>-19.6</Value>\n'
            '\t\t</ValueList>\n\t</Property>\n</PropertyList>', 1)
    if 'Name="IsStreamingEnabled"' not in seg:
        seg = re.sub(r'(<MusicTrack [^>]*>)\s*',
                     r'\1\n<PropertyList>\n<Property Name="IsStreamingEnabled" Type="bool">\n'
                     r'<ValueList>\n<Value>False</Value>\n</ValueList>\n</Property>\n</PropertyList>\n',
                     seg, count=1)
    t = t[:i] + seg + t[j:]
    wr(con, t)

    e = rd(evt)
    k = e.index('<Event Name="%s"' % a.event)
    m = e.index("<ChildrenList>", k) + len("<ChildrenList>")
    STOP = (
        '\n<Action Name="" ID="{%s}" ShortID="%d">\n'
        '<PropertyList>\n'
        '<Property Name="ActionType" Type="int16" Value="2"/>\n'
        '<Property Name="Scope" Type="int16" Value="1"/>\n'
        '</PropertyList>\n'
        '<ReferenceList>\n'
        '<Reference Name="Target">\n'
        '<ObjectRef Name="Music" ID="%s" WorkUnitID="%s"/>\n'
        '</Reference>\n'
        '</ReferenceList>\n'
        '</Action>\n'
    ) % (str(uuid.uuid4()).upper(), 300000000 + (len(e) % 90000), MUSIC_BUS, BUS_WU)
    e = e[:m] + STOP + e[m:]
    wr(evt, e)

    # ── 3b) 把新事件登记进 SoundBank（不然生成的库里没有它） ──
    bnkf = os.path.join(PROJECT_DIR, "SoundBanks", "Default Work Unit.wwu")
    bt = rd(bnkf)
    if a.event not in re.findall(r'<ObjectRef Name="([^"]+)"', bt):
        EVT_WU = re.search(r'<WwiseDocument[^>]*ID="(\{[^}]+\})"', rd(evt)).group(1)
        ev_id = re.search(r'<Event Name="%s" ID="(\{[^}]+\})"' % re.escape(a.event), rd(evt)).group(1)
        bt = bt.replace("</ObjectInclusionList>",
                        '<ObjectRef Name="%s" ID="%s" WorkUnitID="%s" Origin="Manual" Filter="7"/>\n</ObjectInclusionList>'
                        % (a.event, ev_id, EVT_WU), 1)
        wr(bnkf, bt)
        print("SoundBank 登记:", a.event)

    # ── 4) manifest + meta ──
    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    if any(x["event"] == a.event for x in man["tracks"]):
        print("manifest 已有该事件，跳过追加")
    else:
        man["tracks"].append({"index": a.start, "event": a.event, "segment": a.segment,
                              "audio": os.path.basename(wav), "duration_ms": duration})
        io.open(MANIFEST, "w", encoding="utf-8", newline="\n").write(
            json.dumps(man, ensure_ascii=False, indent=2))

    meta = json.load(io.open(META, encoding="utf-8")) if os.path.isfile(META) else {"tracks": {}}
    meta.setdefault("tracks", {})[a.event] = {"label": a.label, "title": a.title,
                                              "composer": "", "performer": "", "flavour": ""}
    io.open(META, "w", encoding="utf-8", newline="\n").write(
        json.dumps(meta, ensure_ascii=False, indent=2))

    print("OK: %s  %.2f 秒  段=%s" % (a.event, duration / 1000.0, a.segment))
    print("下一步：build → install → data")


if __name__ == "__main__":
    main()
