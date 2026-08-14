#!/usr/bin/env python3
"""
Touhou Universalis II — Static Validator Wrapper
=================================================
Reuses the eu5-modding-project reference library's validate.py checks
(anti-patterns YAML, valid enums YAML, vanilla modifier-type whitelist)
and adds TH-specific audits:

  - 5-language localization key alignment (main_menu + in_game)
  - duplicate localization keys within a file
  - empty string values  ("key: \"\"")
  - ';' separator bug in YAML keys
  - residual dev files (test.txt / fix_*.py)
  - BOM policy: .txt/.yml need UTF-8 BOM except main_menu/setup/start (no BOM);
    .gui/.csv must have no BOM

Usage:
  $env:PYTHONUTF8='1'; python tools/th_validate.py                 # validate whole mod
  $env:PYTHONUTF8='1'; python tools/th_validate.py <target-path>   # validate one dir/file
  $env:PYTHONUTF8='1'; python tools/th_validate.py --changed       # git-changed files
  $env:PYTHONUTF8='1'; python tools/th_validate.py --ai-report     # JSON output

Exit code: 0 = pass, 1 = issues found.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TH_ROOT = Path(__file__).resolve().parent.parent
LIB_SCRIPTS = TH_ROOT.parent / "eu5-modding-project" / "scripts"
PYLIBS = TH_ROOT / "tools" / "pylibs"

if PYLIBS.exists():
    sys.path.insert(0, str(PYLIBS))
sys.path.insert(0, str(LIB_SCRIPTS))

import validate as lib  # noqa: E402  (library validate.py, imported as module)

# Point the library's path base at the TH mod so relative_to() works for our files.
lib.REPO_ROOT = TH_ROOT

UTF8_BOM = b"\xef\xbb\xbf"
VALID_DIRS = (TH_ROOT / "in_game", TH_ROOT / "main_menu", TH_ROOT / "loading_screen")

# Generated / data files: huge coordinate or setup data, not script logic.
# Content regex checks are skipped for them (decode + BOM only). This avoids
# the library's O(n) line-number computation per match exploding on files
# with hundreds of thousands of matches (e.g. map locators with 6+ digit floats).
DATA_DIR_MARKERS = ("/map_data/", "/gfx/map/map_objects/", "/main_menu/setup/start/")

# Vanilla-copied data where the precision rule does not apply (values are
# verbatim base-game numbers and must not be rounded).
PRECISION_EXEMPT_PATHS = ("loading_screen/common/defines/00_defines.txt",)

# ---------------------------------------------------------------------------
# TH-specific audits
# ---------------------------------------------------------------------------

LOC_LANGS = {
    "english": "_l_english.yml",
    "simp_chinese": "_l_simp_chinese.yml",
    "japanese": "_l_japanese.yml",
    "korean": "_l_korean.yml",
    "russian": "_l_russian.yml",
}
LOC_HEADER = {"l_english", "l_simp_chinese", "l_japanese", "l_korean", "l_russian"}
KEY_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*:")
SEMICOLON_RE = re.compile(r"^\s*[A-Za-z0-9_]+;\s*")
EMPTY_VALUE_RE = re.compile(r":\s*\"\"\s*$")


def _loc_files(root: Path) -> dict:
    """Return {lang: {stem: Path}} for *_l_*.yml under root/localization."""
    out = {lang: {} for lang in LOC_LANGS}
    loc_dir = root / "localization"
    if not loc_dir.exists():
        return out
    for p in sorted(loc_dir.rglob("*_l_*.yml")):
        for lang, suffix in LOC_LANGS.items():
            if p.name.endswith(suffix):
                out[lang][p.name[: -len(suffix)]] = p
                break
    return out


def _read_keys(path: Path) -> set:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        return set()
    return {
        m.group(1)
        for line in content.splitlines()
        if (m := KEY_RE.match(line)) and m.group(1) not in LOC_HEADER
    }


def audit_loc_alignment(root: Path, label: str) -> None:
    """Every loc stem present in english must exist in all 5 languages with equal key sets."""
    files = _loc_files(root)
    all_stems = set()
    for lang_files in files.values():
        all_stems |= set(lang_files)
    for stem in sorted(all_stems):
        en_file = files["english"].get(stem)
        for lang, lang_files in files.items():
            if lang == "english":
                continue
            lf = lang_files.get(stem)
            if lf is None:
                lib.issues.append(
                    f"[LOC] {label}: file {stem}_l_{lang}.yml missing (english has it)"
                )
                continue
            en_keys = _read_keys(en_file) if en_file else set()
            lf_keys = _read_keys(lf)
            missing = sorted(en_keys - lf_keys)
            extra = sorted(lf_keys - en_keys)
            if missing:
                lib.issues.append(
                    f"[LOC] {label}/{stem} ({lang}): {len(missing)} key(s) missing: "
                    + ", ".join(missing[:20])
                )
            if extra:
                lib.issues.append(
                    f"[LOC] {label}/{stem} ({lang}): {len(extra)} extra key(s) not in english: "
                    + ", ".join(extra[:20])
                )


def audit_loc_files(root: Path) -> None:
    """Duplicate keys, empty values, ';' separators inside every loc file."""
    loc_dir = root / "localization"
    if not loc_dir.exists():
        return
    for p in sorted(loc_dir.rglob("*.yml")):
        rel = p.relative_to(TH_ROOT)
        try:
            lines = p.read_text(encoding="utf-8-sig").splitlines()
        except (UnicodeDecodeError, OSError):
            lib.issues.append(f"[ENCODING] Cannot decode as UTF-8: {rel}")
            continue
        seen = {}
        for i, line in enumerate(lines, 1):
            m = KEY_RE.match(line)
            if m and m.group(1) not in LOC_HEADER:
                key = m.group(1)
                if key in seen:
                    lib.issues.append(
                        f"[LOC] {rel}:{i} -- duplicate key '{key}' (also line {seen[key]})"
                    )
                else:
                    seen[key] = i
            if SEMICOLON_RE.match(line):
                lib.issues.append(
                    f"[LOC] {rel}:{i} -- ';' separator instead of ':' -> "
                    f'Bad: "{line.strip()}" -> replace ; with :'
                )
            if EMPTY_VALUE_RE.search(line):
                lib.issues.append(
                    f"[LOC] {rel}:{i} -- empty string value -> "
                    f'Bad: "{line.strip()}" -> fill in a real translation'
                )


def audit_residual_files() -> None:
    for p in sorted((TH_ROOT / "main_menu" / "localization").rglob("*")):
        if p.is_file() and (p.name == "test.txt" or p.name.startswith("fix_")):
            lib.issues.append(
                f"[RESIDUAL] {p.relative_to(TH_ROOT)} -- dev/test file; delete it"
            )


def audit_bom(path: Path) -> None:
    if path.suffix not in {".txt", ".yml", ".gui", ".csv"}:
        return
    rel = str(path.relative_to(TH_ROOT)).replace("\\", "/")
    in_setup_start = "/main_menu/setup/start/" in rel or rel.startswith("main_menu/setup/start/")
    try:
        with path.open("rb") as f:
            header = f.read(3)
    except OSError:
        return
    has_bom = header == UTF8_BOM
    if path.suffix in {".txt", ".yml"}:
        if in_setup_start and has_bom:
            lib.issues.append(
                f"[ENCODING] {rel} -- setup/start files must have NO BOM"
            )
        elif not in_setup_start and not has_bom:
            lib.issues.append(f"[ENCODING] {rel} -- missing UTF-8 BOM")
    elif path.suffix in {".gui", ".csv"} and has_bom:
        lib.issues.append(f"[ENCODING] {rel} -- .gui/.csv must have NO BOM")


def is_data_file(path: Path) -> bool:
    rel = "/" + str(path.relative_to(TH_ROOT)).replace("\\", "/") + "/"
    return any(marker in rel for marker in DATA_DIR_MARKERS)


def check_anti_patterns_fast(path: Path, content: str, patterns: list) -> None:
    """Like lib.check_anti_patterns but with O(log n) line numbers.

    The library computes line_num via content[:m.start()].count('\\n') for every
    match, which is O(position) per match -> quadratic on files with many matches.
    """
    import bisect

    path_str = str(path).replace("\\", "/")
    rel_str = str(path.relative_to(TH_ROOT)).replace("\\", "/")
    newline_offsets = [m.start() for m in re.finditer(r"\n", content)]

    def line_no(pos: int) -> int:
        return bisect.bisect_right(newline_offsets, pos) + 1

    for entry in patterns:
        regex = entry.get("pattern", "")
        if not regex:
            continue
        if (
            entry.get("id") == "float_precision_exceeds_5dp"
            and rel_str in PRECISION_EXEMPT_PATHS
        ):
            continue
        only_in = entry.get("only_in_paths", [])
        if only_in and not any(sub in path_str for sub in only_in):
            continue
        try:
            for m in re.finditer(regex, content, re.MULTILINE | re.IGNORECASE):
                lib.issues.append(
                    f"[{entry.get('category', 'pattern').upper()}] "
                    f"{path.relative_to(TH_ROOT)}:{line_no(m.start())} -- "
                    f'Bad: "{entry["bad"]}" -> {entry["correction"]}'
                )
        except re.error:
            pass


# ---------------------------------------------------------------------------
# File collection & main
# ---------------------------------------------------------------------------

def collect_files(target: Path) -> list:
    if target.is_file():
        return [target]
    out = []
    for p in target.rglob("*"):
        if p.suffix in {".txt", ".gui", ".yml"} and p.is_file():
            out.append(p)
    return out


def get_changed_files() -> list:
    names = set()
    for args in (["diff", "--name-only", "HEAD"], ["diff", "--name-only", "--cached"]):
        r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=TH_ROOT)
        names |= {n.strip() for n in r.stdout.splitlines() if n.strip()}
    r = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True, cwd=TH_ROOT,
    )
    names |= {n.strip() for n in r.stdout.splitlines() if n.strip()}
    out = []
    for name in names:
        p = TH_ROOT / name
        if p.exists() and p.suffix in {".txt", ".gui", ".yml"}:
            out.append(p)
    return out


def main():
    anti_patterns = lib.load_yaml(lib.KNOWLEDGE_DIR / "anti_patterns.yaml") or []
    enum_data = lib.load_yaml(lib.KNOWLEDGE_DIR / "valid_enums.yaml") or {}
    modifier_whitelist = lib.load_modifier_whitelist()

    ai_report = "--ai-report" in sys.argv
    use_changed = "--changed" in sys.argv
    targets = [a for a in sys.argv[1:] if not a.startswith("-")]

    if use_changed:
        files = get_changed_files()
        if not files:
            if ai_report:
                print(json.dumps({"pass": True, "errors": [], "warnings": [], "files_checked": 0},
                                 ensure_ascii=False))
            else:
                print("[OK] No changed mod files to validate.")
            sys.exit(0)
    elif targets:
        files = []
        for t in targets:
            files.extend(collect_files(Path(t).resolve()))
    else:
        files = []
        for d in VALID_DIRS:
            files.extend(collect_files(d))

    for path in files:
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            lib.issues.append(f"[ENCODING] Cannot decode as UTF-8: {path.relative_to(TH_ROOT)}")
            continue
        if is_data_file(path):
            continue  # generated/setup data: decode check only (no BOM, no content checks)
        audit_bom(path)
        check_anti_patterns_fast(path, content, anti_patterns)
        lib.check_enums(path, content, enum_data)
        lib.check_global_variable_map_updates(path, content)
        lib.check_modifier_names(path, content, modifier_whitelist)

    # TH localization audits
    audit_loc_alignment(TH_ROOT / "main_menu", "main_menu")
    audit_loc_alignment(TH_ROOT / "in_game", "in_game")
    audit_loc_files(TH_ROOT / "main_menu")
    audit_loc_files(TH_ROOT / "in_game")
    audit_residual_files()

    if ai_report:
        errors = [lib._parse_issue_structured(i) for i in lib.issues]
        print(json.dumps({
            "pass": len(errors) == 0,
            "errors": errors,
            "warnings": [],
            "files_checked": len(files),
        }, ensure_ascii=False, indent=2))
        sys.exit(0 if len(errors) == 0 else 1)

    if lib.issues:
        print(f"[FAIL] {len(lib.issues)} issue(s) found:\n")
        for issue in lib.issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print(f"[OK] Validated {len(files)} file(s) -- no issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
